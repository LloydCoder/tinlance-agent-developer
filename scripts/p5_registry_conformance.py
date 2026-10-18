#!/usr/bin/env python3
"""Fail-closed P5 service, agent, repository and contract registry conformance."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
TSIC = Path("/tmp/tinlance-tsic")
REGISTRY_PATH = ROOT / "registries/ecosystem-registry.json"
SCHEMA_PATH = TSIC / "schemas/registry/v1/registry-manifest.schema.json"
CONTRACT_PATH = TSIC / "contracts/registry/registry-contract.json"
LOCK_PATH = ROOT / "ecosystem.lock.json"
MANIFEST_PATH = ROOT / "docs/ecosystem/ecosystem-manifest.json"

REQUIRED_SERVICES = {
    "agent-platform.api",
    "agent-os.runtime",
    "platform-sdk.client",
    "tadl.validator",
    "tsic.conformance",
}
REQUIRED_AGENTS = {"reference.enterprise-a", "reference.enterprise-b"}
REQUIRED_CONTRACTS = {
    "governed-execution.v1",
    "event-envelope.v1",
    "trace-context.v1",
    "transformation.v1",
    "replication.v1",
    "registry-manifest.v1",
}


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def duplicate_ids(items: list[dict[str, Any]], key: str) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for item in items:
        value = item.get(key)
        if value in seen:
            duplicates.add(str(value))
        seen.add(value)
    return duplicates


def semantic_validate(registry: dict[str, Any], lock: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    repositories = registry.get("repositories", [])
    services = registry.get("services", [])
    agents = registry.get("agents", [])
    contracts = registry.get("contracts", [])
    rules = registry.get("compatibility_rules", [])

    for collection, key, label in (
        (repositories, "id", "repository"),
        (services, "service_id", "service"),
        (agents, "agent_id", "agent"),
        (contracts, "contract_id", "contract"),
    ):
        duplicates = duplicate_ids(collection, key)
        require(not duplicates, f"duplicate {label} IDs: {sorted(duplicates)}", failures)

    repository_by_id = {item["id"]: item for item in repositories}
    service_by_id = {item["service_id"]: item for item in services}
    agent_by_id = {item["agent_id"]: item for item in agents}
    contract_by_id = {item["contract_id"]: item for item in contracts}

    expected_repositories = {
        key: (entry["repository"], entry["ref"], entry["role"])
        for key, entry in lock["repositories"].items()
    }
    authority = lock["integration_authority"]
    expected_repositories["tsic"] = (authority["repository"], authority["ref"], "canonical contract and conformance authority")
    require(set(repository_by_id) == set(expected_repositories),
            "registry repository IDs differ from the locked ecosystem", failures)
    for repo_id, (name, sha, role) in expected_repositories.items():
        entry = repository_by_id.get(repo_id)
        if entry is None:
            continue
        require(entry.get("repository") == name, f"{repo_id}: repository identity mismatch", failures)
        require(entry.get("reviewed_sha") == sha, f"{repo_id}: stale or unlocked reviewed SHA", failures)

    require(set(service_by_id) == REQUIRED_SERVICES,
            "service registry is missing or has unexpected canonical services", failures)
    require(set(agent_by_id) == REQUIRED_AGENTS,
            "agent registry is missing or has unexpected reference agents", failures)
    require(set(contract_by_id) == REQUIRED_CONTRACTS,
            "contract registry is missing or has unexpected canonical contracts", failures)

    for service in services:
        owner = service.get("owner_repository_id")
        require(owner in repository_by_id, f"{service.get('service_id')}: unresolved owner repository", failures)
        missing_contracts = set(service.get("contract_ids", [])) - set(contract_by_id)
        require(not missing_contracts,
                f"{service.get('service_id')}: unresolved contracts {sorted(missing_contracts)}", failures)
        mode = service.get("authority_mode")
        if owner == "platform":
            require(mode == "sole_consequential_execution",
                    "Platform service must be the sole consequential execution authority", failures)
        else:
            require(mode in {"authority_free", "conformance_only"},
                    f"{service.get('service_id')}: non-Platform service has authority", failures)
        require(service.get("enabled") is True, f"{service.get('service_id')}: canonical service is disabled", failures)

    for agent in agents:
        require(agent.get("owner_repository_id") in repository_by_id,
                f"{agent.get('agent_id')}: unresolved owner repository", failures)
        missing = set(agent.get("capabilities", []))
        require(bool(missing), f"{agent.get('agent_id')}: no declared capabilities", failures)
        required_contracts = agent.get("required_contracts", {})
        require(bool(required_contracts), f"{agent.get('agent_id')}: no required contract versions", failures)
        for contract_id, version in required_contracts.items():
            contract = contract_by_id.get(contract_id)
            require(contract is not None, f"{agent.get('agent_id')}: unknown contract {contract_id}", failures)
            if contract is not None:
                require(contract.get("version") == version,
                        f"{agent.get('agent_id')}: incompatible {contract_id} version {version}", failures)
        require(agent.get("authority_mode") in {"delegated_only", "authority_free"},
                f"{agent.get('agent_id')}: agent cannot be an execution authority", failures)

    for contract in contracts:
        require(contract.get("owner_repository_id") in repository_by_id,
                f"{contract.get('contract_id')}: unresolved contract owner", failures)

    rule_keys: set[tuple[str, str]] = set()
    for rule in rules:
        key = (rule.get("consumer_id", ""), rule.get("contract_id", ""))
        require(key not in rule_keys, f"duplicate compatibility rule {key}", failures)
        rule_keys.add(key)
        consumer_exists = key[0] in service_by_id or key[0] in agent_by_id
        require(consumer_exists, f"compatibility rule has unknown consumer {key[0]}", failures)
        contract = contract_by_id.get(key[1])
        require(contract is not None, f"compatibility rule references unknown contract {key[1]}", failures)
        if contract is not None:
            require(contract.get("version") in rule.get("supported_versions", []),
                    f"{key[0]} does not support registered {key[1]} version {contract.get('version')}", failures)
        require(rule.get("reject_unknown") is True, f"{key}: unknown versions must fail closed", failures)
        require(rule.get("reject_stale") is True, f"{key}: stale registrations must fail closed", failures)
        require(rule.get("reject_missing") is True, f"{key}: missing registrations must fail closed", failures)

    require(any(rule.get("consumer_id") == "platform-sdk.client" for rule in rules),
            "SDK has no compatibility rules", failures)
    require(any(rule.get("consumer_id") == "agent-os.runtime" for rule in rules),
            "OS has no compatibility rules", failures)
    return failures


def main() -> None:
    for path in (REGISTRY_PATH, SCHEMA_PATH, CONTRACT_PATH, LOCK_PATH, MANIFEST_PATH):
        if not path.is_file():
            raise SystemExit(f"FAIL P5: required registry artifact is missing: {path}")
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []

    require(contract.get("format") == "tinlance-canonical-ecosystem-registry/v1",
            "TSIC registry contract format drifted", failures)
    require(registry.get("baseline_id") == lock.get("baseline_id") == manifest.get("baseline_id"),
            "registry, lock and manifest baseline IDs differ", failures)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    schema_errors = sorted(validator.iter_errors(registry), key=lambda error: list(error.path))
    for error in schema_errors:
        failures.append(f"schema: {'/'.join(map(str, error.path))}: {error.message}")
    failures.extend(semantic_validate(registry, lock))

    # Negative controls prove stale pins, missing contract declarations and authority drift fail closed.
    stale = copy.deepcopy(registry)
    stale["repositories"][0]["reviewed_sha"] = "main"
    require(not validator.is_valid(stale), "negative test: schema accepted a mutable repository ref", failures)
    missing_contract = copy.deepcopy(registry)
    missing_contract["services"][0].pop("contract_ids", None)
    require(not validator.is_valid(missing_contract), "negative test: schema accepted a service without contracts", failures)
    authority_drift = copy.deepcopy(registry)
    authority_drift["services"][0]["authority_mode"] = "authority_free"
    require(bool(semantic_validate(authority_drift, lock)),
            "negative test: semantic validator accepted Platform authority drift", failures)
    incompatible = copy.deepcopy(registry)
    for rule in incompatible["compatibility_rules"]:
        if rule["consumer_id"] == "platform-sdk.client" and rule["contract_id"] == "trace-context.v1":
            rule["supported_versions"] = ["99.0"]
            break
    require(bool(semantic_validate(incompatible, lock)),
            "negative test: semantic validator accepted an incompatible contract version", failures)

    if failures:
        raise SystemExit("FAIL P5 registry conformance:\n- " + "\n- ".join(failures))
    print(json.dumps({
        "phase": "P5",
        "repositories": len(registry["repositories"]),
        "services": len(registry["services"]),
        "agents": len(registry["agents"]),
        "contracts": len(registry["contracts"]),
        "compatibility_rules": len(registry["compatibility_rules"]),
        "status": "pass",
        "production_status": "unverified",
    }, sort_keys=True))


if __name__ == "__main__":
    main()

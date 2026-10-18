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
SCHEMA_PATH = TSIC / "schemas/registry/v2/registry-manifest.schema.json"
CONTRACT_PATH = TSIC / "contracts/registry/registry-contract-v2.json"
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
    "registry-manifest.v2",
    "model-routing.v1",
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
        require(entry.get("role") == role, f"{repo_id}: architectural role mismatch", failures)
        publisher = entry.get("publisher", {})
        publisher_id = publisher.get("publisher_id", "")
        require(bool(publisher_id), f"{repo_id}: publisher identity is missing", failures)
        require(publisher.get("identity_uri") == f"https://github.com/{publisher_id}",
                f"{repo_id}: publisher identity URI does not match publisher ID", failures)
        require(publisher.get("identity_status") in {"verified", "unverified", "revoked"},
                f"{repo_id}: publisher identity state is invalid", failures)
        lifecycle = entry.get("lifecycle", {})
        lifecycle_state = lifecycle.get("state")
        require(lifecycle_state in {"active", "quarantined", "revoked", "deprecated"},
                f"{repo_id}: invalid lifecycle state", failures)
        if lifecycle_state in {"quarantined", "revoked", "deprecated"}:
            require(bool(lifecycle.get("reason")), f"{repo_id}: non-active lifecycle requires a reason", failures)
        if lifecycle_state == "deprecated":
            require(bool(lifecycle.get("replacement_id")), f"{repo_id}: deprecated repository requires a replacement", failures)
        supply_chain = entry.get("supply_chain", {})
        require(supply_chain.get("reviewed_sha") == sha,
                f"{repo_id}: supply-chain SHA differs from the reviewed repository SHA", failures)
        require(
            supply_chain.get("provenance_uri") == f"https://github.com/{name}/commit/{sha}",
            f"{repo_id}: provenance must point to the exact reviewed commit",
            failures,
        )
        attestation_uri = f"https://github.com/{name}/attestations"
        require(supply_chain.get("sbom_uri") == attestation_uri,
                f"{repo_id}: SBOM reference must point to the repository attestation index", failures)
        require(supply_chain.get("signature_uri") == attestation_uri,
                f"{repo_id}: signature reference must point to the repository attestation index", failures)
        require(supply_chain.get("verification_status") in {"pending", "verified", "revoked"},
                f"{repo_id}: revoked or invalid supply-chain attestation fails closed", failures)

    for entry in repositories:
        lifecycle = entry.get("lifecycle", {})
        if lifecycle.get("state") == "deprecated":
            replacement = repository_by_id.get(lifecycle.get("replacement_id"))
            require(
                replacement is not None and replacement.get("lifecycle", {}).get("state") == "active",
                f"{entry.get('id')}: deprecated repository replacement must be active",
                failures,
            )
    for entry in services:
        lifecycle = entry.get("lifecycle", {})
        if lifecycle.get("state") == "deprecated":
            replacement = service_by_id.get(lifecycle.get("replacement_id"))
            require(
                replacement is not None and replacement.get("lifecycle", {}).get("state") == "active",
                f"{entry.get('service_id')}: deprecated service replacement must be active",
                failures,
            )
    for entry in agents:
        lifecycle = entry.get("lifecycle", {})
        if lifecycle.get("state") == "deprecated":
            replacement = agent_by_id.get(lifecycle.get("replacement_id"))
            require(
                replacement is not None and replacement.get("lifecycle", {}).get("state") == "active",
                f"{entry.get('agent_id')}: deprecated agent replacement must be active",
                failures,
            )

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
        lifecycle = service.get("lifecycle", {})
        state = lifecycle.get("state")
        if state == "active":
            require(service.get("enabled") is True, f"{service.get('service_id')}: active service is disabled", failures)
            owner_entry = repository_by_id.get(owner, {})
            require(owner_entry.get("lifecycle", {}).get("state") == "active",
                    f"{service.get('service_id')}: active service owner is not active", failures)
            require(owner_entry.get("publisher", {}).get("identity_status") != "revoked",
                    f"{service.get('service_id')}: owner publisher identity is revoked", failures)
            require(owner_entry.get("supply_chain", {}).get("verification_status") != "revoked",
                    f"{service.get('service_id')}: owner supply-chain attestation is revoked", failures)
            for contract_id in service.get("contract_ids", []):
                registered_contract = contract_by_id.get(contract_id)
                if registered_contract is not None:
                    require(registered_contract.get("lifecycle", {}).get("state") == "active",
                            f"{service.get('service_id')}: active service references non-active contract {contract_id}", failures)
                    contract_owner = repository_by_id.get(registered_contract.get("owner_repository_id"), {})
                    require(contract_owner.get("lifecycle", {}).get("state") == "active",
                            f"{service.get('service_id')}: contract owner is not active", failures)
                    require(contract_owner.get("publisher", {}).get("identity_status") != "revoked",
                            f"{service.get('service_id')}: contract owner publisher is revoked", failures)
                    require(contract_owner.get("supply_chain", {}).get("verification_status") != "revoked",
                            f"{service.get('service_id')}: contract owner supply-chain attestation is revoked", failures)
        else:
            require(service.get("enabled") is False,
                    f"{service.get('service_id')}: non-active lifecycle must fail closed", failures)
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
        agent_lifecycle = agent.get("lifecycle", {})
        if agent.get("agent_id") in REQUIRED_AGENTS:
            require(agent_lifecycle.get("state") == "active",
                    f"{agent.get('agent_id')}: required agent must remain active", failures)
        if agent_lifecycle.get("state") == "active":
            owner_entry = repository_by_id.get(agent.get("owner_repository_id"), {})
            require(owner_entry.get("lifecycle", {}).get("state") == "active",
                    f"{agent.get('agent_id')}: active agent owner is not active", failures)
            require(owner_entry.get("publisher", {}).get("identity_status") != "revoked",
                    f"{agent.get('agent_id')}: owner publisher identity is revoked", failures)
            require(owner_entry.get("supply_chain", {}).get("verification_status") != "revoked",
                    f"{agent.get('agent_id')}: owner supply-chain attestation is revoked", failures)
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
                if agent_lifecycle.get("state") == "active":
                    require(contract.get("lifecycle", {}).get("state") == "active",
                            f"{agent.get('agent_id')}: active agent references non-active contract {contract_id}", failures)
                    contract_owner = repository_by_id.get(contract.get("owner_repository_id"), {})
                    require(contract_owner.get("lifecycle", {}).get("state") == "active",
                            f"{agent.get('agent_id')}: contract owner is not active", failures)
                    require(contract_owner.get("publisher", {}).get("identity_status") != "revoked",
                            f"{agent.get('agent_id')}: contract owner publisher is revoked", failures)
                    require(contract_owner.get("supply_chain", {}).get("verification_status") != "revoked",
                            f"{agent.get('agent_id')}: contract owner supply-chain attestation is revoked", failures)
        require(agent.get("authority_mode") in {"delegated_only", "authority_free"},
                f"{agent.get('agent_id')}: agent cannot be an execution authority", failures)

    owner_roots = {
        "developer": ROOT,
        "os": Path("/tmp/tinlance-os"),
        "platform": Path("/tmp/tinlance-platform"),
        "platform_sdk": Path("/tmp/tinlance-platform_sdk"),
        "tsic": TSIC,
    }
    for contract in contracts:
        owner = contract.get("owner_repository_id")
        require(owner in repository_by_id,
                f"{contract.get('contract_id')}: unresolved contract owner", failures)
        lifecycle = contract.get("lifecycle", {})
        if lifecycle.get("state") == "deprecated":
            replacement = contract_by_id.get(lifecycle.get("replacement_id"))
            require(replacement is not None and replacement.get("lifecycle", {}).get("state") == "active",
                    f"{contract.get('contract_id')}: deprecated contract replacement must be active", failures)
        root = owner_roots.get(owner)
        if root is not None:
            artifact = root / contract.get("schema_path", "")
            require(artifact.is_file(),
                    f"{contract.get('contract_id')}: registered contract artifact is missing: {artifact}",
                    failures)

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

    actual_rule_keys = {
        (rule.get("consumer_id", ""), rule.get("contract_id", "")) for rule in rules
    }
    required_rule_keys = {
        (service.get("service_id", ""), contract_id)
        for service in services for contract_id in service.get("contract_ids", [])
    } | {
        (agent.get("agent_id", ""), contract_id)
        for agent in agents for contract_id in agent.get("required_contracts", {})
    }
    require(required_rule_keys <= actual_rule_keys,
            f"missing compatibility rules: {sorted(required_rule_keys - actual_rule_keys)}", failures)
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

    require(contract.get("format") == "tinlance-canonical-ecosystem-registry/v2",
            "TSIC registry v2 contract format drifted", failures)
    require(registry.get("schema_version") == "registry-manifest/v2",
            "registry must use the canonical v2 schema", failures)
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
    duplicate = copy.deepcopy(registry)
    duplicate["services"].append(copy.deepcopy(duplicate["services"][0]))
    require(bool(semantic_validate(duplicate, lock)), "negative test: duplicate service IDs were accepted", failures)
    authority_drift = copy.deepcopy(registry)
    authority_drift["services"][0]["authority_mode"] = "authority_free"
    require(bool(semantic_validate(authority_drift, lock)),
            "negative test: semantic validator accepted Platform authority drift", failures)
    missing_sbom = copy.deepcopy(registry)
    missing_sbom["repositories"][0]["supply_chain"].pop("sbom_uri", None)
    require(not validator.is_valid(missing_sbom),
            "negative test: schema accepted a repository without an SBOM reference", failures)
    wrong_provenance = copy.deepcopy(registry)
    wrong_provenance["repositories"][2]["supply_chain"]["provenance_uri"] = (
        "https://github.com/LloydCoder/tinlance-agent-platform/commit/" + "f" * 40
    )
    require(bool(semantic_validate(wrong_provenance, lock)),
            "negative test: provenance URI drifted from the exact reviewed SHA", failures)
    wrong_publisher = copy.deepcopy(registry)
    wrong_publisher["repositories"][0]["publisher"]["identity_uri"] = "https://github.com/other-account"
    require(bool(semantic_validate(wrong_publisher, lock)),
            "negative test: publisher identity URI did not match its ID", failures)
    quarantined = copy.deepcopy(registry)
    quarantined["services"][0]["lifecycle"]["state"] = "quarantined"
    quarantined["services"][0]["lifecycle"]["reason"] = "security review pending"
    require(bool(semantic_validate(quarantined, lock)),
            "negative test: enabled quarantined service was accepted", failures)
    deprecated_use = copy.deepcopy(registry)
    deprecated_use["services"][2]["contract_ids"].append("registry-manifest.v1")
    require(bool(semantic_validate(deprecated_use, lock)),
            "negative test: active service used a deprecated contract", failures)
    revoked_publisher = copy.deepcopy(registry)
    revoked_publisher["repositories"][2]["publisher"]["identity_status"] = "revoked"
    require(bool(semantic_validate(revoked_publisher, lock)),
            "negative test: active service accepted a revoked publisher", failures)
    revoked_supply_chain = copy.deepcopy(registry)
    revoked_supply_chain["repositories"][2]["supply_chain"]["verification_status"] = "revoked"
    require(bool(semantic_validate(revoked_supply_chain, lock)),
            "negative test: active service accepted revoked supply-chain evidence", failures)
    missing_replacement = copy.deepcopy(registry)
    missing_replacement["repositories"][0]["lifecycle"] = {
        "state": "deprecated",
        "changed_at": "2026-10-18T06:52:00Z",
        "reason": "superseded",
        "replacement_id": "missing.repository",
    }
    require(bool(semantic_validate(missing_replacement, lock)),
            "negative test: deprecated repository without an active replacement was accepted", failures)
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

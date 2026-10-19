#!/usr/bin/env python3
"""Fail closed when any mandatory TSIC TWI requirement lacks collected test evidence."""
from __future__ import annotations
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / "ecosystem.lock.json").read_text(encoding="utf-8"))
EVIDENCE = json.loads((ROOT / "docs/ecosystem/twi-tsic-test-map.json").read_text(encoding="utf-8"))
TSIC_ROOT = Path("/tmp/tinlance-tsic")
REPOSITORIES = {
    "tadl": ROOT,
    "twi": Path("/tmp/tinlance-twi"),
    "world_intelligence": Path("/tmp/tinlance-world-intelligence"),
    "platform": Path("/tmp/tinlance-platform"),
}

def main() -> None:
    requirements_path = TSIC_ROOT / "conformance/requirements/twi-web-intelligence.json"
    contract = json.loads(requirements_path.read_text(encoding="utf-8"))
    mandatory = {item["id"] for item in contract["requirements"] if item.get("mandatory") is True}
    mapped = {item["id"] for item in EVIDENCE["requirements"]}
    if mandatory != mapped:
        raise SystemExit(f"TSIC TWI evidence map drift: missing={sorted(mandatory-mapped)} extra={sorted(mapped-mandatory)}")
    for alias, path in (("twi", "integrations.twi"), ("world_intelligence", "integrations.world_intelligence")):
        pinned = LOCK["integrations"].get(alias)
        if not pinned or len(pinned.get("ref", "")) != 40:
            raise SystemExit(f"missing immutable pin for {alias}")
        if not (REPOSITORIES[alias] / ".git").exists():
            raise SystemExit(f"missing materialized repository for {alias}")
    for requirement in EVIDENCE["requirements"]:
        if not requirement.get("evidence"):
            raise SystemExit(f"{requirement['id']} has no executable evidence")
        for evidence in requirement["evidence"]:
            root = REPOSITORIES.get(evidence["repository"])
            if root is None:
                raise SystemExit(f"unknown evidence repository {evidence['repository']}")
            test_path = root / evidence["path"]
            if not test_path.is_file():
                raise SystemExit(f"{requirement['id']} references missing test file: {test_path}")
            result = subprocess.run(
                ["python", "-m", "pytest", "--collect-only", "-q", str(test_path)],
                cwd=root, text=True, capture_output=True, check=False,
            )
            if result.returncode != 0:
                raise SystemExit(f"test collection failed for {requirement['id']} {test_path}:\n{result.stdout}\n{result.stderr}")
            collected = result.stdout
            if evidence.get("test") and evidence["test"] not in collected:
                raise SystemExit(f"{requirement['id']} mapped test not collected: {evidence['test']}\n{collected}")
            if not any(line.strip().endswith(".py") or "::" in line for line in collected.splitlines()):
                raise SystemExit(f"{requirement['id']} evidence collected no test: {test_path}")
    print(f"PASS TSIC TWI executable evidence map: {len(mandatory)} mandatory requirements; all mapped tests collected")
if __name__ == "__main__":
    main()

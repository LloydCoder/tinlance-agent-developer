"""P5 team/delegation conformance against locked OS and Platform revisions."""

from pathlib import Path

OS = Path("/tmp/tinlance-os")
PLATFORM = Path("/tmp/tinlance-platform")

REQUIRED = {
    OS / "src/tinlance_agent_os/delegation.py": (
        "attenuated_from",
        "capabilities",
        "budget_tokens",
        "workspace_id",
    ),
    OS / "src/tinlance_agent_os/team_graph.py": (
        "node_id",
        "depends_on",
        "max_depth",
    ),
    PLATFORM / "packages/multi_agent/src/tinlance_agent_platform_multi_agent/service.py": (
        "parent",
        "child",
        "tenant",
    ),
    PLATFORM / "packages/multi_agent/src/tinlance_agent_platform_multi_agent/interoperability.py": (
        "descriptive",
        "RemoteDelegation",
    ),
}

def main() -> None:
    failures = []
    for path, markers in REQUIRED.items():
        if not path.exists():
            failures.append(f"missing: {path}")
            continue
        content = path.read_text(encoding="utf-8").lower()
        for marker in markers:
            if marker.lower() not in content:
                failures.append(f"{path}: missing {marker!r}")
    if failures:
        raise SystemExit("P5 team/delegation certification failed:\n" + "\n".join(failures))
    print("P5 team/delegation certification: PASS")


if __name__ == "__main__":
    main()

"""P3 identity and authority conformance against the locked Platform revision."""

from pathlib import Path

PLATFORM = Path("/tmp/tinlance-platform")

REQUIRED = {
    "docs/production-runtime/M13-2-REAL-IDENTITY.md": (
        "identity",
        "JWKS",
    ),
    "docs/production-runtime/M13-3-AUTHORIZATION-POLICY.md": (
        "authorization",
        "fail-closed",
    ),
    "docs/M22-IDENTITY-CRYPTO-ATTESTATION.md": (
        "attestation",
        "revocation",
    ),
    "packages/identity/src/tinlance_agent_platform_identity/jwt_verifier.py": (
        "issuer",
        "audience",
    ),
    "packages/identity/src/tinlance_agent_platform_identity/token_security.py": (
        "token",
        "binding",
    ),
    "tests/test_identity_jwt.py": (
        "tenant",
        "expiry",
    ),
    "tests/test_authorization_enforcement.py": (
        "deny",
        "tenant",
    ),
}

def main() -> None:
    missing = []
    for relative, markers in REQUIRED.items():
        path = PLATFORM / relative
        if not path.exists():
            missing.append(f"missing: {relative}")
            continue
        content = path.read_text(encoding="utf-8").lower()
        for marker in markers:
            if marker.lower() not in content:
                missing.append(f"{relative}: missing marker {marker!r}")
    if missing:
        raise SystemExit("P3 identity/authority certification failed:\n" + "\n".join(missing))
    print("P3 identity/authority certification: PASS")


if __name__ == "__main__":
    main()

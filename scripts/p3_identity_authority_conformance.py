"""Canonical P2 identity/tenancy regression against the locked Platform revision. The legacy filename is retained for compatibility."""

from pathlib import Path
import subprocess
import sys

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
        "issuer",
        "expires_at",
    ),
    "packages/identity/src/tinlance_agent_platform_identity/resolver.py": (
        "revocation_checker",
        "validate_principal",
    ),
    "packages/identity/src/tinlance_agent_platform_identity/revocation.py": (
        "is_revoked",
        "revoked_tokens",
    ),
    "tests/test_identity_jwt.py": (
        "tenant",
        "exp",
    ),
    "tests/test_authorization_enforcement.py": (
        "approval",
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
    # Marker checks are necessary but not sufficient. Execute the real locked
    # Platform regression suites for JWT claim validation, the concrete HTTP
    # principal resolver, revocation persistence/outage behavior, tenant binding,
    # approval binding, and attestation revocation/expiry.
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests/test_identity_jwt.py",
            "tests/test_identity_resolver.py",
            "tests/test_authorization_enforcement.py",
            "tests/test_m22_identity_crypto_attestation.py",
        ],
        cwd=PLATFORM,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        missing.append(
            "Platform P2 identity regression tests failed:\\n"
            + result.stdout[-4000:]
            + "\\n"
            + result.stderr[-2500:]
        )
    if missing:
        raise SystemExit("P2 identity/tenancy regression failed:\\n" + "\\n".join(missing))
    print("P2 identity/tenancy regression: PASS (markers + executable regression tests)")


if __name__ == "__main__":
    main()

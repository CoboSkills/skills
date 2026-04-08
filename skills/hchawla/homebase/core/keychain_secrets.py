"""
keychain_secrets.py — Secure credential loader for homebase

Priority order for each secret:
  1. macOS Keychain (via keyring library)
  2. Environment variable (set by load_dotenv or the shell)
  3. Empty string (will cause a clear error at the call site)

Usage — replace load_dotenv() calls with:
    from core.keychain_secrets import load_google_secrets
    load_google_secrets()

Migration — run once to move .env values into Keychain:
    python3 migrate_to_keychain.py
"""

import os

KEYRING_SERVICE = "openclaw-family-calendar"

# Keys stored in Keychain / env
_SECRET_KEYS = {
    "GOOGLE_CLIENT_ID":     "google-client-id",
    "GOOGLE_CLIENT_SECRET": "google-client-secret",
    "GOOGLE_REFRESH_TOKEN": "google-refresh-token",
}


_LAST_KEYRING_ERROR: str = ""


def _try_keyring(keyring_key: str) -> str:
    """Attempt to read a secret from macOS Keychain. Returns '' on any failure.

    On failure, records the exception in module-level _LAST_KEYRING_ERROR so
    callers (e.g. preflight) can surface *why* the read failed instead of
    misreporting the secret as "missing." This matters in launchd-spawned
    daemon contexts where Keychain ACL or backend issues are common.
    """
    global _LAST_KEYRING_ERROR
    try:
        import keyring as _kr
        backend = type(_kr.get_keyring()).__name__
        value = _kr.get_password(KEYRING_SERVICE, keyring_key)
        if value is None:
            _LAST_KEYRING_ERROR = f"keyring backend={backend} returned None for {keyring_key}"
            return ""
        return value
    except Exception as e:
        _LAST_KEYRING_ERROR = f"{type(e).__name__}: {e}"
        return ""


def last_keyring_error() -> str:
    """Return the most recent keyring failure reason, or '' if none."""
    return _LAST_KEYRING_ERROR


def load_google_secrets() -> None:
    """
    Populate Google OAuth env vars from Keychain (preferred) or .env fallback.
    Call this instead of load_dotenv() at the top of each script.
    """
    import pathlib

    # Step 1: Try Keychain for each key
    keychain_loaded = []
    for env_key, kr_key in _SECRET_KEYS.items():
        if not os.environ.get(env_key):
            value = _try_keyring(kr_key)
            if value:
                os.environ[env_key] = value
                keychain_loaded.append(env_key)

    if len(keychain_loaded) == len(_SECRET_KEYS):
        return  # All secrets came from Keychain — .env not needed

    # Step 2: Fall back to .env file if Keychain is empty/unavailable
    skill_dir = pathlib.Path(__file__).parent.parent
    env_file  = skill_dir / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
        except ImportError:
            # Manual parse as last resort
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, _, v = line.partition("=")
                        if k.strip() not in os.environ:
                            os.environ[k.strip()] = v.strip()


def store_secret(env_key: str, value: str) -> bool:
    """Store a single secret in macOS Keychain. Returns True on success."""
    kr_key = _SECRET_KEYS.get(env_key)
    if not kr_key:
        print(f"Unknown secret key: {env_key}")
        return False
    try:
        import keyring as _kr
        _kr.set_password(KEYRING_SERVICE, kr_key, value)
        return True
    except Exception as e:
        print(f"Keychain write failed for {env_key}: {e}")
        return False


def verify_secrets() -> list[str]:
    """Return a list of missing required secrets (for startup health checks)."""
    load_google_secrets()
    missing = []
    for env_key in _SECRET_KEYS:
        if not os.environ.get(env_key):
            missing.append(env_key)
    return missing

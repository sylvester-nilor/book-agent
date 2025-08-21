import subprocess
from typing import Optional
import google.auth
from google.auth.transport.requests import AuthorizedSession, Request


def get_auth_token() -> Optional[str]:
    try:
        auth_token = subprocess.check_output(
            ["gcloud", "auth", "print-identity-token"],
            text=True,
            stderr=subprocess.PIPE
        ).strip()
        print(f"Got auth token: {auth_token[:20]}...")
        return auth_token
    except subprocess.CalledProcessError as e:
        print(f"Error getting auth token: {e}")
        return None


def get_auth_session() -> AuthorizedSession:
    credentials, _ = google.auth.default()
    if not credentials.valid:
        credentials.refresh(Request())
    return AuthorizedSession(credentials)


if __name__ == "__main__":
    token = get_auth_token()
    if token:
        print("✅ Auth token retrieved successfully")
    else:
        print("❌ Failed to retrieve auth token")

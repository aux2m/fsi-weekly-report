#!/usr/bin/env python3
"""
One-time Outlook authentication setup.
Opens browser for Microsoft login, stores token cache for automated runs.

Run this once:
    python setup_outlook.py

After successful auth, the pipeline will use the cached refresh token
automatically (including from Task Scheduler).
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

import msal

SCOPES = ["Mail.ReadWrite"]
TOKEN_CACHE_PATH = Path.home() / ".bennett-kew-tokens.json"


def main():
    client_id = os.environ.get("MICROSOFT_CLIENT_ID")
    tenant_id = os.environ.get("MICROSOFT_TENANT_ID")

    if not client_id or not tenant_id:
        print("ERROR: Missing environment variables.")
        print("Add these to your .env file:")
        print("  MICROSOFT_CLIENT_ID=<your-app-client-id>")
        print("  MICROSOFT_TENANT_ID=<your-directory-tenant-id>")
        print()
        print("Setup steps:")
        print("  1. Go to https://entra.microsoft.com")
        print("  2. App registrations > New registration")
        print("  3. Name: 'BennettKew Report Automation'")
        print("  4. Redirect URI: Public client > http://localhost")
        print("  5. API permissions > Add > Microsoft Graph > Mail.ReadWrite")
        print("  6. Copy Application ID and Directory ID to .env")
        sys.exit(1)

    # Load existing cache (if any)
    cache = msal.SerializableTokenCache()
    if TOKEN_CACHE_PATH.exists():
        cache.deserialize(TOKEN_CACHE_PATH.read_text(encoding="utf-8"))

    app = msal.PublicClientApplication(
        client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
        token_cache=cache,
    )

    # Check if already authenticated
    accounts = app.get_accounts()
    if accounts:
        print(f"Found cached account: {accounts[0].get('username', 'unknown')}")
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and "access_token" in result:
            print("Token is still valid! No re-authentication needed.")
            _save_cache(cache)
            _verify_token(result["access_token"])
            return

    # Interactive login — opens browser
    print("\nOpening browser for Microsoft login...")
    print("(If browser doesn't open, use the device code flow below)\n")

    try:
        result = app.acquire_token_interactive(
            SCOPES,
            prompt="select_account",
        )
    except Exception:
        # Fallback to device code flow (works in headless terminals)
        print("Browser login failed. Using device code flow instead.\n")
        flow = app.initiate_device_flow(SCOPES)
        if "user_code" not in flow:
            print(f"ERROR: Could not create device flow: {flow}")
            sys.exit(1)
        print(flow["message"])
        result = app.acquire_token_by_device_flow(flow)

    if "access_token" not in result:
        print(f"\nERROR: Authentication failed.")
        print(f"  Error: {result.get('error', 'unknown')}")
        print(f"  Description: {result.get('error_description', 'no details')}")
        sys.exit(1)

    _save_cache(cache)

    print(f"\nAuthentication successful!")
    print(f"  Account: {result.get('id_token_claims', {}).get('preferred_username', 'unknown')}")
    print(f"  Token cached at: {TOKEN_CACHE_PATH}")
    print(f"\nThe pipeline will now create Outlook drafts automatically.")

    _verify_token(result["access_token"])


def _save_cache(cache: msal.SerializableTokenCache):
    """Save token cache to disk."""
    if cache.has_state_changed:
        TOKEN_CACHE_PATH.write_text(cache.serialize(), encoding="utf-8")


def _verify_token(access_token: str):
    """Quick API call to verify the token works."""
    import requests
    try:
        resp = requests.get(
            "https://graph.microsoft.com/v1.0/me",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        if resp.status_code == 200:
            user = resp.json()
            print(f"\nVerified: {user.get('displayName', '')} ({user.get('mail', '')})")
        else:
            print(f"\nWarning: Token verification returned {resp.status_code}")
    except Exception as e:
        print(f"\nWarning: Could not verify token: {e}")


if __name__ == "__main__":
    main()

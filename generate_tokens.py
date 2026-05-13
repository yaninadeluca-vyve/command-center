"""
generate_tokens.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Run this ONCE locally for each Gmail inbox to generate
the OAuth tokens you'll paste into GitHub Secrets.

Usage:
  pip install google-auth-oauthlib google-api-python-client
  python generate_tokens.py

You'll need a credentials.json from Google Cloud Console.
The script walks you through it.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

INBOXES = [
    "main",
    "vyve",
    "infusive",
]


def authorize_inbox(name: str):
    print(f"\n{'━'*50}")
    print(f"  Authorizing Gmail inbox: {name.upper()}")
    print(f"{'━'*50}")

    creds_file = input(
        f"\n  Paste the path to credentials.json for '{name}' inbox\n"
        f"  (download from Google Cloud Console > APIs & Services > Credentials):\n  > "
    ).strip().strip('"')

    if not os.path.exists(creds_file):
        print(f"  ✗ File not found: {creds_file}")
        return

    flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
    creds = flow.run_local_server(port=0)

    # Read raw credentials.json
    with open(creds_file) as f:
        creds_json_str = f.read()

    token_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
    }
    token_json_str = json.dumps(token_data)

    print(f"\n  ✓ Authorization successful!\n")
    print(f"  ── Copy the values below into GitHub Secrets ──\n")
    print(f"  Secret name:  GMAIL_CREDENTIALS_{name.upper()}")
    print(f"  Secret value: {creds_json_str}\n")
    print(f"  Secret name:  GMAIL_TOKEN_{name.upper()}")
    print(f"  Secret value: {token_json_str}\n")

    # Also save locally for reference
    with open(f"token_{name}.json", "w") as f:
        f.write(token_json_str)
    print(f"  (Also saved to token_{name}.json for reference)")


if __name__ == "__main__":
    print("\n  Gmail Token Generator — Command Center")
    print("  Run this once per inbox, then paste the output into GitHub Secrets.\n")

    for inbox_name in INBOXES:
        do_it = input(f"  Authorize '{inbox_name}' inbox? (y/n): ").strip().lower()
        if do_it == "y":
            authorize_inbox(inbox_name)

    print("\n  ✓ All done. You can now add the secrets to GitHub.")
    print("  See SETUP.md for the next steps.\n")

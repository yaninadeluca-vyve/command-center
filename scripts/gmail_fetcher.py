"""
gmail_fetcher.py
Fetches unread/unanswered emails from one Gmail inbox.
"""

import os
import json
import base64
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def _get_service(credentials_json: str, token_json: str):
    creds = None
    if token_json:
        creds = Credentials.from_authorized_user_info(json.loads(token_json), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise RuntimeError(
                "Token is missing or invalid. Run generate_tokens.py locally first."
            )
    return build("gmail", "v1", credentials=creds)


def _decode_body(payload):
    """Extract plain text body from a Gmail message payload."""
    body = ""
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                data = part["body"].get("data", "")
                body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                break
            elif "parts" in part:
                body = _decode_body(part)
                if body:
                    break
    elif payload.get("mimeType") == "text/plain":
        data = payload["body"].get("data", "")
        body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    return body[:2000]  # cap at 2000 chars to save tokens


def fetch_emails(credentials_json: str, token_json: str, label: str,
                 lookback_hours: int = 24, max_results: int = 20) -> list[dict]:
    """
    Returns a list of email dicts for Claude to triage.
    Each dict has: subject, sender, received_iso, body_preview, thread_id, label
    """
    service = _get_service(credentials_json, token_json)

    since = datetime.datetime.utcnow() - datetime.timedelta(hours=lookback_hours)
    query = f"after:{int(since.timestamp())} -from:me -category:promotions -category:social"

    results = service.users().messages().list(
        userId="me", q=query, maxResults=max_results
    ).execute()

    messages = results.get("messages", [])
    emails = []

    for msg_ref in messages:
        msg = service.users().messages().get(
            userId="me", id=msg_ref["id"], format="full"
        ).execute()

        headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
        subject = headers.get("Subject", "(no subject)")
        sender = headers.get("From", "unknown")
        date_str = headers.get("Date", "")

        try:
            from email.utils import parsedate_to_datetime
            received = parsedate_to_datetime(date_str).isoformat()
        except Exception:
            received = datetime.datetime.utcnow().isoformat()

        body = _decode_body(msg["payload"])

        emails.append({
            "subject": subject,
            "sender": sender,
            "received_iso": received,
            "body_preview": body,
            "thread_id": msg.get("threadId", ""),
            "message_id": msg_ref["id"],
            "source_label": label,
            "link": f"https://mail.google.com/mail/u/0/#inbox/{msg_ref['id']}",
        })

    return emails

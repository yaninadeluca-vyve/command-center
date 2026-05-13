"""
claude_triage.py
Sends raw emails, Slack messages, and Fireflies meetings to Claude.
Returns structured dashboard items ready for data.json.
"""

import json
import datetime
import requests


ANTHROPIC_API = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-20250514"


def _call_claude(api_key: str, system: str, user_prompt: str) -> str:
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {
        "model": MODEL,
        "max_tokens": 4000,
        "system": system,
        "messages": [{"role": "user", "content": user_prompt}],
    }
    resp = requests.post(ANTHROPIC_API, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]


def triage_all(
    api_key: str,
    boss_context: str,
    emails: list[dict],
    slack_messages: list[dict],
    fireflies_meetings: list[dict],
    existing_vendor_names: list[str],
) -> list[dict]:
    """
    Returns a list of dashboard item dicts matching the data.json schema.
    """
    if not emails and not slack_messages and not fireflies_meetings:
        print("  Nothing to triage.")
        return []

    system_prompt = f"""
You are an executive assistant AI triaging incoming communications for a busy medical executive.

{boss_context}

You will receive raw emails, Slack messages, and Fireflies meeting action items.
Your job is to analyze them and return a JSON array of dashboard items.

IMPORTANT RULES:
- Only include items that genuinely need attention or awareness. Skip newsletters, 
  automated notifications, calendar confirmations, and spam.
- Merge related items from the same thread into ONE item. Do not duplicate.
- Each item must follow this exact schema:

{{
  "id": "auto-YYYYMMDD-N",           // e.g. auto-20260512-1
  "urgency": "red|yellow|green",
  "entity": "VYVE|Infusive",
  "category": "vendor|client|pharmacy|clinical|other",
  "categoryLabel": "Vendor|Client|Pharmacy|Clinical|Other",
  "vendor": "Vendor name or null",   // use null if not applicable
  "title": "Short title, max 8 words",
  "summary": "1-2 sentences of context. What is happening.",
  "source": "gmail|slack|fireflies",
  "sourceLabel": "Gmail — main|Gmail — VYVE|Gmail — Infusive|Slack — #channel|Fireflies",
  "from": "sender name or email",
  "received": "ISO 8601 datetime",
  "status": "open",
  "link": "direct URL if available, else null",
  "actionNeeded": "One sentence: exactly what he needs to do"
}}

Known vendor names (use these exact strings when matching):
{json.dumps(existing_vendor_names)}

Return ONLY a valid JSON array. No markdown, no explanation, no preamble.
If there is nothing worth flagging, return an empty array: []
"""

    # Build the user prompt with all raw data
    sections = []

    if emails:
        email_text = "\n\n".join([
            f"--- EMAIL ---\n"
            f"From: {e['sender']}\n"
            f"Subject: {e['subject']}\n"
            f"Received: {e['received_iso']}\n"
            f"Inbox: {e['source_label']}\n"
            f"Link: {e.get('link','')}\n"
            f"Body preview:\n{e['body_preview']}"
            for e in emails
        ])
        sections.append(f"# EMAILS\n\n{email_text}")

    if slack_messages:
        slack_text = "\n\n".join([
            f"--- SLACK MESSAGE ---\n"
            f"Channel: {m['channel']}\n"
            f"From: {m['sender']}\n"
            f"Received: {m['received_iso']}\n"
            f"Link: {m.get('link','')}\n"
            f"Message:\n{m['text']}"
            for m in slack_messages
        ])
        sections.append(f"# SLACK MESSAGES\n\n{slack_text}")

    if fireflies_meetings:
        ff_text = "\n\n".join([
            f"--- MEETING ---\n"
            f"Title: {m['title']}\n"
            f"Date: {m['date_iso']}\n"
            f"Attendees: {m['attendees']}\n"
            f"Link: {m.get('link','')}\n"
            f"Summary: {m['summary']}\n"
            f"Action items:\n" + "\n".join(f"  - {a}" for a in m['action_items'])
            for m in fireflies_meetings
        ])
        sections.append(f"# FIREFLIES MEETINGS\n\n{ff_text}")

    user_prompt = "\n\n".join(sections)

    print("  Sending to Claude for triage...")
    raw = _call_claude(api_key, system_prompt, user_prompt)

    # Clean and parse
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        items = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"  JSON parse error: {e}")
        print(f"  Raw output: {raw[:500]}")
        return []

    # Stamp IDs with today's date
    today = datetime.datetime.utcnow().strftime("%Y%m%d")
    for i, item in enumerate(items):
        item["id"] = f"auto-{today}-{i+1}"
        item.setdefault("status", "open")

    print(f"  Claude returned {len(items)} items.")
    return items

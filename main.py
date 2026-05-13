"""
main.py
Orchestrates the full daily pipeline:
  1. Fetch emails from all Gmail inboxes
  2. Fetch Slack messages from configured channels
  3. Fetch Fireflies meeting summaries + action items
  4. Send everything to Claude for triage
  5. Merge with existing data.json (preserving manual items + statuses)
  6. Deploy updated data.json to Netlify
"""

import os
import sys
import json
import datetime

# Add scripts dir to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))

from gmail_fetcher import fetch_emails
from slack_fetcher import fetch_slack_messages
from fireflies_fetcher import fetch_fireflies
from claude_triage import triage_all
from netlify_deploy import deploy_data_json

# Config
from config import (
    GMAIL_INBOXES, GMAIL_MAX_EMAILS, GMAIL_LOOKBACK_HOURS,
    SLACK_CHANNELS, SLACK_LOOKBACK_HOURS, SLACK_MAX_MESSAGES,
    FIREFLIES_LOOKBACK_HOURS,
    BOSS_CONTEXT,
)

# Preset lists (kept in sync with dashboard)
VENDORS   = ["Influex", "UPQODE", "One Billion Media", "Guide Post Marketing", "SSRP", "Podcasts"]
CLIENTS   = ["iCryo", "Guardian", "Intervene MD", "Hydrate IV Bar"]
PHARMACIES = ["Olympia", "Ageless", "Strive", "Tandem", "Wells", "GenoGenix", "Empower", "Progress", "McGuff"]
ALL_NAMES = VENDORS + CLIENTS + PHARMACIES


def load_existing_data() -> dict:
    """Load existing data.json if it exists (to preserve manual items and statuses)."""
    path = os.path.join(os.path.dirname(__file__), "dashboard", "data.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {"items": [], "calendar": [], "vendors": VENDORS, "clients": CLIENTS, "pharmacies": PHARMACIES}


def merge_items(auto_items: list, existing_data: dict) -> list:
    """
    Keep manual items (added via dashboard) and preserve statuses.
    Replace all auto-generated items with fresh ones from this run.
    """
    manual_items = [i for i in existing_data.get("items", []) if not i.get("id", "").startswith("auto-")]
    return auto_items + manual_items


def build_calendar_from_fireflies(meetings: list) -> list:
    """Convert today's Fireflies meetings into calendar entries for the sidebar."""
    today = datetime.datetime.utcnow().date()
    calendar = []
    for m in meetings:
        try:
            dt = datetime.datetime.fromisoformat(m["date_iso"])
            if dt.date() == today:
                calendar.append({
                    "id": f"cal-{dt.strftime('%H%M')}",
                    "time": dt.strftime("%H:%M"),
                    "title": m["title"],
                    "duration": "—",
                    "attendees": m["attendees"] or "—",
                    "location": "Fireflies",
                    "entity": "Infusive",
                    "prepNeeded": len(m.get("action_items", [])) > 0,
                    "prepNote": m["action_items"][0] if m.get("action_items") else "",
                })
        except Exception:
            continue
    return calendar


def main():
    print("━━━ Command Center — Daily Pipeline ━━━")
    print(f"Run time: {datetime.datetime.utcnow().isoformat()} UTC\n")

    # ── API KEYS ──────────────────────────────────────────
    anthropic_key  = os.environ.get("ANTHROPIC_API_KEY", "")
    slack_token    = os.environ.get("SLACK_BOT_TOKEN", "")
    fireflies_key  = os.environ.get("FIREFLIES_API_KEY", "")
    netlify_token  = os.environ.get("NETLIFY_TOKEN", "")
    netlify_site   = os.environ.get("NETLIFY_SITE_ID", "")

    if not anthropic_key:
        print("ERROR: ANTHROPIC_API_KEY not set"); sys.exit(1)
    if not netlify_token or not netlify_site:
        print("ERROR: NETLIFY_TOKEN or NETLIFY_SITE_ID not set"); sys.exit(1)

    all_emails        = []
    all_slack         = []
    all_fireflies     = []

    # ── GMAIL ─────────────────────────────────────────────
    print("── Gmail ──")
    for inbox in GMAIL_INBOXES:
        creds_json = os.environ.get(inbox["credentials_env"], "")
        token_json = os.environ.get(inbox["token_env"], "")
        if not creds_json or not token_json:
            print(f"  Skipping {inbox['label']} — credentials not set")
            continue
        print(f"  Fetching {inbox['label']}...")
        try:
            emails = fetch_emails(
                creds_json, token_json, inbox["label"],
                lookback_hours=GMAIL_LOOKBACK_HOURS,
                max_results=GMAIL_MAX_EMAILS,
            )
            print(f"  → {len(emails)} emails")
            all_emails.extend(emails)
        except Exception as e:
            print(f"  Error: {e}")

    # ── SLACK ─────────────────────────────────────────────
    print("\n── Slack ──")
    if slack_token:
        try:
            msgs = fetch_slack_messages(
                slack_token, SLACK_CHANNELS,
                lookback_hours=SLACK_LOOKBACK_HOURS,
                max_per_channel=SLACK_MAX_MESSAGES,
            )
            print(f"  → {len(msgs)} messages across {len(SLACK_CHANNELS)} channels")
            all_slack = msgs
        except Exception as e:
            print(f"  Error: {e}")
    else:
        print("  Skipping — SLACK_BOT_TOKEN not set")

    # ── FIREFLIES ─────────────────────────────────────────
    print("\n── Fireflies ──")
    if fireflies_key:
        try:
            meetings = fetch_fireflies(fireflies_key, lookback_hours=FIREFLIES_LOOKBACK_HOURS)
            print(f"  → {len(meetings)} meetings")
            all_fireflies = meetings
        except Exception as e:
            print(f"  Error: {e}")
    else:
        print("  Skipping — FIREFLIES_API_KEY not set")

    # ── CLAUDE TRIAGE ─────────────────────────────────────
    print("\n── Claude triage ──")
    auto_items = triage_all(
        api_key=anthropic_key,
        boss_context=BOSS_CONTEXT,
        emails=all_emails,
        slack_messages=all_slack,
        fireflies_meetings=all_fireflies,
        existing_vendor_names=ALL_NAMES,
    )

    # ── MERGE & BUILD DATA.JSON ───────────────────────────
    print("\n── Building data.json ──")
    existing = load_existing_data()
    merged_items = merge_items(auto_items, existing)

    cal_from_fireflies = build_calendar_from_fireflies(all_fireflies)
    existing_cal = [c for c in existing.get("calendar", []) if not c.get("id","").startswith("cal-")]
    final_calendar = cal_from_fireflies + existing_cal

    data = {
        "lastUpdated": datetime.datetime.utcnow().isoformat(),
        "vendors": VENDORS,
        "clients": CLIENTS,
        "pharmacies": PHARMACIES,
        "calendar": final_calendar,
        "items": merged_items,
    }

    # Save locally (so GitHub has a copy too)
    out_path = os.path.join(os.path.dirname(__file__), "dashboard", "data.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  Saved {len(merged_items)} items to data.json")

    # ── NETLIFY DEPLOY ─────────────────────────────────────
    print("\n── Netlify deploy ──")
    try:
        deploy_data_json(netlify_token, netlify_site, data)
        print("  ✓ Dashboard updated on Netlify")
    except Exception as e:
        print(f"  Deploy error: {e}"); sys.exit(1)

    print("\n━━━ Done ━━━")


if __name__ == "__main__":
    main()

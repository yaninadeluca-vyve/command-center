"""
fireflies_fetcher.py
Fetches recent meeting summaries and action items from Fireflies.ai
"""

import datetime
import requests


FIREFLIES_API = "https://api.fireflies.ai/graphql"


def fetch_fireflies(api_key: str, lookback_hours: int = 48) -> list[dict]:
    """
    Returns a list of meeting dicts for Claude to triage.
    Each dict has: title, date_iso, attendees, summary, action_items, link
    """
    since = datetime.datetime.utcnow() - datetime.timedelta(hours=lookback_hours)
    since_ts = int(since.timestamp() * 1000)  # Fireflies uses milliseconds

    query = """
    query GetTranscripts($fromDate: Long) {
      transcripts(fromDate: $fromDate) {
        id
        title
        date
        duration
        meeting_link
        host_email
        participants
        summary {
          overview
          action_items
          keywords
        }
      }
    }
    """

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(
            FIREFLIES_API,
            json={"query": query, "variables": {"fromDate": since_ts}},
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  Fireflies API error: {e}")
        return []

    transcripts = data.get("data", {}).get("transcripts", []) or []
    meetings = []

    for t in transcripts:
        summary_block = t.get("summary") or {}
        overview = summary_block.get("overview", "") or ""
        action_items_raw = summary_block.get("action_items", "") or ""

        # Convert action items string to list
        action_items = [
            line.strip("•- ").strip()
            for line in action_items_raw.split("\n")
            if line.strip() and line.strip() not in ("•", "-")
        ]

        participants = t.get("participants") or []
        if isinstance(participants, list):
            attendees = ", ".join(participants[:6])
        else:
            attendees = str(participants)

        ts_ms = t.get("date", 0) or 0
        try:
            date_iso = datetime.datetime.utcfromtimestamp(ts_ms / 1000).isoformat()
        except Exception:
            date_iso = datetime.datetime.utcnow().isoformat()

        meetings.append({
            "title": t.get("title", "Untitled meeting"),
            "date_iso": date_iso,
            "attendees": attendees,
            "summary": overview[:1000],
            "action_items": action_items[:10],  # cap at 10
            "link": t.get("meeting_link") or f"https://app.fireflies.ai/view/{t.get('id','')}",
            "source_label": "Fireflies",
        })

    return meetings

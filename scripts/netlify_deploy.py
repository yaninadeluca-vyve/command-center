"""
netlify_deploy.py
Pushes a new data.json to Netlify without touching the rest of the site.
Uses the snippet/file API to update a single file in place.
"""

import json
import requests


NETLIFY_API = "https://api.netlify.com/api/v1"


def deploy_data_json(token: str, site_id: str, data: dict) -> bool:
    """
    Updates data.json on the live Netlify site without affecting index.html
    or any other files. Uses the site files API.
    Returns True on success.
    """
    content = json.dumps(data, indent=2, ensure_ascii=False)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Get the latest deploy ID for this site
    site_resp = requests.get(
        f"{NETLIFY_API}/sites/{site_id}",
        headers=headers,
        timeout=30,
    )
    site_resp.raise_for_status()
    site_data = site_resp.json()
    deploy_id = site_data.get("published_deploy", {}).get("id")

    if not deploy_id:
        print("  No published deploy found — upload the dashboard folder to Netlify manually first")
        return False

    print(f"  Updating data.json in deploy {deploy_id}...")

    # Update data.json in the existing deploy
    upload_resp = requests.put(
        f"{NETLIFY_API}/deploys/{deploy_id}/files/data.json",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/octet-stream",
        },
        data=content.encode("utf-8"),
        timeout=30,
    )
    upload_resp.raise_for_status()
    print("  ✓ data.json updated on Netlify — index.html untouched")
    return True

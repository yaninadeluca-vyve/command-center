"""
netlify_deploy.py
Pushes a new data.json to Netlify via the Files API.
No redeployment needed — the file updates instantly.
"""

import json
import hashlib
import requests


NETLIFY_API = "https://api.netlify.com/api/v1"


def deploy_data_json(token: str, site_id: str, data: dict) -> bool:
    """
    Uploads data.json directly to the Netlify site.
    Returns True on success.
    """
    content = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
    sha1 = hashlib.sha1(content).hexdigest()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/octet-stream",
    }

    # Step 1: create a new deploy
    deploy_resp = requests.post(
        f"{NETLIFY_API}/sites/{site_id}/deploys",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"files": {"/data.json": sha1}},
        timeout=30,
    )
    deploy_resp.raise_for_status()
    deploy = deploy_resp.json()
    deploy_id = deploy["id"]
    required = deploy.get("required", [])

    print(f"  Created Netlify deploy {deploy_id}")

    # Step 2: upload the file if required
    if sha1 in required:
        upload_resp = requests.put(
            f"{NETLIFY_API}/deploys/{deploy_id}/files/data.json",
            headers=headers,
            data=content,
            timeout=30,
        )
        upload_resp.raise_for_status()
        print("  Uploaded data.json to Netlify")
    else:
        print("  data.json unchanged — Netlify skipped upload")

    return True

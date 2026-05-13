import json
import os


def deploy_data_json(token: str, site_id: str, data: dict) -> bool:
    out_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "dashboard", "data.json"
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("  ✓ data.json written locally")
    print("  GitHub Actions commits and pushes — Netlify redeploys automatically")
    return True

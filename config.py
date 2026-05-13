# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  COMMAND CENTER — CONFIG
#  All your settings live here. Nothing else needs editing.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ── GMAIL INBOXES ──────────────────────────────────────
# Add or remove inboxes here. Label is shown on the dashboard.
# credentials_env is the name of the secret you'll add in GitHub.
GMAIL_INBOXES = [
    {
        "label": "Gmail — main",
        "credentials_env": "GMAIL_CREDENTIALS_MAIN",
        "token_env": "GMAIL_TOKEN_MAIN",
    },
    {
        "label": "Gmail — VYVE",
        "credentials_env": "GMAIL_CREDENTIALS_VYVE",
        "token_env": "GMAIL_TOKEN_VYVE",
    },
    {
        "label": "Gmail — Infusive",
        "credentials_env": "GMAIL_CREDENTIALS_INFUSIVE",
        "token_env": "GMAIL_TOKEN_INFUSIVE",
    },
]

# Max emails to pull per inbox per run (keep under 30 to control API cost)
GMAIL_MAX_EMAILS = 20

# Only pull emails from the last N hours
GMAIL_LOOKBACK_HOURS = 24


# ── SLACK CHANNELS ──────────────────────────────────────
# To add a channel later: just add a new line below, e.g.:
#   "new-channel-name",
SLACK_CHANNELS = [
    "atomic-funnels",
    "simplex-media",
    "onebillionmedia",
    "influex-vyve",
    "guide-post-marketing",
    "maeve-ferguson-consulting",
    "vision-labs",
    "born-to-influence",
    "moderate-genius",
]

# Only pull messages from the last N hours
SLACK_LOOKBACK_HOURS = 24

# Max messages to pull per channel per run
SLACK_MAX_MESSAGES = 10


# ── FIREFLIES ───────────────────────────────────────────
# Pull meetings from the last N hours
FIREFLIES_LOOKBACK_HOURS = 48


# ── BOSS CONTEXT (used by Claude for triage) ────────────
BOSS_CONTEXT = """
You are triaging open items for a medical executive who runs two companies:
- VYVE: a clinical/medical practice
- Infusive: a business development and partnerships company

His standing priorities in order:
1. Patient outcomes and clinical quality (VYVE) — always highest urgency
2. Partnerships and business development (Infusive)
3. Operational efficiency and vendor management

Urgency rules:
- red: needs his attention or decision TODAY (patient issues, contract deadlines, 
  time-sensitive partner replies, anything explicitly flagged as urgent)
- yellow: needs attention within 2-3 days (vendor approvals, follow-ups, 
  ongoing projects needing input)
- green: FYI or no hard deadline (updates, informational threads, 
  non-urgent kudos or invitations)

Entity assignment:
- VYVE: anything clinical, patient-related, or referencing VYVE directly
- Infusive: vendor relationships, BD, marketing, partnerships, operations

Category assignment:
- vendor: marketing/creative agencies and service providers
- client: partner clinics or client organizations
- pharmacy: any pharmacy or compounding partner
- clinical: patient care, protocols, medical staff
"""


# ── NETLIFY ─────────────────────────────────────────────
# Your Netlify site ID and the path to data.json in your repo
NETLIFY_SITE_ID_ENV = "NETLIFY_SITE_ID"
NETLIFY_TOKEN_ENV = "NETLIFY_TOKEN"


# ── SCHEDULE ────────────────────────────────────────────
# Cron runs daily at 7:00 AM Eastern (11:00 UTC)
# Change in .github/workflows/daily_update.yml if needed
SCHEDULE_UTC = "0 11 * * *"

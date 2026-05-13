# Command Center — Automation Setup Guide
## Path 3: Claude API + GitHub Actions

Estimated time: **60–90 minutes** (mostly waiting for pages to load).  
Technical skill required: **none** — just copying and pasting.

---

## Overview of what you're setting up

```
Gmail × 3  ──┐
Slack       ──┼──▶  Python script  ──▶  Claude API  ──▶  data.json  ──▶  Netlify dashboard
Fireflies   ──┘         ↑
                  GitHub Actions
                  (runs at 7am daily)
```

---

## Step 1 — Create a GitHub account and repo (10 min)

1. Go to [github.com](https://github.com) → Sign up (free)
2. Click **"New repository"** (green button)
   - Name: `command-center`
   - Set to **Private**
   - Click **Create repository**
3. Upload the entire automation folder to the repo:
   - Click **"uploading an existing file"** on the repo page
   - Drag and drop all files from the zip
   - Click **Commit changes**

---

## Step 2 — Get your API keys (30 min)

You need 4 sets of credentials. Do them in any order.

---

### 2a. Anthropic API key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign in → click **"API Keys"** in the left sidebar
3. Click **"Create Key"** → name it `command-center`
4. Copy the key (starts with `sk-ant-...`)
5. Save it — you'll use it in Step 3

---

### 2b. Gmail — for each of the 3 inboxes

Repeat this for **main**, **VYVE**, and **Infusive** inboxes.

**First, create a Google Cloud project (only once):**

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click the project dropdown at the top → **New Project**
   - Name: `command-center`
   - Click **Create**
3. Go to **APIs & Services → Enable APIs**
4. Search for **Gmail API** → click it → **Enable**
5. Go to **APIs & Services → OAuth consent screen**
   - Choose **External** → **Create**
   - App name: `Command Center`
   - Add your email as a test user
   - Save and continue through all steps
6. Go to **APIs & Services → Credentials**
   - Click **Create Credentials → OAuth client ID**
   - Application type: **Desktop app**
   - Name: `command-center`
   - Click **Create** → **Download JSON**
   - This is your `credentials.json`

**Then, run the token generator (once per inbox):**

1. On your computer, open Terminal (Mac) or Command Prompt (Windows)
2. Run:
   ```
   pip install google-auth-oauthlib google-api-python-client
   python generate_tokens.py
   ```
3. Follow the prompts — it opens a browser to authorize each Gmail account
4. Copy the output values — you'll paste them into GitHub Secrets in Step 3

---

### 2c. Slack Bot Token

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click **Create New App → From scratch**
   - Name: `Command Center`
   - Choose your boss's Slack workspace
3. Go to **OAuth & Permissions** in the left sidebar
4. Under **Bot Token Scopes**, click **Add an OAuth Scope** and add:
   - `channels:read`
   - `channels:history`
   - `groups:read`
   - `groups:history`
   - `users:read`
5. Scroll up → click **Install to Workspace** → Allow
6. Copy the **Bot User OAuth Token** (starts with `xoxb-...`)
7. **Add the bot to each channel:**
   - In Slack, go to each channel in the list below
   - Type `/invite @Command Center`
   - Repeat for all 9 channels:
     `#atomic-funnels` `#simplex-media` `#onebillionmedia` `#influex-vyve`
     `#guide-post-marketing` `#maeve-ferguson-consulting` `#vision-labs`
     `#born-to-influence` `#moderate-genius`

---

### 2d. Fireflies API Key

1. Go to [app.fireflies.ai](https://app.fireflies.ai) → log in
2. Click your avatar (top right) → **Integrations**
3. Scroll to **API Access** → click **Generate API Key**
4. Copy the key

---

### 2e. Netlify Token + Site ID

1. Go to [app.netlify.com](https://app.netlify.com) → log in
2. Click your avatar → **User settings → Applications**
3. Under **Personal access tokens** → **New access token**
   - Name: `command-center`
   - Copy the token
4. Go back to your site → **Site settings → General**
   - Copy the **Site ID** (looks like `abc12345-...`)

---

## Step 3 — Add all secrets to GitHub (10 min)

1. Go to your `command-center` repo on GitHub
2. Click **Settings → Secrets and variables → Actions**
3. Click **New repository secret** for each one below:

| Secret name | Where to get it |
|---|---|
| `ANTHROPIC_API_KEY` | Step 2a |
| `GMAIL_CREDENTIALS_MAIN` | generate_tokens.py output |
| `GMAIL_TOKEN_MAIN` | generate_tokens.py output |
| `GMAIL_CREDENTIALS_VYVE` | generate_tokens.py output |
| `GMAIL_TOKEN_VYVE` | generate_tokens.py output |
| `GMAIL_CREDENTIALS_INFUSIVE` | generate_tokens.py output |
| `GMAIL_TOKEN_INFUSIVE` | generate_tokens.py output |
| `SLACK_BOT_TOKEN` | Step 2c |
| `FIREFLIES_API_KEY` | Step 2d |
| `NETLIFY_TOKEN` | Step 2e |
| `NETLIFY_SITE_ID` | Step 2e |

---

## Step 4 — Test it manually (5 min)

1. In your GitHub repo, click the **Actions** tab
2. Click **Daily Dashboard Update** in the left sidebar
3. Click **Run workflow → Run workflow** (green button)
4. Watch the logs — it should complete in ~2–3 minutes
5. Open your Netlify dashboard URL — it should show real data

If something fails, the log will tell you exactly which step and why.
Most common issues:
- A secret was pasted with a trailing space → re-paste it
- The Slack bot wasn't invited to a channel → run `/invite @Command Center`
- Gmail token expired → re-run `generate_tokens.py` for that inbox

---

## Step 5 — Adding a new Slack channel later

Open `config.py` and add one line inside `SLACK_CHANNELS`:

```python
SLACK_CHANNELS = [
    "atomic-funnels",
    "your-new-channel",   # ← add here
    ...
]
```

Then commit the change to GitHub, and invite the bot to the new channel in Slack.
That's it — next morning's run will include it.

---

## Schedule

The script runs automatically every day at **7:00 AM Eastern**.
To change the time, edit this line in `.github/workflows/daily_update.yml`:

```yaml
- cron: "0 11 * * *"   # 11:00 UTC = 7:00 AM Eastern
```

Use [crontab.guru](https://crontab.guru) to convert times.

---

## Cost estimate

| Service | Cost |
|---|---|
| GitHub Actions | Free (2,000 min/month free tier) |
| Anthropic API | ~$3–8/month (depends on email volume) |
| Netlify | Free tier is enough |
| Google Cloud | Free (Gmail API has no cost) |
| Slack API | Free |
| Fireflies API | Included in your existing plan |
| **Total** | **~$3–8/month** |

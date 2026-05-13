# Command Center — Setup & Daily Workflow Guide

## What's in this folder

| File | Purpose |
|---|---|
| `index.html` | The dashboard — open this in any browser |
| `data.json` | The data file — **you edit this daily** |
| `GUIDE.md` | This file |

---

## One-time setup on Netlify (5 minutes)

1. Go to [netlify.com](https://netlify.com) and create a free account
2. From your dashboard, click **"Add new site" → "Deploy manually"**
3. Drag and drop this entire folder onto the Netlify deploy area
4. Netlify gives you a URL like `https://your-site-name.netlify.app`
5. Share that URL with your boss — bookmark it on his phone and computer

**To update the data daily:**
- Edit `data.json` (see below)
- Go to Netlify → your site → **Deploys → "Deploy manually"** → drag the folder again
- Takes ~10 seconds. The URL stays the same.

> **Tip:** Rename the site to something clean in Netlify settings, e.g. `dr-smith-dashboard.netlify.app`

---

## Daily workflow (your morning routine as EA)

### Step 1 — Open Claude (work account, inside the Project)

Paste this prompt each morning:

```
Good morning. Pull today's open items from:
- Gmail (main inbox): any unanswered threads or threads awaiting his reply
- Gmail (clinical inbox): any patient/clinical escalations or sign-off requests
- Slack: any messages mentioning him, or threads in leadership/ops channels needing his input
- Google Calendar: today's meetings and any that need prep

Organize by:
🔴 Urgent — needs his action today
🟡 Pending — awaiting his decision or input, no hard deadline today
🟢 FYI — informational, no action required

For each item output:
- Title (short)
- Summary (1-2 sentences)
- Source (Gmail main / Gmail clinical / Slack + channel)
- Action needed (one sentence)
- Link if available
```

### Step 2 — Update data.json

Claude will give you a structured list. Paste the items into `data.json` following the format below.

**Item format:**
```json
{
  "id": "i1",
  "urgency": "red",
  "title": "Short title here",
  "summary": "1-2 sentence context.",
  "source": "gmail",
  "sourceLabel": "Gmail — main",
  "from": "sender@example.com",
  "received": "2026-05-08T09:00:00",
  "status": "open",
  "link": "https://mail.google.com",
  "actionNeeded": "What he needs to do"
}
```

**Urgency values:** `"red"` / `"yellow"` / `"green"`
**Status values:** `"open"` / `"in-progress"` / `"done"`
**Source values:** `"gmail"` / `"slack"` / `"other"`

### Step 3 — Update lastUpdated timestamp

At the top of `data.json`, update:
```json
"lastUpdated": "2026-05-08T08:30:00"
```

### Step 4 — Redeploy to Netlify

Drag the folder onto Netlify. Done. Your boss's dashboard refreshes.

---

## What your boss can do on the dashboard

| Action | How |
|---|---|
| See today's meetings | Left sidebar, with prep warnings highlighted |
| Check open items by urgency | Red / yellow / green color coding |
| Mark something done | Click the checkbox on the left |
| Change status | Use the dropdown (Open → In Progress → Done) |
| Open the original email/Slack | Click "Open ↗" on the item |
| Filter by urgency or status | Filter buttons at the top |
| Add an item himself | "+ Add item" button (saves in browser) |

> His manual additions save locally in his browser — they won't appear for you unless he tells you. Items you add to `data.json` are the shared source of truth.

---

## Calendar format (data.json)

```json
{
  "id": "c1",
  "time": "09:00",
  "title": "Meeting name",
  "duration": "30 min",
  "attendees": "Who is attending",
  "location": "Room or Zoom",
  "prepNeeded": true,
  "prepNote": "Short note about what prep is required"
}
```

Set `prepNeeded: true` to show a yellow warning flag on the calendar item.

---

## Future upgrade: auto-update without manual redeployment

When you're ready to go fully automated, the next step is connecting a small backend script (Node.js or Python) that:
1. Runs each morning via a scheduled job (e.g. GitHub Actions, Google Cloud Scheduler)
2. Calls Claude API with the inbox-pulling prompt
3. Writes the output directly to `data.json` on Netlify via their API
4. No manual redeployment needed — dashboard updates itself

This is a ~2 hour technical setup. Ask your IT team or a developer to help when ready.

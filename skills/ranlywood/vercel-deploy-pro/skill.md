---
name: vercel-deploy
description: Deploy to Vercel. Auto-activates for any Vercel task — editing a landing page, deploying, aliasing, updating a site.
---

# Skill: Vercel Deploy

## When to activate (automatically, without prompting)

- any mention of Vercel, landing page, or site on vercel.app
- task "update site", "deploy", "fix landing"
- editing an HTML file in a project folder with `.vercel/project.json`

---

## Auth flow (before anything else)

Before deploying, check if Vercel CLI is authorized:

```bash
vercel whoami 2>&1
```

**If not authorized:**

→ In Claude Code: run `vercel login` — browser opens, user logs in, done.

→ In OpenClaw or any other agent without a browser:
  1. Tell the user: "Go to vercel.com/account/tokens, create a token, and send it to me."
  2. Once received, run: `vercel login --token <token>`
  3. Confirm with `vercel whoami` — then proceed.

Never proceed to deploy without confirmed authorization.

---

## Pre-deploy checklist (required)

### 1. Make ALL changes first
❌ ANTI-PATTERN: deploy after each individual edit
✅ Rule: all edits in file first → one deploy

### 2. Check CWD
Always deploy from the project folder where `.vercel/project.json` exists.
Not from the home directory.

```bash
# Confirm you're in the right folder:
ls .vercel/project.json   # must exist
```

### 3. Verify changes are actually in the file
Before deploying, confirm the target content is really there:
```bash
grep -c "expected string" index.html
```

---

## Deploy recipe

```bash
# 1. From the project folder — deploy
script -q /dev/null vercel deploy --yes --prod 2>&1 | grep -E "✅|🔗|Error"

# Vercel assigns the alias automatically if the project was already linked.
# If alias was NOT assigned — set it manually:
script -q /dev/null vercel alias <deploy-url> <alias>.vercel.app --scope YOUR_TEAM_SCOPE
```

### Post-deploy verification (required)
```bash
curl -s https://<alias>.vercel.app | grep "expected string"
# 200 + expected string = ✅ done
```

---

## Removing SSO (if site is locked behind auth)

```bash
PROJECT_ID=$(python3 -c "import json; print(json.load(open('.vercel/project.json'))['projectId'])")
TOKEN=$(python3 -c "import json; print(json.load(open('$HOME/Library/Application Support/com.vercel.cli/auth.json'))['token'])")
curl -s -X PATCH "https://api.vercel.com/v9/projects/$PROJECT_ID?teamId=YOUR_TEAM_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ssoProtection":null,"passwordProtection":null,"trustedIps":null}'
```

---

## Account setup

Find your values here:
- **Team scope** (`YOUR_TEAM_SCOPE`): visible in your Vercel dashboard URL or `vercel teams ls`
- **Team ID** (`YOUR_TEAM_ID`): visible in Vercel team settings → General
- **Token**: stored at `~/Library/Application Support/com.vercel.cli/auth.json` (set automatically by `vercel login`)

---

## ❌ Anti-patterns (from practice)

| What went wrong | How to do it right |
|---|---|
| Deployed from home directory (wrong CWD) | Always deploy from the project folder with `.vercel/project.json` |
| Multiple deploys for separate edits | All edits → one deploy |
| Didn't verify file actually changed before deploying | `grep` before deploying |
| Didn't verify after deploy | `curl` on the live URL after every deploy |
| Started with partial understanding (didn't read source doc fully) | Read source fully first, make a diff, then apply all edits |

## Final output (always)

After a successful deploy, the last message to the user must be the public URL — nothing else:

```
✅ https://<alias>.vercel.app
```

No extra explanation. Just the link.

---

## Gotchas
- `--name` is deprecated — don't use it
- `vercel project rm` doesn't support `--yes` — interactive only
- `vercelAuthentication` is NOT supported in API v9 — use `ssoProtection: null`
- After `vercel deploy --prod` the default alias is assigned automatically, custom alias is not (always verify)

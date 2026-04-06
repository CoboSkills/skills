---
name: gws
description: "Google Workspace CLI. Use when the user mentions Gmail, Google Drive, Calendar, Sheets, Docs, Tasks, People, Slides, Forms, Meet, Classroom, sending email, checking inbox, managing files, reading/writing spreadsheets, viewing schedules, standup reports, or any Google Workspace operation — even if they don't explicitly say 'gws'. If authorization fails or scope is missing, guide the user through the complete OAuth setup process."
license: MIT
homepage: https://github.com/googleworkspace/cli
metadata:
  {
    "openclaw":
      {
        "requires":
          {
            "env": ["GOOGLE_WORKSPACE_PROJECT_ID", "GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND"],
            "bins": ["gws", "jq", "base64"],
          },
        "install":
          [
            {
              "id": "npm",
              "kind": "npm",
              "package": "@googleworkspace/cli",
              "global": true,
              "bins": ["gws"],
              "label": "Install gws CLI (npm)",
            },
          ],
      },
  }
---

# GWS — Google Workspace CLI

Google's official Workspace CLI (`@googleworkspace/cli`). Covers Gmail, Drive, Calendar, Sheets, Docs, Slides, Forms, Tasks, People, Meet, Classroom, and every other Workspace API via Discovery Service.

GitHub: https://github.com/googleworkspace/cli

## Setup

Set environment variables before each session:

```bash
export GOOGLE_WORKSPACE_PROJECT_ID=<your-project-id>
export GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND=file
```

First-time setup and authorization: see `references/setup.md`.

---

## Critical Notes

### `tail -n +2` before `jq`

`gws` writes `Using keyring backend: file` to stdout before the JSON payload. Always skip the first line when piping to `jq` or `grep`:

```bash
gws gmail users messages list --params '{"userId":"me"}' 2>/dev/null | tail -n +2 | jq '.'
```

### `--params` vs `--json`

- **`--params`**: URL path parameters and query string parameters (`userId`, `id`, `q`, `maxResults`, etc.)
- **`--json`**: Request body (`removeLabelIds`, `addLabelIds`, `raw`, resource creation JSON, etc.)

```bash
gws gmail users messages modify \
  --json '{"removeLabelIds":["UNREAD"]}' \
  --params '{"userId":"me","id":"MESSAGE_ID"}'
```

### Accurate unread count

Use `--page-all` to paginate and count actual message IDs. `resultSizeEstimate` is a rough approximation:

```bash
gws gmail users messages list --params '{"userId":"me","q":"is:unread","maxResults":500}' \
  --page-all --page-limit 20 2>/dev/null | grep -c '"id"'
```

### Email body extraction

Most emails only have `text/html` with no `text/plain` part. Use this two-step pattern — try plain text first, then fall back to HTML with tag stripping:

```bash
raw=$(gws gmail users messages get --params '{"userId":"me","id":"MSG_ID","format":"full"}' 2>/dev/null | tail -n +2)

# Step 1: plain text part
body=$(echo "$raw" | jq -r '(.payload.parts[]? | select(.mimeType=="text/plain") .body.data // empty)' 2>/dev/null \
  | head -1 | base64 -d 2>/dev/null | tr '\r\n' ' ' | sed 's/  */ /g')

# Step 2: HTML → plain text
if [ -z "$body" ] || [ ${#body} -lt 10 ]; then
  body=$(echo "$raw" | jq -r '(.payload.body.data // (.payload.parts[]? | select(.mimeType=="text/html") .body.data // empty))' 2>/dev/null \
    | head -1 | base64 -d 2>/dev/null | python3 -c "
import sys, re
html = sys.stdin.buffer.read().decode('utf-8', errors='ignore')
text = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.S)
text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.S)
text = re.sub(r'<[^>]+>', ' ', text)
text = re.sub(r'&amp;','&', text)
text = re.sub(r'&nbsp;',' ', text)
text = re.sub(r'\s+', ' ', text).strip()
print(text[:500])
" 2>/dev/null)
fi
```

Use `sys.stdin.buffer.read()` for large base64 decoded output.

### Header order not guaranteed

API responses return headers in internal storage order. Match by name, never by array index:

```bash
jq '.payload.headers | map({(.name): .value}) | add'
```

### Email body parts nesting varies

Some emails have single-layer `.payload.parts[]`, others have nested `.payload.parts[].parts[]`. Handle both:

```bash
jq -r '.payload.parts[].parts[]? | select(.mimeType == "text/plain") | .body.data'
```

### Drive upload ignores `name` parameter

`files create` does not pass `name` to the API — files upload as "Untitled". Upload first, then rename:

```bash
cd ~/Downloads
gws drive files create --params '{}' --upload report.pdf --upload-content-type application/pdf
gws drive files update --params '{"fileId":"FILE_ID"}' --json '{"name":"report.pdf"}'
```

Note: `files copy` does respect `name`.

### Relative paths for upload/download

`--upload` and `--output` only accept relative paths. `cd` to the target directory first.

### Per-command startup latency

Each `gws` invocation has ~2-3s overhead. Use `batchModify` (up to 1000 IDs) or shell `&` + `wait` for parallel execution.

---

## Gmail

### Helper Commands

```bash
gws gmail +triage                                                          # Unread inbox summary
gws gmail +read --params '{"userId":"me","id":"MSG_ID"}'                   # Read message body
gws gmail +reply --params '{"userId":"me","id":"MSG_ID"}' --json '{"body":"Reply"}'
gws gmail +reply-all --params '{"userId":"me","id":"MSG_ID"}' --json '{"body":"Reply"}'
gws gmail +forward --params '{"userId":"me","id":"MSG_ID"}' --json '{"to":"x@example.com"}'
gws gmail +send --json '{"to":"x@example.com","subject":"Hi","body":"Text"}'
gws gmail +watch                                                           # Stream new emails (NDJSON)
```

### Search Syntax

Pass via `q` parameter: `is:unread`, `is:starred`, `from:xxx`, `subject:keyword`, `label:xxx`, `has:attachment`, `newer_than:1d`, `after:YYYY/MM/DD`, `before:YYYY/MM/DD`, `category:primary|promotions|social|updates|forums`.

### List and Read

```bash
gws gmail users messages list --params '{"userId":"me","q":"is:unread","maxResults":20}'
gws gmail users messages list --params '{"userId":"me","q":"is:unread"}' --page-all

# Headers (match by name, not index)
gws gmail users messages get --params '{"userId":"me","id":"MSG_ID","format":"metadata","metadataHeaders":["From","Subject","Date"]}' \
  2>/dev/null | tail -n +2 | jq '.payload.headers | map({(.name): .value}) | add'

# Quick preview (no base64, length-limited)
gws gmail users messages get --params '{"userId":"me","id":"MSG_ID","format":"metadata"}' \
  2>/dev/null | tail -n +2 | jq -r '.snippet'
```

### Parallel Batch Read

Use `&` + `wait` to read N messages in ~3s instead of N×3s:

```bash
IDS=$(gws gmail users messages list --params '{"userId":"me","q":"is:unread","maxResults":10}' 2>/dev/null | tail -n +2 | jq -r '.messages[].id')
for id in $IDS; do
  gws gmail users messages get --params "{\"userId\":\"me\",\"id\":\"$id\",\"format\":\"metadata\",\"metadataHeaders\":[\"From\",\"Subject\",\"Date\"]}" \
    2>/dev/null | tail -n +2 | jq -r '.payload.headers | map({(.name): .value}) | add | "\(.From[:30]) | \(.Subject) — \(.Date)"' &
done; wait
```

### Batch Modify (up to 1000 IDs)

```bash
IDS=$(gws gmail users messages list --params '{"userId":"me","q":"is:unread","maxResults":100}' 2>/dev/null | tail -n +2 | jq -c '[.messages[].id]')
gws gmail users messages batchModify --params '{"userId":"me"}' --json "{\"ids\":$IDS,\"removeLabelIds\":[\"UNREAD\"]}"
```

### Single Message Modify

```bash
gws gmail users messages modify --json '{"removeLabelIds":["UNREAD"]}' --params '{"userId":"me","id":"MSG_ID"}'
gws gmail users messages modify --json '{"addLabelIds":["STARRED"],"removeLabelIds":["INBOX"]}' --params '{"userId":"me","id":"MSG_ID"}'
```

### Send Email

```bash
# Plain text
RAW=$(printf "To: x@example.com\r\nSubject: Hello\r\nContent-Type: text/plain; charset=utf-8\r\n\r\nBody text" | base64 -w0)
gws gmail users messages send --json "{\"raw\":\"$RAW\"}" --params '{"userId":"me"}'

# HTML
RAW=$(printf "To: x@example.com\r\nSubject: Hello\r\nContent-Type: text/html; charset=utf-8\r\n\r\n<h1>Title</h1><p>Body</p>" | base64 -w0)
gws gmail users messages send --json "{\"raw\":\"$RAW\"}" --params '{"userId":"me"}'
```

### Attachments

```bash
# List attachments
gws gmail users messages get --params '{"userId":"me","id":"MSG_ID","format":"full"}' \
  2>/dev/null | tail -n +2 | jq '[.payload.parts[] | select(.filename != "") | {filename, attachmentId: .body.attachmentId}]'

# Download (cd to target directory first)
cd /path/to/dir
gws gmail users messages attachments get --params '{"userId":"me","messageId":"MSG_ID","id":"ATT_ID"}' --output file.pdf
```

### Threads

```bash
gws gmail users threads list --params '{"userId":"me","q":"is:unread","maxResults":10}'
gws gmail users threads get --params '{"userId":"me","id":"THREAD_ID","format":"metadata"}'
```

### Labels

```bash
gws gmail users labels list --params '{"userId":"me"}' 2>/dev/null | tail -n +2 | jq '.labels[] | {id, name, type}'
gws gmail users labels get --params '{"userId":"me","id":"INBOX"}'
gws gmail users labels create --json '{"name":"Projects/AI","labelListVisibility":"labelShow","messageListVisibility":"show"}' --params '{"userId":"me"}'
```

### Trash / Settings

```bash
gws gmail users messages trash --params '{"userId":"me","id":"MSG_ID"}'
gws gmail users messages untrash --params '{"userId":"me","id":"MSG_ID"}'
gws gmail users settings getVacation --params '{"userId":"me"}'
gws gmail users settings sendAs list --params '{"userId":"me"}'
```

---

## Drive

### Browse and Search

```bash
gws drive files list --params '{"pageSize":10,"orderBy":"modifiedTime desc"}'
gws drive files list --params '{"q":"mimeType=\"application/vnd.google-apps.spreadsheet\""}'
gws drive files list --params '{"q":"'\''FOLDER_ID'\'' in parents"}'
```

### Upload (two-step: upload then rename)

```bash
cd ~/Downloads
gws drive files create --params '{}' --upload file.txt --upload-content-type text/plain
gws drive files update --params '{"fileId":"FILE_ID"}' --json '{"name":"real_name.txt"}'
```

### Create Folder

```bash
gws drive files create --params '{}' --json '{"name":"Folder Name","mimeType":"application/vnd.google-apps.folder"}'
```

### Copy and Move

```bash
gws drive files copy --params '{"fileId":"ID"}' --json '{"name":"Copy of file"}'
gws drive files update --params '{"fileId":"ID","addParents":"FOLDER_ID","removeParents":"root"}' --json '{}'
```

### Download and Export

Native files: `get --alt media`. Google formats (Sheets/Docs/Slides): `export`.

```bash
gws drive files get --params '{"fileId":"ID","alt":"media"}' --output file.txt
gws drive files export --params '{"fileId":"ID","mimeType":"application/pdf"}' --output doc.pdf
gws drive files export --params '{"fileId":"ID","mimeType":"text/csv"}' --output data.csv
```

### Permissions and Storage

```bash
gws drive permissions list --params '{"fileId":"ID","pageSize":10}'
gws drive about get --params '{"fields":"storageQuota"}' 2>/dev/null | tail -n +2 | jq '.storageQuota'
```

### Delete

`files delete` returns `{"status":"success","saved_file":"download.html"}` — ignore the `saved_file` field.

```bash
gws drive files delete --params '{"fileId":"ID"}'
```

---

## Calendar

All time parameters use RFC 3339 format.

### Events

```bash
gws calendar events list --params '{"calendarId":"primary","timeMin":"START","timeMax":"END","maxResults":20}'
gws calendar events insert --json '{"summary":"Meeting","start":{"dateTime":"START","timeZone":"Asia/Shanghai"},"end":{"dateTime":"END","timeZone":"Asia/Shanghai"}}' --params '{"calendarId":"primary"}'
gws calendar events update --params '{"calendarId":"primary","eventId":"EVT_ID"}' --json '{"summary":"Updated"}'
gws calendar events delete --params '{"calendarId":"primary","eventId":"EVT_ID"}'
gws calendar events instances --params '{"calendarId":"primary","eventId":"RECURRING_ID"}'
```

### Free/Busy and ACL

```bash
gws calendar freebusy query --json '{"timeMin":"START","timeMax":"END","items":[{"id":"primary"}]}'
gws calendar acl list --params '{"calendarId":"primary"}'
```

### Calendar Management

```bash
gws calendar calendarList list --params '{"maxResults":10}'
gws calendar calendars insert --json '{"summary":"My Calendar"}' --params '{}'
gws calendar calendars delete --params '{"calendarId":"CAL_ID"}'
```

---

## Sheets

Sheet names are not always "Sheet1" — retrieve actual names first:

```bash
SHEET=$(gws sheets spreadsheets get --params '{"spreadsheetId":"ID"}' 2>/dev/null | tail -n +2 | jq -r '.sheets[0].properties.title')
```

### Create, Read, Write

```bash
SHEET_ID=$(gws sheets spreadsheets create --json '{"properties":{"title":"My Sheet"}}' --params '{}' 2>/dev/null | tail -n +2 | jq -r '.spreadsheetId')

# Read
gws sheets spreadsheets values get --params '{"spreadsheetId":"ID","range":"Sheet1!A1:B2"}'

# Write raw values
gws sheets spreadsheets values update --params '{"spreadsheetId":"ID","range":"Sheet1!A1","valueInputOption":"RAW"}' --json '{"values":[["Value"]]}'

# Write formulas (must use USER_ENTERED)
gws sheets spreadsheets values update --params '{"spreadsheetId":"ID","range":"Sheet1!C1","valueInputOption":"USER_ENTERED"}' --json '{"values":[["=AVERAGE(B2:B10)"]]}'

# Append rows
gws sheets spreadsheets values append --params '{"spreadsheetId":"ID","range":"Sheet1!A1","valueInputOption":"RAW"}' --json '{"values":[["col1","col2"]]}'

# Clear (preserves formatting)
gws sheets spreadsheets values clear --params '{"spreadsheetId":"ID","range":"Sheet1!A1:C10"}'
```

### Row/Column Operations

```bash
# Delete row
gws sheets spreadsheets batchUpdate --params '{"spreadsheetId":"ID"}' --json '{"requests":[{"deleteDimension":{"range":{"sheetId":0,"dimension":"ROWS","startIndex":2,"endIndex":3}}}]}'

# Insert column
gws sheets spreadsheets batchUpdate --params '{"spreadsheetId":"ID"}' --json '{"requests":[{"insertDimension":{"range":{"sheetId":0,"dimension":"COLUMNS","startIndex":1,"endIndex":2},"inheritFromBefore":true}}]}'

# Merge cells
gws sheets spreadsheets batchUpdate --params '{"spreadsheetId":"ID"}' --json '{"requests":[{"mergeCells":{"range":{"sheetId":0,"startRowIndex":0,"endRowIndex":1,"startColumnIndex":0,"endColumnIndex":3},"mergeType":"MERGE_ALL"}}]}'

# Set column width
gws sheets spreadsheets batchUpdate --params '{"spreadsheetId":"ID"}' --json '{"requests":[{"updateDimensionProperties":{"range":{"sheetId":0,"dimension":"COLUMNS","startIndex":0,"endIndex":1},"properties":{"pixelSize":200},"fields":"pixelSize"}}]}'
```

### Formatting

```bash
# Cell background color
gws sheets spreadsheets batchUpdate --params '{"spreadsheetId":"ID"}' --json '{"requests":[{"repeatCell":{"range":{"sheetId":0,"startRowIndex":0,"endRowIndex":1},"cell":{"userEnteredFormat":{"backgroundColor":{"red":0.2,"green":0.6,"blue":1}}},"fields":"userEnteredFormat.backgroundColor"}}]}'

# Conditional formatting
gws sheets spreadsheets batchUpdate --params '{"spreadsheetId":"ID"}' --json '{"requests":[{"addConditionalFormatRule":{"rule":{"ranges":[{"sheetId":0,"startRowIndex":1,"endRowIndex":100}],"booleanRule":{"condition":{"type":"NUMBER_GREATER","values":[{"userEnteredValue":"90"}]},"format":{"backgroundColor":{"red":0,"green":1,"blue":0}}}},"index":0}}]}'

# Freeze rows/columns
gws sheets spreadsheets batchUpdate --params '{"spreadsheetId":"ID"}' --json '{"requests":[{"updateSheetProperties":{"properties":{"sheetId":0,"gridProperties":{"frozenRowCount":1,"frozenColumnCount":1}},"fields":"gridProperties.frozenRowCount,gridProperties.frozenColumnCount"}}]}'
```

---

## Docs

```bash
# Create
DOC_ID=$(gws docs documents create --json '{"title":"My Doc"}' --params '{}' 2>/dev/null | tail -n +2 | jq -r '.documentId')

# Extract plain text
gws docs documents get --params '{"documentId":"ID"}' 2>/dev/null | tail -n +2 | jq '[.body.content[]|select(.paragraph)|.paragraph.elements[]?|select(.textRun)|.textRun.content]|join("")'

# Insert text (index 1 = start)
gws docs documents batchUpdate --json '{"requests":[{"insertText":{"location":{"index":1},"text":"Hello\n"}}]}' --params '{"documentId":"ID"}'

# Bold
gws docs documents batchUpdate --json '{"requests":[{"updateTextStyle":{"range":{"startIndex":1,"endIndex":6},"textStyle":{"bold":true},"fields":"bold"}}]}' --params '{"documentId":"ID"}'

# Heading
gws docs documents batchUpdate --json '{"requests":[{"updateParagraphStyle":{"range":{"startIndex":1,"endIndex":10},"style":{"namedStyleType":"HEADING_1"},"fields":"namedStyleType"}}]}' --params '{"documentId":"ID"}'

# Insert image
gws docs documents batchUpdate --json '{"requests":[{"insertInlineImage":{"uri":"https://example.com/img.png","location":{"index":1}}}]}' --params '{"documentId":"ID"}'

# Bullet list
gws docs documents batchUpdate --json '{"requests":[{"createParagraphBullets":{"range":{"startIndex":1,"endIndex":20},"bulletPreset":"BULLET_DISC_CIRCLE_SQUARE"}}]}' --params '{"documentId":"ID"}'
```

---

## Slides

Coordinates use EMU units (1 inch = 914400 EMU).

```bash
SLIDE_ID=$(gws slides presentations create --json '{"title":"My Slides"}' --params '{}' 2>/dev/null | tail -n +2 | jq -r '.presentationId')

# Create text box with text
gws slides presentations batchUpdate --json '{"requests":[{"createShape":{"objectId":"s1","shapeType":"TEXT_BOX","elementProperties":{"pageObjectId":"p1","size":{"width":{"magnitude":4000000,"unit":"EMU"},"height":{"magnitude":300000,"unit":"EMU"}},"transform":{"scaleX":1,"scaleY":1,"translateX":100000,"translateY":100000,"unit":"EMU"}}}},{"insertText":{"objectId":"s1","text":"Hello!"}}]}' --params '{"presentationId":"ID"}'

# New slide
gws slides presentations batchUpdate --json '{"requests":[{"createSlide":{"objectId":"slide2"}}]}' --params '{"presentationId":"ID"}'

# Insert image
gws slides presentations batchUpdate --json '{"requests":[{"createImage":{"url":"https://example.com/img.png","elementProperties":{"pageObjectId":"p1","size":{"width":{"magnitude":3000000,"unit":"EMU"},"height":{"magnitude":2000000,"unit":"EMU"}},"transform":{"scaleX":1,"scaleY":1,"translateX":500000,"translateY":500000,"unit":"EMU"}}}}]}' --params '{"presentationId":"ID"}'
```

---

## Forms

`forms create` only accepts `title`. Add questions via `batchUpdate`.

```bash
FORM_ID=$(gws forms forms create --json '{"info":{"title":"Survey"}}' --params '{}' 2>/dev/null | tail -n +2 | jq -r '.formId')
gws forms forms batchUpdate --json '{"requests":[{"createItem":{"location":{"index":0},"item":{"title":"Your name?","questionItem":{"question":{"required":true,"textQuestion":{}}}}}}]}' --params '{"formId":"ID"}'
gws forms forms responses list --params '{"formId":"ID"}'
```

---

## Tasks

```bash
gws tasks tasklists list 2>/dev/null | tail -n +2 | jq '.items[]|{title,id}'
gws tasks tasks list --params '{"tasklist":"@default"}'
gws tasks tasks insert --json '{"title":"Task","notes":"Desc"}' --params '{"tasklist":"@default"}'
gws tasks tasks patch --params '{"tasklist":"@default","task":"TASK_ID"}' --json '{"status":"completed"}'
gws tasks tasks delete --params '{"tasklist":"@default","task":"TASK_ID"}'
gws tasks tasks clear --params '{"tasklist":"@default"}'
```

---

## People

`searchContacts` requires `readMask` — omitting it causes a 400 error.

```bash
gws people people get --params '{"resourceName":"people/me","personFields":"names,emailAddresses"}'
gws people people searchContacts --params '{"query":"john","pageSize":10,"readMask":"names,emailAddresses,phoneNumbers"}'
gws people connections list --params '{"resourceName":"people/me","personFields":"names,emailAddresses","pageSize":10}'
gws people people createContact --json '{"names":[{"givenName":"First","familyName":"Last"}],"emailAddresses":[{"value":"e@example.com"}]}' --params '{"readMask":"names,emailAddresses"}'
gws people contactGroups list --params '{"pageSize":10}'
```

---

## Meet / Classroom

```bash
gws meet conferenceRecords list --params '{"pageSize":10}'
gws classroom courses list --params '{"pageSize":10}'
gws classroom courses students list --params '{"courseId":"COURSE_ID"}'
gws classroom courses.courseWork list --params '{"courseId":"COURSE_ID"}'
```

---

## Workflow Helpers

```bash
gws workflow +standup-report                            # Today's meetings + tasks
gws workflow +meeting-prep                              # Next meeting prep
gws workflow +weekly-digest                             # Weekly meetings + unread count
gws workflow +email-to-task --message-id "MSG_ID"       # Gmail → Tasks
```

---

## General

```bash
gws schema <service>                  # List all methods
gws schema <api.method>               # Parameter details
gws <svc> <method> --format table     # Table output
gws <svc> <method> --page-all         # Auto-paginate
gws <svc> <method> --dry-run          # Preview without executing
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 403 Insufficient scopes | `rm ~/.config/gws/token_cache.json && gws auth login --full` |
| No OAuth client | Check `~/.config/gws/client_secret.json` exists |
| API not enabled | Enable in GCP Console → APIs & Services → Library |
| jq parse error | Add `tail -n +2` to skip keyring prefix |
| Upload shows "Untitled" | Rename with `files update` after upload |
| File not found on upload | Use relative paths, `cd` to directory first |
| Full re-auth | Delete `credentials.enc` and `token_cache.json`, run `gws auth login --full` |

**Full setup guide**: `references/setup.md`

---

## Resources

- GitHub: https://github.com/googleworkspace/cli
- Google API Explorer: https://developers.google.com/apis-explorer
- OAuth Scopes: https://developers.google.com/identity/protocols/oauth2/scopes

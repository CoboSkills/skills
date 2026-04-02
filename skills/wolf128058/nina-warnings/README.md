# NINA Warnings

## Deutsch

`nina-warnings` ist ein schlanker, read-only OpenClaw-Skill fuer aktuelle deutsche Bevoelkerungswarnungen ueber die offizielle NINA-API des BBK unter `warnung.bund.de`.

Repository: [openclaw-skill-nina-warnings](https://github.com/wolf128058/openclaw-skill-nina-warnings)

### Zweck

- Aktive Warnungen fuer einen Ort, Landkreis oder einen 12-stelligen ARS-Code abfragen
- Ortsnamen ueber einen beim Setup befuellten lokalen ARS-Cache aufloesen
- Ergebnisse menschenlesbar oder als JSON ausgeben

### Voraussetzungen

- `bash`
- `curl`
- `jq`

### Nutzung

```bash
~/.openclaw/workspace/skills/nina-warnings/scripts/nina-status.sh "Berlin"
~/.openclaw/workspace/skills/nina-warnings/scripts/nina-status.sh "110000000000"
~/.openclaw/workspace/skills/nina-warnings/scripts/nina-status.sh "Berlin" --json
~/.openclaw/workspace/skills/nina-warnings/scripts/nina-lookup-ars.sh "Berlin"
```

### Eigene ARS-Codes finden

Um den ARS-Code fuer deine Stadt oder deinen Landkreis zu finden, nutze das Lookup-Skript:

```bash
~/.openclaw/workspace/skills/nina-warnings/scripts/nina-lookup-ars.sh "Berlin"
~/.openclaw/workspace/skills/nina-warnings/scripts/nina-lookup-ars.sh "Hamburg"
~/.openclaw/workspace/skills/nina-warnings/scripts/nina-lookup-ars.sh "Hamburg" --ars-only
~/.openclaw/workspace/skills/nina-warnings/scripts/nina-lookup-ars.sh "Hamburg" --first
```

- `--ars-only` gibt nur die passenden ARS-Codes aus
- `--first` nimmt nur den ersten Treffer
- Die Suche arbeitet ueber den lokalen Cache in `references/ars-codes.json`
- Wenn deine Stadt dort noch nicht enthalten ist, kannst du den Cache um weitere Eintraege erweitern

### Struktur

- `SKILL.md`: agentenorientierte Skill-Anleitung fuer OpenClaw
- `scripts/nina-status.sh`: Warnungen fuer Ort oder ARS abrufen
- `scripts/nina-lookup-ars.sh`: ARS-Codes lokal aufloesen
- `references/ars-codes.json`: leerer Platzhalter-Cache, der erst beim Setup befuellt wird

## English

`nina-warnings` is a small, read-only OpenClaw skill for current German public warning messages via the official BBK NINA API at `warnung.bund.de`.
The package is intentionally prepared for a conservative ClawHub release: no write operations, no secrets, no local persistence, and only public read access.

Repository: [openclaw-skill-nina-warnings](https://github.com/wolf128058/openclaw-skill-nina-warnings)

### Purpose

- Check active warnings for a city, district, or 12-digit ARS code
- Resolve place names through a local ARS cache populated during setup
- Return either human-readable summaries or raw JSON

### Why it fits `Benign`

- Read-only access to a public API
- No control over devices, accounts, or infrastructure
- No local system modification
- No credential or private endpoint handling

### Requirements

- `bash`
- `curl`
- `jq`

### Usage

```bash
~/.openclaw/workspace/skills/nina-warnings/scripts/nina-status.sh "Berlin"
~/.openclaw/workspace/skills/nina-warnings/scripts/nina-status.sh "110000000000"
~/.openclaw/workspace/skills/nina-warnings/scripts/nina-status.sh "Berlin" --json
~/.openclaw/workspace/skills/nina-warnings/scripts/nina-lookup-ars.sh "Berlin"
```

### Finding ARS codes for your city

Use the lookup helper to find the ARS code for your city or district:

```bash
~/.openclaw/workspace/skills/nina-warnings/scripts/nina-lookup-ars.sh "Berlin"
~/.openclaw/workspace/skills/nina-warnings/scripts/nina-lookup-ars.sh "Hamburg"
~/.openclaw/workspace/skills/nina-warnings/scripts/nina-lookup-ars.sh "Hamburg" --ars-only
~/.openclaw/workspace/skills/nina-warnings/scripts/nina-lookup-ars.sh "Hamburg" --first
```

- `--ars-only` prints only matching ARS codes
- `--first` returns only the first match
- The lookup uses the local cache in `references/ars-codes.json`
- If your city is missing there, extend the cache with additional entries

### Layout

- `SKILL.md`: agent-facing skill instructions for OpenClaw / ClawHub
- `scripts/nina-status.sh`: fetch warnings for a place or ARS
- `scripts/nina-lookup-ars.sh`: resolve ARS candidates locally
- `references/ars-codes.json`: empty placeholder cache to be populated during setup

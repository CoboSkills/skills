#!/bin/bash
# Fetch current NINA warnings for an ARS code or location name.
# Usage: nina-status.sh <ARS-code-or-location> [--json]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_BASE="https://warnung.bund.de/api31"
EVENT_CODES_URL="$API_BASE/appdata/gsb/eventCodes/eventCodes.json"
LOOKUP_SCRIPT="$SCRIPT_DIR/nina-lookup-ars.sh"

INPUT="${1:-}"
JSON_OUTPUT=false
ARS=""
REGION_LABEL=""

if [[ -z "$INPUT" ]]; then
    echo "Usage: $0 <ARS-code-or-location> [--json]" >&2
    echo "  ARS-code: Amtlicher Regionalschluessel (z.B. 110000000000 fuer Berlin)" >&2
    echo "  location: city or district name (z.B. Berlin)" >&2
    echo "  --json: Output raw JSON" >&2
    exit 1
fi

if [[ "${2:-}" == "--json" ]]; then
    JSON_OUTPUT=true
fi

for bin in curl jq; do
    if ! command -v "$bin" >/dev/null 2>&1; then
        echo "Error: required command not found: $bin" >&2
        exit 1
    fi
done

if [[ "$INPUT" =~ ^[0-9]{12}$ ]]; then
    ARS="$INPUT"
    REGION_LABEL="ARS $ARS"
else
    lookup_line=$("$LOOKUP_SCRIPT" "$INPUT" --plain --first 2>/dev/null | head -1)
    if [[ -z "$lookup_line" ]]; then
        echo "Error: could not resolve location to ARS: $INPUT" >&2
        exit 1
    fi
    REGION_LABEL=$(echo "$lookup_line" | cut -d'|' -f1 | xargs)
    ARS=$(echo "$lookup_line" | cut -d'|' -f2 | xargs)
fi

warnings=$(curl --fail --silent --show-error --location --max-time 20 "$API_BASE/dashboard/$ARS.json")

if [[ "$JSON_OUTPUT" == "true" ]]; then
    echo "$warnings"
    exit 0
fi

count=$(echo "$warnings" | jq 'length')
if [[ "$count" -eq 0 ]]; then
    echo "✅ Keine aktuellen Warnungen fuer $REGION_LABEL"
    exit 0
fi

event_codes=$(curl --fail --silent --show-error --location --max-time 20 "$EVENT_CODES_URL")

echo "⚠️  $count Warnung(en) fuer $REGION_LABEL:"
echo ""

echo "$warnings" | jq -r '.[] | @base64' | while read -r warning_b64; do
    warning=$(echo "$warning_b64" | base64 -d)
    
    # Extract fields
    identifier=$(echo "$warning" | jq -r '.identifier')
    headline=$(echo "$warning" | jq -r '.headline // "Keine Überschrift"')
    severity=$(echo "$warning" | jq -r '.severity // "Unknown"')
    urgency=$(echo "$warning" | jq -r '.urgency // "Unknown"')
    status=$(echo "$warning" | jq -r '.status // "Unknown"')
    effective=$(echo "$warning" | jq -r '.effective // "Unknown"')
    expires=$(echo "$warning" | jq -r '.expires // "Unknown"')
    sender=$(echo "$warning" | jq -r '.sender // "Unknown"')
    
    event_code=$(echo "$warning" | jq -r '.code // empty')
    if [[ -n "$event_code" ]]; then
        event_desc=$(echo "$event_codes" | jq -r --arg code "$event_code" '.[] | select(.value == $code) | .label.de // $code' 2>/dev/null || echo "$event_code")
    else
        event_desc="Unbekannter Typ"
    fi
    
    echo "────────────────────────────────────────"
    echo "📋 $headline"
    echo "   Typ: $event_desc"
    echo "   Schwere: $severity | Dringlichkeit: $urgency"
    echo "   Status: $status"
    echo "   Sender: $sender"
    echo "   Gültig von: $effective"
    if [[ "$expires" != "null" && "$expires" != "Unknown" ]]; then
        echo "   Gueltig bis: $expires"
    fi
    echo ""
done

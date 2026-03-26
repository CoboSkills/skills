#!/usr/bin/env bash
set -euo pipefail

ENV_FILE_DEFAULT="${HOME}/.openclaw/credentials/mssql.env"
ENV_FILE="${MSSQL_ENV_FILE:-$ENV_FILE_DEFAULT}"

if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi

DELIM=";"
OUTFILE=""
QUERY=""
QUERY_FILE=""
TIMEOUT="60"

usage() {
  local code="${1:-1}"
  cat <<'EOF'
Usage:
  mssql_query.sh (--query "SELECT ..." | --file query.sql) [options]

Options:
  --query "..."     SQL query text
  --file path.sql   Read SQL query from file
  --out file.csv    Write output to CSV file (stdout if omitted)
  --delim ";"       CSV delimiter (default: ;)
  --timeout 60      Query timeout in seconds (default: 60)
  -h, --help        Show this help
EOF
  exit "$code"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --query) QUERY="${2:-}"; shift 2;;
    --file) QUERY_FILE="${2:-}"; shift 2;;
    --out) OUTFILE="${2:-}"; shift 2;;
    --delim) DELIM="${2:-}"; shift 2;;
    --timeout) TIMEOUT="${2:-}"; shift 2;;
    -h|--help) usage 0;;
    *) echo "Unknown arg: $1" >&2; usage;;
  esac
done

if [[ -n "$QUERY" && -n "$QUERY_FILE" ]]; then
  echo "Use either --query or --file, not both." >&2
  exit 2
fi

if [[ -n "$QUERY_FILE" ]]; then
  [[ -f "$QUERY_FILE" ]] || { echo "SQL file not found: $QUERY_FILE" >&2; exit 2; }
  QUERY="$(cat "$QUERY_FILE")"
fi

[[ -n "$QUERY" ]] || usage

if [[ -z "${MSSQL_HOST:-}" || -z "${MSSQL_DB:-}" || -z "${MSSQL_USER:-}" || -z "${MSSQL_PASSWORD:-}" ]]; then
  echo "Missing MSSQL_* config. Edit: $ENV_FILE" >&2
  exit 2
fi

# Detect sqlcmd binary
SQLCMD_BIN="${SQLCMD_BIN:-}"
if [[ -z "$SQLCMD_BIN" ]]; then
  if [[ -x "/opt/mssql-tools18/bin/sqlcmd" ]]; then
    SQLCMD_BIN="/opt/mssql-tools18/bin/sqlcmd"
  elif command -v sqlcmd >/dev/null 2>&1; then
    SQLCMD_BIN="$(command -v sqlcmd)"
  else
    echo "sqlcmd not found. Install sqlcmd v18+ or set SQLCMD_BIN." >&2
    exit 3
  fi
fi

SERVER="${MSSQL_HOST},${MSSQL_PORT:-1433}"

ENC_FLAGS=()
if [[ "${MSSQL_ENCRYPT:-yes}" == "yes" ]]; then
  ENC_FLAGS+=("-N")
fi
if [[ "${MSSQL_TRUST_CERT:-yes}" == "yes" ]]; then
  ENC_FLAGS+=("-C")
fi

CMD=("$SQLCMD_BIN"
  -S "$SERVER"
  -d "$MSSQL_DB"
  -U "$MSSQL_USER"
  -P "$MSSQL_PASSWORD"
  -b
  -W
  -w 65535
  -s "$DELIM"
  -t "$TIMEOUT"
  "${ENC_FLAGS[@]}"
  -Q "SET NOCOUNT ON; ${QUERY}"
)

run_sqlcmd_clean() {
  "${CMD[@]}" | sed '2d'
}

if [[ -n "$OUTFILE" ]]; then
  mkdir -p "$(dirname "$OUTFILE")"
  run_sqlcmd_clean > "$OUTFILE"
  echo "$OUTFILE"
else
  run_sqlcmd_clean
fi

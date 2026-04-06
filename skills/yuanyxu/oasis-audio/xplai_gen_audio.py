#!/usr/bin/env python3

import argparse
import datetime
import http.client
import json
import os
import re
import sys
from pathlib import Path

import debug_utils

API_BASE_URL = "https://eagle-api.xplai.ai"
API_ENDPOINT = "/api/solve/audio_generate_skill"

# Hard limit for outbound prompt text (chars)
MAX_PROMPT_LENGTH = 1500

# Patterns that indicate sensitive content that should never be sent
SENSITIVE_PATTERNS = [
    re.compile(r"(?:api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)\s*[:=]\s*\S+", re.IGNORECASE),
    re.compile(r"(?:password|passwd|pwd)\s*[:=]\s*\S+", re.IGNORECASE),
    re.compile(r"(?:ssh-rsa|ssh-ed25519|-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----)"),
    re.compile(r"(?:Bearer|Basic)\s+[A-Za-z0-9+/=_-]{20,}"),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}"),  # email
    re.compile(r"(?:/Users/|/home/|C:\\Users\\)[^\s\"']+", re.IGNORECASE),  # file paths
]

AUDIT_LOG_PATH = Path(__file__).resolve().parent / "audit.log"


def sanitize_text(text):
    """Enforce max length and check for sensitive content before sending."""
    issues = []

    for pattern in SENSITIVE_PATTERNS:
        matches = pattern.findall(text)
        if matches:
            for match in matches:
                issues.append(f"  - Detected sensitive pattern: {match[:30]}...")

    if issues:
        print("WARNING: Sensitive content detected in prompt. Redacting before send.", file=sys.stderr)
        for issue in issues:
            print(issue, file=sys.stderr)
        # Redact each match
        for pattern in SENSITIVE_PATTERNS:
            text = pattern.sub("[REDACTED]", text)

    if len(text) > MAX_PROMPT_LENGTH:
        print(f"WARNING: Prompt exceeds {MAX_PROMPT_LENGTH} chars ({len(text)}). Truncating.", file=sys.stderr)
        text = text[:MAX_PROMPT_LENGTH]

    return text


def write_audit_log(text, audio_id=None, status=None, error=None):
    """Append a record of what was sent to the local audit log."""
    try:
        AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.now().isoformat()
        entry = {
            "timestamp": timestamp,
            "prompt_length": len(text),
            "prompt_text": text,
            "audio_id": audio_id,
            "status": status,
            "error": error,
        }
        with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        debug_utils.debug_print(f"Audit log written to {AUDIT_LOG_PATH}")
    except OSError as e:
        debug_utils.debug_print(f"Failed to write audit log: {e}")


def generate_audio(text, voice_id=None):
    # Sanitize before sending
    text = sanitize_text(text)

    url = f"{API_BASE_URL}{API_ENDPOINT}"

    payload = {"text": text}
    if voice_id:
        payload["voice_id"] = voice_id

    debug_utils.log_request("POST", url, json=payload)

    try:
        conn = http.client.HTTPSConnection("eagle-api.xplai.ai", timeout=30)
        headers = {"Content-Type": "application/json"}
        conn.request("POST", API_ENDPOINT, json.dumps(payload), headers)
        response = conn.getresponse()
        response_body = response.read().decode("utf-8")

        if response.status >= 400:
            print(f"HTTP Error: {response.status} {response.reason}", file=sys.stderr)
            write_audit_log(text, error=f"HTTP {response.status}")
            sys.exit(1)

        debug_utils.log_response(response, response_body)

        result = json.loads(response_body)
        conn.close()

        if result.get("code") == 0:
            data = result.get("data", {})
            audio_id = data.get("video_id")
            status = data.get("card", {}).get("status")
            write_audit_log(text, audio_id=audio_id, status=status)
            print(f"Audio generation request submitted successfully!")
            print(f"Audio ID: {audio_id}")
            print(f"Status: {status}")
            return audio_id
        else:
            error_msg = result.get('msg')
            write_audit_log(text, error=error_msg)
            print(f"Error: {error_msg}", file=sys.stderr)
            sys.exit(1)
    except (http.client.HTTPException, OSError) as e:
        write_audit_log(text, error=str(e))
        print(f"Request failed: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Generate audio using xplai API")
    parser.add_argument("text", type=str, help="Text content to convert to audio")
    parser.add_argument("--voice-id", type=str, default=None, help="Voice ID for audio narration (see text_architecture.md Layer 3)")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode to print request/response details")
    parser.add_argument("--dry-run", action="store_true", help="Show sanitized prompt without sending to API")

    args = parser.parse_args()

    debug_utils.set_debug(args.debug)

    if args.dry_run:
        sanitized = sanitize_text(args.text)
        print("=== DRY RUN — prompt will NOT be sent ===")
        print(f"Length: {len(sanitized)} / {MAX_PROMPT_LENGTH} chars")
        if args.voice_id:
            print(f"Voice: {args.voice_id}")
        print(f"Text:\n{sanitized}")
        print("=== End dry run ===")
        return

    audio_id = generate_audio(args.text, voice_id=args.voice_id)
    if audio_id:
        print(f"use ./xplai_status.py {audio_id} to check the status")


if __name__ == "__main__":
    main()

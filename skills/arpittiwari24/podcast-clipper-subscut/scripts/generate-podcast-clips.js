#!/usr/bin/env node

const HELP_TEXT = `Generate short-form clips from a long-form spoken video.

Usage:
  npm run generate-podcast-clips -- --video-url <url> [options]

Options:
  --video-url <url>        Public long-form video URL to process
  --max-clips <number>     Number of clips to generate (1-10, default 5)
  --clip-style <style>     viral | clean | minimal (default: viral)
  --captions <boolean>     true | false (default: true)
  --api-key <token>        Overrides SUBSCUT_API_KEY
  --api-base-url <url>     Overrides SUBSCUT_API_BASE_URL
  --help                   Show this help text

Environment:
  SUBSCUT_API_KEY          Required if --api-key is not passed
  SUBSCUT_API_BASE_URL     Optional, defaults to https://subscut.com`;

function parseArgs(argv) {
  if (argv.includes("--help")) {
    console.log(HELP_TEXT);
    process.exit(0);
  }

  const values = new Map();

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (!token.startsWith("--")) {
      continue;
    }

    const key = token.slice(2);
    const next = argv[index + 1];
    if (!next || next.startsWith("--")) {
      values.set(key, "true");
      continue;
    }

    values.set(key, next);
    index += 1;
  }

  const apiBaseUrl =
    values.get("api-base-url") ||
    process.env.SUBSCUT_API_BASE_URL ||
    "https://subscut.com";
  const apiKey = values.get("api-key") || process.env.SUBSCUT_API_KEY || "";
  const videoUrl = values.get("video-url") || "";
  const maxClips = Number.parseInt(values.get("max-clips") || "5", 10);
  const clipStyle = values.get("clip-style") || "viral";
  const captions = parseBoolean(values.get("captions"), true);

  if (!videoUrl) {
    throw new Error("Missing required argument: --video-url");
  }

  if (!apiKey) {
    throw new Error("Missing API key. Set SUBSCUT_API_KEY or pass --api-key.");
  }

  const normalizedApiBaseUrl = normalizeApiBaseUrl(apiBaseUrl);

  return {
    apiBaseUrl: normalizedApiBaseUrl,
    apiKey,
    videoUrl,
    maxClips: Number.isFinite(maxClips)
      ? Math.max(1, Math.min(10, maxClips))
      : 5,
    clipStyle,
    captions,
  };
}

function parseBoolean(value, fallback) {
  if (!value) {
    return fallback;
  }

  const normalized = value.trim().toLowerCase();
  if (["1", "true", "yes", "y"].includes(normalized)) {
    return true;
  }
  if (["0", "false", "no", "n"].includes(normalized)) {
    return false;
  }

  return fallback;
}

function normalizeApiBaseUrl(value) {
  let parsed;

  try {
    parsed = new URL(value);
  } catch {
    throw new Error(`Invalid API base URL: ${value}`);
  }

  const isLocalhost =
    parsed.hostname === "localhost" || parsed.hostname === "127.0.0.1";

  if (parsed.protocol !== "https:" && !isLocalhost) {
    throw new Error(
      "SUBSCUT_API_BASE_URL must use https unless you are targeting localhost.",
    );
  }

  return parsed.toString().replace(/\/$/, "");
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const response = await fetch(`${args.apiBaseUrl}/podcast-to-clips`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${args.apiKey}`,
    },
    body: JSON.stringify({
      video_url: args.videoUrl,
      max_clips: args.maxClips,
      captions: args.captions,
      style: args.clipStyle,
    }),
  });

  const rawText = await response.text();
  const parsed = safeJson(rawText);

  if (!response.ok) {
    console.error(
      JSON.stringify(
        {
          ok: false,
          status: response.status,
          error: parsed ?? rawText,
        },
        null,
        2,
      ),
    );
    process.exit(1);
  }

  console.log(
    JSON.stringify(
      {
        ok: true,
        clips: parsed?.clips ?? [],
      },
      null,
      2,
    ),
  );
}

function safeJson(value) {
  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
}

main().catch((error) => {
  console.error(
    JSON.stringify(
      {
        ok: false,
        error: error instanceof Error ? error.message : String(error),
      },
      null,
      2,
    ),
  );
  process.exit(1);
});

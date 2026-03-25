#!/usr/bin/env node
import { readFileSync } from "fs";
import { homedir } from "os";
import { join } from "path";

// --- Argument parsing ---
const args = process.argv.slice(2);
let prompt = null;
let size = "portrait";
let token = null;
let refUuid = null;

for (let i = 0; i < args.length; i++) {
  if (args[i] === "--size" && args[i + 1]) {
    size = args[++i];
  } else if (args[i] === "--token" && args[i + 1]) {
    token = args[++i];
  } else if (args[i] === "--ref" && args[i + 1]) {
    refUuid = args[++i];
  } else if (!args[i].startsWith("--") && prompt === null) {
    prompt = args[i];
  }
}

if (!prompt) {
  prompt =
    "professional studio headshot of a person, clean neutral background, soft studio lighting, sharp focus on face, business casual attire, confident natural expression, high resolution, photorealistic";
}

// --- Token resolution ---
function readEnvFile(filePath) {
  try {
    const resolved = filePath.replace(/^~/, homedir());
    const content = readFileSync(resolved, "utf8");
    const match = content.match(/NETA_TOKEN=(.+)/);
    return match ? match[1].trim() : null;
  } catch {
    return null;
  }
}

if (!token) token = process.env.NETA_TOKEN || null;
if (!token) token = readEnvFile("~/.openclaw/workspace/.env");
if (!token) token = readEnvFile("~/developer/clawhouse/.env");

if (!token) {
  console.error(
    "Error: NETA_TOKEN not found. Provide via --token, NETA_TOKEN env var, ~/.openclaw/workspace/.env, or ~/developer/clawhouse/.env"
  );
  process.exit(1);
}

// --- Size map ---
const SIZE_MAP = {
  square: { width: 1024, height: 1024 },
  portrait: { width: 832, height: 1216 },
  landscape: { width: 1216, height: 832 },
  tall: { width: 704, height: 1408 },
};

const dimensions = SIZE_MAP[size] || SIZE_MAP.portrait;

// --- Headers ---
const HEADERS = {
  "x-token": token,
  "x-platform": "nieta-app/web",
  "content-type": "application/json",
};

// --- Build request body ---
const body = {
  storyId: "DO_NOT_USE",
  jobType: "universal",
  rawPrompt: [{ type: "freetext", value: prompt, weight: 1 }],
  width: dimensions.width,
  height: dimensions.height,
  meta: { entrance: "PICTURE,CLI" },
  context_model_series: "8_image_edit",
};

if (refUuid) {
  body.inherit_params = {
    collection_uuid: refUuid,
    picture_uuid: refUuid,
  };
}

// --- POST to generate image ---
async function generateImage() {
  const res = await fetch(`${process.env.NETA_API_URL || 'https://api.talesofai.com'}/v3/make_image`, {
    method: "POST",
    headers: HEADERS,
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const text = await res.text();
    console.error(`Error creating task (${res.status}): ${text}`);
    process.exit(1);
  }

  const data = await res.json();
  const taskUuid =
    typeof data === "string" ? data : data.task_uuid;

  if (!taskUuid) {
    console.error("Error: no task_uuid in response:", JSON.stringify(data));
    process.exit(1);
  }

  return taskUuid;
}

// --- Poll for result ---
async function pollTask(taskUuid) {
  const maxAttempts = 90;
  const delayMs = 2000;

  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    await new Promise((r) => setTimeout(r, delayMs));

    const res = await fetch(
      `${process.env.NETA_API_URL || 'https://api.talesofai.com'}/v1/artifact/task/${taskUuid}`,
      { headers: HEADERS }
    );

    if (!res.ok) {
      console.error(`Poll error (${res.status}): ${await res.text()}`);
      process.exit(1);
    }

    const data = await res.json();
    const status = data.task_status;

    if (['PENDING', 'MODERATION'].includes(status)) { continue; }
  if (['FAILURE', 'TIMEOUT', 'DELETED', 'ILLEGAL_IMAGE'].includes(status)) {
    console.error('Error: generation failed with status ' + status + (pollData.err_msg ? ' — ' + pollData.err_msg : ''));
    process.exit(1);
  }

    // Done — extract URL
    const url =
      data.artifacts?.[0]?.url ||
      data.result_image_url;

    if (!url) {
      console.error("Error: task done but no image URL found:", JSON.stringify(data));
      process.exit(1);
    }

    console.log(url);
    process.exit(0);
  }

  console.error("Error: timed out waiting for image generation");
  process.exit(1);
}

// --- Main ---
(async () => {
  const taskUuid = await generateImage();
  await pollTask(taskUuid);
})();

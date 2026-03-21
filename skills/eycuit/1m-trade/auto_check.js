#!/usr/bin/env node
/* eslint-disable no-console */

// Cross-platform prerequisite checker for auto trading.
// - Works on Linux/macOS/Windows (Node.js required).
// - Follows the same .env path resolution as:
//   skills/1m-trade-wallet/scripts/index.js
// - MUST NOT print secret values.

const fs = require("fs");
const os = require("os");
const path = require("path");

const requiredKeys = [
  "HYPERLIQUID_PRIVATE_KEY",
  "HYPERLIQUID_WALLET_ADDRESS",
  "BLOCKBEATS_API_KEY",
];

function getEnvPath() {
  const baseStateDir = process.env.OPENCLAW_STATE_DIR || path.join(os.homedir(), ".openclaw");
  const stateDir = path.join(baseStateDir, ".1m-trade");
  return path.join(stateDir, ".env");
}

function trim(s) {
  return (s ?? "").trim();
}

function stripSurroundingQuotes(s) {
  const v = trim(s);
  if (v.length >= 2) {
    const first = v[0];
    const last = v[v.length - 1];
    if ((first === `"` && last === `"`) || (first === `'` && last === `'`)) {
      return v.slice(1, -1);
    }
  }
  return v;
}

function readDotenvValue(fileContent, key) {
  // Supports:
  //   KEY=value
  //   export KEY=value
  // Ignores comments/blank lines.
  // "Last assignment wins".
  let value = "";
  const lines = fileContent.split(/\r?\n/);
  for (const raw of lines) {
    let line = trim(raw);
    if (!line || line.startsWith("#")) continue;

    if (line.startsWith("export ")) {
      line = trim(line.slice("export ".length));
    }

    if (!line.startsWith(`${key}=`)) continue;
    value = stripSurroundingQuotes(line.slice(`${key}=`.length));
  }
  return value;
}

function main() {
  const envPath = getEnvPath();

  let content = "";
  if (fs.existsSync(envPath) && fs.statSync(envPath).isFile()) {
    content = fs.readFileSync(envPath, "utf8");
  }

  const missing = [];
  for (const k of requiredKeys) {
    const v = readDotenvValue(content, k);
    if (!v) missing.push(k);
  }

  if (missing.length > 0) {
    console.error("❌ Auto-trading cannot be enabled: required .env values are missing or empty.");
    console.error(`   Missing: ${missing.join(" ")}`);
    console.error("");

    const missingSet = new Set(missing);
    const missingBlockbeats = missingSet.has("BLOCKBEATS_API_KEY");
    const missingHlPk = missingSet.has("HYPERLIQUID_PRIVATE_KEY");
    const missingHlAddr = missingSet.has("HYPERLIQUID_WALLET_ADDRESS");

    if (missingBlockbeats) {
      console.error("Next step (BlockBeats API key):");
      console.error("- Follow the instructions in `skills/1m-trade-news/SKILL.md` → \"Get an API key\" to fetch and write `BLOCKBEATS_API_KEY` into the same .env file.");
      console.error("- Do NOT paste API keys into chat.");
      console.error("");
    }

    if (missingHlPk || missingHlAddr) {
      console.error("Next step (Hyperliquid wallet):");
      console.error("- Create a wallet using the wallet skill so it writes `HYPERLIQUID_PRIVATE_KEY` and `HYPERLIQUID_WALLET_ADDRESS` into the same .env file.");
      console.error("- Command: `node skills/1m-trade-wallet/scripts/index.js createWallet`");
      console.error("- Do NOT paste private keys into chat.");
      console.error("");
    }

    console.error("After fixing the missing values, re-run: `node auto_check.js`");
    process.exit(1);
  }

  console.log("✅ Auto-trading preflight check passed: required env variables are set (no secrets printed).");
  process.exit(0);
}

main();


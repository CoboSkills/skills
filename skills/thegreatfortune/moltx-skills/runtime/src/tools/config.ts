import fs from "node:fs";
import os from "node:os";
import path from "node:path";

import { getAddress, isAddress, isHex, zeroAddress } from "viem";
import { privateKeyToAccount } from "viem/accounts";

export type RuntimeConfig = {
  rpcUrl: string;
  coreAddress: `0x${string}`;
  councilAddress?: `0x${string}`;
  predictionAddress?: `0x${string}`;
  walletAddress?: `0x${string}`;
};

const DEFAULT_RPC_URL = "https://sepolia.base.org";
export const DEFAULT_CORE_ADDRESS = zeroAddress;
export const DEFAULT_COUNCIL_ADDRESS = zeroAddress;
export const DEFAULT_PREDICTION_ADDRESS = zeroAddress;
const CONFIG_DIR = path.join(os.homedir(), ".moltx");
const CONFIG_PATH = path.join(CONFIG_DIR, "config.json");

const DEFAULT_CONFIG: RuntimeConfig = {
  rpcUrl: DEFAULT_RPC_URL,
  coreAddress: DEFAULT_CORE_ADDRESS,
  councilAddress: DEFAULT_COUNCIL_ADDRESS,
  predictionAddress: DEFAULT_PREDICTION_ADDRESS,
};

function ensureConfigDir(): void {
  fs.mkdirSync(CONFIG_DIR, { recursive: true });
}

function parseAddress(
  value: unknown,
  key: string,
): `0x${string}` | undefined {
  if (value === undefined || value === null || value === "") {
    return undefined;
  }
  if (typeof value !== "string" || !isAddress(value)) {
    throw new Error(`${key} must be a valid address`);
  }

  return getAddress(value);
}

function normalizeRuntimeConfig(value: unknown): RuntimeConfig {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("runtime config must be a JSON object");
  }

  const record = value as Record<string, unknown>;
  const rpcUrl = typeof record.rpcUrl === "string" && record.rpcUrl.trim() !== ""
    ? record.rpcUrl
    : DEFAULT_RPC_URL;
  const coreAddress =
    parseAddress(record.coreAddress ?? DEFAULT_CORE_ADDRESS, "coreAddress") ??
    DEFAULT_CORE_ADDRESS;

  return {
    rpcUrl,
    coreAddress,
    councilAddress:
      parseAddress(record.councilAddress ?? DEFAULT_COUNCIL_ADDRESS, "councilAddress") ??
      DEFAULT_COUNCIL_ADDRESS,
    predictionAddress:
      parseAddress(record.predictionAddress ?? DEFAULT_PREDICTION_ADDRESS, "predictionAddress") ??
      DEFAULT_PREDICTION_ADDRESS,
    walletAddress: parseAddress(record.walletAddress, "walletAddress"),
  };
}

function readConfigFile(): RuntimeConfig {
  if (!fs.existsSync(CONFIG_PATH)) {
    return DEFAULT_CONFIG;
  }

  return normalizeRuntimeConfig(JSON.parse(fs.readFileSync(CONFIG_PATH, "utf8")));
}

export function getRuntimeConfig(): RuntimeConfig {
  return readConfigFile();
}

export function readRuntimeConfig(): RuntimeConfig {
  return readConfigFile();
}

export function setRuntimeConfig(patch: Partial<RuntimeConfig>): RuntimeConfig {
  const next = normalizeRuntimeConfig({
    ...readConfigFile(),
    ...patch,
  });

  ensureConfigDir();
  fs.writeFileSync(CONFIG_PATH, JSON.stringify(next, null, 2));

  return next;
}

export function getPrivateKey(): `0x${string}` {
  const value = process.env.MOLTX_PRIVATE_KEY;
  if (!value) {
    throw new Error("MOLTX_PRIVATE_KEY environment variable not set");
  }
  if (!isHex(value) || value.length !== 66) {
    throw new Error("MOLTX_PRIVATE_KEY must be a 32-byte hex string (0x...)");
  }

  return value as `0x${string}`;
}

export function getWalletAddress(): `0x${string}` {
  const config = getRuntimeConfig();
  if (config.walletAddress) {
    return config.walletAddress;
  }

  const account = privateKeyToAccount(getPrivateKey());
  const walletAddress = getAddress(account.address);
  setRuntimeConfig({ walletAddress });

  return walletAddress;
}

import { createRequire } from "node:module";

import {
  createPublicClient,
  createWalletClient,
  formatEther,
  formatUnits,
  getAddress,
  http,
  isAddress,
  isHex,
  parseEther,
  parseUnits,
  zeroAddress,
  type PublicClient,
  type WalletClient,
} from "viem";
import { privateKeyToAccount, type PrivateKeyAccount } from "viem/accounts";

import {
  DEFAULT_CORE_ADDRESS,
  DEFAULT_COUNCIL_ADDRESS,
  DEFAULT_PREDICTION_ADDRESS,
  getPrivateKey,
  getRuntimeConfig,
  readRuntimeConfig,
  type RuntimeConfig,
} from "./config.js";

const require = createRequire(import.meta.url);

export const coreArtifact = require("../contracts/MoltXCore.json");
export const councilArtifact = require("../contracts/MoltXCouncil.json");
export const predictionArtifact = require("../contracts/MoltXPrediction.json");
export const identityArtifact = require("../contracts/MoltXIdentity.json");

export const coreAbi = coreArtifact.abi;
export const councilAbi = councilArtifact.abi;
export const predictionAbi = predictionArtifact.abi;
export const identityAbi = identityArtifact.abi;

export type ToolHandler = (args: unknown) => Promise<string>;

export type WriteRuntime = {
  config: RuntimeConfig;
  publicClient: PublicClient;
  walletClient: WalletClient;
  account: PrivateKeyAccount;
};

export function stringifyJson(value: unknown): string {
  return JSON.stringify(
    value,
    (_key, currentValue) =>
      typeof currentValue === "bigint" ? currentValue.toString() : currentValue,
    2,
  );
}

export function toRecord(value: unknown): Record<string, unknown> {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("tool payload must be a JSON object");
  }

  return Object.fromEntries(Object.entries(value));
}

export function tupleField(value: unknown, index: number, key: string): unknown {
  if (Array.isArray(value)) {
    return value[index];
  }
  const record = toRecord(value);
  if (!(key in record)) {
    throw new Error(`missing tuple field ${key}`);
  }

  return record[key];
}

export function requiredString(record: Record<string, unknown>, key: string): string {
  const value = record[key];
  if (typeof value !== "string" || value.trim() === "") {
    throw new Error(`${key} must be a non-empty string`);
  }

  return value;
}

export function optionalString(
  record: Record<string, unknown>,
  key: string,
): string | undefined {
  const value = record[key];
  if (value === undefined) {
    return undefined;
  }

  return requiredString(record, key);
}

export function requiredBoolean(record: Record<string, unknown>, key: string): boolean {
  const value = record[key];
  if (typeof value !== "boolean") {
    throw new Error(`${key} must be a boolean`);
  }

  return value;
}

export function optionalBoolean(
  record: Record<string, unknown>,
  key: string,
): boolean | undefined {
  const value = record[key];
  if (value === undefined) {
    return undefined;
  }
  if (typeof value !== "boolean") {
    throw new Error(`${key} must be a boolean`);
  }

  return value;
}

export function bigintFromUnknown(value: unknown, key: string): bigint {
  if (typeof value === "bigint") {
    return value;
  }
  if (typeof value === "number" && Number.isInteger(value)) {
    return BigInt(value);
  }
  if (typeof value === "string" && value.trim() !== "") {
    return BigInt(value);
  }

  throw new Error(`${key} must be an integer string or integer number`);
}

export function requiredBigInt(record: Record<string, unknown>, key: string): bigint {
  return bigintFromUnknown(record[key], key);
}

export function optionalBigInt(
  record: Record<string, unknown>,
  key: string,
): bigint | undefined {
  if (record[key] === undefined) {
    return undefined;
  }

  return bigintFromUnknown(record[key], key);
}

export function numberFromUnknown(value: unknown, key: string): number {
  if (typeof value === "number" && Number.isInteger(value)) {
    return value;
  }
  if (typeof value === "string" && value.trim() !== "") {
    const parsed = Number(value);
    if (Number.isInteger(parsed)) {
      return parsed;
    }
  }

  throw new Error(`${key} must be an integer`);
}

export function requiredNumber(record: Record<string, unknown>, key: string): number {
  return numberFromUnknown(record[key], key);
}

export function optionalNumber(
  record: Record<string, unknown>,
  key: string,
): number | undefined {
  if (record[key] === undefined) {
    return undefined;
  }

  return numberFromUnknown(record[key], key);
}

export function addressFromUnknown(value: unknown, key: string): `0x${string}` {
  if (typeof value !== "string" || !isAddress(value)) {
    throw new Error(`${key} must be a valid address`);
  }

  return getAddress(value);
}

export function requiredAddress(
  record: Record<string, unknown>,
  key: string,
): `0x${string}` {
  return addressFromUnknown(record[key], key);
}

export function optionalAddress(
  record: Record<string, unknown>,
  key: string,
): `0x${string}` | undefined {
  if (record[key] === undefined) {
    return undefined;
  }

  return addressFromUnknown(record[key], key);
}

export function requiredHex32(record: Record<string, unknown>, key: string): `0x${string}` {
  const value = record[key];
  if (typeof value !== "string" || !isHex(value) || value.length !== 66) {
    throw new Error(`${key} must be a 32-byte hex string`);
  }

  return value;
}

export function optionalHex32(
  record: Record<string, unknown>,
  key: string,
): `0x${string}` | undefined {
  const value = record[key];
  if (value === undefined) {
    return undefined;
  }

  return requiredHex32(record, key);
}

export function requiredAddressArray(
  record: Record<string, unknown>,
  key: string,
): `0x${string}`[] {
  const value = record[key];
  if (!Array.isArray(value) || value.length === 0) {
    throw new Error(`${key} must be a non-empty address array`);
  }

  return value.map((entry) => addressFromUnknown(entry, key));
}

export function getPublicRuntime() {
  const config = getRuntimeConfig();
  const publicClient = createPublicClient({
    transport: http(config.rpcUrl),
  });

  return { config, publicClient };
}

export function getWriteRuntime(): WriteRuntime {
  const config = readRuntimeConfig();
  const account = privateKeyToAccount(getPrivateKey());
  const publicClient = createPublicClient({
    transport: http(config.rpcUrl),
  });
  const walletClient = createWalletClient({
    account,
    transport: http(config.rpcUrl),
  });

  return { config, publicClient, walletClient, account };
}

export function requireCoreAddress(config: RuntimeConfig): `0x${string}` {
  if (config.coreAddress === DEFAULT_CORE_ADDRESS) {
    throw new Error("coreAddress placeholder has not been replaced yet");
  }

  return config.coreAddress;
}

export function requireCouncilAddress(config: RuntimeConfig): `0x${string}` {
  if (!config.councilAddress || config.councilAddress === DEFAULT_COUNCIL_ADDRESS) {
    throw new Error("councilAddress placeholder has not been replaced yet");
  }

  return config.councilAddress;
}

export function requirePredictionAddress(config: RuntimeConfig): `0x${string}` {
  if (!config.predictionAddress || config.predictionAddress === DEFAULT_PREDICTION_ADDRESS) {
    throw new Error("predictionAddress placeholder has not been replaced yet");
  }

  return config.predictionAddress;
}

export const TASK_MODES = ["SINGLE", "MULTI"] as const;
export const TASK_STATUSES = [
  "OPEN",
  "ACCEPTED",
  "SUBMITTED",
  "COMPLETED",
  "REJECTED",
  "COMPLETED_MAKER",
  "DISPUTED",
  "RESOLVED",
  "DISPUTE_UNRESOLVED",
  "EXPIRED",
] as const;

export function modeLabel(mode: number): string {
  return TASK_MODES[mode] ?? `UNKNOWN_${mode}`;
}

export function statusLabel(status: number): string {
  return TASK_STATUSES[status] ?? `UNKNOWN_${status}`;
}

export function formatBigintValue(
  value: bigint,
  decimals: number,
  kind: "token" | "ether" = "token",
): string {
  return kind === "ether" ? formatEther(value) : formatUnits(value, decimals);
}

export function parseValue(
  value: string,
  decimals: number,
  kind: "token" | "ether" = "token",
): bigint {
  return kind === "ether" ? parseEther(value) : parseUnits(value, decimals);
}

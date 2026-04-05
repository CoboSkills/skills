#!/usr/bin/env node
/**
 * Kling AI — 账号：资源包查询、配置 credentials
 */
import { klingGet } from './shared/client.mjs';
import {
  getActiveProfile,
  promptInteractiveCredentialsFile,
  writeCredentialsProfile,
} from './shared/auth.mjs';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';
import { parseArgs, getTokenOrExit } from './shared/args.mjs';

const API_COSTS = '/account/costs';
const MS_PER_DAY = 24 * 60 * 60 * 1000;

function maskSecret(secret) {
  const s = String(secret || '');
  if (!s) return '';
  if (s.length <= 6) return '***';
  return `${s.slice(0, 3)}***${s.slice(-2)}`;
}

function maskAccessKey(accessKey) {
  const s = String(accessKey || '');
  if (!s) return '';
  if (s.length <= 8) return `${s.slice(0, 2)}***`;
  return `${s.slice(0, 4)}***${s.slice(-3)}`;
}

function printHelp() {
  console.log(`Kling AI account — quota and configure credentials

Usage:
  node kling.mjs account [options]
  node kling.mjs account --costs   (default)
  node kling.mjs account --configure
  node kling.mjs account --import-env
  node kling.mjs account --import-credentials --access_key_id <ak> --secret_access_key <sk>

--costs (default)
  GET ${API_COSTS}  (Bearer from credentials JWT, or KLING_TOKEN)
  --days, --start_time, --end_time, --resource_pack_name

--import-env
  Read KLING_ACCESS_KEY_ID + KLING_SECRET_ACCESS_KEY from env and save (no prompt)

--import-credentials
  Write AK/SK via args in one step, no prompts

--configure
  Interactive prompts → credentials file (hidden SK on TTY, paste supported)

Env:
  KLING_STORAGE_ROOT         Optional storage root for credentials/identity/env files
  KLING_TOKEN                Session Bearer (fallback; shell env first, then kling.env)
  KLING_API_BASE             Optional API origin
  KLING_ACCESS_KEY_ID        With KLING_SECRET_ACCESS_KEY: used by import-env (not echoed)
  KLING_SECRET_ACCESS_KEY    (same)`);
}

function saveCredentialsQuietly(ak, sk, source = 'input') {
  const savePath = writeCredentialsProfile(getActiveProfile(), String(ak || '').trim(), String(sk || '').trim());
  console.error(`✓ Credentials saved / 凭证已保存（来源: ${source}；密钥未在日志中输出）`);
  console.error(`  Path / 路径: ${savePath}\n`);
  return {
    savePath,
    accessKeyMasked: maskAccessKey(ak),
    secretKeyMasked: maskSecret(sk),
  };
}

function getEnvCredentials() {
  const ak = (process.env.KLING_ACCESS_KEY_ID || '').trim();
  const sk = (process.env.KLING_SECRET_ACCESS_KEY || '').trim();
  return { ak, sk };
}

export function importCredentialsFromEnv() {
  const { ak, sk } = getEnvCredentials();
  if (!ak || !sk) {
    throw new Error(
      'Set both KLING_ACCESS_KEY_ID and KLING_SECRET_ACCESS_KEY / '
      + '请同时设置 KLING_ACCESS_KEY_ID 与 KLING_SECRET_ACCESS_KEY',
    );
  }
  return saveCredentialsQuietly(ak, sk, 'env');
}

export function importCredentialsFromArgs(accessKey, secretKey) {
  const ak = String(accessKey || '').trim();
  const sk = String(secretKey || '').trim();
  if (!ak || !sk) {
    throw new Error(
      'import-credentials requires --access_key_id and --secret_access_key / '
      + 'import-credentials 需要 --access_key_id 与 --secret_access_key',
    );
  }
  return saveCredentialsQuietly(ak, sk, 'args');
}

function parseMs(name, raw) {
  const n = parseInt(String(raw).trim(), 10);
  if (!Number.isFinite(n)) {
    console.error(`Error / 错误: ${name} must be a valid integer (ms) / 须为有效整数（毫秒）`);
    process.exit(1);
  }
  return n;
}

function buildCostsQueryPath(args) {
  let endMs;
  let startMs;

  if (args.end_time != null) {
    endMs = parseMs('--end_time', args.end_time);
  } else {
    endMs = Date.now();
  }

  if (args.start_time != null) {
    startMs = parseMs('--start_time', args.start_time);
  } else {
    const days = Math.max(1, parseInt(String(args.days ?? '30'), 10) || 30);
    startMs = endMs - days * MS_PER_DAY;
  }

  if (startMs >= endMs) {
    console.error('Error / 错误: start_time must be < end_time / start_time 须小于 end_time');
    process.exit(1);
  }

  const params = new URLSearchParams();
  params.set('start_time', String(startMs));
  params.set('end_time', String(endMs));
  if (args.resource_pack_name) {
    params.set('resource_pack_name', String(args.resource_pack_name).trim());
  }

  return `${API_COSTS}?${params.toString()}`;
}

export async function main() {
  const args = parseArgs(process.argv);
  if (args.help) {
    printHelp();
    return;
  }
  if (args.action != null) {
    console.error('Error / 错误: --action has been removed. Use one flag: --costs | --import-env | --import-credentials | --configure');
    process.exit(1);
  }

  const modes = ['costs', 'configure', 'import-env', 'import-credentials'];
  const selected = modes.filter((m) => args[m]);
  if (selected.length > 1) {
    console.error(`Error / 错误: account mode flags are mutually exclusive / account 模式参数互斥: ${selected.map((s) => `--${s}`).join(', ')}`);
    process.exit(1);
  }
  const action = selected[0] || 'costs';

  if (action === 'import-env') {
    try {
      importCredentialsFromEnv();
    } catch (e) {
      console.error(`Error / 错误: ${e?.message || e}`);
      process.exit(1);
    }
    return;
  }

  if (action === 'import-credentials') {
    try {
      importCredentialsFromArgs(args.access_key_id, args.secret_access_key);
    } catch (e) {
      console.error(`Error / 错误: ${e?.message || e}`);
      process.exit(1);
    }
    return;
  }

  if (action === 'configure') {
    try {
      await promptInteractiveCredentialsFile();
    } catch (e) {
      console.error(`Error / 错误: ${e?.message || e}`);
      process.exit(1);
    }
    return;
  }

  const token = await getTokenOrExit();
  const pathWithQuery = buildCostsQueryPath(args);

  try {
    const data = await klingGet(pathWithQuery, token, { contentType: 'application/json' });
    console.log('Account / 账户资源 (API data):');
    console.log(JSON.stringify(data, null, 2));
  } catch (e) {
    console.error(`Error / 错误: ${e.message}`);
    process.exit(1);
  }
}

const __filename = fileURLToPath(import.meta.url);
if (process.argv[1] && resolve(__filename) === resolve(process.argv[1])) {
  main().catch((e) => {
    console.error(`Error / 错误: ${e?.message || e}`);
    process.exit(1);
  });
}

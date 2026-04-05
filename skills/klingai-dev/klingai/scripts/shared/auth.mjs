/**
 * Kling AI — 鉴权与本地凭证（本文件不发起 HTTP）
 *
 * 鉴权优先级：
 *   1. ~/.config/kling/.credentials（INI，[profile] access_key_id / secret_access_key）→ 请求时 makeJwt（30min exp）
 *   2. KLING_TOKEN（进程环境变量）
 *   3. kling.env 注入的 KLING_TOKEN（<storageRoot>/kling.env 或 ~/.config/kling/kling.env）
 * configure / import 写入 credentials，固定 default profile。
 * 存储根目录默认 ~/.config/kling；可选 KLING_STORAGE_ROOT 指向统一存储根。
 * 非凭证 env：读取 <storageRoot>/kling.env，并兼容读取 ~/.config/kling/kling.env（不覆盖启动前已在 process.env 中的键）。
 * 探测得到的 API Base 由 client 调用 `persistProbedApiBase` 写回 ~/.config/kling/kling.env 中的 KLING_API_BASE；
 * 不从文件注入 KLING_API_KEY（仅保留 KLING_TOKEN + credentials 模式）。
 *
 * 业务 HTTP：client.mjs
 */
import { createHmac } from 'node:crypto';
import {
  readFileSync, writeFileSync, mkdirSync, chmodSync,
} from 'node:fs';
import { dirname, resolve, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createInterface } from 'node:readline';

const __dir = dirname(fileURLToPath(import.meta.url));

const KLING_ENV_FILENAME = 'kling.env';
const CREDENTIALS_FILENAME = '.credentials';
const STORAGE_ROOT_ENV = 'KLING_STORAGE_ROOT';
const SHELL_ENV_KEYS = new Set(Object.keys(process.env));
const FILE_INJECTED_ENV_KEYS = new Set();

/** 写入 process.env 时跳过（凭证不走 dotenv 文件） */
const CREDENTIAL_ENV_DENYLIST = new Set(['KLING_API_KEY']);

/**
 * @param {string} content
 * @param {{ shellKeys: Set<string> }} opts
 */
function parseEnvContent(content, opts) {
  const { shellKeys, fileInjectedKeys } = opts;
  for (const line of content.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const eqIdx = trimmed.indexOf('=');
    if (eqIdx <= 0) continue;
    const key = trimmed.slice(0, eqIdx).trim();
    if (CREDENTIAL_ENV_DENYLIST.has(key)) continue;
    let val = trimmed.slice(eqIdx + 1).trim();
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1);
    }
    // 已在启动前导出的环境变量优先，不被文件覆盖。
    if (!shellKeys.has(key) && !(key in process.env)) {
      process.env[key] = val;
      fileInjectedKeys.add(key);
    }
  }
}

export function getKlingConfigDir() {
  const explicitRoot = (process.env[STORAGE_ROOT_ENV] || '').trim();
  if (explicitRoot) return resolve(explicitRoot);
  const home = process.env.HOME || process.env.USERPROFILE;
  if (home) return join(home, '.config', 'kling');
  return resolve(__dir, '..', '..', '..');
}

function getDefaultKlingEnvPath() {
  return join(getKlingConfigDir(), KLING_ENV_FILENAME);
}

function getLegacyHomeKlingEnvPath() {
  const home = process.env.HOME || process.env.USERPROFILE;
  if (!home) return null;
  return join(home, '.config', 'kling', KLING_ENV_FILENAME);
}

/** 更新或追加 KLING_API_BASE=…，仅写入 ~/.config/kling/kling.env */
function upsertEnvFileKey(content, key, value) {
  const line = `${key}=${value}`;
  const escaped = key.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const re = new RegExp(`^${escaped}=.*$`, 'm');
  if (re.test(content)) return content.replace(re, line);
  const trimmed = content.replace(/\s+$/, '');
  if (!trimmed) return `${line}\n`;
  return `${trimmed}\n${line}\n`;
}

(function loadEnvFiles() {
  const shellKeys = SHELL_ENV_KEYS;
  const explicitRoot = (process.env[STORAGE_ROOT_ENV] || '').trim();
  // When storage root is explicitly set, only load that root's env file to
  // avoid leaking host-level defaults (helps deterministic tests and sandboxing).
  const paths = explicitRoot
    ? [getDefaultKlingEnvPath()]
    : [getDefaultKlingEnvPath(), getLegacyHomeKlingEnvPath()].filter(Boolean);
  const seen = new Set();
  for (const p of paths) {
    if (seen.has(p)) continue;
    seen.add(p);
    try {
      parseEnvContent(readFileSync(p, 'utf-8'), { shellKeys, fileInjectedKeys: FILE_INJECTED_ENV_KEYS });
    } catch {}
  }
})();

/** 凭证 INI 路径：<storageRoot>/.credentials */
export function getCredentialsFilePath() {
  return join(getKlingConfigDir(), CREDENTIALS_FILENAME);
}

export function getActiveProfile() {
  return 'default';
}

export class CredentialsMissingError extends Error {
  constructor(msg = 'No credentials / 未配置凭证') {
    super(msg);
    this.name = 'CredentialsMissingError';
  }
}

function logAuthSource(source) {
  const messageMap = {
    credentials: 'Auth source / 鉴权来源: credentials (AK/SK -> JWT)',
    env_token: 'Auth source / 鉴权来源: KLING_TOKEN (process env)',
    file_token: 'Auth source / 鉴权来源: KLING_TOKEN (kling.env)',
  };
  const msg = messageMap[source];
  if (msg) console.error(msg);
}

function parseCredentialsIni(content) {
  const profiles = {};
  let current = null;
  for (const line of content.split('\n')) {
    const t = line.trim();
    if (!t || t.startsWith('#') || t.startsWith(';')) continue;
    const m = t.match(/^\[([^\]]+)\]\s*$/);
    if (m) {
      current = m[1].trim();
      if (!profiles[current]) profiles[current] = {};
      continue;
    }
    const eqIdx = t.indexOf('=');
    if (eqIdx <= 0 || !current) continue;
    const k = t.slice(0, eqIdx).trim();
    let v = t.slice(eqIdx + 1).trim();
    if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
      v = v.slice(1, -1);
    }
    profiles[current][k] = v;
  }
  return profiles;
}

/** @returns {{ access_key_id: string, secret_access_key: string }} */
export function readCredentialsProfile(profile) {
  try {
    const raw = readFileSync(getCredentialsFilePath(), 'utf-8');
    const all = parseCredentialsIni(raw);
    const p = all[profile] || {};
    const ak = String(p.access_key_id || p.access_key || '').trim();
    const sk = String(p.secret_access_key || p.secret_key || '').trim();
    return { access_key_id: ak, secret_access_key: sk };
  } catch {
    return { access_key_id: '', secret_access_key: '' };
  }
}

export function hasStoredAccessKeys() {
  const { access_key_id, secret_access_key } = readCredentialsProfile(getActiveProfile());
  return Boolean(access_key_id && secret_access_key);
}

export function hasSessionBearerOverride() {
  return Boolean((process.env.KLING_TOKEN || '').trim());
}

export function hasUsableCredentialSource() {
  return hasStoredAccessKeys() || hasSessionBearerOverride();
}

/**
 * 写入 [profile] 下 AK/SK，Unix 上 chmod 600
 * @param {string} profile
 * @param {string} accessKey
 * @param {string} secretKey
 * @param {Record<string,string>} [extra]  如 region
 */
export function writeCredentialsProfile(profile, accessKey, secretKey, extra = {}) {
  const path = getCredentialsFilePath();
  mkdirSync(dirname(path), { recursive: true });
  let all = {};
  try {
    all = parseCredentialsIni(readFileSync(path, 'utf-8'));
  } catch {}
  all[profile] = {
    ...all[profile],
    access_key_id: String(accessKey || '').trim(),
    secret_access_key: String(secretKey || '').trim(),
    ...extra,
  };
  const lines = [];
  for (const prof of Object.keys(all)) {
    lines.push(`[${prof}]`);
    const o = all[prof];
    for (const [k, v] of Object.entries(o)) {
      if (v == null || String(v) === '') continue;
      lines.push(`${k} = ${String(v)}`);
    }
    lines.push('');
  }
  writeFileSync(path, lines.join('\n').trimEnd() + '\n');
  try {
    if (process.platform !== 'win32') chmodSync(path, 0o600);
  } catch {}
  return path;
}

// —— Skill 版本 / 请求头 ——
const DEFAULT_SKILL_VERSION = '1.0.0';
let skillVersion = DEFAULT_SKILL_VERSION;
export function setSkillVersion(version) {
  skillVersion = String(version || DEFAULT_SKILL_VERSION);
}
export function getSkillVersion() {
  return skillVersion;
}

export function makeKlingHeaders(token, contentType = 'application/json') {
  const h = { 'User-Agent': `Kling-Provider-Skill/${getSkillVersion()}` };
  if (token) h['Authorization'] = `Bearer ${token}`;
  if (contentType) h['Content-Type'] = contentType;
  return h;
}

function base64url(buf) {
  return Buffer.from(buf).toString('base64')
    .replace(/=/g, '')
    .replace(/\+/g, '-')
    .replace(/\//g, '_');
}

function makeJwt(accessKey, secretKey) {
  const header = base64url(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const now = Math.floor(Date.now() / 1000);
  const payload = base64url(JSON.stringify({
    iss: accessKey,
    exp: now + 1800,
    nbf: now - 5,
  }));
  const signature = base64url(
    createHmac('sha256', secretKey).update(`${header}.${payload}`).digest()
  );
  return `${header}.${payload}.${signature}`;
}

/**
 * 1) 先使用 credentials 文件 AK/SK（每次调用重新签发 JWT，30min exp）
 * 2) 否则使用进程环境变量中的 KLING_TOKEN
 * 3) 最后使用 kling.env 注入的 KLING_TOKEN
 */
export function getBearerToken() {
  const profile = getActiveProfile();
  const { access_key_id, secret_access_key } = readCredentialsProfile(profile);
  if (access_key_id && secret_access_key) {
    logAuthSource('credentials');
    return makeJwt(access_key_id, secret_access_key);
  }
  const tokenRaw = String(process.env.KLING_TOKEN || '').trim();
  if (tokenRaw) {
    const isFileInjected = FILE_INJECTED_ENV_KEYS.has('KLING_TOKEN');
    if (!isFileInjected || SHELL_ENV_KEYS.has('KLING_TOKEN')) {
      logAuthSource('env_token');
      return tokenRaw.toLowerCase().startsWith('bearer ')
        ? tokenRaw.slice(7).trim()
        : tokenRaw;
    }
  }
  if (tokenRaw) {
    logAuthSource('file_token');
    return tokenRaw.toLowerCase().startsWith('bearer ')
      ? tokenRaw.slice(7).trim()
      : tokenRaw;
  }
  throw new CredentialsMissingError(
    'Configure AK/SK in credentials under KLING_STORAGE_ROOT (or ~/.config/kling), or set KLING_TOKEN (env first, then kling.env). '
    + 'Get keys: https://app.klingai.com/cn/dev/console/application (Global: https://app.klingai.com/global/dev/console/application) / '
    + '请先在 KLING_STORAGE_ROOT（或 ~/.config/kling）下配置 AK/SK（credentials），或设置 KLING_TOKEN（先环境变量，后 kling.env）。'
    + '密钥获取: https://app.klingai.com/cn/dev/console/application （国际站: https://app.klingai.com/global/dev/console/application）',
  );
}

export function getConfiguredApiBase() {
  const base = (process.env.KLING_API_BASE || '').trim();
  return base || null;
}

/** 将探测到的业务 API 根写入 ~/.config/kling/kling.env（仅 KLING_API_BASE 一行） */
export function persistProbedApiBase(baseUrl) {
  const b = String(baseUrl || '').trim();
  if (!b) return;
  const dir = getKlingConfigDir();
  const path = getDefaultKlingEnvPath();
  mkdirSync(dir, { recursive: true });
  let raw = '';
  try {
    raw = readFileSync(path, 'utf-8');
  } catch {}
  writeFileSync(path, upsertEnvFileKey(raw, 'KLING_API_BASE', b));
  process.env.KLING_API_BASE = b;
}

export { makeJwt };

function readHiddenLine(prompt) {
  function sanitizeChunk(chunk) {
    // Strip bracketed-paste markers (\x1b[200~...\x1b[201~), keep printable chars only.
    return String(chunk || '')
      .replace(/\u001b\[200~/g, '')
      .replace(/\u001b\[201~/g, '')
      .replace(/[\u0000-\u001f\u007f]/g, '');
  }

  const stdin = process.stdin;
  const stdout = process.stderr;
  if (!stdin.isTTY) {
    return new Promise((r) => {
      const rl = createInterface({ input: stdin, output: stdout });
      rl.question(prompt, (a) => {
        rl.close();
        r(a.trim());
      });
    });
  }
  stdout.write(prompt);
  return new Promise((resolveLine) => {
    stdin.setRawMode(true);
    stdin.resume();
    stdin.setEncoding('utf8');
    let s = '';
    const onData = (key) => {
      const k = String(key);
      if (k === '\u0003') {
        stdin.setRawMode(false);
        stdin.removeListener('data', onData);
        stdin.pause();
        process.exit(1);
      }
      if (k === '\r' || k === '\n') {
        stdin.setRawMode(false);
        stdin.removeListener('data', onData);
        stdin.pause();
        stdout.write('\n');
        resolveLine(s);
        return;
      }
      if (k === '\u007f' || k === '\b') {
        s = s.slice(0, -1);
        return;
      }
      s += sanitizeChunk(k);
    };
    stdin.on('data', onData);
  });
}

/** 交互式录入 AK/SK → credentials（SK 在 TTY 下隐藏输入，支持粘贴） */
export async function promptInteractiveCredentialsFile() {
  if (!process.stdin.isTTY || !process.stderr.isTTY) {
    throw new CredentialsMissingError(
      'TTY required / 需要交互式终端',
    );
  }

  console.error('\n── Kling AI configure / 可灵凭证配置 ─────────────');
  console.error(`Profile / 配置名: ${getActiveProfile()}`);
  console.error(`File / 文件: ${getCredentialsFilePath()}`);
  console.error('Get keys / 获取密钥: https://app.klingai.com/cn/dev/console/application');
  console.error('────────────────────────────────────────────────\n');

  const rl1 = createInterface({ input: process.stdin, output: process.stderr });
  const accessKey = await new Promise((r) => {
    rl1.question('Access Key ID / 访问密钥 ID: ', (a) => r(a.trim()));
  });
  rl1.close();
  if (!accessKey) throw new Error('Access Key required / 需要 Access Key');

  const secretKey = await readHiddenLine('Secret Access Key / 秘密访问密钥（隐藏输入，可粘贴）: ');
  if (!secretKey) throw new Error('Secret Key required / 需要 Secret Key');

  const savePath = writeCredentialsProfile(getActiveProfile(), accessKey, secretKey);
  console.error(`\n✓ Saved / 已保存（密钥未在日志中输出）: ${savePath}\n`);
  return makeJwt(accessKey, secretKey);
}

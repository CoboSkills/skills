/**
 * Kling AI HTTP client (zero external deps, Node.js 18+ fetch)
 *
 * - **klingGet / klingPost**：Bearer 鉴权 + resolveApiBase（业务 API）
 */
import {
  getBearerToken, makeKlingHeaders, getConfiguredApiBase, persistProbedApiBase,
} from './auth.mjs';

const API_BASE = 'https://api-beijing.klingai.com';
const CANDIDATE_BASES = [
  API_BASE,
  'https://api-singapore.klingai.com',
];

async function probeBase(base, token) {
  try {
    const res = await fetch(`${base}/v1/videos/text2video?pageNum=1&pageSize=1`, {
      method: 'GET',
      headers: makeKlingHeaders(token, null),
      signal: AbortSignal.timeout(8000),
    });
    if (!res.ok) return false;
    const json = await res.json().catch(() => null);
    return json != null && (json.code === 0 || json.code === 200);
  } catch {
    return false;
  }
}

let _resolvedBase = null;

async function resolveApiBase(token) {
  if (_resolvedBase) return _resolvedBase;
  const configuredApiBase = getConfiguredApiBase();
  if (configuredApiBase) {
    _resolvedBase = configuredApiBase;
    return _resolvedBase;
  }

  console.error('\n🔍 Probing API endpoints... / 正在检测 API 节点...');
  for (const base of CANDIDATE_BASES) {
    process.stderr.write(`   ${base} ... `);
    if (await probeBase(base, token)) {
      process.stderr.write('✓ OK\n\n');
      _resolvedBase = base;
      try {
        persistProbedApiBase(base);
      } catch {}
      return _resolvedBase;
    }
    process.stderr.write('✗\n');
  }

  console.error('\n❌ Cannot connect to any Kling API endpoint / 无法连接任何可灵 API 节点');
  for (const base of CANDIDATE_BASES) console.error(`   • ${base}`);
  console.error('\nPossible causes / 可能原因:');
  console.error('  1. Token invalid or expired / Token 无效或已过期:');
  console.error('     China / 国内: https://app.klingai.com/cn/dev/console/application');
  console.error('     Global / 国际: https://app.klingai.com/global/dev/console/application');
  console.error('  2. Network issue / 网络问题');
  console.error('\nCheck credentials file or KLING_TOKEN, then retry / 检查 credentials 或 KLING_TOKEN 后重试:\n');
  process.exit(1);
}

/**
 * 保护 JSON 中的大整数字段（防止 Number 精度丢失）
 * 将 element_id, task_id 等大整数字段转为字符串
 */
function protectBigInts(text) {
  return text.replace(
    /"(element_id|task_id|elementId|taskId)":\s*(\d{15,})/g,
    '"$1":"$2"'
  );
}

/**
 * 解析可灵 API 响应，code 为 0 或 200 为成功
 */
function parseResponse(json) {
  if (json.code !== 0 && json.code !== 200) {
    throw new Error(`API error / API 错误 (code=${json.code}): ${json.message || 'Unknown error'}`);
  }
  return json.data;
}

async function safeFetch(url, init, context) {
  try {
    return await fetch(url, init);
  } catch (e) {
    const baseHint = getConfiguredApiBase() || '<auto>';
    const msg = e?.message || String(e);
    throw new Error(
      `Network error / 网络错误: ${msg}\n`
      + `Request / 请求: ${context.method} ${url}\n`
      + `KLING_API_BASE: ${baseHint}\n`
      + 'Hint / 提示: check KLING_API_BASE and network/DNS/proxy, or remove KLING_API_BASE to auto-probe official endpoints / '
      + '请检查 KLING_API_BASE 与网络(DNS/代理)，或移除 KLING_API_BASE 让脚本自动探测官方节点。',
    );
  }
}

/**
 * POST 请求可灵 API
 * @param {string} path  API 路径，如 /v1/videos/image2video
 * @param {object} body  请求体
 * @param {string} [token]  可选 token，不传则自动获取
 * @returns {Promise<object>} data 字段
 */
export async function klingPost(path, body, token) {
  if (!token) token = getBearerToken();
  const base = await resolveApiBase(token);
  const url = `${base}${path}`;
  const res = await safeFetch(url, {
    method: 'POST',
    headers: makeKlingHeaders(token),
    body: JSON.stringify(body),
  }, { method: 'POST' });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  const text = await res.text();
  return parseResponse(JSON.parse(protectBigInts(text)));
}

/**
 * GET 请求可灵 API
 * @param {string} path  API 路径，如 /v1/videos/image2video/{task_id}
 * @param {string} [token]  可选 token，不传则自动获取
 * @param {{ contentType?: string|null }} [options]  如部分接口要求 `Content-Type: application/json`（传 `'application/json'`）；默认不传 Content-Type
 * @returns {Promise<object>} data 字段
 */
export async function klingGet(path, token, options = {}) {
  if (!token) token = getBearerToken();
  const base = await resolveApiBase(token);
  const ct = options.contentType !== undefined ? options.contentType : null;
  const url = `${base}${path}`;
  const res = await safeFetch(url, {
    method: 'GET',
    headers: makeKlingHeaders(token, ct),
  }, { method: 'GET' });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  const text = await res.text();
  return parseResponse(JSON.parse(protectBigInts(text)));
}

export { getBearerToken, makeKlingHeaders, setSkillVersion, getSkillVersion } from './auth.mjs';
export { API_BASE, CANDIDATE_BASES, resolveApiBase };

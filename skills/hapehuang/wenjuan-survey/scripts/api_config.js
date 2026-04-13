#!/usr/bin/env node
/**
 * 问卷网 API 统一配置
 * 可通过环境变量 WENJUAN_HOST 覆盖默认域名。
 */

const DEFAULT_WENJUAN_HOST = "https://www.wenjuan.com";

const WENJUAN_HOST = String(process.env.WENJUAN_HOST || DEFAULT_WENJUAN_HOST)
  .trim()
  .replace(/\/+$/, "");

function wenjuanUrl(pathname = "") {
  if (!pathname) return WENJUAN_HOST;
  const p = String(pathname);
  return `${WENJUAN_HOST}${p.startsWith("/") ? p : `/${p}`}`;
}

module.exports = {
  DEFAULT_WENJUAN_HOST,
  WENJUAN_HOST,
  wenjuanUrl,
};

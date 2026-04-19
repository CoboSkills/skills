#!/usr/bin/env node
/**
 * Resolves the FFmpeg (and optionally ffprobe) binary path.
 *
 * Priority:
 *   1. FFMPEG_PATH / FFPROBE_PATH env vars
 *   2. System binary (which / where)
 *   3. ffmpeg-static / ffprobe-static bundled binary
 *
 * Usage as a module:
 *   const { resolveFfmpeg, resolveFfprobe } = require('./resolve_ffmpeg');
 *   const ffmpegPath = resolveFfmpeg();
 *
 * Usage as a CLI:
 *   node resolve_ffmpeg.js             → prints ffmpeg path
 *   node resolve_ffmpeg.js --ffprobe   → prints ffprobe path
 *   node resolve_ffmpeg.js --json      → prints JSON with both paths and sources
 */

'use strict';

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

function findSystemBinary(name) {
  try {
    const cmd = process.platform === 'win32' ? `where ${name}` : `which ${name}`;
    const result = execSync(cmd, { stdio: ['ignore', 'pipe', 'ignore'] })
      .toString()
      .trim()
      .split(/\r?\n/)[0];
    if (result && fs.existsSync(result)) return result;
  } catch {
    // not found on PATH
  }
  return null;
}

function tryRequire(pkg) {
  try {
    // ffprobe-static returns { path: '...' }; ffmpeg-static returns a string
    const mod = require(pkg);
    return typeof mod === 'string' ? mod : (mod && mod.path) || null;
  } catch {
    return null;
  }
}

function resolveFfmpeg() {
  if (process.env.FFMPEG_PATH) {
    const p = process.env.FFMPEG_PATH;
    if (!fs.existsSync(p)) throw new Error(`FFMPEG_PATH set but not found: ${p}`);
    return p;
  }

  const system = findSystemBinary('ffmpeg');
  if (system) return system;

  const bundled = tryRequire('ffmpeg-static');
  if (bundled && fs.existsSync(bundled)) return bundled;

  throw new Error(
    'FFmpeg not found. Install system FFmpeg or run: npm install ffmpeg-static'
  );
}

function resolveFfprobe() {
  if (process.env.FFPROBE_PATH) {
    const p = process.env.FFPROBE_PATH;
    if (!fs.existsSync(p)) throw new Error(`FFPROBE_PATH set but not found: ${p}`);
    return p;
  }

  const system = findSystemBinary('ffprobe');
  if (system) return system;

  const bundled = tryRequire('ffprobe-static');
  if (bundled && fs.existsSync(bundled)) return bundled;

  throw new Error(
    'ffprobe not found. Install system FFmpeg or run: npm install ffprobe-static'
  );
}

function resolveAll() {
  const result = {};

  try {
    const ffmpegPath = resolveFfmpeg();
    const source = process.env.FFMPEG_PATH
      ? 'env'
      : findSystemBinary('ffmpeg') === ffmpegPath
        ? 'system'
        : 'bundled';
    result.ffmpeg = { path: ffmpegPath, source };
  } catch (e) {
    result.ffmpeg = { path: null, source: null, error: e.message };
  }

  try {
    const ffprobePath = resolveFfprobe();
    const source = process.env.FFPROBE_PATH
      ? 'env'
      : findSystemBinary('ffprobe') === ffprobePath
        ? 'system'
        : 'bundled';
    result.ffprobe = { path: ffprobePath, source };
  } catch (e) {
    result.ffprobe = { path: null, source: null, error: e.message };
  }

  return result;
}

// CLI entry point
if (require.main === module) {
  const args = process.argv.slice(2);

  if (args.includes('--json')) {
    console.log(JSON.stringify(resolveAll(), null, 2));
  } else if (args.includes('--ffprobe')) {
    try {
      console.log(resolveFfprobe());
    } catch (e) {
      console.error(e.message);
      process.exit(1);
    }
  } else {
    try {
      console.log(resolveFfmpeg());
    } catch (e) {
      console.error(e.message);
      process.exit(1);
    }
  }
}

module.exports = { resolveFfmpeg, resolveFfprobe, resolveAll };

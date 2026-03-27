#!/usr/bin/env node
/**
 * pst_extractor_helper.js
 *
 * Native PST parser using the `pst-extractor` npm package.
 * Called by parse_local.py when readpst is unavailable.
 *
 * Usage:
 *   node pst_extractor_helper.js <pst_file> [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--max N]
 *
 * Output: JSON array of email records (stdout), log messages on stderr.
 *
 * Prerequisites (install once before first use):
 *   cd email-summarizer/scripts && npm install
 *   # or: npm install -g pst-extractor
 *
 * The script resolves pst-extractor from (in order):
 *   1. node_modules/ sibling to this script  (recommended: npm install in scripts/)
 *   2. Global npm prefix                     (npm install -g pst-extractor)
 *
 * NOTE: This script does NOT auto-install any packages at runtime.
 *       Run `npm install` in the scripts/ directory first.
 */

'use strict';

const fs   = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// ── Module resolution (no auto-install) ──────────────────────────────────────

function tryRequire(modName, searchDirs) {
  for (const dir of searchDirs) {
    const candidate = path.join(dir, 'node_modules', modName);
    if (fs.existsSync(candidate)) {
      return require(candidate);
    }
  }
  return null;
}

const scriptDir = __dirname;

let PSTFile, PSTFolder, PSTMessage, PSTAttachment;

try {
  // 1. Look for node_modules next to this script
  let mod = tryRequire('pst-extractor', [scriptDir]);

  // 2. Fall back to global npm prefix
  if (!mod) {
    try {
      const globalRoot = execSync('npm root -g', { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim();
      const globalCandidate = path.join(globalRoot, 'pst-extractor');
      if (fs.existsSync(globalCandidate)) mod = require(globalCandidate);
    } catch (_) {}
  }

  if (!mod) {
    process.stderr.write(
      '[pst-helper] ERROR: pst-extractor not found.\n' +
      'Please install it first:\n' +
      '  cd email-summarizer/scripts && npm install\n' +
      'or:\n' +
      '  npm install -g pst-extractor\n'
    );
    process.exit(1);
  }

  ({ PSTFile, PSTFolder, PSTMessage, PSTAttachment } = mod);
} catch (e) {
  process.stderr.write(`[pst-helper] Fatal: cannot load pst-extractor: ${e.message}\n`);
  process.exit(1);
}

// ── Argument parsing ──────────────────────────────────────────────────────────

const args = process.argv.slice(2);
if (args.length === 0 || args[0] === '--help') {
  process.stderr.write('Usage: node pst_extractor_helper.js <file.pst> [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--max N]\n');
  process.exit(0);
}

const pstPath = args[0];
let sinceMs = null;
let untilMs = null;
let maxCount = 2000;

for (let i = 1; i < args.length; i++) {
  if (args[i] === '--since' && args[i + 1]) { sinceMs = new Date(args[++i]).getTime(); }
  else if (args[i] === '--until' && args[i + 1]) { untilMs = new Date(args[++i]).getTime(); }
  else if (args[i] === '--max'   && args[i + 1]) { maxCount = parseInt(args[++i], 10); }
}

if (!fs.existsSync(pstPath)) {
  process.stderr.write(`[pst-helper] File not found: ${pstPath}\n`);
  process.exit(1);
}

// ── HTML → plain text (lightweight) ──────────────────────────────────────────

function htmlToText(html) {
  if (!html) return '';
  return html
    .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
    .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/p>/gi, '\n')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\s{3,}/g, '  ')
    .trim();
}

// ── Date helpers ──────────────────────────────────────────────────────────────

function toIso(dateObj) {
  if (!dateObj) return '';
  try { return new Date(dateObj).toISOString(); } catch (_) { return String(dateObj); }
}

function inRange(dateObj) {
  if (!dateObj) return true;
  const ms = new Date(dateObj).getTime();
  if (isNaN(ms)) return true;
  if (sinceMs !== null && ms < sinceMs) return false;
  if (untilMs !== null && ms >= untilMs) return false;
  return true;
}

// ── Folder name → direction heuristic ────────────────────────────────────────

const SENT_HINTS = ['sent', '已发送', '发件箱', 'outbox', 'outgoing'];

function isSentFolder(name) {
  if (!name) return false;
  const lower = name.toLowerCase();
  return SENT_HINTS.some(h => lower.includes(h));
}

// ── PST traversal ─────────────────────────────────────────────────────────────

const results = [];
let totalSkipped = 0;
let idCounter = 0;

function processFolder(folder, folderPath) {
  const name = folder.displayName || '';
  const currentPath = folderPath ? `${folderPath}/${name}` : name;
  const direction = isSentFolder(name) ? 'sent' : 'received';

  // Process emails in this folder
  if (folder.emailCount > 0 && results.length < maxCount) {
    let item;
    try { item = folder.getNextChild(); } catch (_) { item = null; }

    while (item !== null && results.length < maxCount) {
      if (item instanceof PSTMessage) {
        const dateObj = item.messageDeliveryTime || item.creationTime;
        if (!inRange(dateObj)) {
          totalSkipped++;
        } else {
          // Body: prefer plain text, fall back to HTML→text
          let body = (item.body || '').trim();
          if (!body && item.bodyHTML) {
            body = htmlToText(item.bodyHTML);
          }
          body = body.slice(0, 2000);

          // Attachments
          const attachmentNames = [];
          for (let ai = 0; ai < item.numberOfAttachments; ai++) {
            try {
              const att = item.getAttachment(ai);
              if (att && att.displayName) attachmentNames.push(att.displayName);
            } catch (_) {}
          }

          results.push({
            id:          String(++idCounter),
            direction,
            folder:      currentPath,
            date:        toIso(dateObj),
            from:        item.senderName
                           ? `${item.senderName} <${item.senderEmailAddress || ''}>`
                           : (item.senderEmailAddress || ''),
            to:          item.displayTo  || '',
            cc:          item.displayCC  || '',
            subject:     item.subject    || '(no subject)',
            body,
            attachments: attachmentNames,
          });
        }
      }

      try { item = folder.getNextChild(); } catch (_) { break; }
    }
  }

  // Recurse into subfolders
  let subfolders;
  try { subfolders = folder.getSubFolders(); } catch (_) { return; }
  for (const sub of subfolders) {
    if (results.length >= maxCount) break;
    processFolder(sub, currentPath);
  }
}

// ── Main ──────────────────────────────────────────────────────────────────────

try {
  process.stderr.write(`[pst-helper] Opening ${pstPath} ...\n`);
  const pstFile = new PSTFile(pstPath);
  const root = pstFile.getRootFolder();
  processFolder(root, '');
  process.stderr.write(`[pst-helper] Done. ${results.length} emails loaded, ${totalSkipped} skipped by date filter.\n`);
  process.stdout.write(JSON.stringify(results, null, 2));
} catch (e) {
  process.stderr.write(`[pst-helper] Error: ${e.message}\n${e.stack}\n`);
  process.exit(1);
}

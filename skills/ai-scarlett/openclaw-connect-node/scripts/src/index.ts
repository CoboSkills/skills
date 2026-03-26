/**
 * OpenClaw Connect Enterprise - Node Server v3.0
 * Can run standalone OR be mounted on Hub under /node prefix
 */

import Fastify, { FastifyInstance, FastifyPluginCallback } from 'fastify';
import cors from '@fastify/cors';
import fastifyStatic from '@fastify/static';
import axios from 'axios';
import * as os from 'os';
import * as path from 'path';
import * as fs from 'fs';
import { execSync, spawn } from 'child_process';

// ─── Configuration ───────────────────────────────────────────────
const HUB_URL = process.env.HUB_URL || '';
const APP_ID = process.env.APP_ID || '';
const APP_KEY = process.env.APP_KEY || '';
const APP_TOKEN = process.env.APP_TOKEN || '';
const NODE_PORT = parseInt(process.env.NODE_PORT || '3100');

// ─── Connection State ────────────────────────────────────────────
let nodeId = '';
let sessionToken = '';
let connected = false;
let connecting = false;
let lastHeartbeat = '';
let registeredAt = '';
let connectionError = '';

interface ConnectionLog {
  time: string;
  type: 'info' | 'error' | 'success' | 'warning';
  message: string;
}
const connectionLogs: ConnectionLog[] = [];
function addLog(type: ConnectionLog['type'], message: string) {
  connectionLogs.unshift({ time: new Date().toISOString(), type, message });
  if (connectionLogs.length > 100) connectionLogs.length = 100;
  console.log(`[Node][${type.toUpperCase()}] ${message}`);
}

// ─── Local Data (read/write) ─────────────────────────────────────
interface Memory {
  id: string;
  type: 'stm' | 'mtm' | 'ltm';
  content: string;
  source: string;
  importance: number;
  tags: string[];
  createdAt: string;
  updatedAt: string;
}

// Load from OpenClaw memory files
const evoMemories = new Map<string, Memory>();
const homeDir = process.env.HOME || '/root';
const MEMORY_DIR = path.join(homeDir, '.openclaw/workspace/memory');
const MEMORY_MD = path.join(homeDir, '.openclaw/workspace/MEMORY.md');
const MEMORIES_JSONL = path.join(MEMORY_DIR, 'items/memories.jsonl');

function loadOpenClawMemories() {
  // 1. Load memories.jsonl (structured memories)
  if (fs.existsSync(MEMORIES_JSONL)) {
    const lines = fs.readFileSync(MEMORIES_JSONL, 'utf-8').trim().split('\n');
    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const m = JSON.parse(line);
        evoMemories.set(m.id, {
          id: m.id,
          type: m.category === 'long_term' ? 'ltm' : m.category === 'short_term' ? 'stm' : 'mtm',
          content: m.content || m.topic || '',
          source: m.source || 'openclaw',
          importance: m.confidence ? Math.round(m.confidence * 10) : 5,
          tags: m.related_ids || [],
          createdAt: new Date(m.timestamp * 1000).toISOString(),
          updatedAt: new Date(m.timestamp * 1000).toISOString(),
        });
      } catch {}
    }
    console.log(`[Memory] Loaded ${lines.length} memories from memories.jsonl`);
  }

  // 2. Load MEMORY.md (long-term curated memories)
  if (fs.existsSync(MEMORY_MD)) {
    const content = fs.readFileSync(MEMORY_MD, 'utf-8');
    const sections = content.split(/^##\s+/m);
    for (const section of sections.slice(1)) {
      const title = section.split('\n')[0].trim();
      const body = section.split('\n').slice(1).join('\n').trim();
      if (!title || !body) continue;
      const id = `mem-md-${title.slice(0, 20).replace(/[^a-z0-9]/gi, '-')}`;
      evoMemories.set(id, {
        id,
        type: 'ltm',
        content: `## ${title}\n\n${body}`,
        source: 'MEMORY.md',
        importance: 8,
        tags: ['long-term', 'curated'],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      });
    }
    console.log(`[Memory] Loaded sections from MEMORY.md`);
  }

  // 3. Load daily memory files (memory/YYYY-MM-DD.md)
  if (fs.existsSync(MEMORY_DIR)) {
    const files = fs.readdirSync(MEMORY_DIR).filter(f => /^\d{4}-\d{2}-\d{2}\.md$/.test(f));
    for (const file of files) {
      const content = fs.readFileSync(path.join(MEMORY_DIR, file), 'utf-8');
      const id = `mem-daily-${file.replace('.md', '')}`;
      evoMemories.set(id, {
        id,
        type: 'stm',
        content: content.slice(0, 2000), // Truncate for preview
        source: `memory/${file}`,
        importance: 6,
        tags: ['daily', file.replace('.md', '')],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      });
    }
    console.log(`[Memory] Loaded ${files.length} daily memory files`);
  }
}

function saveMemoryToJsonl(memory: Memory) {
  try {
    if (!fs.existsSync(MEMORY_DIR)) fs.mkdirSync(MEMORY_DIR, { recursive: true });
    if (!fs.existsSync(path.join(MEMORY_DIR, 'items'))) {
      fs.mkdirSync(path.join(MEMORY_DIR, 'items'), { recursive: true });
    }
    const line = JSON.stringify({
      id: memory.id,
      category: memory.type === 'ltm' ? 'long_term' : memory.type === 'stm' ? 'short_term' : 'medium_term',
      topic: memory.content.slice(0, 50),
      content: memory.content,
      source: memory.source,
      timestamp: new Date(memory.createdAt).getTime() / 1000,
      confidence: memory.importance / 10,
      related_ids: memory.tags,
      embeddings: null,
      metadata: {},
    }) + '\n';
    fs.appendFileSync(MEMORIES_JSONL, line);
  } catch (err) {
    console.error('[Memory] Failed to save to JSONL:', err);
  }
}

// ─── Synced Data (read-only) ─────────────────────────────────────
let syncedTasks: any[] = [];
let syncedAgents: any[] = [];
let agentSyncTimer: NodeJS.Timeout | null = null;
// ─── localTasks 持久化到文件 ───
const LOCAL_TASKS_FILE = path.join(process.env.DATA_DIR || path.join(process.env.HOME || '/root', '.openclaw-node'), 'local-tasks.json');

function loadLocalTasks(): Map<string, any> {
  const map = new Map<string, any>();
  try {
    const dir = path.dirname(LOCAL_TASKS_FILE);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    if (fs.existsSync(LOCAL_TASKS_FILE)) {
      const data = JSON.parse(fs.readFileSync(LOCAL_TASKS_FILE, 'utf-8'));
      if (Array.isArray(data)) data.forEach(t => map.set(t.id, t));
    }
  } catch {}
  return map;
}

function saveLocalTasks() {
  try {
    const dir = path.dirname(LOCAL_TASKS_FILE);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(LOCAL_TASKS_FILE, JSON.stringify(Array.from(localTasks.values()), null, 2));
  } catch {}
}

let localTasks = loadLocalTasks();  // 从文件恢复
let syncedSkills: any[] = [];

// ─── Local Skills (read from OpenClaw installation) ──────────────
interface LocalSkill {
  id: string;
  name: string;
  description: string;
  type: 'installed' | 'builtin';
  enabled: boolean;
  path: string;
  usageToday: number;
  usage7d: number;
  usageTotal: number;
  lastUsed: string | null;
  active: boolean;
}
let localSkills: LocalSkill[] = [];
let skillUsageMap = new Map<string, { today: number; week: number; total: number; lastUsed: string | null }>();

function scanLocalSkills() {
  const skills: LocalSkill[] = [];
  const homeDir = process.env.HOME || '/root';

  // 1. User-installed skills: ~/.openclaw/workspace/skills/*/SKILL.md
  const userSkillsDir = path.join(homeDir, '.openclaw/workspace/skills');
  if (fs.existsSync(userSkillsDir)) {
    for (const dir of fs.readdirSync(userSkillsDir)) {
      const skillMd = path.join(userSkillsDir, dir, 'SKILL.md');
      if (!fs.existsSync(skillMd)) continue;
      const { name, description } = parseSkillFrontmatter(skillMd);
      const usage = skillUsageMap.get(name) || { today: 0, week: 0, total: 0, lastUsed: null };
      skills.push({
        id: `skill-${dir}`,
        name: name || dir,
        description: description || '',
        type: 'installed',
        enabled: true,
        path: path.join(userSkillsDir, dir),
        usageToday: usage.today,
        usage7d: usage.week,
        usageTotal: usage.total,
        lastUsed: usage.lastUsed,
        active: usage.today > 0,
      });
    }
  }

  // 2. Builtin skills: find openclaw's bundled skills
  const builtinPatterns = [
    path.join(homeDir, '.local/share/pnpm/global/5/.pnpm/openclaw@*/node_modules/openclaw/skills'),
  ];
  for (const pattern of builtinPatterns) {
    try {
      const { execSync: ex } = require('child_process');
      const resolved = ex(`ls -d ${pattern} 2>/dev/null`).toString().trim().split('\n').filter(Boolean);
      for (const skillsRoot of resolved) {
        if (!fs.existsSync(skillsRoot)) continue;
        for (const dir of fs.readdirSync(skillsRoot)) {
          const skillMd = path.join(skillsRoot, dir, 'SKILL.md');
          if (!fs.existsSync(skillMd)) continue;
          // Skip if already in user skills (overridden)
          if (skills.some(s => s.name === dir)) continue;
          const { name, description } = parseSkillFrontmatter(skillMd);
          const usage = skillUsageMap.get(name || dir) || { today: 0, week: 0, total: 0, lastUsed: null };
          skills.push({
            id: `builtin-${dir}`,
            name: name || dir,
            description: description || '',
            type: 'builtin',
            enabled: true,
            path: path.join(skillsRoot, dir),
            usageToday: usage.today,
            usage7d: usage.week,
            usageTotal: usage.total,
            lastUsed: usage.lastUsed,
            active: usage.today > 0,
          });
        }
      }
    } catch {}
  }

  // 3. Extension skills: ~/.openclaw/extensions/*/skills/*/SKILL.md
  const extDir = path.join(homeDir, '.openclaw/extensions');
  if (fs.existsSync(extDir)) {
    for (const ext of fs.readdirSync(extDir)) {
      const extSkillsDir = path.join(extDir, ext, 'skills');
      if (!fs.existsSync(extSkillsDir)) continue;
      for (const dir of fs.readdirSync(extSkillsDir)) {
        const skillMd = path.join(extSkillsDir, dir, 'SKILL.md');
        if (!fs.existsSync(skillMd)) continue;
        if (skills.some(s => s.name === dir)) continue;
        const { name, description } = parseSkillFrontmatter(skillMd);
        const usage = skillUsageMap.get(name || dir) || { today: 0, week: 0, total: 0, lastUsed: null };
        skills.push({
          id: `ext-${ext}-${dir}`,
          name: name || dir,
          description: description || '',
          type: 'installed',
          enabled: true,
          path: path.join(extSkillsDir, dir),
          usageToday: usage.today,
          usage7d: usage.week,
          usageTotal: usage.total,
          lastUsed: usage.lastUsed,
          active: usage.today > 0,
        });
      }
    }
  }

  localSkills = skills;
  return skills;
}

function parseSkillFrontmatter(filepath: string): { name: string; description: string } {
  try {
    const content = fs.readFileSync(filepath, 'utf-8');
    const match = content.match(/^---\n([\s\S]*?)\n---/);
    if (!match) return { name: '', description: '' };
    const yaml = match[1];
    const nameMatch = yaml.match(/^name:\s*(.+)$/m);
    const descMatch = yaml.match(/^description:\s*(.+)$/m);
    return {
      name: nameMatch ? nameMatch[1].trim().replace(/^["']|["']$/g, '') : '',
      description: descMatch ? descMatch[1].trim().replace(/^["']|["']$/g, '') : '',
    };
  } catch {
    return { name: '', description: '' };
  }
}

function scanSkillUsageFromSessions() {
  const homeDir = process.env.HOME || '/root';
  const sessionsDir = path.join(homeDir, '.openclaw/agents/main/sessions');
  if (!fs.existsSync(sessionsDir)) return;

  const now = Date.now();
  const todayStart = new Date(); todayStart.setHours(0, 0, 0, 0);
  const weekStart = new Date(now - 7 * 86400000);

  const usageMap = new Map<string, { today: number; week: number; total: number; lastUsed: string | null }>();

  try {
    const files = fs.readdirSync(sessionsDir)
      .filter(f => f.endsWith('.jsonl'))
      .map(f => ({ name: f, mtime: fs.statSync(path.join(sessionsDir, f)).mtimeMs }))
      .sort((a, b) => b.mtime - a.mtime)
      .slice(0, 20); // Only scan recent 20 sessions for performance

    for (const file of files) {
      try {
        const content = fs.readFileSync(path.join(sessionsDir, file.name), 'utf-8');
        // Look for SKILL.md reads - indicates skill was triggered
        const skillReads = content.match(/skills\/([^/]+)\/SKILL\.md/g) || [];
        for (const match of skillReads) {
          const skillName = match.match(/skills\/([^/]+)\/SKILL\.md/)?.[1];
          if (!skillName) continue;

          if (!usageMap.has(skillName)) {
            usageMap.set(skillName, { today: 0, week: 0, total: 0, lastUsed: null });
          }
          const usage = usageMap.get(skillName)!;
          usage.total++;

          if (file.mtime >= todayStart.getTime()) usage.today++;
          if (file.mtime >= weekStart.getTime()) usage.week++;
          if (!usage.lastUsed || file.mtime > new Date(usage.lastUsed).getTime()) {
            usage.lastUsed = new Date(file.mtime).toISOString();
          }
        }
      } catch {}
    }
  } catch {}

  skillUsageMap = usageMap;
}

// ─── LLM Stats ──────────────────────────────────────────────────
const LLM_STATS_FILE = path.join(process.env.DATA_DIR || path.join(process.env.HOME || '/root', '.openclaw-node'), 'llm-stats.json');

let llmStats = {
  requestsToday: 0,
  requestsTotal: 0,
  tokensToday: 0,
  tokensTotal: 0,
  codingMinutesToday: 0,
  codingMinutesTotal: 0,
  lastResetDate: new Date().toISOString().slice(0, 10),
};

function loadLlmStats() {
  try {
    const dir = path.dirname(LLM_STATS_FILE);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    if (fs.existsSync(LLM_STATS_FILE)) {
      const data = JSON.parse(fs.readFileSync(LLM_STATS_FILE, 'utf-8'));
      llmStats = { ...llmStats, ...data };
    }
  } catch {}
}

function saveLlmStats() {
  try {
    const dir = path.dirname(LLM_STATS_FILE);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(LLM_STATS_FILE, JSON.stringify(llmStats, null, 2));
  } catch {}
}

function checkDayReset() {
  const today = new Date().toISOString().slice(0, 10);
  if (llmStats.lastResetDate !== today) {
    llmStats.requestsToday = 0;
    llmStats.tokensToday = 0;
    llmStats.codingMinutesToday = 0;
    llmStats.lastResetDate = today;
    saveLlmStats();
  }
}

loadLlmStats();

// ─── Timers ──────────────────────────────────────────────────────
let heartbeatTimer: ReturnType<typeof setInterval> | null = null;
let taskSyncTimer: ReturnType<typeof setInterval> | null = null;
let skillSyncTimer: ReturnType<typeof setInterval> | null = null;
let reconnectTimer: ReturnType<typeof setTimeout> | null = null;

// ─── System Monitor ──────────────────────────────────────────────
function getCpuUsage(): number {
  const cpus = os.cpus();
  let totalIdle = 0, totalTick = 0;
  for (const cpu of cpus) {
    for (const type in cpu.times) totalTick += (cpu.times as any)[type];
    totalIdle += cpu.times.idle;
  }
  return Math.round((1 - totalIdle / totalTick) * 100);
}

function getMemoryUsage() {
  const total = os.totalmem();
  const free = os.freemem();
  const used = total - free;
  return {
    total: Math.round(total / 1024 / 1024 / 1024 * 100) / 100,
    used: Math.round(used / 1024 / 1024 / 1024 * 100) / 100,
    free: Math.round(free / 1024 / 1024 / 1024 * 100) / 100,
    percentage: Math.round(used / total * 100),
  };
}

function getDiskUsage() {
  try {
    const output = execSync("df -B1 / | tail -1").toString().trim();
    const parts = output.split(/\s+/);
    const total = parseInt(parts[1]);
    const used = parseInt(parts[2]);
    return {
      total: Math.round(total / 1024 / 1024 / 1024 * 100) / 100,
      used: Math.round(used / 1024 / 1024 / 1024 * 100) / 100,
      free: Math.round((total - used) / 1024 / 1024 / 1024 * 100) / 100,
      percentage: Math.round(used / total * 100),
    };
  } catch {
    return { total: 0, used: 0, free: 0, percentage: 0 };
  }
}

function getSystemInfo() {
  return {
    hostname: os.hostname(),
    platform: os.platform(),
    arch: os.arch(),
    cpuModel: os.cpus()[0]?.model || 'Unknown',
    cpuCores: os.cpus().length,
    nodeVersion: process.version,
    uptime: os.uptime(),
  };
}

// ─── Network Addresses ───────────────────────────────────────────
let cachedPublicIp: string = '';

function getNetworkAddresses(): { internal: string; interfaces: Record<string, string> } {
  const nets = os.networkInterfaces();
  let internal = '127.0.0.1';
  const interfaces: Record<string, string> = {};
  for (const [name, addrs] of Object.entries(nets)) {
    for (const addr of addrs || []) {
      if (addr.family === 'IPv4' && !addr.internal) {
        interfaces[name] = addr.address;
        if (!internal || internal === '127.0.0.1') internal = addr.address;
      }
    }
  }
  return { internal, interfaces };
}

// Fetch public IP once at startup (non-blocking)
(async () => {
  try {
    const res = await axios.get('https://api.ipify.org?format=text', { timeout: 5000 });
    cachedPublicIp = (res.data || '').trim();
  } catch { cachedPublicIp = ''; }
})();

// ─── Hub Communication ───────────────────────────────────────────
function clearTimers() {
  if (heartbeatTimer) { clearInterval(heartbeatTimer); heartbeatTimer = null; }
  if (taskSyncTimer) { clearInterval(taskSyncTimer); taskSyncTimer = null; }
  if (skillSyncTimer) { clearInterval(skillSyncTimer); skillSyncTimer = null; }
  if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null; }
  if (agentSyncTimer) { clearInterval(agentSyncTimer); agentSyncTimer = null; }
}

function startTimers() {
  clearTimers();
  heartbeatTimer = setInterval(sendHeartbeat, 10000);
  taskSyncTimer = setInterval(fetchTasks, 30000);
  skillSyncTimer = setInterval(fetchSkills, 60000);
  agentSyncTimer = setInterval(syncAgents, 60000);
}

async function syncAgents() {
  if (!nodeId || !sessionToken) return;
  try {
    const res = await axios.get(`${HUB_URL}/api/nodes/${nodeId}/agents`, {
      headers: { Authorization: `Bearer ${sessionToken}` },
      timeout: 10000,
    });
    if (res.data?.code === 0 && Array.isArray(res.data.data)) {
      syncedAgents = res.data.data;
      addLog('info', `🤖 同步 Agent 列表: ${syncedAgents.length} 个`);
    }
  } catch (err: any) {
    addLog('error', `同步 Agent 失败: ${err.message}`);
  }
}


async function registerLocalAgents() {
  if (!nodeId || !sessionToken) return;
  
  const homeDir = process.env.HOME || '/root';
  let agentName = os.hostname();
  let soulMd = '';
  let channel: string | null = null;
  let agentSkills: string[] = [];
  
  // 读取 IDENTITY.md
  const identityPath = path.join(homeDir, '.openclaw/workspace/IDENTITY.md');
  if (fs.existsSync(identityPath)) {
    const content = fs.readFileSync(identityPath, 'utf-8');
    const nameMatch = content.match(/\*\*Name:\*\*\s*(.+)/);
    if (nameMatch) agentName = nameMatch[1].trim();
  }
  
  // 读取 SOUL.md
  const soulPath = path.join(homeDir, '.openclaw/workspace/SOUL.md');
  if (fs.existsSync(soulPath)) {
    soulMd = fs.readFileSync(soulPath, 'utf-8').slice(0, 2000);
  }
  
  // 扫描技能列表
  const skillsDir = path.join(homeDir, '.openclaw/workspace/skills');
  if (fs.existsSync(skillsDir)) {
    agentSkills = fs.readdirSync(skillsDir).filter(d => 
      fs.existsSync(path.join(skillsDir, d, 'SKILL.md'))
    );
  }
  
  // 检测渠道
  try {
    const configPath = path.join(homeDir, '.openclaw/config.yaml');
    if (fs.existsSync(configPath)) {
      const cfg = fs.readFileSync(configPath, 'utf-8');
      if (cfg.includes('feishu')) channel = 'feishu';
      else if (cfg.includes('wecom')) channel = 'wecom';
      else if (cfg.includes('telegram')) channel = 'telegram';
      else if (cfg.includes('discord')) channel = 'discord';
    }
  } catch {}
  
  try {
    const res = await axios.post(`${HUB_URL}/api/nodes/${nodeId}/agents/register`, {
      name: agentName,
      role: 'worker',
      soulMd,
      channel,
      capabilities: ['reasoning', 'coding', 'writing'],
      skills: agentSkills,
    }, {
      headers: { Authorization: `Bearer ${sessionToken}` },
      timeout: 10000,
    });
    
    if (res.data?.code === 0) {
      addLog('success', `Agent "${agentName}" 已注册到 Hub`);
    }
  } catch (err: any) {
    addLog('error', `Agent 注册失败: ${err.message}`);
  }
}

async function registerLocalSkills() {
  if (!nodeId || !sessionToken) return;
  
  // 上报本地技能到 Hub
  for (const skill of localSkills) {
    try {
      await axios.post(`${HUB_URL}/api/nodes/${nodeId}/skills/register`, {
        name: skill.name,
        description: skill.description,
        type: skill.type,
        usageToday: skill.usageToday,
        usage7d: skill.usage7d,
        usageTotal: skill.usageTotal,
      }, {
        headers: { Authorization: `Bearer ${sessionToken}` },
        timeout: 5000,
      });
    } catch {}
  }
  
  addLog('info', `已上报 ${localSkills.length} 个技能到 Hub`);
}

async function registerWithHub(): Promise<boolean> {
  if (!HUB_URL || !APP_ID || !APP_KEY || !APP_TOKEN) {
    addLog('warning', '未配置 HUB_URL / APP_ID / APP_KEY / APP_TOKEN，跳过连接');
    addLog('info', '请先在 Hub 管理后台创建节点，获取凭证后配置到 .env 文件');
    return false;
  }

  connecting = true;
  connectionError = '';
  addLog('info', `正在连接 Hub: ${HUB_URL}（仅验证凭证，不会自动创建节点）`);

  try {
    const res = await axios.post(`${HUB_URL}/api/nodes/register`, {
      appId: APP_ID,
      key: APP_KEY,
      token: APP_TOKEN,
      // 只传认证信息，不传 name/hostname 等，防止覆盖 Hub 上的配置
      hostname: os.hostname(),
      port: NODE_PORT,
      platform: os.platform(),
      arch: os.arch(),
      capabilities: ['task-execution', 'monitoring'],
    }, { timeout: 10000 });

    if (res.data?.code === 0 && res.data?.data) {
      nodeId = res.data.data.nodeId;
      sessionToken = res.data.data.sessionToken;
      connected = true;
      connecting = false;
      registeredAt = new Date().toISOString();
      addLog('success', `连接成功! nodeId=${nodeId}, name=${res.data.data.name || nodeId}`);
      reconnectAttempts = 0; // 重置退避计数
      await registerLocalAgents();
      await registerLocalSkills();
      startTimers();
      await fetchTasks();
      await fetchSkills();
      await syncAgents();
      return true;
    } else {
      throw new Error(res.data?.message || '连接返回异常');
    }
  } catch (err: any) {
    const msg = err.response?.data?.message || err.message;
    connectionError = msg;
    connected = false;
    connecting = false;
    
    // 如果是 403，不管什么原因都停止重试（凭证问题需要人工修复）
    if (err.response?.status === 403) {
      addLog('error', `连接被拒绝 (403): ${msg}`);
      addLog('info', '请检查 APP_ID/APP_KEY/APP_TOKEN 是否正确，或在 Hub 管理后台确认节点已创建');
      return false;
    }
    
    addLog('error', `连接失败: ${msg}，将自动重试...`);
    scheduleReconnect();
    return false;
  }
}

let reconnectAttempts = 0;

function scheduleReconnect() {
  if (reconnectTimer) return;
  // 指数退避: 30s → 60s → 120s → 240s → 300s (上限5分钟)
  const delay = Math.min(30000 * Math.pow(2, reconnectAttempts), 300000);
  reconnectAttempts++;
  addLog('info', `将在 ${Math.round(delay / 1000)} 秒后重试连接 (第 ${reconnectAttempts} 次)...`);
  reconnectTimer = setTimeout(async () => {
    reconnectTimer = null;
    await registerWithHub();
  }, delay);
}

async function sendHeartbeat() {
  if (!nodeId || !connected) return;
  // 每日重置 LLM 统计
  checkDayReset();
  try {
    // 收集本地记忆（新增的）
    const newMemories = getUnsentMemories();
    
    // 收集正在执行的任务状态
    const runningTaskStatuses = Array.from(executingTasks).map(taskId => {
      const local = localTasks.get(taskId);
      return local ? { id: taskId, status: local.status || 'running', progress: local.progress || 0, title: local.title || '' } : { id: taskId, status: 'running', progress: 0 };
    });

    // 获取网络地址
    const addresses = getNetworkAddresses();

    await axios.post(`${HUB_URL}/api/nodes/${nodeId}/heartbeat`, {
      cpu: getCpuUsage(),
      memory: getMemoryUsage(),
      disk: getDiskUsage(),
      uptime: os.uptime(),
      timestamp: new Date().toISOString(),
      // 网络地址
      internalIp: addresses.internal,
      publicIp: cachedPublicIp,
      port: NODE_PORT,
      adminUrl: `http://${addresses.internal}:${NODE_PORT}`,
      publicAdminUrl: cachedPublicIp ? `http://${cachedPublicIp}:${NODE_PORT}` : '',
      // 同步记忆
      memories: newMemories,
      // 同步正在执行的任务
      runningTasks: runningTaskStatuses,
      // LLM 统计
      llmStats: llmStats,
    }, {
      headers: { Authorization: `Bearer ${sessionToken}` },
      timeout: 10000,
    });
    lastHeartbeat = new Date().toISOString();
    connected = true;
    
    // 标记记忆已发送
    if (newMemories.length > 0) {
      markMemoriesSent(newMemories);
      addLog('info', `📤 同步 ${newMemories.length} 条记忆到 Hub`);
    }
  } catch (err: any) {
    addLog('error', `心跳失败: ${err.message}`);
    connected = false;
    clearTimers();
    scheduleReconnect();
  }
}

// ─── 本地记忆管理 ───
const MEMORIES_FILE = path.join(process.env.DATA_DIR || path.join(process.env.HOME || '/root', '.openclaw-node'), 'memories.json');
const SENT_MEMORY_IDS_FILE = path.join(process.env.DATA_DIR || path.join(process.env.HOME || '/root', '.openclaw-node'), 'sent-memory-ids.json');

interface LocalMemory {
  id: string;
  type: 'stm' | 'mtm' | 'ltm';
  content: string;
  source: string;
  agentId?: string;
  importance: number;
  tags: string[];
  createdAt: string;
}

// 初始化时加载（pendingMemories 用于心跳上报，evoMemories Map 用于 API 查询）
let pendingMemories: LocalMemory[] = [];
let sentMemoryIds = new Set<string>();
loadLocalMemories();

function loadLocalMemories() {
  try {
    const dir = path.dirname(MEMORIES_FILE);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    if (fs.existsSync(MEMORIES_FILE)) {
      pendingMemories = JSON.parse(fs.readFileSync(MEMORIES_FILE, 'utf-8'));
      if (!Array.isArray(pendingMemories)) pendingMemories = [];
    }
    if (fs.existsSync(SENT_MEMORY_IDS_FILE)) {
      sentMemoryIds = new Set(JSON.parse(fs.readFileSync(SENT_MEMORY_IDS_FILE, 'utf-8')));
    }
  } catch {}
}

function saveLocalMemories() {
  try {
    const dir = path.dirname(MEMORIES_FILE);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(MEMORIES_FILE, JSON.stringify(pendingMemories, null, 2));
    fs.writeFileSync(SENT_MEMORY_IDS_FILE, JSON.stringify([...sentMemoryIds]));
  } catch {}
}

function addLocalMemory(content: string, type: 'stm' | 'mtm' | 'ltm' = 'stm', agentId?: string, tags: string[] = []) {
  const mem: LocalMemory = {
    id: `mem-local-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
    type,
    content,
    source: `node:${nodeId}`,
    agentId: agentId || '',
    importance: type === 'ltm' ? 8 : type === 'mtm' ? 5 : 3,
    tags,
    createdAt: new Date().toISOString(),
  };
  evoMemories.set(mem.id, { id: mem.id, type: mem.type, content: mem.content, source: mem.source, importance: mem.importance, tags: mem.tags, createdAt: mem.createdAt, updatedAt: mem.createdAt });
  pendingMemories.push(mem);
  saveLocalMemories();
  return mem;
}

function getUnsentMemories(): LocalMemory[] {
  return pendingMemories.filter(m => !sentMemoryIds.has(m.id));
}

function markMemoriesSent(memories: LocalMemory[]) {
  for (const m of memories) sentMemoryIds.add(m.id);
  saveLocalMemories();
}

// 初始化时加载
loadLocalMemories();

// ─── 命令白名单：只允许执行这些前缀的命令 ───
const ALLOWED_COMMANDS = [
  'clawhub install',
  'clawhub update',
  'clawhub uninstall',
  'openclaw',
  'npm install',
  'npx tsx',
];

function isCommandAllowed(cmd: string): boolean {
  const trimmed = cmd.trim();
  return ALLOWED_COMMANDS.some(prefix => trimmed.startsWith(prefix));
}

const executingTasks = new Set<string>();

async function fetchTasks() {
  if (!nodeId || !sessionToken) return;
  try {
    const res = await axios.get(`${HUB_URL}/api/nodes/${nodeId}/tasks`, {
      headers: { Authorization: `Bearer ${sessionToken}` },
      timeout: 10000,
    });
    if (res.data?.code === 0 && Array.isArray(res.data.data)) {
      syncedTasks = res.data.data;
      
      for (const task of syncedTasks) {
        if (task.status === 'pending' || task.status === 'assigned') {
          if (executingTasks.has(task.id)) continue;

          // 全量记忆收集任务
          if (task.userInput === '__COLLECT_ALL_MEMORIES__') {
            collectAndUploadAllMemories(task);
            continue;
          }
          
          const category = task.taskCategory || 'short';
          
          if (category === 'scheduled') {
            // 定时任务 → 注册定时调度
            scheduleRecurringTask(task);
          } else if (task.userInput && isCommandAllowed(task.userInput)) {
            // 命令型任务
            executeCommandTask(task);
          } else {
            // 通用协作任务（短期/长期）→ 用大模型执行
            executeAgentTask(task);
          }
        }
      }
    }
  } catch (err: any) {
    addLog('error', `拉取任务失败: ${err.message}`);
  }
}

async function collectAndUploadAllMemories(task: any) {
  if (executingTasks.has(task.id)) return;
  executingTasks.add(task.id);

  addLog('info', '📦 开始全量记忆收集...');

  // 标记 running
  try {
    await axios.post(`${HUB_URL}/api/tasks/${task.id}/start`, { nodeId }, {
      headers: { Authorization: `Bearer ${sessionToken}` },
      timeout: 5000,
    });
  } catch {}

  const allMemories: any[] = [];
  const WORKSPACE = process.env.OPENCLAW_WORKSPACE || path.join(process.env.HOME || '/root', '.openclaw', 'workspace');

  await reportProgress(task.id, 10, '扫描工作区...');

  // 1. 扫描 MEMORY.md（长期记忆）
  try {
    const memoryMdPath = path.join(WORKSPACE, 'MEMORY.md');
    if (fs.existsSync(memoryMdPath)) {
      const content = fs.readFileSync(memoryMdPath, 'utf-8');
      const sections = content.split(/^## /m).filter((s: string) => s.trim());
      for (const section of sections) {
        const title = section.split('\n')[0].trim();
        allMemories.push({
          type: 'ltm',
          content: `## ${section.trim()}`,
          tags: ['MEMORY.md', title.slice(0, 30)],
          createdAt: new Date().toISOString(),
        });
      }
      addLog('info', `📄 MEMORY.md: ${sections.length} 条长期记忆`);
    }
  } catch (err: any) {
    addLog('warning', `读取 MEMORY.md 失败: ${err.message}`);
  }

  await reportProgress(task.id, 30, `已收集 ${allMemories.length} 条...`);

  // 2. 扫描 memory/*.md（日志记忆）
  try {
    const memoryDir = path.join(WORKSPACE, 'memory');
    if (fs.existsSync(memoryDir)) {
      const files = fs.readdirSync(memoryDir).filter((f: string) => f.endsWith('.md'));
      for (const file of files) {
        const filePath = path.join(memoryDir, file);
        const content = fs.readFileSync(filePath, 'utf-8');
        const isDateFile = /^\d{4}-\d{2}-\d{2}/.test(file);
        const sections = content.split(/^## /m).filter((s: string) => s.trim());

        for (const section of sections) {
          allMemories.push({
            type: isDateFile ? 'stm' : 'mtm',
            content: `## ${section.trim()}`,
            tags: [file.replace('.md', ''), 'memory-dir'],
            createdAt: isDateFile ? new Date(file.replace('.md', '')).toISOString() : new Date().toISOString(),
          });
        }
      }
      addLog('info', `📁 memory/ 目录: ${files.length} 个文件`);
    }
  } catch (err: any) {
    addLog('warning', `扫描 memory/ 失败: ${err.message}`);
  }

  await reportProgress(task.id, 50, `已收集 ${allMemories.length} 条...`);

  // 3. 扫描 SOUL.md, USER.md, TOOLS.md, IDENTITY.md 等重要文件
  const importantFiles = ['SOUL.md', 'USER.md', 'TOOLS.md', 'IDENTITY.md', 'AGENTS.md', 'HEARTBEAT.md'];
  for (const fileName of importantFiles) {
    try {
      const filePath = path.join(WORKSPACE, fileName);
      if (fs.existsSync(filePath)) {
        const content = fs.readFileSync(filePath, 'utf-8');
        if (content.trim()) {
          allMemories.push({
            type: 'ltm',
            content: `[${fileName}]\n${content.slice(0, 5000)}`,
            tags: [fileName, 'workspace-config'],
            createdAt: new Date(fs.statSync(filePath).mtime).toISOString(),
          });
        }
      }
    } catch {}
  }

  await reportProgress(task.id, 60, `已收集 ${allMemories.length} 条，扫描会话...`);

  // 4. 扫描 sessions 目录（会话历史摘要）
  try {
    const sessionsDir = path.join(process.env.HOME || '/root', '.openclaw', 'sessions');
    if (fs.existsSync(sessionsDir)) {
      const sessionFiles = fs.readdirSync(sessionsDir).filter((f: string) => f.endsWith('.json') || f.endsWith('.jsonl'));
      let sessionCount = 0;
      for (const file of sessionFiles.slice(-50)) { // 最近 50 个会话
        try {
          const filePath = path.join(sessionsDir, file);
          const stat = fs.statSync(filePath);
          if (stat.size > 500000) continue; // 跳过超大文件

          const content = fs.readFileSync(filePath, 'utf-8');
          // 提取摘要（前 2000 字符）
          const summary = content.slice(0, 2000);
          allMemories.push({
            type: 'stm',
            content: `[会话 ${file}]\n${summary}`,
            tags: ['session', file.replace(/\.(json|jsonl)$/, '')],
            createdAt: new Date(stat.mtime).toISOString(),
          });
          sessionCount++;
        } catch {}
      }
      addLog('info', `💬 sessions/ 目录: ${sessionCount} 个会话`);
    }
  } catch (err: any) {
    addLog('warning', `扫描 sessions/ 失败: ${err.message}`);
  }

  await reportProgress(task.id, 80, `共收集 ${allMemories.length} 条，开始上传...`);

  // 5. 批量上报到 Hub（分批，每批 50 条）
  let totalImported = 0;
  let totalSkipped = 0;
  const BATCH_SIZE = 50;

  for (let i = 0; i < allMemories.length; i += BATCH_SIZE) {
    const batch = allMemories.slice(i, i + BATCH_SIZE);
    try {
      const res = await axios.post(`${HUB_URL}/api/nodes/${nodeId}/memories/bulk`, {
        memories: batch,
      }, {
        headers: { Authorization: `Bearer ${sessionToken}` },
        timeout: 30000,
      });
      if (res.data?.code === 0) {
        totalImported += res.data.data?.imported || 0;
        totalSkipped += res.data.data?.skipped || 0;
      }
    } catch (err: any) {
      addLog('error', `批量上传失败 (batch ${Math.floor(i / BATCH_SIZE) + 1}): ${err.message}`);
    }

    const progress = 80 + Math.round((i / allMemories.length) * 20);
    await reportProgress(task.id, progress, `上传中 ${i + batch.length}/${allMemories.length}...`);
  }

  addLog('success', `📦 全量收集完成: 共 ${allMemories.length} 条, 导入 ${totalImported}, 跳过 ${totalSkipped}`);

  // 标记完成
  try {
    await axios.post(`${HUB_URL}/api/tasks/${task.id}/complete`, {
      nodeId,
      result: {
        output: `收集完成: ${allMemories.length} 条记忆 (导入 ${totalImported}, 跳过重复 ${totalSkipped})`,
        success: true,
        stats: { total: allMemories.length, imported: totalImported, skipped: totalSkipped },
      },
    }, {
      headers: { Authorization: `Bearer ${sessionToken}` },
      timeout: 5000,
    });
  } catch {}

  executingTasks.delete(task.id);
}

async function executeCommandTask(task: any) {
  if (executingTasks.has(task.id)) return;
  executingTasks.add(task.id);

  const cmd = task.userInput?.trim();
  
  // 二次安全校验
  if (!cmd || !isCommandAllowed(cmd)) {
    addLog('warning', `拒绝执行不安全命令: ${cmd}`);
    executingTasks.delete(task.id);
    try {
      await axios.post(`${HUB_URL}/api/tasks/${task.id}/fail`, {
        nodeId,
        result: { error: `命令不在白名单中: ${cmd}` },
      }, { headers: { Authorization: `Bearer ${sessionToken}` }, timeout: 5000 });
    } catch {}
    return;
  }

  addLog('info', `开始执行任务: ${task.title} (${task.id})`);

  // 标记 running
  try {
    await axios.post(`${HUB_URL}/api/tasks/${task.id}/start`, { nodeId }, {
      headers: { Authorization: `Bearer ${sessionToken}` },
      timeout: 5000,
    });
  } catch {}

  // 异步执行命令（不阻塞事件循环）
  const parts = cmd.split(/\s+/);
  const command = parts[0];
  const args = parts.slice(1);
  const homeDir = process.env.HOME || '/root';

  const child = spawn(command, args, {
    cwd: homeDir,
    env: { ...process.env, PATH: (process.env.PATH || '') + ':/usr/local/bin:/root/.local/share/pnpm:/opt/homebrew/bin' },
    shell: true,
    timeout: 300000, // 5 分钟超时
  });

  let stdout = '';
  let stderr = '';

  child.stdout?.on('data', (data: Buffer) => {
    const chunk = data.toString();
    stdout += chunk;
    // 保留最后 2000 字符
    if (stdout.length > 2000) stdout = stdout.slice(-2000);
  });

  child.stderr?.on('data', (data: Buffer) => {
    const chunk = data.toString();
    stderr += chunk;
    if (stderr.length > 2000) stderr = stderr.slice(-2000);
  });

  child.on('close', async (code: number | null) => {
    executingTasks.delete(task.id);
    
    if (code === 0) {
      addLog('success', `任务完成: ${task.title}`);
      addLocalMemory(`命令任务完成: ${task.title}\n命令: ${cmd}\n输出: ${stdout.slice(0, 200)}`, 'stm', undefined, ['command-task', task.id]);
      try {
        await axios.post(`${HUB_URL}/api/tasks/${task.id}/complete`, {
          nodeId,
          result: { output: stdout.slice(-500) || 'done', success: true },
        }, { headers: { Authorization: `Bearer ${sessionToken}` }, timeout: 5000 });
      } catch {}
    } else {
      addLog('error', `任务失败 (exit ${code}): ${task.title}`);
      try {
        await axios.post(`${HUB_URL}/api/tasks/${task.id}/fail`, {
          nodeId,
          result: { error: `exit code ${code}`, stderr: stderr.slice(-500), stdout: stdout.slice(-500) },
        }, { headers: { Authorization: `Bearer ${sessionToken}` }, timeout: 5000 });
      } catch {}
    }
  });

  child.on('error', async (err: Error) => {
    executingTasks.delete(task.id);
    addLog('error', `任务执行异常: ${task.title} - ${err.message}`);
    try {
      await axios.post(`${HUB_URL}/api/tasks/${task.id}/fail`, {
        nodeId,
        result: { error: err.message },
      }, { headers: { Authorization: `Bearer ${sessionToken}` }, timeout: 5000 });
    } catch {}
  });
}

// ─── 定时任务调度 ───
const scheduledTasks = new Map<string, NodeJS.Timeout>();
const SCHEDULED_STATE_FILE = path.join(process.env.DATA_DIR || path.join(process.env.HOME || '/root', '.openclaw-node'), 'scheduled-tasks.json');

function scheduleRecurringTask(task: any) {
  if (scheduledTasks.has(task.id)) return; // 已注册
  
  // 解析执行间隔（从描述中提取，默认 1 小时）
  const desc = (task.description || task.title || '').toLowerCase();
  let intervalMs = 3600000; // 默认 1 小时
  if (/每\s*(\d+)\s*分钟|every\s*(\d+)\s*min/i.test(desc)) {
    const m = desc.match(/每\s*(\d+)\s*分钟|every\s*(\d+)\s*min/i);
    intervalMs = parseInt(m![1] || m![2]) * 60000;
  } else if (/每\s*(\d+)\s*小时|every\s*(\d+)\s*hour/i.test(desc)) {
    const m = desc.match(/每\s*(\d+)\s*小时|every\s*(\d+)\s*hour/i);
    intervalMs = parseInt(m![1] || m![2]) * 3600000;
  } else if (/每天|daily|every\s*day/i.test(desc)) {
    intervalMs = 86400000;
  } else if (/每周|weekly/i.test(desc)) {
    intervalMs = 604800000;
  }
  
  addLog('info', `⏰ 注册定时任务: ${task.title} (间隔 ${Math.round(intervalMs / 60000)} 分钟)`);
  
  // 标记为 running
  axios.post(`${HUB_URL}/api/tasks/${task.id}/start`, { nodeId }, {
    headers: { Authorization: `Bearer ${sessionToken}` },
    timeout: 5000,
  }).catch(() => {});
  
  // 立即执行一次
  executeScheduledRun(task);
  
  // 设置定时器
  const timer = setInterval(() => {
    executeScheduledRun(task);
  }, intervalMs);
  
  scheduledTasks.set(task.id, timer);
  
  // 持久化
  saveScheduledState();
}

async function executeScheduledRun(task: any) {
  const runId = `run-${Date.now()}`;
  addLog('info', `⏰ 定时执行: ${task.title} (${runId})`);
  
  try {
    if (task.userInput && isCommandAllowed(task.userInput)) {
      // 命令型
      const { execSync: es } = require('child_process');
      const output = es(task.userInput, {
        cwd: process.env.HOME || '/root',
        timeout: 120000,
        encoding: 'utf-8',
        env: { ...process.env, PATH: (process.env.PATH || '') + ':/usr/local/bin:/root/.local/share/pnpm:/opt/homebrew/bin' },
      });
      await reportProgress(task.id, 100, `⏰ 定时执行成功 (${runId}): ${(output || '').slice(0, 200)}`);
    } else {
      // 大模型型 — 简化版，不重复完整 executeAgentTask
      await reportProgress(task.id, 50, `⏰ 定时执行中 (${runId})...`);
      // TODO: 调用大模型执行
      await reportProgress(task.id, 100, `⏰ 定时执行完成 (${runId})`);
    }
    
    addLocalMemory(`定时任务执行: ${task.title} (${runId})`, 'stm', task.assigneeAgentId, ['scheduled', task.id]);
  } catch (err: any) {
    addLog('error', `⏰ 定时执行失败: ${task.title} - ${err.message}`);
    await reportProgress(task.id, -1, `⏰ 定时执行失败 (${runId}): ${err.message}`);
  }
}

function saveScheduledState() {
  try {
    const state = Array.from(scheduledTasks.keys());
    const dir = path.dirname(SCHEDULED_STATE_FILE);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(SCHEDULED_STATE_FILE, JSON.stringify(state));
  } catch {}
}

async function executeAgentTask(task: any) {
  if (executingTasks.has(task.id)) return;
  executingTasks.add(task.id);
  
  const agentId = task.assigneeAgentId;
  addLog('info', `🤖 接收协作任务: ${task.title} (Agent: ${task.assigneeAgentName || agentId})`);
  
  // 标记 running + 上报进度 10%
  try {
    await axios.post(`${HUB_URL}/api/tasks/${task.id}/start`, { nodeId }, {
      headers: { Authorization: `Bearer ${sessionToken}` },
      timeout: 5000,
    });
    await reportProgress(task.id, 10, '任务已接收，开始执行...');
  } catch {}
  
  // 获取 Agent 的模型配置（通过专用 API）
  let modelConfig: any = null;
  try {
    const modelRes = await axios.get(`${HUB_URL}/api/nodes/${nodeId}/agent-model-config`, {
      params: { agentId },
      headers: { Authorization: `Bearer ${sessionToken}` },
      timeout: 5000,
    });
    if (modelRes.data?.code === 0) {
      modelConfig = modelRes.data.data;
    }
  } catch (err: any) {
    addLog('warning', `获取模型配置失败: ${err.message}`);
  }
  
  if (!modelConfig) {
    // 没有模型配置，标记失败
    addLog('error', `任务执行失败: Agent ${task.assigneeAgentName} 未配置大模型`);
    await reportTaskFailed(task.id, 'Agent 未配置大模型，无法执行任务');
    executingTasks.delete(task.id);
    // 更新本地任务状态
    localTasks.set(task.id, { ...task, status: 'failed', updatedAt: new Date().toISOString(), result: { error: 'Agent 未配置大模型' } });
    saveLocalTasks();
    return;
  }
  
  await reportProgress(task.id, 20, '模型配置已获取，准备调用大模型...');
  
  // 构建 prompt
  const systemPrompt = `你是 ${task.assigneeAgentName || 'AI Agent'}，正在执行一个分配给你的任务。
请认真完成任务，输出具体的执行结果。
如果任务需要写代码，请输出完整代码。
如果任务需要分析，请输出详细分析报告。
如果任务需要创作，请输出完整的创作内容。`;

  const userPrompt = `## 任务
${task.title}

${task.description ? `## 详细描述\n${task.description}` : ''}

请完成以上任务，输出具体的执行结果。`;

  await reportProgress(task.id, 30, '正在调用大模型执行任务...');
  
  // 调用大模型
  try {
    const llmRes = await axios.post(`${modelConfig.baseUrl}/chat/completions`, {
      model: modelConfig.modelId,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt },
      ],
      temperature: 0.3,
      max_tokens: 4096,
    }, {
      headers: {
        'Authorization': `Bearer ${modelConfig.apiKey}`,
        'Content-Type': 'application/json',
      },
      timeout: 120000, // 2分钟
    });
    
    const result = llmRes.data?.choices?.[0]?.message?.content || '';
    
    // 记录 LLM 统计
    llmStats.requestsToday++;
    llmStats.requestsTotal++;
    if (llmRes.data?.usage) {
      llmStats.tokensToday += (llmRes.data.usage.total_tokens || 0);
      llmStats.tokensTotal += (llmRes.data.usage.total_tokens || 0);
    }
    saveLlmStats();
    
    await reportProgress(task.id, 90, '大模型执行完成，上报结果...');
    
    addLog('success', `✅ 任务完成: ${task.title}`);
    
    // 创建记忆：记录任务执行结果
    addLocalMemory(
      `任务完成: ${task.title}\n结果摘要: ${result.slice(0, 200)}`,
      'stm',
      task.assigneeAgentId,
      ['task-result', task.id]
    );
    
    // 上报完成
    try {
      await axios.post(`${HUB_URL}/api/tasks/${task.id}/complete`, {
        nodeId,
        result: { output: result, success: true },
      }, {
        headers: { Authorization: `Bearer ${sessionToken}` },
        timeout: 10000,
      });
    } catch {}
    
    // 更新本地任务状态
    localTasks.set(task.id, { ...task, status: 'completed', updatedAt: new Date().toISOString(), completedAt: new Date().toISOString(), result: { output: result, success: true } });
    saveLocalTasks();
    
  } catch (err: any) {
    const errMsg = err.response?.data?.error?.message || err.message;
    addLog('error', `❌ 任务执行失败: ${task.title} - ${errMsg}`);
    await reportTaskFailed(task.id, errMsg);
    
    // 更新本地任务状态
    localTasks.set(task.id, { ...task, status: 'failed', updatedAt: new Date().toISOString(), result: { error: errMsg, success: false } });
    saveLocalTasks();
  }
  
  executingTasks.delete(task.id);
}

async function reportProgress(taskId: string, progress: number, log: string) {
  try {
    await axios.post(`${HUB_URL}/api/tasks/${taskId}/progress`, {
      progress,
      log,
    }, {
      headers: { Authorization: `Bearer ${sessionToken}` },
      timeout: 5000,
    });
  } catch {}
}

async function reportTaskFailed(taskId: string, error: string) {
  try {
    await axios.post(`${HUB_URL}/api/tasks/${taskId}/fail`, {
      nodeId,
      result: { error, success: false },
    }, {
      headers: { Authorization: `Bearer ${sessionToken}` },
      timeout: 5000,
    });
  } catch {}
}

async function fetchSkills() {
  if (!sessionToken) return;
  try {
    const res = await axios.get(`${HUB_URL}/api/nodes/${nodeId}/skills`, {
      headers: { Authorization: `Bearer ${sessionToken}` },
      timeout: 10000,
    });
    if (res.data?.code === 0 && Array.isArray(res.data.data)) {
      syncedSkills = res.data.data;
    }
  } catch (err: any) {
    addLog('error', `拉取技能失败: ${err.message}`);
  }
}

async function reportTaskAction(taskId: string, action: 'start' | 'complete' | 'fail', body?: any) {
  if (!sessionToken) throw new Error('未连接到 Hub');
  const res = await axios.post(`${HUB_URL}/api/tasks/${taskId}/${action}`, body || {}, {
    headers: { Authorization: `Bearer ${sessionToken}` },
    timeout: 10000,
  });
  if (res.data?.code === 0) {
    await fetchTasks();
    return res.data;
  }
  throw new Error(res.data?.message || '操作失败');
}

// ─── Register Node API routes on a Fastify instance ──────────────
// This function registers all Node routes. Can be called on:
//   - The Hub's app with prefix '/node' (embedded mode)
//   - A standalone Fastify instance (standalone mode)
export function registerNodeRoutes(app: FastifyInstance) {

  // ═══ LOCAL READ/WRITE APIs ═══

  app.get('/api/status', async () => {
    const mem = getMemoryUsage();
    const disk = getDiskUsage();
    return {
      code: 0,
      data: {
        nodeId,
        nodeName: os.hostname(),
        hubUrl: HUB_URL,
        appId: APP_ID,
        hubConnected: connected,
        connecting,
        connectionError,
        lastHeartbeat,
        registeredAt,
        system: { cpu: getCpuUsage(), memory: mem.percentage, disk: disk.percentage, uptime: os.uptime() },
        tasks: {
          pending: syncedTasks.filter(t => t.status === 'pending').length,
          running: syncedTasks.filter(t => t.status === 'running').length,
          completed: syncedTasks.filter(t => t.status === 'completed').length,
          failed: syncedTasks.filter(t => t.status === 'failed').length,
        },
      }
    };
  });

  app.get('/api/monitor', async () => {
    return {
      code: 0,
      data: {
        cpu: getCpuUsage(),
        memory: getMemoryUsage(),
        disk: getDiskUsage(),
        system: getSystemInfo(),
        uptime: os.uptime(),
        timestamp: new Date().toISOString(),
      }
    };
  });

  // Memory (local CRUD)
  app.get('/api/memory', async (req) => {
    const { type, search } = req.query as any;
    let list = Array.from(evoMemories.values());
    if (type) list = list.filter(m => m.type === type);
    if (search) {
      const q = search.toLowerCase();
      list = list.filter(m => m.content.toLowerCase().includes(q) || m.tags.some((t: string) => t.toLowerCase().includes(q)));
    }
    list.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
    return { code: 0, data: list, total: list.length };
  });

  app.post('/api/memory', async (req) => {
    const { type, content, source, importance, tags } = req.body as any;
    if (!content) return { code: 400, message: '内容不能为空' };
    const id = `mem-${Date.now()}`;
    const memory: Memory = {
      id, type: type || 'stm', content, source: source || 'manual',
      importance: importance || 5, tags: tags || [],
      createdAt: new Date().toISOString(), updatedAt: new Date().toISOString(),
    };
    evoMemories.set(id, memory);
    saveMemoryToJsonl(memory); // Persist to OpenClaw memory file
    return { code: 0, message: '记忆创建成功', data: memory };
  });

  app.put('/api/memory/:id', async (req) => {
    const id = (req.params as any).id;
    const memory = evoMemories.get(id);
    if (!memory) return { code: 404, message: '记忆不存在' };
    const { type, content, importance, tags } = req.body as any;
    if (type) memory.type = type;
    if (content) memory.content = content;
    if (importance !== undefined) memory.importance = importance;
    if (tags) memory.tags = tags;
    memory.updatedAt = new Date().toISOString();
    return { code: 0, message: '记忆更新成功', data: memory };
  });

  app.delete('/api/memory/:id', async (req) => {
    const id = (req.params as any).id;
    if (!evoMemories.has(id)) return { code: 404, message: '记忆不存在' };
    evoMemories.delete(id);
    return { code: 0, message: '记忆删除成功' };
  });


  // ═══ AGENT APIs ═══
  
  app.get('/api/agents', async () => {
    // Return locally synced agents (updated every 60s), fallback to direct Hub call
    if (syncedAgents.length > 0) {
      return { code: 0, data: syncedAgents, total: syncedAgents.length };
    }
    if (!sessionToken || !nodeId) return { code: 503, message: '未连接到 Hub' };
    try {
      const res = await axios.get(`${HUB_URL}/api/nodes/${nodeId}/agents`, {
        headers: { Authorization: `Bearer ${sessionToken}` },
        timeout: 10000,
      });
      return res.data;
    } catch (err: any) {
      return { code: 500, message: err.message };
    }
  });

  app.post('/api/agents', async (req) => {
    const { name, role, soulMd, capabilities, skills } = req.body as any;
    if (!name) return { code: 400, message: 'Agent 名称不能为空' };
    
    if (sessionToken && nodeId) {
      try {
        const res = await axios.post(`${HUB_URL}/api/nodes/${nodeId}/agents/register`, {
          name, role, soulMd, capabilities, skills,
        }, {
          headers: { Authorization: `Bearer ${sessionToken}` },
          timeout: 10000,
        });
        return res.data;
      } catch (err: any) {
        return { code: 500, message: err.message };
      }
    }
    return { code: 503, message: '未连接到 Hub' };
  });

  // ═══ HUB-SYNCED READ-ONLY APIs ═══

  app.get('/api/tasks', async () => {
    // 合并 Hub 同步的任务和本地创建的任务
    const allTasks = [...syncedTasks, ...Array.from(localTasks.values())];
    return { code: 0, data: allTasks, total: allTasks.length };
  });

  app.post('/api/tasks', async (req) => {
    const { title, description, priority, userInput, channel, peerId } = req.body as any;
    if (!title) return { code: 400, message: '任务标题不能为空' };

    // 支持多渠道：feishu, wecom, dingtalk, qqbot, telegram, discord, whatsapp, webchat, etc.
    const supportedChannels = ['feishu', 'wecom', 'dingtalk', 'qqbot', 'telegram', 'discord', 'whatsapp', 'signal', 'webchat', 'wechat', 'openclaw-weixin', 'yuanbao', 'adp-openclaw', 'other'];
    const taskChannel = channel || 'other';
    
    const task = {
      id: `local-task-${Date.now()}`,
      title,
      description: description || '',
      status: 'pending',
      priority: priority || 'medium',
      assigneeId: null,
      nodeId: nodeId || 'local',
      sourceNodeId: nodeId,
      createdBy: 'local',
      channel: supportedChannels.includes(taskChannel) ? taskChannel : 'other',
      peerId: peerId || null,  // 消息发送者 ID
      userInput: userInput || title,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      completedAt: null,
      result: null,
    };

    localTasks.set(task.id, task);
    saveLocalTasks();  // 持久化
    // 异步上报到 Hub
    if (nodeId && sessionToken) {
      axios.post(`${HUB_URL}/api/tasks`, task, {
        headers: { Authorization: `Bearer ${sessionToken}` },
        timeout: 5000,
      }).catch(err => addLog('warning', `上报任务到 Hub 失败: ${err.message}`));
    }

    return { code: 0, message: '任务创建成功', data: task };
  });

  app.post('/api/tasks/:id/start', async (req) => {
    try {
      const result = await reportTaskAction((req.params as any).id, 'start', { nodeId });
      return { code: 0, message: '任务已开始', data: result.data };
    } catch (err: any) {
      return { code: 500, message: err.message };
    }
  });

  app.post('/api/tasks/:id/complete', async (req) => {
    try {
      const result = await reportTaskAction((req.params as any).id, 'complete', (req.body as any) || {});
      return { code: 0, message: '任务已完成', data: result.data };
    } catch (err: any) {
      return { code: 500, message: err.message };
    }
  });

  app.post('/api/tasks/:id/fail', async (req) => {
    try {
      const result = await reportTaskAction((req.params as any).id, 'fail', { error: (req.body as any)?.error || '手动标记失败' });
      return { code: 0, message: '任务已标记失败', data: result.data };
    } catch (err: any) {
      return { code: 500, message: err.message };
    }
  });

  // --- Skills (local OpenClaw skills, not from Hub) ---
  app.get('/api/skills', async () => {
    return { code: 0, data: localSkills, total: localSkills.length };
  });

  // Refresh skills scan on demand
  app.post('/api/skills/refresh', async () => {
    scanSkillUsageFromSessions();
    scanLocalSkills();
    return { code: 0, message: '技能列表已刷新', data: localSkills, total: localSkills.length };
  });

  // ═══ CONNECTION MANAGEMENT ═══

  app.get('/api/connection', async () => {
    return {
      code: 0,
      data: {
        hubUrl: HUB_URL,
        appId: APP_ID,
        nodeId,
        sessionToken: sessionToken ? '****' : '',
        connected,
        connecting,
        connectionError,
        lastHeartbeat,
        registeredAt,
        logs: connectionLogs.slice(0, 50),
      }
    };
  });

  app.post('/api/connection/reconnect', async () => {
    clearTimers();
    connected = false;
    connecting = false;
    nodeId = '';
    sessionToken = '';
    addLog('info', '手动触发重连...');
    const ok = await registerWithHub();
    return { code: 0, message: ok ? '重连成功' : '重连失败', data: { connected: ok } };
  });

  app.get('/health', async () => {
    return { status: 'ok', nodeId, connected, timestamp: new Date().toISOString() };
  });
}

// Export for Hub to call
export { registerWithHub };

// ─── Standalone Mode ─────────────────────────────────────────────
// When run directly (not imported by Hub), start its own Fastify server
async function startStandalone() {
  const app = Fastify({ logger: true });
  await app.register(cors, { origin: true });

  // Try multiple possible frontend dist paths
  const distCandidates = [
    path.join(__dirname, '../../assets/frontend-dist'),   // skill package layout
    path.join(__dirname, '../../frontend/dist'),           // original project layout
  ];
  const frontendDist = distCandidates.find(p => fs.existsSync(p)) || distCandidates[0];

  // Serve frontend at /node/ prefix (consistent with Hub embedded mode)
  if (fs.existsSync(frontendDist)) {
    await app.register(fastifyStatic, { root: frontendDist, prefix: '/node/', decorateReply: false });
  }

  // Mount all node API routes under /node/api/* prefix
  app.register(async (nodeApp) => {
    registerNodeRoutes(nodeApp);
  }, { prefix: '/node' });

  // Root redirect → /node
  app.get('/', async (request, reply) => {
    reply.redirect('/node');
  });

  // /node SPA entry point
  app.get('/node', async (request, reply) => {
    const indexPath = path.join(frontendDist, 'index.html');
    if (fs.existsSync(indexPath)) {
      return reply.type('text/html').send(fs.readFileSync(indexPath));
    }
    reply.code(404);
    return { code: 404, message: '前端未构建' };
  });

  // SPA fallback: /node/* non-API routes → index.html
  app.setNotFoundHandler(async (request, reply) => {
    if (request.url.startsWith('/node/api/') || request.url.startsWith('/node/health')) {
      reply.code(404);
      return { code: 404, message: 'Not Found' };
    }
    if (request.url.startsWith('/node')) {
      const indexPath = path.join(frontendDist, 'index.html');
      if (fs.existsSync(indexPath)) {
        return reply.type('text/html').send(fs.readFileSync(indexPath));
      }
    }
    reply.code(404);
    return { code: 404, message: 'Not Found. Node UI at /node' };
  });

  await app.listen({ port: NODE_PORT, host: '0.0.0.0' });
  addLog('info', `子节点服务已启动: http://0.0.0.0:${NODE_PORT}/node`);

  // Load OpenClaw memories
  loadOpenClawMemories();
  addLog('info', `已加载 ${evoMemories.size} 条记忆`);
  // Scan local skills
  scanSkillUsageFromSessions();
  scanLocalSkills();
  addLog('info', `已扫描到 ${localSkills.length} 个本地技能`);

  // Refresh skills every 5 minutes
  setInterval(() => {
    scanSkillUsageFromSessions();
    scanLocalSkills();
  }, 300000);

  await registerWithHub();
}

// ─── 全局异常处理 ─────────────────────────────────────
process.on('uncaughtException', (err) => {
  console.error('[Node][FATAL] Uncaught exception:', err);
  addLog('error', `未捕获异常: ${err.message}`);
  // 不立即退出，让 systemd 重启
});

process.on('unhandledRejection', (reason: any) => {
  console.error('[Node][FATAL] Unhandled rejection:', reason);
  addLog('error', `未处理的 Promise 拒绝: ${reason?.message || reason}`);
});

// Auto-start standalone when run directly
const isMain = !process.argv[1]?.includes('hub/server');
if (isMain) {
  startStandalone().catch((err) => {
    console.error('[Node] 启动失败:', err);
    process.exit(1);
  });
}

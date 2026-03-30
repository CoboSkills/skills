import type { LocalMemoryStore } from "./store.js";

interface LocalMemoryConfig {
  autoRecall?: boolean;
  autoCapture?: boolean;
  maxRecallResults?: number;
  similarityThreshold?: number;
  debug?: boolean;
  // NEW: Smart capture settings
  captureInterval?: number;        // Capture every N turns (default: 10)
  summariseThreshold?: number;     // Token threshold to trigger summary+prune (default: 150000)
  captureSignificantOnly?: boolean; // Only capture significant content (default: true)
  pruneAfterCapture?: boolean;      // Clear captured context from session (default: true)
}

type LogFn = (level: "info" | "warn" | "debug", msg: string, data?: Record<string, unknown>) => void;

// ─── Significance Detection Patterns ────────────────────────────────────────

const SIGNIFICANT_PATTERNS = [
  // Decisions
  /\b(entschieden|beschlossen|geplant|werde|werden|machen|setup|konfiguriert|installiert|aktiviert)\b/i,
  // Facts about user/company
  /\b(ich bin|mein|unser|unser Unternehmen|Flowagenten|Dustin|Böhmer)\b/i,
  // Credentials/keys (but mask them)
  /\b(api[_-]?key|password|secret|token|credential)\b/i,
  // Preferences
  /\b(bevorzug|präferiert|immer|nie|niemals|nur|nie wieder)\b/i,
  // Project/tasks
  /\b(projekt|setup|build|deploy|integration|team|agent)\b/i,
  // Questions about intent
  /\b(warum|wofür|was ist das|ziel| цель)\b/i,
];

function isSignificantContent(content: string): boolean {
  let matchCount = 0;
  for (const pattern of SIGNIFICANT_PATTERNS) {
    if (pattern.test(content)) matchCount++;
  }
  return matchCount >= 2 || content.length > 500;
}

function detectCategory(content: string): "preference" | "fact" | "decision" | "entity" | "other" {
  if (/\b(immer|nur|nie|bevorzug|präferiert)\b/i.test(content)) return "preference";
  if (/\b(entschieden|beschlossen|geplant|werde|werden)\b/i.test(content)) return "decision";
  if (/\b(ich bin|mein|unser|Name|Email|Konto)\b/i.test(content)) return "entity";
  if (/\b(Fact|Info|Wissenswert|Daten|Statistik)\b/i.test(content)) return "fact";
  return "other";
}

// ─── Capture Handler ─────────────────────────────────────────────────────────

export function buildCaptureHandler(
  store: LocalMemoryStore,
  cfg: LocalMemoryConfig,
  log: LogFn,
) {
  // Track pending user messages per session
  const pendingUserMessages = new Map<string, { content: string; turnIndex: number; timestamp: number }>();
  
  // Track turn counts for periodic capture
  const turnCountBySession = new Map<string, number>();
  
  // Track accumulated content for summarisation
  const accumulatedContent = new Map<string, string[]>();

  const captureInterval = cfg.captureInterval ?? 10;
  const summariseThreshold = cfg.summariseThreshold ?? 150000;
  const captureSignificantOnly = cfg.captureSignificantOnly ?? true;
  const pruneAfterCapture = cfg.pruneAfterCapture ?? true;

  return {
    /**
     * Register a user message before assistant responds
     */
    async registerUserMessage(
      userContent: string,
      sessionKey: string,
      turnIndex: number,
    ) {
      if (userContent.length < 20) return;
      if (userContent.startsWith("[") && userContent.includes("agent_end")) return;
      if (userContent.split(" ").length < 4) return;
      
      const now = Date.now();
      pendingUserMessages.set(sessionKey, { content: userContent, turnIndex, timestamp: now });
      
      // Accumulate content for later summarisation
      if (!accumulatedContent.has(sessionKey)) {
        accumulatedContent.set(sessionKey, []);
      }
      accumulatedContent.get(sessionKey)!.push(userContent);
      
      // Update turn count
      const currentTurns = turnCountBySession.get(sessionKey) ?? 0;
      turnCountBySession.set(sessionKey, currentTurns + 1);
    },

    /**
     * Main handler called at agent_end
     */
    async handle(
      event: Record<string, unknown>,
      ctx: Record<string, unknown>,
      sessionKey?: string,
    ) {
      if (!sessionKey) return;

      try {
        // Extract assistant response
        const assistantContent = extractAssistantResponse(event);
        if (!assistantContent || assistantContent.length < 5) {
          log("debug", "no assistant response to capture");
          return;
        }

        // Get pending user message
        const pending = pendingUserMessages.get(sessionKey);
        pendingUserMessages.delete(sessionKey);

        const userContent = pending?.content ?? "";
        const turnIndex = pending?.turnIndex ?? 0;
        const turnCount = turnCountBySession.get(sessionKey) ?? 0;

        // Build exchange text
        const exchangeText = buildExchangeText(userContent, assistantContent);

        // Decide what to do based on settings
        const shouldCapture = captureSignificantOnly 
          ? isSignificantContent(exchangeText) 
          : true;

        const shouldPeriodicCapture = turnCount > 0 && turnCount % captureInterval === 0;
        
        // Get token count estimate from context
        const tokenEstimate = estimateTokens(event);
        const shouldSummarise = tokenEstimate > summariseThreshold;

        if (shouldCapture || shouldPeriodicCapture || shouldSummarise) {
          // Add to memory
          const id = await store.add(exchangeText, {
            sessionKey,
            conversationId: sessionKey,
            turnIndex,
            messageType: "exchange",
            source: "assistant",
            category: detectCategory(exchangeText),
            createdAt: new Date().toISOString(),
          });

          log("info", "exchange captured", {
            id: id.slice(0, 8),
            turnIndex,
            significant: shouldCapture,
            periodic: shouldPeriodicCapture,
            summarised: shouldSummarise,
            tokenEstimate,
          });

          // If prune is enabled and we captured significant content, mark for context prune
          if (pruneAfterCapture && (shouldCapture || shouldPeriodicCapture)) {
            markContextForPruning(ctx, sessionKey, turnIndex);
          }
        }

        // Periodic summary: consolidate accumulated content
        if (shouldSummarise) {
          await consolidateMemory(store, sessionKey, accumulatedContent, log);
          accumulatedContent.set(sessionKey, []); // Clear accumulation
          
          // Mark session for context pruning after summary
          markContextForPruning(ctx, sessionKey, turnIndex);
        }
      } catch (err) {
        log("warn", "capture failed", { error: String(err) });
      }
    },
  };
}

// ─── Memory Consolidation ───────────────────────────────────────────────────

async function consolidateMemory(
  store: LocalMemoryStore,
  sessionKey: string,
  accumulated: Map<string, string[]>,
  log: LogFn,
) {
  const content = accumulated.get(sessionKey);
  if (!content || content.length < 3) return;

  // Create summary of recent conversation
  const summaryText = `Session summary (${content.length} exchanges):\n` +
    content.slice(-5).join("\n---\n");

  const id = await store.add(summaryText, {
    sessionKey,
    conversationId: sessionKey,
    turnIndex: 0,
    messageType: "summary",
    source: "system",
    category: "fact",
    createdAt: new Date().toISOString(),
  });

  log("info", "memory consolidated", { id: id.slice(0, 8), exchanges: content.length });
}

// ─── Context Pruning ────────────────────────────────────────────────────────

function markContextForPruning(
  ctx: Record<string, unknown>,
  sessionKey: string,
  turnIndex: number,
) {
  // Store pruning markers in context for the agent to use
  if (!ctx.__memoryMeta) ctx.__memoryMeta = {};
  (ctx.__memoryMeta as Record<string, unknown>)[sessionKey] = {
    lastPrunedAt: new Date().toISOString(),
    lastPrunedTurn: turnIndex,
    shouldPrune: true,
  };
}

/**
 * Call this to get the pruning signal for a session
 */
export function shouldPruneContext(
  ctx: Record<string, unknown>,
  sessionKey: string,
): boolean {
  const meta = ctx.__memoryMeta as Record<string, Record<string, unknown>> | undefined;
  if (!meta || !meta[sessionKey]) return false;
  return meta[sessionKey].shouldPrune === true;
}

// ─── Token Estimation ────────────────────────────────────────────────────────

function estimateTokens(event: Record<string, unknown>): number {
  // Rough estimate: 1 token ≈ 4 chars for German/English mixed
  let total = 0;
  
  if (typeof event.prompt === "string") {
    total += event.prompt.length;
  }
  
  if (Array.isArray(event.messages)) {
    for (const msg of event.messages as Record<string, unknown>[]) {
      const content = msg.content;
      if (typeof content === "string") {
        total += content.length;
      } else if (Array.isArray(content)) {
        for (const c of content) {
          if (typeof c === "string") total += c.length;
          else if (typeof c === "object" && c !== null) total += (c as Record<string, unknown>).text?.length ?? 0;
        }
      }
    }
  }
  
  return Math.floor(total / 4);
}

// ─── Recall Handler ──────────────────────────────────────────────────────────

export function buildRecallHandler(
  store: LocalMemoryStore,
  cfg: LocalMemoryConfig,
  log: LogFn,
) {
  return async (event: Record<string, unknown>, ctx: Record<string, unknown>) => {
    try {
      const prompt = extractPrompt(event);
      if (!prompt || prompt.length < 5) return;

      const limit = cfg.maxRecallResults ?? 10;
      const threshold = cfg.similarityThreshold ?? 0.7;

      const results = await store.search(prompt, limit, threshold);

      if (results.length === 0) return;

      const memorySection = buildMemorySection(results);

      if (Array.isArray(event.prependContext)) {
        event.prependContext.push(memorySection);
      }

      if (ctx && typeof ctx === "object") {
        (ctx as Record<string, unknown>).__localMemoryResults = results;
      }

      log("debug", "recalled memories", { count: results.length });
    } catch (err) {
      log("warn", "recall failed", { error: String(err) });
    }
  };
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function extractMessages(event: Record<string, unknown>): (string | Record<string, unknown>)[] {
  if (Array.isArray(event.messages)) {
    return event.messages as (string | Record<string, unknown>)[];
  }
  if (Array.isArray(event.content)) {
    return event.content as (string | Record<string, unknown>)[];
  }
  return [];
}

function extractPrompt(event: Record<string, unknown>): string {
  if (typeof event.prompt === "string") return event.prompt;
  if (typeof event.messages === "string") return event.messages;

  if (Array.isArray(event.messages)) {
    for (const msg of event.messages as Record<string, unknown>[]) {
      if (msg.role === "user") {
        const content = msg.content;
        if (typeof content === "string") return content;
        if (Array.isArray(content)) {
          return content.map((c) => (typeof c === "string" ? c : (c as Record<string, unknown>).text ?? "")).join(" ");
        }
      }
    }
  }
  return "";
}

function extractAssistantResponse(event: Record<string, unknown>): string {
  const messages = extractMessages(event);
  
  for (let i = messages.length - 1; i >= 0; i--) {
    const msg = messages[i];
    if (typeof msg === "object" && msg !== null && (msg as Record<string, unknown>).role === "assistant") {
      const content = (msg as Record<string, unknown>).content;
      if (typeof content === "string") return content;
      if (Array.isArray(content)) {
        return content.map((c) => (typeof c === "string" ? c : (c as Record<string, unknown>).text ?? "")).join(" ");
      }
    }
  }
  return "";
}

function buildExchangeText(user: string, assistant: string): string {
  // Limit individual messages to prevent overly long entries
  const maxLen = 2000;
  const truncatedUser = user.length > maxLen ? user.slice(0, maxLen) + "..." : user;
  const truncatedAsst = assistant.length > maxLen ? assistant.slice(0, maxLen) + "..." : assistant;
  
  return `[User]: ${truncatedUser}\n\n[Assistant]: ${truncatedAsst}`;
}

function buildMemorySection(results: { content: string; similarity: number; metadata: Record<string, unknown> }[]): string {
  if (results.length === 0) return "";
  
  const lines = results.map((r) => {
    const cat = r.metadata?.category ?? "other";
    const sim = Math.round(r.similarity * 100);
    const source = r.metadata?.source ?? "unknown";
    return `[${cat}·${sim}%·${source}] ${r.content}`;
  });

  return `\n\n📚 Memory:\n${lines.join("\n\n")}`;
}
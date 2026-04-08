#!/usr/bin/env python3
"""
OpenDream dream viewer & event server.

Watches the dreams/ directory for file changes and streams WebSocket events
to a live browser-based viewer at ``GET /``.

Usage:
    pip install aiohttp watchdog
    python3 scripts/dream_events.py                    # default workspace
    python3 scripts/dream_events.py /path/to/workspace  # explicit path
    python3 scripts/dream_events.py --port 9736         # custom port

Endpoints:
    GET /                  — HTML dream viewer
    GET /opendream.stream  — WebSocket event stream

Events emitted:
    cycle_start   — new cycle file created
    thought       — dream thought appended to a cycle file
    morning_recall  — morning recall written
    dream_start   — first file of the night created
    dream_end     — morning recall signals end of dream session

Event format (JSON):
    {
      "event": "thought",
      "cycle": 3,
      "cycle_name": "cognitive-processing",
      "date": "2026-04-06",
      "timestamp": "2026-04-06T02:30:00",
      "content": "The day had more interruptions than tasks completed."
    }
"""

import asyncio
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    from aiohttp import web
except ImportError:
    print("Install aiohttp: pip install aiohttp")
    sys.exit(1)

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("Install watchdog: pip install watchdog")
    sys.exit(1)

logger = logging.getLogger("opendream.viewer")


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_PORT = 9736  # 9-R-E-M on phone keypad
VIEWER_HTML = SKILL_DIR / "assets" / "viewer.html"

CYCLE_PATTERN = re.compile(r"cycle-(\d+)-(.+)\.md$")
MORNING_PATTERN = re.compile(r"morning-recall\.md$")

CLIENTS: set[web.WebSocketResponse] = set()
EVENT_QUEUE: asyncio.Queue = asyncio.Queue()


# ---------------------------------------------------------------------------
# Workspace detection
# ---------------------------------------------------------------------------

def find_workspace(explicit: str | None = None) -> Path:
    if explicit:
        ws = Path(explicit).expanduser().resolve()
        if ws.is_dir():
            return ws
    candidate = SKILL_DIR.parent.parent
    if (candidate / "AGENTS.md").exists() or (candidate / "SOUL.md").exists():
        return candidate
    default = Path.home() / ".openclaw" / "workspace"
    if default.is_dir():
        return default
    print("Could not detect workspace. Pass path as argument.")
    sys.exit(1)


# ---------------------------------------------------------------------------
# File event handler
# ---------------------------------------------------------------------------

class DreamFileHandler(FileSystemEventHandler):
    """Watches dreams/ for new or modified files and queues WS events."""

    def __init__(self, dreams_dir: Path):
        self.dreams_dir = dreams_dir
        self._seen_files: set[str] = set()
        self._last_content: dict[str, str] = {}

    def on_created(self, event):
        if event.is_directory:
            return
        self._handle(event.src_path, is_new=True)

    def on_modified(self, event):
        if event.is_directory:
            return
        self._handle(event.src_path, is_new=False)

    def _handle(self, path_str: str, is_new: bool):
        path = Path(path_str)
        if path.suffix != ".md":
            return

        rel = path.relative_to(self.dreams_dir)
        parts = rel.parts  # e.g. ("2026-04-06", "cycle-1-emotional-review.md")
        if len(parts) != 2:
            return

        date_str = parts[0]
        filename = parts[1]

        try:
            content = path.read_text().strip()
        except OSError:
            return

        # Detect new content (appended thought)
        prev = self._last_content.get(path_str, "")
        new_content = content[len(prev):].strip() if content.startswith(prev) else content
        self._last_content[path_str] = content

        if not new_content:
            return

        # Parse event type
        cycle_match = CYCLE_PATTERN.search(filename)
        morning_match = MORNING_PATTERN.search(filename)

        if cycle_match:
            cycle_num = int(cycle_match.group(1))
            cycle_name = cycle_match.group(2)
            file_key = path_str

            if file_key not in self._seen_files:
                self._seen_files.add(file_key)
                # Check if this is the first file of the night
                date_dir = path.parent
                existing = [f for f in date_dir.glob("cycle-*.md")]
                if len(existing) <= 1:
                    self._queue_event({
                        "event": "dream_start",
                        "date": date_str,
                        "timestamp": datetime.now().isoformat(timespec="seconds"),
                    })
                self._queue_event({
                    "event": "cycle_start",
                    "cycle": cycle_num,
                    "cycle_name": cycle_name,
                    "date": date_str,
                    "timestamp": datetime.now().isoformat(timespec="seconds"),
                })

            self._queue_event({
                "event": "thought",
                "cycle": cycle_num,
                "cycle_name": cycle_name,
                "date": date_str,
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "content": new_content,
            })

        elif morning_match:
            self._queue_event({
                "event": "morning_recall",
                "date": date_str,
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "content": new_content,
            })
            self._queue_event({
                "event": "dream_end",
                "date": date_str,
                "timestamp": datetime.now().isoformat(timespec="seconds"),
            })

    def _queue_event(self, event: dict):
        try:
            EVENT_QUEUE.put_nowait(event)
        except asyncio.QueueFull:
            pass


# ---------------------------------------------------------------------------
# HTTP handler — GET /
# ---------------------------------------------------------------------------

async def serve_viewer(_request: web.Request) -> web.Response:
    """Serve the self-contained viewer HTML page."""
    html = VIEWER_HTML.read_text(encoding="utf-8")
    return web.Response(text=html, content_type="text/html", charset="utf-8")


# ---------------------------------------------------------------------------
# WebSocket handler — GET /opendream.stream
# ---------------------------------------------------------------------------

async def ws_handler(request: web.Request) -> web.WebSocketResponse:
    """Accept a WebSocket connection and keep it open for event relay."""
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    CLIENTS.add(ws)
    logger.info("Viewer client connected (%d total)", len(CLIENTS))

    try:
        async for _msg in ws:
            pass  # read-only stream
    finally:
        CLIENTS.discard(ws)
        logger.info("Viewer client disconnected (%d remaining)", len(CLIENTS))

    return ws


# ---------------------------------------------------------------------------
# Broadcast loop
# ---------------------------------------------------------------------------

async def broadcast_loop(_app: web.Application) -> None:
    """Background task: pull events from queue and send to all WS clients."""
    while True:
        event = await EVENT_QUEUE.get()
        payload = json.dumps(event)
        logger.info("[event] %s: %s", event["event"], event.get("cycle_name", event.get("date", "")))

        closed: list[web.WebSocketResponse] = []
        for ws in CLIENTS:
            if ws.closed:
                closed.append(ws)
                continue
            try:
                await ws.send_str(payload)
            except Exception:
                logger.warning("Failed to send event to viewer client")
                closed.append(ws)
        for ws in closed:
            CLIENTS.discard(ws)


async def start_background_tasks(app: web.Application) -> None:
    app["broadcast_task"] = asyncio.create_task(broadcast_loop(app))


async def cleanup_background_tasks(app: web.Application) -> None:
    app["broadcast_task"].cancel()
    try:
        await app["broadcast_task"]
    except asyncio.CancelledError:
        pass


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

def create_app(workspace: Path) -> web.Application:
    """Create and configure the aiohttp application."""
    dreams_dir = workspace / "dreams"
    dreams_dir.mkdir(parents=True, exist_ok=True)

    handler = DreamFileHandler(dreams_dir)
    observer = Observer()
    observer.schedule(handler, str(dreams_dir), recursive=True)
    observer.start()

    app = web.Application()
    app.router.add_get("/", serve_viewer)
    app.router.add_get("/opendream.stream", ws_handler)

    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)

    app["observer"] = observer
    app["workspace"] = workspace
    app["dreams_dir"] = dreams_dir

    return app


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    port = DEFAULT_PORT
    workspace_path = None
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--port" and i + 1 < len(args):
            port = int(args[i + 1])
            i += 2
        elif not args[i].startswith("--"):
            workspace_path = args[i]
            i += 1
        else:
            i += 1
    return workspace_path, port


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="  %(message)s")
    workspace_path, port = parse_args()
    workspace = find_workspace(workspace_path)

    print(f"\n--- OpenDream Dream Viewer ---")
    print(f"  Workspace: {workspace}")
    print(f"  Watching:  {workspace / 'dreams'}")
    print(f"  Viewer:    http://localhost:{port}")
    print(f"  WebSocket: ws://localhost:{port}/opendream.stream")
    print(f"")
    print(f"  Open in browser:")
    print(f"    macOS:   open http://localhost:{port}")
    print(f"    Linux:   xdg-open http://localhost:{port}")
    print(f"    Windows: start http://localhost:{port}")
    print(f"")
    print(f"  Waiting for dream files...\n")

    app = create_app(workspace)
    try:
        web.run_app(app, host="localhost", port=port, print=None)
    except KeyboardInterrupt:
        print("\n  Stopped.")

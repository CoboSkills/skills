#!/usr/bin/env python3
"""Email Bridge Daemon - Background service for real-time email monitoring.

This daemon runs in the background and monitors email accounts using IMAP IDLE
for real-time new message notifications.

Usage:
    email-bridge daemon start
    email-bridge daemon stop
    email-bridge daemon status
"""

import json
import os
import signal
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable, Dict, Any

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from email_bridge.models import EmailProvider
from email_bridge.service import EmailBridgeService
from email_bridge.adapters.imap import IMAPAdapter


class EmailDaemon:
    """Background daemon for monitoring emails."""

    def __init__(
        self,
        poll_interval: int = 300,  # Fallback polling interval (seconds)
        on_new_email: Optional[Callable[[Dict[str, Any]], None]] = None,
        notify_openclaw: bool = True,  # Send notifications to OpenClaw
    ):
        """Initialize the daemon.

        Args:
            poll_interval: Fallback polling interval in seconds (default 5 min)
            on_new_email: Callback function when new email arrives
            notify_openclaw: Send new email notifications to OpenClaw main session
        """
        self.poll_interval = poll_interval
        self.on_new_email = on_new_email
        self.notify_openclaw = notify_openclaw
        self.service = EmailBridgeService()
        self._running = False
        self._threads: Dict[str, threading.Thread] = {}
        self._stop_events: Dict[str, threading.Event] = {}
        self._last_seen: Dict[str, set] = {}  # account_id -> set of message_ids

        # PID file for daemon management
        self.pid_file = Path.home() / ".email-bridge" / "daemon.pid"
        self.log_file = Path.home() / ".email-bridge" / "daemon.log"

    def start(self, background: bool = False):
        """Start the daemon.

        Args:
            background: If True, fork to background (daemon mode)
        """
        if self.is_running():
            print("Daemon is already running")
            return

        if background:
            self._fork_to_background()
        else:
            self._run_foreground()

    def stop(self):
        """Stop the daemon."""
        if not self.is_running():
            print("Daemon is not running")
            return

        pid = self._read_pid()
        if pid:
            try:
                os.kill(pid, signal.SIGTERM)
                print(f"Sent SIGTERM to daemon (PID {pid})")
                # Wait for daemon to stop
                for _ in range(10):
                    time.sleep(0.5)
                    if not self.is_running():
                        break
                if self.is_running():
                    os.kill(pid, signal.SIGKILL)
                    print(f"Sent SIGKILL to daemon (PID {pid})")
            except ProcessLookupError:
                pass

        # Clean up PID file
        if self.pid_file.exists():
            self.pid_file.unlink()

    def status(self) -> dict:
        """Get daemon status."""
        result = {
            "running": self.is_running(),
            "pid": self._read_pid(),
            "accounts": [],
        }

        if self.is_running():
            accounts = self.service.list_accounts()
            for acc in accounts:
                if acc.status.value == "active":
                    result["accounts"].append({
                        "id": acc.id,
                        "email": acc.email,
                        "provider": acc.provider.value,
                    })

        return result

    def is_running(self) -> bool:
        """Check if daemon is running."""
        pid = self._read_pid()
        if not pid:
            return False

        try:
            os.kill(pid, 0)  # Check if process exists
            return True
        except ProcessLookupError:
            # PID file exists but process is dead
            if self.pid_file.exists():
                self.pid_file.unlink()
            return False

    def _read_pid(self) -> Optional[int]:
        """Read PID from file."""
        if not self.pid_file.exists():
            return None
        try:
            return int(self.pid_file.read_text().strip())
        except (ValueError, IOError):
            return None

    def _write_pid(self):
        """Write current PID to file."""
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)
        self.pid_file.write_text(str(os.getpid()))

    def _fork_to_background(self):
        """Fork to background (Unix daemon)."""
        # First fork
        pid = os.fork()
        if pid > 0:
            # Parent exits
            print(f"Daemon started in background (PID {pid})")
            sys.exit(0)

        # Decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # Second fork
        pid = os.fork()
        if pid > 0:
            sys.exit(0)

        # Redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()

        # Redirect to log file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_file, "a") as log:
            os.dup2(log.fileno(), sys.stdout.fileno())
            os.dup2(log.fileno(), sys.stderr.fileno())

        # Write PID
        self._write_pid()

        # Run daemon
        self._run()

    def _run_foreground(self):
        """Run in foreground (for debugging)."""
        self._write_pid()
        print(f"Daemon started (PID {os.getpid()})")
        try:
            self._run()
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            if self.pid_file.exists():
                self.pid_file.unlink()

    def _run(self):
        """Main daemon loop."""
        self._running = True

        # Set up signal handlers
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)

        self._log("Daemon started")

        # Get active accounts
        accounts = self.service.list_accounts()
        active_accounts = [a for a in accounts if a.status.value == "active"]

        if not active_accounts:
            self._log("No active accounts to monitor")
            return

        # Start a monitor thread for each account
        for account in active_accounts:
            if account.provider in [EmailProvider.QQ, EmailProvider.NETEASE]:
                self._start_account_monitor(account)
            elif account.provider == EmailProvider.GMAIL:
                # Gmail doesn't support IMAP IDLE, use polling
                self._start_account_poller(account)

        # Wait for stop signal
        while self._running:
            time.sleep(1)

        # Stop all threads
        for account_id in list(self._stop_events.keys()):
            self._stop_events[account_id].set()

        # Wait for threads to finish
        for thread in self._threads.values():
            thread.join(timeout=5)

        self._log("Daemon stopped")

    def _handle_signal(self, signum, frame):
        """Handle shutdown signals."""
        self._log(f"Received signal {signum}")
        self._running = False

    def _log(self, message: str):
        """Log a message."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {message}"
        print(log_line, flush=True)

    def _start_account_monitor(self, account):
        """Start IMAP IDLE monitor for an account."""
        stop_event = threading.Event()
        self._stop_events[account.id] = stop_event

        thread = threading.Thread(
            target=self._monitor_account,
            args=(account, stop_event),
            daemon=True,
        )
        thread.start()
        self._threads[account.id] = thread
        self._log(f"Started monitor for {account.email}")

    def _start_account_poller(self, account):
        """Start polling for Gmail (no IDLE support)."""
        stop_event = threading.Event()
        self._stop_events[account.id] = stop_event

        thread = threading.Thread(
            target=self._poll_account,
            args=(account, stop_event),
            daemon=True,
        )
        thread.start()
        self._threads[account.id] = thread
        self._log(f"Started poller for {account.email} (interval: {self.poll_interval}s)")

    def _monitor_account(self, account, stop_event: threading.Event):
        """Monitor an account using IMAP IDLE with proper response handling."""
        import imaplib2

        # Get IMAP server config
        host, port = self._get_imap_server(account)
        password = account.config.get("password")

        if not password:
            self._log(f"{account.email}: No password configured")
            return

        while not stop_event.is_set():
            try:
                # Connect
                conn = imaplib2.IMAP4_SSL(host, port)
                conn.login(account.email, password)
                conn.select("INBOX")

                # Get initial message count
                status, data = conn.search(None, "ALL")
                last_count = len(data[0].split()) if data[0] else 0
                self._log(f"{account.email}: Connected, {last_count} messages in inbox")

                # Clear any pending responses
                list(conn.pop_untagged_responses())

                # IDLE loop
                while not stop_event.is_set():
                    try:
                        self._log(f"{account.email}: Entering IDLE mode...")

                        # Start IDLE with shorter timeout for responsiveness
                        result = conn.idle(timeout=60)  # 1 minute timeout

                        # Check untagged responses for new mail notifications
                        untagged = list(conn.pop_untagged_responses())
                        
                        # Check for EXISTS response (new message)
                        has_new_mail = False
                        for resp in untagged:
                            if len(resp) >= 2 and resp[0] == 'EXISTS':
                                has_new_mail = True
                                new_count = int(resp[1][0]) if resp[1] else 0
                                self._log(f"{account.email}: EXISTS response, count={new_count}")
                                break

                        # Also check if message count changed
                        status, data = conn.search(None, "ALL")
                        current_count = len(data[0].split()) if data[0] else 0

                        if current_count > last_count:
                            new_msg_count = current_count - last_count
                            self._log(f"{account.email}: {new_msg_count} new message(s) detected!")
                            last_count = current_count

                            # Sync the new messages
                            try:
                                sync_count = self.service.sync_account(account.id, limit=new_msg_count)
                                self._log(f"{account.email}: Synced {sync_count} message(s)")
                            except Exception as e:
                                self._log(f"{account.email}: Sync error: {e}")

                            # Notify OpenClaw
                            self._notify_openclaw(account.email, new_msg_count, account.id)

                            # Trigger callback
                            if self.on_new_email:
                                self.on_new_email({
                                    "account_id": account.id,
                                    "email": account.email,
                                    "new_count": new_msg_count,
                                })
                        else:
                            self._log(f"{account.email}: No new messages (count: {current_count})")

                    except Exception as e:
                        self._log(f"{account.email}: IDLE error: {e}")
                        break

                conn.logout()
                self._log(f"{account.email}: Disconnected")

            except Exception as e:
                self._log(f"{account.email}: Connection error: {e}")

            # Wait before reconnecting
            if not stop_event.is_set():
                stop_event.wait(timeout=60)

    def _get_imap_server(self, account) -> tuple:
        """Get IMAP server host and port for an account."""
        from .adapters.imap import IMAP_SERVERS

        email_domain = account.email.split("@")[1].lower()

        if account.provider == EmailProvider.QQ:
            config = IMAP_SERVERS[EmailProvider.QQ]
            return config["host"], config["port"]
        elif account.provider == EmailProvider.NETEASE:
            netease_config = IMAP_SERVERS[EmailProvider.NETEASE]
            if email_domain in netease_config:
                return netease_config[email_domain]["host"], netease_config[email_domain]["port"]
            return netease_config["163.com"]["host"], netease_config["163.com"]["port"]

        raise ValueError(f"Unknown provider: {account.provider}")

    def _get_latest_message_info(self, account_id: str, count: int) -> list:
        """Get details of the latest messages from an account."""
        try:
            messages = self.service.list_recent_messages(account_id=account_id, limit=count)
            result = []
            for msg in messages:
                info = {
                    "sender": msg.sender_name or msg.sender,
                    "subject": msg.subject[:50] + "..." if len(msg.subject) > 50 else msg.subject,
                }
                result.append(info)
            return result
        except Exception as e:
            self._log(f"Error getting message info: {e}")
            return []

    def _notify_openclaw(self, account_email: str, new_count: int, account_id: str = None):
        """Send notification to OpenClaw main session via system event."""
        if not self.notify_openclaw:
            return

        try:
            import subprocess
            
            # Get message details if available
            details = []
            if account_id:
                details = self._get_latest_message_info(account_id, min(new_count, 3))  # Max 3 messages
            
            if details:
                lines = [f"📧 新邮件: {account_email}"]
                for i, info in enumerate(details, 1):
                    lines.append(f"\n{i}. {info['sender']}")
                    lines.append(f"   {info['subject']}")
                if new_count > len(details):
                    lines.append(f"\n... 还有 {new_count - len(details)} 封")
                message = "\n".join(lines)
            else:
                message = f"新邮件: {account_email} 收到 {new_count} 封新邮件"
            
            self._log(f"Sending notification to OpenClaw")
            result = subprocess.run(
                ["openclaw", "system", "event", "--text", message, "--mode", "now"],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                self._log(f"OpenClaw notification sent successfully")
            else:
                self._log(f"OpenClaw notification failed (code {result.returncode}): {result.stderr.strip() or 'No error'}")
        except subprocess.TimeoutExpired:
            self._log("OpenClaw notification timed out")
        except FileNotFoundError:
            self._log("OpenClaw CLI not found at PATH")
        except Exception as e:
            self._log(f"Error sending notification: {e}")

    def _poll_account(self, account, stop_event: threading.Event):
        """Poll an account for new messages (for Gmail)."""
        # Track message count to detect new messages
        last_count = None
        
        while not stop_event.is_set():
            try:
                # Get current message count from database
                messages = self.service.list_recent_messages(account_id=account.id, limit=1000)
                current_count = len(messages)
                
                # First poll: just record the count, don't notify
                if last_count is None:
                    last_count = current_count
                    self._log(f"{account.email}: Initial count = {current_count}")
                elif current_count > last_count:
                    # New messages detected
                    new_count = current_count - last_count
                    self._log(f"{account.email}: {new_count} new message(s) detected (was {last_count}, now {current_count})")
                    last_count = current_count
                    
                    # Sync to get message details
                    self.service.sync_account(account.id, limit=new_count)
                    
                    # Notify OpenClaw
                    self._notify_openclaw(account.email, new_count, account.id)
                    
                    # Trigger callback
                    if self.on_new_email:
                        self.on_new_email({
                            "account_id": account.id,
                            "email": account.email,
                            "new_count": new_count,
                        })
                else:
                    # No new messages, just sync to keep database updated
                    self._log(f"{account.email}: No new messages (count: {current_count})")
                    self.service.sync_account(account.id, limit=10)
                    last_count = current_count

            except Exception as e:
                self._log(f"{account.email}: Poll error: {e}")

            # Wait for next poll
            stop_event.wait(timeout=self.poll_interval)


def main():
    """CLI entry point for daemon management."""
    import argparse

    parser = argparse.ArgumentParser(description="Email Bridge Daemon")
    parser.add_argument(
        "action",
        choices=["start", "stop", "status"],
        help="Action to perform",
    )
    parser.add_argument(
        "-d", "--daemon",
        action="store_true",
        help="Run in background (daemon mode)",
    )
    parser.add_argument(
        "-i", "--interval",
        type=int,
        default=300,
        help="Polling interval in seconds (default: 300)",
    )

    args = parser.parse_args()

    daemon = EmailDaemon(poll_interval=args.interval)

    if args.action == "start":
        daemon.start(background=args.daemon)
    elif args.action == "stop":
        daemon.stop()
    elif args.action == "status":
        status = daemon.status()
        print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
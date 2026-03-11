#!/usr/bin/env python3
"""
OpenClaw Security Scanner - Main Scan Script

Performs comprehensive security audit of OpenClaw deployment:
1. Network port scanning
2. Channel policy audit
3. Permission analysis
4. Risk assessment and remediation guidance

Usage:
    python3 security_scan.py [--ports-only | --channels-only | --full]
    python3 security_scan.py --help
"""

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import re

# Configuration
OPENCLAW_CONFIG_PATHS = [
    Path.home() / ".openclaw" / "openclaw.json",  # Primary config file
    Path.home() / ".openclaw" / "config.json",
    Path.home() / ".openclaw" / "gateway.config.json",
    Path("/etc/openclaw/openclaw.json"),
]

DEFAULT_PORTS = {
    "gateway": 18789,
    "web": 8080,
    "https": 443,
    "http": 80,
    "ssh": 22,
}

class PortDetectionMode(Enum):
    CONFIG_ONLY = "config_only"      # Read from config only
    PROCESS_CHECK = "process_check"  # Check running process
    MULTI_SOURCE = "multi_source"    # Multi-source verification (default)

PORT_DETECTION_MODE = PortDetectionMode.MULTI_SOURCE

RISK_LEVELS = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]


class Finding:
    """Security finding with risk assessment"""
    
    def __init__(self, level: str, category: str, title: str, 
                 description: str, impact: str, remediation: str,
                 risk_of_fix: str = "LOW", rollback: str = ""):
        self.level = level
        self.category = category
        self.title = title
        self.description = description
        self.impact = impact
        self.remediation = remediation
        self.risk_of_fix = risk_of_fix
        self.rollback = rollback
        self.evidence = []
    
    def to_dict(self) -> Dict:
        return {
            "level": self.level,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "impact": self.impact,
            "remediation": self.remediation,
            "risk_of_fix": self.risk_of_fix,
            "rollback": self.rollback,
            "evidence": self.evidence,
        }


class SecurityScanner:
    """Main security scanner class"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.findings: List[Finding] = []
        self.config: Dict = {}
        self.config_path: Optional[Path] = None
        self.scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.hostname = socket.gethostname()
        
    def log(self, message: str, level: str = "INFO"):
        """Log message with level"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def find_config(self) -> Optional[Path]:
        """Find OpenClaw configuration file"""
        for path in OPENCLAW_CONFIG_PATHS:
            if path.exists():
                self.log(f"Found config: {path}")
                return path
        
        # Try to find via environment
        if "OPENCLAW_CONFIG" in os.environ:
            path = Path(os.environ["OPENCLAW_CONFIG"])
            if path.exists():
                self.log(f"Found config via env: {path}")
                return path
        
        self.log("No config file found", "WARN")
        return None
    
    def load_config(self) -> bool:
        """Load OpenClaw configuration"""
        self.config_path = self.find_config()
        if not self.config_path:
            return False
        
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            self.log(f"Loaded config from {self.config_path}")
            return True
        except Exception as e:
            self.log(f"Failed to load config: {e}", "ERROR")
            return False
    
    def scan_ports(self) -> List[Finding]:
        """Scan for exposed ports"""
        findings = []
        
        self.log("Starting port scan...")
        
        # Check common OpenClaw ports
        for service, port in DEFAULT_PORTS.items():
            is_open = self.check_port(port)
            if is_open:
                self.log(f"Port {port} ({service}) is OPEN")
                
                # Check if bound to 0.0.0.0 (dangerous)
                bound_to = self.get_port_binding(port)
                
                if bound_to == "0.0.0.0":
                    if port == DEFAULT_PORTS["gateway"]:
                        finding = Finding(
                            level="CRITICAL",
                            category="NETWORK",
                            title=f"Gateway port {port} exposed to all interfaces",
                            description=f"OpenClaw gateway is listening on 0.0.0.0:{port}, accessible from any network interface",
                            impact="Attackers on the network can access gateway API, potentially leading to unauthorized access",
                            remediation=f"Bind gateway to 127.0.0.1:{port} or use firewall rules to restrict access",
                            risk_of_fix="MEDIUM - may break remote access if not careful",
                            rollback="Restore config and restart gateway"
                        )
                        finding.evidence.append(f"Port {port} bound to 0.0.0.0")
                        findings.append(finding)
                    else:
                        finding = Finding(
                            level="MEDIUM",
                            category="NETWORK",
                            title=f"Port {port} ({service}) exposed to all interfaces",
                            description=f"Service is listening on 0.0.0.0:{port}",
                            impact="Service accessible from any network interface",
                            remediation=f"Bind to 127.0.0.1:{port} if external access not needed",
                            risk_of_fix="LOW",
                            rollback="Restore config"
                        )
                        findings.append(finding)
                elif bound_to == "127.0.0.1":
                    self.log(f"Port {port} properly bound to localhost", "INFO")
        
        # Check for default/predictable ports
        config_port = self.get_port_from_config()
        running_port = None
        
        # Get actual port based on detection mode
        if PORT_DETECTION_MODE in [PortDetectionMode.PROCESS_CHECK, PortDetectionMode.MULTI_SOURCE]:
            running_port = self.get_port_from_running_process()
        
        # Determine final port to use
        if PORT_DETECTION_MODE == PortDetectionMode.MULTI_SOURCE:
            actual_port = running_port if running_port is not None else config_port
        elif PORT_DETECTION_MODE == PortDetectionMode.PROCESS_CHECK:
            actual_port = running_port if running_port is not None else DEFAULT_PORTS["gateway"]
        else:
            actual_port = config_port
        
        # Check for configuration mismatch
        if running_port and config_port != running_port:
            self.log(f"Configuration mismatch: config port={config_port}, running port={running_port}", "WARN")
        
        # Check if using default port
        if actual_port in [18789, 8080, 80, 443]:
            finding = Finding(
                level="LOW",
                category="NETWORK",
                title=f"Using default port {actual_port}",
                description=f"Gateway uses well-known default port {actual_port}",
                impact="Attackers can easily guess the service port",
                remediation="Consider using a non-standard port (security through obscurity, not a primary defense)",
                risk_of_fix="HIGH - changing port will break all existing connections",
                rollback="Revert port configuration"
            )
            findings.append(finding)
        
        return findings
    
    def check_port(self, port: int, host: str = "127.0.0.1") -> bool:
        """Check if port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def get_port_from_running_process(self) -> Optional[int]:
        """Get actual running gateway port by checking process status"""
        try:
            result = subprocess.run(
                ["openclaw", "gateway", "status", "--json"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                status = json.loads(result.stdout)
                port_value = status.get("port")
                if port_value is not None:
                    return int(port_value)
        except Exception as e:
            self.log(f"Failed to get running port: {e}", "DEBUG")
        
        return None
    
    def get_port_from_config(self) -> int:
        """Get port from configuration with proper fallback"""
        if not self.config:
            return DEFAULT_PORTS["gateway"]
        
        return self.config.get("gateway", {}).get("port", DEFAULT_PORTS["gateway"])
    
    def get_port_binding(self, port: int) -> str:
        """Get address port is bound to.

        Tries lsof first (macOS/Linux), then falls back to ss (Linux).
        Returns 'unknown' if neither tool is available.
        """
        binding = self._try_lsof(port) or self._try_ss(port)
        if not binding:
            self.log(
                "Neither 'lsof' nor 'ss' found; cannot determine port binding. "
                "Install lsof or iproute2 for full network scanning.",
                "WARN",
            )
        return binding or "unknown"

    def _parse_listen_line(self, line: str) -> Optional[str]:
        if "127.0.0.1" in line:
            return "127.0.0.1"
        if "*" in line or "0.0.0.0" in line:
            return "0.0.0.0"
        if ":::" in line:
            return ":: (IPv6 any)"
        return None

    def _try_lsof(self, port: int) -> Optional[str]:
        if not shutil.which("lsof"):
            return None
        try:
            result = subprocess.run(
                ["lsof", "-i", f":{port}", "-n", "-P"],
                capture_output=True, text=True, timeout=5,
            )
            for line in result.stdout.splitlines():
                if "LISTEN" in line:
                    binding = self._parse_listen_line(line)
                    if binding:
                        return binding
        except Exception:
            pass
        return None

    def _try_ss(self, port: int) -> Optional[str]:
        if not shutil.which("ss"):
            return None
        try:
            result = subprocess.run(
                ["ss", "-tlnp", f"sport = :{port}"],
                capture_output=True, text=True, timeout=5,
            )
            for line in result.stdout.splitlines():
                if "LISTEN" in line:
                    binding = self._parse_listen_line(line)
                    if binding:
                        return binding
        except Exception:
            pass
        return None
    
    def scan_channels(self) -> List[Finding]:
        """Audit channel configurations"""
        findings = []
        
        self.log("Scanning channel configurations...")
        
        channels = self.config.get("channels", {})
        
        # Telegram
        telegram = channels.get("telegram", {})
        if telegram.get("enabled"):
            group_policy = telegram.get("groupPolicy", "deny")
            
            if group_policy == "allow":
                finding = Finding(
                    level="CRITICAL",
                    category="CHANNEL",
                    title="Telegram allows all group messages",
                    description="Telegram channel configured with groupPolicy='allow', permitting messages from any group",
                    impact="Anyone can send messages to your OpenClaw instance, potential for spam, abuse, or prompt injection attacks",
                    remediation="Set groupPolicy='allowlist' or 'deny' and explicitly configure allowedGroups",
                    risk_of_fix="LOW - won't break existing 1:1 chats",
                    rollback="Revert groupPolicy to 'allow'"
                )
                finding.evidence.append(f"groupPolicy: {group_policy}")
                findings.append(finding)
            
            # Check for missing allowlist
            if group_policy == "allowlist":
                allowed_groups = telegram.get("allowedGroups", [])
                if not allowed_groups:
                    finding = Finding(
                        level="HIGH",
                        category="CHANNEL",
                        title="Telegram allowlist is empty",
                        description="groupPolicy='allowlist' but allowedGroups is empty or not configured",
                        impact="No groups can message the bot, may indicate misconfiguration",
                        remediation="Add group IDs to allowedGroups or change groupPolicy",
                        risk_of_fix="LOW",
                        rollback="N/A"
                    )
                    findings.append(finding)
        
        # WhatsApp
        whatsapp = channels.get("whatsapp", {})
        if whatsapp.get("enabled"):
            # Check for missing authentication
            if not whatsapp.get("webhookSecret"):
                finding = Finding(
                    level="HIGH",
                    category="CHANNEL",
                    title="WhatsApp webhook missing secret",
                    description="WhatsApp channel enabled without webhookSecret for request validation",
                    impact="Attackers could forge WhatsApp messages",
                    remediation="Generate and configure webhookSecret",
                    risk_of_fix="LOW",
                    rollback="N/A"
                )
                findings.append(finding)
        
        # Web channel
        web = channels.get("web", {})
        if web.get("enabled"):
            auth_enabled = web.get("authentication", {}).get("enabled", False)
            if not auth_enabled:
                finding = Finding(
                    level="CRITICAL",
                    category="CHANNEL",
                    title="Web channel has no authentication",
                    description="Web UI is accessible without authentication",
                    impact="Anyone with network access can use the web interface",
                    remediation="Enable authentication in web channel config",
                    risk_of_fix="MEDIUM - will require login",
                    rollback="Disable authentication (not recommended)"
                )
                findings.append(finding)
        
        # Check for all channels with allow-all policies
        for channel_name, channel_config in channels.items():
            if isinstance(channel_config, dict):
                policy = channel_config.get("policy", channel_config.get("groupPolicy", ""))
                if policy == "allow" and channel_name not in ["telegram"]:
                    finding = Finding(
                        level="HIGH",
                        category="CHANNEL",
                        title=f"{channel_name} channel allows all messages",
                        description=f"Channel {channel_name} has permissive policy",
                        impact="Unauthorized users may interact with the bot",
                        remediation=f"Configure allowlist or denylist for {channel_name}",
                        risk_of_fix="LOW",
                        rollback=f"Revert {channel_name} policy"
                    )
                    findings.append(finding)
        
        return findings
    
    def scan_permissions(self) -> List[Finding]:
        """Analyze tool and execution permissions"""
        findings = []
        
        self.log("Analyzing permissions...")
        
        tools = self.config.get("tools", {})
        
        # Check exec policy
        exec_policy = tools.get("exec", {}).get("policy", "deny")
        
        if exec_policy == "allow":
            finding = Finding(
                level="CRITICAL",
                category="PERMISSION",
                title="Tool execution policy is 'allow'",
                description="All tools can execute without restrictions (tools.exec.policy='allow')",
                impact="Any tool can run arbitrary commands, high risk of abuse or accidental damage",
                remediation="Set tools.exec.policy='deny' or 'allowlist' and configure allowedCommands",
                risk_of_fix="HIGH - may break existing workflows",
                rollback="Revert exec policy to 'allow'"
            )
            finding.evidence.append(f"exec.policy: {exec_policy}")
            findings.append(finding)
        
        # Check filesystem access
        fs_config = tools.get("fs", {})
        workspace_only = fs_config.get("workspaceOnly", True)
        
        if not workspace_only:
            finding = Finding(
                level="HIGH",
                category="PERMISSION",
                title="Filesystem access not restricted to workspace",
                description="tools.fs.workspaceOnly=false allows access to entire filesystem",
                impact="Tools can read/write sensitive files outside workspace",
                remediation="Set tools.fs.workspaceOnly=true",
                risk_of_fix="MEDIUM - may break tools needing broader access",
                rollback="Set workspaceOnly=false"
            )
            findings.append(finding)
        
        # Check for dangerous tools enabled
        dangerous_tools = ["exec", "shell", "system.run", "canvas.eval"]
        enabled_tools = tools.get("enabled", [])
        
        for tool in dangerous_tools:
            if tool in enabled_tools:
                finding = Finding(
                    level="MEDIUM",
                    category="PERMISSION",
                    title=f"Dangerous tool enabled: {tool}",
                    description=f"Tool '{tool}' can execute arbitrary code",
                    impact="Potential for code execution attacks if tool is compromised",
                    remediation=f"Disable {tool} if not needed, or restrict via allowlist",
                    risk_of_fix="MEDIUM - may break functionality",
                    rollback=f"Re-enable {tool}"
                )
                findings.append(finding)
        
        # Check for context-aware permissions (advanced feature)
        if not self.config.get("contexts", {}).get("enabled"):
            finding = Finding(
                level="LOW",
                category="PERMISSION",
                title="Context-aware permissions not enabled",
                description="No dynamic permission switching based on context (user, channel, time)",
                impact="Cannot implement least-privilege per scenario",
                remediation="Consider implementing context-aware permissions for flexible security",
                risk_of_fix="LOW",
                rollback="N/A"
            )
            findings.append(finding)
        
        return findings
    
    def generate_report(self, output_path: Optional[Path] = None) -> str:
        """Generate security audit report"""
        
        # Count findings by level
        level_counts = {level: 0 for level in RISK_LEVELS}
        for finding in self.findings:
            level_counts[finding.level] = level_counts.get(finding.level, 0) + 1
        
        # Determine overall risk
        if level_counts["CRITICAL"] > 0:
            overall_risk = "CRITICAL"
        elif level_counts["HIGH"] > 0:
            overall_risk = "HIGH"
        elif level_counts["MEDIUM"] > 0:
            overall_risk = "MEDIUM"
        elif level_counts["LOW"] > 0:
            overall_risk = "LOW"
        else:
            overall_risk = "INFO"
        
        # Generate report
        report = f"""# OpenClaw Security Audit Report

**Scan Date**: {self.scan_time}
**Hostname**: {self.hostname}
**Config Path**: {self.config_path or 'Not found'}
**Overall Risk Level**: {overall_risk}

---

## Executive Summary

Security scan identified **{len(self.findings)} findings**:
- 🔴 CRITICAL: {level_counts['CRITICAL']}
- 🟠 HIGH: {level_counts['HIGH']}
- 🟡 MEDIUM: {level_counts['MEDIUM']}
- 🔵 LOW: {level_counts['LOW']}
- ⚪ INFO: {level_counts['INFO']}

"""
        
        if overall_risk in ["CRITICAL", "HIGH"]:
            report += """⚠️ **IMMEDIATE ACTION REQUIRED**

Critical or high-risk vulnerabilities detected. Review and remediate immediately.
Some fixes may require staged rollout to avoid breaking remote access.

"""
        
        report += """---

## Findings

"""
        
        # Group findings by level
        for level in RISK_LEVELS:
            level_findings = [f for f in self.findings if f.level == level]
            if level_findings:
                emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🔵", "INFO": "⚪"}[level]
                report += f"### {emoji} {level} ({len(level_findings)})\n\n"
                
                for i, finding in enumerate(level_findings, 1):
                    report += f"""#### {i}. {finding.title}

**Category**: {finding.category}  
**Impact**: {finding.impact}  
**Risk of Fix**: {finding.risk_of_fix}

**Description**:  
{finding.description}

**Remediation**:  
{finding.remediation}

"""
                    if finding.rollback:
                        report += f"""**Rollback Plan**:  
{finding.rollback}

"""
                    if finding.evidence:
                        report += f"""**Evidence**:  
"""
                        for ev in finding.evidence:
                            report += f"- {ev}\n"
                        report += "\n"
                    
                    report += "---\n\n"
        
        # Remediation plan
        report += """---

## Remediation Plan

### Immediate Actions (< 24h)

"""
        immediate = [f for f in self.findings if f.level in ["CRITICAL", "HIGH"] and f.risk_of_fix in ["LOW", "MEDIUM"]]
        if immediate:
            for finding in immediate:
                report += f"- [ ] **{finding.title}**\n"
                report += f"  - Fix: {finding.remediation}\n"
                report += f"  - Risk: {finding.risk_of_fix}\n\n"
        else:
            report += "No immediate low-risk actions identified.\n\n"
        
        report += """### Staged Rollout Required

⚠️ These fixes may break remote access. Follow staged rollout protocol:

1. Backup current configuration
2. Verify alternative access (SSH, console)
3. Test in staging environment
4. Apply with monitoring
5. Keep rollback ready

"""
        staged = [f for f in self.findings if f.risk_of_fix in ["HIGH", "MEDIUM"]]
        if staged:
            for finding in staged:
                report += f"- [ ] **{finding.title}**\n"
                report += f"  - Fix: {finding.remediation}\n"
                report += f"  - Rollback: {finding.rollback}\n\n"
        else:
            report += "No staged rollout required.\n\n"
        
        # Appendix
        report += f"""---

## Appendix

### Scan Configuration
- Verbose: {self.verbose}
- Config loaded: {self.config_path is not None}
- Total findings: {len(self.findings)}

### Recommendations

1. **Regular Scans**: Run this scan weekly or after major changes
2. **Backup Configs**: Always backup before changes
3. **Least Privilege**: Default to minimal permissions
4. **Defense in Depth**: Multiple security layers

### Contact

For security emergencies, contact your security team immediately.

---

*Report generated by OpenClaw Security Scanner v1.0.3*
"""
        
        # Save report
        if output_path:
            with open(output_path, 'w') as f:
                f.write(report)
            self.log(f"Report saved to {output_path}")
        
        return report
    
    def run_full_scan(self) -> List[Finding]:
        """Run complete security scan"""
        self.log("=" * 60)
        self.log("OpenClaw Security Scanner v1.0.3")
        self.log("=" * 60)
        
        # Load config
        if not self.load_config():
            self.log("Continuing scan without config (limited checks)", "WARN")
        
        # Run scans
        self.log("\n[1/3] Network port scanning...")
        self.findings.extend(self.scan_ports())
        
        self.log("\n[2/3] Channel policy audit...")
        self.findings.extend(self.scan_channels())
        
        self.log("\n[3/3] Permission analysis...")
        self.findings.extend(self.scan_permissions())
        
        self.log(f"\n{'=' * 60}")
        self.log(f"Scan complete. {len(self.findings)} findings.")
        self.log(f"{'=' * 60}")
        
        return self.findings


def main():
    parser = argparse.ArgumentParser(description="OpenClaw Security Scanner")
    parser.add_argument("--ports-only", action="store_true", help="Only scan ports")
    parser.add_argument("--channels-only", action="store_true", help="Only audit channels")
    parser.add_argument("--permissions-only", action="store_true", help="Only analyze permissions")
    parser.add_argument("--output", "-o", type=Path, help="Output report path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--full", action="store_true", help="Full scan (default)")
    
    args = parser.parse_args()
    
    scanner = SecurityScanner(verbose=args.verbose)
    
    # Determine scan type
    if args.ports_only:
        scanner.load_config()
        scanner.findings.extend(scanner.scan_ports())
    elif args.channels_only:
        scanner.load_config()
        scanner.findings.extend(scanner.scan_channels())
    elif args.permissions_only:
        scanner.load_config()
        scanner.findings.extend(scanner.scan_permissions())
    else:
        scanner.run_full_scan()
    
    # Generate report
    output_path = args.output or Path(f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    report = scanner.generate_report(output_path)
    
    # Print summary
    print("\n" + "=" * 60)
    print("SCAN SUMMARY")
    print("=" * 60)
    
    level_counts = {}
    for finding in scanner.findings:
        level_counts[finding.level] = level_counts.get(finding.level, 0) + 1
    
    for level in RISK_LEVELS:
        count = level_counts.get(level, 0)
        if count > 0:
            print(f"{level}: {count}")
    
    print(f"\nFull report: {output_path}")
    
    # Exit with error if critical/high findings
    if level_counts.get("CRITICAL", 0) > 0 or level_counts.get("HIGH", 0) > 0:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()

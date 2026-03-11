#!/usr/bin/env python3
"""
OpenClaw Security Scanner - CLI Wrapper

Provides `openclaw security-scan` command interface.

Usage:
    openclaw security-scan [OPTIONS]
    
Options:
    --ports-only      Only scan network ports
    --channels        Only audit channel policies
    --permissions     Only analyze permissions
    --output, -o FILE Save report to file
    --verbose, -v     Verbose output
    --help, -h        Show this help
"""

import argparse
import sys
import os
from pathlib import Path

# Find the script directory
script_dir = Path(__file__).parent
security_scan_script = script_dir / "security_scan.py"

def main():
    parser = argparse.ArgumentParser(
        prog="openclaw security-scan",
        description="OpenClaw Security Scanner - Audit your deployment for vulnerabilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  openclaw security-scan                      # Full security audit
  openclaw security-scan --ports-only         # Scan ports only
  openclaw security-scan -o report.md         # Save report to file
  openclaw security-scan --verbose            # Verbose output

Risk Levels:
  CRITICAL  - Immediate action required (< 1 hour)
  HIGH      - Fix within 24 hours
  MEDIUM    - Fix within 1 week
  LOW       - Fix within 1 month

For more info: https://github.com/openclaw/openclaw/tree/main/skills/openclaw-security-scanner
        """
    )
    
    parser.add_argument(
        "--ports-only",
        action="store_true",
        help="Only scan network ports"
    )
    parser.add_argument(
        "--channels",
        action="store_true",
        help="Only audit channel policies"
    )
    parser.add_argument(
        "--permissions",
        action="store_true",
        help="Only analyze permissions"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Save report to file"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be scanned without running"
    )
    
    args = parser.parse_args()
    
    # Build command
    cmd = [sys.executable, str(security_scan_script)]
    
    if args.ports_only:
        cmd.append("--ports-only")
    elif args.channels:
        cmd.append("--channels-only")
    elif args.permissions:
        cmd.append("--permissions-only")
    
    if args.output:
        cmd.extend(["--output", str(args.output)])
    
    if args.verbose:
        cmd.append("--verbose")
    
    if args.dry_run:
        print(f"Would execute: {' '.join(cmd)}")
        return 0
    
    # Execute the security scan script
    import subprocess
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except FileNotFoundError:
        print(f"Error: Security scan script not found at {security_scan_script}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nScan interrupted by user")
        return 130
    except Exception as e:
        print(f"Error running security scan: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())

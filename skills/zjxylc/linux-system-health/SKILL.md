---
name: linux-system-health
description: Diagnose Linux OS-level issues — slow server, OOM kills, disk full, high CPU/load, DNS failures, connection timeouts, port exhaustion, too many open files, zombie processes, browser automation failures, locale problems, and kernel misconfigurations.
version: 1.0.0
tags:
  - linux
  - diagnostics
  - performance
  - memory
  - disk
  - network
  - troubleshooting
metadata:
  openclaw:
    os:
      - linux
    requires:
      bins:
        - bash
        - ss
        - free
    emoji: "\U0001F5A5"
    homepage: https://github.com/ecsgo-helper/openclaw-system-health
---

# Linux System Health Diagnostic Skill

You are a Linux OS diagnostic expert. When a user reports any of the following problems, use this skill:
- **Performance**: server slow, high load, lag, unresponsive
- **Memory**: OOM killed, out of memory, memory leak, swap thrashing
- **Disk**: disk full, read-only filesystem, inode exhaustion, log files too large
- **CPU**: high CPU, IO wait, process stuck, load average spike
- **Network**: DNS failure, connection timeout, port exhaustion, CLOSE_WAIT accumulation, firewall blocking
- **Process**: crash, zombie processes, too many open files, file descriptor limit
- **Browser automation**: missing shared libraries, Chromium sandbox error, headless browser failures
- **Locale/Encoding**: garbled text, character encoding issues, locale not configured

Use the shell commands and judgment rules below to systematically diagnose OS-level root causes.

**When NOT to use this skill**: For application-level issues specific to OpenClaw (gateway config, API keys, model configuration, service management, systemd units), use the `openclaw-diagnostic` skill instead. This skill only covers OS-level diagnostics.

**Diagnostic workflow**:
1. Always start with Section 1 (System Environment Baseline) to establish context
2. Then run the sections relevant to the user's reported symptoms
3. If the root cause is unclear, run all sections in order for a comprehensive check

> **Execution convention**: All commands must be run on the target Linux server as root. Run `export LANG=C` first for consistent output. Every command is **read-only** — no writes, restarts, or deletes.

**Output format**: After running diagnostics, report findings as a severity-sorted list (FATAL > CRITICAL > ERROR > WARNING > INFO). For each issue found, include:
- Issue name (e.g., `OpenClaw.Memory.SystemMemoryCritical`)
- Severity level
- Observed value vs threshold
- Recommended remediation

---

## Severity Levels

| Level | Meaning | Action |
|-------|---------|--------|
| **FATAL** | System cannot support workloads at all | Must fix before launching any service |
| **CRITICAL** | Major functionality broken or at risk of crashing | Fix immediately |
| **ERROR** | Partial degradation of system services | Fix soon |
| **WARNING** | Potential risk; may cause problems under load | Recommended fix |
| **INFO** | Informational observation | No action needed |

---

## 1. System Environment Baseline

Collect OS context for subsequent analysis.

```bash
# OS identification
cat /etc/os-release 2>/dev/null || cat /etc/system-release 2>/dev/null

# Kernel and architecture
uname -r
uname -m

# Uptime and load
uptime

# Memory overview
free -h

# Disk overview
df -Th

# CPU count
nproc
```

**Judgment rules**:
- Record output as **OpenClaw.System.EnvironmentBaseline** (INFO) — no issues, context only.

---

## 2. Memory & OOM

Detect low memory and past OOM kills that affect any workload on this server.

```bash
# Current memory
free -h

# Detailed memory info
cat /proc/meminfo | grep -E 'MemTotal|MemFree|MemAvailable|SwapTotal|SwapFree'

# Kernel OOM events
dmesg | grep -iE 'out of memory|oom-killer|killed process'

# Journal OOM events
journalctl --no-pager -k | grep -iE 'oom-killer|killed process' 2>/dev/null

# Syslog OOM events
grep -iE 'out of memory|oom-killer' /var/log/messages /var/log/syslog 2>/dev/null | tail -20

# Which processes were OOM-killed
dmesg | grep -i 'oom-killer' | grep -oP 'comm="\K[^"]+' 2>/dev/null | sort | uniq -c | sort -rn | head -5

# Top memory consumers
ps -eo rss,pid,comm --sort=-rss | head -11
```

**Judgment rules**:
- MemAvailable / MemTotal < 5% → **OpenClaw.Memory.SystemMemoryCritical** (CRITICAL)
  - Remediation: Kill unnecessary processes, add swap, or increase instance RAM
- MemAvailable / MemTotal < 10% → **OpenClaw.Memory.SystemMemoryLow** (WARNING)
  - Remediation: Monitor closely; consider scaling up
- MemTotal < 2 GB → **OpenClaw.Memory.InsufficientTotalMemory** (ERROR)
  - Remediation: 4 GB+ RAM recommended for production workloads
- dmesg contains "oom-killer" → **OpenClaw.Memory.OOMKillerEvent** (WARNING)
  - Remediation: Identify which processes were killed; review memory allocation

---

## 3. CPU & Performance

Resource contention causes slow responses; high iowait indicates disk bottlenecks.

```bash
# System load overview
top -bn1 | head -5

# CPU time breakdown
cat /proc/stat | head -1
# Format: cpu user nice system idle iowait irq softirq steal

# Load averages and CPU count
cat /proc/loadavg
nproc

# Top CPU consumers
ps -eo %cpu,pid,comm --sort=-%cpu | head -11
```

**Judgment rules**:
- Load average (1 min) > 2x `nproc` → **OpenClaw.CPU.SystemLoadHigh** (WARNING)
  - Remediation: Identify top CPU consumers; check for runaway processes
- CPU idle < 10% (i.e., total utilization > 90%) → **OpenClaw.CPU.SystemCPUExhausted** (CRITICAL)
  - Remediation: Identify top process; check for log flooding or computation storms
- iowait > 30% (from `/proc/stat`) → **OpenClaw.CPU.HighIOWait** (WARNING)
  - Remediation: Check disk I/O — likely excessive logging or disk-bound workload

---

## 4. Network Infrastructure

Basic network configuration, DNS, IPv6, and firewall state.

```bash
# All listening TCP ports
ss -tlnp

# Network interfaces — IPv4 vs IPv6
ip addr show | grep -E 'inet |inet6 '

# IPv6 state
sysctl net.ipv6.conf.all.disable_ipv6 2>/dev/null

# DNS configuration
cat /etc/resolv.conf

# Firewall rules
iptables -L -n 2>/dev/null | head -20
```

**Judgment rules**:
- IPv6 enabled and services bind `::` but upstream resolves to IPv4 only → **OpenClaw.Network.IPv6Mismatch** (WARNING)
  - Remediation: Set `NODE_OPTIONS='--dns-result-order=ipv4first'` or `sysctl -w net.ipv6.conf.all.disable_ipv6=1`

---

## 5. Disk & inotify

Disk space exhaustion and inotify limits cause "ENOSPC" errors.

```bash
# Disk usage
df -Th

# Inode usage
df -ih

# inotify limits
cat /proc/sys/fs/inotify/max_user_watches
cat /proc/sys/fs/inotify/max_user_instances
```

**Judgment rules**:
- Any filesystem usage >= 95% → **OpenClaw.Disk.FilesystemFull** (CRITICAL)
  - Remediation: Clean old logs and data; extend partition or add disk
- Any filesystem usage >= 80% → **OpenClaw.Disk.FilesystemHighUsage** (WARNING)
  - Remediation: Monitor; plan cleanup or expansion
- `max_user_watches` < 65536 → **OpenClaw.Disk.InotifyWatchesTooLow** (ERROR)
  - Remediation: `echo 'fs.inotify.max_user_watches=524288' >> /etc/sysctl.d/99-inotify.conf && sysctl -p /etc/sysctl.d/99-inotify.conf`
- `max_user_instances` < 256 → **OpenClaw.Disk.InotifyInstancesTooLow** (WARNING)
  - Remediation: `echo 'fs.inotify.max_user_instances=512' >> /etc/sysctl.d/99-inotify.conf && sysctl -p /etc/sysctl.d/99-inotify.conf`

---

## 6. File Descriptor & Process Limits

Low ulimits cause "too many open files" (EMFILE) errors under load.

```bash
# Current shell nofile limit
ulimit -n

# System-wide limits config
cat /etc/security/limits.conf 2>/dev/null | grep -v '^#' | grep -i nofile

# Kernel maximums
sysctl fs.nr_open
sysctl fs.file-max

# Current system-wide file descriptor usage
cat /proc/sys/fs/file-nr
# Format: allocated  free  max

# PID space
sysctl kernel.pid_max
```

**Judgment rules**:
- Shell `ulimit -n` < 4096 → **OpenClaw.Limits.NofileTooLow** (ERROR)
  - Remediation: Add `* soft nofile 65536` and `* hard nofile 65536` to `/etc/security/limits.conf`; re-login
- limits.conf `nofile` value > `fs.nr_open` → **OpenClaw.Limits.NofileExceedsKernelMax** (CRITICAL)
  - Remediation: Increase `fs.nr_open` first: `sysctl -w fs.nr_open=1048576` and persist in `/etc/sysctl.d/`
- `file-nr` allocated / max > 80% → **OpenClaw.Limits.SystemFileDescriptorsHigh** (WARNING)
  - Remediation: Identify processes holding many FDs (`ls /proc/*/fd 2>/dev/null | wc -l`); increase `fs.file-max` if needed

---

## 7. Kernel & Sysctl Tuning

nf_conntrack, TCP tuning, and somaxconn affect high-concurrency workloads.

```bash
# Key kernel parameters
sysctl -a 2>/dev/null | grep -E \
  'net.core.somaxconn|net.ipv4.tcp_max_tw_buckets|net.netfilter.nf_conntrack_max|net.ipv4.tcp_tw_reuse|net.ipv4.ip_local_port_range|net.ipv4.tcp_fin_timeout|net.core.netdev_max_backlog|vm.swappiness|vm.overcommit_memory'

# Conntrack overflow events
dmesg | grep -i 'nf_conntrack.*table full'

# TCP connection state summary
ss -s

# TCP extended stats
cat /proc/net/netstat | grep -E 'TcpExt|ListenOverflows|ListenDrops'

# Swap info
swapon --show 2>/dev/null
```

**Judgment rules**:
- `nf_conntrack_max` < 65536 → **OpenClaw.Kernel.NfConntrackMaxTooLow** (ERROR)
  - Remediation: `sysctl -w net.netfilter.nf_conntrack_max=262144` and persist in `/etc/sysctl.d/99-sysctl.conf`
- dmesg contains "nf_conntrack: table full" → **OpenClaw.Kernel.NfConntrackTableFull** (CRITICAL)
  - Remediation: Increase `nf_conntrack_max`; check for connection leaks
- `somaxconn` < 1024 → **OpenClaw.Kernel.SomaxconnTooLow** (WARNING)
  - Remediation: `sysctl -w net.core.somaxconn=4096` and persist
- `tcp_max_tw_buckets` < 10000 → **OpenClaw.Kernel.TcpMaxTwBucketsTooLow** (WARNING)
  - Remediation: `sysctl -w net.ipv4.tcp_max_tw_buckets=262144`
- `tcp_tw_reuse = 0` → **OpenClaw.Kernel.TcpTwReuseNotEnabled** (WARNING)
  - Remediation: `sysctl -w net.ipv4.tcp_tw_reuse=1`
- TIME_WAIT count from `ss -s` > 10000 → **OpenClaw.Kernel.TimeWaitOverflow** (WARNING)
  - Remediation: Enable `tcp_tw_reuse`, increase `tcp_max_tw_buckets`, reduce `tcp_fin_timeout`
- ListenOverflows > 0 in `/proc/net/netstat` → **OpenClaw.Kernel.TcpListenOverflows** (WARNING)
  - Remediation: Increase `somaxconn` and application backlog setting
- `vm.overcommit_memory = 2` and swap < 1 GB → **OpenClaw.Kernel.StrictOvercommitWithLowSwap** (WARNING)
  - Remediation: Add swap space or set `vm.overcommit_memory=0`

---

## 8. DNS Resolution Health

Broken or slow DNS causes `EAI_AGAIN` errors, API timeouts, and silent connectivity failures.

```bash
# DNS configuration
cat /etc/resolv.conf

# Count nameserver lines
grep -c '^nameserver' /etc/resolv.conf 2>/dev/null

# Resolution test (multiple methods, fallback chain)
timeout 5 nslookup github.com 2>&1 || timeout 5 dig +short github.com 2>&1 || timeout 5 getent hosts github.com 2>&1

# Nameserver reachability
for ns in $(grep '^nameserver' /etc/resolv.conf | awk '{print $2}'); do
  timeout 3 bash -c "echo >/dev/tcp/$ns/53" 2>/dev/null && echo "$ns reachable" || echo "$ns UNREACHABLE"
done

# systemd-resolved status
systemctl is-active systemd-resolved 2>/dev/null
resolvectl status 2>/dev/null | head -10
```

**Judgment rules**:
- `/etc/resolv.conf` is empty or has zero `nameserver` lines → **OpenClaw.Network.NoDNSNameservers** (ERROR)
  - Remediation: Add nameservers — e.g., `echo 'nameserver 8.8.8.8' >> /etc/resolv.conf`; for systemd-resolved check `/etc/systemd/resolved.conf`
- `nslookup`, `dig`, and `getent` all fail for a known-good domain → **OpenClaw.Network.DNSResolutionFailed** (CRITICAL)
  - Remediation: Verify network connectivity; check if nameservers are reachable; inspect firewall rules blocking UDP/TCP port 53
- Any configured nameserver fails TCP/53 reachability test → **OpenClaw.Network.DNSNameserverUnreachable** (WARNING)
  - Remediation: Replace unreachable nameserver in `/etc/resolv.conf`; consider adding a backup nameserver

---

## 9. Time Synchronization

Clock drift causes SSL/TLS certificate validation failures, API auth token rejection, and log timestamp inconsistencies.

```bash
# Time and NTP status
timedatectl 2>/dev/null

# NTP service status (check all common implementations)
systemctl is-active chronyd 2>/dev/null || echo "chronyd not active"
systemctl is-active ntpd 2>/dev/null || echo "ntpd not active"
systemctl is-active systemd-timesyncd 2>/dev/null || echo "systemd-timesyncd not active"

# Clock offset (chrony)
chronyc tracking 2>/dev/null | grep -E 'System time|Last offset'

# Clock offset (ntpd)
ntpstat 2>/dev/null

# Hardware clock vs system clock
hwclock --show 2>/dev/null
date '+%Y-%m-%d %H:%M:%S %Z'
```

**Judgment rules**:
- None of `chronyd`, `ntpd`, or `systemd-timesyncd` is active → **OpenClaw.Time.NTPServiceNotRunning** (ERROR)
  - Remediation: Install and enable a time sync service — `yum install chrony && systemctl enable --now chronyd` (RHEL/CentOS) or `apt install chrony && systemctl enable --now chronyd` (Debian/Ubuntu)
- `timedatectl` shows "NTP synchronized: no" → **OpenClaw.Time.ClockNotSynchronized** (CRITICAL)
  - Remediation: Start NTP service; verify NTP server reachability (`chronyc sources` or `ntpq -p`); check firewall allows UDP port 123
- `chronyc tracking` shows system clock offset > 3 seconds, or hwclock drift > 5 seconds from system time → **OpenClaw.Time.ClockDriftDetected** (WARNING)
  - Remediation: Force sync — `chronyc makestep` or `ntpdate -u pool.ntp.org`; investigate why drift occurred (suspended VM, unreachable NTP server)

---

## 10. Zombie & D-State Processes

Zombie processes indicate child process leaks; D-state (uninterruptible sleep) processes signal I/O hangs that block system operations.

```bash
# Zombie process count
ZOMBIE_COUNT=$(ps aux | awk '$8 ~ /^Z/ {count++} END {print count+0}')
echo "Zombie processes: $ZOMBIE_COUNT"

# List zombies with parent
ps -eo pid,ppid,stat,comm | awk '$3 ~ /^Z/'

# D-state (uninterruptible sleep) processes
DSTATE_COUNT=$(ps aux | awk '$8 ~ /^D/ {count++} END {print count+0}')
echo "D-state processes: $DSTATE_COUNT"
ps -eo pid,stat,wchan,comm | awk '$2 ~ /^D/'

# Total process count vs limit
echo "Total processes: $(ps -e --no-headers | wc -l)"
sysctl kernel.pid_max
```

**Judgment rules**:
- Zombie count > 10 → **OpenClaw.Process.ZombieProcessesHigh** (WARNING)
  - Remediation: Identify parent processes (`ps -eo pid,ppid,stat,comm | awk '$3~/Z/'`); the parent is not reaping children — restart or fix the parent process
- D-state process count > 0 → **OpenClaw.Process.DStateProcessesFound** (CRITICAL)
  - Remediation: D-state processes are blocked on I/O — check disk health (`dmesg | grep -i error`), NFS mounts (`mount -t nfs`), and storage subsystem; these processes cannot be killed normally
- Total process count > 80% of `kernel.pid_max` → **OpenClaw.Process.TotalProcessCountHigh** (WARNING)
  - Remediation: Identify process-spawning storms (`ps -eo user --sort=user | uniq -c | sort -rn | head`); increase `kernel.pid_max` if needed

---

## 11. Systemd Journal & Log Disk Usage

Systemd journal grows unbounded on long-running servers, silently consuming disk space — a common hidden root cause of "disk full" events.

```bash
# Journal disk usage
journalctl --disk-usage 2>/dev/null

# Journal retention config
grep -E 'SystemMaxUse|SystemKeepFree|MaxRetentionSec' /etc/systemd/journald.conf 2>/dev/null

# /var/log total size
du -sh /var/log/ 2>/dev/null

# Largest log files
find /var/log -type f -size +100M 2>/dev/null | head -10
```

**Judgment rules**:
- Journal disk usage > 2 GB → **OpenClaw.Logs.JournalDiskUsageHigh** (WARNING)
  - Remediation: `journalctl --vacuum-size=500M`; set `SystemMaxUse=500M` in `/etc/systemd/journald.conf` and restart `systemd-journald`
- `/var/log` total size > 5 GB → **OpenClaw.Logs.VarLogOversized** (WARNING)
  - Remediation: Identify large files (`find /var/log -type f -size +100M`); configure logrotate; clean old rotated logs

---

## 12. Filesystem Integrity

Read-only filesystem (from ext4/xfs journal errors) prevents writing session data, logs, and PID files. Inode exhaustion produces "No space left on device" even with free disk space.

```bash
# Read-only filesystem detection (exclude virtual filesystems)
mount | grep -E '\bro\b' | grep -v 'proc\|sys\|cgroup\|tmpfs\|squashfs\|snap'

# Filesystem errors in dmesg
dmesg | grep -iE 'EXT4-fs error|XFS.*error|remount.*read-only|I/O error' | tail -10

# Inode usage — high inode consumption on any filesystem
df -ih | awk 'NR>1 && $5 ~ /%/ {gsub(/%/,"",$5); if ($5+0 >= 80) print}'

# Write test (self-cleaning)
touch /tmp/.oc_write_test 2>/dev/null && rm -f /tmp/.oc_write_test && echo "Write OK" || echo "Write FAILED"
```

**Judgment rules**:
- Any non-virtual mount has `ro` flag, or `/tmp` write test fails → **OpenClaw.Disk.ReadOnlyFilesystem** (CRITICAL)
  - Remediation: Check `dmesg` for filesystem errors; run `fsck` on the affected partition (requires unmount or single-user mode); may indicate disk hardware failure
- Any real filesystem inode usage >= 80% → **OpenClaw.Disk.InodeUsageHigh** (WARNING)
  - Remediation: Find directories with many small files (`find / -xdev -printf '%h\n' | sort | uniq -c | sort -rn | head -10`); clean up session/temp files
- `dmesg` contains EXT4-fs error, XFS error, or read-only remount messages → **OpenClaw.Disk.FilesystemErrorsDetected** (CRITICAL)
  - Remediation: Back up data immediately; run `fsck` at next maintenance window; check disk SMART status (`smartctl -a /dev/sdX`)

---

## 13. Firewall & Outbound Connectivity

Firewall rules blocking inbound or outbound traffic are the #1 cause of "port not reachable" and "API connection refused" in self-hosted deployments.

```bash
# iptables DROP/REJECT rules on INPUT and OUTPUT
iptables -L INPUT -n --line-numbers 2>/dev/null | grep -iE 'DROP|REJECT'
iptables -L OUTPUT -n --line-numbers 2>/dev/null | grep -iE 'DROP|REJECT'

# nftables (modern replacement for iptables)
nft list ruleset 2>/dev/null | grep -iE 'drop|reject' | head -10

# ufw status
ufw status 2>/dev/null

# Outbound HTTPS connectivity test (generic target)
# timeout 5 bash -c 'echo >/dev/tcp/1.1.1.1/443' 2>/dev/null && echo "Outbound 443 OK" || echo "Outbound 443 BLOCKED"

# Outbound HTTP connectivity test
# timeout 5 bash -c 'echo >/dev/tcp/1.1.1.1/80' 2>/dev/null && echo "Outbound 80 OK" || echo "Outbound 80 BLOCKED"
```

**Judgment rules**:
- DROP or REJECT rules detected on INPUT or OUTPUT chains → **OpenClaw.Network.FirewallDropRulesDetected** (WARNING)
  - Remediation: Review rules — ensure required ports (gateway port, 443 outbound) are allowed; use `iptables -L -n -v` for detailed hit counts
<!-- - Outbound TCP connect to external port 443 fails → **OpenClaw.Network.OutboundHTTPSBlocked** (ERROR)
  - Remediation: Check OUTPUT chain rules; verify cloud security group allows outbound 443; check if proxy is required (`HTTP_PROXY`/`HTTPS_PROXY`) -->
- `ufw status` shows default deny incoming (informational only) → **OpenClaw.Network.UFWDefaultDeny** (INFO)
  - Remediation: No action required if intentional; ensure gateway port is explicitly allowed (`ufw allow <port>/tcp`)

---

## 14. Transparent Hugepages

THP causes latency spikes and memory fragmentation for Node.js workloads. Multiple database and runtime vendors recommend disabling it on servers.

```bash
# THP status
cat /sys/kernel/mm/transparent_hugepage/enabled 2>/dev/null

# THP defrag status
cat /sys/kernel/mm/transparent_hugepage/defrag 2>/dev/null

# Current AnonHugePages usage
grep AnonHugePages /proc/meminfo 2>/dev/null
```

**Judgment rules**:
- THP `enabled` is set to `[always]` → **OpenClaw.Kernel.THPEnabled** (WARNING)
  - Remediation: `echo never > /sys/kernel/mm/transparent_hugepage/enabled`; persist via systemd unit or `/etc/rc.local`
- THP `defrag` is set to `[always]` → **OpenClaw.Kernel.THPDefragEnabled** (INFO)
  - Remediation: `echo never > /sys/kernel/mm/transparent_hugepage/defrag`; reduces latency spikes from compaction

---

## 15. TCP Connection Overload

Excessive network connections exhaust file descriptors, memory, and conntrack table capacity, degrading system-wide performance.

```bash
# Total TCP connections by state
ss -ant | awk 'NR>1 {state[$1]++} END {for (s in state) print s, state[s]}' | sort -k2 -rn

# Total TCP connection count
ss -ant | tail -n +2 | wc -l

# CLOSE_WAIT connections (application not closing sockets properly)
CLOSE_WAIT_COUNT=$(ss -ant state close-wait | tail -n +2 | wc -l)
echo "CLOSE_WAIT connections: $CLOSE_WAIT_COUNT"

# CLOSE_WAIT by process (identify leaking applications)
ss -antp state close-wait 2>/dev/null | awk '{print $NF}' | sort | uniq -c | sort -rn | head -10

# ESTABLISHED connections count
ESTAB_COUNT=$(ss -ant state established | tail -n +2 | wc -l)
echo "ESTABLISHED connections: $ESTAB_COUNT"

# Top processes by connection count
ss -antp 2>/dev/null | awk -F'"' '{print $2}' | sort | uniq -c | sort -rn | head -10

# Ephemeral port range and usage
sysctl net.ipv4.ip_local_port_range
ss -ant | awk 'NR>1 {split($4,a,":"); if(a[length(a)]>=32768) count++} END {print "Ephemeral ports in use:", count+0}'
```

**Judgment rules**:
- Total TCP connections > 10000 → **OpenClaw.Network.TcpConnectionCountHigh** (WARNING)
  - Remediation: Identify top connection-holding processes; check for connection leaks; consider connection pooling
- CLOSE_WAIT count > 500 → **OpenClaw.Network.CloseWaitAccumulation** (ERROR)
  - Remediation: CLOSE_WAIT indicates the local application is not calling `close()` on sockets — identify the leaking process and restart it; this is an application bug
- ESTABLISHED count > 5000 → **OpenClaw.Network.EstablishedConnectionsHigh** (WARNING)
  - Remediation: Review whether all connections are legitimate; check for connection pool exhaustion or slow clients holding connections open
- Ephemeral ports in use > 80% of available range → **OpenClaw.Network.EphemeralPortExhaustion** (CRITICAL)
  - Remediation: Widen range `sysctl -w net.ipv4.ip_local_port_range='1024 65535'`; enable `tcp_tw_reuse`; check for connection leaks

---

## 16. Headless Browser / Chromium Dependencies

OpenClaw skills that use browser automation (Playwright, Puppeteer) require Chromium shared libraries and a display server or headless mode. Missing `.so` files produce cryptic "error while loading shared libraries" failures, and disabled user namespaces cause sandbox errors.

```bash
# Locate chromium binaries (system-installed and Playwright-bundled)
which chromium chromium-browser google-chrome google-chrome-stable 2>/dev/null
find /root/.cache/ms-playwright -name chrome -type f 2>/dev/null | head -3

# Check critical shared libraries required by Chromium
LDCONFIG_BIN=$(which ldconfig 2>/dev/null || echo "/sbin/ldconfig")
for lib in libnss3.so libatk-bridge-2.0.so libgbm.so libxkbcommon.so \
           libdrm.so libgtk-3-0.so libasound.so.2; do
    $LDCONFIG_BIN -p 2>/dev/null | grep -q "$lib" && echo "$lib OK" || echo "$lib MISSING"
done

# ldd on found chromium binary (detect unresolvable dynamic links)
CHROME_BIN=$(which chromium chromium-browser google-chrome 2>/dev/null | head -1)
[ -z "$CHROME_BIN" ] && CHROME_BIN=$(find /root/.cache/ms-playwright -name chrome -type f 2>/dev/null | head -1)
[ -n "$CHROME_BIN" ] && ldd "$CHROME_BIN" 2>/dev/null | grep 'not found'

# User namespace clone support (Chrome sandbox requirement)
cat /proc/sys/kernel/unprivileged_userns_clone 2>/dev/null || echo "sysctl not present (likely allowed)"
```

**Judgment rules**:
- Any of the 7 critical shared libraries is absent from `ldconfig -p` → **OpenClaw.Browser.ChromiumDependenciesMissing** (ERROR)
  - Remediation: On Debian/Ubuntu: `apt install -y libnss3 libatk-bridge2.0-0 libgbm1 libxkbcommon0 libdrm2 libgtk-3-0 libasound2`; on RHEL/CentOS: `yum install -y nss atk at-spi2-atk mesa-libgbm libxkbcommon libdrm gtk3 alsa-lib`
- `ldd` on found chromium binary shows one or more "not found" entries → **OpenClaw.Browser.ChromiumBinaryLddFailures** (CRITICAL)
  - Remediation: Install the specific missing libraries identified by `ldd`; run `ldconfig` after installation to update the dynamic linker cache
- `/proc/sys/kernel/unprivileged_userns_clone` is `0` → **OpenClaw.Browser.UserNamespaceDisabled** (ERROR)
  - Remediation: `sysctl -w kernel.unprivileged_userns_clone=1` and persist in `/etc/sysctl.d/99-userns.conf`; or configure Chromium with `--no-sandbox` (less secure, not recommended for production)

---

## 17. Locale & Encoding Configuration

Missing or misconfigured locale causes garbled text output, incorrect sorting in logs, and subtle bugs like backspace deleting two characters over SSH (when client sends UTF-8 but server expects ASCII). OpenClaw's text processing relies on correct UTF-8 support.

```bash
# Resolve locale binary (may not be in non-root user's PATH)
LOCALE_BIN=$(command -v locale 2>/dev/null || echo /usr/bin/locale)
[ ! -x "$LOCALE_BIN" ] && echo "locale command not found" && LOCALE_BIN=""

# Current locale vars
[ -n "$LOCALE_BIN" ] && $LOCALE_BIN 2>/dev/null
echo "LANG=${LANG:-not set} LC_ALL=${LC_ALL:-not set} LC_CTYPE=${LC_CTYPE:-not set}"

# Available UTF-8 locales
[ -n "$LOCALE_BIN" ] && $LOCALE_BIN -a 2>/dev/null | grep -iE 'utf-?8' | head -20

# Check if configured locale is actually installed
# Note: LANG uses "en_US.UTF-8" but locale -a outputs "en_US.utf8", so normalize before comparison
CONFIGURED_LOCALE=$(echo "${LANG:-}")
if [ -n "$LOCALE_BIN" ] && [ -n "$CONFIGURED_LOCALE" ] && [ "$CONFIGURED_LOCALE" != "C" ] && [ "$CONFIGURED_LOCALE" != "POSIX" ]; then
  NORMALIZED=$(echo "$CONFIGURED_LOCALE" | sed 's/UTF-8/utf8/g')
  $LOCALE_BIN -a 2>/dev/null | grep -qiF "$NORMALIZED" && \
    echo "Locale $CONFIGURED_LOCALE installed" || echo "Locale $CONFIGURED_LOCALE NOT INSTALLED"
fi

# Persistent locale config
cat /etc/default/locale 2>/dev/null
cat /etc/locale.conf 2>/dev/null
```

**Judgment rules**:
- `LANG` is empty, unset, or set to `POSIX`/`C` → **OpenClaw.Locale.LocaleNotConfigured** (ERROR)
  - Remediation: On Debian/Ubuntu: `apt install locales && dpkg-reconfigure locales`, then set `LANG=en_US.UTF-8` in `/etc/default/locale`; on RHEL/CentOS: `localectl set-locale LANG=en_US.UTF-8`
- The `LANG` value does not appear in `locale -a` output (configured but not generated/installed) → **OpenClaw.Locale.LocaleNotGenerated** (WARNING)
  - Remediation: On Debian/Ubuntu: uncomment the locale in `/etc/locale.gen` and run `locale-gen`; on RHEL/CentOS: `localedef -i en_US -f UTF-8 en_US.UTF-8`
- `LANG` or `LC_CTYPE` does not contain `UTF-8` or `utf8` → **OpenClaw.Locale.NonUTF8LocaleDetected** (WARNING)
  - Remediation: Change to a UTF-8 variant: `localectl set-locale LANG=en_US.UTF-8`; re-login for the change to take effect

---

## Issue Name Registry

All issue types defined in this skill:

| # | Issue Name | Sev |
|---|-----------|-----|
| 1 | OpenClaw.System.EnvironmentBaseline | INFO |
| 2 | OpenClaw.Memory.SystemMemoryCritical | CRITICAL |
| 3 | OpenClaw.Memory.SystemMemoryLow | WARNING |
| 4 | OpenClaw.Memory.InsufficientTotalMemory | ERROR |
| 5 | OpenClaw.Memory.OOMKillerEvent | WARNING |
| 6 | OpenClaw.CPU.SystemLoadHigh | WARNING |
| 7 | OpenClaw.CPU.SystemCPUExhausted | CRITICAL |
| 8 | OpenClaw.CPU.HighIOWait | WARNING |
| 9 | OpenClaw.Network.IPv6Mismatch | WARNING |
| 10 | OpenClaw.Disk.FilesystemFull | CRITICAL |
| 11 | OpenClaw.Disk.FilesystemHighUsage | WARNING |
| 12 | OpenClaw.Disk.InotifyWatchesTooLow | ERROR |
| 13 | OpenClaw.Disk.InotifyInstancesTooLow | WARNING |
| 14 | OpenClaw.Limits.NofileTooLow | ERROR |
| 15 | OpenClaw.Limits.NofileExceedsKernelMax | CRITICAL |
| 16 | OpenClaw.Limits.SystemFileDescriptorsHigh | WARNING |
| 17 | OpenClaw.Kernel.NfConntrackMaxTooLow | ERROR |
| 18 | OpenClaw.Kernel.NfConntrackTableFull | CRITICAL |
| 19 | OpenClaw.Kernel.SomaxconnTooLow | WARNING |
| 20 | OpenClaw.Kernel.TcpMaxTwBucketsTooLow | WARNING |
| 21 | OpenClaw.Kernel.TcpTwReuseNotEnabled | WARNING |
| 22 | OpenClaw.Kernel.TimeWaitOverflow | WARNING |
| 23 | OpenClaw.Kernel.TcpListenOverflows | WARNING |
| 24 | OpenClaw.Kernel.StrictOvercommitWithLowSwap | WARNING |
| 25 | OpenClaw.Network.NoDNSNameservers | ERROR |
| 26 | OpenClaw.Network.DNSResolutionFailed | CRITICAL |
| 27 | OpenClaw.Network.DNSNameserverUnreachable | WARNING |
| 28 | OpenClaw.Time.NTPServiceNotRunning | ERROR |
| 29 | OpenClaw.Time.ClockNotSynchronized | CRITICAL |
| 30 | OpenClaw.Time.ClockDriftDetected | WARNING |
| 31 | OpenClaw.Process.ZombieProcessesHigh | WARNING |
| 32 | OpenClaw.Process.DStateProcessesFound | CRITICAL |
| 33 | OpenClaw.Process.TotalProcessCountHigh | WARNING |
| 34 | OpenClaw.Logs.JournalDiskUsageHigh | WARNING |
| 35 | OpenClaw.Logs.VarLogOversized | WARNING |
| 36 | OpenClaw.Disk.ReadOnlyFilesystem | CRITICAL |
| 37 | OpenClaw.Disk.InodeUsageHigh | WARNING |
| 38 | OpenClaw.Disk.FilesystemErrorsDetected | CRITICAL |
| 39 | OpenClaw.Network.FirewallDropRulesDetected | WARNING |
<!-- | 40 | OpenClaw.Network.OutboundHTTPSBlocked | ERROR | -->
| 41 | OpenClaw.Network.UFWDefaultDeny | INFO |
| 42 | OpenClaw.Kernel.THPEnabled | WARNING |
| 43 | OpenClaw.Kernel.THPDefragEnabled | INFO |
| 44 | OpenClaw.Network.TcpConnectionCountHigh | WARNING |
| 45 | OpenClaw.Network.CloseWaitAccumulation | ERROR |
| 46 | OpenClaw.Network.EstablishedConnectionsHigh | WARNING |
| 47 | OpenClaw.Network.EphemeralPortExhaustion | CRITICAL |
| 48 | OpenClaw.Browser.ChromiumDependenciesMissing | ERROR |
| 49 | OpenClaw.Browser.ChromiumBinaryLddFailures | CRITICAL |
| 50 | OpenClaw.Browser.UserNamespaceDisabled | ERROR |
| 51 | OpenClaw.Locale.LocaleNotConfigured | ERROR |
| 52 | OpenClaw.Locale.LocaleNotGenerated | WARNING |
| 53 | OpenClaw.Locale.NonUTF8LocaleDetected | WARNING |

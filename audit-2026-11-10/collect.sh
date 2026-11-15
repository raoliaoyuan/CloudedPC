#!/bin/bash
export LC_ALL=C
section() { printf '\n### %s ###\n' "$1"; }
section IDENTITY
date -Is; hostname; id; uname -a; cat /etc/os-release; uptime; systemd-detect-virt; ps -p 1 -o pid,comm; timedatectl 2>&1
section CPU
lscpu; nproc; nproc --all; taskset -pc $$; cat /sys/fs/cgroup/cpu.max /sys/fs/cgroup/cpu.stat /sys/fs/cgroup/cpuset.cpus.effective 2>/dev/null
section MEMORY
free -b; cat /sys/fs/cgroup/memory.max /sys/fs/cgroup/memory.current /sys/fs/cgroup/memory.peak /sys/fs/cgroup/memory.events /sys/fs/cgroup/memory.swap.max /sys/fs/cgroup/memory.swap.current 2>/dev/null
cat /proc/pressure/cpu /proc/pressure/memory /proc/pressure/io
section STORAGE
lsblk -e 7 -o NAME,TYPE,SIZE,FSTYPE,ROTA,MODEL,MOUNTPOINTS; df -hT; df -i; findmnt -o TARGET,SOURCE,FSTYPE,OPTIONS / /workspace /data /home /root 2>/dev/null
section DEVICES
command -v lspci >/dev/null && lspci; ls -ld /dev/dri /dev/nvidia* /dev/kvm /dev/net/tun /var/run/docker.sock 2>/dev/null
command -v nvidia-smi >/dev/null && nvidia-smi
for f in /sys/class/dmi/id/sys_vendor /sys/class/dmi/id/product_name /sys/class/dmi/id/board_vendor; do test -r "$f" && { printf '%s: ' "$f"; cat "$f"; }; done
section PERFORMANCE
vmstat 1 6; ps -eo pid,ppid,user,comm,%cpu,%mem,rss --sort=-rss | head -22
section NETWORK
ip -br address; ip route; ip -6 route; cat /etc/resolv.conf; ss -lntup; ip -s link
section SERVICES
systemctl --failed --no-pager; systemctl list-units --type=service --state=running --no-pager; systemctl list-timers --all --no-pager; systemctl is-system-running
section SECURITY
/usr/sbin/sshd -T 2>/dev/null | awk '$1 ~ /^(permitrootlogin|passwordauthentication|pubkeyauthentication|kbdinteractiveauthentication|permitemptypasswords|x11forwarding|allowtcpforwarding|gatewayports|maxauthtries|usepam|listenaddress)$/'; passwd -S root
awk -F: '($3==0 || ($3>=1000 && $3<65534)){print $1, "uid=" $3, "shell=" $7}' /etc/passwd
command -v ufw >/dev/null && ufw status verbose
command -v nft >/dev/null && nft list ruleset 2>&1
command -v iptables >/dev/null && iptables -S 2>&1
cat /proc/self/status | awk '/^(Cap|NoNewPrivs|Seccomp)/'; cat /proc/sys/kernel/randomize_va_space /proc/sys/kernel/kptr_restrict /proc/sys/kernel/dmesg_restrict
command -v aa-status >/dev/null && aa-status 2>&1
section SOFTWARE
for c in python3 pip pip3 node npm git docker podman java go rustc cargo gcc g++ cmake make nginx tailscale ssh; do command -v "$c" 2>/dev/null; done
python3 --version; node --version; npm --version; git --version; tailscale version; ssh -V
command -v docker >/dev/null && docker version 2>&1
section PACKAGES
dpkg-query -W -f='${binary:Package}\t${Version}\n' 2>/dev/null | sort
section UPDATES
apt list --upgradable 2>/dev/null
find /var/lib/apt/lists -maxdepth 1 -type f -name '*InRelease' -printf '%TY-%Tm-%Td %TH:%TM %f\n'
test -f /var/run/reboot-required && cat /var/run/reboot-required
section LOG_COUNTS
journalctl --disk-usage 2>&1; journalctl -p 0..3 --since '-24 hours' --no-pager -o json 2>/dev/null | python3 -c 'import sys,json,collections; c=collections.Counter(); [c.update([json.loads(l).get("_SYSTEMD_UNIT", json.loads(l).get("SYSLOG_IDENTIFIER","unknown"))]) for l in sys.stdin]; print(c)'
section CGROUP_MOUNTS
findmnt -t cgroup2; cat /proc/self/cgroup; cat /sys/fs/cgroup/pids.max /sys/fs/cgroup/pids.current /sys/fs/cgroup/io.stat 2>/dev/null
section BOOT_FILES
for f in /root/.bashrc /root/.bash_profile /root/.profile /etc/profile /etc/bash.bashrc; do test -f "$f" && { printf '%s\n' "$f"; stat -c '%a %U %s %y' "$f"; }; done

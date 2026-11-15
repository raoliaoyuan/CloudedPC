#!/bin/bash
export LC_ALL=C
section() { printf '\n### %s ###\n' "$1"; }
section CGROUP_DETAIL
for d in /sys/fs/cgroup /sys/fs/cgroup/init.scope; do for f in cpu.max memory.max memory.current memory.peak memory.events cpu.stat cpu.pressure memory.pressure io.pressure memory.swap.max; do test -r "$d/$f" && { printf '%s\n' "$d/$f"; cat "$d/$f"; }; done; done
python3 - <<'PY'
import time,pathlib,json
p=pathlib.Path('/sys/fs/cgroup/cpu.stat')
def read():return dict((k,int(v)) for k,v in (l.split() for l in p.read_text().splitlines()))
a=read(); t=time.monotonic(); time.sleep(5); b=read(); elapsed=time.monotonic()-t
print('cpu_sample',json.dumps({'seconds':elapsed,'cores_used':(b['usage_usec']-a['usage_usec'])/1e6/elapsed,'throttled_periods_delta':b['nr_throttled']-a['nr_throttled'],'throttled_usec_delta':b['throttled_usec']-a['throttled_usec']}))
PY
section STORAGE_DETAIL
findmnt -T / -o TARGET,SOURCE,FSTYPE,OPTIONS; findmnt -T /root -o TARGET,SOURCE,FSTYPE; findmnt -T /workspace -o TARGET,SOURCE,FSTYPE; df -B1 / /root /tmp; ls -ld /workspace /data /home /root /dev/dri /dev/nvidia* /dev/kvm /dev/net/tun 2>&1
section TAILSCALE
tailscale status --json | python3 -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps({k:d.get(k) for k in ["Version","TUN","BackendState","TailscaleIPs","Health"]},indent=2)); s=d.get("Self",{}); print(json.dumps({k:s.get(k) for k in ["HostName","DNSName","Relay","Online","KeyExpiry"]},indent=2)); print(json.dumps([{k:p.get(k) for k in ["HostName","TailscaleIPs","CurAddr","Relay","Online","Active","RxBytes","TxBytes"]} for p in d.get("Peer",{}).values() if "100.82.31.127" in p.get("TailscaleIPs",[])],indent=2))'
tailscale debug prefs | python3 -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps({k:d.get(k) for k in ["WantRunning","RunSSH","ShieldsUp","CorpDNS","RouteAll","AdvertiseRoutes","ExitNodeID","NetfilterMode"]},indent=2))'
timeout 20 tailscale netcheck 2>&1
tailscale serve status; tailscale funnel status
section SSH_EFFECTIVE
/usr/sbin/sshd -t 2>&1; /usr/sbin/sshd -T -C user=root,host=steam-os,addr=100.82.31.127 | awk '$1 ~ /^(permitrootlogin|passwordauthentication|pubkeyauthentication|authenticationmethods|authorizedkeysfile|allowusers|denyusers|allowgroups|denygroups|forcecommand|usepam)$/'; stat -c '%a %U %n' /root/.ssh /root/.ssh/authorized_keys 2>/dev/null
section FIREWALL
command -v iptables-legacy >/dev/null && iptables-legacy -S 2>&1
command -v supervisorctl >/dev/null && supervisorctl status 2>&1
docker info --format '{{json .}}' | python3 -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps({k:d.get(k) for k in ["ServerVersion","Containers","ContainersRunning","Images","Driver","CgroupDriver","CgroupVersion","NCPU","MemTotal","DockerRootDir","SecurityOptions","Warnings"]},indent=2))'
docker ps --format '{{.Image}}\t{{.Status}}\t{{.Ports}}'
section INIT_REFERENCES
python3 - <<'PY'
import pathlib,re
paths=[pathlib.Path(p) for p in ['/root/.bashrc','/root/.profile','/etc/profile','/etc/bash.bashrc']]+list(pathlib.Path('/etc/profile.d').glob('*.sh'))
for p in paths:
 if p.exists():
  for n,l in enumerate(p.read_text(errors='replace').splitlines(),1):
   if re.search(r'pyenv|nvm|yargs|mv |node|npm|eval|source |^\s*\. ',l):
    if re.search(r'token|password|secret|api.key|credential',l,re.I): l='[redacted sensitive line]'
    print(f'{p}:{n}: {l}')
print('NVM installed', [p.name for p in pathlib.Path('/root/.nvm/versions/node').glob('*')])
print('pyenv executable',pathlib.Path('/root/.pyenv/bin/pyenv').exists())
for p in pathlib.Path('/root/.nvm/versions/node').glob('*/lib/node_modules/*/package.json'):
 try:
  import json
  d=json.loads(p.read_text()); print('GLOBAL_NPM',d.get('name'),d.get('version'),d.get('engines'))
 except Exception:pass
for p in pathlib.Path('/root/.nvm/versions/node').glob('*/lib/node_modules/@*/*/package.json'):
 try:
  d=json.loads(p.read_text()); print('GLOBAL_NPM',d.get('name'),d.get('version'),d.get('engines'))
 except Exception:pass
PY
section PYTHON_PACKAGES
python3 -m pip list --format=json 2>/dev/null
section DESKTOP
ps -eo comm | sort -u | grep -Ei 'xorg|xvfb|vnc|rdp|gnome|xfce|chrome|wayland|pipewire|pulse|cron|supervisor|sshd'
section APT_SUMMARY
python3 - <<'PY'
import apt,json
c=apt.Cache(); u=[p for p in c if p.is_upgradable]
s=[p for p in u if any(o.archive=='noble-security' for o in p.candidate.origins)]
print(json.dumps({'installed':sum(p.is_installed for p in c),'upgradable':len(u),'candidates_in_security':len(s),'held':[p.name for p in c if p.is_installed and p._pkg.selected_state==2]},indent=2))
PY
section BACKUP_INDICATORS
for c in restic borg duplicity rclone crontab; do command -v "$c"; done
find /etc/cron.d /etc/cron.daily -maxdepth 1 -type f -printf '%f\n' 2>/dev/null
section CLOCK
 date -Is; readlink /etc/localtime; cat /proc/uptime

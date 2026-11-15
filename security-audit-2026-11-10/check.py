import subprocess,pathlib,json,re,os,stat,collections

def run(cmd,timeout=15):
 print('\n$', ' '.join(cmd), flush=True)
 try:
  r=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout)
  print(r.stdout[:25000]);print(r.stderr[:2500] if r.stderr else '',end='')
 except Exception as e: print(type(e).__name__)
def read(p):
 try:return pathlib.Path(p).read_text().strip()
 except OSError:return '[unavailable]'
def sec(t):print('\n###',t,'###',flush=True)
sec('IDENTITY');run(['date','-Is']);run(['hostname']);run(['id'])
sec('SSH')
r=subprocess.run(['/usr/sbin/sshd','-T'],capture_output=True,text=True)
keys={'permitrootlogin','passwordauthentication','pubkeyauthentication','kbdinteractiveauthentication','permitemptypasswords','authenticationmethods','usepam','maxauthtries','maxstartups','loglevel','syslogfacility','allowtcpforwarding','allowagentforwarding','x11forwarding','gatewayports','permituserenvironment','permituserrc','strictmodes','allowusers','allowgroups','denyusers','denygroups','authorizedkeyscommand','authorizedkeysfile','listenaddress'}
print('\n'.join(l for l in r.stdout.splitlines() if l.split()[0] in keys))
run(['/usr/sbin/sshd','-t'])
sec('ACCOUNT_AND_SUDO')
users=[]
for l in read('/etc/passwd').splitlines():
 f=l.split(':')
 if len(f)==7 and (int(f[2])==0 or (1000<=int(f[2])<65534)):
  users.append(f[0]);print({'user':f[0],'uid':f[2],'gid':f[3],'home':f[5],'shell':f[6]})
for u in users:run(['passwd','-S',u])
for l in read('/etc/group').splitlines():
 if l.split(':')[0] in ['sudo','docker','adm','shadow']:print(l)
for base in ['/etc/sudoers','/etc/sudoers.d']:
 p=pathlib.Path(base);files=list(p.glob('*')) if p.is_dir() else [p]
 for f in files:
  if f.is_file():
   for n,l in enumerate(read(f).splitlines(),1):
    if l.strip() and not l.lstrip().startswith('#'):print(str(f),n,l)
sec('TAILSCALE')
for sub in [['status','--json'],['debug','prefs']]:
 r=subprocess.run(['tailscale']+sub,capture_output=True,text=True)
 try:
  a=json.loads(r.stdout)
  if sub[0]=='status':
   print({k:a.get(k) for k in ['Version','BackendState','TUN','Health']})
   print('Self',{k:a.get('Self',{}).get(k) for k in ['HostName','Online','KeyExpiry']})
  else:print({k:a.get(k) for k in ['RunSSH','ShieldsUp','AdvertiseRoutes','ExitNodeID','CorpDNS','RouteAll','AutoUpdate','NoStatefulFiltering']})
 except Exception:print('unable to parse')
run(['tailscale','serve','status']);run(['tailscale','funnel','status'])
sec('FIREWALL_AND_LISTENERS')
for cmd in [['ss','-lntup'],['iptables','-S'],['iptables-legacy','-S'],['ip6tables','-S'],['nft','list','ruleset']]:run(cmd)
sec('CONTAINER_ISOLATION')
for path in ['/proc/self/uid_map','/proc/self/gid_map','/proc/self/attr/current','/sys/kernel/security/lsm','/sys/module/apparmor/parameters/enabled','/proc/sys/kernel/cap_last_cap','/proc/sys/kernel/randomize_va_space','/proc/sys/kernel/kptr_restrict','/proc/sys/kernel/dmesg_restrict']:
 print(path,read(path))
capnames=['CHOWN','DAC_OVERRIDE','DAC_READ_SEARCH','FOWNER','FSETID','KILL','SETGID','SETUID','SETPCAP','LINUX_IMMUTABLE','NET_BIND_SERVICE','NET_BROADCAST','NET_ADMIN','NET_RAW','IPC_LOCK','IPC_OWNER','SYS_MODULE','SYS_RAWIO','SYS_CHROOT','SYS_PTRACE','SYS_PACCT','SYS_ADMIN','SYS_BOOT','SYS_NICE','SYS_RESOURCE','SYS_TIME','SYS_TTY_CONFIG','MKNOD','LEASE','AUDIT_WRITE','AUDIT_CONTROL','SETFCAP','MAC_OVERRIDE','MAC_ADMIN','SYSLOG','WAKE_ALARM','BLOCK_SUSPEND','AUDIT_READ','PERFMON','BPF','CHECKPOINT_RESTORE']
for pid in ['self','1']:
 for l in read('/proc/'+pid+'/status').splitlines():
  if l.startswith(('CapEff:','CapBnd:','NoNewPrivs:','Seccomp:','Seccomp_filters:')):
   print(pid,l)
   if l.startswith('CapEff:'):
    x=int(l.split()[1],16);print('effective',[v for i,v in enumerate(capnames) if x&(1<<i)])
print('namespace IDs',{n:os.readlink('/proc/self/ns/'+n) for n in ['user','pid','mnt','net','cgroup']})
run(['findmnt','-T','/sys/fs/cgroup','-o','TARGET,FSTYPE,OPTIONS'])
run(['findmnt','-T','/proc','-o','TARGET,FSTYPE,OPTIONS'])
sec('DOCKER')
r=subprocess.run(['docker','info','--format','{{json .}}'],capture_output=True,text=True)
try:
 a=json.loads(r.stdout);print({k:a.get(k) for k in ['ServerVersion','Containers','ContainersRunning','SecurityOptions','LiveRestoreEnabled','LoggingDriver','CgroupDriver','Warnings']})
except Exception:print('unavailable')
run(['docker','ps','--format','{{.Image}}\t{{.Status}}\t{{.Ports}}'])
sec('PERMISSIONS_ONLY')
for path in ['/var/run/docker.sock','/var/run/tailscale/tailscaled.sock','/var/lib/tailscale','/var/lib/tailscale/tailscaled.state','/root/.ssh','/etc/ssh/sshd_config','/etc/shadow','/root/.aws','/root/.config','/workspace']:
 p=pathlib.Path(path)
 try:
  s=p.stat();print(path,oct(stat.S_IMODE(s.st_mode)),s.st_uid,s.st_gid)
 except OSError:print(path,'absent')
for p in pathlib.Path('/etc/ssh').glob('ssh_host_*_key'):
 s=p.stat();print(str(p),oct(stat.S_IMODE(s.st_mode)),s.st_uid)
sec('SECURITY_AGENTS_AND_LOGGING')
procs=collections.Counter()
for p in pathlib.Path('/proc').glob('[0-9]*/comm'):
 try:procs[p.read_text().strip()]+=1
 except OSError:pass
print({k:v for k,v in procs.items() if re.search(r'fail2ban|audit|rsyslog|syslog|journal|clam|aegis|yunjing|qcloud|falco|wazuh|ossec|tetragon|log|supervis|tailscale|sshd|cron',k,re.I)})
for name in ['fail2ban','auditd','rsyslog','unattended-upgrades','ufw','apparmor','libpam-pwquality','libpam-modules','sudo','tailscale']:
 run(['dpkg-query','-W','-f=${binary:Package}\t${db:Status-Status}\t${Version}\n',name])
for p in ['/var/log/auth.log','/var/log/syslog','/var/log/audit/audit.log','/var/log/btmp','/var/log/wtmp','/var/log/journal']:
 f=pathlib.Path(p);print(p,{'exists':f.exists(),'bytes':f.stat().st_size if f.exists() else None})
run(['lastb','-n','5','-w'])
sec('UPDATE_POLICY')
for p in pathlib.Path('/etc/apt/apt.conf.d').glob('*'):
 if p.is_file():
  for l in read(p).splitlines():
   if re.search(r'APT::Periodic|Unattended-Upgrade::',l) and not l.strip().startswith('//'):print(p.name,l)
for p in ['/etc/pam.d/sshd','/etc/pam.d/common-auth','/etc/pam.d/common-password','/etc/pam.d/common-account']:
 for l in read(p).splitlines():
  if l.strip() and not l.strip().startswith('#'):print(p,l)
try:
 import apt
 c=apt.Cache();up=[p for p in c if p.is_upgradable]
 print('APT',{'upgradable':len(up),'security_candidates':sum(any(o.archive=='noble-security' for o in p.candidate.origins) for p in up)})
except Exception as e:print(type(e).__name__)
sec('BACKUP_CONFIG_METADATA')
for root in ['/etc/cron.d','/etc/cron.daily','/var/spool/cron/crontabs']:
 p=pathlib.Path(root)
 if p.exists():print(root,[x.name for x in p.iterdir()])
sec('RESOURCE_GUARDS')
for f in ['cpu.max','memory.max','memory.events','pids.max','pids.current']:
 print(f,read('/sys/fs/cgroup/'+f))
print('END')

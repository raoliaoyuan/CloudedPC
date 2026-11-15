import pathlib,subprocess,configparser,re,json,os

def safe_arg(a):
 a=re.sub(r'(https?://)[^/@\s]+:[^/@\s]+@',r'\1[redacted]@',a)
 a=re.sub(r'(?i)((?:token|password|secret|api[-_]?key|auth[-_]?key)\s*[=:]\s*)[^\s]+',r'\1[redacted]',a)
 return a
print('TIME',subprocess.check_output(['date','-Is'],text=True).strip())
procs=[]
for p in pathlib.Path('/proc').glob('[0-9]*'):
 try:
  name=(p/'comm').read_text().strip()
  status=(p/'status').read_text()
  ppid=re.search(r'^PPid:\s+(\d+)',status,re.M).group(1)
  args=(p/'cmdline').read_bytes().decode(errors='replace').split('\0')
  if name not in ['python3','bash','ssh','timeout','login','tail','nc','log-forward-tee']:
   clean=[];skip=False
   for a in args:
    if skip:clean.append('[redacted]');skip=False;continue
    if re.search(r'(?i)^--?(?:token|password|secret|api[-_]?key|auth[-_]?key)$',a):clean.append(a);skip=True
    elif a.startswith('--remote-user='):clean.append('--remote-user=[redacted]')
    elif not a.startswith('--cmd='):clean.append(safe_arg(a))
   if name=='tailscaled' and 'be-child' in args:clean=['[Tailscale SSH session child]']
   procs.append({'pid':int(p.name),'ppid':int(ppid),'name':name,'exe':os.readlink(p/'exe'),'args':clean})
 except (OSError,AttributeError):pass
print('PROCESSES');print(json.dumps(procs,indent=2,ensure_ascii=False))
main=None;superbin=None
for p in procs:
 if p['name']=='supervisord':
  args=p['args'];main=args[args.index('-c')+1];superbin=p['exe']
print('SUPERVISOR_MAIN',main)
paths=[pathlib.Path(main)] if main else []
if main:paths+=list(pathlib.Path(main).parent.glob('*.conf'))
paths+=list(pathlib.Path('/usr/local/share/supervisor').glob('*.conf'))
print('SUPERVISOR_CONFIG')
for path in dict.fromkeys(paths):
 c=configparser.RawConfigParser(strict=False)
 try:c.read(path)
 except Exception as e:print(path,type(e).__name__);continue
 for sec in c.sections():
  if sec.startswith(('program:','group:','eventlistener:')) or sec=='include':
   a={'file':str(path),'section':sec}
   for key in ['command','autostart','autorestart','startsecs','startretries','priority','user','directory','stdout_logfile','stderr_logfile','redirect_stderr','files','programs']:
    if c.has_option(sec,key):a[key]=safe_arg(c.get(sec,key))
   print(json.dumps(a,ensure_ascii=False))
if main and superbin:
 ctl=pathlib.Path(superbin).parent/'supervisorctl'
 if ctl.exists():
  r=subprocess.run([str(ctl),'-c',main,'status'],capture_output=True,text=True,timeout=15)
  print('SUPERVISOR_STATUS',r.stdout,r.stderr)
print('PORTS')
r=subprocess.run(['ss','-lntup'],capture_output=True,text=True);print(r.stdout)
print('PROCESS_STARTS')
r=subprocess.run(['ps','-eo','pid,ppid,lstart,comm'],capture_output=True,text=True);print(r.stdout)
print('PM2_READONLY_SOCKET_STATUS')
p=pathlib.Path('/root/.pm2/pm2.pid')
print('pm2_pid_file',p.read_text().strip() if p.exists() else 'absent')
# Never run pm2 CLI here: it may start a daemon. Read persisted metadata only.
p=pathlib.Path('/root/.pm2/dump.pm2')
if p.exists():
 try:
  arr=json.loads(p.read_text());print([{k:a.get(k) for k in ['name','pm_exec_path','exec_interpreter','autorestart','status']} for a in arr])
 except Exception as e:print(type(e).__name__)
print('SYSTEMD_NOT_INIT')
print(pathlib.Path('/proc/1/comm').read_text())

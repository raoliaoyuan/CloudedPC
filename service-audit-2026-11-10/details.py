import os,pathlib,configparser,re,json,glob,socket,http.client,xmlrpc.client
pid='61'
env={}
for chunk in pathlib.Path('/proc/'+pid+'/environ').read_bytes().split(b'\0'):
 if chunk.startswith(b'IDE_EDITOR_SERVER_DIR='):env['ENV_IDE_EDITOR_SERVER_DIR']=chunk.split(b'=',1)[1].decode()
base=pathlib.Path(env['ENV_IDE_EDITOR_SERVER_DIR']);conf=base/'supervisord-conf/supervisord.conf'
c=configparser.RawConfigParser(strict=False);c.read(conf)
paths=[conf]
for pat in (c.get('include','files')%env).split():paths.extend(pathlib.Path(p) for p in glob.glob(pat))
print('EFFECTIVE_CONFIG_FILES',[str(p) for p in paths]);c.read([str(p) for p in paths])
print('EFFECTIVE_PROGRAMS')
for s in c.sections():
 if s.startswith('program:'):
  print(s,{k:c.get(s,k,fallback=v) for k,v in [('autostart','true (Supervisor default)'),('autorestart','unexpected (Supervisor default)'),('startsecs','1 (Supervisor default)'),('priority','999 (Supervisor default)')]})
raw=c.get('supervisorctl','serverurl')%env
print('SUPERVISOR_SERVER_TYPE',raw.split(':')[0])
if raw.startswith('unix://') and pathlib.Path(raw[7:]).exists():
 sockpath=raw[7:]
 class UnixHTTP(http.client.HTTPConnection):
  def connect(self):
   self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.sock.settimeout(10);self.sock.connect(sockpath)
 conn=UnixHTTP('localhost')
 body=xmlrpc.client.dumps((),methodname='supervisor.getAllProcessInfo')
 conn.request('POST','/RPC2',body,{'Content-Type':'text/xml'})
 res=conn.getresponse();payload=res.read()
 try:
  data,_=xmlrpc.client.loads(payload)
  print('LIVE_SUPERVISOR_STATUS',json.dumps([{k:x.get(k) for k in ['name','group','statename','pid','start','stop','exitstatus','spawnerr']} for x in data[0]],indent=2))
 except Exception as e:print('status_error',res.status,str(e)[:200])
print('STARTUP_SCRIPT_CONTENTS_REDACTED')
names=['start-terminal','start-api','start-proxy','start-e2b-envd','start-cbc.d','init-git-credential-helper','agent-init','start-sync-server','start-editor-sdk','start-sandbox-log-collector','start-vscode','log-forward-tee','init']
for name in names:
 p=base/'workspace-init'/name
 print('\nFILE',name)
 try:
  b=p.read_bytes()
  if b'\x00' in b[:4096]:print('[binary]');continue
  lines=b.decode(errors='replace').splitlines()
  for i,l in enumerate(lines,1):
   if re.search(r'token|password|secret|credential|api.?key|auth.?key|authorization',l,re.I):
    print(f'{i}: [credential-related line omitted]');continue
   if len(l)>900:l=l[:900]+' [truncated]'
   if i<=180:print(f'{i}: {l}')
  if len(lines)>180:print('[remaining lines omitted]',len(lines))
 except OSError as e:print(type(e).__name__)
print('PM2_SCRIPT_HINTS')
for p in [pathlib.Path('/root/proxy'),pathlib.Path('/root/.pm2')]:
 print(p,[x.name for x in p.iterdir()] if p.exists() else [])

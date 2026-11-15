import pathlib,re,json,subprocess,os
print('STARTUP FRAGMENTS')
for p in sorted(pathlib.Path('/root/.bashrc.d').glob('*')):
 if p.is_file() and p.stat().st_size<30000:
  print('\nFILE',p)
  for n,l in enumerate(p.read_text(errors='replace').splitlines(),1):
   if re.search(r'token|password|secret|api.?key|credential',l,re.I):l='[sensitive line omitted]'
   print(f'{n}: {l}')
print('\nNVM DEFAULT')
p=pathlib.Path('/root/.nvm/alias/default'); print(p.read_text() if p.exists() else 'none')
print('\nRUNTIME BINARIES')
for p in ['/usr/bin/node','/root/.nvm/versions/node/v22.13.1/bin/node','/root/.pyenv/bin/pyenv']:
 try:print(p,subprocess.run([p,'--version'],capture_output=True,text=True,timeout=8).stdout.strip())
 except Exception as e:print(type(e).__name__)
print('\nYARGS DEPENDENCIES')
for p in pathlib.Path('/root/.nvm/versions/node/v22.13.1/lib/node_modules').glob('*/node_modules/yargs/package.json'):
 d=json.loads(p.read_text());print(str(p),d.get('version'),d.get('type'),d.get('engines'))
for p in pathlib.Path('/root/.nvm/versions/node/v22.13.1/lib/node_modules').glob('@*/*/node_modules/yargs/package.json'):
 d=json.loads(p.read_text());print(str(p),d.get('version'),d.get('type'),d.get('engines'))
print('\nPYENV VERSIONS')
print([p.name for p in pathlib.Path('/root/.pyenv/versions').glob('*')]);p=pathlib.Path('/root/.pyenv/version');print(p.read_text() if p.exists() else 'none')
print('\nPROCESS START TIMES')
subprocess.run(['ps','-eo','pid,ppid,lstart,comm'])
print('\nSUPERVISOR CONFIG SECTIONS')
for base in ['/etc/supervisor','/etc/supervisord.d']:
 for p in pathlib.Path(base).rglob('*'):
  if p.is_file() and p.suffix in ['.conf','.ini']:
   for n,l in enumerate(p.read_text(errors='replace').splitlines(),1):
    if l.startswith('[') or re.match(r'^(autostart|autorestart|user|stdout_logfile|stderr_logfile)\s*=',l) or 'tailscale' in l:
     if re.search(r'auth.?key|token|password|secret',l,re.I):l='[sensitive line omitted]'
     print(str(p),n,l)
print('\nLOG FILE NAMES AND SIZES')
for base in ['/var/log','/root/.pm2/logs']:
 for p in pathlib.Path(base).glob('*'):
  if p.is_file():print(str(p),p.stat().st_size)
print('\nKEY STATE PERMISSIONS')
for name in ['/var/lib/tailscale','/var/lib/tailscale/tailscaled.state']:
 p=pathlib.Path(name)
 if p.exists():print(name,oct(p.stat().st_mode & 0o777),p.stat().st_uid)

#!/bin/bash
printf '\n### PATH_AND_LAZY_NVM ###\n'
printf '%s\n' "$PATH"
command -v ng; command -v pyenv; command -v rustup
ls -l /usr/bin/ng /usr/local/bin/ng /root/.cargo/bin/rustup /workspace/.cargo/bin/rustup 2>/dev/null
sed -n '1,220p' /root/.nvm/nvm-lazy.sh
printf '\n### ESM_INTEROP_ISOLATED ###\n'
for nodebin in /usr/bin/node /root/.nvm/versions/node/v22.13.1/bin/node; do "$nodebin" -e 'try { require("/root/.nvm/versions/node/v22.13.1/lib/node_modules/@angular/cli/node_modules/yargs/helpers/helpers.mjs"); console.log(process.version,"yargs ESM require OK"); } catch (e) { console.log(process.version, e.code, e.message.split("\n")[0]); }'; done
printf '\n### PYENV_PYTHON ###\n'
/root/.pyenv/versions/3.11.1/bin/python --version
printf '\n### SERVICE_CONFIG_PATHS ###\n'
python3 - <<'PY'
import pathlib,re
for name in ['supervisord','tailscaled','sshd']:
 for d in pathlib.Path('/proc').glob('[0-9]*'):
  try:
   if (d/'comm').read_text().strip()!=name:continue
   args=(d/'cmdline').read_bytes().decode(errors='replace').split('\x00')
   safe=[]
   for a in args:
    if re.search(r'token|auth.?key|password|secret',a,re.I):safe.append('[sensitive argument omitted]')
    else:safe.append(a)
   print(d.name, name, safe)
  except (OSError,PermissionError):pass
for p in [pathlib.Path('/etc/supervisord.conf')]+list(pathlib.Path('/etc/supervisor/conf.d').glob('*')):
 if p.is_file():
  for n,l in enumerate(p.read_text(errors='replace').splitlines(),1):
   if l.startswith('[') or re.match(r'^(files|autostart|autorestart)\s*=',l) or 'tailscale' in l:
    if re.search(r'token|auth.?key|password|secret',l,re.I):l='[sensitive line omitted]'
    print(str(p),n,l)
PY
printf '\n### FAILED_LOGIN_RECORDS ###\n'
lastb -n 5 -w 2>/dev/null
printf '\n### PACKAGE_INTEGRITY ###\n'
dpkg --audit
printf '\n### REBOOT_FLAG ###\n'
if test -f /var/run/reboot-required; then cat /var/run/reboot-required; else printf 'not present\n'; fi

import os
import sys

site_pkgs = os.path.join(os.path.basename(__file__), 'site-packages')
os.makedirs(site_pkgs, exist_ok=True)
sys.path.append(site_pkgs)

try:
  import earthaccess
except:
  import subprocess
  subprocess.run([
    sys.executable, '-m', 'pip', 'install', f'--target={site_pkgs}', 'earthaccess'
  ])
  import earthaccess




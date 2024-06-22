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


try:
  import h5py
except:
  import subprocess
  subprocess.run([
    sys.executable, '-m', 'pip', 'install', f'--target={site_pkgs}', 'h5py'
  ])
  import h5py

try:
  import numpy
except:
  import subprocess
  subprocess.run([
    sys.executable, '-m', 'pip', 'install', f'--target={site_pkgs}', 'numpy'
  ])
  import numpy


try:
  import PIL
  import PIL.Image
  import PIL.ImageDraw
except:
  import subprocess
  subprocess.run([
    sys.executable, '-m', 'pip', 'install', f'--target={site_pkgs}', 'Pillow'
  ])
  import PIL
  import PIL.Image
  import PIL.ImageDraw

import PIL.GifImagePlugin
#PIL.GifImagePlugin.LOADING_STRATEGY = PIL.GifImagePlugin.LoadingStrategy.RGB_AFTER_DIFFERENT_PALETTE_ONLY
PIL.GifImagePlugin.LOADING_STRATEGY = PIL.GifImagePlugin.LoadingStrategy.RGB_ALWAYS

try:
  import dateparser
except:
  import subprocess
  subprocess.run([
    sys.executable, '-m', 'pip', 'install', f'--target={site_pkgs}', 'dateparser'
  ])
  import dateparser

try:
  import dateutil
  import dateutil.parser
except:
  import subprocess
  subprocess.run([
    sys.executable, '-m', 'pip', 'install', f'--target={site_pkgs}', 'python-dateutil'
  ])
  import dateutil
  import dateutil.parser


try:
  import cv2
except:
  import subprocess
  subprocess.run([
    sys.executable, '-m', 'pip', 'install', f'--target={site_pkgs}', 'opencv-python'
  ])
  import cv2






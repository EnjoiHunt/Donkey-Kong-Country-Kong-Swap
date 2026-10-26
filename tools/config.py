"""Paths. Point these at your own clean, headerless USA ROMs (see README)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
SRC = os.path.join(ROOT, 'src')
DKC1_ROM = os.environ.get('DKC1_ROM', os.path.join(ROOT, 'roms', 'dkc1.sfc'))
DKC2_ROM = os.environ.get('DKC2_ROM', os.path.join(ROOT, 'roms', 'dkc2.sfc'))
DKC3_ROM = os.environ.get('DKC3_ROM', os.path.join(ROOT, 'roms', 'dkc3.sfc'))
ASAR = os.environ.get('ASAR', 'asar')
BUILD = os.path.join(ROOT, 'build')
os.makedirs(BUILD, exist_ok=True)
def data(name): return os.path.join(DATA, name)

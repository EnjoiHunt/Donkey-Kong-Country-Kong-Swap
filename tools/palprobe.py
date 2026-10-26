import sys
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as CFG

from dkcsprite import render
from PIL import Image, ImageDraw
def pal_at(rom, off):
    out = [(0, 0, 0)]
    for i in range(15):
        v = rom[off+i*2] | rom[off+i*2+1] << 8
        out.append(((v & 31) << 3, ((v >> 5) & 31) << 3, ((v >> 10) & 31) << 3))
    return out
if __name__ == '__main__':
    rom = open(sys.argv[1], 'rb').read()
    frame = int(sys.argv[2], 16); center = int(sys.argv[3], 16)
    offs = [center + k*30 for k in range(-12, 13)]
    sheet = Image.new('RGB', (len(offs)*64, 90), (48, 52, 70)); d = ImageDraw.Draw(sheet)
    for n, o in enumerate(offs):
        im = render(rom, frame, pal_at(rom, o)); sheet.paste(im, (n*64+4, 4), im)
        d.text((n*64+2, 76), hex(o)[3:], fill=(255, 255, 140))
    sheet.resize((sheet.width*2, sheet.height*2)).save(sys.argv[4])

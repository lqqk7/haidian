# -*- coding: utf-8 -*-
"""逐像素差异量化：给出差异像素数、最大通道差、差异包围盒（原图 4800x3000 坐标）。"""
import sys
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
a = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(np.int16)
b = np.asarray(Image.open(sys.argv[2]).convert('RGB')).astype(np.int16)
if a.shape != b.shape:
    print('shape mismatch', a.shape, b.shape)
    sys.exit(1)
d = np.abs(a - b).max(axis=2)
for thr in (0, 3, 8, 24, 64):
    m = d > thr
    n = int(m.sum())
    if n == 0:
        print(f'>{thr:3d}: 0')
        continue
    ys, xs = np.nonzero(m)
    print(f'>{thr:3d}: {n:8d} px  bbox x[{xs.min()},{xs.max()}] y[{ys.min()},{ys.max()}]')
print('max delta', int(d.max()))

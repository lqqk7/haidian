#!/usr/bin/env python3
"""为 report/*.html 的本地图片补 width/height 与 max-width 内联样式。
与历史链条一致：读取图片真实像素尺寸，写入 width/height 属性，
并附 style="max-width:100%;height:auto"，使离线报告在窄屏不溢出、
加载时不发生布局抖动（CLS）。可重复执行：已带 width 的 img 跳过。"""
import re, sys, os
from PIL import Image

IMG = re.compile(r'<img src="([^"]+)" alt="((?:[^"\\]|\\.)*)">')

def patch(path):
    base = os.path.dirname(os.path.abspath(path))
    s = open(path, encoding='utf-8').read()
    n = 0
    def rep(m):
        nonlocal n
        src, alt = m.group(1), m.group(2)
        p = os.path.normpath(os.path.join(base, src))
        if not os.path.isfile(p):
            print('  MISSING', src); return m.group(0)
        with Image.open(p) as im:
            w, h = im.size
        n += 1
        return (f'<img src="{src}" alt="{alt}" width="{w}" height="{h}" '
                f'style="max-width:100%;height:auto">')
    out = IMG.sub(rep, s)
    open(path, 'w', encoding='utf-8').write(out)
    print(f'{path}: {n} img 注入尺寸')

for a in sys.argv[1:]:
    patch(a)

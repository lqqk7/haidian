#!/bin/bash

HAIDIAN_TOOLCHAIN_ROOT="$(cd "$(dirname "$0")/../" && pwd)"
HAIDIAN_PROJECT_ROOT="$(cd "$HAIDIAN_TOOLCHAIN_ROOT/../.." && pwd)"
export HAIDIAN_TOOLCHAIN_ROOT HAIDIAN_PROJECT_ROOT
# w100-plates —— 万感京张 v10.0 两张英文图版重建链
#
# 体裁：HTML -> Chromium(Playwright) 无头截图 -> 局部带无缝拼接 -> pngquant -> zopflipng
#      渲染器沿用 wp4b/render.js 的调用形态，断言探测沿用 w81-basemap/probe.js。
#
# 策略：两图的缺陷都是局部的（enterprise-journey.en 只有卡片行的标题/徽标叠印；
#      op04-detail.en 只有八要素卡被硬切与免责条带缺失），其余像素与中文版逐块对齐且完好。
#      因此只重渲缺陷带，其余像素原样保留 —— 观感零漂移，字节增量最小。
#      拼接缝均落在纯背景 #F2EFE7 行上，无接缝。
#
# 版式规格（自中文版逐块扫描提取，CSS px = 原图 px / 2，dsf=2）：
#   enterprise-journey  4800x3000 (CSS 2400x1500)  页边距 38
#     header 0-128 | 卡片行 168-390(高222) 6卡宽333 gap65 | 两翼白框 532-606
#     双白框 660-910(各宽1143 gap35) | 虚线框 1096-1169.5 | 深色条 1250-1372 | 页脚 1459.5-1482.5
#   op04-detail         2352x2016 (CSS 1176x1008)  页边距 31.5 内容宽 1113
#     图区 149-672 | 段标题 688-705 | 卡行1 713-836.5 | 卡行2 844.5-968.5 | 免责条带 976.5-1008
#   配色 #F2EFE7 底 / #10383D 墨绿 / #177C78 青 / #5D87B0 蓝 / #6B5B95 紫 / #D76450 珊瑚 / #D9A33A 金
#   字体 Source Han Sans SC（拉丁字形即 Source Sans 衍生，与两版原图一致；包内 OFL 已登记）
set -e
cd "$(dirname "$0")"
OUT=out; FIG=${HAIDIAN_PROJECT_ROOT}/submissions/lqqk7/every-sense-jingzhang/assets/figures
mkdir -p $OUT

# 1) 渲染缺陷带（shoot.js 在截图前跑溢出/裁切/叠印断言，任一非零则不写 PNG 并以 1 退出）
node shoot.js ej-band.html    $OUT/ej-band.png    2400 310 2
node shoot.js op04-foot.html  $OUT/op04-foot.png  1176 299 2

# 2) 无缝拼接（替换段：ej 原图 y 320-940；op04 原图 y 1418-2016）
"${HAIDIAN_TOOLCHAIN_ROOT}/venv/bin/python" - <<'PY'
from PIL import Image
import os
from pathlib import Path
F=str(Path(os.environ['HAIDIAN_PROJECT_ROOT']) / 'submissions/lqqk7/every-sense-jingzhang/assets/figures') + '/'
ej=Image.open(F+'enterprise-journey.en.png').convert('RGB')
b=Image.open('out/ej-band.png').convert('RGB'); assert b.size==(4800,620)
o=Image.new('RGB',(4800,3000))
o.paste(ej.crop((0,0,4800,320)),(0,0)); o.paste(b,(0,320)); o.paste(ej.crop((0,940,4800,3000)),(0,940))
o.save('out/enterprise-journey.en.raw.png')

op=Image.open(F+'op04-detail.en.png').convert('RGB')
f=Image.open('out/op04-foot.png').convert('RGB'); assert f.size==(2352,598)
o=Image.new('RGB',(2352,2016))
o.paste(op.crop((0,0,2352,1418)),(0,0)); o.paste(f,(0,1418))
o.save('out/op04-detail.en.raw.png')
PY

# 3) 压缩（96 色档：中文版原图为 P/71 与 P/69，96 色留足余量且目检无损）
for p in "ej:enterprise-journey.en" "op:op04-detail.en"; do
  k=${p%%:*}; n=${p##*:}
  pngquant --force --speed 1 --quality 70-100 96 -o $OUT/$k.96.png $OUT/$n.raw.png
  zopflipng -y --iterations=5 --filters=0 $OUT/$k.96.png $OUT/$k.96.z.png
done

# 4) 落位（可写范围仅这两个文件）
cp $OUT/ej.96.z.png $FIG/enterprise-journey.en.png
cp $OUT/op.96.z.png $FIG/op04-detail.en.png
stat -f "%z %N" $FIG/enterprise-journey.en.png $FIG/op04-detail.en.png

#!/bin/zsh

HAIDIAN_TOOLCHAIN_ROOT="$(cd "$(dirname "$0")/../" && pwd)"
HAIDIAN_PROJECT_ROOT="$(cd "$HAIDIAN_TOOLCHAIN_ROOT/../.." && pwd)"
export HAIDIAN_TOOLCHAIN_ROOT HAIDIAN_PROJECT_ROOT
# 只重排 A3 英文册（wp4b/mkpdf.sh 的单册版，逐字沿用其渲染与合并方式）
set -e
cd "${HAIDIAN_TOOLCHAIN_ROOT}/wp4b"
PY="${HAIDIAN_TOOLCHAIN_ROOT}/venv/bin/python"
files=$(ls out/a3/en-*.html | sort)
node render.js pdf out/a3/en.pdf ${(f)files} > /dev/null
$PY - <<'PYEOF'
from pypdf import PdfWriter, PdfReader
import json, os
parts = json.load(open('out/a3/en.pdf.parts.json'))
w = PdfWriter()
for p in parts: w.append(p)
out = 'out/a3/en.pdf'
w.write(out); w.close()
r = PdfReader(out); b = r.pages[0].mediabox
print(f'a3-en: {len(r.pages)} pages  {os.path.getsize(out):,} B  '
      f'{float(b.width)/72*25.4:.2f} x {float(b.height)/72*25.4:.2f} mm')
PYEOF

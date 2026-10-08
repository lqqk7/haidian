#!/bin/zsh

HAIDIAN_TOOLCHAIN_ROOT="$(cd "$(dirname "$0")/../" && pwd)"
HAIDIAN_PROJECT_ROOT="$(cd "$HAIDIAN_TOOLCHAIN_ROOT/../.." && pwd)"
export HAIDIAN_TOOLCHAIN_ROOT HAIDIAN_PROJECT_ROOT
set -e
cd "$(dirname "$0")"
PY="${HAIDIAN_TOOLCHAIN_ROOT}/venv/bin/python"
for k in a3 a0; do
  for l in zh en; do
    files=$(ls out/$k/$l-*.html | sort)
    node render.js pdf out/$k/$l.pdf ${(f)files} > /dev/null
    $PY - "$k" "$l" <<'PYEOF'
from pypdf import PdfWriter, PdfReader
import json, sys, os
k, l = sys.argv[1], sys.argv[2]
parts = json.load(open(f'out/{k}/{l}.pdf.parts.json'))
w = PdfWriter()
for p in parts: w.append(p)
out = f'out/{k}/{l}.pdf'
w.write(out); w.close()
PYEOF
    # every page was rendered on its own, so each carries a private subset of the
    # same face; fold those subsets into one shared font program per weight
    $PY merge_fonts.py out/$k/$l.pdf out/$k/$l.merged.pdf > /dev/null
    mv out/$k/$l.merged.pdf out/$k/$l.pdf
    $PY - "$k" "$l" <<'PYEOF'
from pypdf import PdfReader
import sys, os
k, l = sys.argv[1], sys.argv[2]
out = f'out/{k}/{l}.pdf'
r = PdfReader(out); b = r.pages[0].mediabox
print(f'{k}-{l}: {len(r.pages)} pages  {os.path.getsize(out):,} B  '
      f'{float(b.width)/72*25.4:.2f} x {float(b.height)/72*25.4:.2f} mm')
PYEOF
  done
done

# -*- coding: utf-8 -*-
"""PG-07 全册字体审计（双取修订版）。

修订缘由
--------
v9.9 之前的审计口径只读字体字典的 `/BaseFont`。Type3 字体在 PDF 规范里**没有**
`/BaseFont` 项——它的名字只出现在 `/FontDescriptor` 的 `/FontName` 里（且该描述符
本身是可选的）。于是三条 `PingFangSC-Regular` 的 Type3 条目对旧脚本完全不可见，
审计因此报出「非 OFL 条目为 0」，与 `pdffonts` 的实测直接矛盾。

本脚本对每个字体字典**双取**名字：
    name = /BaseFont  或（缺失时）/FontDescriptor 的 /FontName
Type0 复合字体另下钻到 /DescendantFonts[0] 取其描述符。名字带 `AAAAAA+` 六字母
子集前缀的一律剥前缀后判定。

判据
----
* 嵌入字体程序：`/FontFile`（Type1）、`/FontFile2`（TrueType）、`/FontFile3`（CFF/OpenType）。
  这是「再分发了字体文件」的唯一判据。
* Type3：不含任何字体程序，字形以页面路径算子写出；不构成字体文件再分发，但其
  描述符名称仍须落在已清权族内，否则登记为例外。

用法：python pdf_font_audit.py <pdf> [<pdf> ...]
"""
from __future__ import annotations

import os
import re
import sys

from pypdf import PdfReader

OFL_FAMILIES = ("SourceHanSansSC",)
SUBSET_PREFIX = re.compile(r"^[A-Z]{6}\+")
PROGRAM_KEYS = ("/FontFile", "/FontFile2", "/FontFile3")


def strip_subset(name: str) -> str:
    return SUBSET_PREFIX.sub("", str(name).lstrip("/"))


def font_dicts(reader: PdfReader):
    """逐页 yield (page_no, resource_name, font_dict)，含 XObject 内的嵌套资源。"""
    seen = set()

    def walk(res, page_no, depth=0):
        if res is None or depth > 6:
            return
        res = res.get_object()
        fonts = res.get("/Font")
        if fonts is not None:
            for nm, ref in fonts.get_object().items():
                f = ref.get_object()
                key = (page_no, str(nm), id(f))
                if key in seen:
                    continue
                seen.add(key)
                yield page_no, str(nm), f
        xo = res.get("/XObject")
        if xo is not None:
            for _nm, ref in xo.get_object().items():
                o = ref.get_object()
                yield from walk(o.get("/Resources"), page_no, depth + 1)

    for i, page in enumerate(reader.pages, 1):
        yield from walk(page.get("/Resources"), i)


def descriptor_of(f):
    """返回该字体字典的 FontDescriptor（Type0 下钻到 DescendantFonts[0]）。"""
    if str(f.get("/Subtype")) == "/Type0" and "/DescendantFonts" in f:
        d0 = f["/DescendantFonts"].get_object()[0].get_object()
        return d0.get("/FontDescriptor"), d0
    return f.get("/FontDescriptor"), f


def audit(path):
    reader = PdfReader(path)
    rows = []
    for page_no, res_name, f in font_dicts(reader):
        subtype = str(f.get("/Subtype"))
        fd_ref, owner = descriptor_of(f)
        fd = fd_ref.get_object() if fd_ref is not None else None
        # ---- 双取 ----
        base = f.get("/BaseFont") or owner.get("/BaseFont")
        fdname = fd.get("/FontName") if fd else None
        name = base if base is not None else fdname
        source = "/BaseFont" if base is not None else ("/FontDescriptor /FontName" if fdname else "(anonymous)")
        fam = strip_subset(name) if name is not None else None
        programs = [k for k in PROGRAM_KEYS if fd and k in fd]
        ofl = fam is not None and any(fam.startswith(p) for p in OFL_FAMILIES)
        rows.append(dict(page=page_no, res=res_name, subtype=subtype,
                         name=(str(name) if name is not None else None),
                         name_source=source, family=fam,
                         programs=programs, ofl=ofl,
                         charprocs=(len(f["/CharProcs"].get_object()) if "/CharProcs" in f else 0)))
    return rows


def report(path):
    rows = audit(path)
    prog_rows = [r for r in rows if r["programs"]]
    t3_rows = [r for r in rows if r["subtype"] == "/Type3"]
    bad_prog = [r for r in prog_rows if not r["ofl"]]
    bad_t3 = [r for r in t3_rows if not r["ofl"]]
    anon = [r for r in rows if r["name"] is None]
    fams = sorted({r["family"] for r in rows if r["family"]})
    by_desc = [r for r in rows if r["name_source"] != "/BaseFont" and r["name"]]
    print("== %s ==" % os.path.basename(path))
    print("   字体字典 %d 条；families: %s" % (len(rows), ", ".join(fams)))
    print("   嵌入字体程序条目 %d；Type3 条目 %d；名字取自 /FontDescriptor 的 %d 条"
          % (len(prog_rows), len(t3_rows), len(by_desc)))
    print("   非 OFL 嵌入字体程序 %d；非 OFL Type3 %d；无名字体 %d"
          % (len(bad_prog), len(bad_t3), len(anon)))
    for r in bad_prog + bad_t3:
        print("   EXCEPTION p%-3d %-6s %-14s %s  (name from %s, glyphs %d)"
              % (r["page"], r["res"], r["subtype"], r["name"], r["name_source"], r["charprocs"]))
    return len(bad_prog), len(bad_t3), len(t3_rows), len(prog_rows)


if __name__ == "__main__":
    tot = [0, 0]
    for p in sys.argv[1:]:
        bp, bt, nt3, npr = report(p)
        tot[0] += bp
        tot[1] += bt
    print("== 合计：非 OFL 嵌入字体程序 %d，非 OFL Type3 描述符名 %d ==" % tuple(tot))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WP-E2 renderer: ten-node dual-state reachability + blue-green / slow mobility.
Builds the zh and en HTML at 1200x750 CSS px; render.js screenshots at dsf 4
-> 4800x3000 PNG.  Panels are drawn at 4 m per CSS px, i.e. exactly 1 metre per
output pixel; the corridor locator at 20 m per CSS px (5 m per output pixel)."""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import base64
import io
import os
import pickle
import subprocess
import sys

from shapely.geometry import box, Point
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fcopy import T, SCEN, AREA, ROAD  # noqa: E402

PY = str(_HaidianPath(__file__).resolve().parents[2] / 'venv/bin/python')
MKFONT = str(_HaidianPath(__file__).resolve().parents[2] / 'wpn2b/wp4b/mkfont.py')

G = pickle.load(open(os.path.join(HERE, "geom.pkl"), "rb"))
ROWS, SUM = G["rows"], G["summary"]
ROWBY = {r["id"]: r for r in ROWS}
RD = {p["id"]: g for p, g in G["roads"]}

C = dict(deep="#10383d", teal="#177c78", coral="#d76450", purple="#6b5b95",
         gold="#d6a13b", sky="#4aa3c4", paper="#f2efe7", ink="#17383c",
         line="#cbd3cf", muted="#68787b", edge="#e2ddd0", onDarkEn="#9ecdc7")
GREEN_F, GREEN_S = "#cbdcc6", "#8fae8a"
BLDG_F, BLDG_S = "#b7c2c0", "#8fa19e"
GATE = {"G0": C["muted"], "G1": C["gold"], "G2": C["purple"], "G3": C["coral"]}

# ------------------------------------------------------------------ layout
W, H = 1200, 750
HEAD_H, LEG_H, FOOT_H, PAD, MAIN_T = 84, 46, 46, 22, 8
MAIN_H = H - HEAD_H - LEG_H - MAIN_T - FOOT_H            # 568
MAIN_W = W - 2 * PAD                                      # 1156
RAIL_W, COLGAP, GP, LOC_W = 302, 12, 8, 140
MAPS_W = MAIN_W - RAIL_W - COLGAP                         # 842
K1_W = 262
COLC_W = MAPS_W - LOC_W - GP - K1_W - GP                  # 424
K2_H, PH = 306, 15
K3_H = MAIN_H - K2_H - GP                                 # 254
S = 4.0                                                   # m per CSS px
S_LOC = 20.0
LOC_MAP_H, LOC_MAP_W = 490, 74


def window(bounds, wpx, hpx, scale):
    cx, cy = (bounds[0] + bounds[2]) / 2.0, (bounds[1] + bounds[3]) / 2.0
    return (cx - wpx * scale / 2, cy - hpx * scale / 2,
            cx + wpx * scale / 2, cy + hpx * scale / 2)


BW = 2  # 1px border either side of .pn
PAN = []
for pid, boxw, boxh in (("K1", K1_W, MAIN_H), ("K2", COLC_W, K2_H), ("K3", COLC_W, K3_H)):
    p = G["panels"][pid]
    wpx, hpx = boxw - BW, boxh - PH - BW
    PAN.append(dict(id=pid, w=wpx, h=hpx, boxw=boxw, boxh=boxh, scale=S,
                    area_id=p["area_id"], members=p["members"],
                    win=window(p["content_bounds"], wpx, hpx, S)))
LOC_WIN = window(G["site"][0][1].bounds, LOC_MAP_W, LOC_MAP_H, S_LOC)


# --------------------------------------------------------------------- svg
def _ring(cs, out):
    out.append("M" + " L".join(f"{x - ORX:.2f} {ORY - y:.2f}" for x, y in cs) + "Z")


def d_of(g):
    if g.is_empty:
        return ""
    o, t = [], g.geom_type
    if t == "Polygon":
        _ring(g.exterior.coords, o)
        for r in g.interiors:
            _ring(r.coords, o)
    elif t == "LineString":
        o.append("M" + " L".join(f"{x - ORX:.2f} {ORY - y:.2f}" for x, y in g.coords))
    elif t.startswith("Multi") or t == "GeometryCollection":
        return " ".join(filter(None, (d_of(x) for x in g.geoms)))
    return "".join(o)


def clip(g, win, pad=90.0):
    b = box(win[0] - pad, win[1] - pad, win[2] + pad, win[3] + pad)
    try:
        return g.intersection(b)
    except Exception:
        return g.buffer(0).intersection(b)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def nf(v, d=0):
    return f"{v:,.{d}f}"


ORX, ORY = 444000.0, 4428000.0   # false origin: keeps SVG user units small
VE = 'vector-effect="non-scaling-stroke"'


def map_svg(win, wpx, hpx, scale, members, tag):
    x0, y0, x1, y1 = win
    vb = f"{x0 - ORX:.3f} {ORY - y1:.3f} {x1 - x0:.3f} {y1 - y0:.3f}"
    hz = 3.4 * scale
    P = [f'<svg class="mp" viewBox="{vb}" width="{wpx}" height="{hpx}" '
         f'data-ox="{ORX}" data-oy="{ORY}" data-mpp="{scale}" '
         f'shape-rendering="geometricPrecision">',
         f'<defs><pattern id="ht{tag}" width="{hz:.2f}" height="{hz:.2f}" '
         f'patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
         f'<line x1="0" y1="0" x2="0" y2="{hz:.2f}" stroke="{C["teal"]}" '
         f'stroke-width="{0.6 * scale:.2f}" opacity=".55"/></pattern></defs>']

    def add(g, style):
        d = d_of(clip(g, win))
        if d:
            P.append(f'<path d="{d}" {style}/>')

    add(G["site"][0][1], f'fill="none" stroke="{C["deep"]}" stroke-width="1" '
                         f'stroke-dasharray="5 3.5" opacity=".5" {VE}')
    for _, g in G["green"]:
        add(g, f'fill="{GREEN_F}" fill-opacity=".66" stroke="{GREEN_S}" stroke-width=".7" {VE}')
    for _, g in G["public"]:
        add(g, f'fill="{C["sky"]}" fill-opacity=".15" stroke="{C["sky"]}" stroke-width=".85" '
               f'stroke-dasharray="3.5 2.4" {VE}')
    for _, g in G["blds"]:
        add(g, f'fill="{BLDG_F}" fill-opacity=".95" stroke="{BLDG_S}" stroke-width=".6" {VE}')
    for _, g in G["keyareas"]:
        add(g, f'fill="{C["coral"]}" fill-opacity=".05" stroke="{C["coral"]}" stroke-width="1.3" '
               f'stroke-dasharray="7 4" {VE}')
    if members:
        on = unary_union([G["on"][m] for m in members])
        off = unary_union([G["off"][m] for m in members])
        gap = on.difference(off)
        add(on, f'fill="{C["teal"]}" fill-opacity=".13" stroke="none"')
        add(gap, f'fill="{C["coral"]}" fill-opacity=".36" stroke="none"')
        add(off, f'fill="{C["paper"]}" fill-opacity=".9" stroke="none"')
        add(off, f'fill="url(#ht{tag})" stroke="none"')
        add(gap, f'fill="none" stroke="{C["coral"]}" stroke-width=".9" {VE}')
        add(off, f'fill="none" stroke="{C["deep"]}" stroke-width="1.1" {VE}')
        add(on, f'fill="none" stroke="{C["teal"]}" stroke-width="1.9" {VE}')
    for p, g in G["roads"]:
        rid = p["id"]
        st = (f'stroke="{C["teal"]}" stroke-width="2.4"' if rid == "ROAD-001" else
              f'stroke="{C["purple"]}" stroke-width="2.2" stroke-dasharray="6 3.2"'
              if rid == "ROAD-005" else f'stroke="{C["gold"]}" stroke-width="1.9"')
        add(g, f'fill="none" {st} stroke-linecap="round" {VE}')
    for m in (members or []):
        add(G["stubs"][m], f'fill="none" stroke="{C["purple"]}" stroke-width="1" '
                           f'stroke-dasharray="2 1.8" {VE}')
    P.append("</svg>")

    def to_px(X, Y):
        return ((X - x0) / scale, (y1 - Y) / scale)

    return "".join(P), to_px


# ------------------------------------------------------- road-tag placement
def tag_spot(pan, rid, lab, lang, reserved):
    """Put a road tag on the stretch of that road furthest from anything busy."""
    win, sc = pan["win"], pan["scale"]
    n = len(lab)
    cw = 5.6 if lang == "zh" else 3.15
    vertical = rid in ("ROAD-001", "ROAD-005")
    bw, bh = ((9.5, n * cw + 6) if vertical else (n * cw + 7, 8.5))
    mx, my = bw / 2 * sc + 4 * sc, bh / 2 * sc + 4 * sc
    inset = box(win[0] + mx, win[1] + my, win[2] - mx, win[3] - my)
    seg = RD[rid].intersection(inset)
    if seg.is_empty:
        seg = RD[rid].intersection(box(*win))
    if seg.is_empty:
        return None
    busy = [G["on"][m] for m in pan["members"]]
    busy += [Point(ROWBY[m]["x"], ROWBY[m]["y"]).buffer(14 * sc) for m in pan["members"]]
    for lx, ly, lw, lh in reserved:                       # px rects -> world
        busy.append(box(win[0] + lx * sc, win[3] - (ly + lh) * sc,
                        win[0] + (lx + lw) * sc, win[3] - ly * sc))
    B = unary_union(busy)
    L = seg.length
    best, bd = None, -1.0
    for i in range(241):
        p = seg.interpolate(L * i / 240.0)
        d = p.distance(B) - abs(i / 240.0 - 0.5) * 12.0   # mild pull to mid-run
        if d > bd:
            bd, best = d, p
    x0, y0, x1, y1 = win
    return best.x, best.y, ((best.x - x0) / sc - bw / 2, (y1 - best.y) / sc - bh / 2, bw, bh)


# ------------------------------------------------------------ label placer
CAND = [(9, -4, "l"), (9, 6, "l"), (-9, -4, "r"), (-9, 6, "r"),
        (9, -14, "l"), (-9, -14, "r"), (9, 16, "l"), (-9, 16, "r"),
        (0, -15, "c"), (0, 16, "c"), (20, -22, "l"), (-20, -22, "r"),
        (20, 24, "l"), (-20, 24, "r"), (0, -26, "c"), (0, 27, "c")]


def place(items, wpx, hpx, taken=()):
    boxes, out = list(taken), {}
    for px, py, bw, bh, k in items:
        best = bc = None
        for i, (dx, dy, an) in enumerate(CAND):
            lx = px + dx if an == "l" else (px + dx - bw if an == "r" else px - bw / 2 + dx)
            ly = py + dy - bh / 2
            c = i * 0.9
            c += max(0, 3 - lx) * 40 + max(0, lx + bw - wpx + 3) * 40
            c += max(0, 3 - ly) * 40 + max(0, ly + bh - hpx + 3) * 40
            for ox, oy, ow, oh in boxes:
                ix = min(lx + bw, ox + ow) - max(lx, ox)
                iy = min(ly + bh, oy + oh) - max(ly, oy)
                if ix > 0 and iy > 0:
                    c += ix * iy * 0.6
            if bc is None or c < bc:
                bc, best = c, (lx, ly, an)
        boxes.append((best[0], best[1], bw, bh))
        out[k] = best
    return out, boxes


# ------------------------------------------------------------------ blocks
def panel(pan, lang, idx):
    t = T[lang]
    name = AREA[pan["area_id"]][0 if lang == "zh" else 1]
    svg, to_px = map_svg(pan["win"], pan["w"], pan["h"], pan["scale"],
                         pan["members"], pan["id"])
    ov = []
    # furniture the map owns: scale bar (bottom-left) and north arrow (top-right)
    taken = [(2, pan["h"] - 20, 200 / pan["scale"] + 12, 20), (pan["w"] - 20, 2, 18, 20)]
    if pan.get("callout"):
        r = ROWBY[pan["callout"]]
        px, py = to_px(r["x"], r["y"])
        taken.append((px - 14, py - 4, 76, 300 / pan["scale"] + 12))
    # road tags: each takes the emptiest stretch of its own line
    for rid, cls in pan["roadtags"]:
        lab = ROAD[rid][0 if lang == "zh" else 1]
        got = tag_spot(pan, rid, lab, lang, taken)
        if not got:
            continue
        wx, wy, bx = got
        px, py = to_px(wx, wy)
        taken.append(bx)
        ov.append(f'<div class="rt {cls}" style="left:{px:.1f}px;top:{py:.1f}px">{esc(lab)}</div>')
    items = []
    for m in sorted(pan["members"]):
        r = ROWBY[m]
        px, py = to_px(r["x"], r["y"])
        items.append((px, py, 46 if lang == "zh" else 48, 13, m))
    pos, _ = place(items, pan["w"], pan["h"], taken)
    lead = []
    for px, py, bw, bh, m in items:
        lx, ly, _a = pos[m]
        cx = min(max(px, lx), lx + bw)
        cy = min(max(py, ly), ly + bh)
        d = ((cx - px) ** 2 + (cy - py) ** 2) ** 0.5
        if d > 5.5:
            k = 4.6 / d
            lead.append(f'<line x1="{px + (cx - px) * k:.1f}" y1="{py + (cy - py) * k:.1f}" '
                        f'x2="{cx:.1f}" y2="{cy:.1f}" stroke="{GATE[ROWBY[m]["gate"]]}" '
                        f'stroke-width=".8" stroke-linecap="round"/>')
    if lead:
        ov.append(f'<svg class="ld" width="{pan["w"]}" height="{pan["h"]}" '
                  f'viewBox="0 0 {pan["w"]} {pan["h"]}">{"".join(lead)}</svg>')
    for m in sorted(pan["members"]):
        r = ROWBY[m]
        px, py = to_px(r["x"], r["y"])
        gc = GATE[r["gate"]]
        lx, ly, _a = pos[m]
        ov.append(f'<i class="nd" style="left:{px:.1f}px;top:{py:.1f}px;border-color:{gc}"></i>')
        ov.append(f'<div class="nl" style="left:{lx:.1f}px;top:{ly:.1f}px">'
                  f'<b style="color:{gc}">{m.split("-")[1]}</b> {m}'
                  f'<span>{r["scenario"]} · {r["gate"]}</span></div>')
    if pan.get("callout"):
        r = ROWBY[pan["callout"]]
        px, py = to_px(r["x"], r["y"])
        a, b = 150.0 / pan["scale"], 300.0 / pan["scale"]
        wpx = 40.0 / pan["scale"]
        ov.append(
            f'<div class="cal" style="left:{px:.1f}px;top:{py:.1f}px">'
            f'<i class="cvl" style="height:{b:.1f}px"></i>'
            f'<i class="ck" style="top:{a:.1f}px"></i><i class="ck" style="top:{b:.1f}px"></i>'
            f'<span class="cl off" style="top:{a:.1f}px">{esc(t["callout_off"])}</span>'
            f'<span class="cl on" style="top:{b:.1f}px">{esc(t["callout_on"])}</span>'
            f'<i class="cw" style="top:{b * 0.27:.1f}px;left:{-wpx:.1f}px;width:{wpx * 2:.1f}px"></i>'
            f'<span class="cl w" style="top:{b * 0.27:.1f}px;left:{-wpx - 2:.1f}px">w = 40 m</span>'
            f'</div>')
    ov.append(f'<div class="sb" style="width:{200.0 / pan["scale"]:.1f}px"><i></i><i></i>'
              f'<span>200 {t["m"]}</span></div>')
    ov.append(f'<div class="na">{t["north"]}</div>')
    return (f'<section class="pn" style="width:{pan["boxw"]}px;height:{pan["boxh"]}px">'
            f'<div class="ph"><b>{idx:02d}</b>{esc(name)}'
            f'<u>{esc(t["px_tag"].format(n=int(pan["scale"] / 4)))}</u></div>'
            f'<div class="pm" style="height:{pan["h"]}px">{svg}'
            f'<div class="ovl">{"".join(ov)}</div></div></section>')


def locator(lang):
    t = T[lang]
    svg, to_px = map_svg(LOC_WIN, LOC_MAP_W, LOC_MAP_H, S_LOC,
                         [r["id"] for r in ROWS], "LC")
    ov = []
    for i, kid in enumerate(("PROV-KEY-001", "PROV-KEY-002", "PROV-KEY-003")):
        p, g = next((a, b) for a, b in G["keyareas"] if a["id"] == kid)
        b = g.bounds
        px, py = to_px(b[2], (b[1] + b[3]) / 2)
        ov.append(f'<div class="kt" style="left:{px + 3:.1f}px;top:{py:.1f}px">'
                  f'<b>{i + 1:02d}</b><span>{esc(AREA[p["area_id"]][0 if lang == "zh" else 1])}</span></div>')
    for r in ROWS:
        px, py = to_px(r["x"], r["y"])
        ov.append(f'<i class="nd sm" style="left:{px:.1f}px;top:{py:.1f}px;'
                  f'border-color:{GATE[r["gate"]]}"></i>')
    ov.append(f'<div class="sb" style="width:{1000.0 / S_LOC:.1f}px"><i></i><i></i>'
              f'<span>1 {t["km"]}</span></div>')
    ov.append(f'<div class="na">{t["north"]}</div>')
    return (f'<section class="loc" style="width:{LOC_W}px;height:{MAIN_H}px">'
            f'<div class="lh">{esc(t["loc_t"])}<span>{esc(t["loc_s"])}'
            f'<em class="pv">{esc(t["pv_area"])}</em></span></div>'
            f'<div class="lm" style="width:{LOC_MAP_W}px;height:{LOC_MAP_H}px">{svg}'
            f'<div class="ovl">{"".join(ov)}</div></div>'
            f'<p class="ln">{esc(t["loc_note"])}<br><b>{esc(t["panel_scale"])}</b></p></section>')


def rail(lang):
    t = T[lang]
    # 首行（网络总长）是唯一带高精度工程量的口径行，紧贴挂“非工程量”短标。
    len_tag = f'<em class="pv">{esc(t["pv_len"])}</em>'
    cal = "".join(
        f'<div class="cr"><b>{esc(k)}</b><span>{esc(v)}{len_tag if i == 0 else ""}'
        f'</span></div>' for i, (k, v) in enumerate(t["cal_rows"]))
    mx = max(r["area_gap_sqm"] for r in ROWS)
    # 主图只保留前三位断点，完整十行下沉到审计明细附图。
    tr = "".join(
        f'<div class="tr hot">'
        f'<span class="c0">{r["rank"]}</span>'
        f'<span class="c1">{r["id"]}<i>{r["scenario"]}</i></span>'
        f'<span class="c2" style="color:{GATE[r["gate"]]};border-color:{GATE[r["gate"]]}">{r["gate"]}</span>'
        f'<span class="c3"><i style="width:{r["area_gap_sqm"] / mx * 100:.1f}%"></i>'
        f'<b>{nf(r["area_gap_sqm"])}</b></span>'
        f'<span class="c4">{r["gap_share"] * 100:.1f}%</span></div>' for r in ROWS[:3])
    st = SUM
    sq = "".join(
        f'<div class="sq"><b>{v}</b><span>{esc(k)}</span>'
        f'<em class="pv">{esc(t["pv_area"] if i < 3 else t["pv_perf"])}</em></div>'
        for i, (k, v) in enumerate((
            (t["eq_stat"][0], nf(st["union_on_sqm"]) + " m²"),
            (t["eq_stat"][1], nf(st["union_off_sqm"]) + " m²"),
            (t["eq_stat"][2], nf(st["union_gap_sqm"]) + " m²"),
            (t["eq_stat"][3], f'{st["union_gap_share"] * 100:.2f}%'))))
    return f'''<aside class="rail" style="width:{RAIL_W}px;height:{MAIN_H}px">
<section class="rs"><div class="tp" style="background:{C["teal"]}"></div>
<div class="rh"><div class="n">{t["cal_n"]}</div><h3>{esc(t["cal_t"])}</h3></div>
{cal}<p class="warn">{esc(t["cal_warn"])}</p></section>
<section class="rs"><div class="tp" style="background:{C["coral"]}"></div>
<div class="rh"><div class="n">{t["tab_n"]}</div><h3>{esc(t["tab_t_brief"])}</h3><p>{esc(t["tab_s_brief"])}</p></div>
<div class="th"><span class="c0">{t["tab_head"][0]}</span><span class="c1">{t["tab_head"][1]}</span>
<span class="c2">{t["tab_head"][2]}</span><span class="c3">{t["tab_head"][3]} m²</span>
<span class="c4">{t["tab_head"][4]}</span></div>{tr}
<div class="tu"><span>{esc(t["tab_foot_u"])}</span><b>{nf(st["union_gap_sqm"])} m²</b>
<em class="pv">{esc(t["pv_area"])}</em></div>
<div class="fab"><b>{esc(t["first_breaks"])}</b><span>{" · ".join(r["id"] for r in ROWS[:3])}</span></div>
<p class="tn">{esc(t["resp"])}</p>
<p class="tn ptr">{esc(t["aud_ptr"])}</p></section>
<section class="rs"><div class="tp" style="background:{C["purple"]}"></div>
<div class="rh"><div class="n">{t["eq_n"]}</div><h3>{esc(t["eq_t"])}</h3></div>
<div class="eqw"><div class="eq on"><b>{esc(t["eq_on"])}</b><span>{esc(t["eq_on_s"])}</span></div>
<div class="eqs">=</div>
<div class="eq off"><b>{esc(t["eq_off"])}</b><span>{esc(t["eq_off_s"])}</span></div></div>
<p class="claim">{esc(t["eq_claim"])}</p><div class="sqw">{sq}</div>
<p class="tn">{esc(t["attr_ok"])}</p></section></aside>'''


TIER_C = {"provisional": C["coral"], "concept": C["teal"], "computed": C["purple"]}
LSW = {"road": f'<i class="sw ln" style="background:{C["teal"]}"></i>',
       "green": f'<i class="sw" style="background:{GREEN_F};border-color:{GREEN_S}"></i>',
       "public": f'<i class="sw" style="background:#dbecf3;border-color:{C["sky"]}"></i>',
       "node": f'<i class="sw dot" style="border-color:{C["purple"]}"></i>',
       "key": f'<i class="sw" style="background:#fbeae6;border-color:{C["coral"]}"></i>',
       "bldg": f'<i class="sw" style="background:{BLDG_F};border-color:{BLDG_S}"></i>'}
DSW = {"on": f'<i class="sw" style="background:#dcebe9;border-color:{C["teal"]}"></i>',
       "off": '<i class="sw ht"></i>',
       "gap": f'<i class="sw" style="background:#f4cfc6;border-color:{C["coral"]}"></i>',
       "stub": '<i class="sw ln dsh"></i>'}
RULE = '<span class="bar">' + "".join(
    f'<i style="width:{w}em;background:{c}"></i>' for w, c in
    ((3.1, "#5fb3ab"), (1.5, C["sky"]), (1.0, C["gold"]), (1.3, C["coral"]))) + "</span>"


def roadtags():
    return {"K1": [("ROAD-001", "spine vert"), ("ROAD-005", "alt vert"),
                   ("ROAD-002", "cross")],
            "K2": [("ROAD-001", "spine vert"), ("ROAD-005", "alt vert"),
                   ("ROAD-003", "cross")],
            "K3": [("ROAD-001", "spine vert"), ("ROAD-005", "alt vert"),
                   ("ROAD-004", "cross")]}


def build(lang):
    t = T[lang]
    tg = roadtags()
    for p in PAN:
        p["roadtags"] = tg[p["id"]]
        p["callout"] = "OP-05" if p["id"] == "K1" else None
    tiers = "".join(f'<span class="tg"><b style="background:{TIER_C[k]}"></b>{esc(a)}'
                    f'<em>{esc(b)}</em></span>' for k, a, b in t["tiers"])
    layers = "".join(f'<span class="lg">{LSW[k]}{esc(a)}<u>{b}</u></span>'
                     for k, a, b in t["layers"])
    doms = "".join(f'<span class="lg">{DSW[k]}{esc(a)}</span>' for k, a in t["doms"])
    body = (locator(lang) + panel(PAN[0], lang, 1) +
            f'<div class="colc" style="width:{COLC_W}px">' +
            panel(PAN[1], lang, 2) + panel(PAN[2], lang, 3) + "</div>" + rail(lang))
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8">
<title>ten-node-reachability</title><style>__FONTFACE__{CSS}{EN_CSS if lang == "en" else ""}</style></head><body>
<div class="hd"><div><div class="k">{RULE}<span>{t["kicker"]}</span></div>
<h1>{esc(t["title"])}</h1><div class="alt">{esc(t["alt"])}</div></div>
<div class="r"><div class="i">{t["idx"]}</div><div class="s">{esc(t["sub"])}</div>
<div class="pill">{esc(t["pill"])}</div></div></div>
<div class="lgs"><div class="lr">{tiers}<span class="sp"></span>
<span class="gt">{esc(t["gate_lab"])}</span>
{"".join(f'<span class="gc"><b style="border-color:{v}"></b>{k}</span>' for k, v in GATE.items())}</div>
<div class="lr b"><span class="hl">{esc(t["layerhead"])}</span>{layers}<span class="sp"></span>
<span class="hl">{esc(t["domhead"])}</span>{doms}<span class="sp"></span>
<span class="cv"><b>{SUM["union_on_share_of_site"] * 100:.2f}%</b><u class="cvn">{esc(t["cover_note"])}<em class="pv">{esc(t["pv_perf"])}</em></u></span></div></div>
<div class="mn">{body}</div>
<div class="ft"><p class="disc">{esc(t["disc"])}</p>
<div class="fr"><span>{esc(t["footL"])}</span><span class="fx">{t["footR"]}</span></div></div>
</body></html>'''


CSS = f"""
*{{box-sizing:border-box}}html,body{{margin:0;padding:0}}
body{{width:{W}px;height:{H}px;overflow:hidden;background:{C["paper"]};color:{C["ink"]};
font-family:SHS,"Helvetica Neue",Arial,sans-serif;-webkit-font-smoothing:antialiased;
text-rendering:geometricPrecision}}
.hl,.fx,.na{{font-family:"Helvetica Neue",Arial,SHS,sans-serif}}
.bar{{display:flex;gap:.35em;height:.32em}}.bar i{{display:block;height:.32em;border-radius:.16em}}
.hd{{height:{HEAD_H}px;background:{C["deep"]};color:#fff;padding:11px {PAD}px 0;display:flex;
justify-content:space-between}}
.hd .k{{font-size:6.4px;letter-spacing:.19em;color:{C["onDarkEn"]};display:flex;align-items:center;
gap:9px;font-family:"Helvetica Neue",Arial,SHS,sans-serif;font-weight:700}}
.hd h1{{font-size:21px;font-weight:700;margin:10px 0 0;line-height:1.14;max-width:850px}}
.alt{{font-size:7.4px;color:{C["onDarkEn"]};margin-top:5px;letter-spacing:.02em}}
.hd .r{{text-align:right}}
.hd .r .i{{font-size:6.2px;letter-spacing:.15em;font-weight:700;
font-family:"Helvetica Neue",Arial,SHS,sans-serif}}
.hd .r .s{{font-size:6.4px;color:{C["onDarkEn"]};margin-top:4px}}
.pill{{display:inline-block;margin-top:9px;background:{C["coral"]};color:#fff;font-size:6.4px;
letter-spacing:.08em;padding:4px 11px;border-radius:9px;font-weight:700}}
.lgs{{height:{LEG_H}px;padding:0 {PAD}px;border-bottom:1px solid {C["edge"]};display:flex;
flex-direction:column;justify-content:center;gap:6px}}
.lr{{display:flex;align-items:center;gap:11px}}
.lr>*{{flex:none}}.lr .sp{{flex:1 1 auto}}
.tg{{display:flex;align-items:center;gap:4px;font-size:6.4px;font-weight:700;white-space:nowrap}}
.tg b{{width:6.5px;height:6.5px;border-radius:1.5px;display:block}}
.tg em{{font-style:normal;font-weight:400;color:{C["muted"]};margin-left:1px}}
.gt{{font-size:6.2px;color:{C["muted"]};font-weight:700;letter-spacing:.06em;white-space:nowrap}}
.gc{{display:flex;align-items:center;gap:3px;font-size:6.2px;color:{C["muted"]};white-space:nowrap}}
.gc b{{width:5.4px;height:5.4px;border-radius:50%;border:1.5px solid;display:block;background:#fff}}
.lr.b{{gap:5.5px;flex-wrap:wrap;row-gap:3px}}
.lr.b .lg{{gap:3px}}
.lr.b .sp{{flex:0 0 8px}}
.hl{{font-size:6px;letter-spacing:.12em;font-weight:700;color:{C["deep"]};white-space:nowrap}}
.lg{{display:flex;align-items:center;gap:3.5px;font-size:6.2px;white-space:nowrap}}
.lg u{{text-decoration:none;font-weight:700;color:{C["teal"]};background:#e2ecea;border-radius:5px;
padding:.5px 3.5px;font-family:"Helvetica Neue",Arial,SHS,sans-serif}}
.sw{{width:8px;height:6px;border:1px solid transparent;border-radius:1px;display:block;flex:none}}
.sw.ln{{height:2.2px;border:0;border-radius:1.1px}}
.sw.dsh{{background:repeating-linear-gradient(90deg,{C["purple"]} 0 2px,transparent 2px 3.6px)}}
.sw.dot{{width:6.4px;height:6.4px;border-radius:50%;border-width:1.6px;background:#fff}}
.sw.ht{{background:repeating-linear-gradient(45deg,rgba(23,124,120,.6) 0 .8px,{C["paper"]} .8px 2.6px);
border:1px solid {C["deep"]}}}
.cv{{display:flex;align-items:flex-start;gap:4px;font-size:6px;color:{C["muted"]};white-space:nowrap}}
.cv .cvn{{display:block;text-decoration:none;line-height:1.3}}
.cv .pv{{display:block;margin:1.6px 0 0}}
.cv b{{font-size:8.6px;color:{C["coral"]};font-family:"Helvetica Neue",Arial,SHS,sans-serif;
font-weight:700}}
.mn{{display:flex;gap:{GP}px;padding:{MAIN_T}px {PAD}px 0;height:{MAIN_H + MAIN_T}px}}
.colc{{display:flex;flex-direction:column;gap:{GP}px;flex:none}}
.rail{{margin-left:{COLGAP - GP}px;display:flex;flex-direction:column;gap:4px;flex:none}}
.pn{{background:#fff;border:1px solid {C["edge"]};border-radius:2.5px;overflow:hidden;flex:none}}
.pm{{position:relative;overflow:hidden}}
.mp{{position:absolute;left:0;top:0;display:block}}
.ovl{{position:absolute;inset:0}}
.ld{{position:absolute;left:0;top:0;display:block}}
.ph{{height:{PH}px;background:{C["deep"]};color:#fff;display:flex;align-items:center;gap:5px;
padding:0 6px;font-size:6.6px;font-weight:700;white-space:nowrap;overflow:hidden}}
.ph b{{font-size:6.6px;color:{C["onDarkEn"]};font-family:"Helvetica Neue",Arial,SHS,sans-serif;
letter-spacing:.06em}}
.ph u{{margin-left:auto;text-decoration:none;font-size:6px;font-weight:700;color:{C["onDarkEn"]};
letter-spacing:.04em;font-family:"Helvetica Neue",Arial,SHS,sans-serif}}
.nd{{position:absolute;width:7.4px;height:7.4px;margin:-3.7px 0 0 -3.7px;border:2px solid;
border-radius:50%;background:#fff;box-shadow:0 0 0 1.2px rgba(255,255,255,.95);display:block}}
.nd.sm{{width:5px;height:5px;margin:-2.5px 0 0 -2.5px;border-width:1.4px}}
.nl{{position:absolute;font-size:6.2px;font-weight:700;color:{C["deep"]};line-height:1.16;
white-space:nowrap;background:rgba(255,255,255,.88);border-radius:1.5px;padding:1px 2.5px}}
.nl b{{font-family:"Helvetica Neue",Arial,SHS,sans-serif;font-size:6.6px}}
.nl span{{display:block;font-size:6px;font-weight:400;color:{C["muted"]};
font-family:Menlo,"Helvetica Neue",SHS,monospace}}
.rt{{position:absolute;font-size:6px;font-weight:700;white-space:nowrap;
background:rgba(255,255,255,.9);border-radius:1.5px;padding:.8px 2.5px;
transform:translate(-50%,-50%)}}
.rt.spine{{color:{C["teal"]}}}.rt.alt{{color:{C["purple"]}}}.rt.cross{{color:#a4761a}}
.rt.vert{{writing-mode:vertical-rl;padding:2.5px .8px}}
.cal{{position:absolute;width:0;height:0}}
.cal .cvl{{position:absolute;left:-.5px;top:0;width:1px;background:{C["deep"]};display:block}}
.cal .ck{{position:absolute;left:-10px;width:20px;height:1.2px;background:{C["deep"]};display:block}}
.cal .cw{{position:absolute;height:1.2px;background:{C["purple"]};display:block}}
.cl{{position:absolute;left:5px;font-size:6.2px;font-weight:700;white-space:nowrap;
background:rgba(255,255,255,.93);border-radius:1.5px;padding:.4px 2px;transform:translateY(-50%)}}
.cl.on{{color:{C["coral"]}}}.cl.off{{color:{C["deep"]}}}
.cl.w{{color:{C["purple"]};font-size:6px;transform:translate(-100%,-50%)}}
.sb{{position:absolute;left:6px;bottom:6px;height:9px}}
.sb i{{position:absolute;bottom:0;width:50%;height:3px;border:.8px solid {C["deep"]};background:#fff}}
.sb i:nth-of-type(2){{left:50%;background:{C["deep"]}}}
.sb span{{position:absolute;bottom:4px;left:0;font-size:6px;color:{C["deep"]};font-weight:700;
font-family:"Helvetica Neue",Arial,SHS,sans-serif;white-space:nowrap;
background:rgba(255,255,255,.85);padding:0 1.5px}}
.na{{position:absolute;right:6px;top:6px;font-size:6px;font-weight:700;color:{C["deep"]};
text-align:center;background:rgba(255,255,255,.86);border-radius:1.5px;padding:0 2px}}
.na:before{{content:'';display:block;width:0;height:0;margin:0 auto 1px;border:3.2px solid transparent;
border-bottom-color:{C["deep"]};border-top:0}}
.loc{{display:flex;flex-direction:column;gap:3px;flex:none}}
.lh{{font-size:6.4px;font-weight:700;letter-spacing:.09em;color:{C["deep"]};line-height:1.3}}
.lh span{{display:block;font-size:6px;font-weight:400;letter-spacing:0;color:{C["muted"]};
margin-top:1.5px}}
.lm{{position:relative;background:#fff;border:1px solid {C["edge"]};border-radius:2.5px;
overflow:visible;flex:none}}
.lm .mp{{border-radius:2px}}
.ln{{font-size:6px;color:{C["muted"]};line-height:1.45;margin:0}}
.ln b{{color:{C["deep"]}}}
.kt{{position:absolute;display:flex;align-items:flex-start;gap:2.5px;transform:translateY(-50%);
z-index:3}}
.kt b{{font-size:5.6px;color:#fff;background:{C["coral"]};border-radius:5px;padding:.8px 3px;
font-family:"Helvetica Neue",Arial,SHS,sans-serif;flex:none}}
.kt span{{font-size:6px;font-weight:700;color:{C["deep"]};width:50px;line-height:1.2}}
.rs{{background:#fff;border:1px solid {C["edge"]};border-radius:2.5px;padding:0 0 3px;
overflow:hidden;display:flex;flex-direction:column;flex:none}}
.rs>.tp{{height:2.4px;flex:none}}
.rh{{padding:6px 8px 4px}}
.rh .n{{font-size:6px;letter-spacing:.15em;color:{C["teal"]};font-weight:700;
font-family:"Helvetica Neue",Arial,SHS,sans-serif}}
.rh h3{{font-size:8.6px;margin:3px 0 0;font-weight:700;line-height:1.22}}
.rh p{{font-size:6px;color:{C["muted"]};margin:2.5px 0 0;line-height:1.42}}
.cr{{display:grid;grid-template-columns:40px 1fr;gap:5px;padding:2.6px 8px;border-top:1px solid #f1ede3}}
.cr b{{font-size:6.2px;color:{C["deep"]};line-height:1.3}}
.cr span{{font-size:6px;color:{C["muted"]};line-height:1.34}}
.warn{{margin:5px 8px 0;padding:4.5px 6px;background:#fdf1ee;border-left:2.2px solid {C["coral"]};
color:{C["coral"]};font-size:6px;line-height:1.4;font-weight:700}}
.th,.tr{{display:grid;grid-template-columns:9px 41px 15px 1fr 21px;gap:4px;align-items:center;
padding:0 8px}}
.th{{font-size:6px;letter-spacing:.05em;color:{C["muted"]};font-weight:700;padding-bottom:2.5px;
font-family:"Helvetica Neue",Arial,SHS,sans-serif}}
.tr{{padding-top:2.4px;padding-bottom:2.4px;border-top:1px solid #f1ede3}}
.tr.hot{{background:#fdf4f1}}
.c0{{font-size:6.4px;color:{C["muted"]};font-family:"Helvetica Neue",Arial,SHS,sans-serif;
font-weight:700}}
.tr.hot .c0{{color:{C["coral"]}}}
.c1{{font-size:6.6px;font-weight:700;color:{C["deep"]};font-family:Menlo,"Helvetica Neue",SHS,monospace}}
.c1 i{{font-style:normal;color:{C["muted"]};font-weight:400;margin-left:2.5px;font-size:6px}}
.c2{{font-size:6px;font-weight:700;text-align:center;
font-family:"Helvetica Neue",Arial,SHS,sans-serif}}
.tr .c2{{border:.9px solid;border-radius:4px;padding:.6px 0}}
.c3{{position:relative;height:9px;display:flex;align-items:center;background:#f4f1e8;border-radius:1.5px}}
.c3 i{{position:absolute;left:0;top:0;bottom:0;background:{C["coral"]};opacity:.34;border-radius:1.5px}}
.c3 b{{position:relative;font-size:6.4px;color:{C["deep"]};padding-left:3px;
font-family:"Helvetica Neue",Arial,SHS,sans-serif;font-variant-numeric:tabular-nums}}
.c4{{font-size:6px;color:{C["muted"]};text-align:right;
font-family:"Helvetica Neue",Arial,SHS,sans-serif;font-variant-numeric:tabular-nums}}
.tu{{display:flex;justify-content:space-between;align-items:baseline;gap:5px;margin:3px 8px 0;padding-top:3px;
border-top:1.4px solid {C["deep"]};font-size:6.2px;color:{C["deep"]};font-weight:700}}
.tu b{{font-size:7px;font-family:"Helvetica Neue",Arial,SHS,sans-serif}}
.fab{{display:flex;align-items:center;gap:5px;margin:4px 8px 0;padding:3.5px 5px;background:#fdf1ee;border-radius:2px}}
.fab b{{font-size:6px;color:{C["coral"]};font-weight:700;white-space:nowrap}}
.fab span{{font-size:6.2px;font-weight:700;color:{C["deep"]};letter-spacing:.03em;font-family:Menlo,"Helvetica Neue",SHS,monospace}}
.tn{{margin:3px 8px 0;font-size:6px;color:{C["muted"]};line-height:1.38}}
.eqw{{display:grid;grid-template-columns:1fr 11px 1fr;gap:4px;padding:1px 8px 0}}
.eq{{border-radius:2px;padding:4.5px 5px}}
.eq.on{{background:#e4efed;border-left:2px solid {C["teal"]}}}
.eq.off{{background:#ece9f2;border-left:2px solid {C["purple"]}}}
.eq b{{display:block;font-size:6.6px;font-weight:700;letter-spacing:.03em;
font-family:"Helvetica Neue",Arial,SHS,sans-serif}}
.eq.on b{{color:{C["teal"]}}}.eq.off b{{color:{C["purple"]}}}
.eq span{{display:block;font-size:6px;color:{C["muted"]};line-height:1.38;margin-top:2px}}
.eqs{{display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:700;
color:{C["deep"]}}}
.claim{{margin:4px 8px 0;font-size:6.2px;font-weight:700;color:{C["coral"]};line-height:1.34}}
.sqw{{display:grid;grid-template-columns:1fr 1fr;gap:3.5px;padding:3px 8px 0}}
.sq{{border:1px solid {C["edge"]};border-radius:2px;padding:3.5px 4.5px;background:#fdfcf9}}
.sq b{{display:block;font-size:7.2px;color:{C["deep"]};line-height:1;
font-family:"Helvetica Neue",Arial,SHS,sans-serif;font-variant-numeric:tabular-nums}}
.sq span{{display:block;font-size:6px;color:{C["muted"]};margin-top:2px;line-height:1.25}}
.ft{{padding:5px {PAD}px 0;height:{FOOT_H}px}}
.pv{{display:inline-block;font-style:normal;font-weight:700;font-size:5.4px;
letter-spacing:.02em;color:{C["coral"]};background:#fdf1ee;border-radius:3px;
padding:.6px 3px;margin-left:4px;white-space:nowrap;line-height:1.3;vertical-align:.4px}}
.sq .pv,.lh .pv{{display:block;margin:2.5px 0 0;white-space:normal}}
.ptr{{color:{C["deep"]};font-weight:700}}
.disc{{margin:0;font-size:6px;color:{C["coral"]};line-height:1.4}}
.fr{{margin-top:4px;padding-top:4px;border-top:1px solid {C["edge"]};display:flex;
justify-content:space-between;font-size:6px;color:{C["muted"]}}}
.fx{{font-weight:700;color:{C["deep"]};letter-spacing:.1em}}
"""


EN_CSS = """
.ln{line-height:1.32}
.lh span{line-height:1.3}
.cr{grid-template-columns:31px 1fr;padding:2.3px 8px}
.cr span{line-height:1.3}
.warn{line-height:1.33;padding:4px 6px}
.rh p{line-height:1.34}
.tn{line-height:1.3}
.eq span{line-height:1.3}
.rh h3{font-size:8.2px}
"""


def fontface(htmls):
    d, cf = os.path.join(HERE, "fonts"), os.path.join(HERE, "chars.txt")
    chars = "".join(sorted({c for c in "".join(htmls) if ord(c) > 31}))
    os.makedirs(d, exist_ok=True)
    io.open(cf, "w", encoding="utf-8").write(chars)
    subprocess.run([PY, MKFONT, cf, d], check=True, capture_output=True)
    return "".join(
        f"@font-face{{font-family:SHS;font-weight:{w};font-style:normal;src:url("
        f"data:font/ttf;base64,"
        f"{base64.b64encode(open(os.path.join(d, f'shs-{w}.ttf'), 'rb').read()).decode()}"
        f") format('truetype')}}" for w in ("400", "500", "700"))


def main():
    docs = {l: build(l) for l in ("zh", "en")}
    face = fontface(list(docs.values()))
    for l, doc in docs.items():
        p = os.path.join(HERE, f"fig-{l}.html")
        io.open(p, "w", encoding="utf-8").write(doc.replace("__FONTFACE__", face))
        print("wrote", p, f"{len(doc) / 1024:.0f} KB body")


if __name__ == "__main__":
    main()

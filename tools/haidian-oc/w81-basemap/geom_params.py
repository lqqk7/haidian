# -*- coding: utf-8 -*-
"""五张图版各自的图面投影，逐字复刻各自生成器的算式。

site / land-use  : wpn2b/wp4b/build/{sitefig,landusefig}.js
dual-state       : wpv70/dsp/build.py
mobility         : wpr6/wpe2/build.py（EPSG:4548，viewBox 自带 data-ox/oy/mpp）
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import json
import math
import os

PKG = str(_HaidianPath(__file__).resolve().parents[3] / 'submissions/lqqk7/every-sense-jingzhang')

MLAT = 110540.0
MLON = 111320.0 * math.cos(math.radians(39.98))


def gj(name):
    with open(os.path.join(PKG, "geometry", name + ".geojson"), encoding="utf-8") as f:
        return json.load(f)["features"]


_site_ring = gj("site_boundary")[0]["geometry"]["coordinates"][0]
LATS = [c[1] for c in _site_ring]
LONS = [c[0] for c in _site_ring]
LAT0, LAT1 = min(LATS), max(LATS)
LON0, LON1 = min(LONS), max(LONS)


# ----------------------------------------------------------- 01 site-overview
def site_overview():
    W, H = 1140.0, 264.0
    s = (W - 44) / ((LAT1 - LAT0) * MLAT)
    y0 = (H - (LON1 - LON0) * MLON * s) / 2

    def to_px(lon, lat):
        return (22 + (lat - LAT0) * MLAT * s, y0 + (lon - LON0) * MLON * s)

    return dict(to_px=to_px, clip=(0, 0, W, H), mpp=1 / s, W=W, H=H)


# ------------------------------------------------------ 02 land-use main band
def landuse_main():
    W, H = 1140.0, 202.5
    s = (W - 24) / ((LAT1 - LAT0) * MLAT)
    y0 = (H - (LON1 - LON0) * MLON * s) / 2

    def to_px(lon, lat):
        return (12 + (lat - LAT0) * MLAT * s, y0 + (lon - LON0) * MLON * s)

    return dict(to_px=to_px, clip=(0, 0, W, H), mpp=1 / s, W=W, H=H)


# ---------------------------------------------------------- 02b land-use 插图
def landuse_inset(idx):
    W, H = 370.0, 134.0
    rid = ["ROAD-002", "ROAD-003", "ROAD-004"][idx]
    xr = next(r for r in gj("roads") if r["properties"]["id"] == rid)
    ctr_lat = xr["geometry"]["coordinates"][0][1]
    ctr_lon = 116.3458
    mppx = 250.0 / 75.0
    span_lon = (W * mppx) / MLON
    span_lat = (H * mppx) / MLAT

    def to_px(lon, lat):
        x = (lon - (ctr_lon - span_lon / 2)) / span_lon * W
        y = H - (lat - (ctr_lat - span_lat / 2)) / span_lat * H
        return (x, y)

    return dict(to_px=to_px, clip=(0, 0, W, H), mpp=mppx, W=W, H=H)


# ------------------------------------------------------- 07 dual-state (dsp)
def dual_state():
    DLON0, DLAT0 = 116.3475, 39.9827

    def proj(lon, lat):
        return (lon - DLON0) * MLON, (lat - DLAT0) * MLAT

    pts = [proj(c[0], c[1]) for c in _site_ring]
    xmin = min(p[0] for p in pts)
    xmax = max(p[0] for p in pts)
    ymin = min(p[1] for p in pts)
    ymax = max(p[1] for p in pts)
    span_x, span_y = xmax - xmin, ymax - ymin
    MAP_W, MAP_H, MX, MY = 1150.0, 177.0, 12.0, 11.0
    S = max(span_y / (MAP_W - 2 * MX), span_x / (MAP_H - 2 * MY))
    OX = (MAP_W - span_y / S) / 2.0
    OY = (MAP_H - span_x / S) / 2.0

    def to_px(lon, lat):
        x, y = proj(lon, lat)
        return ((y - ymin) / S + OX, (x - xmin) / S + OY)

    return dict(to_px=to_px, clip=(0, 0, MAP_W, MAP_H), mpp=S, W=MAP_W, H=MAP_H)


# --------------------------------------------- 06 mobility-bluegreen (EPSG:4548)
def mobility_panel(viewbox):
    """viewbox: (vx, vy, vw, vh)，SVG 用户单位 = 米，原点偏移见 build.py。"""
    from pyproj import Transformer
    tf = Transformer.from_crs("EPSG:4326", "EPSG:4548", always_xy=True).transform
    ORX, ORY = 444000.0, 4428000.0
    vx, vy, vw, vh = viewbox

    def to_px(lon, lat):
        X, Y = tf(lon, lat)
        return (X - ORX, ORY - Y)

    return dict(to_px=to_px, clip=(vx, vy, vx + vw, vy + vh), W=vw, H=vh)


if __name__ == "__main__":
    for name, f in (("site", site_overview()), ("lu", landuse_main()),
                    ("dsp", dual_state())):
        print(name, "mpp=%.3f" % f["mpp"], "clip", f["clip"],
              "site corner ->", tuple(round(v, 2) for v in f["to_px"](LON0, LAT0)))
    for i in range(3):
        f = landuse_inset(i)
        print("inset%d" % i, "mpp=%.3f" % f["mpp"])

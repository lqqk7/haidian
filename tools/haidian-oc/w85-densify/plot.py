# -*- coding: utf-8 -*-
"""把 OSM 底图 + 旧线位 + 新线位画成 SVG，供目视核查。"""
from pathlib import Path as _HaidianPath
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
PKG=str(_HaidianPath(__file__).resolve().parents[3] / 'submissions/lqqk7/every-sense-jingzhang')
HERE=os.path.dirname(os.path.abspath(__file__))
ways=[]
for p in ("part1","part2"):
    ways+=json.load(open(os.path.join(PKG,"visual/assets/osm-fabric","osm-fabric-snapshot-%s.json"%p),encoding="utf-8"))["ways"]
base=json.load(open(os.path.join(HERE,"roads.baseline.geojson"),encoding="utf-8"))
rep=json.load(open(os.path.join(HERE,"densify-report.json"),encoding="utf-8"))
nodes=json.load(open(os.path.join(PKG,"geometry/constraints.geojson"),encoding="utf-8"))["features"]
X0,X1,Y0,Y1=116.336,116.358,39.9385,40.0265
W=900; H=int(W*(Y1-Y0)/(X1-X0)*1.3)
def px(c): return ((c[0]-X0)/(X1-X0)*W, H-(c[1]-Y0)/(Y1-Y0)*H)
out=['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d"><rect width="%d" height="%d" fill="#fff"/>'%(W,H,W,H,W,H)]
for w in ways:
    if not w[1]: continue
    pts=" ".join("%.1f,%.1f"%px(c) for c in w[5])
    col="#c8c8c8" if w[1] in ("footway","service","path","steps") else "#9aa5b1"
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="0.6"/>'%(pts,col))
for f in base["features"]:
    pts=" ".join("%.1f,%.1f"%px(c) for c in f["geometry"]["coordinates"])
    out.append('<polyline points="%s" fill="none" stroke="#d76450" stroke-width="1.6" stroke-dasharray="5 4"/>'%pts)
COL={"ROAD-001":"#1d6fb8","ROAD-002":"#6b5b95","ROAD-003":"#2e8b57","ROAD-004":"#d6a13b","ROAD-005":"#c2185b"}
for rid,d in rep.items():
    pts=" ".join("%.1f,%.1f"%px(c) for c in d["coords"])
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'%(pts,COL[rid]))
    for c in d["coords"]:
        x,y=px(c); out.append('<circle cx="%.1f" cy="%.1f" r="2.2" fill="%s"/>'%(x,y,COL[rid]))
for f in nodes:
    x,y=px(f["geometry"]["coordinates"])
    out.append('<circle cx="%.1f" cy="%.1f" r="4" fill="none" stroke="#000" stroke-width="1.4"/>'%(x,y))
    out.append('<text x="%.1f" y="%.1f" font-size="9">%s</text>'%(x+6,y+3,f["properties"]["id"]))
out.append("</svg>")
open(os.path.join(HERE,"plot.svg"),"w").write("".join(out))
print("ok",W,H)

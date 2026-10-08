# -*- coding: utf-8 -*-
"""复算 FAB-03 街块面集合，并按 district-strategy.json 的候选质心/面积匹配面。"""
from pathlib import Path as _HaidianPath
import json, os, pickle
from shapely.geometry import LineString, Polygon, shape
from shapely.ops import polygonize, transform as shp_transform
from pyproj import Transformer

PKG = str(_HaidianPath(__file__).resolve().parents[3] / 'submissions/lqqk7/every-sense-jingzhang')
SNAP = os.path.join(PKG, "visual/assets/osm-fabric")
EXCL = {"bus_guideway","construction","elevator","escape","motorway","motorway_link",
        "platform","proposed","raceway","trunk","trunk_link"}

def load_ways():
    ways=[]
    for p in ("osm-fabric-snapshot-part1.json","osm-fabric-snapshot-part2.json"):
        d=json.load(open(os.path.join(SNAP,p),encoding="utf-8"))
        ways+=d["ways"]
    return ways

def main():
    ways=load_ways()
    segs=[]
    n_walk=0
    for w in ways:
        hw=w[1]
        if hw is None or hw in EXCL: continue
        n_walk+=1
        cs=w[5]
        for a,b in zip(cs,cs[1:]):
            if a!=b: segs.append(LineString([a,b]))
    print("walkable ways:",n_walk,"segments:",len(segs))
    faces=list(polygonize(segs))
    print("polygonized_total:",len(faces))
    fwd=Transformer.from_crs("EPSG:4326","EPSG:4548",always_xy=True).transform
    site=shape(json.load(open(os.path.join(PKG,"geometry/site_boundary.geojson")))["features"][0]["geometry"])
    recs=[]
    for f in faces:
        rp=f.representative_point()
        inside = site.contains(rp)
        fp = shp_transform(fwd, f)
        recs.append(dict(area=fp.area, perim=fp.length, inside=inside,
                         cen=(f.centroid.x, f.centroid.y), poly=f))
    ins=[r for r in recs if r["inside"]]
    print("block_count_in_site:",len(ins))
    ar=sorted(r["area"] for r in ins)
    n=len(ar); med = ar[n//2] if n%2 else (ar[n//2-1]+ar[n//2])/2
    print("median:",round(med,3),"total:",round(sum(ar),3),"largest:",round(max(ar),3))
    pickle.dump([(r["area"],r["perim"],r["cen"],list(r["poly"].exterior.coords),r["inside"]) for r in recs],
                open(os.path.dirname(os.path.abspath(__file__))+"/faces.pkl","wb"))

main()

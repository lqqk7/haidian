# -*- coding: utf-8 -*-
"""交付 ④ 复核：绿地包络 ∩ 公共空间包络（EPSG:4548 平面米）。"""
from pathlib import Path as _HaidianPath
import json, os
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform, unary_union

PKG = str(_HaidianPath(__file__).resolve().parents[3] / 'submissions/lqqk7/every-sense-jingzhang')
TF = Transformer.from_crs("EPSG:4326", "EPSG:4548", always_xy=True).transform


def u(name):
    fs = json.load(open(os.path.join(PKG, "geometry", name + ".geojson"), encoding="utf-8"))["features"]
    return unary_union([transform(lambda x, y, z=None: TF(x, y), shape(f["geometry"])) for f in fs])


site, green, pub = u("site_boundary"), u("green_space"), u("public_space")
inter = green.intersection(pub)
print("site   %.3f   （登记 11,412,825.386）" % site.area)
print("green  %.3f   （登记  2,432,035.047）" % green.area)
print("public %.3f   （登记  2,074,629.805）" % pub.area)
print("inter  %.3f   （登记    448,404.185 / 旧印 452,986.656）" % inter.area)
print("green_ratio  %.4f%%  public_ratio %.4f%%" % (green.area/site.area*100, pub.area/site.area*100))
print("overlap_share %.4f%%  （旧印 3.9691%%）" % (inter.area/site.area*100))

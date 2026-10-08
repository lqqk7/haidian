# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gapcalc_lib import *   # noqa
from shapely.geometry import LineString
from shapely.ops import unary_union, substring

# 支线长度
for nid, sid, gate, p in nodes:
    best = min(((s.distance(p), k) for k, (a, b, s) in enumerate(edges)))
    print("%s spur %.2f m" % (nid, best[0]))

def dom(pt, budget, mode):
    """mode: 'std' 支线计入预算；'free' 支线不计入预算；'circle' 支线超预算时退化为节点圆。"""
    best = None
    for k, (a, b, s) in enumerate(edges):
        d = s.distance(pt)
        if best is None or d < best[0]:
            best = (d, k, s.project(pt))
    spur_len, ek, t = best
    if mode == 'free':
        rem = budget
    else:
        rem = budget - spur_len
    if rem <= 0:
        if mode == 'circle':
            return pt.buffer(W, quad_segs=QS)
        return None
    return unary_union([l.buffer(W, quad_segs=QS) for l in reach_lines_from(pt, ek, t, spur_len, rem)])

def reach_lines_from(pt, ek, t, spur_len, rem):
    import heapq
    a, b, s = edges[ek]
    out = []
    if spur_len > 1e-9:
        out.append(LineString([(pt.x, pt.y), s.interpolate(t).coords[0]]))
    lo, hi = max(0.0, t - rem), min(s.length, t + rem)
    if hi > lo:
        out.append(substring(s, lo, hi))
    dist, pq = {}, []
    if rem - t > 0: heapq.heappush(pq, (rem - t, a))
    if rem - (s.length - t) > 0: heapq.heappush(pq, (rem - (s.length - t), b))
    while pq:
        left, v = heapq.heappop(pq)
        if dist.get(v, -1) >= left: continue
        dist[v] = left
        for (u, k, L) in adj[v]:
            e = edges[k][2]
            if L <= left:
                out.append(e); nl = left - L
                if nl > dist.get(u, -1): heapq.heappush(pq, (nl, u))
            else:
                out.append(substring(e, 0, left) if edges[k][0] == v
                           else substring(e, e.length - left, e.length))
    return out

for mode in ('std', 'free', 'circle'):
    offs = []
    per = {}
    for nid, sid, gate, p in nodes:
        d = dom(p, R_OFF, mode)
        per[nid] = 0.0 if d is None else d.area
        if d is not None: offs.append(d)
    U = unary_union(offs)
    print("mode=%-7s OFF union = %.1f   (target 257208)" % (mode, U.area))
    print("   ", {k: round(v) for k, v in per.items()})

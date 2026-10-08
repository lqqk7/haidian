# -*- coding: utf-8 -*-
"""十节点差集审计台账最终复算（口径已对上图版四个汇总值与前三行）。

规则（由汇总值反解并逐值命中）：
  接入支线长度计入行程预算；若支线长度已超出预算，可达线形退化为该支线
  被预算截断的一段（网络部分为空）。
"""
import json, os, sys, heapq
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gapcalc_lib import *   # noqa
from shapely.geometry import LineString
from shapely.ops import unary_union, substring

def access(pt):
    return min(((s.distance(pt), k, s.project(pt)) for k, (a, b, s) in enumerate(edges)))

def net_lines(ek, t, rem):
    a, b, s = edges[ek]; out = []
    lo, hi = max(0.0, t - rem), min(s.length, t + rem)
    if hi > lo: out.append(substring(s, lo, hi))
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

def dom(pt, budget):
    sl, ek, t = access(pt)
    spur = LineString([(pt.x, pt.y), edges[ek][2].interpolate(t).coords[0]]) if sl > 1e-9 else None
    rem = budget - sl
    if rem > 0:
        L = ([spur] if spur else []) + net_lines(ek, t, rem)
    else:
        L = [substring(spur, 0, budget)]
    return unary_union([x.buffer(W, quad_segs=QS) for x in L]), sl

rows = []
ONs, OFFs = [], []
for nid, sid, gate, p in nodes:
    don, sl = dom(p, R_ON)
    doff, _ = dom(p, R_OFF)
    ONs.append(don); OFFs.append(doff)
    g = don.difference(doff)
    rows.append(dict(id=nid, sid=sid, gate=gate, spur=round(sl, 2),
                     on=don.area, off=doff.area, gap=g.area,
                     share=g.area / don.area * 100))
ON, OFF = unary_union(ONs), unary_union(OFFs)
GAP = ON.difference(OFF)
rows.sort(key=lambda r: -r["gap"])
summary = dict(network_length_m=sum(e[2].length for e in edges),
               on_union=ON.area, off_union=OFF.area, gap_union=GAP.area,
               gap_share_pct=GAP.area / ON.area * 100,
               site_area=None)
print("network %.1f  ON %.3f  OFF %.3f  GAP %.3f  share %.6f%%"
      % (summary["network_length_m"], ON.area, OFF.area, GAP.area, summary["gap_share_pct"]))
print("%-7s %-4s %-3s %8s %10s %10s %10s %7s" % ("id","sid","G","spur","on","off","gap","share"))
for r in rows:
    print("%-7s %-4s %-3s %8.2f %10.1f %10.1f %10.1f %6.1f%%  ->  %s / %.1f%%"
          % (r["id"], r["sid"], r["gate"], r["spur"], r["on"], r["off"], r["gap"],
             r["share"], format(round(r["gap"]), ","), r["share"]))
json.dump(dict(summary=summary, rows=rows),
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gap-audit-data.json"), "w"),
          indent=1, ensure_ascii=False)

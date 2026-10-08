# -*- coding: utf-8 -*-
import os, sys, heapq, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gapcalc_lib import *   # noqa
from shapely.geometry import LineString
from shapely.ops import unary_union, substring

def access(pt):
    best = None
    for k, (a, b, s) in enumerate(edges):
        d = s.distance(pt)
        if best is None or d < best[0]:
            best = (d, k, s.project(pt))
    return best  # (spur_len, edge_idx, t)

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

def spur_line(pt, ek, t):
    return LineString([(pt.x, pt.y), edges[ek][2].interpolate(t).coords[0]])

VAR = {}
def build(pt, budget, rule):
    sl, ek, t = access(pt)
    rem = budget - sl
    L = []
    if rem > 0:
        if sl > 1e-9: L.append(spur_line(pt, ek, t))
        L += net_lines(ek, t, rem)
    else:
        if rule == 'none':      pass
        elif rule == 'circle':  return pt.buffer(W, quad_segs=QS)
        elif rule == 'fullspur':L.append(spur_line(pt, ek, t))
        elif rule == 'cutspur':
            g = spur_line(pt, ek, t)
            L.append(substring(g, 0, min(budget, g.length)))
        elif rule == 'disc':    return pt.buffer(budget, quad_segs=QS)
    if not L: return None
    return unary_union([x.buffer(W, quad_segs=QS) for x in L])

on = unary_union([build(p, R_ON, 'none') for _,_,_,p in nodes])
print("ON = %.3f   target 482267" % on.area)
for rule in ('none','circle','fullspur','cutspur','disc'):
    ds = [build(p, R_OFF, rule) for _,_,_,p in nodes]
    U = unary_union([d for d in ds if d is not None])
    gap = on.difference(U)
    print("%-9s OFF=%10.1f (t 257208)  GAP=%10.1f (t 225058)  share=%.4f%% (t 46.67)"
          % (rule, U.area, gap.area, gap.area/on.area*100))

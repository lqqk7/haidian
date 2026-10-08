# -*- coding: utf-8 -*-
"""触觉走廊图的几何泛化：简化 → 平滑 → 位移，全部量登记后由图注如实印出。

触觉印刷与墨印的区别在于分辨率：指尖的横向分辨能力约 2—3 mm，两条平行凸线
低于该间距即读成一条。包内 roads.geojson 的两条纵向线位在图面最近处只差
62 m（本图比例尺下 7.0 px ≈ 3.5 mm），墨印可读、触摸不可读。因此本图对线位
做三步泛化，每一步的量都记进 report() 并印在图上：

  1. Douglas-Peucker 简化：去掉低于指尖分辨率的摆动，保留走向证据；
  2. Chaikin 平滑：转角圆化，避免尖角被读成端点；
  3. 位移：把安静线沿主脊法向外推，直到两线净间距达到设计目标值。

端点不参与位移，主脊不动——位移全部落在安静线上，方向恒为远离主脊。
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import math
import sys

sys.path.insert(0, str(_HaidianPath(__file__).resolve().parents[1] / 'w81-basemap'))


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def seg_dist(q, a, b):
    ax, ay = a
    bx, by = b
    qx, qy = q
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((qx - ax) * dx + (qy - ay) * dy) / L))
    fx, fy = ax + t * dx, ay + t * dy
    return math.hypot(qx - fx, qy - fy), (fx, fy)


def poly_dist(q, poly):
    """点到折线的最短距离与最近点。"""
    best = None
    for i in range(len(poly) - 1):
        d, f = seg_dist(q, poly[i], poly[i + 1])
        if best is None or d < best[0]:
            best = (d, f)
    return best


def dp(pts, tol):
    """Douglas-Peucker，端点不动。"""
    if len(pts) < 3:
        return list(pts)
    a, b = pts[0], pts[-1]
    k, dmax = 0, -1.0
    for i in range(1, len(pts) - 1):
        d, _ = seg_dist(pts[i], a, b)
        if d > dmax:
            k, dmax = i, d
    if dmax <= tol:
        return [a, b]
    return dp(pts[:k + 1], tol)[:-1] + dp(pts[k:], tol)


def chaikin(pts, rounds=1, ratio=0.25):
    """转角切角平滑；端点保留。"""
    out = list(pts)
    for _ in range(rounds):
        new = [out[0]]
        for i in range(len(out) - 1):
            (x0, y0), (x1, y1) = out[i], out[i + 1]
            new.append((x0 + ratio * (x1 - x0), y0 + ratio * (y1 - y0)))
            new.append((x0 + (1 - ratio) * (x1 - x0), y0 + (1 - ratio) * (y1 - y0)))
        new.append(out[-1])
        out = new
    return out


def displace(movable, fixed, target, passes=14):
    """把 movable 沿远离 fixed 的方向外推，直到逐点距离达到 target。

    端点不动（首尾各一个顶点锁定），推移量沿链做三角权重扩散，避免出现折角。
    """
    pts = [list(p) for p in movable]
    n = len(pts)
    for _ in range(passes):
        push = [0.0] * n
        vec = [(0.0, 0.0)] * n
        worst = 0.0
        for i in range(n):
            d, f = poly_dist(tuple(pts[i]), fixed)
            if d < target:
                need = target - d
                worst = max(worst, need)
                if d < 1e-6:
                    ux, uy = 0.0, 1.0
                else:
                    ux, uy = (pts[i][0] - f[0]) / d, (pts[i][1] - f[1]) / d
                push[i] = need
                vec[i] = (ux, uy)
        if worst < 1e-3:
            break
        for i in range(n):
            if push[i] <= 0:
                continue
            for j in range(max(1, i - 2), min(n - 1, i + 2) + 1):
                w = 1.0 - abs(i - j) / 3.0
                pts[j][0] += vec[i][0] * push[i] * w * 0.55
                pts[j][1] += vec[i][1] * push[i] * w * 0.55
    return [tuple(p) for p in pts]


def max_dev(orig, new):
    """新线相对原线的最大偏移（逐点到原折线的距离）。"""
    return max(poly_dist(q, orig)[0] for q in new)


def length(pts):
    return sum(dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))

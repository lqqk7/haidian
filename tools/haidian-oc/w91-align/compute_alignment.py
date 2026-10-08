#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""万感京张 空间对齐参考读数 —— 复算脚本（自足单文件）。

输入（全部取自提交包内既有文件，不发起任何网络请求，不引入任何新抓取）：
  visual/assets/osm-fabric/osm-fabric-snapshot-part1.json  OSM 精简快照 第一片
  visual/assets/osm-fabric/osm-fabric-snapshot-part2.json  OSM 精简快照 第二片
  geometry/roads.geojson            五条慢行中心线（本文件用 ROAD-001 与 ROAD-005）
  geometry/site_boundary.geojson    临时总体设计范围 SITE-001
  geometry/constraints.geojson      十个独立完成节点 OP-01..OP-10

输出：
  visual/assets/alignment-reference.json

口径：与本包 osm-fabric-readings.json 的 DEV-01 完全一致——沿提交中心线每 25 m 取一
采样点（末段不足 25 m 时补一个终点采样），在 EPSG:4548 平面上量算采样点到廊道中心线
的最短欧氏距离，登记中位数、P90、最大值、最小值、均值与样本数，分位数按线性插值。
唯一新增的限制是数据带截断：快照中廊道要素的最北顶点纬度为 40.007178，其以北无廊道
数据，故纬度高于该值的采样点一律不出读数，也不外推。

依赖：shapely >= 2.0，pyproj >= 3.0。
用法：python3 compute_alignment.py（ESJZ_PKG 环境变量可覆盖提交包路径）
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import hashlib
import json
import os

from pyproj import Transformer
from shapely.geometry import LineString, Point, shape
from shapely.ops import transform as shp_transform, unary_union

PKG = os.environ.get(
    "ESJZ_PKG",
    str(_HaidianPath(__file__).resolve().parents[3] / 'submissions/lqqk7/every-sense-jingzhang'),
)
OUT = os.path.join(PKG, "visual/assets/alignment-reference.json")
CORRIDOR_NAMES = ("京包线", "京包客专线")
SAMPLE_STEP_M = 25.0
CRS_SRC, CRS_DST = "EPSG:4326", "EPSG:4548"

_fwd = Transformer.from_crs(CRS_SRC, CRS_DST, always_xy=True)
_inv = Transformer.from_crs(CRS_DST, CRS_SRC, always_xy=True)


# ------------------------------------------------------------------ 基础工具
def r3(x):
    return round(float(x), 3)


def r6(x):
    return round(float(x), 6)


def project(coords):
    return [_fwd.transform(lon, lat) for lon, lat in coords]


def percentile(values, q):
    """线性插值分位数，与 osm-fabric-readings.json 同法。"""
    v = sorted(values)
    k = (len(v) - 1) * q
    lo = int(k)
    hi = min(lo + 1, len(v) - 1)
    return v[lo] if lo == hi else v[lo] + (v[hi] - v[lo]) * (k - lo)


def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_json(rel):
    with open(os.path.join(PKG, rel), encoding="utf-8") as f:
        return json.load(f)


def sample_points(line, step=SAMPLE_STEP_M):
    """自线起点每 step 米取一点；末段不足 step 时补一个终点采样。"""
    out, d, total = [], 0.0, line.length
    while d < total:
        out.append((d, line.interpolate(d)))
        d += step
    out.append((total, line.interpolate(total)))
    return out


def offset_reading(line_px, corridor, lat_max):
    rows = []
    for chainage, pt in sample_points(line_px):
        lon, lat = _inv.transform(pt.x, pt.y)
        rows.append({"chainage_m": chainage, "lon": lon, "lat": lat,
                     "distance_m": pt.distance(corridor)})
    inside = [r for r in rows if r["lat"] <= lat_max]
    outside = [r for r in rows if r["lat"] > lat_max]
    d = [r["distance_m"] for r in inside]
    far = max(inside, key=lambda r: r["distance_m"])
    near = min(inside, key=lambda r: r["distance_m"])
    return {
        "median_m": r3(percentile(d, 0.5)),
        "p90_m": r3(percentile(d, 0.9)),
        "max_m": r3(max(d)),
        "min_m": r3(min(d)),
        "mean_m": r3(sum(d) / len(d)),
        "sample_count": len(inside),
        "sample_count_total": len(rows),
        "sample_count_outside_data_band": len(outside),
        "max_offset_location": {"lon": r6(far["lon"]), "lat": r6(far["lat"]),
                                "chainage_m": r3(far["chainage_m"]),
                                "distance_m": r3(far["distance_m"])},
        "min_offset_location": {"lon": r6(near["lon"]), "lat": r6(near["lat"]),
                                "chainage_m": r3(near["chainage_m"]),
                                "distance_m": r3(near["distance_m"])},
    }


# ------------------------------------------------------------------ 固定文本
DECLARATION_ZH = [
    "本文件全部读数为 OpenStreetMap 快照时点的计算值，状态为 PROVISIONAL（临时）；读数不是现场测量结果，不是官方测绘或规划数据，不构成任何规划结论、设计依据或合规判定。",
    "声明一：本文件所称「遗址公园廊道参考线」是 OpenStreetMap 登记的铁路廊道中心线，不是遗址公园红线，不是公园边界，不代表真实情况。京张铁路遗址公园的法定范围、用地边界与建成范围均不在本包任何数据内，本文件不掌握、不推断、也不主张任何一项。",
    "声明二：本包快照的 Overpass 查询只取 highway 与 railway 两类要素（逐字查询语句见快照 part1 的 meta.provenance）。产生仓库议题 #846 中 412.5 米读数的公园多边形（leisure=park）不在本包数据内，本文件因此无法复核该数值，也不以任何读数替代它。",
    "声明三：本文件廊道数据的纬度带止于 40.007178（快照中廊道要素的最北顶点），以北无覆盖。凡采样点或节点纬度高于该值者，一律不出读数、不外推、不以到最近端点的距离顶替；四项读数各自登记被截断的样本数。",
    "方法阈值（采样间距 25 米、量算坐标系 EPSG:4548、分位数线性插值）沿用本包 osm-fabric-readings.json 的 DEV-01 口径，属本包方法选择而非规范强制值；改变阈值将改变读数。",
    "数值登记精度：读数保留三位小数，经纬度坐标保留六位小数（约 0.11 米），与快照坐标精度一致。登记精度不代表测量精度，OpenStreetMap 社区数据的实际定位误差远大于登记位数。",
]

DECLARATION_EN = [
    "Every reading in this file is a value computed at the timestamp of the OpenStreetMap snapshot; its status is PROVISIONAL. The readings are not field measurements, not official survey or planning data, and constitute no planning conclusion, design basis, or compliance determination.",
    "Statement one: the \"heritage park corridor reference line\" named in this file is the centreline of the rail corridor as registered in OpenStreetMap. It is not the heritage park's redline, not the park boundary, and does not represent the real situation. The statutory extent, land boundary and as-built extent of the Jing-Zhang Railway Heritage Park are absent from every dataset in this package; this file neither holds, infers, nor asserts any of them.",
    "Statement two: the Overpass query behind this package's snapshot retrieves only highway and railway features (the verbatim query is in meta.provenance of snapshot part1). The park polygon (leisure=park) that produced the 412.5 m figure in repository issue #846 is not in this package's data, so this file cannot re-check that figure and substitutes no reading for it.",
    "Statement three: the corridor data in this file stops at latitude 40.007178, the northernmost corridor vertex in the snapshot; there is no coverage north of it. Sample points and nodes above that latitude issue no reading, are not extrapolated, and are not replaced by a distance to the nearest corridor end point. Each of the four readings registers how many samples were truncated this way.",
    "The method thresholds (25 m sampling interval, EPSG:4548 planar measurement, linearly interpolated percentiles) follow the DEV-01 caliber of this package's osm-fabric-readings.json. They are choices made by this package, not mandatory standard values; changing a threshold changes the reading.",
    "Registered precision: readings carry three decimal places and geographic coordinates six (about 0.11 m), matching the snapshot. Registered precision is not measurement accuracy -- the real positional error of OpenStreetMap community data is far larger than the number of digits shown.",
]

LICENSE = {
    "attribution": "© OpenStreetMap contributors",
    "license": "Open Database License (ODbL) 1.0",
    "license_url": "https://opendatacommons.org/licenses/odbl/1-0/",
    "notice_zh": "本文件的廊道几何与全部偏差读数均由 OpenStreetMap 数据派生，须按 ODbL 1.0 署名并以相同条件开放衍生数据库。",
    "notice_en": "The corridor geometry and every deviation reading in this file are derived from OpenStreetMap data and must be attributed and shared under ODbL 1.0.",
    "upstream_copyright_string": "The data included in this document is from www.openstreetmap.org. The data is made available under ODbL.",
}

PROXY_RISK_ZH = (
    "本文件用作位置代理的廊道由两条命名线合成，其中「京包客专线」十七条 way、11,526.107 米，多为新建"
    "高速铁路走廊，与京张铁路遗址公园的关系是空间伴行而不是同一实体；「京包线」六条 way、2,560.778 米"
    "（usage=tourism 的 rail 与 disused，另有一条 razed）才是遗址属性更接近的部分。把这条合成线整体当作"
    "遗址公园的位置代理，会把高铁走廊的走向一并计入。因此本文件全部偏差数值只作偏差量级参考，不得用于"
    "判定主脊选线是否正确，不得支持任何与公园边界的对位结论，也不构成设计依据或合规判定。官方遗址公园"
    "边界公开后，四项读数必须整体重算；重算前的任何引用都须连同本条风险一并引用。"
)

PROXY_RISK_EN = (
    "The corridor used here as a positional proxy is a composite of two named lines. Seventeen ways and 11,526.107 m "
    "of it are the Jingbao Passenger Dedicated Line, largely a newly built high-speed corridor whose relation to the "
    "Jing-Zhang Railway Heritage Park is spatial adjacency, not identity; only the six ways and 2,560.778 m of the "
    "Jingbao Line (rail and disused tagged usage=tourism, plus one razed way) carry a heritage character. Treating the "
    "composite line as a positional proxy for the park therefore folds the high-speed alignment into the measurement. "
    "Every deviation figure in this file is accordingly an order-of-magnitude reference only. It must not be used to "
    "judge whether the spine alignment is correct, must not support any conclusion about registration against the park "
    "boundary, and is neither a design basis nor a compliance determination. Once official park boundaries are "
    "published, all four readings must be recomputed in full; until then any citation must carry this risk note with it."
)


# ------------------------------------------------------------------ 主流程
def main():
    ways = []
    part_sha = {}
    for part in (1, 2):
        rel = f"visual/assets/osm-fabric/osm-fabric-snapshot-part{part}.json"
        part_sha[f"snapshot_part{part}_sha256"] = sha256_file(os.path.join(PKG, rel))
        ways.extend(load_json(rel)["ways"])

    corr_rows = sorted([w for w in ways if w[3] in CORRIDOR_NAMES],
                       key=lambda w: (w[3], w[0]))
    lines, features, by_name = [], [], {}
    for osm_id, _highway, railway, name, tags, geom in corr_rows:
        line = LineString(project(geom))
        lines.append(line)
        tags = tags or {}
        features.append({
            "osm_id": osm_id,
            "railway": railway,
            "name": name,
            "usage": tags.get("usage"),
            "bridge": tags.get("bridge"),
            "tunnel": tags.get("tunnel"),
            "vertex_count": len(geom),
            "length_m": r3(line.length),
            "coordinates_lon_lat": [[r6(c[0]), r6(c[1])] for c in geom],
        })
        slot = by_name.setdefault(name, {"way_count": 0, "length_m": 0.0,
                                         "vertex_count": 0, "railway_values": set(),
                                         "usage_values": set()})
        slot["way_count"] += 1
        slot["length_m"] += line.length
        slot["vertex_count"] += len(geom)
        slot["railway_values"].add(railway)
        slot["usage_values"].add(tags.get("usage"))
    for slot in by_name.values():
        slot["length_m"] = r3(slot["length_m"])
        slot["railway_values"] = sorted(v for v in slot["railway_values"] if v)
        slot["usage_values"] = sorted(v for v in slot["usage_values"] if v)

    corridor = unary_union(lines)
    lat_all = [c[1] for w in corr_rows for c in w[5]]
    lon_all = [c[0] for w in corr_rows for c in w[5]]
    lat_max, lat_min = max(lat_all), min(lat_all)

    roads = {ft["properties"]["id"]: ft
             for ft in load_json("geometry/roads.geojson")["features"]}
    site_features = load_json("geometry/site_boundary.geojson")["features"]
    nodes = [ft for ft in load_json("geometry/constraints.geojson")["features"]
             if str(ft["properties"].get("id", "")).startswith("OP-")]

    spine = LineString(project(roads["ROAD-001"]["geometry"]["coordinates"]))
    quiet = LineString(project(roads["ROAD-005"]["geometry"]["coordinates"]))
    aln01 = offset_reading(spine, corridor, lat_max)
    aln02 = offset_reading(quiet, corridor, lat_max)

    poly = unary_union([shp_transform(lambda x, y: _fwd.transform(x, y),
                                      shape(ft["geometry"]))
                        for ft in site_features])
    inside_geom = corridor.intersection(poly)
    outside_geom = corridor.difference(poly)
    inside_lats = [_inv.transform(x, y)[1]
                   for g in getattr(inside_geom, "geoms", [inside_geom])
                   for x, y in g.coords]

    node_rows = []
    for ft in sorted(nodes, key=lambda ft: ft["properties"]["id"]):
        lon, lat = ft["geometry"]["coordinates"][:2]
        pt = Point(_fwd.transform(lon, lat))
        in_band = lat <= lat_max
        node_rows.append({
            "id": ft["properties"]["id"],
            "name_zh": ft["properties"].get("name_zh"),
            "scenario_id": ft["properties"].get("scenario_id"),
            "key_area_id": ft["properties"].get("key_area_id"),
            "submitted_confidence": ft["properties"].get("confidence"),
            "submitted_evidence_status": ft["properties"].get("evidence_status"),
            "lon": r6(lon),
            "lat": r6(lat),
            "within_corridor_data_band": in_band,
            "distance_to_corridor_m": r3(pt.distance(corridor)) if in_band else None,
            "note_zh": None if in_band else
            "超出廊道数据带（纬度高于 %.6f），本文件不出读数、不外推。" % lat_max,
            "note_en": None if in_band else
            "Outside the corridor data band (latitude above %.6f); this file issues no reading and extrapolates none." % lat_max,
        })
    band_rows = [r for r in node_rows if r["within_corridor_data_band"]]
    band_d = [r["distance_to_corridor_m"] for r in band_rows]

    doc = {
        "schema_version": "0.1.0",
        "declaration": {
            "package_zh": "万感京张 空间对齐参考 —— 主脊与遗址公园廊道参考线的偏差登记",
            "package_en": "Every-Sense Jingzhang spatial alignment reference -- registered offsets between the spine and the heritage park corridor reference line",
            "status": "PROVISIONAL",
            "purpose_zh": "本文件把此前只以文字表述的空间关系（「主脊沿已建成公共基底组织」）转为可复算的读数登记。登记的是偏差事实，不是达标声明，也不是选线论证。",
            "purpose_en": "This file converts a spatial relationship that was previously stated only in prose (\"the spine is organised along the built public ground\") into recomputable registered readings. What is registered is the fact of an offset -- not a claim of conformity and not an argument for the alignment.",
            "statement_zh": DECLARATION_ZH,
            "statement_en": DECLARATION_EN,
            "license": LICENSE,
        },
        "provenance": {
            "derivation_zh": "廊道中心线几何全部从提交包内既有 OSM 快照派生，本轮未发起任何新的数据抓取、未引入任何包外数据源、未接触网络。",
            "derivation_en": "The corridor centreline geometry is derived entirely from the OpenStreetMap snapshot already inside the submission package. This round issued no new data retrieval, introduced no external source, and touched no network.",
            "snapshot_file": "osm-fabric-snapshot.json",
            "snapshot_sha256": "855296cd2f8da491eb8fae9f70e50bd5c7953040e5fc5d0fa91b77bc93b5c7c6",
            "snapshot_bytes": 781114,
            "snapshot_parts_in_package": [
                "visual/assets/osm-fabric/osm-fabric-snapshot-part1.json",
                "visual/assets/osm-fabric/osm-fabric-snapshot-part2.json",
            ],
            "snapshot_query_sent_utc": "2026-08-15T21:54:38Z",
            "snapshot_osm_data_timestamp_utc": "2026-08-15T21:53:34Z",
            "snapshot_endpoint": "https://overpass-api.de/api/interpreter",
            "submission_geometry": [
                "geometry/roads.geojson",
                "geometry/site_boundary.geojson",
                "geometry/constraints.geojson",
            ],
            "compute_script": "compute_alignment.py",
            "projected_crs": CRS_DST,
            "projected_crs_name": "CGCS2000 / 3-degree Gauss-Kruger CM 117E",
            "sibling_readings_file": "visual/assets/osm-fabric/osm-fabric-readings.json",
            "determinism_zh": "本脚本不使用随机数、不依赖集合迭代顺序（全部排序后处理），同一输入重复执行输出逐字节一致。",
            "determinism_en": "The script uses no randomness and does not depend on set iteration order (all collections are sorted before use); repeated runs on the same input produce byte-identical output.",
        },
        "definitions": {
            "corridor_selection_zh": "廊道参考线 = 快照中 name 为「京包线」或「京包客专线」的全部 way，按 name 与 osm_id 排序后并集为一条多线要素。选取规则只用 name 字段，不做人工挑拣，任何人按同一规则可从同一快照得到同一集合。",
            "corridor_selection_en": "The corridor reference line is the union of every way in the snapshot whose name is 京包线 (Jingbao Line) or 京包客专线 (Jingbao Passenger Dedicated Line), ordered by name and osm_id. The selection uses the name field alone with no manual picking, so anyone applying the same rule to the same snapshot obtains the same set.",
            "sampling_zh": "沿提交中心线自起点每 25 米取一采样点，末段不足 25 米时补一个终点采样；距离为采样点到廊道多线要素的最短欧氏距离，在 EPSG:4548 平面上量算。",
            "sampling_en": "Sampling advances at 25 metre intervals from the start of each submitted centreline, with one extra sample at the end point when the last segment is shorter than 25 metres. The distance is the shortest Euclidean distance from the sample point to the corridor multi-line, measured in the EPSG:4548 plane.",
            "data_band_zh": "数据带 = 廊道要素在快照中覆盖的纬度区间。纬度高于其上界的采样点与节点一律标记为超出数据带，不出读数。",
            "data_band_en": "The data band is the latitude range covered by the corridor features in the snapshot. Sample points and nodes above its upper bound are marked as outside the band and issue no reading.",
            "corridor_data_band_lat_min": r6(lat_min),
            "corridor_data_band_lat_max": r6(lat_max),
            "corridor_data_band_lon_min": r6(min(lon_all)),
            "corridor_data_band_lon_max": r6(max(lon_all)),
            "straight_line_distance_zh": "全部距离为直线距离，不是沿网络的绕行距离；实际步行接入距离不小于本读数。",
            "straight_line_distance_en": "All distances are straight-line, not network-detour; an actual walking access distance is never less than the reading.",
        },
        "proxy_risk": {
            "id": "PROXY-01",
            "title_zh": "廊道作为遗址公园位置代理的适用限度",
            "title_en": "Limits of using the rail corridor as a positional proxy for the heritage park",
            "severity": "high",
            "statement_zh": PROXY_RISK_ZH,
            "statement_en": PROXY_RISK_EN,
            "linked_risk_ids": ["R-05", "R-06"],
            "linked_assumption_ids": ["A-11"],
        },
        "corridor_geometry": {
            "way_count": len(features),
            "vertex_count": sum(f["vertex_count"] for f in features),
            "total_length_m": r3(corridor.length),
            "by_name": by_name,
            "note_zh": "以下逐 way 登记 osm_id、railway 值、usage 值、顶点数、投影长度与完整坐标串，供逐要素复核；坐标与快照逐字节同源，未做任何简化或平滑。",
            "note_en": "Each way below registers its osm_id, railway value, usage value, vertex count, projected length and full coordinate string for feature-by-feature checking. The coordinates come from the snapshot unchanged, with no simplification or smoothing applied.",
            "ways": features,
        },
        "readings": [
            {
                "id": "ALN-01",
                "metric_key": "spine_to_heritage_corridor_median_offset_m",
                "name_zh": "通用可达底线（主脊）相对遗址公园廊道参考线的偏差",
                "name_en": "Offset of the Universal Access Baseline (the spine) from the heritage park corridor reference line",
                "unit": "m",
                "subject": "ROAD-001",
                "subject_length_m": r3(spine.length),
                "reading": aln01,
                "discretion_zh": [
                    "本读数替换的是正文此前「主脊即沿这条已建成公共基底组织」的文字表述。该表述在本包数据上没有支撑：主脊中位偏差为数百米量级，不是贴线关系。",
                    "主脊本身贴合的是现状街道：本包 osm-fabric-readings.json 的 DEV-01 登记其对可步行网络中位偏差 2.940 米。两项读数并读的结论是——主脊沿现状街道组织，与廊道参考线保持数百米量级的偏差。",
                    "偏差数值不表示选线错误。ROAD-001 在提交包中为 agent_generated_design、geometry_role=design_proposal 的概念示意走向，其位置由继承的临时总体范围决定，而该范围与廊道的不相交关系已由仓库议题 #846 登记。",
                ],
                "discretion_en": [
                    "This reading replaces the earlier prose claim that \"the spine is organised along that built public ground\". The package's own data does not support that claim: the median offset is in the hundreds of metres, which is not a following relationship.",
                    "What the spine does follow is the existing street network: DEV-01 in this package's osm-fabric-readings.json registers its median offset from the walkable network at 2.940 m. Read together, the two readings say the spine is organised along existing streets and stands a few hundred metres off the corridor reference line.",
                    "The figure is not an alignment error. ROAD-001 is tagged agent_generated_design with geometry_role=design_proposal in the submission and is a schematic alignment whose position follows the inherited provisional overall extent, whose non-intersection with the corridor is already registered as repository issue #846.",
                ],
            },
            {
                "id": "ALN-02",
                "metric_key": "quiet_route_to_heritage_corridor_median_offset_m",
                "name_zh": "低刺激安静替代路线相对遗址公园廊道参考线的偏差",
                "name_en": "Offset of the Low-Stimulation Quiet Alternative Route from the heritage park corridor reference line",
                "unit": "m",
                "subject": "ROAD-005",
                "subject_length_m": r3(quiet.length),
                "reading": aln02,
                "discretion_zh": [
                    "安静替代线与主脊并行布置，其相对廊道的偏差高于主脊，与两线的东西位置关系一致，不表示该线更偏离设计意图。",
                    "该线在提交包中同为概念示意走向，最小偏差处也在两百米以上，全线不与廊道参考线相交。",
                ],
                "discretion_en": [
                    "The quiet alternative runs parallel to the spine and sits further from the corridor, consistent with the two lines' east-west relationship; it does not indicate a greater departure from design intent.",
                    "This line is likewise a schematic alignment in the submission. Even at its closest it stands more than two hundred metres away, and it nowhere meets the corridor reference line.",
                ],
            },
            {
                "id": "ALN-03",
                "metric_key": "site_boundary_to_heritage_corridor_outside_length_m",
                "name_zh": "遗址公园廊道参考线落在临时总体设计范围之外的长度",
                "name_en": "Length of the heritage park corridor reference line falling outside the provisional overall design extent",
                "unit": "m",
                "subject": "SITE-001",
                "reading": {
                    "corridor_total_length_m": r3(corridor.length),
                    "inside_site_length_m": r3(inside_geom.length),
                    "outside_site_length_m": r3(outside_geom.length),
                    "outside_share_pct": r3(outside_geom.length / corridor.length * 100.0),
                    "inside_lat_min": r6(min(inside_lats)),
                    "inside_lat_max": r6(max(inside_lats)),
                },
                "discretion_zh": [
                    "廊道参考线全长的绝大部分落在临时总体设计范围之外，落入范围内的部分全部集中在场地南段（纬度上界见 inside_lat_max）。场地北段在本快照上不存在廊道要素。",
                    "该读数与本包 osm-fabric-readings.json 的 DQ 节 rail_corridor_extent 同向：快照中的地面轨道要素在场地内只覆盖约 2.1 公里，占场地纵向跨度约 21.8%。",
                    "本读数不评价临时范围划得对不对。临时总体范围在提交包中自述为 provisional_rough、official_boundary=false，其与官方红线的关系待官方资料公开后另行处置 [A-11]。",
                ],
                "discretion_en": [
                    "Most of the corridor reference line falls outside the provisional overall design extent, and the part that falls inside is confined to the southern end of the site (see inside_lat_max). The northern part of the site carries no corridor feature in this snapshot.",
                    "The reading points the same way as the DQ section's rail_corridor_extent in this package's osm-fabric-readings.json: surface rail features cover only about 2.1 km inside the site, some 21.8 per cent of its longitudinal extent.",
                    "This reading passes no judgement on whether the provisional extent is drawn correctly. The submission declares that extent as provisional_rough with official_boundary=false, and its relation to an official redline is left to a later round once official material is published [A-11].",
                ],
            },
            {
                "id": "ALN-04",
                "metric_key": None,
                "name_zh": "十个独立完成节点到遗址公园廊道参考线的距离",
                "name_en": "Distance from each of the ten Independent Completion Points to the heritage park corridor reference line",
                "unit": "m",
                "subject": "OP-01..OP-10",
                "reading": {
                    "nodes": node_rows,
                    "within_band_count": len(band_rows),
                    "outside_band_count": len(node_rows) - len(band_rows),
                    "within_band_median_m": r3(percentile(band_d, 0.5)),
                    "within_band_min_m": r3(min(band_d)),
                    "within_band_max_m": r3(max(band_d)),
                },
                "discretion_zh": [
                    "北段节点全部超出廊道数据带，本表对其一律留空并写明理由，不以到廊道北端点的距离顶替——那个距离量的是数据边界，不是与廊道的真实关系。",
                    "带内节点的距离同为直线距离，不代表可步行接入距离；节点相对现状步行网络的接入距离另见 osm-fabric-readings.json 的 DEV-02。",
                    "节点名称、confidence 与 evidence_status 均逐字取自提交包，未作改写。提交包的节点属性中不含英文名称字段，本包不代为拟定，故各节点只有 name_zh。",
                ],
                "discretion_en": [
                    "Every node in the northern part of the site falls outside the corridor data band. This table leaves those entries empty and states why, rather than substituting a distance to the corridor's northern end point: that distance measures the edge of the data, not a real relationship to the corridor.",
                    "Distances for in-band nodes are likewise straight-line and are not walking access distances; connection distances against the existing pedestrian network are registered separately as DEV-02 in osm-fabric-readings.json.",
                    "Node names, confidence and evidence_status are carried verbatim from the submission without rewording. The submission's node properties contain no English name field, and this package does not invent one, so each node carries name_zh only.",
                ],
            },
        ],
        "cross_references": {
            "assumptions": ["A-11"],
            "risks": ["R-05", "R-06"],
            "metrics": [
                "spine_to_heritage_corridor_median_offset_m",
                "quiet_route_to_heritage_corridor_median_offset_m",
                "site_boundary_to_heritage_corridor_outside_length_m",
            ],
            "repository_issues": [
                {"issue": 846,
                 "subject_zh": "临时总体设计范围多边形与 OSM 测绘的遗址公园已建段不相交，最近距离约 412.5 米",
                 "subject_en": "The provisional overall-design polygon does not intersect the OSM-surveyed built park; the nearest distance is about 412.5 m",
                 "handling_zh": "该读数由官方框自身与公园多边形量得，公园多边形不在本包数据内，本文件不复核该数值；本文件登记的是另一件事——提交线位与廊道参考线之间的偏差。",
                 "handling_en": "That figure was measured between the official frame itself and a park polygon that is not in this package's data, so this file does not re-check it. What this file registers is a different thing: the offset between the submitted alignments and the corridor reference line."},
            ],
        },
        "reproduction": {
            "note_zh": "下方嵌入复算脚本全文。另存为 compute_alignment.py 后在提交包同级运行即可复现本文件全部读数；脚本只读取包内既有文件，不发起网络请求。两片快照的 sha256 一并登记，可先行校验输入未被改动。",
            "note_en": "The full recomputation script is embedded below. Save it as compute_alignment.py and run it against the submission package to reproduce every reading in this file; it reads only files already inside the package and issues no network request. The sha256 of both snapshot parts is registered alongside so the inputs can be verified unchanged first.",
            "snapshot_whole_sha256": "855296cd2f8da491eb8fae9f70e50bd5c7953040e5fc5d0fa91b77bc93b5c7c6",
            **part_sha,
            "compute_alignment_py": open(os.path.abspath(__file__), encoding="utf-8").read(),
        },
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write("\n")

    print("written", OUT, os.path.getsize(OUT), "bytes")
    print("ALN-01 median %.3f p90 %.3f max %.3f min %.3f n %d (truncated %d)" % (
        aln01["median_m"], aln01["p90_m"], aln01["max_m"], aln01["min_m"],
        aln01["sample_count"], aln01["sample_count_outside_data_band"]))
    print("ALN-02 median %.3f p90 %.3f max %.3f min %.3f n %d (truncated %d)" % (
        aln02["median_m"], aln02["p90_m"], aln02["max_m"], aln02["min_m"],
        aln02["sample_count"], aln02["sample_count_outside_data_band"]))
    print("ALN-03 total %.3f inside %.3f outside %.3f" % (
        corridor.length, inside_geom.length, outside_geom.length))
    print("ALN-04 in-band %d out-band %d" % (
        len(band_rows), len(node_rows) - len(band_rows)))


if __name__ == "__main__":
    main()

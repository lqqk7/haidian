# -*- coding: utf-8 -*-
"""visual/assets/concept-design-register.json —— 概念详图三图的设想要素登记。

本文件的唯一职责：把三张概念详图上出现的每一个设想要素，与它所依据的包内既有
判据一一对上，并把「哪一部分是数据、哪一部分是设想」写成可核对的条目。没有登记
的设想要素不得出现在图上；登记条目里 judgment_source 指不到包内锚点的，同样不得
出现在图上。
"""
from __future__ import annotations
from pathlib import Path as _HaidianPath

import json
import os

OUT = (str(_HaidianPath(__file__).resolve().parents[3] / 'submissions/lqqk7') + "/"
       "every-sense-jingzhang/visual/assets/concept-design-register.json")

DECL_ZH = ("概念推演图：建筑体量、通道线位与界面划分均为设计设想，"
           "不基于权属、红线或测绘资料，不代表现状或规划真实情况。")
DECL_EN = ("Concept speculation drawing: the building masses, passage alignments "
           "and frontage divisions are design speculation. They rest on no tenure, "
           "red-line or survey data and represent neither existing conditions nor "
           "any actual plan.")

DS = "visual/assets/district-strategy.json"
SDC = "visual/assets/sensory-design-code.json"


def E(eid, zh, en, drawn, data_zh, data_en, spec_zh, spec_en, src):
    return {"element_id": eid, "name_zh": zh, "name_en": en, "drawn_as": drawn,
            "data_part_zh": data_zh, "data_part_en": data_en,
            "speculative_part_zh": spec_zh, "speculative_part_en": spec_en,
            "judgment_source": src}


FIG1 = {
    "figure_id": "CD-01",
    "file": "assets/figures/district-concept-sections.png",
    "title_zh": "三片区概念详图：建筑—街道—公共空间—运营关系的一次空间组合",
    "title_en": ("District concept detail — one spatial composition of the building, "
                 "street, public-space and operation relations across the three key areas"),
    "orientation": "north_to_the_right",
    "shared_scale_m_per_css_px": 3.3,
    "window_m": [1221, 851],
    "answers_gap_zh": "专业评估五项欠缺之一：重点区详细设计只到判据层，没有一次落成空间组合。",
    "answers_gap_en": ("The first of the five gaps named in professional review: the key-area "
                       "detailed design stopped at the criteria layer and never landed one "
                       "spatial composition."),
    "data_layers": [
        {"id": "block_faces", "name_zh": "四处候选街块轮廓", "name_en": "candidate block faces",
         "source": "visual/assets/osm-fabric/osm-fabric-snapshot-part1.json + part2.json"
                   " → FAB-03 街块面集合；面积与周长与 %s#districts[*].opening_candidates 逐项一致" % DS},
        {"id": "centrelines", "name_zh": "五条提交中心线", "name_en": "five submitted centrelines",
         "source": "geometry/roads.geojson#ROAD-001..ROAD-005"},
        {"id": "nodes", "name_zh": "十处独立完成节点", "name_en": "ten completion nodes",
         "source": "geometry/constraints.geojson#OP-01..OP-10"},
        {"id": "public_faces", "name_zh": "公共空间面", "name_en": "public-space faces",
         "source": "geometry/public_space.geojson"},
        {"id": "key_areas", "name_zh": "重点区粗略范围（临时多边形）",
         "name_en": "key-area provisional extents",
         "source": "geometry/key_areas.geojson#official_boundary=false"},
        {"id": "band_widths", "name_zh": "通道断面四带取值", "name_en": "four passage-band widths",
         "source": "%s#node_design_parameters.master_card.band_widths_zh" % SDC},
    ],
    "speculative_elements": [
        E("CD-01-A1", "ZZY-BK-01 贯通通道线位", "Through-route alignment at ZZY-BK-01",
          "dashed_heavy",
          "该街块的开放化动作类型登记为 through_route，与主脊中心线距离 0 m，最近节点 OP-01 距 24.4 m。",
          "The block's opening action is registered as through_route, 0 m from the spine centreline, with OP-01 24.4 m away.",
          "通道从哪一点进、到哪一点出、走什么走向，本图给了一条；这条线位不是唯一解，也未经权属与内部通道现场核实。",
          "Where the route enters, where it leaves and how it runs are given here as one option; the alignment is neither unique nor verified against tenure or any field survey of internal passages.",
          ["%s#districts[zhongzhiyuan_ai_acceleration_area].opening_candidates[ZZY-BK-01].opening_action_type" % DS,
           "%s#districts[zhongzhiyuan_ai_acceleration_area].opening_candidates[ZZY-BK-01].action_definition_zh" % DS,
           "%s#districts[zhongzhiyuan_ai_acceleration_area].opening_candidates[ZZY-BK-01].preconditions" % DS]),
        E("CD-01-A2", "通道两侧建筑体量概念块", "Concept masses flanking the through-route",
          "dashed_fill",
          "包内已登记四处概念体量，其 geometry_role 为 design_proposal、confidence 为 low／medium，概念体量本身是既有做法。",
          "Four concept masses are already registered with geometry_role design_proposal at low or medium confidence; concept massing is an existing practice in this package.",
          "本图新增的体量块只有一个作用：使活性界面的入口间距在该段成立。位置、进深、高度与用途一律未定，且不构成任何强度结论。",
          "The masses added here serve one purpose: to make the active-frontage entrance spacing hold along that stretch. Position, depth, height and use are all undetermined and imply no intensity conclusion.",
          ["geometry/buildings.geojson#geometry_role=design_proposal",
           "%s#frontage_rules.classes[active_frontage].criteria[0]" % DS,
           "%s#intensity_envelope.refusal_zh（强度不给数值，本图亦不给）" % DS]),
        E("CD-01-A3", "活性界面入口落位（间距 50.5 m）", "Active-frontage entrances at 50.5 m",
          "dashed_dots",
          "50.5 m 是众智园街块中位规模的等效方形边长，属既有参考标尺；参考区间为该值的 0.8—1.0 倍。",
          "50.5 m is the equivalent square side of Zhongzhiyuan's median block size, an existing reference scale; the reference band is 0.8 to 1.0 of it.",
          "把间距按等距打点落在通道上是一次示意；实际入口位取决于首层功能与权属，现场以实测入口间距核查。",
          "Placing entrances at equal spacing along the route is indicative; actual positions depend on ground-floor use and tenure and are checked by measured spacing in the field.",
          ["%s#frontage_rules.classes[active_frontage].criteria[0]" % DS,
           "%s#frontage_rules.reference_scale_zh" % DS,
           "%s#frontage_rules.classes[active_frontage].check_zh" % DS]),
        E("CD-01-A4", "安静支线绕行", "Quiet spur bypass", "dotted",
          "静界面适用于低刺激安静替代路线沿线的边段，且低刺激缓冲不得由主脊绿带代偿。",
          "Quiet frontage applies along the low-stimulus alternative route, and its buffer may not be substituted by the spine belt.",
          "支线的具体绕行走向为设想，仅表达「安静路径与活性通道分离」这一关系，不表示可行路径。",
          "The spur's alignment is speculative and expresses only the relation that the quiet path stays separate from the active route; it asserts no walkable path.",
          ["%s#frontage_rules.classes[quiet_frontage].applies_zh" % DS,
           "%s#bluegreen_stormwater.layer_relations[BG-R1]" % SDC]),
        E("CD-01-A5", "展示界面边段", "Display-frontage stretch", "dashed_thick",
          "展示界面的适用条款为众智园受控测试庭与实验测试用房沿公共空间的边段。",
          "Display frontage applies to the edges of Zhongzhiyuan's controlled test court and laboratory rooms facing public space.",
          "该边段落在哪一块概念体量上为设想；本图未指认任何真实用房。",
          "Which concept mass carries that edge is speculation; no actual room is identified.",
          ["%s#frontage_rules.classes[display_frontage].applies_zh" % DS]),
        E("CD-01-B1", "三块开放化动作的空间落位", "Where the three opening actions land",
          "dashed_mixed",
          "AIO-BK-01 为 through_route、BK-02 为 edge_permeation、BK-03 为 corner_opening；三块到 ROAD-003 的距离均为 0 m。",
          "AIO-BK-01 is through_route, BK-02 edge permeation and BK-03 corner opening; all three lie 0 m from ROAD-003.",
          "动作类型是数据，落在街块的哪一边、哪一角、哪一条穿越线上是设想。",
          "The action types are data; which edge, which corner and which crossing line they land on is speculation.",
          ["%s#districts[beijing_ai_origin_community].opening_candidates[*].opening_action_type" % DS,
           "%s#districts[beijing_ai_origin_community].opening_candidates[*].nearest_submitted_centreline" % DS]),
        E("CD-01-B2", "接口连续界面", "Continuous interface frontage", "dashed_line",
          "既有读数：该接口能否成段由这三块决定；ROAD-003 是五条线中干道贴线率最低者（22%），慢行专用采样占比同为 22%。",
          "Registered reading: whether this interface can run continuously is decided by these three blocks; ROAD-003 has the lowest arterial adjacency of the five lines at 22 per cent, with an equal 22 per cent slow-mobility-exclusive.",
          "把三块开放后的界面连成一段是设想；A／B／C 三类采样的逐段位置未登记，本图不指认哪一段属哪一类。",
          "Joining the three opened edges into one continuous frontage is speculation; the per-sample positions of the three classes are not registered and this sheet identifies none.",
          ["%s#districts[beijing_ai_origin_community].opening_candidates[*].ranking_basis_zh" % DS,
           "%s#corridor_and_interchange.segmentation.lines[ROAD-003]" % DS]),
        E("CD-01-B3", "共创院一街两院组合", "Co-design courtyards astride the street",
          "dashed_fill",
          "原点社区的既有设计角色为「独立生活共创院」，既有承载面为 PUBLIC-005，既有概念体量为 BLDG-003。",
          "The Origin Community's registered design role is the Independent Living Co-design Lab, carried by PUBLIC-005 with concept mass BLDG-003.",
          "「一街两院」的院落数量、位置与规模均为设想，不构成任何用地或建筑结论。",
          "The number, position and size of the courtyards are speculation and imply no land-use or building conclusion.",
          ["%s#districts[beijing_ai_origin_community].design_role_zh" % DS,
           "geometry/public_space.geojson#PUBLIC-005",
           "geometry/buildings.geojson#BLDG-003"]),
        E("CD-01-B4", "服务点位落位（间距 41.0 m）", "Service points at 41.0 m", "dashed_squares",
          "41.0 m 是原点社区街块中位规模的等效方形边长，属既有参考标尺。",
          "41.0 m is the equivalent square side of the Origin Community's median block size, an existing reference scale.",
          "沿接口等距落点为示意；点位性质、开放时段与运营主体均未定。",
          "Equal spacing along the interface is indicative; the nature of each point, its hours and its operator are undetermined.",
          ["%s#frontage_rules.classes[active_frontage].criteria[0]" % DS,
           "%s#frontage_rules.reference_scale_zh" % DS]),
        E("CD-01-C1", "服务桌落位与四位序图解", "Desk position and the four-station order",
          "dashed_blocks",
          "四位序为人工窗口、多通道信息位、AI 开关、退出回执位，顺序不可调换；四位中只有 AI 开关属 AI 层。承载面为 PUBLIC-007。",
          "The four stations are the staffed window, the multichannel information point, the AI switch and the exit receipt, in a non-negotiable order; only the AI switch belongs to the AI layer. The carrier face is PUBLIC-007.",
          "服务桌落在前厅面的哪一处、朝向如何为设想；且该桌的七项开办条件当前全部为待办，整体结论为 no-go。",
          "Where the desk sits within the forecourt and how it faces are speculation; all seven readiness conditions are outstanding and the overall verdict is no-go.",
          ["visual/assets/seb-spec.json#canonical_station_sequence",
           "visual/assets/service-desk-gonogo.json#subject.carrier_zh",
           "visual/assets/service-desk-gonogo.json#overall_decision.verdict=no-go",
           "geometry/public_space.geojson#PUBLIC-007"]),
        E("CD-01-C2", "「不消费也能停留」停留空间", "The no-purchase dwelling area", "dashed_fill",
          "「不消费也能停留」与四位序同属已确定的设计判据，不因开办条件未备而待定。",
          "The promise that staying requires no purchase is, like the four-station order, a settled design criterion and does not await readiness.",
          "该停留面的位置、面积与遮蔽方式为设想；面积与座位数均未定。",
          "The position, area and shelter of that dwelling surface are speculation; neither area nor seat count is fixed.",
          ["visual/assets/service-desk-gonogo.json#overall_decision.what_no_go_does_not_mean_zh",
           "%s#frontage_rules.derivation_zh" % DS]),
        E("CD-01-C3", "界面分类沿街落位（活性／静）", "Frontage classes along the street",
          "dashed_thick",
          "三类界面的适用条款已登记；大钟寺无受控测试庭，故展示界面在该联不适用，本图因此不画。",
          "The applicability clauses of the three classes are registered; Dazhongsi has no controlled test court, so display frontage does not apply in this panel and is not drawn.",
          "哪一段街面属活性、哪一段属静为设想；三类不是用地分类，也不是法定界面控制。",
          "Which stretch is active and which is quiet is speculation; the three classes are neither a land-use classification nor statutory frontage control.",
          ["%s#frontage_rules.classes[*].applies_zh" % DS,
           "%s#frontage_rules.boundary_zh" % DS]),
        E("CD-01-C4", "触觉文化带穿越市场空间", "Tactile culture band across the market",
          "dotted",
          "触觉文化带的既有主张为沿主脊连续、任一段可停可跳过；大钟寺段的解说载体含百感台公开记录面与服务桌四位序处的现场人工解说。",
          "The tactile culture band is registered as continuous along the spine and stoppable or skippable at any point; the Dazhongsi segment's carriers include the Hundred-Sense Forum record face and in-person explanation at the desk.",
          "带的具体走向、进入前厅面与百感台的接续位置为设想；触觉可用性未经视障使用者测试。",
          "The band's alignment and where it enters the forecourt and the Forum face are speculation; tactile usability has not been tested with blind or low-vision users.",
          ["%s#heritage_interpretation.sequence_rule_zh" % SDC,
           "%s#heritage_interpretation.segments[HS-3].carriers" % SDC,
           "visual/assets/op04-tactile-map.json#print_params_zh（未经视障使用者测试）"]),
        E("CD-01-C5", "入口间距 31.1 m 落位", "Entrance spacing at 31.1 m", "dashed_dots",
          "31.1 m 是大钟寺街块中位规模的等效方形边长，属既有参考标尺；该区街块诊断为「粒度已细、问题在界面」。",
          "31.1 m is the equivalent square side of Dazhongsi's median block size, an existing reference scale; the area's block diagnosis reads as already fine-grained with the problem lying in frontage.",
          "沿街等距落点为示意，非实测分配。",
          "Equal spacing along the street is indicative, not a measured allocation.",
          ["%s#frontage_rules.reference_scale_zh" % DS,
           "%s#districts[dazhongsi_ai_industry_cluster].block_diagnosis" % DS]),
    ],
}

FIG2 = {
    "figure_id": "CT-02",
    "file": "assets/figures/transport-system-concept.png",
    "title_zh": "交通系统概念图：轨道接入、走廊分段、骑行与保障车时段分离",
    "title_en": ("Transport system concept — rail access, corridor segmentation, cycling "
                 "and the time separation of support vehicles"),
    "orientation": "north_to_the_right",
    "scale_m_per_css_px": 8.7,
    "answers_gap_zh": "专业评估五项欠缺之二：交通系统没有一张把轨道、公交、慢行、骑行与货运并置的分层图。",
    "answers_gap_en": ("The second gap named in professional review: no single layered sheet "
                       "placed rail, bus, walking, cycling and freight side by side."),
    "data_layers": [
        {"id": "rail_clusters", "name_zh": "轨道接入点簇六处（11 簇中已登记 6 处）",
         "name_en": "six registered rail access clusters of eleven",
         "source": "%s#corridor_and_interchange.rail_access.clusters" % DS},
        {"id": "cluster_foot", "name_zh": "接入点簇到最近中心线的垂足与距离",
         "name_en": "foot of perpendicular and distance to the nearest centreline",
         "source": "EPSG:4548 复算；六条距离与 %s#corridor_and_interchange.rail_access.clusters"
                   "[*].nearest_centreline.distance_m 逐条一致（17.5／44.3／100.9／30.5／47.1／211.6 m）" % DS},
        {"id": "abc_shares", "name_zh": "五线三类判据分段占比",
         "name_en": "A/B/C shares on the five lines",
         "source": "%s#corridor_and_interchange.segmentation.lines" % DS},
        {"id": "spine_shared", "name_zh": "主脊唯一连续共存段（自南端 150—1700 m）",
         "name_en": "the spine's only continuous shared stretch, 150 to 1700 m from the south end",
         "source": "%s#corridor_and_interchange.segmentation.lines[ROAD-001].reading_zh；"
                   "链距按 EPSG:4548 复算，主脊全长 9,425.7 m 对登记值 9,426 m" % DS},
        {"id": "cycleway_existing", "name_zh": "快照内既有骑行专用要素 45 条 · 21.1 km",
         "name_en": "45 existing cycleway ways, 21.1 km, in the snapshot",
         "source": "visual/assets/osm-fabric/osm-fabric-snapshot-part1.json + part2.json#highway=cycleway"},
    ],
    "speculative_elements": [
        E("CT-02-S1", "骑行走向设想", "Speculative cycling alignment", "dashed_line",
          "快照登记了 45 条既有骑行专用要素；慢行专用候选段（B 类）判据与其占比已登记。",
          "The snapshot registers 45 existing cycleway ways, and the slow-mobility-exclusive criterion with its shares is registered.",
          "沿主脊与三处横向接口的骑行走向为侧向偏移的概念表达，不是线位、不是断面、不表示可骑行性，也不提出与机动车的路权划分。",
          "The alignments offset alongside the spine and the three lateral interfaces are a conceptual expression: not an alignment, not a cross-section, no claim of rideability and no right-of-way split with motor traffic.",
          ["%s#corridor_and_interchange.segmentation.method_zh（B 类判据）" % DS,
           "%s#corridor_and_interchange.freight_and_support.route_criteria_zh[1]" % DS,
           "%s#corridor_and_interchange.statement_zh（中心线表达关系，不是道路红线）" % DS]),
        E("CT-02-S2", "节点停放点设想", "Speculative parking at the nodes", "dashed_square",
          "十节点为已登记的独立完成点；活性界面要求首层含一类可无账户、无手机完成的事项。",
          "The ten nodes are registered independently completable points, and active frontage requires one act completable without an account or a phone.",
          "每个节点旁一处停放位是设想；规模、车型、是否收费与管理方式一律未定。",
          "One parking position beside each node is speculation; capacity, vehicle type, charging and management are all undetermined.",
          ["geometry/constraints.geojson#OP-01..OP-10",
           "%s#frontage_rules.classes[active_frontage].criteria[1]" % DS]),
        E("CT-02-S3", "换乘步行接驳设想", "Speculative walking link at interchange", "dotted",
          "接驳序列已登记：众智园两处接入点簇均落在重点区内，距主脊 17.5 m 与 44.3 m。",
          "The interchange sequence is registered: both Zhongzhiyuan clusters fall inside the key area, 17.5 m and 44.3 m from the spine.",
          "接入点簇到最近节点之间的连线为直线示意，不表示可步行路径、不表示步行距离、不表示过街条件。",
          "The line from a cluster to its nearest node is a straight indicative link and represents neither a walkable route, nor a walking distance, nor a crossing condition.",
          ["%s#corridor_and_interchange.rail_access.sequence_zh" % DS,
           "geometry/constraints.geojson#OP-01..OP-10"]),
        E("CT-02-S4", "保障车时段分离概念条", "Concept bar for the time separation of support vehicles",
          "concept_bar_no_clock",
          "时段分离原则、三条路径判据与挂既有维护 SLA 四级阶梯的响应关系均已登记。",
          "The time-separation principle, the three route criteria and the response relation hanging on the existing four-level maintenance SLA are all registered.",
          "条上三段的先后与互斥关系是判据的图示；任何钟点值、时长与班次均未登记，本图一概不给。",
          "The order and mutual exclusion of the three bands illustrate the criteria; no clock value, duration or frequency is registered and none is given here.",
          ["%s#corridor_and_interchange.freight_and_support.principle_zh" % DS,
           "%s#corridor_and_interchange.freight_and_support.route_criteria_zh" % DS,
           "%s#corridor_and_interchange.freight_and_support.sla_linkage_zh" % DS,
           "%s#corridor_and_interchange.freight_and_support.boundary_zh" % DS]),
    ],
}

FIG3 = {
    "figure_id": "CB-03",
    "file": "assets/figures/bluegreen-system-concept.png",
    "title_zh": "蓝绿系统概念图：汇水概念分区、排水类型、遮荫与夜间照明分级",
    "title_en": ("Blue-green system concept — conceptual catchments, drainage types, "
                 "shading and the night-lighting grades"),
    "orientation": "north_to_the_right",
    "scale_m_per_css_px": 8.7,
    "answers_gap_zh": "专业评估五项欠缺之三：蓝绿系统只有三层关系图，没有落在走廊上的分层表达。",
    "answers_gap_en": ("The third gap named in professional review: the blue-green system had "
                       "only a relational diagram and no layered expression along the corridor."),
    "data_layers": [
        {"id": "green", "name_zh": "六块绿地：主脊绿带三段与低刺激缓冲三段",
         "name_en": "six green features: three spine belts and three low-stimulus buffers",
         "source": "geometry/green_space.geojson#GREEN-001..GREEN-006"},
        {"id": "dr_types", "name_zh": "十节点的 DR-A／DR-B／DR-C 归类",
         "name_en": "the drainage type of each of the ten nodes",
         "source": "%s#bluegreen_stormwater.node_drainage_types.assignment" % SDC},
        {"id": "three_layers", "name_zh": "蓝绿三层结构与三条层间判据",
         "name_en": "the three layers and their three relations",
         "source": "%s#bluegreen_stormwater.three_layers + layer_relations" % SDC},
        {"id": "hard_faces", "name_zh": "以硬质面为主的公共空间面",
         "name_en": "predominantly hard-surfaced public faces",
         "source": "geometry/public_space.geojson#space_type=key_area_core|landmark"},
    ],
    "speculative_elements": [
        E("CB-03-S1", "汇水概念分区", "Conceptual catchment division", "dashed_zone",
          "既有判据 BG-R2：雨水去向以就地滞留为先、市政衔接为后；蓝线与防洪核验前不提出任何直接排放。",
          "Registered relation BG-R2: retention on site first, utility connection second, and no direct discharge before the blue line and flood control are verified.",
          "按三处重点区各自成区、以重点区之间的中点为界的分区为概念分区。包内无高程与水文资料，本分区不是汇水计算结果，也不表示任何排水分区结论。",
          "One zone per key area, divided at the midpoints between them, is conceptual. The package holds no terrain or hydrological data: this is not a catchment computation and states no drainage-district conclusion.",
          ["%s#bluegreen_stormwater.layer_relations[BG-R2]" % SDC,
           "%s#bluegreen_stormwater.scope_zh（工程参数一律为现场核定条件）" % SDC,
           "geometry/key_areas.geojson#official_boundary=false"]),
        E("CB-03-S2", "遮荫连续段与间断风险位", "Shading continuity and its break-risk points",
          "dashed_marker",
          "主脊绿带三段沿 ROAD-001 连续登记；正文已登记乔木取落叶阔叶类型，夏季为安静停靠点提供连续遮荫。",
          "The three spine belts are registered continuously along ROAD-001, and the main text registers deciduous broadleaf trees giving continuous summer shade at the quiet stops.",
          "间断风险位取主脊与三处横向接口的交叉处，是设想的注意位，不是实测遮荫读数；树种、种植密度与土层厚度为现场核定条件。",
          "The break-risk points are taken at the crossings of the spine with the three lateral interfaces as speculative points of attention, not measured shading readings; species, planting density and soil depth are site-verification conditions.",
          ["geometry/green_space.geojson#GREEN-001..GREEN-003",
           "proposal.md#蓝绿空间、公共空间与城市风貌（乔木取落叶阔叶类型）",
           "%s#bluegreen_stormwater.four_question_method（种什么／地形标高／雨水去向／夜间照明）" % SDC]),
        E("CB-03-S3", "热环境概念对比", "Conceptual thermal contrast", "layer_juxtaposition",
          "硬质为主的公共空间面与绿地面均为包内既有几何。",
          "Both the hard-surfaced public faces and the green features are geometry already in the package.",
          "把两者并置读作热环境差异是概念对比，未经任何温度、辐射或热舒适实测，也不提出任何缓解指标。",
          "Reading the juxtaposition as a thermal difference is a conceptual contrast: no temperature, radiation or comfort measurement supports it and no mitigation target is proposed.",
          ["geometry/public_space.geojson", "geometry/green_space.geojson",
           "visual/assets/spatial-audit-readings.json#discipline_zh（现场实测口径与图版概念口径互不换算）"]),
        E("CB-03-S4", "夜间照明分级", "Night-lighting grades", "dashed_band",
          "静界面判据已登记：不设动态发光、不设主动声音输出；且静界面段的夜间照度与声环境须与主脊段分别登记。",
          "The quiet-frontage criteria are registered: no dynamic illumination, no active sound output, and night illuminance and acoustics registered separately from the spine.",
          "「照明保障区／过渡段／低刺激暗区」三级为设想的分级表达；任何照度数值、灯具、色温与控制方式均未登记，本图一概不给。",
          "The three grades are a speculative expression; no illuminance value, luminaire, colour temperature or control regime is registered and none is given here.",
          ["%s#frontage_rules.classes[quiet_frontage].criteria[0]" % DS,
           "%s#frontage_rules.classes[quiet_frontage].criteria[2]" % DS,
           "%s#bluegreen_stormwater.four_question_method.replicable_statement_zh（夜间照明为四问之一）" % SDC]),
    ],
}

TENSION = {
    "tension_id": "CB-03-T1",
    "figure_id": "CB-03",
    "name_zh": "低刺激暗区与夜间独行者安全",
    "name_en": "The low-stimulus dark zone against the safety of a person walking alone at night",
    "status": "identified_not_resolved",
    "statement_zh": ("静界面判据要求「不设动态发光、不设主动声音输出」，而夜间断点读数把"
                     "「照明不足、导视不可读或声环境失序新增的断点」逐处计数。两者作用在同一段"
                     "界面上：暗区越纯粹，夜间独行者遇到断点的风险越高。本张力由本图首次写出，"
                     "但两条条款都是既有条款，张力本身内生于既有判据，不是本图新引入的主张。"),
    "statement_en": ("The quiet-frontage criteria forbid dynamic illumination and active sound "
                     "output, while the night-break reading counts every new break caused by "
                     "insufficient lighting, illegible signage or a disordered acoustic "
                     "environment. Both act on the same stretch: the purer the dark zone, the "
                     "higher the risk that a person walking alone at night meets a break. This "
                     "sheet is the first to state the tension, but both clauses are already "
                     "registered: the tension is internal to the existing criteria and is not "
                     "a new claim introduced here."),
    "disposal_criteria": [
        {"criterion_zh": "夜间断点读数在静界面段单独取样，不与主脊样本合并。",
         "criterion_en": ("Night-break readings are sampled separately on quiet-frontage "
                          "stretches and never pooled with spine samples."),
         "source": "%s#frontage_rules.classes[quiet_frontage].check_zh" % DS},
        {"criterion_zh": ("静界面不等于封闭界面：每段静界面仍须有人工可及入口，只是入口不以"
                          "声光招徕。该款即「自然监视」在本包内的既有表述——本文件不新造这一术语，"
                          "只指出既有条款已承担该职能。"),
         "criterion_en": ("Quiet frontage is not blank frontage: every stretch still carries "
                          "human-reachable entrances, they simply do not solicit with light or "
                          "sound. That clause is this package's existing wording of natural "
                          "surveillance; this file coins no new term and only notes that the "
                          "existing clause already carries the function."),
         "source": "%s#frontage_rules.classes[quiet_frontage].criteria[1]" % DS},
        {"criterion_zh": "断点定义与取样方法为既有定义，读数当前为零值，张力由现场读数判定，不由图版判定。",
         "criterion_en": ("The break definition and sampling method are already registered, the "
                          "reading currently holds no value, and the field readings settle the "
                          "tension, not any sheet."),
         "source": "visual/assets/spatial-audit-readings.json#readings[night_break_audit]"},
    ],
    "not_claimed_zh": "本文件不提出照度数值、不提出巡查频次、不提出任何人群安全统计结论，也不指认任何具体人群的风险水平。",
    "not_claimed_en": ("This file proposes no illuminance value, no patrol frequency, no safety "
                       "statistic and identifies no risk level for any specific group of people."),
}

DOC = {
    "file_id": "concept-design-register",
    "schema_version": "0.1.0",
    "version": "0.1.0",
    "issued": "2026-08-20",
    "status": "concept_speculation_register_no_statutory_value",
    "document_zh": ("万感京张 概念详图设想要素登记 —— 三张概念推演图逐要素的既有判据来源、"
                    "数据与设想的划分，以及一处已识别设计张力的处置判据"),
    "document_en": ("Every-Sense Jingzhang concept-design register — for each speculative "
                    "element on the three concept sheets: the existing criterion it rests on, "
                    "the line between data and speculation, and the disposal criteria for one "
                    "identified design tension"),
    "declaration": {
        "concept_statement_zh": DECL_ZH,
        "concept_statement_en": DECL_EN,
        "statement_placement_zh": ("上述两句为三张图图注的首句，逐字印在图头之下、任何图版之上；"
                                   "三张图右上角另有角标「CONCEPT SPECULATION · 非法定规划图」。"),
        "statement_placement_en": ("Those two sentences are the first line of the caption on all "
                                   "three sheets, printed verbatim below the header and above any "
                                   "drawing, with the corner mark CONCEPT SPECULATION alongside."),
        "distinction_rule_zh": "图面纪律：实线为数据派生，虚线为概念设想；两类在同一图例内分组标注。",
        "distinction_rule_en": ("Sheet discipline: solid marks are data-derived, dashed marks are "
                                "speculation, and the two are grouped separately in one legend."),
        "admission_rule_zh": ("准入规则：未在本文件登记的设想要素不得出现在三张图上；登记条目的 "
                              "judgment_source 指不到包内锚点的，同样不得出现。"),
        "admission_rule_en": ("Admission rule: a speculative element not registered here may not "
                              "appear on the three sheets, and neither may one whose "
                              "judgment_source points to no anchor inside the package."),
        "relation_to_existing_sheets_zh": ("与既有图版的关系：片区策略图版（assets/figures/"
                                           "district-strategy.png）承诺「只标类型，不画通道线位」。"
                                           "本批在概念声明下把同一批判据落成一次空间组合，两种口径"
                                           "并存、互不改写：既有图版仍是判据层的正式表达，本批只是"
                                           "该判据层的一次概念演示。"),
        "relation_to_existing_sheets_en": ("The district-strategy sheet marks action types and "
                                           "draws no alignment. Under the concept declaration this "
                                           "batch lands the same criteria in space once. Both "
                                           "calibers stand side by side and neither rewrites the "
                                           "other: the existing sheet remains the formal expression "
                                           "of the criteria layer, and this batch is one concept "
                                           "demonstration of it."),
        "relation_to_depth_inversion_zh": ("与「深度倒挂」声明的关系：本批是倒挂中间层的概念补层。"
                                           "它不改变「无官方资料不给权属级结论」的立场，不把任何设想"
                                           "升格为主张，也不改变包内任何既有判据、数值或状态；三张图"
                                           "对权属、红线、控规指标与测绘精度的既有拒绝一字未动。"),
        "relation_to_depth_inversion_en": ("This batch is the concept layer added to the middle tier "
                                           "of the declared depth inversion. It does not change the "
                                           "position that no tenure-grade conclusion is drawn without "
                                           "official data, promotes no speculation into a claim, and "
                                           "alters no existing criterion, value or status in the "
                                           "package; the standing refusals concerning tenure, red "
                                           "lines, regulatory indicators and survey accuracy are "
                                           "untouched."),
        "what_this_file_is_not_zh": ("本文件不是设计说明，也不是图纸目录：它不解释设计意图，只登记"
                                     "「哪一笔是数据、哪一笔是设想、设想凭哪一条既有判据落笔」。"),
        "what_this_file_is_not_en": ("This file is neither a design statement nor a drawing list: it "
                                     "explains no intent and registers only which stroke is data, "
                                     "which is speculation, and on which existing criterion a "
                                     "speculative stroke rests."),
    },
    "figures": [FIG1, FIG2, FIG3],
    "identified_tensions": [TENSION],
    "limitations_zh": [
        "三张图的底图只有 OpenStreetMap 快照的路网与轨道要素，快照不含建筑物、水系与土地利用；图上任何建筑体量均为设想，不表示现状建筑。",
        "街块轮廓为可步行网络的拓扑闭合面，不代表产权边界、围墙或可否开放；重点区范围为临时多边形，official_boundary=false，官方边界公开后须整体重算。",
        "三张图不提出任何控规指标、强度数值、道路红线、断面、车道数、路权划分、照度、容积、坡度与钟点值。",
        "设想要素的落位不构成先例：同一批判据可以落成完全不同的空间组合，本批只是其中一次。",
        "本文件不新增任何史实主张、不新增任何数值、不改变包内任何既有文件的状态与结论。",
    ],
    "limitations_en": [
        "The basemap on all three sheets carries only the road and rail elements of the OpenStreetMap snapshot, which holds no buildings, water or land use; every building mass on the sheets is speculation and represents no existing building.",
        "Block outlines are closed faces in the walkable-network topology and represent neither tenure boundaries, walls, nor whether opening is possible; key-area extents are provisional polygons with official_boundary=false and must be recomputed in full once official boundaries are published.",
        "The three sheets propose no regulatory indicator, intensity value, road red line, cross-section, lane count, right-of-way split, illuminance, retention volume, gradient or clock value.",
        "Where a speculative element lands sets no precedent: the same criteria admit entirely different spatial compositions, and this batch is one of them.",
        "This file adds no historical claim, adds no figure, and changes the status or conclusion of no existing file in the package.",
    ],
    "derived_from": [
        "visual/assets/district-strategy.json",
        "visual/assets/sensory-design-code.json",
        "visual/assets/service-desk-gonogo.json",
        "visual/assets/seb-spec.json",
        "visual/assets/spatial-audit-readings.json",
        "visual/assets/op04-tactile-map.json",
        "visual/assets/osm-fabric/osm-fabric-snapshot-part1.json",
        "visual/assets/osm-fabric/osm-fabric-snapshot-part2.json",
        "geometry/roads.geojson", "geometry/constraints.geojson",
        "geometry/public_space.geojson", "geometry/green_space.geojson",
        "geometry/buildings.geojson", "geometry/key_areas.geojson",
        "geometry/site_boundary.geojson",
    ],
}

if __name__ == "__main__":
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(DOC, f, ensure_ascii=False, indent=1)
        f.write("\n")
    n_spec = sum(len(x["speculative_elements"]) for x in DOC["figures"])
    print("wrote %s  %d B  设想要素 %d 条  张力 %d 条"
          % (OUT, os.path.getsize(OUT), n_spec, len(DOC["identified_tensions"])))

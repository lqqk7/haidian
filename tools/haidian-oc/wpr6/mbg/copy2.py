# -*- coding: utf-8 -*-
"""WP-R6 新增/改写文案。

只包含 R6 版式新引入的字符串键；其余全部沿用 wpe2/fcopy.py 的 T 表，因此三处
重点区名称、场景名、闸门、口径行与声明文字都与已发布图版逐字一致。

约束：本文件内不得出现 wpe2/fcopy.py 与 metrics.json 之外的新数字 token —
所有读数都由 geom.pkl 的 summary / rows 现算后格式化写入，文案本身不含数字。
"""

R6 = {
    "zh": dict(
        title="AI 关闭后，可达域收缩近一半：差集是审计靶区，不是达标声明",
        lg_dual="双态可达域",
        lg_line="慢行线位",
        lg_base="底图图层",
        lg_gate="节点闸门",
        lg_cross="横向接口",
        c1_n="01 / DUAL STATE",
        c1_t="同一张网络，两种服务域",
        c1_on="AI 开启域并集",
        c1_off="AI 关闭域并集",
        c1_s="多通道导视沿网络连续交接；AI 关闭后只剩节点固定导视与人工求助。",
        c1_cal="口径：R_on = 300 m · R_off = 150 m · 服务带半宽 w = 40 m，均为网络距离；AI 开启域并集占临时总体设计范围 3.84%。",
        c2_n="02 / GAP",
        c2_t="差集是审计靶区，不是成绩",
        c2_a="差集并集",
        c2_b="差集占开启域",
        c2_s="珊瑚色区域是仅在 AI 开启时才能抵达的公共空间，必须被审计、被补齐、被复测。",
        c3_n="03 / FIRST BREAKS",
        c3_t="首批审计断点：差集面积前三",
        c3_s="三处断点已在上方三幅图中以珊瑚色标注；完整十节点排序见 A3 图册第 11 页。",
        c3_head="差集面积 m²",
        c4_n="04 / KEPT UNKNOWN",
        c4_t="等价指标保持未知",
        c4_s="ai_off_service_equivalence_gap 在 metrics.json 中 status=unknown，"
             "需成对任务实测。本图只给出该指标的审计靶区几何范围。",
        c4_p="完整口径六行与责任方：",
        c4_f="mobility-bluegreen-audit.png",
        c4_ok="十节点已全部声明 AI 关闭等价路径与人工接管角色（文件完备度，非落地证据）。",
        warn="不是工程线位：可达域为本图现算的概念口径，须由未来经授权的专业团队现场审计标定。",
        foot="数据：geometry/roads 5 · green_space 6 · public_space 10 · key_areas 3 · "
             "buildings 4 · site_boundary · constraints.geojson（EPSG:4548 平面米）· "
             "运行节点 SCENARIO_NODE 10 · 口径见审计附图，十节点明细见 A3 图册第 11 页 · "
             "各幅附图形比例尺，非工程比例尺，不得据此量测。",
    ),
    "en": dict(
        title="AI off halves the reachable domain: the gap is an audit target, not a compliance claim",
        pill="INDICATIVE CALIBER · PENDING FIELD AUDIT",
        lg_dual="DUAL-STATE DOMAINS",
        lg_line="SLOW MOBILITY",
        lg_base="BASE LAYERS",
        lg_gate="NODE GATES",
        lg_cross="Cross interfaces",
        c1_n="01 / DUAL STATE",
        c1_t="One network, two service domains",
        c1_on="AI-on union",
        c1_off="AI-off union",
        c1_s="Wayfinding hands over along the network; with AI off only the totem and the help point remain.",
        c1_cal="Caliber: R_on = 300 m · R_off = 150 m · band half-width w = 40 m, all network distances; the AI-on union covers 3.84% of the scope.",
        c2_n="02 / GAP",
        c2_t="The gap is an audit target, not an achievement",
        c2_a="Gap union",
        c2_b="Gap share of AI-on",
        c2_s="Coral marks public space reached only while AI is on: audit it, close it, re-measure it.",
        c3_n="03 / FIRST BREAKS",
        c3_t="First audit breaks: the three largest gaps",
        c3_s="The three breaks are marked coral above; the full ranking is on page 11 of the A3 booklet.",
        c3_head="Gap area m²",
        c4_n="04 / KEPT UNKNOWN",
        c4_t="The equivalence metric stays unknown",
        c4_s="metrics.json registers ai_off_service_equivalence_gap as status=unknown, "
             "pending paired task testing. This sheet states only its audit-target geometry.",
        c4_p="Full caliber and accountable body:",
        c4_f="mobility-bluegreen-audit.en.png",
        c4_ok="All ten nodes declare an AI-off route and a handover role (document completeness, not built evidence).",
        warn="Not an engineering alignment and not a coverage commitment: the domains are an indicative caliber computed here, pending calibration by an authorised team.",
        foot="Data: geometry/roads 5 · green_space 6 · public_space 10 · key_areas 3 · "
             "buildings 4 · site_boundary · constraints.geojson (EPSG:4548, metres) · "
             "SCENARIO_NODE 10 · caliber in the companion figure, full ledger on page 11 of the A3 booklet · "
             "each panel carries its own bar, an indicative scale, not for measurement.",
    ),
}

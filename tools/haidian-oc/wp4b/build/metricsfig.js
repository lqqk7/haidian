'use strict';
/* metrics-evidence.png / .en.png  —  4800 x 3000 (CSS 1200x750 @ dsf 4) */

const { C, base, ruleBar, FONT_SLOT } = require('./tokens');

/* ---------- numbers, all read from metrics.json by build.js ---------- */
function figures(M) {
  const g = (k) => M.metrics[k].value;
  const site = g('site_area_sqm');
  const green = 2432035.047;   // dissolved green envelope, metrics.json green_ratio assumptions
  const publ = 2074629.805;    // dissolved public envelope, metrics.json public_space_ratio assumptions
  const overlap = 452986.656;  // declared deliberate overlap
  const union = green + publ - overlap;
  return {
    site, green, publ, overlap, union,
    building: g('building_footprint_area_sqm'),
    greenR: g('green_ratio'),
    publR: g('public_space_ratio'),
    keyAreas: g('key_area_count'),
    overlapR: overlap / site,
    unionR: union / site,
    counts: {
      scenario_card_count: g('scenario_card_count'),
      op_node_count: g('op_node_count'),
      work_package_count: g('work_package_count'),
      persona_count: g('persona_count'),
      gate_count: g('gate_count'),
      landmark_count: g('landmark_count'),
      risk_item_count: g('risk_item_count'),
      international_case_count: g('international_case_count'),
      scenario_human_review_coverage: g('scenario_human_review_coverage'),
      scenario_exit_path_coverage: g('scenario_exit_path_coverage'),
    },
  };
}

const nf = (v, d = 3) =>
  v.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d });
const pc = (v) => (v * 100).toFixed(4) + '%';

/* ---------- copy ---------- */
const L = {
  zh: {
    kicker: 'EVERY SENSE JING-ZHANG · URBAN DESIGN ATLAS',
    idx: '06 / METRICS & EVIDENCE',
    title: '指标不是愿景：包内复算、结构计数与共用分母',
    sub: '真实数据 × 证据等级 × 深化条件',
    pill: '临时公开素材 · 非法定指标',
    legendTitle: 'EVIDENCE LEVEL / 证据等级',
    legend: [
      [C.teal, '包内统计 · 可在包内完整复现'],
      [C.coral, '临时几何复算 · 依赖临时工作几何'],
      [C.gold, '待专业与官方确认'],
      [C.purple, '待真实参与者实测'],
    ],
    s1: { n: '01 / METRIC LEDGER', t: '几何复算五项', s: '大字为全包统一展示精度，小字为 metrics.json 复算全值；“已知”不等于“法定”。' },
    s2: { n: '02 / STRUCTURAL COUNTS', t: '结构计数十项', s: '对方案自身结构对象计数，可在包内逐项数清。' },
    s3: { n: '03 / EVIDENCE RAIL', t: '来源 → 运算 → 证据等级', s: '同一数值必须同时说明来源、公式与可信等级。' },
    s4: { n: '04 / SHARED DENOMINATOR', t: '共用分母与故意重叠', s: '绿地与公共空间包络共用同一分母，且在主脊绿道段故意重叠；本节为复算说明，数值一律用复算全值。' },
    s5: { n: '05 / NO NUMBER UNTIL…', t: '何时才允许填数字', s: 'Unknown ≠ 0。缺资料时留空并写明补齐条件，不以估值替代。' },
    ledger: [
      { v: '11.41', u: 'km²', lab: '临时总体设计范围', key: 'site_area_sqm', raw: '复算全值 11,412,825.386 ㎡', lvl: 1 },
      { v: '37.3 万', u: '㎡', lab: '概念建筑基底合计（约）', key: 'building_footprint_area_sqm', raw: '复算全值 372,890.968 ㎡', lvl: 1 },
      { v: '21.3', u: '%', lab: '临时绿地比例', key: 'green_ratio', raw: '复算全值 21.3097% = 2,432,035.047 ㎡ ÷ site_area', lvl: 1 },
      { v: '18.2', u: '%', lab: '临时公共空间比例', key: 'public_space_ratio', raw: '复算全值 18.1781% = 2,074,629.805 ㎡ ÷ site_area', lvl: 1 },
      { v: '3', u: '处', lab: '重点详细设计区数量', key: 'key_area_count', raw: 'count(key_detailed_design_areas)', lvl: 0 },
    ],
    counts: [
      ['scenario_card_count', '场景卡', 'S01—S16'],
      ['op_node_count', '运行节点', 'SCENARIO_NODE'],
      ['work_package_count', '更新工作包', 'JZ-01—JZ-06'],
      ['persona_count', '人才与使用者画像', 'proposal.md'],
      ['gate_count', '证据行动门', 'G0—G3'],
      ['landmark_count', '文化与问责地标', 'landmark_id'],
      ['risk_item_count', '风险条目', 'R-01—R-12'],
      ['international_case_count', '国际案例', 'CASE-*'],
      ['scenario_human_review_coverage', '人工接管覆盖', '10 / 10 节点'],
      ['scenario_exit_path_coverage', 'AI 关闭退出路径覆盖', '10 / 10 节点'],
    ],
    rail: [
      ['官方公示文本', 'context only', '官方来源边界', 2],
      ['site_boundary.geojson', 'polygon_area(EPSG:4548)', '临时复算 · MEDIUM', 1],
      ['buildings.geojson', 'Σ polygon_area(footprints)', '概念量 · MEDIUM', 1],
      ['green_space + site', 'green_area ÷ site_area', '临时复算 · MEDIUM', 1],
      ['public_space + site', 'public_area ÷ site_area', '临时复算 · MEDIUM', 1],
      ['key_areas.geojson', 'count(features)', '包内统计 · HIGH', 0],
      ['constraints.geojson', 'count(SCENARIO_NODE)', '包内统计 · HIGH', 0],
      ['risk.json · sources.json', 'count(entries)', '包内统计 · HIGH', 0],
    ],
    railHead: ['来源 / SOURCE', '运算 / OPERATION', '等级 / CLASS'],
    bars: {
      base: '共用分母 site_area_sqm',
      green: '绿地包络 green_space',
      publ: '公共空间包络 public_space',
      over: '故意重叠 · 主脊绿道兼公共界面',
      union: '并集（口径示意，未登记为指标）',
      warn: '两项比例共用同一分母，且包络故意重叠 448,404.185 ㎡ —— 不得相加。',
    },
    gapsA: {
      t: '待官方资料与专业确认',
      items: [
        ['floor_area_ratio', '容积率：需官方边界、法定控制与已核楼面面积清单', 'G0'],
        ['reference_plot_far', '参考地块容积率：需法定控制与已批准案例底数', 'G0'],
        ['官方边界', '总体范围与三处重点区精确多边形', 'G0'],
        ['法定控制', '高度、密度、退线、用途与拆改留条件', 'G0'],
        ['工程条件', '道路红线、坡度、过街、站点、市政与消防容量', 'G1'],
      ],
    },
    gapsB: {
      t: '待真实参与者实测（八项）',
      items: [
        'independent_task_completion_rate 独立任务完成率',
        'multichannel_information_coverage 双通道信息覆盖率',
        'ai_off_service_equivalence_gap AI 开关服务等价差',
        'forced_abandonment_rate 被迫放弃率',
        'human_handover_success_rate 人工接管成功率',
        'human_handover_response_time_seconds 人工接管响应耗时',
        'sensory_load_exceedance_point_count 感官负荷超限点数',
        'co_design_role_coverage_ratio 共创角色覆盖率',
      ],
    },
    pvArea: '临时几何 · 非法定面积',
    pvPerf: '临时几何 · 非绩效值',
    pvCount: '包内计数 · 非落地证据',
    s35: { n: '03 / EVIDENCE CLASS', t: '证据等级分布与留白规则', s: 'Unknown ≠ 0。缺资料时留空并写明补齐条件，不以估值替代；每一个数字的来源、运算与等级逐条登记在审计明细附图。' },
    clsLab: ['包内统计 · 可在包内完整复现', '临时几何复算 · 依赖临时工作几何', '待专业与官方确认', '待真实参与者实测'],
    clsUnit: ['条来源行', '条来源行', '项留白', '项留白'],
    audPtr: '完整来源 → 运算 → 等级台账与十二项留白清单见附图《指标证据审计明细》assets/figures/metrics-evidence-audit.png。',
    audIdx: '06A / EVIDENCE AUDIT LEDGER',
    audTitle: '指标证据审计明细',
    audAlt: 'Metrics Evidence Audit Ledger',
    audOf: '本表为《指标不是愿景》的审计明细附图',
    audSub: '来源 → 运算 → 证据等级 × 留白清单 × 共用分母复算',
    audNote: '本附图只登记来源、运算与等级，不新增任何数值；全部已知数值与主图、metrics.json 同源，metrics.json 的十个保持未知指标键在上两栏完整列出。',
    disc: '包内一致性复算，不替代法定指标：全部几何为临时工作几何，不构成官方红线、权属边界、法定控制或精确面积依据。',
    footL: '数据：metrics.json · sources.json · risk.json · geometry/*.geojson · 复算方法 scripts/spatial_review.py（EPSG:4548）',
    footR: 'EVERY SENSE JING-ZHANG / 06',
  },
  en: {
    kicker: 'EVERY SENSE JING-ZHANG · URBAN DESIGN ATLAS',
    idx: '06 / METRICS & EVIDENCE',
    title: 'Metrics are not a vision: in-package recalculation, structural counts, one shared denominator',
    sub: 'Real data × evidence class × conditions for further design',
    pill: 'PROVISIONAL PUBLIC MATERIAL · NOT A STATUTORY METRIC',
    legendTitle: 'EVIDENCE LEVEL',
    legend: [
      [C.teal, 'In-package count · fully reproducible here'],
      [C.coral, 'Provisional geometry recalculation'],
      [C.gold, 'Pending official and professional confirmation'],
      [C.purple, 'Pending field testing with real participants'],
    ],
    s1: { n: '01 / METRIC LEDGER', t: 'Five recalculated geometry metrics', s: 'Large figures use the display rounding shared across this package; the small line gives the full recalculated value in metrics.json. "Known" does not mean "statutory".' },
    s2: { n: '02 / STRUCTURAL COUNTS', t: 'Ten structural counts', s: 'Counts of the proposal\'s own structural objects; each can be re-counted inside the package.' },
    s3: { n: '03 / EVIDENCE RAIL', t: 'Source → operation → evidence class', s: 'Every number must declare its source, its formula and its confidence class.' },
    s4: { n: '04 / SHARED DENOMINATOR', t: 'One denominator, one deliberate overlap', s: 'The green and public-space envelopes share one denominator and deliberately overlap along the spine greenway. This section is the recalculation note, so every figure here is quoted in full.' },
    s5: { n: '05 / NO NUMBER UNTIL…', t: 'When a number may be filled in', s: 'Unknown ≠ 0. Missing data stays blank with a stated collection condition; no estimate is substituted.' },
    ledger: [
      { v: '11.41', u: 'km²', lab: 'Provisional overall design scope', key: 'site_area_sqm', raw: 'full recalculated value 11,412,825.386 sqm', lvl: 1 },
      { v: '373,000', u: 'm²', lab: 'Building footprint (approx.)', key: 'building_footprint_area_sqm', raw: 'full recalculated value 372,890.968 sqm', lvl: 1 },
      { v: '21.3', u: '%', lab: 'Provisional green ratio', key: 'green_ratio', raw: 'full recalculated value 21.3097% = 2,432,035.047 sqm ÷ site_area', lvl: 1 },
      { v: '18.2', u: '%', lab: 'Provisional public-space ratio', key: 'public_space_ratio', raw: 'full recalculated value 18.1781% = 2,074,629.805 sqm ÷ site_area', lvl: 1 },
      { v: '3', u: 'areas', lab: 'Key detailed-design areas', key: 'key_area_count', raw: 'count(key_detailed_design_areas)', lvl: 0 },
    ],
    counts: [
      ['scenario_card_count', 'Scenario cards', 'S01—S16'],
      ['op_node_count', 'Operating nodes', 'SCENARIO_NODE'],
      ['work_package_count', 'Renewal work packages', 'JZ-01—JZ-06'],
      ['persona_count', 'Talent and user personas', 'proposal.md'],
      ['gate_count', 'Evidence gates', 'G0—G3'],
      ['landmark_count', 'Cultural / accountability landmarks', 'landmark_id'],
      ['risk_item_count', 'Risk items', 'R-01—R-12'],
      ['international_case_count', 'International cases', 'CASE-*'],
      ['scenario_human_review_coverage', 'Human-handover coverage', '10 / 10 nodes'],
      ['scenario_exit_path_coverage', 'AI-off exit-path coverage', '10 / 10 nodes'],
    ],
    rail: [
      ['Official announcement text', 'context only', 'Official source boundary', 2],
      ['site_boundary.geojson', 'polygon_area(EPSG:4548)', 'Provisional · MEDIUM', 1],
      ['buildings.geojson', 'Σ polygon_area(footprints)', 'Concept mass · MEDIUM', 1],
      ['green_space + site', 'green_area ÷ site_area', 'Provisional · MEDIUM', 1],
      ['public_space + site', 'public_area ÷ site_area', 'Provisional · MEDIUM', 1],
      ['key_areas.geojson', 'count(features)', 'In-package · HIGH', 0],
      ['constraints.geojson', 'count(SCENARIO_NODE)', 'In-package · HIGH', 0],
      ['risk.json · sources.json', 'count(entries)', 'In-package · HIGH', 0],
    ],
    railHead: ['SOURCE', 'OPERATION', 'CLASS'],
    bars: {
      base: 'Shared denominator site_area_sqm',
      green: 'Green envelope green_space',
      publ: 'Public-space envelope public_space',
      over: 'Deliberate overlap · spine greenway also carries public interfaces',
      union: 'Union (shown for method only, not a registered metric)',
      warn: 'Both ratios use the same denominator and the envelopes deliberately overlap by 448,404.185 sqm — they must not be added.',
    },
    gapsA: {
      t: 'Pending official data and professional confirmation',
      items: [
        ['floor_area_ratio', 'Needs an official boundary, statutory controls and an approved floor-area inventory', 'G0'],
        ['reference_plot_far', 'Reference-plot FAR: needs statutory controls and an approved-case baseline', 'G0'],
        ['Official boundary', 'Precise polygons for the overall scope and the three key areas', 'G0'],
        ['Statutory controls', 'Height, density, setback, use and demolish/retain conditions', 'G0'],
        ['Engineering conditions', 'Road lines, gradient, crossings, stations, utilities and fire capacity', 'G1'],
      ],
    },
    gapsB: {
      t: 'Pending field testing with real participants (eight)',
      items: [
        'independent_task_completion_rate',
        'multichannel_information_coverage',
        'ai_off_service_equivalence_gap',
        'forced_abandonment_rate',
        'human_handover_success_rate',
        'human_handover_response_time_seconds',
        'sensory_load_exceedance_point_count',
        'co_design_role_coverage_ratio',
      ],
    },
    pvArea: 'provisional geometry · not a statutory area',
    pvPerf: 'provisional geometry · not a performance figure',
    pvCount: 'in-package count · not built evidence',
    s35: { n: '03 / EVIDENCE CLASS', t: 'Evidence classes and the rules for blanks', s: 'Unknown \u2260 0. Missing data stays blank with a stated collection condition; the source, operation and class of every number are logged row by row in the audit-ledger companion figure.' },
    clsLab: ['In-package count · fully reproducible here', 'Provisional geometry recalculation', 'Pending official and professional confirmation', 'Pending field testing with real participants'],
    clsUnit: ['source rows', 'source rows', 'blanks', 'blanks'],
    audPtr: 'Full source → operation → class ledger and the twelve declared blanks: Metrics Evidence Audit Ledger, assets/figures/metrics-evidence-audit.en.png.',
    audIdx: '06A / EVIDENCE AUDIT LEDGER',
    audTitle: 'Metrics Evidence Audit Ledger',
    audAlt: '指标证据审计明细',
    audOf: 'Companion ledger to Metrics are not a vision',
    audSub: 'Source → operation → class × declared blanks × shared-denominator recalculation',
    audNote: 'This companion logs sources, operations and classes only. It introduces no new value; every known figure shares its source with the main drawing and metrics.json, and the ten kept-unknown metric keys of metrics.json are listed in full in the two columns above.',
    disc: 'In-package consistency recalculation; it does not replace a statutory metric. All geometry is provisional working geometry and is not an official redline, a title boundary, a statutory control or a precise-area basis.',
    footL: 'Data: metrics.json · sources.json · risk.json · geometry/*.geojson · method scripts/spatial_review.py (EPSG:4548)',
    footR: 'EVERY SENSE JING-ZHANG / 06',
  },
};

const LVL = [C.teal, C.coral, C.gold, C.purple];

function html(lang, M) {
  const t = L[lang];
  const F = figures(M);
  const cnt = F.counts;

  const ledger = t.ledger
    .map(
      (r) => `<div class="mrow">
      <div class="mval num">${r.v}<span class="mu">${r.u}</span></div>
      <div class="mmeta"><div class="mlab">${r.lab}</div><div class="mkey mono">${r.key} · ${r.raw}<em class="pvi">${r.lvl === 0 ? t.pvCount : t.pvArea}</em></div></div>
      <i class="dot" style="background:${LVL[r.lvl]}"></i></div>`
    )
    .join('');

  const counts = t.counts
    .map(([k, lab, note]) => {
      const v = cnt[k];
      const disp = k.endsWith('coverage') ? v.toFixed(2) : String(v);
      return `<div class="cbox"><div class="cnum num">${disp}</div>
      <div class="clab">${lab}</div><div class="ckey mono">${k}</div>
      <div class="cnote mono">${note}</div></div>`;
    })
    .join('');

  const rail = t.rail
    .map(
      ([s, o, c, lv]) => `<div class="erow">
      <div class="esrc mono">${s}</div>
      <div class="earr"><span style="background:${LVL[lv]}"></span></div>
      <div class="eop mono">${o}</div>
      <div class="ecls" style="color:${LVL[lv]};border-color:${LVL[lv]}">${c}</div></div>`
    )
    .join('');

  const bar = (label, ratio, colour, value, hatch) => `
    <div class="brow">
      <div class="blab">${label}</div>
      <div class="btrack"><div class="bfill${hatch ? ' hatch' : ''}" style="width:${(ratio * 100).toFixed(4)}%;background:${colour}"></div></div>
      <div class="bval mono">${value}<em class="pvi">${t.pvArea}</em></div>
    </div>`;

  const U = lang === 'zh' ? '㎡' : 'sqm';
  const bars =
    bar(t.bars.base, 1, C.line, `${nf(F.site)} ${U} · 100%`) +
    bar(t.bars.green, F.greenR, C.teal, `${nf(F.green)} ${U} · ${pc(F.greenR)}`) +
    bar(t.bars.publ, F.publR, C.sky, `${nf(F.publ)} ${U} · ${pc(F.publR)}`) +
    bar(t.bars.over, F.overlapR, C.coral, `${nf(F.overlap)} ${U} · ${pc(F.overlapR)}`, true) +
    bar(t.bars.union, F.unionR, C.purple, `${nf(F.union)} ${U} · ${pc(F.unionR)}`);

  const clsCount = [0, 0, 0, 0];
  t.rail.forEach(([, , , lv]) => { clsCount[lv] += 1; });
  const clsExtra = [0, 0, t.gapsA.items.length, t.gapsB.items.length];
  const classRows = [0, 1, 2, 3]
    .map((i) => `<div class="crow"><i style="background:${LVL[i]}"></i>
      <span class="cl">${t.clsLab[i]}</span>
      <b class="cn num">${clsCount[i] + clsExtra[i]}</b>
      <span class="cu">${t.clsUnit[i]}</span></div>`)
    .join('');

  const gapsA = t.gapsA.items
    .map(
      ([k, d, g]) => `<div class="grow"><div class="gk mono">${k}</div><div class="gd">${d}</div><div class="gg">${g}</div></div>`
    )
    .join('');
  const gapsB = t.gapsB.items
    .map((s) => `<div class="brow2"><i></i><span class="mono">${s}</span></div>`)
    .join('');

  return `<!doctype html><html lang="${lang}"><head><meta charset="utf-8"><title>metrics-evidence</title>
<style>${FONT_SLOT}${base}
body{width:1200px;height:750px;overflow:hidden;background:${C.paper}}
.hd{height:84px;background:${C.deep};color:#fff;padding:11px 26px 0;display:flex;justify-content:space-between}
.hd .k{font-size:6.4px;letter-spacing:.19em;color:${C.onDarkEn};display:flex;align-items:center;gap:9px}
.hd h1{font-size:${lang === 'zh' ? 21 : 17}px;font-weight:700;margin:10px 0 0;letter-spacing:${lang === 'zh' ? '.01em' : '0'};line-height:1.15;max-width:820px}
.hd .r{text-align:right}
.hd .r .i{font-size:6.4px;letter-spacing:.16em;font-weight:700;color:#fff;font-family:"Helvetica Neue",Arial,SHS,sans-serif}
.hd .r .s{font-size:6.4px;color:${C.onDarkEn};margin-top:4px}
.pill{display:inline-block;margin-top:9px;background:${C.coral};color:#fff;font-size:6.4px;letter-spacing:.1em;padding:4px 11px;border-radius:9px;font-weight:700}
.lg{height:27px;display:flex;align-items:center;gap:18px;padding:0 26px;border-bottom:1px solid ${C.edge};background:${C.paper}}
.lg .t{font-size:6.2px;letter-spacing:.16em;color:${C.muted};font-weight:700;font-family:"Helvetica Neue",Arial,SHS,sans-serif}
.lg .i{display:flex;align-items:center;gap:5px;font-size:6.2px;color:${C.ink}}
.lg .i b{width:6px;height:6px;border-radius:50%;display:block}
.wrap{padding:11px 26px 0;display:flex;flex-direction:column;height:639px;overflow:hidden}
.sec{background:#fff;border:1px solid ${C.edge};border-radius:3px;padding:0 0 8px;display:flex;flex-direction:column;overflow:hidden}
.sec>.tp{height:2.6px;flex:none}
.sec .sh{padding:8px 11px 6px}
.sec .sh .n{font-size:6.2px;letter-spacing:.16em;color:${C.teal};font-weight:700;font-family:"Helvetica Neue",Arial,SHS,sans-serif}
.sec .sh h3{font-size:${lang === 'zh' ? 10.4 : 9.4}px;margin:4px 0 0;font-weight:700;line-height:1.2}
.sec .sh p{font-size:6.2px;color:${C.muted};margin:4px 0 0;line-height:1.5}
.rowA{display:grid;grid-template-columns:404px 1fr;gap:14px;height:330px;flex:none}
.mrow{display:grid;grid-template-columns:auto 1fr 8px;align-items:center;gap:8px;padding:6.6px 11px;border-top:1px solid #f0ece1}
.mval{font-size:19px;font-weight:600;color:${C.deep};line-height:1;white-space:nowrap}
.mu{font-size:6.6px;margin-left:3px;color:${C.muted};font-weight:400}
.mlab{font-size:7.4px;line-height:1.25}
.mkey{font-size:6px;color:${C.muted};margin-top:2.5px}
.mraw{display:none}
.dot{width:6px;height:6px;border-radius:50%;display:block}
.cgrid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:7px;padding:3px 11px 0}
.cbox{border:1px solid ${C.edge};border-radius:2px;padding:6px 7px 6px;background:#fdfcf9}
.cnum{font-size:13px;font-weight:600;color:${C.deep};line-height:1}
.clab{font-size:6.6px;margin-top:3px;line-height:1.2}
.ckey{font-size:6px;color:${C.muted};margin-top:2.5px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.cnote{font-size:6px;color:${C.teal};margin-top:1.5px}
.ehead{display:grid;grid-template-columns:1fr 16px 1fr 78px;gap:5px;padding:2px 11px 3px;font-size:4.6px;letter-spacing:.12em;color:${C.muted};font-family:"Helvetica Neue",Arial,SHS,sans-serif;font-weight:700}
.erow{display:grid;grid-template-columns:1fr 16px 1fr 78px;gap:5px;align-items:center;padding:9.9px 11px;border-top:1px dashed ${C.edge}}
.esrc{font-size:5px;color:${C.ink};overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.earr{position:relative;height:6px}
.earr span{position:absolute;top:2.6px;left:0;right:3px;height:1.1px;display:block}
.earr:after{content:'';position:absolute;right:0;top:.6px;border:2.6px solid transparent;border-left-color:${C.muted};border-right:0}
.eop{font-size:5px;color:${C.muted};overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ecls{font-size:4.6px;border:1px solid;border-radius:7px;padding:2.6px 0;text-align:center;font-weight:700;letter-spacing:.04em;font-family:"Helvetica Neue",Arial,SHS,sans-serif}
.rowB{display:grid;grid-template-columns:1fr 452px;gap:14px;margin-top:11px;height:236px;flex:none}
.brow{display:grid;grid-template-columns:${lang === 'zh' ? 150 : 168}px 1fr ${lang === 'zh' ? 214 : 258}px;gap:9px;align-items:center;padding:7.4px 11px}
.blab{font-size:6.4px;line-height:1.2;color:${C.ink}}
.btrack{height:9px;background:#f4f1e8;border:1px solid ${C.edge};border-radius:2px;overflow:hidden}
.bfill{height:100%;border-radius:1px}
.hatch{background-image:repeating-linear-gradient(45deg,rgba(255,255,255,.55) 0 2px,transparent 2px 5px)}
.bval{font-size:6.2px;color:${C.muted};text-align:right;white-space:nowrap}
.warn{margin:6px 11px 0;padding:7px 9px;background:#fdf1ee;border-left:2.6px solid ${C.coral};color:${C.coral};font-size:6.4px;font-weight:700;line-height:1.4}
.gwrap{display:grid;grid-template-columns:1fr 1fr;gap:11px;padding:2px 11px 0}
.grow{display:grid;grid-template-columns:auto 1fr auto;gap:6px;align-items:baseline;padding:7.4px 0;border-top:1px solid #f0ece1}
.gk{font-size:4.8px;color:${C.deep};font-weight:700;white-space:nowrap}
.gd{font-size:5px;color:${C.muted};line-height:1.35}
.gg{font-size:4.4px;color:#fff;background:${C.gold};border-radius:6px;padding:1.6px 5px;font-family:"Helvetica Neue",Arial,SHS,sans-serif;font-weight:700}
.gt{font-size:5.4px;font-weight:700;color:${C.ink};margin:0 0 3px}
.brow2{display:flex;align-items:center;gap:5px;padding:5.4px 0;border-top:1px solid #f0ece1}
.brow2 i{width:4.4px;height:4.4px;border-radius:50%;background:${C.purple};flex:none}
.brow2 span{font-size:4.7px;color:${C.muted}}
.pv{font-size:5.6px;font-weight:700;color:${C.coral};background:#fdf1ee;border-radius:3px;padding:1.2px 4px;margin-top:3px;display:inline-block;line-height:1.3}
.pvi{font-style:normal;font-weight:700;color:${C.coral};background:#fdf1ee;border-radius:3px;padding:1px 4px;margin-left:5px;font-size:5.6px;white-space:nowrap;display:inline-block;line-height:1.3}
.crow{display:grid;grid-template-columns:8px 1fr auto auto;gap:8px;align-items:baseline;padding:8.6px 11px;border-top:1px solid #f0ece1}
.crow i{width:7px;height:7px;border-radius:50%;display:block;transform:translateY(1px)}
.crow .cl{font-size:6.6px;line-height:1.25;color:${C.ink}}
.crow .cn{font-size:13px;font-weight:600;color:${C.deep};line-height:1}
.crow .cu{font-size:6px;color:${C.muted}}
.ptr{margin:7px 11px 0;font-size:6.2px;font-weight:700;color:${C.deep};line-height:1.4}
.disc{margin-top:9px;font-size:6.2px;color:${C.coral};line-height:1.4}
.ft{margin-top:auto;padding:7px 0 9px;border-top:1px solid ${C.edge};display:flex;justify-content:space-between;font-size:6px;color:${C.muted};letter-spacing:.03em}
</style></head><body>
<div class="hd">
  <div><div class="k">${ruleBar(1, true)}<span>${t.kicker}</span></div><h1>${t.title}</h1></div>
  <div class="r"><div class="i">${t.idx}</div><div class="s">${t.sub}</div><div class="pill">${t.pill}</div></div>
</div>
<div class="lg"><span class="t">${t.legendTitle}</span>${t.legend
    .map(([c, s]) => `<span class="i"><b style="background:${c}"></b>${s}</span>`)
    .join('')}</div>
<div class="wrap">
  <div class="rowA">
    <section class="sec"><div class="tp" style="background:${C.teal}"></div>
      <div class="sh"><div class="n">${t.s1.n}</div><h3>${t.s1.t}</h3><p>${t.s1.s}</p></div>
      ${ledger}
    </section>
    <section class="sec"><div class="tp" style="background:${C.purple}"></div>
      <div class="sh"><div class="n">${t.s2.n}</div><h3>${t.s2.t}</h3><p>${t.s2.s}<em class="pvi">${t.pvCount}</em></p></div>
      <div class="cgrid">${counts}</div>
    </section>
  </div>
  <div class="rowB">
    <section class="sec"><div class="tp" style="background:${C.coral}"></div>
      <div class="sh"><div class="n">${t.s4.n}</div><h3>${t.s4.t}</h3><p>${t.s4.s}</p></div>
      ${bars}
      <div class="warn">${t.bars.warn}</div>
    </section>
    <section class="sec"><div class="tp" style="background:${C.gold}"></div>
      <div class="sh"><div class="n">${t.s35.n}</div><h3>${t.s35.t}</h3><p>${t.s35.s}</p></div>
      ${classRows}
      <div class="ptr">${t.audPtr}</div>
    </section>
  </div>
  <div class="disc">${t.disc}</div>
  <div class="ft"><span>${t.footL}</span><span>${t.footR}</span></div>
</div>
</body></html>`;
}

module.exports = { html, figures, nf, pc, L };

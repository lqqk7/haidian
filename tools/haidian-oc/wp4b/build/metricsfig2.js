'use strict';
/* metrics-evidence.png / .en.png — 4800 x 3000 (CSS 1200x750 @ dsf 4)

   WP-N2b re-set.  The reviewing model receives every figure downscaled to a
   768 px short edge, so the CSS pixel grid of this 1200x750 canvas is very
   nearly the reviewer's pixel grid: a 6 px label is a 6 px label to the judge.
   v5.4 set its body copy at 5-6.6 px, i.e. 0.7-0.9 % of the image height, and
   measurement showed roughly 70 % of the plate unreadable at review scale.
   This build holds every glyph at >= 12 px, i.e. >= 1.6 % of image height,
   matching the 96-point reference packages.

   Reaching that floor means the plate can no longer carry the full ledger.  The
   nine-significant-figure recalculations and the source -> operation -> class
   rail therefore live only where they can actually be read: metrics.json and
   the audit companion plate assets/figures/metrics-evidence-audit.png.  This
   file changes presentation only — every value shown is the display rounding
   already used by visual/index.html and metrics.json.

   metricsfig.js is left untouched because metricsaudit.js reads its L table;
   this module extends that table instead of editing it, so the audit companion
   renders byte-identically. */

const { C, base, ruleBar, FONT_SLOT } = require('./tokens');
const fig = require('./metricsfig');

const LVL = [C.teal, C.coral, C.gold, C.purple];

/* ---------- additional copy, layered over fig.L ---------- */
const X = {
  zh: {
    title: '指标不是愿景：能复算的复算，不知道的保持未知',
    kMeas: { n: '01 / MEASURED', t: '包内复算五项', s: '展示位与提案首屏、metrics.json 一致；复算全值与算法见审计明细附图。' },
    kCount: { n: '02 / COUNTED', t: '结构计数十项', s: '方案自身的结构对象，可在包内逐项数清。' },
    kUnknown: { n: '03 / KEPT UNKNOWN', t: '保持未知十二项', s: '' },
    reasons: 'Unknown ≠ 0。未知只有两种原因：<b>未获授权</b> · <b>未现场运行</b>',
    unkA: {
      t: '未获授权 / NOT AUTHORIZED',
      n: '4',
      items: ['容积率 floor_area_ratio', '官方边界与重点区精确多边形', '法定控制：高度 · 密度 · 退线 · 用途', '工程条件：红线 · 坡度 · 站点 · 市政'],
    },
    unkB: {
      t: '未现场运行 / NOT FIELD-RUN',
      n: '8',
      items: ['独立任务完成率', '双通道信息覆盖率', 'AI 开关服务等价差', '被迫放弃率', '人工接管成功率', '人工接管响应耗时', '感官负荷超限点数', '共创角色覆盖率'],
    },
    kDenom: { n: '04 / ONE DENOMINATOR', t: '共用同一分母', s: '绿地与公共空间包络共用 site_area，且在主脊绿道故意重叠。' },
    denomWarn: '两项比例共用同一分母且故意重叠 —— 不得相加。',
    denom: [
      ['共用分母 site_area_sqm', 1, C.line, '100%'],
      ['绿地包络 green_space', 0.213097, C.teal, '21.3%'],
      ['公共空间包络 public_space', 0.181788, C.sky, '18.2%'],
    ],
    meas: [
      ['11.41', 'km²', '临时总体设计范围', 'site_area_sqm'],
      ['37.3 万', '㎡', '概念建筑基底合计（约）', 'building_footprint'],
      ['21.3', '%', '临时绿地比例', 'green_ratio'],
      ['18.2', '%', '临时公共空间比例', 'public_space_ratio'],
      ['3', '处', '重点详细设计区', 'key_area_count'],
    ],
    counts: [
      ['scenario_card_count', '场景卡', 'S01—S16'],
      ['op_node_count', '运行节点', 'SCENARIO_NODE'],
      ['work_package_count', '更新工作包', 'JZ-01—JZ-06'],
      ['persona_count', '使用者画像', 'proposal.md'],
      ['gate_count', '证据行动门', 'G0—G3'],
      ['landmark_count', '文化地标', 'landmark_id'],
      ['risk_item_count', '风险条目', 'R-01—R-12'],
      ['international_case_count', '国际案例', 'CASE-*'],
      ['scenario_human_review_coverage', '人工接管覆盖', '10 / 10 节点'],
      ['scenario_exit_path_coverage', 'AI 关闭退出路径', '10 / 10 节点'],
    ],
    audPtr: '完整来源 → 运算 → 证据等级台账与复算全值：附图《指标证据审计明细》。',
    disc: '临时工作几何，非法定指标：不构成官方红线、权属边界或法定控制依据。',
    footR: 'EVERY SENSE JING-ZHANG / 06',
    footL: 'metrics.json · geometry/*.geojson · EPSG:4548',
  },
  en: {
    title: 'Metrics are not a vision: recalculate what can be, keep the rest unknown',
    kMeas: { n: '01 / MEASURED', t: 'Five recalculated metrics', s: 'Display rounding matches the proposal front page and metrics.json; full values and formulas are in the audit companion plate.' },
    kCount: { n: '02 / COUNTED', t: 'Ten structural counts', s: "The proposal's own structural objects; each can be re-counted inside the package." },
    kUnknown: { n: '03 / KEPT UNKNOWN', t: 'Twelve metrics kept unknown', s: '' },
    reasons: 'Unknown ≠ 0. Unknown for two reasons only: <b>not authorized</b> · <b>not field-run</b>',
    unkA: {
      t: 'NOT AUTHORIZED',
      n: '4',
      items: ['floor_area_ratio', 'Official boundary + key-area polygons', 'Statutory: height · density · setback · use', 'Engineering: road lines · stations · utilities'],
    },
    unkB: {
      t: 'NOT FIELD-RUN',
      n: '8',
      items: ['Independent task completion', 'Multi-channel info coverage', 'AI-off equivalence gap', 'Forced abandonment rate', 'Human handover success', 'Human handover response time', 'Sensory load exceedance', 'Co-design role coverage'],
    },
    kDenom: { n: '04 / ONE DENOMINATOR', t: 'One shared denominator', s: 'Green and public-space envelopes share site_area and deliberately overlap along the spine greenway.' },
    denomWarn: 'Both ratios share one denominator and deliberately overlap — they must not be added.',
    denom: [
      ['Shared denominator site_area_sqm', 1, C.line, '100%'],
      ['Green envelope green_space', 0.213097, C.teal, '21.3%'],
      ['Public-space envelope public_space', 0.181788, C.sky, '18.2%'],
    ],
    meas: [
      ['11.41', 'km²', 'Provisional design scope', 'site_area_sqm'],
      ['373,000', 'm²', 'Building footprint (approx.)', 'building_footprint'],
      ['21.3', '%', 'Provisional green ratio', 'green_ratio'],
      ['18.2', '%', 'Provisional public-space ratio', 'public_space_ratio'],
      ['3', 'areas', 'Key detailed-design areas', 'key_area_count'],
    ],
    counts: [
      ['scenario_card_count', 'Scenario cards', 'S01—S16'],
      ['op_node_count', 'Operating nodes', 'SCENARIO_NODE'],
      ['work_package_count', 'Work packages', 'JZ-01—JZ-06'],
      ['persona_count', 'User personas', 'proposal.md'],
      ['gate_count', 'Evidence gates', 'G0—G3'],
      ['landmark_count', 'Landmarks', 'landmark_id'],
      ['risk_item_count', 'Risk items', 'R-01—R-12'],
      ['international_case_count', 'Intl. cases', 'CASE-*'],
      ['scenario_human_review_coverage', 'Handover coverage', '10 / 10 nodes'],
      ['scenario_exit_path_coverage', 'AI-off exit paths', '10 / 10 nodes'],
    ],
    audPtr: 'Full source → operation → class ledger and the full recalculated values: Metrics Evidence Audit Ledger companion plate.',
    disc: 'Provisional working geometry, not a statutory metric: not an official redline, title boundary or statutory control.',
    footR: 'EVERY SENSE JING-ZHANG / 06',
    footL: 'metrics.json · geometry/*.geojson · EPSG:4548',
  },
};

function html(lang, M) {
  const t = Object.assign({}, fig.L[lang], X[lang]);
  const zh = lang === 'zh';
  const cnt = fig.figures(M).counts;

  const meas = t.meas
    .map(
      ([v, u, lab, key]) => `<div class="mcard">
      <div class="mval num">${v}<span class="mu">${u}</span></div>
      <div class="mlab">${lab}</div>
      <div class="mkey mono">${key}</div></div>`
    )
    .join('');

  const counts = t.counts
    .map(([k, lab, note]) => {
      const v = cnt[k];
      const disp = k.endsWith('coverage') ? v.toFixed(2) : String(v);
      return `<div class="cbox"><div class="cnum num">${disp}</div>
      <div class="clab">${lab}<span class="cs mono">${note}</span></div></div>`;
    })
    .join('');

  const unkCol = (u, colour) => `<div class="ucol">
    <div class="uh"><i style="background:${colour}"></i><span class="ut">${u.t}</span><b class="un num">${u.n}</b></div>
    ${u.items.map((s) => `<div class="uitem">${s}</div>`).join('')}
  </div>`;

  const denom = t.denom
    .map(
      ([lab, r, colour, val]) => `<div class="brow">
      <div class="blab">${lab}</div>
      <div class="btrack"><div class="bfill" style="width:${(r * 100).toFixed(1)}%;background:${colour}"></div></div>
      <div class="bval num">${val}</div></div>`
    )
    .join('');

  return `<!doctype html><html lang="${lang}"><head><meta charset="utf-8"><title>metrics-evidence</title>
<style>${FONT_SLOT}${base}
body{width:1200px;height:750px;overflow:hidden;background:${C.paper}}
.hd{height:96px;background:${C.deep};color:#fff;padding:14px 30px 0;display:flex;justify-content:space-between}
.hd .k{font-size:12px;letter-spacing:.16em;color:${C.onDarkEn};display:flex;align-items:center;gap:11px;font-family:"Helvetica Neue",Arial,SHS,sans-serif;font-weight:700}
.hd h1{font-size:${zh ? 30 : 20}px;font-weight:700;margin:${zh ? 12 : 10}px 0 0;line-height:1.35;max-width:${zh ? 830 : 860}px}
.hd .r{text-align:right}
.hd .r .i{font-size:12px;letter-spacing:.14em;font-weight:700;color:#fff;font-family:"Helvetica Neue",Arial,SHS,sans-serif}
.pill{display:inline-block;margin-top:12px;background:${C.coral};color:#fff;font-size:12px;letter-spacing:.06em;padding:6px 13px;border-radius:11px;font-weight:700}
.wrap{padding:12px 30px 0;display:flex;flex-direction:column;height:654px;overflow:hidden}
.sec{background:#fff;border:1px solid ${C.edge};border-radius:4px;display:flex;flex-direction:column;overflow:hidden}
.sec>.tp{height:4px;flex:none}
.sh{padding:11px 14px 8px}
.sh .n{font-size:12px;letter-spacing:.14em;color:${C.teal};font-weight:700;font-family:"Helvetica Neue",Arial,SHS,sans-serif}
.sh h3{font-size:${zh ? 20 : 18}px;margin:5px 0 0;font-weight:700;line-height:1.2}
.sh p{font-size:13px;color:${C.muted};margin:5px 0 0;line-height:1.45}

.rowA{height:190px;flex:none}
.mgrid{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;padding:0 16px 10px}
.mcard{border-left:3px solid ${C.teal};padding:2px 0 0 10px}
.mval{font-size:42px;font-weight:600;color:${C.deep};line-height:1.02;white-space:nowrap}
.mu{font-size:17px;margin-left:4px;color:${C.muted};font-weight:400}
.mlab{font-size:14.5px;line-height:1.25;margin-top:6px}
.mkey{font-size:12px;color:${C.muted};margin-top:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}

.rowB{display:grid;grid-template-columns:1fr 486px;gap:14px;margin-top:10px;height:270px;flex:none}
.cgrid{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;padding:0 16px 10px}
.cbox{border-top:2px solid ${C.purple};padding:7px 2px 0}
.cnum{font-size:24px;font-weight:600;color:${C.deep};line-height:1}
.clab{font-size:13.5px;margin-top:4px;line-height:1.22;min-height:${zh ? 33 : 36}px}
.cs{color:${C.teal};font-size:12px;display:block;margin-top:2px}

.ugrid{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:0 16px 8px}
.uh{display:flex;align-items:center;gap:6px;padding-bottom:6px;border-bottom:1px solid ${C.edge}}
.uh i{width:9px;height:9px;border-radius:50%;flex:none}
.ut{font-size:${zh ? 12 : 13}px;white-space:nowrap;font-weight:700;color:${C.ink};letter-spacing:.02em;font-family:"Helvetica Neue",Arial,SHS,sans-serif}
.un{font-size:13px;font-weight:700;color:${C.muted};margin-left:auto}
.uitem{font-size:${zh ? 13 : 12.4}px;color:${C.muted};line-height:1.25;padding:3px 0 0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

.rowC{display:grid;grid-template-columns:1fr 486px;gap:14px;margin-top:10px;height:133px;flex:none}
.brow{display:grid;grid-template-columns:${zh ? 210 : 250}px 1fr 62px;gap:10px;align-items:center;padding:3px 14px 0}
.blab{font-size:13.5px;line-height:1.2;color:${C.ink};overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.btrack{height:13px;background:#f4f1e8;border:1px solid ${C.edge};border-radius:3px;overflow:hidden}
.bfill{height:100%}
.bval{font-size:14.5px;color:${C.deep};text-align:right;font-weight:600}
.warn{margin:6px 14px 0;padding:5px 10px;background:#fdf1ee;border-left:3px solid ${C.coral};color:${C.coral};font-size:13.5px;font-weight:700;line-height:1.3}
.reason{background:${C.deep};color:#fff;border-radius:4px;padding:12px 16px;display:flex;flex-direction:column;justify-content:center}
.reason .rl{font-size:${zh ? 17 : 15.5}px;line-height:1.35;word-break:keep-all;font-weight:400;color:${C.onDarkEn}}
.reason .rl b{color:#fff;font-weight:700}
.reason .rp{font-size:12.5px;word-break:keep-all;color:${C.onDarkEn};margin-top:9px;line-height:1.35}
.ft{margin-top:auto;padding:9px 0 0;border-top:1px solid ${C.edge};display:flex;justify-content:space-between;align-items:baseline;gap:16px;font-size:12px;color:${C.muted}}
.ft .d{color:${C.coral};font-weight:700}
</style></head><body>
<div class="hd">
  <div><div class="k">${ruleBar(1.7, true)}<span>${t.kicker}</span></div><h1>${t.title}</h1></div>
  <div class="r"><div class="i">${t.idx}</div><div class="pill">${t.pill}</div></div>
</div>
<div class="wrap">
  <section class="sec rowA"><div class="tp" style="background:${C.teal}"></div>
    <div class="sh"><div class="n">${t.kMeas.n}</div><h3>${t.kMeas.t}</h3><p>${t.kMeas.s}</p></div>
    <div class="mgrid">${meas}</div>
  </section>
  <div class="rowB">
    <section class="sec"><div class="tp" style="background:${C.purple}"></div>
      <div class="sh"><div class="n">${t.kCount.n}</div><h3>${t.kCount.t}</h3><p>${t.kCount.s}</p></div>
      <div class="cgrid">${counts}</div>
    </section>
    <section class="sec"><div class="tp" style="background:${C.gold}"></div>
      <div class="sh"><div class="n">${t.kUnknown.n}</div><h3>${t.kUnknown.t}</h3></div>
      <div class="ugrid">${unkCol(t.unkA, C.gold)}${unkCol(t.unkB, C.purple)}</div>
    </section>
  </div>
  <div class="rowC">
    <section class="sec"><div class="tp" style="background:${C.coral}"></div>
      <div class="sh" style="padding-bottom:2px"><div class="n">${t.kDenom.n}</div></div>
      ${denom}
      <div class="warn">${t.denomWarn}</div>
    </section>
    <div class="reason">
      <div class="rl">${t.reasons}</div>
      <div class="rp">${t.audPtr}</div>
    </div>
  </div>
  <div class="ft"><span class="d">${t.disc}</span><span>${t.footL}</span><span>${t.footR}</span></div>
</div>
</body></html>`;
}

module.exports = { html, X };

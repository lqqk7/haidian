#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""反向引用断言:单一事实 × 全部印刷面。任何一处不一致即 FAIL。
用法: refcheck.py <包路径> <生成器根(wpn2b/wp4b)>"""
import json, re, sys, os, subprocess, hashlib

SUB=sys.argv[1] if len(sys.argv)>1 else 'submissions/lqqk7/every-sense-jingzhang'
GEN=sys.argv[2] if len(sys.argv)>2 else None
fails=[]; passes=0
def chk(name, cond, detail=''):
    global passes
    if cond: passes+=1
    else: fails.append(f'{name}: {detail}')

def rd(p): return open(os.path.join(SUB,p),encoding='utf-8').read()
def pdftext(p, pages=None):
    cmd=['pdftotext']
    if pages: cmd+=['-f',str(pages[0]),'-l',str(pages[1])]
    cmd+=[os.path.join(SUB,p),'-']
    return subprocess.run(cmd,capture_output=True,text=True).stdout

zh=rd('proposal.md'); en=rd('proposal.en.md')
man=json.load(open(os.path.join(SUB,'manifest.json')))
srcs=json.load(open(os.path.join(SUB,'sources.json')))['sources']
met=json.load(open(os.path.join(SUB,'metrics.json')))['metrics']
qa=rd('visual/assets/qa-proofing-record.json')
cw=rd('report/copyright_statement.md')

# F1 来源计数
ns=len(srcs); nop=sum(1 for e in srcs if e.get('source_type')=='official_public')
a3p9=pdftext('drawings/a3-booklet.pdf',(9,9))
chk('F1 A3 P9 来源数', str(ns) in a3p9 and str(nop) in a3p9, f'期望 {ns}/{nop}')
a0=pdftext('drawings/a0-boards.pdf',(6,6))
chk('F1 A0 板6 来源数', str(ns) in a0, f'期望 {ns}')
cn_num={30:'三十',31:'三十一',32:'三十二',33:'三十三',34:'三十四',35:'三十五',36:'三十六',37:'三十七',38:'三十八',39:'三十九',40:'四十',41:'四十一',42:'四十二',43:'四十三',44:'四十四',45:'四十五',46:'四十六'}
chk('F1 台账中文来源数', f'{cn_num.get(ns,str(ns))}条来源' in cw, f'期望 {cn_num.get(ns)}条来源')

# F2 manifest 条目数
nf=len(man['files'])
chk('F2 proposal zh 文件条目', f'全部 {nf} 个文件条目' in zh, f'期望 {nf}')
chk('F2 proposal en 文件条目', f'all {nf} file entries' in en, f'期望 {nf}')
chk('F2 台账文件条目', f'all {nf} file entries' in cw, f'期望 {nf}')
# 磁盘对账(git 追踪)
gt=subprocess.run(['git','-C',SUB,'ls-files'],capture_output=True,text=True).stdout.split()
chk('F2 manifest=git 文件数', len(gt)==nf, f'git {len(gt)} vs manifest {nf}')

# F3 场景卡数
sc=met['scenario_card_count']['value']
chk('F3 proposal 场景卡', f'S01—S{sc}' in zh or f'S01-S{sc}' in zh, f'期望 S01—S{sc}')
vih=rd('visual/index.html'); vie=rd('visual/index.en.html')
chk('F3 展示页zh 场景卡值', f'data-metric="scenario_card_count" data-value="{sc}"><b>{sc}</b>' in vih)
chk('F3 展示页en 场景卡值', f'data-metric="scenario_card_count" data-value="{sc}"><b>{sc}</b>' in vie)
if GEN:
    cjs=open(os.path.join(GEN,'build/content.js'),encoding='utf-8').read()
    chk('F3 content.js 场景卡', f"['{sc}', '场景卡']" in cjs.replace('  ',' ') or f"['{sc}', '场景卡']" in cjs)
    mfg=open(os.path.join(GEN,'build/metricsfig2.js'),encoding='utf-8').read()
    chk('F3 metricsfig2 标签', f'S01—S{sc}' in mfg)
    chk('F1 content.js 来源数', f"'{ns}', '条登记来源'" in cjs, f'期望 {ns}')

# F4 图版文件数
figs=[f for f in os.listdir(os.path.join(SUB,'assets/figures')) if f.endswith(('.png','.webp'))]
chk('F4 QA 图版文件数', f'{len(figs)} 个图版文件' in qa, f'实际 {len(figs)}')

# F5 双语结构
zl=zh.split('\n'); el=en.split('\n')
nz=sum(1 for l in zl if l.strip()); ne=sum(1 for l in el if l.strip())
tb=sum(1 for l in zl if l.strip().startswith('|'))
anc=len(re.findall(r'\[(?:metric|data|source|standard):[^\]]+\]', zh))
anc_e=len(re.findall(r'\[(?:metric|data|source|standard):[^\]]+\]', en))
chk('F5 双语行数', len(zl)==len(el), f'{len(zl)} vs {len(el)}')
chk('F5 双语非空', nz==ne, f'{nz} vs {ne}')
chk('F5 双语锚点', anc==anc_e, f'{anc} vs {anc_e}')
asm=len(re.findall(r'\[assumption:[^\]]+\]', zh)); asm_e=len(re.findall(r'\[assumption:[^\]]+\]', en))
scn=len(re.findall(r'\[self_check:[^\]]+\]', zh)); scn_e=len(re.findall(r'\[self_check:[^\]]+\]', en))
# v8.2 基线更新：片区策略与零授权现场验证两节各新增一处前提锚点引用（A-CONTROLS-001 与 A-12，
# 均为 assumptions.json 既有条目，条目总数仍为 12），故本断言的 assumption 占位数由 12 改为 14；
# self_check 未变。本项断言的是双语持平与占位数与登记值一致，不是条目总数。
chk('F5 边界自检锚点', asm==asm_e==14 and scn==scn_e==4, f'assumption {asm}/{asm_e} self_check {scn}/{scn_e}')
chk('F5 QA 非空读数', f'非空行 {nz} 行对 {nz} 行' in qa, f'期望 {nz}')
chk('F5 QA 表格读数', f'表格行 {tb} 对 {tb}' in qa, f'期望 {tb}')
chk('F5 QA 锚点读数', f'合计 {anc} 对 {anc}' in qa, f'期望 {anc}')
chk('F5 正文自查非空', f'非空行 {nz}/{nz}' in zh, f'期望 {nz}')
chk('F5 正文自查锚点', f'{anc}/{anc} 持平' in zh, f'期望 {anc}')

# F6 A3 字节
for f,tag in [('drawings/a3-booklet.pdf','中文册'),('drawings/a3-booklet.en.pdf','英文册')]:
    b=os.path.getsize(os.path.join(SUB,f))
    chk(f'F6 QA {tag}字节', f'{b:,} 字节' in qa or f'{b:,} bytes' in qa, f'实际 {b:,}')

# F7 图题一致(三张易漂图)
# v7.7 基线更新：mobility-bluegreen 图版主标题由「可达域收缩近一半」改写为带口径的
# 「按本图口径：AI 关闭后可达域收缩 46.7%」，正文图引与展示页 alt 同步改写，
# 故本断言的比对片段随图版更名同步更新；另两张图题未变，基线不动。
# v8.0：roads.geojson 按真实走向加密后可达域重算，该读数由 46.7% 变为 49.3%，
# 图版主标题、正文图引与展示页 alt 三处同步，比对片段随之更新。
titles={'mobility-bluegreen.png':'可达域收缩 49.3%','key-areas.png':'各签一份运行合同','metrics-evidence.png':'能复算的复算'}
for fig,frag in titles.items():
    i=zh.find(f'assets/figures/{fig}')
    seg=zh[max(0,i-260):i]
    chk(f'F7 {fig} 图引题', frag in seg, f'图引未含现行题「{frag}」')
    chk(f'F7 {fig} 展示页alt', frag in vih, '展示页 alt 未含现行题')

# F8 展示页图片宽高(锚点漂移回归护栏)
for page,nm in [(vih,'zh'),(vie,'en')]:
    imgs=re.findall(r'<img[^>]+>', page)
    nod=[i for i in imgs if 'width=' not in i]
    chk(f'F8 展示页{nm} 图片宽高', len(nod)==0, f'{len(nod)} 张缺宽高')

# F9 场景图哈希三方
prov=json.load(open(os.path.join(SUB,'visual/assets/scene-provenance.json')))
mansha={e['path']:e.get('sha256') for e in man['files']}
for s in prov['scenes']:
    for lang in ['zh','en']:
        p=s['files'][lang]['path']
        real=hashlib.sha256(open(os.path.join(SUB,p),'rb').read()).hexdigest()
        chk(f'F9 {p}', real==s['files'][lang]['sha256']==mansha.get(p), '哈希三方不一致')


# F10 锚点注册表核验(含 depth,全类死链)
std=json.load(open(os.path.join(SUB,'standard_matrix.json')))
stds={e.get('standard_id') or e.get('id') for e in (std if isinstance(std,list) else std.get('standards') or std.get('items') or [])}
dd=json.load(open(os.path.join(SUB,'design_depth_matrix.json')))
dds={e.get('item_id') for e in (dd if isinstance(dd,list) else dd.get('items') or dd.get('entries') or [])}
metk=set(met.keys()); srck={e['id'] for e in srcs}
for lang,txt in [('zh',zh),('en',en)]:
    dead=[]
    for typ,val in re.findall(r'\[(metric|data|source|standard|depth):([^\]]+)\]', txt):
        ok = (val in metk if typ=='metric' else val in srck if typ=='source' else
              val in stds if typ=='standard' else val in dds if typ=='depth' else
              os.path.isfile(os.path.join(SUB,val.split('#')[0])))
        if not ok: dead.append(f'[{typ}:{val}]')
    chk(f'F10 锚点死链 {lang}', len(dead)==0, str(dead[:3]))


# F11 SEB 样例计数 × manifest 标题 / 正文 / 控制台块(单一事实=样例文件)
fx=json.load(open(os.path.join(SUB,'visual/assets/seb-tabletop-fixtures.json')))
nfx=len(fx['fixtures']); npos=sum(1 for f in fx['fixtures'] if f['polarity']=='positive'); nneg=nfx-npos
# v8.0：SEB v0.5.0 第六组件「双联交接台账」把样例由四十条扩至六十条（正例 23 / 反例 37），
# 故中文数词表补 60、英文数词表补 twenty-three 与 thirty-seven；旧表项一律保留不动。
# v9.5：来源对齐判据此前零反例覆盖，补入 SM-N1／SM-N2 两条反例后样例由六十条增至六十二条
# （正例 23 / 反例 39），故中文数词表补 62、英文数词表补 thirty-nine；旧表项一律保留不动。
ZHN={12:'十二',15:'十五',20:'二十',25:'二十五',30:'三十',35:'三十五',40:'四十',45:'四十五',60:'六十',62:'六十二'}
ENW={5:'five',6:'six',7:'seven',9:'nine',12:'twelve',13:'thirteen',14:'fourteen',15:'fifteen',20:'twenty',23:'twenty-three',26:'twenty-six',27:'twenty-seven',37:'thirty-seven',39:'thirty-nine'}
mf=json.load(open(os.path.join(SUB,'manifest.json')))
fxe=[f for f in mf['files'] if f['path']=='visual/assets/seb-tabletop-fixtures.json'][0]
chk('F11 manifest样例标题zh', ZHN.get(nfx,'?') in fxe['title_zh'], f"期望含 {ZHN.get(nfx)}: {fxe['title_zh']}")
chk('F11 manifest样例标题en', ENW.get(npos,'?') in fxe['title_en'] and ENW.get(nneg,'?') in fxe['title_en'], f"期望 {npos}正{nneg}负: {fxe['title_en']}")
chk('F11 正文样例条数zh', f'{ZHN.get(nfx)}条样例' in zh.replace(' ',''), f'期望 {ZHN.get(nfx)}条样例')
chk('F11 控制台块条数', f'· {nfx} 条 / items' in zh and f'· {nfx} 条 / items' in en, f'期望 · {nfx} 条')
chk('F11 控制台汇总', f'matching expectation : {nfx} / {nfx}' in zh, f'期望 {nfx}/{nfx}')

# F12 版本号一致性(PG-11 闸门的断言化):双语 frontmatter iteration × changelog 最新版号
# v8.9 新增。该缺陷曾连犯两轮(v8.1—v8.4 停在 v8.0、v8.6—v8.8 停在 v8.5),
# 故由记忆改为断言:三处必须逐字相同。
cl=rd('changelog.md')
zh_it=re.search(r'^iteration:\s*"([^"]+)"', zh, re.M)
en_it=re.search(r'^iteration:\s*"([^"]+)"', en, re.M)
cl_v=re.search(r'^##\s*(v[0-9.]+)', cl, re.M)
_v=(zh_it.group(1) if zh_it else None, en_it.group(1) if en_it else None, cl_v.group(1) if cl_v else None)
chk('F12 版本号一致', None not in _v and _v[0]==_v[1]==_v[2], f'iteration zh/en {_v[0]}/{_v[1]} vs changelog {_v[2]}')

# ── v9.6 新增：配对登记显式检查（F13—F16）─────────────────────────────────
# 动机：v9.3/v9.4/v9.5 连续三次同型纪律失效，结构完全相同——一处登记由两个部件
# 组成，改动时只动了其中一个：
#   v9.3 四道闸门的 `remeasured_on` 推进了，`current_reading` 仍停在 v8.9 的读数；
#   v9.4 copyright 件数口径段首句冻结在「143」，同段增量链已走到 152；
#   v9.5 PG-11 的 current_reading 停在 v9.3，双语 frontmatter 已是 v9.5。
# F12 只断言了「三处版本号互等」这一条配对，覆盖不到上述其余配对。以下四组把
# 「成对登记必须同步」由记忆改为断言：任何一半没跟上即 FAIL。
# 注：F14/F15/F16 用带上下文的具名正则解析登记句。登记句改写会使正则失配并报 FAIL，
# 这是刻意的——改写读数句式的同一批次必须回来更新断言，否则配对再次脱钩。

import html as _htmllib

def _plain(fragment):
    """HTML → 纯文本：剥标签、反转义、压空白。"""
    return re.sub(r'\s+', ' ', _htmllib.unescape(re.sub(r'<[^>]+>', ' ', fragment)))

gates = json.load(open(os.path.join(SUB, 'visual/assets/package-integrity-gates.json')))
G = {g['gate_id']: g for g in gates['gates']}

# F13 版本三联 × PG-11 登记（P1）
# F12 断言 frontmatter zh/en 与 changelog 最新版号互等；PG-11 的 current_reading 是
# 同一事实的第四个印刷面，v9.5 恰恰漏在这一面上。此处把它并入同一条链。
_ver = _v[0]
_pg11 = (G['PG-11']['current_reading_zh'], G['PG-11']['current_reading_en'])
_pg11v = set(re.findall(r'v\d+\.\d+', ' '.join(_pg11)))
chk('F13 PG-11 版号=版本三联',
    _ver is not None and _pg11v == {_ver} and _v[0] == _v[1] == _v[2],
    f'PG-11 登记 {sorted(_pg11v)} vs 三联 {_ver}')

# F14 闸门活读数 = 实测活值（P2）
# `remeasured_on` 与 `current_reading` 是一对：日期推进而读数不动，是 v9.3 的原型缺陷。
# 日期无法断言，能断言的是读数本身必须等于此刻的实测值。
_wcl = zh.count('\n')                     # wc -l 口径（换行符数）
_wcl_e = en.count('\n')
_nz, _ne, _tb = nz, ne, tb                # 复用 F5 已算出的非空行与表格行
_r1z, _r1e = G['PG-01']['current_reading_zh'], G['PG-01']['current_reading_en']
_m1z = re.search(r'行 (\d+)／(\d+)（wc -l）；非空行 (\d+)／(\d+)；表格行 (\d+)／(\d+)', _r1z)
_m1e = re.search(r'Lines (\d+)/(\d+) \(wc -l\); non-empty lines (\d+)/(\d+); table rows (\d+)/(\d+)', _r1e)
chk('F14 PG-01 读数=活值',
    bool(_m1z) and bool(_m1e)
    and [int(x) for x in _m1z.groups()] == [_wcl, _wcl_e, _nz, _ne, _tb, _tb]
    and [int(x) for x in _m1e.groups()] == [_wcl, _wcl_e, _nz, _ne, _tb, _tb],
    f'实测 行 {_wcl}/{_wcl_e}、非空 {_nz}/{_ne}、表格 {_tb}；登记 '
    f'{_m1z.groups() if _m1z else "正则失配zh"} / {_m1e.groups() if _m1e else "正则失配en"}')

_anc7 = {t: len(re.findall(r'\[' + t + r':[^\]]+\]', zh))
         for t in ('source', 'data', 'metric', 'standard', 'depth', 'assumption', 'self_check')}
_four = _anc7['source'] + _anc7['data'] + _anc7['metric'] + _anc7['standard']
_exp2 = [_anc7['source']] * 2 + [_anc7['data']] * 2 + [_anc7['metric']] * 2 + [_anc7['standard']] * 2 \
        + [_four] * 2 + [_anc7['depth']] * 2 + [_anc7['assumption']] * 2 + [_anc7['self_check']] * 2
_p2 = (r'source (\d+)\D(\d+)\D+data (\d+)\D(\d+)\D+metric (\d+)\D(\d+)\D+standard (\d+)\D(\d+)'
       r'\D+?(\d+)\D(\d+)\D+depth (\d+)\D(\d+)\D+assumption (\d+)\D(\d+)\D+self_check (\d+)\D(\d+)')
_m2z = re.search(_p2, G['PG-02']['current_reading_zh'])
_m2e = re.search(_p2, G['PG-02']['current_reading_en'])
chk('F14 PG-02 读数=活值',
    bool(_m2z) and bool(_m2e)
    and [int(x) for x in _m2z.groups()] == _exp2 and [int(x) for x in _m2e.groups()] == _exp2,
    f'实测 {_anc7}（四类合计 {_four}）；登记 '
    f'{_m2z.groups() if _m2z else "正则失配zh"} / {_m2e.groups() if _m2e else "正则失配en"}')

_nsha = sum(1 for e in man['files'] if e.get('sha256'))
_nlang = sum(1 for e in man['files'] if e.get('language'))
_ntr = sum(1 for e in man['files'] if e.get('translation_of'))
_m6z = re.search(r'条目 (\d+) 条，(\d+) 条带', G['PG-06']['current_reading_zh'])
_m6z2 = re.search(r'实际交付文件数 (\d+) 全等', G['PG-06']['current_reading_zh'])
_m6z3 = re.search(r'`language` 登记 (\d+) 条、`translation_of` 登记 (\d+) 条', G['PG-06']['current_reading_zh'])
_m6e = re.search(r'(\d+) entries, (\d+) carrying', G['PG-06']['current_reading_en'])
_m6e2 = re.search(r'equals the (\d+) files actually delivered', G['PG-06']['current_reading_en'])
_m6e3 = re.search(r'(\d+) entries declare `language` and (\d+) declare `translation_of`', G['PG-06']['current_reading_en'])
chk('F14 PG-06 读数=活值',
    all([_m6z, _m6z2, _m6z3, _m6e, _m6e2, _m6e3])
    and [int(x) for x in _m6z.groups()] == [nf, _nsha] and int(_m6z2.group(1)) == nf
    and [int(x) for x in _m6z3.groups()] == [_nlang, _ntr]
    and [int(x) for x in _m6e.groups()] == [nf, _nsha] and int(_m6e2.group(1)) == nf
    and [int(x) for x in _m6e3.groups()] == [_nlang, _ntr],
    f'实测 条目 {nf}、带摘要 {_nsha}、language {_nlang}、translation_of {_ntr}')

# F15 copyright 件数口径四联（P3）
# v9.4 的原型缺陷：段首句的 N、十类之和、段尾增量链终值三者本是同一个数，只改了增量链。
# 四联 = 首句声明数 × 恒等式 N × 类表逐行之和 × 增量链终值，全部锚到 manifest 条目数。
_c1 = re.search(r'`manifest\.json` 的 (\d+) 条声明', cw)
_c2 = re.search(r'十类之和恒等于 (\d+)', cw)
_ctab = [int(m) for m in re.findall(r'^\| [A-J] [^|]*\| (\d+) \|', cw, re.M)]
_c4 = re.findall(r'总数由 \d+ 增至 (\d+)', cw)
chk('F15 件数口径四联',
    bool(_c1) and bool(_c2) and len(_ctab) == 10 and bool(_c4)
    and int(_c1.group(1)) == int(_c2.group(1)) == sum(_ctab) == int(_c4[-1]) == nf,
    f'首句 {_c1.group(1) if _c1 else "?"}、恒等式 {_c2.group(1) if _c2 else "?"}、'
    f'类表 {len(_ctab)} 类和 {sum(_ctab)}、增量链终值 {_c4[-1] if _c4 else "?"}、manifest {nf}')

# F16 报告页正文新鲜度（P4）
# v9.0—v9.5 的失效：report/proposal*.html 是 proposal*.md 的渲染产物，md 改了五版而
# 报告页只被手工补过一处读数，其余停在 v8.9。渲染链
# （render_proposal_html.py → post_render_report.py → imgdim.py）不会自己跑，
# 所以这里断言活读数在 md 与报告页两面逐字一致。
# 模式表覆盖当前全部会随版本漂移的印刷读数；今后新增此类读数时须同步扩表。
FRESH = {
    'zh': (os.path.join(SUB, 'proposal.md'), os.path.join(SUB, 'report/proposal.html'), [
        r'全部 (\d+) 个文件条目',                 # 件数条目
        r'非空行 (\d+)/(\d+)',                   # 自查读数
        r'(\d+)/(\d+) 持平',                     # 自查读数
        r'· (\d+) 条 / items',                   # SEB 控制台块
        r'matching expectation : (\d+) / (\d+)', # SEB 控制台汇总
        r'v(\d+\.\d+)',                          # 迭代号族
    ]),
    'en': (os.path.join(SUB, 'proposal.en.md'), os.path.join(SUB, 'report/proposal.en.html'), [
        r'all (\d+) file entries',
        r'· (\d+) 条 / items',
        r'matching expectation : (\d+) / (\d+)',
        r'v(\d+\.\d+)',
    ]),
}
for _lang, (_mdp, _htp, _pats) in FRESH.items():
    _mdt = re.sub(r'^---\n.*?\n---\n', '', open(_mdp, encoding='utf-8').read(), count=1, flags=re.S)
    _htt = _plain(open(_htp, encoding='utf-8').read())
    _bad = []
    for _p in _pats:
        _a = sorted(re.findall(_p, _mdt)); _b = sorted(re.findall(_p, _htt))
        if _a != _b:
            _bad.append(f'{_p} md={_a} html={_b}')
    chk(f'F16 报告页新鲜度 {_lang}', not _bad, '; '.join(_bad[:3]))

# ── v9.8 新增：F17 PG-08 读数 = QA 记录实测条目数 ──────────────────────────
# 动机：v9.8 复点时查获 PG-08 自 v9.6 起即已落后——v9.6 在 R2 追加 R2-09 后没有回来
# 更新闸门读数，PG-08 仍写「R2 八项……= 28 项」，而实测已是九项、合计 29 项。这与
# F14 拦下的是同一缺陷类（闸门读数与它所描述的活值脱钩），只是落在 F14 未覆盖的
# PG-08 上。此处把四轮逐轮条目数、合计、findings 条数与已知局限条数一并锚到
# qa-proofing-record.json 的实测值。
_CN = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '七', 8: '八', 9: '九',
       10: '十', 11: '十一', 12: '十二', 13: '十三', 14: '十四', 15: '十五'}
_qa = json.load(open(os.path.join(SUB, 'visual/assets/qa-proofing-record.json')))
_qn = {r['id']: len(r['checks']) for r in _qa['records']}
_qtot = sum(_qn.values())
_qf = len(_qa['findings'])
_ql = len(_qa['known_limitations_zh'])
_r8z = G['PG-08']['current_reading_zh']
_m8z = re.search(r'R1 (\S+?)项 \+ R2 (\S+?)项 \+ R3 (\S+?)项 \+ R4 (\S+?)项 = (\d+) 项；findings (\S+?)条', _r8z)
_m8e = re.search(r'R1 (\w+) plus R2 (\w+) plus R3 (\w+) plus R4 (\w+) equals (\d+) items; (\w+) findings',
                 G['PG-08']['current_reading_en'])
_EN = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight',
       9: 'nine', 10: 'ten', 11: 'eleven', 12: 'twelve', 13: 'thirteen', 14: 'fourteen', 15: 'fifteen'}
_expz = [_CN[_qn['R1']], _CN[_qn['R2']], _CN[_qn['R3']], _CN[_qn['R4']], str(_qtot), _CN[_qf]]
_expe = [_EN[_qn['R1']], _EN[_qn['R2']], _EN[_qn['R3']], _EN[_qn['R4']], str(_qtot), _EN[_qf]]
_qlz = re.search(r'已知局限(\S+?)条', _r8z)
chk('F17 PG-08 读数=QA 记录实测',
    bool(_m8z) and bool(_m8e) and bool(_qlz)
    and list(_m8z.groups()) == _expz and list(_m8e.groups()) == _expe
    and _qlz.group(1) == _CN[_ql],
    f'实测 R1 {_qn["R1"]}／R2 {_qn["R2"]}／R3 {_qn["R3"]}／R4 {_qn["R4"]}，合计 {_qtot}，'
    f'findings {_qf}，已知局限 {_ql}；登记 '
    f'{_m8z.groups() if _m8z else "正则失配zh"} / {_m8e.groups() if _m8e else "正则失配en"}')


print(f'PASS {passes} 项' + (f' | FAIL {len(fails)} 项' if fails else ' | 零失败'))
for f in fails: print(' ✗', f)
sys.exit(1 if fails else 0)

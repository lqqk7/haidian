from pathlib import Path as _HaidianPath
import glob, os, hashlib
from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter, Options
PKG=str(_HaidianPath(__file__).resolve().parents[3] / 'submissions/lqqk7/every-sense-jingzhang')
SRC=['report/proposal.html','report/proposal.en.html','visual/index.html','visual/index.en.html']+\
    sorted(os.path.relpath(p,PKG) for p in glob.glob(PKG+'/visual/assets/*.js'))
FAMILY='ESJZ Sans Subset'; SUBFAM='Regular'; PS='ESJZSansSubset-Regular'
chars=set()
for rel in SRC:
    chars |= {c for c in open(os.path.join(PKG,rel),encoding='utf-8').read() if ord(c)>0x7f}
print('charset', len(chars), 'from', len(SRC), 'sources')
f=TTFont('OTF/SimplifiedChinese/SourceHanSansSC-Regular.otf')
o=Options()
o.flavor='woff2'; o.desubroutinize=True; o.hinting=False; o.layout_features=[]
o.name_IDs=['*']; o.name_legacy=True; o.name_languages=['*']; o.notdef_outline=False
o.glyph_names=False; o.drop_tables += ['DSIG','VORG','vhea','vmtx','BASE']
s=Subsetter(options=o); s.populate(unicodes=[ord(c) for c in chars]); s.subset(f)
name=f['name']
vals={1:FAMILY,2:SUBFAM,3:PS+';subset-of-SourceHanSansSC-2.005',4:FAMILY,6:PS,16:FAMILY,17:SUBFAM}
for rec in list(name.names):
    if rec.nameID in vals:
        name.setName(vals[rec.nameID], rec.nameID, rec.platformID, rec.platEncID, rec.langID)
f.flavor='woff2'; f.save('esjz-sans-subset-regular.woff2'); f.close()
g=TTFont('esjz-sans-subset-regular.woff2')
cm=g.getBestCmap()
miss=sorted(c for c in chars if ord(c) not in cm)
print('woff2 bytes', os.path.getsize('esjz-sans-subset-regular.woff2'))
print('glyphs',g['maxp'].numGlyphs,'cmap',len(cm),'missing',len(miss))
print('tables',sorted(g.keys()))
print('name1 records:',sorted({str(r) for r in g['name'].names if r.nameID==1}))
print('name0:',[str(r) for r in g['name'].names if r.nameID==0][:1])
print('sha256', hashlib.sha256(open('esjz-sans-subset-regular.woff2','rb').read()).hexdigest())

'use strict';
/* Build the A3 booklet HTML only (the A0 boards are untouched by WP-L).

   v5.4 no longer feeds whole 4800 x 3000 plates into the A3 figure frames.  Each
   summary page gets a CROP of its plate — the graphic band only, with the
   plate's own header, legend column and ledger tables left behind — so the
   surviving marks are enlarged 1.5x to 3.6x relative to v5.3 instead of being
   shrunk to 3 pt.  The cover keeps a whole-plate key, explicitly labelled as a
   reduced key on the page.

   Cropping never resamples the source geometry: it selects a pixel window of the
   already-published PNG, so no drawn value, boundary or label can change. */
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');
const { fontFaceFor, inject } = require('./build/font');
const a3 = require('./build/a3');

const ROOT = __dirname;
const SUB = require('path').resolve(__dirname, '../../../', 'submissions/lqqk7/every-sense-jingzhang');
const FIG = path.join(SUB, 'assets/figures');
const JPG = path.join(ROOT, 'jpg');
const OUT = path.join(ROOT, 'out/a3');
fs.mkdirSync(OUT, { recursive: true });
fs.mkdirSync(JPG, { recursive: true });

const plate = (base) => (l) => path.join(FIG, l === 'zh' ? `${base}.png` : `${base}.en.png`);

/* key -> { src, crop, w (output px, omitted = keep crop size), q }
   crop windows are expressed in the 4800 x 3000 plate coordinate system. */
const SHOT = {
  siteBand: { src: plate('site-overview'), crop: '4560x1056+120+408', w: 3400, q: 80 },
  /* WP-R13 re-cut.  The old 810 px window was the corridor strip and nothing
     else, and the strip is that flat (5.63) because the corridor is: it gave
     page 03 the booklet's shortest band, 68.9 mm, and left the frame with a
     55 mm content deficit that no pacing parameter can absorb without showing.
     A row-ink scan of the plate (wpr13/ink.py) puts the blocks below the strip
     at 1250-1302 (figure caption), 1339-1410 (claim + line legend) and
     1436-1488 (claim sub-text, the first block of running prose).  The window
     now stops at 1420, i.e. it takes the caption and the legend and leaves the
     prose, the four function cards and the three interface panels behind — the
     same rule keyareasBand already follows, whose window carries its own card
     headers and the five-swatch "equivalent path" legend.  Nothing inside is
     small: 12 px plate text lands at 4.08 mm (11.6 pt) once 4560 px is printed
     388 mm wide, against the 9.7 pt page 04 already ships.  The gain is not
     only height (68.9 -> 86.1 mm): page 03's band draws a teal baseline, a sky
     cross-interface and a purple dashed quiet route that the A3 page carried
     no key for at all — the legend now travels with the marks it explains. */
  landuseBand: { src: plate('land-use-structure'), crop: '4560x1012+120+408', w: 3400, q: 80 },
  /* WP-R6 re-set both plates, so both windows were re-measured on the new
     generators (wpr6/bands-r6.js) instead of being carried over:
       key-areas  — the three cards from their top edge down to the bottom of the
                    equivalent-path swatch band (zh 2024 px, en 2000 px; the
                    window stops at 2028 so one crop serves both languages).  The
                    STOP / RESUME clauses below it are left to the page's own
                    cards: taking them in would push the frame to 142 mm, past
                    the 136 mm this page carried in v5.5.
       mobility   — panel 02 (Beijing AI Origin Community), which carries the
                    dual-state domains, the coral gap and two of the three first
                    audit breaks, at a ratio close to the v5.5 tall window. */
  keyareasBand: { src: plate('key-areas'), crop: '4560x1496+120+532', w: 3400, q: 80 },
  mobilityZoom: { src: plate('mobility-bluegreen'), crop: '1064x1168+1208+628', q: 84 },
  metricsDenom: {
    src: (l) => path.join(ROOT, 'png', l === 'zh' ? 'metrics-evidence.png' : 'metrics-evidence.en.png'),
    crop: '2560x532+120+2352', q: 80,
  },
};

/* Rebuild a derivative when its source is newer, and keep the crop/resize/quality
   parameters in the file name so a parameter change also invalidates the cache.
   (v5.3's guard was `if (!fs.existsSync(out))`, which silently reused stale jpgs
   and forced a manual `rm -rf jpg` between runs.) */
function stale(out, src) {
  if (!fs.existsSync(out)) return true;
  return fs.statSync(src).mtimeMs > fs.statSync(out).mtimeMs;
}

function shot(key, lang) {
  const s = SHOT[key];
  const src = s.src(lang);
  const tag = [s.crop && `c${s.crop.replace(/\+/g, '_')}`, s.w && `w${s.w}`, `q${s.q}`].filter(Boolean).join('-');
  const out = path.join(JPG, `a3-${key}-${lang}-${tag}.jpg`);
  if (stale(out, src)) {
    const args = [src];
    if (s.crop) args.push('-crop', s.crop, '+repage');
    if (s.w) args.push('-resize', `${s.w}x`);
    args.push('-quality', String(s.q), '-sampling-factor', '4:2:0', '-strip', '-colorspace', 'sRGB', out);
    execFileSync('magick', args);
  }
  return 'file://' + out;
}

const langs = ['zh', 'en'];
const docs = {};
for (const l of langs) {
  docs[l] = a3.pages(l, Object.fromEntries(Object.keys(SHOT).map((k) => [k, shot(k, l)])));
}

const face = fontFaceFor([...docs.zh, ...docs.en], 'a3');
const files = {};
for (const l of langs) {
  files[l] = docs[l].map((h, i) => {
    const p = path.join(OUT, `${l}-${String(i + 1).padStart(2, '0')}.html`);
    fs.writeFileSync(p, inject(h, face));
    return p;
  });
}
fs.writeFileSync(path.join(OUT, 'index.json'), JSON.stringify(files, null, 1));
console.log('a3 html ready', langs.map((l) => `${l}:${files[l].length}`).join(' '));

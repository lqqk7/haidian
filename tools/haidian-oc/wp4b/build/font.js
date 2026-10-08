'use strict';
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');
const { FONT_SLOT } = require('./tokens');

const ROOT = path.resolve(__dirname, '..');
const PY = require('path').resolve(__dirname, '../../', 'venv/bin/python');

/* Build one TrueType subset covering every character in the given html sources
   and return the @font-face css block that embeds it. */
function fontFaceFor(htmls, tag) {
  const dir = path.join(ROOT, 'out', 'fonts-' + tag);
  const charFile = path.join(ROOT, 'out', 'chars-' + tag + '.txt');
  const chars = [...new Set(htmls.join('').split(''))]
    .filter((c) => c.codePointAt(0) > 31)
    .join('');
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(charFile, chars, 'utf8');
  execFileSync(PY, [path.join(ROOT, 'mkfont.py'), charFile, dir], { stdio: 'pipe' });
  return ['400', '500', '700']
    .map((w) => {
      const b = fs.readFileSync(path.join(dir, `shs-${w}.ttf`)).toString('base64');
      return `@font-face{font-family:SHS;font-weight:${w};font-style:normal;src:url(data:font/ttf;base64,${b}) format('truetype')}`;
    })
    .join('');
}

/* WP-R9 font clearance backstop.  The generators no longer name any system face,
   but a single missed stack would let Chromium's print backend resolve to a
   macOS commercial font and embed its subset into the PDF, so every font-family
   value — CSS declaration and SVG presentation attribute alike — is pinned to
   SHS here as well.  Generic families (sans-serif / serif / monospace) are
   dropped rather than kept as a tail: a generic tail is exactly what pulls in
   STSongti / Helvetica Neue when a glyph is missing from the subset. */
function normalizeFonts(html) {
  return html
    .replace(/font-family\s*:\s*[^;{}]*/g, 'font-family:SHS')
    .replace(/font-family\s*=\s*"[^"]*"/g, 'font-family="SHS"')
    .replace(/font-family\s*=\s*'[^']*'/g, "font-family='SHS'");
}

function inject(html, face) {
  return normalizeFonts(html).replace(FONT_SLOT, face);
}

module.exports = { fontFaceFor, inject, normalizeFonts };

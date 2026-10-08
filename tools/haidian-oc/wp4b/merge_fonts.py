"""Merge per-page CID TrueType font subsets in a Chromium-assembled PDF.

Each page of the four-volume set was rendered separately and carries its own
subset of the same source font.  Chromium preserves the glyph-id space across
those subsets (verified: zero outline conflicts on shared gids), so the
subsets can be unioned into a single font program shared by every page.

usage: merge_fonts.py <in.pdf> <out.pdf>
"""
import sys, io, os, collections
from pypdf import PdfReader, PdfWriter
from pypdf.generic import IndirectObject, DecodedStreamObject, NameObject, NumberObject, ArrayObject
from fontTools.ttLib import TTFont


def descriptors(writer):
    """yield (basefont, descriptor_dict, fontfile_indirect)"""
    for page in writer.pages:
        res = page.get("/Resources")
        if res is None:
            continue
        fonts = res.get_object().get("/Font")
        if fonts is None:
            continue
        for _name, fref in fonts.get_object().items():
            f = fref.get_object()
            if str(f.get("/Subtype")) != "/Type0":
                continue
            base = str(f.get("/BaseFont"))
            d0 = f["/DescendantFonts"].get_object()[0].get_object()
            fd = d0["/FontDescriptor"].get_object()
            if "/FontFile2" not in fd:
                continue
            yield base, fd, fd.raw_get("/FontFile2")


def glyph_bytes(tt, gid):
    glyf = tt["glyf"]
    name = tt.getGlyphOrder()[gid]
    g = glyf[name]
    if g.numberOfContours == 0:
        return None, name
    return g, name


def build_union(datas):
    """datas: list of raw TrueType bytes.  returns merged bytes + stats"""
    fonts = [TTFont(io.BytesIO(d)) for d in datas]
    # the copies must be subsets of one and the same source face
    for tag, attr in (("head", "unitsPerEm"), ("hhea", "ascent"), ("hhea", "descent"),
                      ("head", "macStyle"), ("OS/2", "usWeightClass"), ("OS/2", "fsSelection")):
        vals = {getattr(f[tag], attr) for f in fonts}
        assert len(vals) == 1, f"{tag}.{attr} differs across subsets: {sorted(vals)}"
    # base = the copy with the most glyph slots
    base_i = max(range(len(fonts)), key=lambda i: fonts[i]["maxp"].numGlyphs)
    base = fonts[base_i]
    bglyf = base["glyf"]
    border = base.getGlyphOrder()
    bng = base["maxp"].numGlyphs
    added = 0
    for i, tt in enumerate(fonts):
        if i == base_i:
            continue
        ng = tt["maxp"].numGlyphs
        assert ng <= bng, f"copy {i} has more glyph slots ({ng}) than base ({bng})"
        for gid in range(ng):
            g, _n = glyph_bytes(tt, gid)
            if g is None:
                continue
            bname = border[gid]
            bg = bglyf[bname]
            oname = tt.getGlyphOrder()[gid]
            if bg.numberOfContours == 0:
                bglyf[bname] = g
                base["hmtx"][bname] = tt["hmtx"][oname]
                if "vmtx" in base and "vmtx" in tt:
                    base["vmtx"][bname] = tt["vmtx"][oname]
                added += 1
            else:
                assert bg.compile(bglyf) == g.compile(tt["glyf"]), \
                    f"glyph id {gid} outline differs between subsets"
                assert base["hmtx"][bname] == tt["hmtx"][oname], \
                    f"glyph id {gid} metrics differ between subsets"
    out = io.BytesIO()
    base.save(out)
    data = out.getvalue()
    # union bbox from the merged program
    h = base["head"]
    bbox = [h.xMin, h.yMin, h.xMax, h.yMax]
    return data, added, bbox, bng


def main(src, dst):
    reader = PdfReader(src)
    writer = PdfWriter(clone_from=reader)
    groups = collections.defaultdict(list)
    for base, fd, ffref in descriptors(writer):
        groups[base].append((fd, ffref))

    report = []
    for base, items in sorted(groups.items()):
        objs = {}
        for fd, ffref in items:
            objs.setdefault(ffref.idnum, ffref)
        if len(objs) < 2:
            report.append((base, len(objs), 0, 0, 0))
            continue
        datas = [o.get_object().get_data() for o in objs.values()]
        before = sum(len(o.get_object()._data) for o in objs.values())  # compressed bytes on disk
        merged, added, bbox, ng = build_union(datas)

        st = DecodedStreamObject()
        st.set_data(merged)
        st = st.flate_encode(level=9)
        st[NameObject("/Length1")] = NumberObject(len(merged))
        ref = writer._add_object(st)
        for fd, _ffref in items:
            fd[NameObject("/FontFile2")] = ref
            fd[NameObject("/FontBBox")] = ArrayObject([NumberObject(v) for v in bbox])
        report.append((base, len(objs), before, len(merged), added))

    buf = io.BytesIO()
    writer.write(buf)
    # second pass: clone from the root so the orphaned subset streams are dropped
    buf.seek(0)
    w2 = PdfWriter(clone_from=PdfReader(buf))
    with open(dst, "wb") as fh:
        w2.write(fh)

    print(f"{os.path.basename(src)}: {os.path.getsize(src):,} B -> {os.path.getsize(dst):,} B "
          f"({os.path.getsize(src)-os.path.getsize(dst):+,} B)")
    for base, n, before, after, added in report:
        if n < 2:
            print(f"    {base}: 1 copy, untouched")
        else:
            print(f"    {base}: {n} copies -> 1  (raw stream {before:,} B; merged program "
                  f"{after:,} B uncompressed, {added} glyphs folded in)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

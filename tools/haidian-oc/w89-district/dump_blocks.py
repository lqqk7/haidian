from pathlib import Path as _HaidianPath
import json,pickle,os
HERE=os.path.dirname(os.path.abspath(__file__))
PKG=str(_HaidianPath(__file__).resolve().parents[3] / 'submissions/lqqk7/every-sense-jingzhang')
faces=pickle.load(open(HERE+"/faces.pkl","rb"))
d=json.load(open(PKG+"/visual/assets/district-strategy.json"))
out={}
for dist in d["districts"]:
    for c in dist["opening_candidates"]:
        A=c["block_area_m2"]
        best=min(range(len(faces)), key=lambda i: abs(faces[i][0]-A))
        a,p,ce,ring,ins=faces[best]
        assert abs(a-A)<0.06 and abs(p-c["block_perimeter_m"])<0.06, (c["candidate_id"],a,p)
        assert abs(ce[0]-c["centroid_wgs84"][0])<1e-6 and abs(ce[1]-c["centroid_wgs84"][1])<1e-6
        out[c["candidate_id"]]=[[round(x,6),round(y,6)] for x,y in ring]
json.dump(out,open(HERE+"/cand_rings.json","w"))
print("ok",{k:len(v) for k,v in out.items()})

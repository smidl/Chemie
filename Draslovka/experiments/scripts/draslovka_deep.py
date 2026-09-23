"""#2 Feedstock-restricted deep run: force MULTI-step routes to Draslovka products
from a small bulk/platform feedstock (HCN, acetone, cyanide, urea, benzil, ...).
Arms: standard value net vs our L*. Captures full route + depth.
"""
import json, pickle, argparse
import numpy as np, torch, torch.nn as nn
from rdkit import Chem
from valueNet import ValueMLP
import Cluster_sampling as C

FEEDSTOCK = [
 "C#N","[C-]#N","CC(C)=O","C=O","NC=O","NC(N)=O","N","CO","CCO","CC(=O)O","OC=O",
 "O=Cc1ccccc1","O=C(C(=O)c1ccccc1)c1ccccc1","O=C(c1ccccc1)c1ccccc1","Nc1ccccc1",
 "c1ccccc1","Cc1ccccc1","OC(=O)CCl","NCCN","CN(C)C","ClCCCl","ClCCBr","C=C","O=C=O",
 "C=C(C)C(=O)O","NCC(=O)O","CC=O","CC#N","OCC#N","ClC(=O)C(=O)Cl","O","Cl","[OH-]",
 "CS(=O)(=O)O","O=S(=O)(O)O","CC(C)(O)C#N","ClCCl","BrCCBr","CC(=O)Cl","COC=O",
]

class ValueFeatureMLP2(nn.Module):
    def __init__(self, device, value_ckpt, feat_ckpt=None):
        super().__init__()
        feat_ckpt = feat_ckpt or value_ckpt
        def load(p):
            m = ValueMLP(n_layers=1, fp_dim=2048, latent_dim=128, dropout_rate=0.1, device=device).to(device)
            m.load_state_dict(torch.load(p, map_location=device)); m.eval(); return m
        vm = load(value_ckpt); fm = load(feat_ckpt)
        self.v_feature = nn.Sequential(*list(vm.children())[0][:2]); self.v_out = list(vm.children())[0][3]
        self.f_feature = nn.Sequential(*list(fm.children())[0][:2])
    def forward(self, fps):
        val = torch.log(1 + torch.exp(self.v_out(self.v_feature(fps))))
        return val, torch.sigmoid(self.f_feature(fps))

ap = argparse.ArgumentParser()
ap.add_argument("--arm", required=True); ap.add_argument("--ckpt", required=True)
ap.add_argument("--candidate_size", type=int, required=True)
ap.add_argument("--timeout", type=int, default=300); ap.add_argument("--out", required=True)
a = ap.parse_args()

np.random.seed(0); torch.manual_seed(0)
device = "cpu"
def canon(s):
    m = Chem.MolFromSmiles(s); return Chem.MolToSmiles(m) if m else None
known = set(c for c in (canon(s) for s in FEEDSTOCK) if c)
print("feedstock size:", len(known), flush=True)
one_step = C.prepare_expand(-1)
vmodel = ValueFeatureMLP2(device, a.ckpt)
targets = list(pickle.load(open("./test_dataset/draslovka.pkl", "rb")))

res = []
for smi in targets:
    known.discard(smi)
    ok, iters, expanded, route = False, 500, 0, []
    try:
        with C.time_limits(a.timeout):
            ag = C.SearchAgent(smi, known, vmodel, one_step, device, a.candidate_size, weight=0.15)
            out = ag.search()
            ok, iters, expanded = bool(out[0]), int(out[2]), int(out[3])
            if ok:
                rp, tp = ag.vis_synthetic_path(out[1]); route = [str(x) for x in rp]
    except C.TimeoutException:
        ok = False
    except Exception as e:
        ok = False; print("ERR", smi, str(e)[:120], flush=True)
    res.append({"smi": smi, "solved": ok, "iters": iters, "expanded": expanded,
                "depth": len(route), "route": route})
    print(("SOLVED" if ok else "fail"), "depth=%d exp=%d %s" % (len(route), expanded, smi), flush=True)

summ = {"arm": a.arm, "cs": a.candidate_size, "solved": sum(1 for r in res if r["solved"]), "n": len(res)}
json.dump({"summary": summ, "rows": res}, open(a.out, "w"), indent=2)
print("SUMMARY", json.dumps(summ), flush=True)

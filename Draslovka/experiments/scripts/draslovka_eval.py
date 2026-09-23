"""Draslovka demo: run our retro stack on their products.
Target is removed from purchasable stock so the planner must PROPOSE a route to it.
Arms: standard value net (best_epoch.pt) vs our L* (lstar_broad.pt). Captures the route.
"""
import json, pickle, argparse
import numpy as np, torch, torch.nn as nn
from valueNet import ValueMLP
import Cluster_sampling as C

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
        feat = torch.sigmoid(self.f_feature(fps))
        return val, feat

ap = argparse.ArgumentParser()
ap.add_argument("--dataset", default="draslovka")
ap.add_argument("--arm", required=True)
ap.add_argument("--ckpt", required=True)
ap.add_argument("--feat_ckpt", default="")
ap.add_argument("--candidate_size", type=int, required=True)
ap.add_argument("--weight", type=float, default=0.15)
ap.add_argument("--timeout", type=int, default=300)
ap.add_argument("--out", required=True)
a = ap.parse_args()

np.random.seed(0); torch.manual_seed(0)
device = "cpu"
known = C.prepare_starting_molecules()
one_step = C.prepare_expand(-1)
vmodel = ValueFeatureMLP2(device, a.ckpt, a.feat_ckpt or None)
targets = list(pickle.load(open("./test_dataset/" + a.dataset + ".pkl", "rb")))

res = []
for smi in targets:
    was_in = smi in known
    known.discard(smi)                       # force a disconnection to OTHER stock
    ok, iters, expanded, route = False, 500, 0, []
    try:
        with C.time_limits(a.timeout):
            ag = C.SearchAgent(smi, known, vmodel, one_step, device, a.candidate_size, weight=a.weight)
            out = ag.search()
            ok, iters, expanded = bool(out[0]), int(out[2]), int(out[3])
            if ok:
                rp, tp = ag.vis_synthetic_path(out[1])
                route = [str(x) for x in rp]
    except C.TimeoutException:
        ok = False
    except Exception as e:
        ok = False; print("ERR", smi, str(e)[:120], flush=True)
    finally:
        if was_in: known.add(smi)            # restore shared stock
    res.append({"smi": smi, "solved": ok, "iters": iters, "expanded": expanded,
                "route_len": len(route), "route": route})
    print(("SOLVED" if ok else "fail"), "steps=%d exp=%d %s" % (len(route), expanded, smi), flush=True)

summ = {"arm": a.arm, "ckpt": a.ckpt, "cs": a.candidate_size,
        "solved": sum(1 for r in res if r["solved"]), "n": len(res)}
json.dump({"summary": summ, "rows": res}, open(a.out, "w"))
print("SUMMARY", json.dumps(summ), flush=True)

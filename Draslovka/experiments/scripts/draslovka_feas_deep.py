"""Capstone: feasibility-audit EVERY step of the multi-step routes (does our
feasibility layer flag the chemically-unsound steps our planner produced?).
Needs only the routes JSON + ReactionT5 (no harness dependency).
"""
import json, argparse
import torch, torch.nn.functional as F
from rdkit import Chem, RDLogger
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
RDLogger.DisableLog('rdApp.*')

MN = "sagawa/ReactionT5v2-forward"
tok = AutoTokenizer.from_pretrained(MN)
model = AutoModelForSeq2SeqLM.from_pretrained(MN); model.eval()

NAMES = {
 "CC(C)(O)C#N": "acetone cyanohydrin", "C=C(C)C(=O)OC": "MMA",
 "O=C1NC(=O)C(c2ccccc2)(c2ccccc2)N1": "phenytoin", "CC1(C)NC(=O)NC1=O": "dimethylhydantoin",
 "O=C(O)CN(CCN(CC(=O)O)CC(=O)O)CC(=O)O": "EDTA", "C[N+](C)(C)CCCl": "chlormequat",
}

def canon(s):
    m = Chem.MolFromSmiles(s); return Chem.MolToSmiles(m) if m else None

def nll(reactants, product):
    inp = tok(reactants, return_tensors="pt", truncation=True, max_length=300)
    lab = tok(product, return_tensors="pt", truncation=True, max_length=200)
    with torch.no_grad():
        out = model(input_ids=inp.input_ids, labels=lab.input_ids)
        lp = F.log_softmax(out.logits, dim=-1)
        return F.nll_loss(lp.view(-1, lp.size(-1)), lab.input_ids.view(-1),
                          ignore_index=tok.pad_token_id).item()

def roundtrip(reactants, product_canon, k=5):
    inp = tok(reactants, return_tensors="pt", truncation=True, max_length=300)
    with torch.no_grad():
        out = model.generate(**inp, min_length=1, max_new_tokens=200, num_beams=10,
                             num_return_sequences=k, early_stopping=True)
    preds = [canon(p) for p in tok.batch_decode(out, skip_special_tokens=True)]
    preds = [p for p in preds if p]
    return (product_canon in preds), preds[:k]

ap = argparse.ArgumentParser()
ap.add_argument("--routes", required=True); ap.add_argument("--out", required=True)
a = ap.parse_args()
data = json.load(open(a.routes)); rows = data["rows"] if isinstance(data, dict) else data

report = []
for r in rows:
    if not r.get("route"): continue
    name = NAMES.get(r["smi"], r["smi"]); steps = []
    for i, step in enumerate(r["route"]):
        reactants, product = step.split(">>"); pc = canon(product)
        try:
            score = nll(reactants, product); match, preds = roundtrip(reactants, pc)
        except Exception as e:
            score = float("nan"); match = False; preds = []
        steps.append({"i": i, "step": step, "nll": round(score, 3), "pass": bool(match),
                      "top_pred": preds[0] if preds else None})
        print("  %-20s step%d %s NLL=%6.3f  %s" % (name, i, "PASS" if match else "FAIL", score, step[:80]), flush=True)
    npass = sum(1 for s in steps if s["pass"]); n = len(steps)
    verdict = "SOUND" if npass == n else "UNSOUND (%d/%d steps fail)" % (n - npass, n)
    report.append({"name": name, "depth": n, "steps_pass": npass, "verdict": verdict, "steps": steps})
    print(">>> %-20s depth=%d  %d/%d steps pass -> %s\n" % (name, n, npass, n, verdict), flush=True)
json.dump(report, open(a.out, "w"), indent=2)
print("DONE_FEASDEEP", flush=True)

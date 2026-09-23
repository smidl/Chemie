"""Feasibility scoring of the proposed 1-step disconnections via ReactionT5v2-forward.
For each step (reactants>>product): (a) NLL of the product given reactants (lower=more feasible),
(b) forward round-trip (does the forward model actually predict the target product?).
This is the 'decision layer' that separates real routes from hallucinations.
"""
import json, torch, torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from rdkit import Chem, RDLogger
RDLogger.DisableLog('rdApp.*')

MN = "sagawa/ReactionT5v2-forward"
tok = AutoTokenizer.from_pretrained(MN)
model = AutoModelForSeq2SeqLM.from_pretrained(MN)
model.eval()

NAMES = {
 "CC(C)(O)C#N": "acetone cyanohydrin", "C=C(C)C(=O)OC": "MMA",
 "O=C1NC(=O)C(c2ccccc2)(c2ccccc2)N1": "phenytoin", "CC1(C)NC(=O)NC1=O": "5,5-dimethylhydantoin",
 "O=C(O)CN(CCN(CC(=O)O)CC(=O)O)CC(=O)O": "EDTA", "C[N+](C)(C)CCCl": "chlormequat",
}

def canon(s):
    m = Chem.MolFromSmiles(s); return Chem.MolToSmiles(m) if m else None

def nll(reactants, product):
    inp = tok(reactants, return_tensors="pt")
    lab = tok(product, return_tensors="pt")
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

rows = json.load(open("draslovka_out/lstar_seea.json"))["rows"]
res = []
for r in rows:
    if not r["route"]:
        continue
    step = r["route"][0]
    reactants, product = step.split(">>")
    pc = canon(product)
    score = nll(reactants, product)
    match, preds = roundtrip(reactants, pc)
    res.append({"name": NAMES.get(r["smi"], r["smi"]), "smi": r["smi"], "step": step,
                "nll": round(score, 3), "roundtrip_pass": match, "top_pred": preds[0] if preds else None})
    print("%-22s NLL=%6.3f  round-trip=%s  top_pred=%s" %
          (NAMES.get(r["smi"], r["smi"]), score, "PASS" if match else "FAIL", preds[0] if preds else "-"), flush=True)

res.sort(key=lambda x: x["nll"])
print("\n=== RANKED BY FEASIBILITY (low NLL = feasible) ===", flush=True)
for x in res:
    print("%-22s NLL=%6.3f  round-trip=%s" % (x["name"], x["nll"], "PASS" if x["roundtrip_pass"] else "FAIL"), flush=True)
json.dump(res, open("draslovka_out/feasibility.json", "w"), indent=2)
print("\nWROTE draslovka_out/feasibility.json", flush=True)

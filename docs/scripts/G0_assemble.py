"""Assemble the six walkthrough reactions, and find out whether BH9 hands us the atom map.

The pipeline's input is (mapped reactant SMILES, mapped product SMILES). Atom mapping is the
unowned gap. But BH9 stores reactant, TS and product geometries for the same reaction, and IF the
atom ordering is consistent across them, the map is implicit in the index -- automatic AND
checkable by a chemist against the depictions, which is better than either hand-mapping or a mapper.

Test: for each of the six, is the concatenated element sequence of the reactant side identical to
that of the TS, and to that of the product side?
"""
import glob, json, os, sys
sys.path.insert(0, "/mnt/data/resynthesis/admissibility/scripts")
from E0_pick import parse_db

SI = "/mnt/data/resynthesis/admissibility/data/BH9_SI"
PICKED = ["407", "107", "93", "92", "95", "436"]
NAMES = {
    "407": "2-pyridone + water, water-assisted tautomerisation",
    "107": "1-methylcyclopropene + methyl azide, [3+2]",
    "93":  "thiophene-1,1-dioxide + ethylene, Diels-Alder",
    "92":  "thiophene S-oxide + 2,3-dihydrofuran, Diels-Alder",
    "95":  "3,6-dimethyltetrazine + benzyne, inverse-electron-demand DA",
    "436": "CO2 + thiazolium enol, nucleophilic addition",
}


def seq(blocks, sign):
    out = []
    for b in blocks:
        if (b["coef"] > 0) == (sign > 0):
            out += [a[0] for a in b["atoms"]]
    return out


out = {}
for n in PICKED:
    fwd = f"{SI}/DB_files/BH/BH9-BH_{n}_forward.db"
    rev = f"{SI}/DB_files/BH/BH9-BH_{n}_reverse.db"
    re_ = f"{SI}/DB_files/RE/BH9-RE_{n}.db"
    d_f = parse_db(fwd)
    d_r = parse_db(rev) if os.path.exists(rev) else None
    d_e = parse_db(re_) if os.path.exists(re_) else None

    ts_seq = seq(d_f["blocks"], +1)
    rx_seq = seq(d_f["blocks"], -1)
    # the reverse file's negative side is the PRODUCT side
    pr_seq = seq(d_r["blocks"], -1) if d_r else None

    print(f"\n=== #{n}  {NAMES[n]}")
    print(f"  forward ref {d_f['ref']:>7.2f} kcal/mol   reverse ref "
          f"{d_r['ref'] if d_r else float('nan'):>7.2f}   RE {d_e['ref'] if d_e else float('nan'):>7.2f}")
    nrx = len([b for b in d_f['blocks'] if b['coef'] < 0])
    npr = len([b for b in d_r['blocks'] if b['coef'] < 0]) if d_r else None
    print(f"  reactant fragments {nrx}   product fragments {npr}   TS atoms {len(ts_seq)}")
    print(f"  element sequence  reactants==TS: {rx_seq == ts_seq}"
          f"   products==TS: {pr_seq == ts_seq if pr_seq else 'n/a'}")
    if rx_seq != ts_seq:
        from collections import Counter
        print(f"    reactant formula {dict(Counter(rx_seq))}")
        print(f"    TS       formula {dict(Counter(ts_seq))}")
        print(f"    same multiset: {sorted(rx_seq) == sorted(ts_seq)}  <- if True, only ORDER differs")
    out[n] = dict(name=NAMES[n], fwd_ref=d_f["ref"],
                  rev_ref=d_r["ref"] if d_r else None, re=d_e["ref"] if d_e else None,
                  n_reactant_frags=nrx, n_product_frags=npr, n_atoms=len(ts_seq),
                  order_matches_ts=dict(reactants=rx_seq == ts_seq,
                                        products=(pr_seq == ts_seq) if pr_seq else None))

json.dump(out, open("/mnt/data/resynthesis/admissibility/out/walkthrough_six.json", "w"), indent=1)
print("\nwrote out/walkthrough_six.json")

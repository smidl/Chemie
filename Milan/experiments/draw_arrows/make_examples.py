#!/usr/bin/env python
"""Pick a few held-out RMechDB steps and draw, side by side, the chemist's
route, the released model's sampled chain and the fine-tuned model's chain.

Inputs are the fine-tune test split (reactant in the model's convention), the
manifest (to find the chemist's arrows), and the instrumented roll-out logs of
the two models on that split. Output: one SVG per panel and an index.html.

    ../human_plausibility/.venv/bin/python make_examples.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cairosvg

HERE = Path(__file__).resolve().parent
HP = HERE.parent / "human_plausibility"
FT = HERE.parent / "finetune" / "data" / "rmechdb_ft"
sys.path.insert(0, str(HP))
from score_reactions import complete_atom_map, to_model_moves  # noqa: E402
from draw_moves import ChainDrawer, KIND_NAMES  # noqa: E402

OUT = HERE / "out"
KIND_INDEX = {k: i for i, k in enumerate(KIND_NAMES)}


def main():
    OUT.mkdir(exist_ok=True)
    lines = [l.strip().split("|")[0].split(">>") for l in open(FT / "test.txt") if ">>" in l]
    manifest = json.load(open(FT / "manifest.json"))["splits"]["test"]["lines"]
    sources = {s: json.load(open(HP / s)) for s in ("targets.json", "multistep.json")}
    logs = {name: {json.loads(l)["index"]: json.loads(l) for l in open(HP / "results" / f"instrumented_test_{name}.jsonl")}
            for name in ("released", "ft_mixed")}

    # one small example per class, preferring short reactants
    wanted = ["abstraction", "addition", "retroaddition", "homolyze"]
    chosen = {}
    for row in sorted(manifest, key=lambda r: logs["released"][r["seq"]]["n_atoms"]):
        cls = row["meta"][2]
        if cls in wanted and cls not in chosen and row["n_moves"] >= (2 if cls != "homolyze" else 1):
            chosen[cls] = row
    html = ["<html><head><meta charset='utf-8'><style>body{font-family:Helvetica;margin:24px} h2{margin-top:36px} .row{display:flex;gap:8px;align-items:flex-start;flex-wrap:wrap} .lab{width:130px;font-size:13px;color:#444;padding-top:8px} img,svg{border:1px solid #ddd}</style></head><body>",
            "<h1>Chemist's route vs the model's chain, held-out RMechDB steps</h1>",
            "<p>Orange: two-electron arrow (pair move). Magenta half-head: one-electron fish-hook (homolysis, colligation). Dashed: bond about to form. Atoms keep their positions across panels; only hydrogens a move touches are drawn.</p>"]
    for cls, row in chosen.items():
        seq = row["seq"]
        reactant = lines[seq][0]
        entry = sources[row["source"]][row["index"]]
        _, o2n = complete_atom_map(entry["reactant"])
        chemist = [tuple(m) for m in to_model_moves(entry["moves"], o2n)[0].tolist()]
        html.append(f"<h2>{cls} — {entry['reactant']}</h2><p style='font-size:12px;color:#666'>RMechDB: {' ; '.join(' '.join(map(str, m)) for m in entry['moves'])}</p>")
        for label, moves, stopped in (
            ("chemist's route", chemist, True),
            ("released model", [(KIND_INDEX[s["move"]], s["i"], s["j"]) for s in logs["released"][seq]["chains"][0]["steps"] if s["move"] != "STOP"], logs["released"][seq]["chains"][0]["stopped"]),
            ("fine-tuned model", [(KIND_INDEX[s["move"]], s["i"], s["j"]) for s in logs["ft_mixed"][seq]["chains"][0]["steps"] if s["move"] != "STOP"], logs["ft_mixed"][seq]["chains"][0]["stopped"]),
        ):
            drawer = ChainDrawer(reactant, moves)
            panels = drawer.panels(stopped=stopped)
            if len(panels) > 6:  # a wandering chain: first five states and the end
                panels = panels[:5] + [panels[-1]]
            html.append(f"<div class='row'><div class='lab'>{label}<br><span style='color:#999'>{len(moves)} moves</span></div>")
            for k, svg in enumerate(panels):
                name = f"{cls}_{label.split()[0].strip(chr(39))}_{k}"
                (OUT / f"{name}.svg").write_text(svg)
                cairosvg.svg2png(bytestring=svg.encode(), write_to=str(OUT / f"{name}.png"), output_width=680)
                html.append(f"<img src='{name}.png' width='340'>")
            html.append("</div>")
    (OUT / "index.html").write_text("\n".join(html) + "</body></html>")
    print(f"wrote {OUT/'index.html'} with {len(chosen)} examples: {list(chosen)}")


if __name__ == "__main__":
    main()

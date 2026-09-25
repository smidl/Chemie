#!/usr/bin/env python
"""Draw the disputed long steps: the recorded mechanism against the one the
model scores higher, as a chemist would draw them.

Input is `analysis/results/strata_dispute_afm.json` from
`experiments/stratified/strata_dispute.py` -- the steps where AFM's
highest-scoring trajectory ends somewhere other than the recorded product,
small enough to draw legibly. Reactants are FlowER's own, already fully mapped
with every hydrogen explicit, so no preprocessing is needed.

    ../human_plausibility/.venv/bin/python draw_disputes.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent.parent / "analysis" / "results" / "strata_dispute_afm.json"
sys.path.insert(0, str(HERE))
from draw_moves import KIND_NAMES, ChainDrawer  # noqa: E402

OUT = HERE / "out_disputes"
KIND_INDEX = {k: i for i, k in enumerate(KIND_NAMES)}


def main():
    OUT.mkdir(exist_ok=True)
    data = json.load(open(RESULTS))
    cases = sorted(data["disputed"], key=lambda c: (c["stratum"], c["n_atoms"]))
    html = ["<title>Disputed Mechanisms</title>",
            "<link rel='stylesheet' href='https://fonts.googleapis.com/css2?family=IBM+Plex+Serif:wght@500&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono&display=swap'>",
            """<style>
:root{--bg:#F6F7F5;--ink:#23282D;--muted:#6B7378;--rule:#D5D9D6;--paper:#fff;--edge:#CBD0CC;--pair:#d9541e;--hook:#b5338f}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#15181B;--ink:#E6E8E6;--muted:#98A0A6;--rule:#2C3237;--edge:#3A4147}}
:root[data-theme="dark"]{--bg:#15181B;--ink:#E6E8E6;--muted:#98A0A6;--rule:#2C3237;--edge:#3A4147}
body{background:var(--bg);color:var(--ink);font-family:"IBM Plex Sans",system-ui,sans-serif;font-size:15px;margin:0;padding:36px 28px 64px}
main{max-width:1180px;margin:0 auto}
h1{font-family:"IBM Plex Serif",Georgia,serif;font-weight:500;font-size:28px;margin:0 0 8px}
h2{font-family:"IBM Plex Serif",Georgia,serif;font-weight:500;font-size:19px;margin:0 0 4px}
.lede{max-width:70ch;color:var(--muted);margin:0 0 20px}
section{padding:26px 0 6px;border-bottom:1px solid var(--rule)}
.meta{font-size:12.5px;color:var(--muted);margin:0 0 14px;line-height:1.7}
.meta code{font-family:"IBM Plex Mono",monospace;font-size:12px;color:var(--ink)}
.row{display:grid;grid-template-columns:170px 1fr;gap:14px;align-items:start;padding:8px 0}
.lab{padding-top:10px;font-weight:600;font-size:14px}
.lab small{display:block;font-weight:400;color:var(--muted);font-variant-numeric:tabular-nums}
.panels{display:flex;gap:10px;overflow-x:auto;padding-bottom:6px}
figure{margin:0;flex:0 0 auto;background:var(--paper);border:1px solid var(--edge);border-radius:3px}
figure svg{width:300px;height:auto;display:block}
</style>""",
            "<main><h1>Disputed mechanisms</h1>",
            "<p class='lede'>Held-out FlowER steps where the model's highest-scoring trajectory ends on a different product from the record. Orange: two-electron arrow. Magenta half-head: one-electron fish-hook. Dashed: bond about to form. Higher log-probability is the model's own preference.</p>"]
    for k, c in enumerate(cases):
        rec = [(KIND_INDEX[m[0]], m[1], m[2]) for m in c["recorded_moves"]]
        pref = [(KIND_INDEX[m[0]], m[1], m[2]) for m in c["preferred_moves"]]
        html.append(f"<section><h2>{c['stratum'].replace('test_','')} &middot; {c['n_atoms']} atoms</h2>"
                    f"<p class='meta'><code>{c['reactant'][:150]}</code><br>"
                    f"recorded route log-probability <b>{c['logp_recorded']}</b> &middot; "
                    f"model's preferred <b>{c['logp_preferred']}</b> &middot; "
                    f"recorded product reached somewhere in the beam: {c['reached_recorded_in_beam']}</p>")
        for label, moves in (("recorded", rec), ("model prefers", pref)):
            try:
                panels = ChainDrawer(c["reactant"], moves).panels(stopped=True)
            except Exception as exc:  # noqa: BLE001
                html.append(f"<div class='row'><div class='lab'>{label}</div><div>drawing failed: {exc}</div></div>")
                continue
            html.append(f"<div class='row'><div class='lab'>{label}<small>{len(moves)} moves</small></div><div class='panels'>")
            for p, svg in enumerate(panels):
                (OUT / f"case{k}_{label.split()[0]}_{p}.svg").write_text(svg)
                html.append(f"<figure>{svg}</figure>")
            html.append("</div></div>")
        html.append("</section>")
    html.append("</main>")
    (OUT / "disputes.html").write_text("\n".join(html))
    print("wrote", OUT / "disputes.html", "with", len(cases), "cases")


if __name__ == "__main__":
    main()

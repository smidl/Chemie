#!/usr/bin/env python
"""Assemble the rendered panels into one page with the drawings inline.

    ../human_plausibility/.venv/bin/python make_page.py   (after make_examples.py)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HP = HERE.parent / "human_plausibility"
FT = HERE.parent / "finetune" / "data" / "rmechdb_ft"
OUT = HERE / "out"
sys.path.insert(0, str(HP))

ROWS = [("chemist's", "chemist's route"), ("released", "released model"), ("fine-tuned", "fine-tuned model")]
CLASS_TITLE = {"abstraction": "Hydrogen abstraction", "addition": "Radical addition",
               "retroaddition": "Retro-addition (β-scission)", "homolyze": "Homolysis (initiation)"}


def panels_for(cls, label):
    files = sorted(OUT.glob(f"{cls}_{label}_*.svg"), key=lambda p: int(p.stem.rsplit("_", 1)[1]))
    out = []
    for f in files:
        svg = f.read_text()
        svg = re.sub(r"<\?xml[^>]*\?>", "", svg)
        svg = re.sub(r"<rect style='opacity:1.0;fill:#FFFFFF[^>]*>", "", svg, count=1)  # let the panel paint its own paper
        out.append(svg)
    return out


def main():
    lines = [l.strip().split("|")[0].split(">>") for l in open(FT / "test.txt") if ">>" in l]
    manifest = {r["seq"]: r for r in json.load(open(FT / "manifest.json"))["splits"]["test"]["lines"]}
    sources = {s: json.load(open(HP / s)) for s in ("targets.json", "multistep.json")}
    order = ["abstraction", "addition", "retroaddition", "homolyze"]
    # recover which test line each class example came from (same selection rule as make_examples.py)
    logs = {json.loads(l)["index"]: json.loads(l) for l in open(HP / "results" / "instrumented_test_released.jsonl")}
    chosen = {}
    for seq, row in sorted(manifest.items(), key=lambda kv: logs[kv[0]]["n_atoms"]):
        cls = row["meta"][2]
        if cls in order and cls not in chosen and row["n_moves"] >= (2 if cls != "homolyze" else 1):
            chosen[cls] = row

    sections = []
    for cls in order:
        row = chosen[cls]
        entry = sources[row["source"]][row["index"]]
        arrows = " ; ".join(" ".join(map(str, m)) for m in entry["moves"])
        rows_html = []
        for key, label in ROWS:
            panels = panels_for(cls, key)
            n_moves = len(panels) - 1
            rows_html.append(f"""
      <div class="row">
        <div class="rowlabel"><span>{label}</span><small>{n_moves} move{'s' if n_moves != 1 else ''}</small></div>
        <div class="panels">{''.join(f'<figure class="panel">{s}</figure>' for s in panels)}</div>
      </div>""")
        sections.append(f"""
  <section>
    <h2>{CLASS_TITLE[cls]}</h2>
    <p class="meta"><span class="k">reactant</span> <code>{entry['reactant']}</code><br>
       <span class="k">chemist's arrows</span> <code>{arrows}</code> <span class="k">· {row['meta'][1].lower()}, {row['meta'][0].lower()}</span></p>
    {''.join(rows_html)}
  </section>""")

    page = f"""<title>Arrows on Held-out Steps</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Serif:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400&display=swap">
<style>
:root {{ --bg:#F6F7F5; --ink:#23282D; --muted:#6B7378; --rule:#D5D9D6; --paper:#FFFFFF; --paper-edge:#CBD0CC; --pair:#d9541e; --hook:#b5338f; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#15181B; --ink:#E6E8E6; --muted:#98A0A6; --rule:#2C3237; --paper:#FFFFFF; --paper-edge:#3A4147; }} }}
:root[data-theme="dark"] {{ --bg:#15181B; --ink:#E6E8E6; --muted:#98A0A6; --rule:#2C3237; --paper:#FFFFFF; --paper-edge:#3A4147; }}
body {{ background:var(--bg); color:var(--ink); font-family:"IBM Plex Sans",system-ui,sans-serif; font-size:15px; line-height:1.5; margin:0; padding:40px 32px 64px; }}
main {{ max-width:1180px; margin:0 auto; }}
h1 {{ font-family:"IBM Plex Serif",Georgia,serif; font-weight:500; font-size:30px; letter-spacing:-0.01em; margin:0 0 8px; text-wrap:balance; }}
h2 {{ font-family:"IBM Plex Serif",Georgia,serif; font-weight:500; font-size:22px; margin:0 0 6px; }}
.lede {{ max-width:68ch; color:var(--muted); margin:0 0 18px; }}
.legend {{ display:flex; gap:28px; flex-wrap:wrap; font-size:13px; color:var(--muted); padding:12px 0 28px; border-bottom:1px solid var(--rule); }}
.legend svg {{ vertical-align:middle; margin-right:6px; }}
section {{ padding:32px 0 8px; border-bottom:1px solid var(--rule); }}
.meta {{ margin:0 0 18px; font-size:13px; color:var(--muted); line-height:1.7; }}
.meta code {{ font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:12.5px; color:var(--ink); }}
.k {{ text-transform:uppercase; letter-spacing:0.08em; font-size:11px; }}
.row {{ display:grid; grid-template-columns:150px 1fr; gap:14px; align-items:start; padding:10px 0; }}
.rowlabel {{ display:flex; flex-direction:column; gap:2px; padding-top:10px; font-weight:600; font-size:14px; }}
.rowlabel small {{ font-weight:400; color:var(--muted); font-size:12px; font-variant-numeric:tabular-nums; }}
.panels {{ display:flex; gap:12px; overflow-x:auto; padding-bottom:6px; }}
.panel {{ margin:0; flex:0 0 auto; width:300px; background:var(--paper); border:1px solid var(--paper-edge); border-radius:3px; }}
.panel svg {{ width:300px; height:auto; display:block; }}
@media (max-width:640px) {{ .row {{ grid-template-columns:1fr; }} body {{ padding:24px 14px; }} }}
</style>
<main>
  <h1>Arrows on held-out steps</h1>
  <p class="lede">Four RMechDB steps the fine-tuned model never saw. Each row is one move sequence read as a chemist would draw it: the state, with the next move's arrows on it, then the next state. Atoms keep their positions from panel to panel; only hydrogens a move touches are drawn.</p>
  <div class="legend">
    <span><svg width="46" height="14"><path d="M2 11 Q 22 -6 40 8" fill="none" stroke="var(--pair)" stroke-width="2.4"/><polygon points="43,8 35,4 36,11" fill="var(--pair)"/></svg>two-electron arrow (pair move)</span>
    <span><svg width="46" height="14"><path d="M2 11 Q 22 -6 40 8" fill="none" stroke="var(--hook)" stroke-width="2.4"/><polygon points="43,8 35,3 38,8" fill="var(--hook)"/></svg>one-electron fish-hook (homolysis, colligation)</span>
    <span><svg width="46" height="14"><line x1="2" y1="7" x2="44" y2="7" stroke="#999" stroke-dasharray="3,3"/></svg>bond about to form</span>
    <span>· unpaired electron</span>
  </div>
  {''.join(sections)}
</main>
"""
    (OUT / "arrows.html").write_text(page)
    print("wrote", OUT / "arrows.html")


if __name__ == "__main__":
    main()

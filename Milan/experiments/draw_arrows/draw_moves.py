#!/usr/bin/env python
"""Draw a move sequence the way a chemist draws a mechanism: each state as a
2D structure, with the *next* move's arrows on it -- one two-electron curly
arrow for a pair move, two half-headed fish-hooks for a homolysis or a
colligation -- and the final state last.

Arrows come straight from the alphabet's expansion into RMechDB's arrow
notation (analysis/rmechdb_arrows.py::moves_to_arrows):

    LONE_TO_BOND(i->j)    atom i  ==> bond (i,j)
    BOND_TO_LONE(i,j->j)  bond (i,j) ==> atom j
    HOMOLYSIS(i,j)        bond (i,j) -> i ; bond (i,j) -> j
    COLLIGATION(i,j)      i -> bond (i,j) ; j -> bond (i,j)

Atoms keep their 2D positions across panels (coordinates are computed once on
the reactant and reused), so the eye follows electrons, not a re-layout.
Hydrogens are drawn only where a move touches them; the rest stay implicit.
States that are not molecules (book-keeping intermediates) are drawn from the
matrix without sanitisation and labelled as such.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import torch
from rdkit import Chem, RDLogger
from rdkit.Chem import rdDepictor
from rdkit.Chem.Draw import rdMolDraw2D

HERE = Path(__file__).resolve().parent
HP = HERE.parent / "human_plausibility"
sys.path.insert(0, str(HP))
from fully_explicit_stability import build_batch  # noqa: E402
from score_reactions import AFM_REPO  # noqa: E402

sys.path.insert(0, str(AFM_REPO))
RDLogger.DisableLog("rdApp.*")
import chem  # noqa: E402
from models.afm import scatter_moves  # noqa: E402

KIND_NAMES = ["LONE_TO_BOND", "BOND_TO_LONE", "HOMOLYSIS", "COLLIGATION"]
PAIR_COLOUR = "#d9541e"   # two-electron arrow
HOOK_COLOUR = "#b5338f"   # one-electron fish-hook
W, H = 340, 260


def arrows_for_move(kind: int, i: int, j: int):
    """(electrons, source slot, sink slot); a slot is an atom index or a bond (i, j)."""
    bond = (i, j)
    if kind == 0:
        return [(2, i, bond)]
    if kind == 1:
        return [(2, bond, j)]
    if kind == 2:
        return [(1, bond, i), (1, bond, j)]
    return [(1, i, bond), (1, j, bond)]


def move_label(kind, i, j, symbols):
    si, sj = f"{symbols[i]}{i + 1}", f"{symbols[j]}{j + 1}"
    return {0: f"lone pair on {si} -> bond {si}-{sj}", 1: f"bond {si}-{sj} -> lone pair on {sj}",
            2: f"homolysis of {si}-{sj}", 3: f"colligation of {si} and {sj}"}[kind]


class ChainDrawer:
    def __init__(self, mapped_reactant: str, moves):
        batch, _ = build_batch(mapped_reactant)
        self.mol = batch["reactant_mols"][0]
        self.src = batch["src"].long()
        self.size = int(batch["lengths"][0])
        self.symbols = [None] * self.size
        for a in self.mol.GetAtoms():
            self.symbols[a.GetIntProp("molAtomMapNumber") - 1] = a.GetSymbol()
        self.moves = [tuple(int(v) for v in m) for m in moves]
        # hydrogens touched by any move stay explicit in every panel
        touched = {i for _, i, j in self.moves for i in (i, j)}
        self.keep_h = {k for k in touched if self.symbols[k] == "H"}
        self.coords = None

    # -- state -> drawable mol -------------------------------------------------
    def state_mol(self, matrix):
        smiles = chem.product_mapped_smiles_from_be(self.mol, matrix)
        molecule = bool(smiles)
        if not molecule:  # book-keeping state: build the graph directly from the matrix
            rw = Chem.RWMol()
            for k in range(self.size):
                a = Chem.Atom(self.symbols[k]); a.SetAtomMapNum(k + 1); a.SetNoImplicit(True); rw.AddAtom(a)
            for a in range(self.size):
                for b in range(a + 1, self.size):
                    o = int(matrix[a, b])
                    if o:
                        rw.AddBond(a, b, {1: Chem.BondType.SINGLE, 2: Chem.BondType.DOUBLE, 3: Chem.BondType.TRIPLE}[min(o, 3)])
            m = rw.GetMol()
            m.UpdatePropertyCache(strict=False)
        else:
            m = Chem.MolFromSmiles(smiles, sanitize=False)
            try:
                Chem.SanitizeMol(m)
            except Exception:  # noqa: BLE001
                m.UpdatePropertyCache(strict=False)
        # drop hydrogens no move touches; map numbers identify atoms across panels
        for a in m.GetAtoms():
            if a.GetSymbol() == "H" and (a.GetAtomMapNum() - 1) not in self.keep_h:
                a.SetAtomMapNum(0)
        ps = Chem.RemoveHsParameters()
        ps.removeMapped = False
        ps.removeDegreeZero = False
        try:
            m = Chem.RemoveHs(m, ps, sanitize=False)
        except Exception:  # noqa: BLE001
            pass
        m.UpdatePropertyCache(strict=False)
        return m, molecule

    def _layout(self, m):
        """Coordinates by map number; computed on the first (reactant) panel, reused after."""
        if self.coords is None:
            rdDepictor.Compute2DCoords(m)
            conf = m.GetConformer()
            self.coords = {a.GetAtomMapNum(): conf.GetAtomPosition(a.GetIdx()) for a in m.GetAtoms() if a.GetAtomMapNum()}
        conf = Chem.Conformer(m.GetNumAtoms())
        missing = [a for a in m.GetAtoms() if a.GetAtomMapNum() not in self.coords]
        if missing:  # a hydrogen newly detached, etc.: place next to its neighbour
            for a in missing:
                nb = [n for n in a.GetNeighbors() if n.GetAtomMapNum() in self.coords]
                p = self.coords[nb[0].GetAtomMapNum()] if nb else list(self.coords.values())[0]
                self.coords[a.GetAtomMapNum()] = type(p)(p.x + 0.9, p.y + 0.9, 0.0)
        for a in m.GetAtoms():
            conf.SetAtomPosition(a.GetIdx(), self.coords[a.GetAtomMapNum()])
        m.RemoveAllConformers()
        m.AddConformer(conf, assignId=True)

    # -- one panel -------------------------------------------------------------
    def panel(self, matrix, move=None, title=""):
        m, molecule = self.state_mol(matrix)
        self._layout(m)
        idx_by_map = {a.GetAtomMapNum(): a.GetIdx() for a in m.GetAtoms()}
        for a in m.GetAtoms():
            a.SetAtomMapNum(0)
        d = rdMolDraw2D.MolDraw2DSVG(W, H)
        opts = d.drawOptions()
        opts.padding = 0.18
        opts.bondLineWidth = 2.0
        opts.fixedBondLength = 55
        opts.minFontSize = 14
        try:
            rdMolDraw2D.PrepareMolForDrawing(m, kekulize=molecule)
        except Exception:  # noqa: BLE001
            pass
        d.DrawMolecule(m)
        d.FinishDrawing()
        svg = d.GetDrawingText()
        pos = {k: d.GetDrawCoords(idx) for k, idx in idx_by_map.items()}
        centroid = np.mean([[p.x, p.y] for p in pos.values()], axis=0)

        def slot_xy(slot):
            if isinstance(slot, tuple):
                a, b = pos[slot[0] + 1], pos[slot[1] + 1]
                return np.array([(a.x + b.x) / 2, (a.y + b.y) / 2])
            p = pos[slot + 1]
            return np.array([p.x, p.y])

        extra = []
        if move is not None:
            kind, i, j = move
            if not int(matrix[i, j]) and kind in (0, 3):  # bond being formed: show where it will be
                a, b = pos[i + 1], pos[j + 1]
                extra.append(f'<line x1="{a.x:.1f}" y1="{a.y:.1f}" x2="{b.x:.1f}" y2="{b.y:.1f}" stroke="#999" stroke-width="1" stroke-dasharray="3,3"/>')
            for electrons, src, dst in arrows_for_move(kind, i, j):
                extra.append(self._arrow(slot_xy(src), slot_xy(dst), centroid, electrons))
        label = title + ("" if molecule else " (not a molecule)")
        extra.append(f'<text x="8" y="{H - 8}" font-family="Helvetica" font-size="11" fill="#333">{label}</text>')
        return svg.replace("</svg>", "\n".join(extra) + "\n</svg>")

    @staticmethod
    def _arrow(p, q, centroid, electrons):
        v = q - p
        dist = np.linalg.norm(v) + 1e-9
        u = v / dist
        n = np.array([-u[1], u[0]])
        mid = (p + q) / 2
        if np.dot(mid - centroid, n) < 0:  # bulge away from the molecule
            n = -n
        # a bond midpoint and its own atom are ~25 px apart, so the arc must
        # bulge well clear of the bond to be readable
        bulge = max(0.55 * dist, 26)
        c = mid + n * bulge
        # start and end just off the slots, on the bulge side
        p2 = p + u * 5 + n * 6
        q2 = q - u * 5 + n * 6
        # tangent at the end of the quadratic curve
        t = q2 - c
        t = t / (np.linalg.norm(t) + 1e-9)
        tn = np.array([-t[1], t[0]])
        colour = PAIR_COLOUR if electrons == 2 else HOOK_COLOUR
        head = 9
        tip = q2
        base = tip - t * head
        left = base + tn * head * 0.55
        right = base - tn * head * 0.55
        if electrons == 2:
            head_svg = f'<polygon points="{tip[0]:.1f},{tip[1]:.1f} {left[0]:.1f},{left[1]:.1f} {right[0]:.1f},{right[1]:.1f}" fill="{colour}"/>'
        else:  # fish-hook: one barb only
            barb = left if np.dot(tn, n) > 0 else right
            head_svg = f'<polygon points="{tip[0]:.1f},{tip[1]:.1f} {barb[0]:.1f},{barb[1]:.1f} {base[0]:.1f},{base[1]:.1f}" fill="{colour}"/>'
        path = f'<path d="M {p2[0]:.1f} {p2[1]:.1f} Q {c[0]:.1f} {c[1]:.1f} {q2[0]:.1f} {q2[1]:.1f}" fill="none" stroke="{colour}" stroke-width="2.4" stroke-linecap="round"/>'
        return path + head_svg

    # -- whole chain -----------------------------------------------------------
    def panels(self, stopped=True):
        state = self.src.clone()
        out = []
        for k, (kind, i, j) in enumerate(self.moves):
            mat = state[0, :self.size, :self.size].numpy()
            out.append(self.panel(mat, (kind, i, j), f"state {k}: {move_label(kind, i, j, self.symbols)}"))
            scatter_moves(state, torch.tensor([kind]), torch.tensor([i]), torch.tensor([j]), torch.ones(1, dtype=torch.bool))
        mat = state[0, :self.size, :self.size].numpy()
        out.append(self.panel(mat, None, f"state {len(self.moves)}: " + ("Stop" if stopped else "budget exhausted, emits reactant")))
        return out

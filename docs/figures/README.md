# Figure assets — matplotlib styles and colour references

Vendored 2026-09-03 from [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates)
(MIT), path `cli-tool/components/skills/scientific/scientific-visualization/`.
Files are upstream **verbatim** except for the two `_` → `-` renames noted
below; this README is the only local addition.

| File | Upstream name | What it is |
|---|---|---|
| `publication.mplstyle` | same | 3.5 in single-column, 8 pt Arial, Okabe-Ito cycle, 300 dpi PDF |
| `nature.mplstyle` | same | Nature portfolio: 89 mm column, 7 pt, 600 dpi PDF |
| `presentation.mplstyle` | same | Posters/slides: 8×6 in, 14 pt, 2.5 pt lines, 300 dpi PNG |
| `color_palettes.py` | same | Okabe-Ito / Wong / Paul Tol palettes + `apply_palette()` |
| `journal-requirements.md` | `references/journal_requirements.md` | Per-publisher figure specs (Nature, Science, Cell, PLOS, ACS, Elsevier, IEEE, BMC) |
| `color-palettes.md` | `references/color_palettes.md` | Colour-choice guidance behind the palettes |

Nothing here touches the network, needs an API key, or calls another skill.
Pure `.mplstyle` + stdlib/matplotlib Python.

Verified 2026-09-03 against matplotlib 3.10: all three styles parse, render,
and save to PDF with no warnings; `apply_palette()` and `get_palette()` work.

## Use

```python
import matplotlib.pyplot as plt
plt.style.use('docs/figures/publication.mplstyle')   # or nature / presentation
```

Or from anywhere, by absolute path:

```python
from pathlib import Path
plt.style.use(Path.home() / 'AIC/Chemie/docs/figures/nature.mplstyle')
```

To install them as named styles (`plt.style.use('nature')`), symlink into
`matplotlib.get_configdir()/stylelib/`.

Palettes without the style file:

```python
import sys; sys.path.insert(0, 'docs/figures')
from color_palettes import apply_palette, OKABE_ITO_LIST
apply_palette('okabe_ito')
```

## Caveats

- The styles assume **Arial/Helvetica**, falling back to DejaVu Sans. Both
  Arial and Helvetica are present on this machine, so the fallback does not
  kick in here; re-check on the cluster or any other box.
- `savefig.format` is set (`pdf` for publication/nature, `png` for
  presentation). An explicit extension in `savefig()` overrides it.
- `color_palettes.py` lists `'RdGn'` in `DIVERGING_COLORMAPS_AVOID`; no such
  matplotlib colormap exists (the real red-green ones are `RdYlGn` and
  `RdGy`). Left verbatim — it is in an avoid-list, so it is inert.
- Journal specs go stale. Treat `journal-requirements.md` as a first pass and
  confirm against the venue's current author guidelines before submission.

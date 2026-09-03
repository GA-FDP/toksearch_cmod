# toksearch_cmod

Alcator C-Mod support for the Fusion Data Platform.

Today this package exists to contribute the **`cmod` device catalog** to the
`fdp_schema.catalogs` entry-point group. C-Mod data is read with the
device-neutral `toksearch.MdsSignal`, so no C-Mod-specific signal classes are
needed yet.

## Usage

```bash
fdp -D cmod run python my_script.py
```

```python
from toksearch import Pipeline, MdsSignal

pipe = Pipeline([1160930043])
pipe.fetch("btor",   MdsSignal(r"\magnetics::btor", "magnetics"))
pipe.fetch("cpasma", MdsSignal(r"\analysis::efit_aeqdsk:cpasma", "analysis"))
pipe.keep(["btor", "cpasma"])
recs = pipe.compute_serial()
```

Note C-Mod has no `\ip` tag — plasma current is `\analysis::efit_aeqdsk:cpasma`
(amps, signed negative).

## Data layout

Tree files live on the `fdp-cmod` Pelican origin at

```
cmod_archive/YY/MM/DD/<tree>/<tree>_<shot>.{tree,characteristics,datafile}
```

where a C-Mod shot is `[1]YYMMDDNNN` (10 digits post-2000, 9 in the 1990s).
See `toksearch_cmod/data/cmod.yaml` for how that maps onto the MDSplus
tilde-substitution search path.

## Status

Catalog only. Release plumbing used by the other FDP repos — versioneer,
`recipe/`, and the `conda_build.yaml` workflow — is **not** set up here yet, so
this is not yet publishable to the `ga-fdp` channel.

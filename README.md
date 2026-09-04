# toksearch_cmod

Alcator C-Mod support for the Fusion Data Platform.

This package provides two things:

1. The **`cmod` device catalog**, contributed to the `fdp_schema.catalogs`
   entry-point group. C-Mod data is read with the device-neutral
   `toksearch.MdsSignal`, so no C-Mod-specific signal classes are needed.
2. **MIT PSFC's custom TDI functions and FORTRAN libraries**, without which a
   large set of C-Mod nodes cannot be evaluated at all. See `src/README.md`.

## Usage

```bash
fdp -D cmod run python my_script.py
```

```python
from toksearch import Pipeline, MdsSignal

pipe = Pipeline([1160930043])
pipe.fetch("ip",     MdsSignal(r"\IP", "cmod"))
pipe.fetch("btor",   MdsSignal(r"\magnetics::btor", "magnetics"))
pipe.keep(["ip", "btor"])
recs = pipe.compute_serial()
```

## Why the native half matters

C-Mod tree nodes are frequently *expressions* that call custom code at
evaluation time. Because FDP evaluates them at the remote site rather than at
PSFC, that code has to ship with the client.

The failure mode is not degraded data, it is no data: a missing library raises
`LibKEYNOTFOU` and a missing TDI function raises `TdiUNKNOWN_VAR`. The plasma
current is the headline case — `\IP` routes through `libHYBEXE.so` and is
unreadable without it.

Installation is deliberately configuration-free. The TDI functions go to
`$PREFIX/tdi`, which is exactly what `fdp` sets `MDS_PATH` to, and the shared
libraries go to `$PREFIX/lib`, where MDSplus's bare `dlopen("libHYBEXE.so")`
finds them via `libMdsShr`'s `RPATH $ORIGIN`. No environment variables, and no
changes to `fdp`. `tests/test_native.py` guards that layout.

Because of the compiled half, this package is **linux-64 only**. That costs
nothing in practice: every compiled member of the FDP stack is linux-64
already, and `ga-fdp` publishes no osx or win subdir.

## Data layout

Tree files live on the `fdp-cmod` Pelican origin at

```
cmod_archive/YY/MM/DD/<tree>/<tree>_<shot>.{tree,characteristics,datafile}
```

where a C-Mod shot is `[1]YYMMDDNNN` (10 digits post-2000, 9 in the 1990s).
See `toksearch_cmod/data/cmod.yaml` for how that maps onto the MDSplus
tilde-substitution search path.

Note that the origin is still being populated; shots outside the staged range
fail with `TreeFOPENR` on every subtree.

## Development

```bash
pixi run build-libs         # build + install the TDI functions and .so files
pixi run test               # network-free suite
pixi run test-integration   # live origin; needs BEARER_TOKEN for fdp-cmod
```

The integration suite reproduces MIT's published reference values for shot
1160930043 exactly — all 22 of them, which is what establishes that the port
off their Ubuntu 24.04 / gfortran 13 build is faithful.

## Attribution

Everything under `src/` is MIT PSFC's work (Mark Winkel; the FORTRAN dates to
2002–2011, attributed to `smw`), redistributed under the MIT license — see
`src/LICENSE.mit`. The rest of this repository is Apache-2.0.

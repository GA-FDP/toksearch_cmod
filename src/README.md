# Custom C-Mod TDI functions and FORTRAN libraries

Third-party source, vendored. **Provenance:** MIT PSFC's `fdp-cmod` repo
(`github.mit.edu:mwinkel/fdp-cmod`, commit `aa424c8`), by Mark Winkel, with
the FORTRAN itself dating to 2002–2011 and attributed to `smw`. Redistributed
under the MIT license — see `LICENSE.mit`. The rest of `toksearch_cmod` is
Apache-2.0.

## Why this exists

C-Mod tree nodes are not plain stored arrays; many are expressions that call
out to custom TDI functions and FORTRAN libraries at evaluation time. FDP
distributes clones of PSFC's C-Mod archive to remote sites, and evaluation
happens *at the remote site* — so the custom code has to travel with the data.

Without it the affected nodes are not slow or degraded, they are unreadable:
missing libraries raise `LibKEYNOTFOU` and missing TDI functions raise
`TdiUNKNOWN_VAR`. That includes the plasma current, `\IP`
(`MHD.MAGNETICS.PROCESSED.CURRENT_DATA.IP`), which routes through HYBEXE.

## How the contents were identified

Not by reading the trees. MIT instrumented MDSplus to log every library and
TDI function call, walked *every node* of one shot per operating year (26
shots, 1991–2016), and diffed the result against a stock MDSplus
distribution. The survey ran on an air-gapped VM, because some C-Mod nodes
shell out and could in principle write to the archive.

The five TDI functions below are a small subset of the 182 files in PSFC's
`/usr/local/cmod/tdi`; the rest appear to be for running shots and post-shot
analysis.

## Contents

| Path | Role |
|---|---|
| `tdi/dpcs_concatenate.fun` | Splices an array of signals into one, wavegen-style |
| `tdi/probe_control.fun`, `tdi/probe_control2.fun` | Scanning-probe control decoding |
| `tdi/transpose_matrix.fun` | 2-D transpose via index mapping |
| `tdi/load_spect_rois.py` | Builds spectroscopy ROI arrays |
| `imsl/` | A PSFC-written stand-in for the commercial IMSL library (matrix/FFT helpers) |
| `hybexe/` | `get_input_p_to_v` — magnetics pressure-to-voltage calibration; backs `\IP` |

`libMMUL.so` is a symlink to `libIMSL.so`; C-Mod expressions reference MMUL
more often than IMSL.

## Building

`make` (see `../src/Makefile`). Requires gfortran and an MDSplus prefix with
`include/mdslib.inc` and `lib/libMdsLib.so`:

```bash
make install PREFIX=$CONDA_PREFIX MDSPLUS_DIR=$CONDA_PREFIX
# or, from the repo root:
pixi run build-libs
```

The Makefile is a rewrite of the two upstream per-library Makefiles, which
hardcoded the author's Ubuntu 24.04 / gfortran 13 paths. Three portability
fixes are documented in its header comment.

Install layout is load-bearing, not arbitrary: `.fun`/`.py` go to
`$PREFIX/tdi` because that is exactly what `fdp` sets `MDS_PATH` to, and the
`.so` files go to `$PREFIX/lib` because that is where MDSplus's bare
`dlopen("libHYBEXE.so")` lands (via `libMdsShr`'s `RPATH $ORIGIN`). Together
that means no environment variables and no changes to `fdp`.
`tests/test_native.py` asserts it.

## Caveats carried over from upstream

- **Linux only.** Porting the FORTRAN to macOS/Windows is impractical, and a
  rewrite in another language would not give bit-identical numerics. MIT
  expects the libraries may become unnecessary in the future.
- **Some 1990s nodes cannot be evaluated at all.** They call VAX/VMS-era
  libraries (`LIBRTL`, `PLASMA`) that no longer exist anywhere, including on
  PSFC's own archive server. Likewise the `SURFACE` library, whose source was
  never found — expressions referencing it happen to abort earlier for other
  reasons.
- **Do not evaluate nodes containing `Build_Action()`, `Build_Conglom()`, or
  `SPAWN()`.** These relate to running shots and controlling digitizers, not
  analysis. The `DNB::*CREATE_SHOT*` nodes (2007 and later) try to execute
  `/usr/local/cmod/codes/dnb/create_shot.sh`.
- The survey covered 26 shots, so this is representative of the ~50,000-shot
  archive but not exhaustive; more custom software may surface once the full
  ~170 TB origin is in production.

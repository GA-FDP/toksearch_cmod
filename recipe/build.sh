#!/bin/bash
# Build script for the toksearch_cmod conda package.
#
# Two halves:
#   1. the Python package (catalog YAML + entry point), via pip
#   2. the native half -- MIT PSFC's custom TDI functions and the two FORTRAN
#      libraries that MDSplus dlopen()s while evaluating C-Mod expressions
set -euo pipefail

# --- 1. Python package ------------------------------------------------
${PYTHON} -m pip install . --no-deps --no-build-isolation --ignore-installed -vv

# --- 2. TDI functions + FORTRAN libraries -----------------------------
# The Makefile puts .fun/.py in $PREFIX/tdi and the .so files in $PREFIX/lib.
# Both are load-bearing locations, not arbitrary choices:
#   * $PREFIX/tdi is literally what fdp sets MDS_PATH to (it hardcodes
#     env_dir/"tdi"), so the TDI functions are found with no configuration.
#   * $PREFIX/lib is where MDSplus's bare dlopen("libHYBEXE.so") lands, via
#     libMdsShr's RPATH $ORIGIN.
# See tests/test_native.py, which asserts this layout.
#
# CONDA_BUILD_SYSROOT carries the old-glibc sysroot that keeps the artifact
# from being over-constrained to the build machine's glibc (the bug that left
# ga-dfl-labeler pinned to __glibc <2.35). conda-forge's compiler activation
# usually injects it already; pass it explicitly so we don't depend on that.
EXTRA=""
if [ -n "${CONDA_BUILD_SYSROOT:-}" ]; then
    EXTRA="--sysroot=${CONDA_BUILD_SYSROOT}"
fi

make -C src install \
    PREFIX="${PREFIX}" \
    MDSPLUS_DIR="${PREFIX}" \
    EXTRA_FFLAGS="${EXTRA}" \
    EXTRA_LDFLAGS="${EXTRA}"

# Fail loudly here rather than at import time if the UPPERCASE aliases that
# the tree expressions call did not make it into .dynsym. They come from
# `ld --defsym`, which silently produces a working-looking library if the
# flag is dropped, so this is worth checking at build time.
for sym in MURRV MRRRR MUZRV MRRZZ; do
    nm -D --defined-only "${PREFIX}/lib/libIMSL.so" | grep -qE " ${sym}\$" \
        || { echo "ERROR: libIMSL.so is missing entry point ${sym}" >&2; exit 1; }
done
nm -D --defined-only "${PREFIX}/lib/libHYBEXE.so" | grep -qE " GET_INPUT_P_TO_V\$" \
    || { echo "ERROR: libHYBEXE.so is missing entry point GET_INPUT_P_TO_V" >&2; exit 1; }

echo "Native C-Mod support installed:"
ls -l "${PREFIX}/lib/libIMSL.so" "${PREFIX}/lib/libMMUL.so" "${PREFIX}/lib/libHYBEXE.so"
ls -l "${PREFIX}/tdi/"*.fun "${PREFIX}/tdi/load_spect_rois.py"

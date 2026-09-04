"""Guards on the native half of the package: MIT PSFC's custom TDI functions
and the two FORTRAN libraries MDSplus dlopen()s to evaluate C-Mod expressions.

These assert against the *installed* environment rather than the source tree,
because that is what actually has to be right -- and because the conda test
phase copies only tests/, so the source tree isn't there to look at.

Everything here is network-free. The tests that read real C-Mod data and
reproduce MIT's reference values live in test_integration.py.
"""

import ctypes
import os
import sys
from pathlib import Path

import pytest

# sys.prefix, not $PREFIX. rattler-build leaks its own PREFIX into the test
# subprocess (the same trap that forced get_default_xrd_pluginconfdir() to
# prefer CONDA_PREFIX), so the interpreter's own idea of its prefix is the
# only reliable answer in both a conda test and a pixi dev env.
PREFIX = Path(sys.prefix)
LIB_DIR = PREFIX / "lib"
TDI_DIR = PREFIX / "tdi"

# The five custom TDI functions identified by instrumenting MDSplus across 26
# C-Mod shots, one per operating year (see src/README.md).
TDI_FILES = [
    "dpcs_concatenate.fun",
    "probe_control.fun",
    "probe_control2.fun",
    "transpose_matrix.fun",
    "load_spect_rois.py",
]

# The UPPERCASE names C-Mod tree expressions invoke via IMAGE->ROUTINE.
# gfortran emits lowercase-with-underscore, so these exist only because of
# `ld --defsym` aliases. A dropped flag would still produce a library that
# loads, and would fail much later with LibKEYNOTFOU, so pin them here.
IMSL_ENTRY_POINTS = ["MURRV", "MRRRR", "MUZRV", "MRRZZ"]
HYBEXE_ENTRY_POINTS = ["GET_INPUT_P_TO_V"]


@pytest.mark.parametrize("name", TDI_FILES)
def test_tdi_function_installed(name):
    """Each custom TDI function lands in $PREFIX/tdi."""
    assert (TDI_DIR / name).is_file(), f"{name} missing from {TDI_DIR}"


def test_tdi_dir_is_what_fdp_puts_on_mds_path():
    """$PREFIX/tdi is not an arbitrary location -- it is where fdp points
    MDS_PATH, so installing there is what makes the functions resolvable
    with no configuration. If fdp ever stops hardcoding env_dir/"tdi",
    this test is the thing that notices."""
    from fdp.catalog import catalog
    from fdp.environment import build_device_config

    mds_path = build_device_config(catalog["cmod"])["MDS_PATH"]

    entries = [Path(p) for p in mds_path.split(";") if p]
    assert TDI_DIR in entries, (
        f"MDS_PATH={mds_path!r} does not include {TDI_DIR}, so the custom "
        "C-Mod TDI functions installed there would not be found"
    )


@pytest.mark.parametrize(
    "libname,entry_points",
    [("libIMSL.so", IMSL_ENTRY_POINTS), ("libHYBEXE.so", HYBEXE_ENTRY_POINTS)],
)
def test_library_loads_and_exports_entry_points(libname, entry_points):
    """The libraries load, and expose the uppercase aliases by which C-Mod
    tree expressions call them."""
    path = LIB_DIR / libname
    assert path.is_file(), f"{libname} missing from {LIB_DIR}"

    lib = ctypes.CDLL(str(path))
    for sym in entry_points:
        assert getattr(lib, sym, None) is not None, (
            f"{libname} does not export {sym}; the `ld --defsym` alias was "
            "probably dropped from the link"
        )


def test_mmul_is_an_alias_for_imsl():
    """C-Mod expressions reference MMUL more often than IMSL, but there is
    only one library. Upstream ships MMUL as a soft link."""
    mmul = LIB_DIR / "libMMUL.so"
    assert mmul.is_symlink(), f"{mmul} should be a symlink to libIMSL.so"
    assert os.readlink(mmul) == "libIMSL.so"


def test_hybexe_can_find_libmdslib_without_ld_library_path():
    """libHYBEXE.so has a DT_NEEDED on libMdsLib.so. MDSplus dlopen()s it
    from arbitrary processes, so it must resolve that on its own rather than
    relying on the caller having libMdsLib already loaded or on
    LD_LIBRARY_PATH being set -- hence -rpath $ORIGIN in src/Makefile."""
    env = dict(os.environ)
    env.pop("LD_LIBRARY_PATH", None)

    import subprocess

    code = (
        "import ctypes, sys, pathlib;"
        f"ctypes.CDLL(str(pathlib.Path(sys.prefix) / 'lib' / 'libHYBEXE.so'));"
        "print('ok')"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], env=env, capture_output=True, text=True
    )
    assert result.returncode == 0, (
        "libHYBEXE.so failed to load without LD_LIBRARY_PATH: " + result.stderr
    )

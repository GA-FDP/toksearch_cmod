"""Live-origin tests: read real C-Mod data over Pelican and check the values
against MIT PSFC's reference output.

These are marked `integration` and excluded from the conda test phase -- they
need a BEARER_TOKEN for the fdp-cmod namespace and the FDP environment
(run them under `fdp -D cmod run`, not bare pytest).

    fdp -D cmod run python -m pytest tests/ -m integration -v

The expected values are the ones published in the READMEs of MIT's fdp-cmod
repo, produced on Ubuntu 24.04 / gfortran 13 against a local copy of the C-Mod
archive. Reproducing them here -- on a different OS, a different gfortran, a
patched MDSplus, and over Pelican rather than local disk -- is what tells us
the port is faithful, so they are pinned exactly rather than approximately.

Every node below is unreadable without this package's native half: the
libraries fail with LibKEYNOTFOU and the TDI functions with TdiUNKNOWN_VAR.
"""

import os

import numpy as np
import pytest

pytestmark = pytest.mark.integration

mds = pytest.importorskip("MDSplus")

# The "trophy shot" MIT used for its reference values: the largest production
# shot of 2016, C-Mod's final operating year.
TROPHY_SHOT = 1160930043

# Mark Winkel's published baseline. mean values are exact repr()s.
TDI_CASES = [
    ("load_spect_rois.py", "SPECTROSCOPY.CHROMEX2.SETUP:ROI_CALCED", 96, 269.3229166666667),
    ("dpcs_concatenate.fun", "HYBRID.DPCS.LOADABLES.WAVE_SYNC.P:POUT_01", 15, -5.865228176116943),
    ("probe_control.fun", "EDGE.OMEGATRON.PROBES.G_1.P0:BYTE_OUT", 1, 87.0),
    ("probe_control2.fun", "EDGE.PROBES.ABLIM.RFA.P0:BYTE_OUT", 1, 35.0),
    ("transpose_matrix.fun", "MHD.XTOMO.BRIGHTNESSES.ARRAY_1:CHORD_ANGLES", 38, 2.3458559048556844),
]

# Nodes routed through libIMSL.so / libMMUL.so.
IMSL_CASES = [
    ("ENGINEERING.POWER_SYSTEM.CORRECT_COIL:BMN", -1.2339813892925378e-10 + 4.874565195933656e-10j),
    ("MHD.ANALYSIS:RECON_VAC:BP_CURRENT", -512568.25),
    ("MHD.ANALYSIS.NON_AXISYM:BMN_APPLIED:BMN_FFT", -2.5001371639632453e-08 + 9.876164597244497e-08j),
    ("MHD.ANALYSIS.NON_AXISYM:BMN_APPLIED:BMN_JACOBIAN", -5.628500332477415e-08 + 2.215767409552427e-07j),
    ("MHD.ANALYSIS.NON_AXISYM:BMN_OH1WIND:BMN_FFT", -1.026594873110298e-06 + 7.615551744777349e-09j),
    ("MHD.ANALYSIS.NON_AXISYM:BMN_OH1WIND:BMN_JACOBIAN", -2.3205241177493008e-06 + 1.7550819464418055e-08j),
    ("MHD.ANALYSIS.NON_AXISYM:BMN_OH2LWIND:BMN_FFT", -1.753210017341189e-05 - 2.2854296233276727e-08j),
    ("MHD.ANALYSIS.NON_AXISYM:BMN_OH2LWIND:BMN_JACOBIAN", -3.9929203921929e-05 - 5.2485940926771946e-08j),
    ("MHD.ANALYSIS.NON_AXISYM:BMN_OH2UWIND:BMN_FFT", 2.2579299184144475e-05 + 1.8251567368565702e-08j),
    ("MHD.ANALYSIS.NON_AXISYM:BMN_OH2UWIND:BMN_JACOBIAN", 5.137104380992241e-05 + 4.2364007413198124e-08j),
    ("MHD.ANALYSIS.NON_AXISYM:BMN_TFBUS:BMN_FFT", -7.823136002116371e-06 - 1.5530200471403077e-05j),
    ("MHD.ANALYSIS.NON_AXISYM:BMN_TFBUS:BMN_JACOBIAN", -1.7759199181455187e-05 - 3.526316140778363e-05j),
    ("MHD.ANALYSIS.NON_AXISYM:BMN_TLT_SHFT:BMN_FFT", 4.7633332656005223e-07 + 4.91718594730628e-07j),
    ("MHD.ANALYSIS.NON_AXISYM:BMN_TLT_SHFT:BMN_JACOBIAN", 1.0945027497655246e-06 + 1.1643659263427253e-06j),
    ("MHD.ANALYSIS.NON_AXISYM.MODEL:A_COIL_COEFS:FFT_COEFS", -1.2339813892925378e-10 + 4.874565195933656e-10j),
    ("MHD.ANALYSIS.NON_AXISYM.MODEL:A_COIL_COEFS:JACOB_COEFS", -2.778026975125414e-10 + 1.0936334060573927e-09j),
]

# Plasma current. The headline case: \IP is simply not readable without HYBEXE.
HYBEXE_NODE = "MHD.MAGNETICS.PROCESSED.CURRENT_DATA.IP"
HYBEXE_NSAMP = 14336
HYBEXE_MEAN = -499357.34375


@pytest.fixture(scope="module")
def cmod_tree():
    if not os.getenv("BEARER_TOKEN"):
        pytest.skip("BEARER_TOKEN not set; needs credentials for the fdp-cmod namespace")
    try:
        return mds.Tree("cmod", TROPHY_SHOT)
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"cannot open C-Mod tree over Pelican: {exc}")


def _mean(tree, node):
    return np.mean(tree.getNode(node).record.data())


@pytest.mark.parametrize("func,node,count,expected", TDI_CASES, ids=[c[0] for c in TDI_CASES])
def test_custom_tdi_functions(cmod_tree, func, node, count, expected):
    """The five custom TDI functions evaluate, and agree with MIT's values."""
    data = cmod_tree.getNode(node).record.data()
    assert data.size == count
    assert np.mean(data) == expected


@pytest.mark.parametrize("node,expected", IMSL_CASES, ids=[c[0] for c in IMSL_CASES])
def test_imsl_backed_nodes(cmod_tree, node, expected):
    """Nodes whose expressions call into libIMSL.so / libMMUL.so."""
    assert _mean(cmod_tree, node) == expected


def test_plasma_current_via_hybexe(cmod_tree):
    """\\IP -- the reason libHYBEXE.so has to ship at all."""
    data = cmod_tree.getNode(HYBEXE_NODE).record.data()
    assert len(data) == HYBEXE_NSAMP
    assert np.mean(data) == HYBEXE_MEAN

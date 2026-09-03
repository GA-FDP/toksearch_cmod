# Copyright 2024 General Atomics
# Licensed under the Apache License, Version 2.0.

"""Catalog + env-wiring guards for the cmod device.

All network-free. These run against the *installed* package (the recipe
invokes them as `cd tests && pytest -q`), so resolving cmod.yaml through
importlib.resources also proves the YAML was actually packaged as
package-data rather than merely sitting in the source tree.
"""

import pytest

from fdp_schema import load_tokamak
from toksearch_cmod.data import cmod_yaml

# The exact search-path entry verified against live data on the fdp-cmod
# origin. Kept as a literal so a well-meaning edit to the tilde string has
# to come through this test.
EXPECTED_SEARCH_PATH = (
    "pelican://osg-htc.org:443/fdp-cmod/cmod_archive/~i~h/~g~f/~e~d/~t"
)


@pytest.fixture(scope="module")
def tokamak():
    return load_tokamak(cmod_yaml)


def test_yaml_is_packaged_and_validates(tokamak):
    assert tokamak.name == "cmod"
    assert tokamak.schema_version == 1


def test_single_mds_tree_locator_with_expected_search_path(tokamak):
    mds = [l for l in tokamak.locators if l.kind == "mds_tree"]
    assert len(mds) == 1
    assert mds[0].transport == "pelican"
    assert mds[0].search_path == [EXPECTED_SEARCH_PATH]


def test_search_path_agrees_with_pelican_root(tokamak):
    """pelican_root and the search path must not drift apart."""
    assert tokamak.pelican_root is not None
    for loc in tokamak.locators:
        for entry in getattr(loc, "search_path", []):
            assert entry.startswith(tokamak.pelican_root)


def test_bearer_token_auth_declared(tokamak):
    mds = [l for l in tokamak.locators if l.kind == "mds_tree"][0]
    assert mds.auth is not None
    assert mds.auth.kind == "bearer_token"
    assert mds.auth.env == "BEARER_TOKEN"


def test_no_origin_server():
    """Regression guard, not an oversight.

    The cmod origin (fdp-cmod-origin.nationalresearchplatform.org) serves
    HTTP on :8083 only -- unlike the d3d origin it has no XRootD listener on
    :8443. Data access is unaffected because xrdcl-pelican reads over HTTP
    through the OSDF caches, but there is no `root://` endpoint for `fdp ls`.
    Leaving origin_server unset is what makes fdp's `origin` capability skip
    this device instead of hanging on a closed port. If someone copies d3d's
    origin_server in here, `fdp ls -D cmod` starts hanging -- so fail loudly.
    """
    assert load_tokamak(cmod_yaml).origin_server is None


# --- MDSplus tilde substitution -------------------------------------------
#
# Specification test for the search path. MaskReplace() in MDSplus
# treeshr/TreeOpen.c pads the shot with "%012u" and maps ~a -> index 11 (the
# ones digit) through ~j -> index 2; ~t is the tree name. C-Mod shots are
# [1]YYMMDDNNN, so the archive's YY/MM/DD components land on indices
# [3][4], [5][6], [7][8] -- i.e. ~i~h / ~g~f / ~e~d.
#
# The expected paths below are directories observed on the live origin.

def _mask_replace(pattern: str, tree: str, shot: int) -> str:
    mask = "%012u" % shot
    out = pattern
    for i, letter in enumerate("abcdefghij"):
        out = out.replace("~" + letter, mask[11 - i])
    return out.replace("~t", tree)


@pytest.mark.parametrize(
    "shot, tree, expected_dir",
    [
        # 2016-09-30, shot 043 -- 10-digit (post-2000) form
        (1160930043, "magnetics", "cmod_archive/16/09/30/magnetics"),
        # 1999-02-25, shot 022 -- 9-digit (1990s) form
        (990225022, "analysis", "cmod_archive/99/02/25/analysis"),
    ],
)
def test_tilde_path_expands_to_real_archive_dir(shot, tree, expected_dir):
    resolved = _mask_replace(EXPECTED_SEARCH_PATH, tree, shot)
    assert resolved.endswith(expected_dir), resolved
    assert "~" not in resolved, f"unsubstituted token left in {resolved}"


# --- fdp integration ------------------------------------------------------

def test_entry_point_is_registered():
    from importlib.metadata import entry_points
    eps = {ep.name: ep.value for ep in entry_points(group="fdp_schema.catalogs")}
    assert eps.get("cmod") == "toksearch_cmod.data:cmod_yaml"


def test_device_visible_in_fdp_catalog():
    from fdp.catalog import catalog
    assert "cmod" in catalog.names()


def test_env_wiring():
    """The composed env must carry the tree path and nothing d3d-specific."""
    from fdp.catalog import catalog
    from fdp.environment import build_device_config

    cfg = build_device_config(catalog["cmod"])
    assert cfg["default_tree_path"] == EXPECTED_SEARCH_PATH
    assert "MDS_PATH" in cfg
    assert cfg.get("XRD_PELICANUSEAUTHHEADERS") == "true"
    # Locator-gated: cmod has no ptdata_indexed or sql locator, so none of
    # these may be emitted.
    for leaked in ("PTDATA_LOC", "PTDATA_JSON_INDEX_DIR", "TDSVER", "D3DATA"):
        assert leaked not in cfg, f"{leaked} leaked into the cmod env"


def test_capabilities():
    """cmod offers bearer auth but must not claim an origin."""
    from fdp.catalog import catalog
    from fdp.devices import CAPABILITIES

    handle = catalog["cmod"]
    assert CAPABILITIES["bearer"][0](handle) is True
    assert bool(CAPABILITIES["origin"][0](handle)) is False

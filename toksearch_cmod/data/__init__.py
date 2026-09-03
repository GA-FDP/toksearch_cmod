# Copyright 2024 General Atomics
# Licensed under the Apache License, Version 2.0.

"""Catalog data shipped by toksearch_cmod.

Exposes a Traversable for cmod.yaml so the fdp_schema.catalogs entry-point
group can load it without importing fdp_schema or pydantic.
"""

from importlib.resources import files

cmod_yaml = files(__package__) / "cmod.yaml"

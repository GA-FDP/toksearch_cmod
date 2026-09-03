# Copyright 2024 General Atomics
# Licensed under the Apache License, Version 2.0.

"""TokSearch C-Mod: Alcator C-Mod data access for the Fusion Data Platform.

At present this package exists to contribute the `cmod` device catalog
(see `toksearch_cmod.data.cmod_yaml`) to the `fdp_schema.catalogs`
entry-point group. C-Mod data is read with the device-neutral
`toksearch.MdsSignal`; no C-Mod-specific signal classes are needed yet.
"""

from . import _version

__version__ = _version.get_versions()["version"]

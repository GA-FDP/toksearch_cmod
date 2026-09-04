"""Marker registration lives here, not only in pyproject.toml.

The conda test phase copies just `tests/` into the test environment, so
pyproject.toml's [tool.pytest.ini_options] is not present there and the
`integration` marker would raise PytestUnknownMarkWarning on every run.
Registering it in a conftest inside tests/ covers both contexts.
"""


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "integration: reads real C-Mod data over Pelican; needs BEARER_TOKEN "
        "and the fdp environment",
    )

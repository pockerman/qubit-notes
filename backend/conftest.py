"""Top-level pytest hooks: the --platform option and the step libraries the scenarios share.

``--platform=fake`` (the default) runs every scenario against ``FakePlatform``. ``--platform=gogi`` runs only the
scenarios tagged ``@gogi``, against the gogi gateway at ``STUDY_ASSISTANT_GATEWAY_URL``.
"""

import pytest

pytest_plugins = ["tests.bdd.steps.common_steps", "tests.bdd.steps.health_steps"]


def pytest_addoption(parser):
    parser.addoption("--platform", choices=["fake", "gogi"], default="fake", help="what the scenarios run against")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--platform") != "gogi":
        return
    skip = pytest.mark.skip(reason="not tagged @gogi")
    for item in items:
        if "gogi" not in item.keywords:
            item.add_marker(skip)

"""Top-level pytest hooks: the --platform option and the step libraries the scenarios share.

``--platform=fake`` (the default) runs every scenario against ``FakePlatform``. ``--platform=gogi`` runs only the
scenarios tagged ``@gogi``, against the gogi gateway at ``STUDY_ASSISTANT_GATEWAY_URL``.
"""

import pytest

pytest_plugins = [
    "tests.bdd.steps.common_steps",
    "tests.bdd.steps.reading_steps",
    "tests.bdd.steps.health_steps",
    "tests.bdd.steps.materials_steps",
    "tests.bdd.steps.sharing_steps",
    "tests.bdd.steps.ui_steps",
]


def pytest_addoption(parser):
    parser.addoption("--platform", choices=["fake", "gogi"], default="fake", help="what the scenarios run against")


def pytest_collection_modifyitems(config, items):
    # @wip scenarios are written and reviewed, but not built yet
    wip = pytest.mark.skip(reason="work in progress (@wip)")
    not_gogi = pytest.mark.skip(reason="not tagged @gogi")
    for item in items:
        if "wip" in item.keywords:
            item.add_marker(wip)
        elif config.getoption("--platform") == "gogi" and "gogi" not in item.keywords:
            item.add_marker(not_gogi)

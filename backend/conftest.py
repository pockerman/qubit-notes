"""Top-level pytest hooks: the --platform option and the step libraries the scenarios share.

``--platform=fake`` (the default) runs every scenario against ``FakePlatform``. ``--platform=gogi`` runs only the
scenarios tagged ``@gogi``, against the gogi gateway at ``STUDY_ASSISTANT_GATEWAY_URL``.
"""

import pytest

pytest_plugins = [
    "tests.bdd.steps.common_steps",
    "tests.bdd.steps.reading_steps",
    "tests.bdd.steps.notes_steps",
    "tests.bdd.steps.study_steps",
    "tests.bdd.steps.assistant_steps",
    "tests.bdd.steps.courses_steps",
    "tests.bdd.steps.editing_steps",
    "tests.bdd.steps.health_steps",
    "tests.bdd.steps.materials_steps",
    "tests.bdd.steps.writing_steps",
    "tests.bdd.steps.images_steps",
    "tests.bdd.steps.sharing_steps",
    "tests.bdd.steps.ui_steps",
]


def pytest_addoption(parser):
    parser.addoption("--platform", choices=["fake", "gogi"], default="fake", help="what the scenarios run against")
    parser.addoption(
        "--with-ai",
        action="store_true",
        help="on gogi, also run the @ai scenarios, which need a model provider's API key in gogi",
    )


def pytest_collection_modifyitems(config, items):
    # @wip scenarios are written and reviewed, but not built yet
    wip = pytest.mark.skip(reason="work in progress (@wip)")
    not_gogi = pytest.mark.skip(reason="not tagged @gogi")
    no_ai = pytest.mark.skip(reason="needs the AI: run with --with-ai once gogi has a model provider's API key")
    on_gogi = config.getoption("--platform") == "gogi"
    for item in items:
        if "wip" in item.keywords:
            item.add_marker(wip)
        elif on_gogi and "gogi" not in item.keywords:
            item.add_marker(not_gogi)
        elif on_gogi and "ai" in item.keywords and not config.getoption("--with-ai"):
            item.add_marker(no_ai)

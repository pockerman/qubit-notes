"""Top-level pytest hooks: the --platform option and the step libraries the scenarios share.

``--platform=fake`` (the default) runs every scenario but the @standalone ones against ``FakePlatform``.
``--platform=standalone`` runs the scenarios tagged ``@platform`` or ``@standalone`` against the app's own platform,
with a stand-in for the AI unless ``--with-ai`` is given. ``--platform=gogi`` runs only the scenarios tagged
``@platform``, against the gogi gateway at ``QUBIT_NOTES_GATEWAY_URL``.
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
    "tests.bdd.steps.application_steps",
    "tests.bdd.steps.sign_in_steps",
    "tests.bdd.steps.materials_steps",
    "tests.bdd.steps.writing_steps",
    "tests.bdd.steps.images_steps",
    "tests.bdd.steps.sharing_steps",
    "tests.bdd.steps.standalone_steps",
    "tests.bdd.steps.converting_steps",
    "tests.bdd.steps.references_steps",
    "tests.bdd.steps.reading_order_steps",
    "tests.bdd.steps.generating_steps",
    "tests.bdd.steps.ui_steps",
]


def pytest_addoption(parser):
    parser.addoption(
        "--platform", choices=["fake", "standalone", "gogi"], default="fake", help="what the scenarios run against"
    )
    parser.addoption(
        "--with-ai",
        action="store_true",
        help="also run the @ai scenarios with the real AI: on gogi, gogi needs a model provider's API key; on the "
        "app's own platform, QUBIT_NOTES_ANTHROPIC_API_KEY",
    )
    parser.addoption(
        "--with-embedding-keys",
        action="store_true",
        help="on the app's own platform, also run the @embedding_keys scenarios, which embed with Voyage AI and "
        "OpenAI: QUBIT_NOTES_VOYAGE_API_KEY and QUBIT_NOTES_OPENAI_API_KEY",
    )


def pytest_collection_modifyitems(config, items):
    def skip(reason: str):
        return pytest.mark.skip(reason=reason)

    platform = config.getoption("--platform")
    for item in items:
        keywords = item.keywords
        if "wip" in keywords:
            # @wip scenarios are written and reviewed, but not built yet
            item.add_marker(skip("work in progress (@wip)"))
        elif platform != "gogi" and ("gogi_keys" in keywords or "gogi_wrong_key" in keywords):
            item.add_marker(skip("runs only on gogi (--platform=gogi): gogi's application keys"))
        elif platform != "standalone" and "standalone" in keywords:
            item.add_marker(skip("runs only on the app's own platform (--platform=standalone)"))
        elif platform != "fake" and "platform" not in keywords and "standalone" not in keywords:
            item.add_marker(skip("not tagged @platform"))
        elif platform == "gogi" and "ai" in keywords and not config.getoption("--with-ai"):
            item.add_marker(skip("needs the AI: run with --with-ai once gogi has a model provider's API key"))
        elif "embedding_keys" in keywords and not config.getoption("--with-embedding-keys"):
            item.add_marker(skip("embeds with Voyage AI and OpenAI: run with --with-embedding-keys"))

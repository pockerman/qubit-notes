"""``qubit-notes``: what is done for a deployment, e.g. bringing the app's database up to date.

    qubit-notes migrate
    qubit-notes reembed
    echo "$ANTHROPIC_API_KEY" | qubit-notes store-provider-key anthropic

``migrate`` brings the app's database up to date, as the app does when it starts; a deployment runs it first, so a
new version's migrations run once, before it serves. ``reembed`` embeds the material again with the app's embedding
model (QUBIT_NOTES_EMBEDDING_MODEL), after it was changed: material is found only by searching with the model it was
embedded with. ``store-provider-key`` is for where the platform is gogi, which keeps the app's keys: the app's
summaries, quizzes and answers are then written with its own key. The key is read from standard input, so it is not
in the shell's history or the process list. On its own, the app takes its keys from its settings, e.g.
QUBIT_NOTES_ANTHROPIC_API_KEY.
"""

import argparse
import sys
from typing import TextIO

from qubit_notes.platform.port import PlatformError, StudyPlatform
from qubit_notes.settings import Settings

PROVIDERS = ("anthropic", "openai")


def _platform(settings: Settings) -> StudyPlatform:
    from qubit_notes import storage
    from qubit_notes.platform import platform_from

    return platform_from(settings, storage.connect(settings.database_url))


def main(argv: list[str] | None = None, stdin: TextIO = sys.stdin, platform: StudyPlatform | None = None) -> int:
    parser = argparse.ArgumentParser(prog="qubit-notes", description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("migrate", help="bring the app's database (QUBIT_NOTES_DATABASE_URL) up to date")
    commands.add_parser("reembed", help="embed the material again with the app's embedding model")
    store = commands.add_parser("store-provider-key", help="store the app's key of a model provider in gogi")
    store.add_argument("provider", choices=PROVIDERS)
    args = parser.parse_args(argv)
    settings = Settings()

    if args.command == "migrate":
        from qubit_notes import storage

        storage.connect(settings.database_url).dispose()
        print("the database is up to date")
        return 0

    if args.command == "reembed":
        platform = platform or _platform(settings)
        if not hasattr(platform, "reembed"):
            print("gogi embeds the material: there's nothing for the app to embed again", file=sys.stderr)
            return 1
        count = platform.reembed(progress=lambda document: print(f"embedded {document.filename}"))
        print(f"embedded {count} material(s) with {settings.embedding_model}")
        return 0

    key = stdin.read().strip()
    if not key:
        print(f"no {args.provider} key on standard input", file=sys.stderr)
        return 1
    platform = platform or _platform(settings)
    try:
        platform.store_credential(args.provider, key)
    except PlatformError as e:
        print(e.details, file=sys.stderr)
        return 1
    print(f"stored the app's {args.provider} key in gogi; its credentials: {', '.join(platform.list_credentials())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

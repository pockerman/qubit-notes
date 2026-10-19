"""``qubit-notes``: what is done for a deployment, e.g. storing the app's Anthropic key in gogi.

    echo "$ANTHROPIC_API_KEY" | qubit-notes store-provider-key anthropic
    qubit-notes migrate

The key is read from standard input, so it is not in the shell's history or the process list. The app's summaries,
quizzes and answers are then written with it: where gogi serves many applications, each calls the model providers
with its own key. ``migrate`` brings the app's database up to date, as the app does when it starts; a deployment runs
it first, so a new version's migrations run once, before it serves.
"""

import argparse
import sys
from typing import TextIO

from qubit_notes.platform.port import StudyPlatform
from qubit_notes.settings import Settings

PROVIDERS = ("anthropic", "openai")


def _platform() -> StudyPlatform:
    from qubit_notes.platform.gogi_adapter import GogiPlatform

    return GogiPlatform(Settings())


def main(argv: list[str] | None = None, stdin: TextIO = sys.stdin, platform: StudyPlatform | None = None) -> int:
    parser = argparse.ArgumentParser(prog="qubit-notes", description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    store = commands.add_parser("store-provider-key", help="store the app's key of a model provider in gogi")
    store.add_argument("provider", choices=PROVIDERS)
    commands.add_parser("migrate", help="bring the app's database (QUBIT_NOTES_DATABASE_URL) up to date")
    args = parser.parse_args(argv)

    if args.command == "migrate":
        from qubit_notes import storage

        storage.connect(Settings().database_url).dispose()
        print("the database is up to date")
        return 0

    key = stdin.read().strip()
    if not key:
        print(f"no {args.provider} key on standard input", file=sys.stderr)
        return 1
    platform = platform or _platform()
    platform.store_credential(args.provider, key)
    print(f"stored the app's {args.provider} key in gogi; its credentials: {', '.join(platform.list_credentials())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

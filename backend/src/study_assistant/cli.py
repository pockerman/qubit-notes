"""``study-assistant``: what is done once for a deployment, e.g. storing the app's Anthropic key in gogi.

    echo "$ANTHROPIC_API_KEY" | study-assistant store-provider-key anthropic

The key is read from standard input, so it is not in the shell's history or the process list. The app's summaries,
quizzes and answers are then written with it: where gogi serves many applications, each calls the model providers
with its own key.
"""

import argparse
import sys
from typing import TextIO

from study_assistant.platform.port import StudyPlatform
from study_assistant.settings import Settings

PROVIDERS = ("anthropic", "openai")


def _platform() -> StudyPlatform:
    from study_assistant.platform.gogi_adapter import GogiPlatform

    return GogiPlatform(Settings())


def main(argv: list[str] | None = None, stdin: TextIO = sys.stdin, platform: StudyPlatform | None = None) -> int:
    parser = argparse.ArgumentParser(prog="study-assistant", description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    store = commands.add_parser("store-provider-key", help="store the app's key of a model provider in gogi")
    store.add_argument("provider", choices=PROVIDERS)
    args = parser.parse_args(argv)

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

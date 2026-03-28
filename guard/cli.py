"""CLI entry point for the oh-my-agent AST guard."""

import argparse
import sys
from pathlib import Path

from guard.checker import validate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="oh-my-agent-guard",
        description="Validate generated agent project structure",
    )
    subparsers = parser.add_subparsers(dest="command")

    check_parser = subparsers.add_parser("check", help="Check project structure")
    check_parser.add_argument("path", type=Path, help="Path to agent project")
    check_parser.add_argument(
        "--rules",
        type=Path,
        default=Path(__file__).parent / "rules.yaml",
        help="Path to rules.yaml (default: built-in rules)",
    )

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_usage()
        return 2

    violations = validate(args.path, args.rules)

    if violations:
        print(f"Found {len(violations)} violation(s):\n")
        for v in violations:
            print(f"  [{v.rule}] {v.message}")
            print(f"    -> {v.path}\n")
        return 1

    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

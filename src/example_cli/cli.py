"""Dummy CLI showing the src/ pattern. Copy this package to start your own tool.

Anatomy of a CLI in this repo:

- one package per command under src/, named <tool>_cli
- main() builds an argparse parser with one subparser per subcommand
- each subcommand is a cmd_<name>(args) function
- registered as a global command in pyproject.toml under [project.scripts], then reinstalled
  with `pipx install -e . --force`

Use src/ over bin/ when the tool needs third-party packages, or grows past a single file.
"""

import argparse
import sys
from pathlib import Path


def cmd_greet(args):
    """Print a greeting, repeated."""
    for _ in range(args.times):
        print(f"Hello, {args.name}.")


def cmd_count(args):
    """Count files by extension in a directory."""
    root = Path(args.path).resolve()
    if not root.is_dir():
        sys.exit(f"Error: {root} is not a directory")

    counts = {}
    for f in root.rglob("*"):
        if f.is_file():
            ext = f.suffix or "(no extension)"
            counts[ext] = counts.get(ext, 0) + 1

    if not counts:
        print(f"No files under {root}")
        return

    for ext, n in sorted(counts.items(), key=lambda kv: kv[1], reverse=True):
        print(f"  {n:>5}  {ext}")
    print(f"\nTotal: {sum(counts.values())}")


def main():
    parser = argparse.ArgumentParser(prog="example", description="Dummy CLI to copy from")
    sub = parser.add_subparsers(dest="command")

    p_greet = sub.add_parser("greet", help="Print a greeting")
    p_greet.add_argument("name", help="Who to greet")
    p_greet.add_argument("--times", type=int, default=1, help="Repeat count (default: 1)")

    p_count = sub.add_parser("count", help="Count files by extension")
    p_count.add_argument("path", nargs="?", default=".", help="Directory to scan (default: .)")

    args = parser.parse_args()
    if args.command == "greet":
        cmd_greet(args)
    elif args.command == "count":
        cmd_count(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

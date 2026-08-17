"""CLI for global toolbox management.

Owns everything needed to make this repo's content visible to coding agents: generating the Cursor
specific rule format, and symlinking each content directory into the agent config directories.
"""

import argparse
import sys
from pathlib import Path

MDC_FRONTMATTER = "---\nalwaysApply: true\n---\n"

# (directory in this repo, symlink to create). Add a row to link a new content directory.
LINK_TARGETS = [
    ("skills", Path.home() / ".claude" / "skills"),
    ("skills", Path.home() / ".cursor" / "skills"),
    ("skills", Path.home() / ".config" / "opencode" / "skills"),
    ("commands", Path.home() / ".claude" / "commands"),
    ("commands", Path.home() / ".cursor" / "commands"),
    ("rules", Path.home() / ".claude" / "rules"),
    (".cursor-rules", Path.home() / ".cursor" / "rules"),
]


def _repo_root() -> Path:
    """Resolve the repo root from this file's location (editable install)."""
    return Path(__file__).resolve().parent.parent.parent


def cmd_generate(args):
    """Generate Cursor .mdc rule files from rules/*.md."""
    repo = _repo_root()
    rules_dir = repo / "rules"
    if not rules_dir.is_dir():
        sys.exit(f"Error: {rules_dir} does not exist")

    output_dir = repo / ".cursor-rules"
    output_dir.mkdir(parents=True, exist_ok=True)

    for old in output_dir.glob("*.mdc"):
        old.unlink()

    count = 0
    for f in sorted(rules_dir.glob("*.md")):
        mdc = output_dir / f"{f.stem}.mdc"
        mdc.write_text(MDC_FRONTMATTER + f.read_text())
        count += 1

    print(f"Generated {count} .mdc files in {output_dir}")


def cmd_link(args):
    """Symlink this repo's content into ~/.claude, ~/.cursor, ~/.config/opencode."""
    repo = _repo_root()

    for source_name, target in LINK_TARGETS:
        source = repo / source_name
        if not source.is_dir():
            sys.exit(f"Error: {source} does not exist. Run 'skills generate' first.")
        # Refuse to delete real content someone already has at the target path.
        if target.is_dir() and not target.is_symlink():
            sys.exit(
                f"Error: {target} is a real directory, not a symlink.\n"
                f"  Move its contents into {source} and remove it, then rerun."
            )

    for source_name, target in LINK_TARGETS:
        source = repo / source_name
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink() or target.exists():
            target.unlink()
        target.symlink_to(source)
        print(f"  {target} -> {source}")

    print("Symlinks created.")


def cmd_sync(args):
    """Generate Cursor rules, then create the global symlinks."""
    cmd_generate(args)
    cmd_link(args)


def main():
    parser = argparse.ArgumentParser(prog="skills", description="Global toolbox management")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("generate", help="Generate Cursor .mdc rule files from rules/*.md")
    sub.add_parser("link", help="Create global symlinks to ~/.claude, ~/.cursor, ~/.config/opencode")
    sub.add_parser("sync", help="Generate Cursor rules and create global symlinks")

    args = parser.parse_args()
    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "link":
        cmd_link(args)
    elif args.command == "sync":
        cmd_sync(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

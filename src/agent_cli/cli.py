"""CLI for project-level agent management.

The global toolbox is shared across every project. This CLI handles the other half: rules, commands,
and skills that belong to a single project. They live in a project's `agent/` directory and are
synced into `.cursor/` and `.claude/` so both tools see them.
"""

import argparse
import os
import sys
from pathlib import Path

MDC_FRONTMATTER = "---\nalwaysApply: true\n---\n"

EXCLUDE_LINES = [
    "/agent",
    ".cursor/commands/",
    ".cursor/rules/",
    ".cursor/skills/",
    ".claude/commands/",
    ".claude/rules/",
    ".claude/skills/",
]

EXAMPLE_RULE = """\
# Project conventions

Follow the project's existing patterns and naming conventions.
"""

EXAMPLE_COMMAND = """\
# Research

Research the given topic. Gather facts from multiple angles, note trade-offs, and present findings.
"""

EXAMPLE_SKILL = """\
---
name: example-skill
description: Example project skill. Replace with your own.
---

# Example skill

1. Confirm context with the user.
2. Perform the task.
3. Summarize what was done.
"""


def cmd_init(args):
    """Scaffold agent directory structure with examples in cwd."""
    root = Path.cwd() / "agent"
    if root.exists():
        sys.exit(f"Error: {root} already exists")

    (root / "rules").mkdir(parents=True)
    (root / "commands").mkdir(parents=True)
    (root / "skills" / "example-skill").mkdir(parents=True)
    (root / "references").mkdir(parents=True)

    (root / "rules" / "conventions.md").write_text(EXAMPLE_RULE)
    (root / "commands" / "research.md").write_text(EXAMPLE_COMMAND)
    (root / "skills" / "example-skill" / "SKILL.md").write_text(EXAMPLE_SKILL)

    print(f"Initialized agent structure in {root.resolve()}")
    print("  rules/conventions.md")
    print("  commands/research.md")
    print("  skills/example-skill/SKILL.md")


def cmd_sync(args):
    """Sync agent/ into .cursor/ and .claude/ for the current project."""
    project_root = Path.cwd()
    agent_dir = project_root / "agent"

    if not agent_dir.exists():
        sys.exit(
            "Error: ./agent/ does not exist.\n"
            "  Run 'agent init' to create the structure, then symlink it into your project."
        )

    cursor_rules = project_root / ".cursor" / "rules"
    cursor_commands = project_root / ".cursor" / "commands"
    cursor_skills = project_root / ".cursor" / "skills"
    claude_rules = project_root / ".claude" / "rules"
    claude_commands = project_root / ".claude" / "commands"
    claude_skills = project_root / ".claude" / "skills"

    for d in (cursor_rules, cursor_commands, cursor_skills, claude_rules, claude_commands, claude_skills):
        d.mkdir(parents=True, exist_ok=True)

    for d in (cursor_rules, cursor_commands, cursor_skills, claude_rules, claude_commands, claude_skills):
        _clean_stale_symlinks(d, agent_dir)
    _clean_stale_mdc(cursor_rules, agent_dir / "rules")

    counts = {"rules": 0, "commands": 0, "skills": 0}

    # Cursor reads .mdc with frontmatter, Claude Code reads plain .md
    rules_src = agent_dir / "rules"
    if rules_src.is_dir():
        for f in sorted(rules_src.glob("*.md")):
            name = f.stem
            (cursor_rules / f"{name}.mdc").write_text(MDC_FRONTMATTER + f.read_text())
            _symlink(f, claude_rules / f"{name}.md")
            counts["rules"] += 1

    commands_src = agent_dir / "commands"
    if commands_src.is_dir():
        for f in sorted(commands_src.glob("*.md")):
            name = f.stem
            _symlink(f, cursor_commands / f"{name}.md")
            _symlink(f, claude_commands / f"{name}.md")
            counts["commands"] += 1

    skills_src = agent_dir / "skills"
    if skills_src.is_dir():
        for d in sorted(p for p in skills_src.iterdir() if p.is_dir() and not p.name.startswith(".")):
            _symlink(d, cursor_skills / d.name)
            _symlink(d, claude_skills / d.name)
            counts["skills"] += 1

    _update_git_exclude(project_root)

    print(f"Synced {counts['rules']} rules, {counts['commands']} commands, {counts['skills']} skills")


def _symlink(source: Path, target: Path):
    """Create or replace a symlink."""
    source = source.resolve()
    if target.is_symlink() or target.exists():
        target.unlink()
    os.symlink(source, target)


def _clean_stale_symlinks(target_dir: Path, agent_dir: Path):
    """Remove symlinks pointing into agent_dir whose target no longer exists."""
    if not target_dir.exists():
        return
    agent_resolved = agent_dir.resolve()
    for entry in target_dir.iterdir():
        if not entry.is_symlink():
            continue
        try:
            link_target = entry.resolve()
        except OSError:
            continue
        if str(link_target).startswith(str(agent_resolved)) and not link_target.exists():
            entry.unlink()


def _clean_stale_mdc(target_dir: Path, rules_src: Path):
    """Remove generated .mdc files whose .md source no longer exists."""
    if not target_dir.exists() or not rules_src.exists():
        return
    for entry in target_dir.iterdir():
        if entry.suffix != ".mdc":
            continue
        if not (rules_src / f"{entry.stem}.md").exists():
            entry.unlink()


def _update_git_exclude(project_root: Path):
    """Ignore generated agent files locally, without touching the project's .gitignore."""
    git_dir = project_root / ".git"
    if not git_dir.is_dir():
        return
    exclude_file = git_dir / "info" / "exclude"
    exclude_file.parent.mkdir(parents=True, exist_ok=True)

    existing = exclude_file.read_text() if exclude_file.exists() else ""

    lines_to_add = [line for line in EXCLUDE_LINES if line not in existing]
    if lines_to_add:
        with exclude_file.open("a") as f:
            if existing and not existing.endswith("\n"):
                f.write("\n")
            for line in lines_to_add:
                f.write(line + "\n")


def main():
    parser = argparse.ArgumentParser(prog="agent", description="Project-level agent management")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("init", help="Scaffold agent directory structure")
    sub.add_parser("sync", help="Sync agent/ into .cursor/ and .claude/")

    args = parser.parse_args()
    if args.command == "init":
        cmd_init(args)
    elif args.command == "sync":
        cmd_sync(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

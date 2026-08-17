# Agent toolbox template

Template for a personal agent toolbox: one repo holding the rules, commands, skills, and CLI tools
you build up while working with coding agents.

Repo tries to organize agent primitives (skills, commands, rules, CLI tools) to:
- live in a single git repo
- work across repos and coding agents (Claude Code, Cursor, OpenCode)
- support both a global configuration and project specific ones
- have minimal hassle to add or edit, and scale over time

Fork it, delete the examples, add your own.

## Description

The idea is to have one place to store all agent building primitives, and symlink them into the
global configs of popular coding agents, so these primitives become available in every repo.

Symlinking allows editing from this repo or from an agent's config directory, keeping everything in
sync automatically.

The only exception so far is Cursor rules: automatically-applied `.md` rules expect a specific `.mdc`
extension, so symlinking alone doesn't work. This project adds a `skills sync` command to regenerate
rules for Cursor. In the future it will run any other additional logic needed to keep configs in
sync.

This repo is also the standard place to add CLI tools that skills can reference. Keeping CLI tools
separate from skills is intentional: it lets many skills, rules, and commands share the same CLI.

For project specific skills, rules, etc, use the `agent` CLI, which helps add those to a project.

Every directory below ships with one example that explains its own format. Read it, then replace it.

## Folder structure

Symlinked agent primitives:
- `commands/` - plain .md slash commands, user-triggered via `/name`
- `rules/` - always-applied .md rules. Run `skills sync` to generate Cursor .mdc variants and symlink them globally.
- `skills/` - SKILL.md directories, auto-invoked by the agent

Supporting folders:
- `references/` - documentation, files, any other assets that skills, commands, rules can reference
- `bin/` - standalone executable scripts
- `src/` - Python packages installed via `pip install -e .` that needs 3rd party dependencies

## Set up

### Install CLI

```shell
# Install/reinstall CLI from local repo
pipx install -e . --force

# or install CLI from the github repo
pipx install git+https://github.com/<you>/<your-fork>.git
```

### Symlink to global configs

```shell
skills sync
```

If a target such as `~/.claude/skills` already exists as a real directory rather than a symlink,
`skills sync` stops with an error instead of overwriting it. Move its contents into this repo, remove
the directory, then rerun.

### Add "bin" folder to PATH

Add the [`bin`](bin) folder to `~/.zshrc`:
```shell
subl ~/.zshrc
export PATH="/path/to/this/repo/bin:$PATH"
```

### Development

- `make setup` - create local venv and install packages (for development)
- `make clean` - remove generated files and virtual environment

## Flow

### Add skill

Create a new directory with a `SKILL.md` under `skills/`. No need to rerun `skills sync`: the whole
`skills/` folder is symlinked as one unit, so new skills show up automatically once linked.

### Add rule

Add a new `.md` file under `rules/`, then run `skills sync` to regenerate the Cursor `.mdc` variant
and relink.

### Add command

Add a new `.md` file under `commands/`. No need to rerun `skills sync`: the whole `commands/` folder
is symlinked as one unit, so new commands show up automatically once linked.

### Add bin script

Drop an executable file with a shebang into `bin/`, no extension, then `chmod +x` it. It is available
immediately because `bin/` is on your PATH. Best for shell one-liners and single-file scripts with no
dependencies.

### Add CLI

1. create a new package under `src/`, e.g. `src/my_cli/cli.py`, with a `main()` function
2. register it under `[project.scripts]` in `pyproject.toml`, e.g. `my-cli = "my_cli.cli:main"`
3. run `pipx install -e . --force` to reinstall the package

Copy `src/example_cli/` as a starting point. Best when a tool needs third-party packages or more than
one file.

## CLI

Available CLI tools:

- [Skills CLI](#skills-cli) - `skills sync` - sync rules across coding agents
- [Agent CLI](#agent-cli) - manage project-local primitives
- `example` - dummy CLI showing the `src/` pattern, delete it
- `hello` - dummy `bin` script, delete it

### Skills CLI

Manages this repo's `rules/`, `skills/`, `commands/`, then syncs them into the global `~/.claude`,
`~/.cursor`, `~/.config/opencode` directories.

- `skills generate` - generate Cursor `.mdc` rule files from `rules/*.md` into `.cursor-rules/`
- `skills link` - symlink `rules/`, `skills/`, `commands/` into coding agent global configuration `~/.claude`, `~/.cursor`, `~/.config/opencode`
- `skills sync` - run `generate` then `link`

Links created by `skills link`:

~/.claude
 skills -> skills/
 commands -> commands/
 rules -> rules/
~/.cursor
 skills -> skills/
 commands -> commands/
 rules -> .cursor-rules/
~/.config/opencode
 skills -> skills/

To link another directory, add a row to `LINK_TARGETS` in `src/skills_cli/cli.py`.

### Agent CLI

Sometimes rules and commands should only load in the context of a specific project, e.g. to save
token space rather than loading everything globally. The Agent CLI helps set that up.

Manages a project-local `agent/` folder with rules, commands, etc, then syncs it into the project's
`.cursor/` and `.claude/` directories.

Project specific CLI tools aren't supported: all CLIs live in this one `skills-cli` package to keep
management simple.

`agent init` - scaffold an `./agent` directory with example rules, commands, and skills.

`agent sync` - sync `./agent/` into `.cursor/` and `.claude/` for the current project. Creates
symlinks for commands and skills, generates `.mdc` for Cursor rules, and updates
`.git/info/exclude` so nothing leaks into a shared project's git history.
env`, add `.venv/bin` to PATH

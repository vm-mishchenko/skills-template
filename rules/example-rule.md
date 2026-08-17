# Example rule

Context the agent always has. Use it for stable preferences: coding style, review expectations,
which CLI tools exist. Every rule loads into every conversation, so keep it short. Task specific
guidance belongs in a skill or command instead.

Delete this file and add your own.

## Writing rules

- One topic per file, named after the topic
- Write directives, not explanations
- Plain Markdown, no frontmatter. `skills generate` adds the `.mdc` Cursor needs
- Link to `references/` rather than inlining long material, keeping the always-loaded part small

When proposing a change, follow [example-template.md](../references/example-template.md).

# plugin-template

Starter for a new Gold Valley plugin. One source tree, three thin manifests.

```
plugin-template/
  .claude-plugin/plugin.json   # Claude Code and claude.ai (docs: https://code.claude.com/docs/en/plugins/manifest-reference)
  .cursor-plugin/plugin.json   # Cursor plugin (docs: https://cursor.com/docs/reference/plugins)
  plugin.json                  # Agent Plugins, portable (docs: https://agent-plugins.org/plugin-authors/manifest)
  skills/<skill-name>/SKILL.md # the work itself, written once
  memory-templates/            # empty starter files copied into the user's folder at setup
  evals/                       # fixtures and expected answers
```

## Make a new plugin

1. Copy this folder to `plugins/<name>`. Use a lowercase kebab-case name.
2. In all three manifests, change `name`, `description` and `version`. They must match.
3. Rename or replace `skills/example/` with your real skills. Each skill folder name must equal its `name` in the `SKILL.md` frontmatter.
4. Add the plugin to both `.claude-plugin/marketplace.json` and `.cursor-plugin/marketplace.json` at the repository root.
5. Run `python3 scripts/validate.py`.

## Notes on the manifests

- The three manifests repeat the same `name`, `version` and `description` on purpose. `scripts/validate.py` fails if they drift.
- Agent Plugins: the root `plugin.json` must carry the `$schema` line shown here, and the schema is closed, so extra top-level fields are errors in this repo. Client-specific data goes under `extensions`.
- Cursor does not expand the Agent Plugins `${PLUGIN_ROOT}` variable in `mcp.json`. Use `${CURSOR_PLUGIN_ROOT}` for Cursor if you add MCP servers.
- If you add MCP servers, keep `.mcp.json` (Claude) and `mcp.json` (Cursor and Agent Plugins) in step. Validate checks that both exist together and match. Free Claude accounts can add only one custom connector, so avoid requiring one.
- Plugin files are read-only at runtime. Anything the plugin learns is written into the user's own working folder, never into the plugin folder.

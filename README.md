# gvs-plugins

The Gold Valley Solutions plugin marketplace: plugins that each do one office job, which you install by name on a personal Claude account or another tool that accepts them.

Plugins are plain files: instructions (skills), starter notes and fixtures. There is no server, nothing is sent anywhere by the plugins themselves, and what a plugin learns about your office is saved as text files in your own working folder.

**Status: early.** The planned order is Coordinator, then Inbox, Librarian and Bookkeeper. Install a listed plugin as `<name>@goldvalleysolutions`, for example `coordinator@goldvalleysolutions`.

## Plugins

| Plugin | What it does | Status |
| --- | --- | --- |
| [Coordinator](plugins/coordinator/README.md) | Tasks, assignees, due dates, and Google Calendar meetings, in your own notes. | 0.1.0, built. A human install test and a model eval on a Claude account are still outstanding. |

## Install

### 1. On claude.ai or the Claude desktop app (the usual path)

Open **Customize > Plugins**, choose **Add > Add marketplace**, and enter `goldvalleysolutions/gvs-plugins`. Then pick a plugin from the list and select **Add**.

The install name is the plugin name, an `@`, and the marketplace name, for example `coordinator@goldvalleysolutions` once Coordinator is listed. A plugin's skills then run as `/<plugin>:<skill>`, for example `/coordinator:setup`.

### 2. Upload a zip

Zip a plugin folder (either the folder itself or its contents), then use **Customize > Plugins > Add > Upload plugin** and choose the `.zip` (or `.plugin`) file. The archive must hold exactly one `.claude-plugin/plugin.json`.

### 3. Claude Code (terminal or session)

```bash
claude plugin marketplace add goldvalleysolutions/gvs-plugins
claude plugin install coordinator@goldvalleysolutions
```

Or inside a Claude Code session:

```text
/plugin marketplace add goldvalleysolutions/gvs-plugins
/plugin install coordinator@goldvalleysolutions
```

### 4. Install one plugin from a folder

Each plugin folder is self-contained, so you can use one without the marketplace.

- Claude Code, for one session: `claude --plugin-dir ./plugins/<name>`
- Cursor: copy the folder to `~/.cursor/plugins/local/<name>`, then restart Cursor or run **Developer: Reload Window**.

Questions? Use the contact form on our website: [goldvalleysolutions.com/#contact](https://goldvalleysolutions.com/#contact).

## What works on which Claude plan

Plans and limits are Anthropic's and can change; checked in November 2026.

- **Free:** plugins work on the Claude Free plan (Customize > Plugins). You can add this marketplace and upload a plugin zip.
- **Free limits that matter:** one custom connector, and no scheduled tasks. These plugins keep their notes in local files and do not need a custom connector.
- **Pro or higher** is needed for scheduled tasks (for example a morning "needs you" list). On Free you ask by hand.
- **Claude Code** works with a plugin from this marketplace as shown above.
- Plugins that only contain skills and notes, like the ones planned here, load in chat. Hooks and sub-agents run in Cowork and Claude Code, not in chat.

## Other tools

Each plugin keeps one source tree and thin manifests for each tool. Formats are still moving, so treat the lines below as what the docs say today, not as a promise.

| Tool | Manifest in this repo | Docs |
| --- | --- | --- |
| Claude Code and claude.ai | `.claude-plugin/marketplace.json`, `<plugin>/.claude-plugin/plugin.json` | https://code.claude.com/docs/en/plugins/marketplace-reference, https://code.claude.com/docs/en/plugins/manifest-reference |
| Cursor | `.cursor-plugin/marketplace.json`, `<plugin>/.cursor-plugin/plugin.json` | https://cursor.com/docs/plugins, https://cursor.com/docs/reference/plugins |
| Agent Plugins (portable; ChatGPT and Codex) | `<plugin>/plugin.json` | https://agent-plugins.org/plugin-authors/manifest, https://developers.openai.com/plugins/build/plugins |

Known gaps, so nobody is surprised:

- **Cursor marketplace:** Cursor documents `.cursor-plugin/marketplace.json` for multi-plugin repositories, but installing from a third-party GitHub marketplace in Cursor may need a team plan or a listing in the Cursor Marketplace. We have not tested it and have not submitted anything. Installing one plugin from a local folder is documented and is the safe path.
- **Codex and ChatGPT:** the root `plugin.json` is the portable Agent Plugins manifest and should load there. OpenAI also describes its own marketplace catalog file at `.agents/plugins/marketplace.json`. This repo does not ship one yet. Untested.
- We have tried the Claude Code install from a local copy of this repository. Installing from the public GitHub address, or from Customize > Plugins against this marketplace, needs the repository to be published first.

## Check your work

```bash
python3 scripts/validate.py                  # our checks, plus `claude plugin validate` if the CLI is installed
python3 scripts/validate.py --require-cli    # fail instead of skip when the claude CLI is missing
python3 -m unittest discover -s tests -v     # tests for the validator
python3 plugins/coordinator/evals/run_evals.py check   # offline Coordinator evals (no login)
```

The validator checks both marketplace files, then every folder in `plugins/` and `templates/plugin`: the three manifests agree on name, version and description, every referenced path exists, and every skill has frontmatter. It exits nonzero on any problem and prints a `SKIPPED` line, never a silent pass, when the `claude` CLI is not available. Install the CLI with `npm install -g @anthropic-ai/claude-code` (no login is needed to validate).

## Repository layout

```
.claude-plugin/marketplace.json   Claude Code marketplace catalog
.cursor-plugin/marketplace.json   Cursor marketplace catalog
plugins/<name>/                   one folder per plugin, installable on its own
templates/plugin/                 starter for a new plugin
scripts/validate.py               validator
tests/                            validator tests and fixtures
```

See [CONTRIBUTING.md](CONTRIBUTING.md) to add or change a plugin. To report a security issue, see [SECURITY.md](SECURITY.md). Licensed under the [MIT License](LICENSE).

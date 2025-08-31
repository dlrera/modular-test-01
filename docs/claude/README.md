# Using Claude Code with this repo

- Keep the model’s context small.
- Use the module context files as the only source of truth for cross-module behavior.
- For each task, create a `docs/claude/task-<ticket>-context.md` with acceptance criteria and allowed edit paths.
- Always run tests locally after applying patches.
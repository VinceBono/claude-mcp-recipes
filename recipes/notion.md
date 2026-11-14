# Notion (official server)

Connect Claude to Notion with the official `@notionhq/notion-mcp-server`, scoped to the pages you choose and read-only unless you need writes.

## 1. Create a scoped integration

1. Go to <https://www.notion.so/profile/integrations> → **New integration** (internal).
2. Under **Capabilities**, keep **Read content**. Turn off **Update content** and **Insert content** unless the assistant needs to write.
3. Copy the token (`ntn_…`). It goes in an environment variable, never in a config file you sync or commit.
4. In Notion, open each page or database the assistant should see → **⋯ → Connections → add your integration**. It can't see anything you don't share.

## 2. Claude Code (`.mcp.json` expands `${VAR}`)

```json
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server@2.6.1"],
      "env": { "NOTION_TOKEN": "${NOTION_TOKEN}" }
    }
  }
}
```

The token stays in your shell environment, so the file is safe to commit.

## 3. Claude Desktop

Claude Desktop doesn't expand `${VAR}`, and it doesn't hand your full environment to stdio servers. Use the launcher pattern in [windows-secrets.md](windows-secrets.md) instead of pasting the token into `claude_desktop_config.json`.

## Security notes

- **Least privilege is set in Notion, not in the MCP config.** Read-only capabilities plus page-level sharing is the real boundary.
- **Separate integrations per purpose** (e.g. `claude-research-ro`, `claude-ops-rw`), so you can revoke one without breaking the rest.
- **Page content is untrusted input.** Shared or public pages can carry prompt injection. Keep write capabilities off for integrations that read pages other people edit.
- **Rotate** the token if it ever lands in a file, a screenshot or a chat log.

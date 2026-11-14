# Obsidian vault (filesystem server)

Give Claude read and write access to one Obsidian vault and nothing else. An Obsidian vault is just a folder of Markdown files, so the official filesystem server is all you need. No plugin, no REST API, no TLS workarounds.

## Claude Desktop

```json
{
  "mcpServers": {
    "research-vault": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem@2.3.0", "D:\\Vaults\\Research"]
    }
  }
}
```

On Windows, if Claude Desktop can't find `npx`, use the full path (`C:\\Program Files\\nodejs\\npx.cmd`).

## Claude Code

From inside the vault, plain `claude` already has the folder. Add the server only when you want the vault available from other projects:

```bash
claude mcp add research-vault -- npx -y @modelcontextprotocol/server-filesystem@2.3.0 /path/to/vault
```

## Security notes

- **Pin the version** (`@2.3.0`). `npx -y package` with no version runs whatever was published last, the moment it was published. That's a supply-chain hole with auto-accept turned on.
- **Root it at the vault, never at `C:\`, `~` or your home folder.** The server can reach everything below the roots you pass. Your home folder holds SSH keys, browser profiles and `.env` files.
- **The server can write.** `write_file`, `edit_file` and `move_file` change your notes. Keep the vault under git, or sync with version history, so a bad edit is one revert away.
- **One server per vault.** Separate entries (`research-vault`, `work-notes`) keep a client vault out of a personal session, and make the tool calls easy to read in logs.
- **Notes are untrusted input.** Web clippings in a vault can carry prompt injection ("ignore previous instructions…"). Don't combine a vault server with high-impact tools (shell, cloud admin) in the same session without approval prompts on.

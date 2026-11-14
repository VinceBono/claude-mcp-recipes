# n8n workflows as MCP tools (authenticated remote server)

n8n's **MCP Server Trigger** node turns selected workflows into MCP tools at a URL on your n8n instance. That makes it a *remote* MCP server: anyone who can reach the URL and pass its auth can run those workflows. Treat the URL like an API, not like a local tool.

## 1. In n8n

1. Add an **MCP Server Trigger** node and attach only the tool workflows the assistant should run.
2. Set **Authentication** to **Bearer Auth** and create a credential with a long random token (`openssl rand -hex 32`). Don't leave it on "None".
3. Activate the workflow and copy the **Production URL**. The test URL only works while the editor is listening.

## 2. Claude Code (`.mcp.json`)

```json
{
  "mcpServers": {
    "n8n": {
      "type": "http",
      "url": "https://n8n.example.com/mcp/<path>",
      "headers": { "Authorization": "Bearer ${N8N_MCP_TOKEN}" }
    }
  }
}
```

`${N8N_MCP_TOKEN}` is read from your shell environment, so the file is safe to commit.

## 3. Claude Desktop (stdio bridge)

Claude Desktop reaches a remote server through `mcp-remote`. The header is passed with no spaces around the colon, because some clients on Windows mangle spaces in `args`:

```json
{
  "mcpServers": {
    "n8n": {
      "command": "npx",
      "args": ["-y", "mcp-remote@0.16.6", "https://n8n.example.com/mcp/<path>", "--header", "Authorization:${AUTH_HEADER}"]
    }
  }
}
```

`mcp-remote` fills `${AUTH_HEADER}` from its environment (`Bearer <token>`). Set that variable in a launcher script, as in [windows-secrets.md](windows-secrets.md), instead of an `env` block in the config. `mcp-remote` also supports `--header-file`, which keeps the token out of the process list.

## Security notes

- **HTTPS only.** A bearer token over plain HTTP is readable by anything on the path.
- **Don't expose n8n to the internet just for this.** Put it behind a VPN or Tailscale and use that hostname in the URL.
- **Each attached workflow is a capability.** A workflow that sends email, moves money or runs shell commands is now something a prompt injection can ask for. Expose narrow workflows with validated inputs, not a generic "HTTP request" or "execute command" tool.
- **Use a dedicated token per client**, and rotate it by editing the n8n credential. Executions appear in n8n's execution log, which is your audit trail.
- **Validate inputs inside the workflow.** The assistant chooses the arguments; the workflow should reject anything outside what it expects.

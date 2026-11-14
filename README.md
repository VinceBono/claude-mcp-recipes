# claude-mcp-recipes

Copy-paste MCP server setups for Claude Desktop and Claude Code, **hardened by default**: pinned versions, least-privilege credentials, no secrets in config files.

Most MCP setup guides stop at "it works". These recipes also cover what an attacker, or a confused agent, could do with the access you just granted, and how to shrink it.

## Recipes

| Recipe | What it connects | Key hardening |
|---|---|---|
| [Obsidian vault](recipes/obsidian-vault.md) | A Markdown vault via the official filesystem server | Pinned package, vault-only root, git as undo |
| [Notion](recipes/notion.md) | Notion pages and databases via `@notionhq/notion-mcp-server` | Read-only integration, page-level sharing, token via env |
| [Proxmox VE](recipes/proxmox.md) | A Proxmox cluster via an API-token MCP server | `PVEAuditor` token with privilege separation, TLS on, no public 8006 |
| [Docker MCP gateway](recipes/docker-mcp-gateway.md) | Containerized servers behind Docker's MCP gateway | Server and tool allowlists, `--block-network`, keychain secrets, signed images |
| [Cloudflare](recipes/cloudflare.md) | Cloudflare zones, DNS and Workers via `@cloudflare/mcp-server-cloudflare` | Scoped token instead of the Global API Key, read-only DNS, expiry and IP filter |
| [Windows secrets](recipes/windows-secrets.md) | Any server on Claude Desktop for Windows | Launcher script keeps tokens out of `claude_desktop_config.json` |

## The five rules behind every recipe

1. **Pin every package.** `npx -y some-server` with no version runs whatever was published last.
2. **Scope access at the source.** Read-only tokens, single folders, shared pages, one pool. The MCP config can't enforce limits the credential doesn't have.
3. **Secrets live in the environment or a vault**, never in a JSON file that gets synced, backed up or screenshotted.
4. **Treat tool output as untrusted input.** Notes, pages and web content can carry prompt injection. Don't pair read-anything servers with do-anything servers without approval prompts.
5. **Make it auditable.** A dedicated user or token per assistant shows up in the target system's logs as itself.

## Checked in CI

`scripts/check_recipes.py` lints every JSON block in `recipes/`. It fails on unpinned `npx`/`uvx` packages, literal secrets in `env`, and filesystem roots like `C:\` or `~`. Run it locally:

```bash
python scripts/check_recipes.py
```

These checks are a small preview of [mcpscan](https://github.com/darkdatalabs/mcpscan), a scanner for MCP configs and servers.

## Contributing

PRs with new recipes are welcome. Every recipe needs a working config, a **Security notes** section, and has to pass `check_recipes.py`.

## License

MIT © 2026 Vince Bono

# Cloudflare (scoped API token)

Let Claude inspect and manage Cloudflare resources with a token that can only touch what you list. The usual mistake is handing the assistant the **Global API Key**, which is full control of every zone, DNS record and billing setting on the account, with no expiry.

## 1. Create a scoped token

Cloudflare dashboard → **My Profile → API Tokens → Create Token → Custom token**.

| Setting | Recommendation |
|---|---|
| Permissions | Only what the task needs, **Read** unless you want writes. For example `Zone → DNS → Read`, `Account → Workers Scripts → Read` |
| Zone resources | **Specific zone**, not "All zones" |
| Account resources | The one account |
| Client IP filtering | Your home or VPN egress IP, if it's stable |
| TTL | Set an end date. Short for experiments |

Verify it before use:

```bash
curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" https://api.cloudflare.com/client/v4/user/tokens/verify
```

## 2. Claude Code (`.mcp.json`)

```json
{
  "mcpServers": {
    "cloudflare": {
      "command": "npx",
      "args": ["-y", "@cloudflare/mcp-server-cloudflare@0.2.0", "run", "<account-id>"],
      "env": { "CLOUDFLARE_API_TOKEN": "${CLOUDFLARE_API_TOKEN}" }
    }
  }
}
```

For Claude Desktop, use the launcher pattern in [windows-secrets.md](windows-secrets.md) so the token isn't stored in `claude_desktop_config.json`.

Cloudflare also runs hosted MCP servers that sign you in with OAuth in the browser. Those avoid a long-lived token on disk; check Cloudflare's docs for the current list and the scopes each one asks for.

## Security notes

- **Never use the Global API Key for an assistant.** It can't be scoped, and rotating it breaks everything else that uses it.
- **DNS write is high impact.** A changed MX or A record redirects mail or traffic. Keep DNS tokens read-only, and make changes yourself or through a separate write token you enable only when needed.
- **One token per assistant and per purpose.** The token name shows in Cloudflare's audit log, so assistant activity is easy to tell apart from yours, and you can revoke one without breaking the rest.
- **Pin the package.** An unpinned `npx -y` server that holds a Cloudflare token is a supply-chain path into your DNS.
- **Rotate** any token that was ever pasted into a config file, a chat or a screenshot.

# Proxmox VE (read-only API token)

Let Claude inventory and monitor a Proxmox cluster without being able to break it. This works with any Proxmox MCP server that authenticates with an API token (the example uses ProxmoxMCP-Plus's variable names). The safety comes from the token, not from the server.

## 1. Create a read-only token on the Proxmox host

```bash
pveum user add mcp@pve --comment "MCP assistant, read-only"
pveum user token add mcp@pve claude --privsep 1
pveum acl modify / --tokens 'mcp@pve!claude' --roles PVEAuditor
```

- `--privsep 1` gives the token its own permissions, separate from the user, so it gets **only** the ACL you grant it.
- `PVEAuditor` can read everything and change nothing.
- Need power actions later? Grant `PVEVMUser` on **one pool** (`/pool/lab`), not on `/`. Your production VMs stay out of reach.

The token secret is shown once. Store it in your password manager and an environment variable.

## 2. Claude Code (`.mcp.json`)

```json
{
  "mcpServers": {
    "proxmox": {
      "command": "<path-to-venv>\\Scripts\\python.exe",
      "args": ["-m", "proxmox_mcp.server"],
      "env": {
        "PROXMOX_HOST": "${PROXMOX_HOST}",
        "PROXMOX_USER": "mcp@pve",
        "PROXMOX_TOKEN_NAME": "claude",
        "PROXMOX_TOKEN_VALUE": "${PROXMOX_TOKEN_VALUE}",
        "PROXMOX_PORT": "8006",
        "PROXMOX_VERIFY_SSL": "true"
      }
    }
  }
}
```

For Claude Desktop, use the launcher pattern in [windows-secrets.md](windows-secrets.md) for `PROXMOX_TOKEN_VALUE`.

## Security notes

- **Never use `root@pam`.** A root password in an assistant config is full control of every VM, disk and backup.
- **Keep `VERIFY_SSL` on.** Install a proper certificate (ACME in the Proxmox UI), or pin the cluster CA, instead of turning verification off.
- **Don't expose port 8006 to the internet** for this. Reach the API over a VPN or Tailscale, and point `PROXMOX_HOST` at that address.
- **Audit:** API calls show up in the Proxmox task log and syslog under `mcp@pve!claude`, so assistant activity is easy to tell apart from yours.

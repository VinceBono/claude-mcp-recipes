# Keeping secrets out of Claude Desktop's config (Windows)

`claude_desktop_config.json` stores `env` values in plain text, and the file often ends up in backups, OneDrive sync or screenshots. Claude Desktop also doesn't pass your full user environment to stdio servers, so "just set an environment variable" doesn't work on its own.

Fix: launch the server through a small PowerShell script that reads the secret at start time.

## 1. Store the secret as a user environment variable

```powershell
[Environment]::SetEnvironmentVariable("NOTION_TOKEN", "<paste token>", "User")
```

This writes it to your user profile (HKCU), not to a synced file. For stronger protection, read it from Windows Credential Manager or your password manager's CLI in the script below.

## 2. Launcher script, e.g. `C:\mcp\notion.ps1`

```powershell
$env:NOTION_TOKEN = [Environment]::GetEnvironmentVariable("NOTION_TOKEN", "User")
if (-not $env:NOTION_TOKEN) { Write-Error "NOTION_TOKEN is not set"; exit 1 }
& "C:\Program Files\nodejs\npx.cmd" -y @notionhq/notion-mcp-server@2.6.1
```

## 3. Point Claude Desktop at the script

```json
{
  "mcpServers": {
    "notion": {
      "command": "powershell.exe",
      "args": ["-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "C:\\mcp\\notion.ps1"]
    }
  }
}
```

## Notes

- `-ExecutionPolicy Bypass` applies only to this process. If your machine enforces `AllSigned`, sign the script instead.
- Keep the package version pinned inside the script, the same as in a JSON config.
- The same pattern works for any server: Proxmox tokens, Cloudflare API tokens, database URLs.
- If a token was ever pasted into the config file, **rotate it**. Deleting the line doesn't remove copies from backups or sync history.

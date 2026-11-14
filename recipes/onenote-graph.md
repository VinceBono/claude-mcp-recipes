# OneNote via Microsoft Graph (least-privilege app registration)

Any MCP server that reads OneNote through Microsoft Graph needs an Entra ID app registration. The registration decides what the assistant can reach, so that's where the hardening goes. The same steps apply to Graph-based servers for Outlook, OneDrive or Teams; only the permission names change.

## 1. Register the app

Entra admin center → **App registrations → New registration**.

| Setting | Recommendation |
|---|---|
| Supported account types | **Single tenant** (or "personal accounts only" for a personal notebook). Not multi-tenant |
| Platform | **Mobile and desktop** (public client). Turn on **Allow public client flows** for device-code sign-in |
| Client secret / certificate | **None.** A local tool can't keep a secret; use the public client flow |
| API permissions | **Delegated** `Notes.Read` and `User.Read`. Remove everything else |

- **Delegated, not Application.** Delegated permissions act as the signed-in user and see only that user's notebooks. Application permissions (`Notes.Read.All`) read every user's notebooks in the tenant with no user present.
- Add `Notes.ReadWrite` only if the assistant must create or edit pages. Avoid the `.All` variants.

## 2. Claude Code (`.mcp.json`)

```json
{
  "mcpServers": {
    "onenote": {
      "command": "<path-to-venv>\\Scripts\\python.exe",
      "args": ["<path-to-server>\\server.py"],
      "env": {
        "AZURE_TENANT_ID": "${AZURE_TENANT_ID}",
        "AZURE_CLIENT_ID": "${AZURE_CLIENT_ID}"
      }
    }
  }
}
```

Variable names depend on the server you use. The tenant and client IDs aren't secrets, but there should be **no client secret** in this block at all.

## Security notes

- **The token cache is the credential.** After sign-in, the server stores a refresh token on disk. Check where your server keeps it, make sure it's encrypted (DPAPI on Windows, Keychain on macOS) or at least in a user-only folder, and keep it out of synced folders and git.
- **Consent is visible and revocable.** Review it under Enterprise applications → your app → Permissions, and revoke sessions there if a machine is lost.
- **Conditional Access still applies.** Delegated sign-in honors your MFA and device policies; an app secret would bypass them.
- **Notebook content is untrusted input.** Shared notebooks and pasted web clippings can carry prompt injection. Keep the registration read-only if other people can edit what the assistant reads.
- **Local alternative on Windows:** a server that talks to the OneNote desktop app over COM needs no app registration and no tokens. It can reach every notebook open in the app, so it has no permission boundary of its own.

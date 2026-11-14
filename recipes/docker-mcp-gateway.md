# Docker MCP gateway (containers, allowlists, keychain secrets)

Docker's MCP Toolkit runs each MCP server in its own container behind a single gateway. Claude sees one server; the gateway decides which servers start, which tools they expose, what network they reach, and which secrets they get. Most of the safety comes from flags you have to pass on purpose.

## Claude Desktop / Claude Code

```json
{
  "mcpServers": {
    "docker-gateway": {
      "command": "docker",
      "args": [
        "mcp", "gateway", "run",
        "--servers", "<server-a>,<server-b>",
        "--tools", "<tool-a>,<tool-b>",
        "--block-network",
        "--cpus", "1",
        "--memory", "512Mb"
      ]
    }
  }
}
```

Find exact server and tool names with `docker mcp catalog show docker-mcp`. If you manage servers as a profile instead, use `--profile <id>` in place of `--servers`, and set the tool allowlist with `docker mcp profile tools`.

## Secrets: OS keychain, not config

```bash
docker mcp secret set GITHUB_TOKEN        # paste the value on stdin, not on the command line
docker mcp secret ls
```

The gateway injects keychain secrets into the containers that declare them. `--block-secrets` (on by default) also stops secret values from passing through tool inputs and outputs.

## Hardening flags

| Flag | Default | Recommendation |
|---|---|---|
| `--servers` / `--profile` | none | Name the servers you want. **Avoid `--enable-all-servers`**: every catalog server becomes reachable |
| `--tools` | all tools | Allowlist the tools you use. Fewer tools means less surface for injection to steer |
| `--block-network` | off | **Turn it on.** Blocks tools from reaching forbidden network resources |
| `--block-secrets` | on | Keep it on |
| `--verify-signatures` | on | Keep it on. Refuses unsigned or tampered server images |
| `--cpus` / `--memory` | 1 / 2Gb | Lower memory for small servers; caps a runaway or hostile container |
| `--log-calls` | on | Keep it on. It's your audit trail of what the assistant actually ran |
| `--transport` | stdio | Stay on stdio for local clients. If you need `sse`/`streaming`, bind `--host 127.0.0.1` and set `MCP_GATEWAY_AUTH_TOKEN` |
| `--allow-unauthenticated` | off | **Never** on a shared or reachable network |

## Security notes

- **Containers aren't a full sandbox.** A server with a host volume mount can read and write that path. Don't add mounts for home folders, SSH keys or the Docker socket. Mounting `docker.sock` gives a server full control of the host.
- **Pin what you can.** Use `--oci-ref` with a digest (`image@sha256:…`) for servers you depend on, so a catalog update can't swap the image under you.
- **One gateway per trust level.** Run a read-only research gateway and a separate admin gateway with its own client entry, instead of one gateway with everything enabled.
- **Test the config without serving:** `docker mcp gateway run --dry-run …` starts the gateway and validates it without listening for connections.

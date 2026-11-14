# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Vince Bono
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_recipes import check_text  # noqa: E402


def md(servers: dict) -> str:
    return "```json\n" + json.dumps({"mcpServers": servers}) + "\n```"


def test_hardened_config_passes():
    ok = {
        "fs": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem@2.3.0", "D:\\Vault"]},
        "n": {"command": "npx", "args": ["-y", "@notionhq/notion-mcp-server@2.6.1"], "env": {"NOTION_TOKEN": "${NOTION_TOKEN}"}},
    }
    assert check_text(md(ok)) == []


def test_unpinned_package_fails():
    errs = check_text(md({"fs": {"command": "npx.cmd", "args": ["-y", "@modelcontextprotocol/server-filesystem", "D:\\V"]}}))
    assert any("pin" in e for e in errs)


def test_literal_secret_fails():
    errs = check_text(md({"n": {"command": "x", "env": {"NOTION_TOKEN": "ntn_abc123secret"}}}))
    assert any("literal secret" in e for e in errs)


def test_broad_filesystem_root_fails():
    for root in ["C:\\", "/", "~"]:
        args = ["-y", "@modelcontextprotocol/server-filesystem@2.3.0", root]
        assert any("too broad" in e for e in check_text(md({"fs": {"command": "npx", "args": args}})))


def test_invalid_json_fails():
    assert check_text("```json\n{nope\n```")


def test_repo_recipes_are_clean():
    root = Path(__file__).resolve().parents[1]
    for f in (root / "recipes").glob("*.md"):
        assert check_text(f.read_text(encoding="utf-8")) == [], f.name

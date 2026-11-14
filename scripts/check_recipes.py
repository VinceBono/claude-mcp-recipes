#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Vince Bono
"""Lint every JSON config block in recipes/*.md, so the repo never ships an unsafe example.

Rules (a subset of what mcpscan will enforce):
  pin      npx/uvx packages must carry an exact version (pkg@1.2.3)
  secret   secret-looking env values (TOKEN, KEY, PASSWORD...) must be placeholders (${VAR} or <...>), never literal tokens
  root     filesystem servers must not be rooted at /, ~ or a bare drive (C:\\)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BLOCK = re.compile(r"```json\n(.*?)```", re.S)
PLACEHOLDER = re.compile(r"^(\$\{[A-Z0-9_:-]+\}|<[^>]+>)$")
SECRET_KEY = re.compile(r"TOKEN|SECRET|PASSWORD|PASSWD|API_?KEY|PRIVATE|HEADERS|CREDENTIAL", re.I)
NON_SECRET = re.compile(r"_(NAME|ID|USER)$", re.I)  # identifiers like PROXMOX_TOKEN_NAME
PINNED = re.compile(r"^(@[\w.-]+/)?[\w.-]+@\d+\.\d+\.\d+$")
BAD_ROOTS = {"/", "~", "~/", "%USERPROFILE%"}
DRIVE_ROOT = re.compile(r"^[A-Za-z]:\\{0,2}$")


def check_server(name: str, s: dict) -> list[str]:
    errs = []
    cmd = Path(str(s.get("command", ""))).name.lower()
    args = [str(a) for a in s.get("args", [])]
    if cmd.startswith(("npx", "uvx")):
        pkgs = [a for a in args if not a.startswith("-")]
        if not pkgs or not PINNED.match(pkgs[0]):
            errs.append(f"{name}: pin the package to an exact version (pkg@x.y.z)")
    if any("server-filesystem" in a for a in args):
        roots = args[args.index(next(a for a in args if "server-filesystem" in a)) + 1 :]
        for r in roots:
            if r in BAD_ROOTS or DRIVE_ROOT.match(r):
                errs.append(f"{name}: filesystem root {r!r} is too broad")
    for k, v in (s.get("env") or {}).items():
        if SECRET_KEY.search(k) and not NON_SECRET.search(k) and not PLACEHOLDER.match(str(v)):
            errs.append(f"{name}: env {k} looks like a literal secret; use ${{VAR}} or <placeholder>")
    return errs


def check_text(text: str) -> list[str]:
    errs = []
    for i, block in enumerate(BLOCK.findall(text), 1):
        try:
            doc = json.loads(block)
        except json.JSONDecodeError as e:
            errs.append(f"block {i}: invalid JSON ({e})")
            continue
        for name, s in doc.get("mcpServers", {}).items():
            errs += check_server(name, s)
    return errs


def main() -> int:
    failed = False
    for f in sorted(Path("recipes").glob("*.md")):
        for e in check_text(f.read_text(encoding="utf-8")):
            print(f"{f}: {e}")
            failed = True
    print("recipes: FAIL" if failed else "recipes: ok")
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())

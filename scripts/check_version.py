#!/usr/bin/env python3
"""Validate release metadata for Network Topology."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "custom_components" / "network_topology" / "manifest.json"
CHANGELOG = ROOT / "CHANGELOG.md"
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def main() -> int:
    manifest = json.loads(MANIFEST.read_text())
    version = manifest.get("version")
    if not isinstance(version, str) or not SEMVER.match(version):
        print(f"Invalid manifest version: {version!r}", file=sys.stderr)
        return 1

    changelog = CHANGELOG.read_text()
    heading = f"## {version} - "
    if heading not in changelog:
        print(
            f"CHANGELOG.md must contain a release heading starting with {heading!r}",
            file=sys.stderr,
        )
        return 1

    print(f"version ok: {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

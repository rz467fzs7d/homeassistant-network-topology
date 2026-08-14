#!/usr/bin/env python3
"""Bump manifest version and create a changelog section."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "custom_components" / "network_topology" / "manifest.json"
CHANGELOG = ROOT / "CHANGELOG.md"
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="New semantic version, for example 0.2.0")
    parser.add_argument(
        "--message",
        default="Describe this release.",
        help="First changelog bullet for the new version.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not SEMVER.match(args.version):
        raise SystemExit(f"Version must be semantic x.y.z: {args.version}")

    manifest = json.loads(MANIFEST.read_text())
    old_version = manifest.get("version")
    manifest["version"] = args.version
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")

    changelog = CHANGELOG.read_text()
    heading = f"## {args.version} - "
    if heading not in changelog:
        release = f"## {args.version} - {date.today().isoformat()}\n\n- {args.message}\n\n"
        marker = "\n## "
        index = changelog.find(marker)
        if index == -1:
            changelog = changelog.rstrip() + "\n\n" + release
        else:
            changelog = changelog[: index + 1] + release + changelog[index + 1 :]
        CHANGELOG.write_text(changelog)

    print(f"bumped {old_version} -> {args.version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

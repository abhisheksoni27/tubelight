#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Literal

PYPROJECT = Path(__file__).resolve().parent.parent / "pyproject.toml"
PACKAGE_INIT = Path(__file__).resolve().parent.parent / "tubelight" / "__init__.py"

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")

Action = Literal["patch", "minor", "major", "set"]


def parse_version(version: str) -> tuple[int, int, int]:
    match = SEMVER_RE.match(version)
    if not match:
        raise ValueError(f"Invalid version: {version}")
    return tuple(int(part) for part in match.groups())


def format_version(version: tuple[int, int, int]) -> str:
    return ".".join(str(part) for part in version)


def bump_version(
    version: tuple[int, int, int], release_type: Action
) -> tuple[int, int, int]:
    major, minor, patch = version
    if release_type == "patch":
        return major, minor, patch + 1
    if release_type == "minor":
        return major, minor + 1, 0
    if release_type == "major":
        return major + 1, 0, 0
    raise ValueError(f"Unsupported bump type: {release_type}")


def read_pyproject() -> str:
    return PYPROJECT.read_text(encoding="utf-8")


def update_pyproject(version: str) -> None:
    content = read_pyproject()
    new_content, count = re.subn(
        r'^(version\s*=\s*")[0-9]+\.[0-9]+\.[0-9]+("$)',
        lambda m: f"{m.group(1)}{version}{m.group(2)}",
        content,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise RuntimeError("Failed to update version in pyproject.toml")
    PYPROJECT.write_text(new_content, encoding="utf-8")


def read_package_version() -> str:
    content = PACKAGE_INIT.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*"([0-9]+\.[0-9]+\.[0-9]+)"', content)
    if not match:
        raise RuntimeError("No __version__ found in package __init__.py")
    return match.group(1)


def update_package_version(version: str) -> None:
    content = PACKAGE_INIT.read_text(encoding="utf-8")
    new_content, count = re.subn(
        r'(__version__\s*=\s*")[0-9]+\.[0-9]+\.[0-9]+("$)',
        lambda m: f"{m.group(1)}{version}{m.group(2)}",
        content,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise RuntimeError("Failed to update __version__ in package __init__.py")
    PACKAGE_INIT.write_text(new_content, encoding="utf-8")


def current_version() -> str:
    return read_package_version()


def main(argv: list[str] | None = None) -> None:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("Usage: bump_version.py <patch|minor|major|set> [version]")
        raise SystemExit(1)

    action = argv[0]
    if action not in {"patch", "minor", "major", "set"}:
        raise SystemExit(f"Unknown action: {action}")

    if action == "set":
        if len(argv) != 2:
            raise SystemExit("Usage: bump_version.py set <version>")
        new_version = argv[1]
    else:
        current = current_version()
        new_version = format_version(bump_version(parse_version(current), action))

    update_pyproject(new_version)
    update_package_version(new_version)
    print(f"Version updated to {new_version}")


if __name__ == "__main__":
    main()

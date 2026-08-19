#!/usr/bin/env python3
"""Validate repository scope metadata, Markdown links, and research indexes."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
SCOPE_FILES = (ROOT / "android16/research-scope.json", ROOT / "android17/research-scope.json")
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def load_scope(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(errors, f"scope metadata cannot be read: {path.relative_to(ROOT)}: {exc}")
        return {}


def validate_scope(scope: dict, errors: list[str]) -> None:
    if not scope:
        return
    version_dir = scope.get("version_dir")
    baseline = scope.get("baseline", {})
    target = scope.get("target", {})
    required_values = (
        str(baseline.get("aosp_tag", "")),
        str(target.get("aosp_tag", "")),
        str(target.get("target_sdk", "")),
    )
    for relative in scope.get("scope_files", []):
        path = ROOT / relative
        if not path.is_file():
            fail(errors, f"scope file is missing: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for value in required_values:
            if value and value not in text:
                fail(errors, f"scope value {value!r} is missing from {relative}")

    expected_prompt_root = f"tmp/research-prompts/{version_dir}"
    if scope.get("output_roots", {}).get("intermediate_prompts") != expected_prompt_root:
        fail(errors, f"intermediate prompt root must be {expected_prompt_root}")

    for name in ("AGENTS.md", "README.md", "GETTING_STARTED.md"):
        path = ROOT / version_dir / name
        if "research-scope.json" not in path.read_text(encoding="utf-8"):
            fail(errors, f"scope metadata is not referenced from {path.relative_to(ROOT)}")


def local_link_target(markdown: Path, raw_target: str) -> Path | None:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    target = target.split(maxsplit=1)[0]
    if not target or target.startswith("#") or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
        return None
    target = unquote(target.split("#", 1)[0])
    if not target:
        return None
    return (markdown.parent / target).resolve()


def validate_markdown_links(errors: list[str]) -> None:
    for markdown in ROOT.rglob("*.md"):
        relative_parts = markdown.relative_to(ROOT).parts
        if ".git" in markdown.parts or relative_parts[0] in {"frameworks-base", "tmp"}:
            continue
        text = markdown.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK.findall(text):
            target = local_link_target(markdown, raw_target)
            if target is not None and not target.exists():
                fail(
                    errors,
                    f"broken Markdown link: {markdown.relative_to(ROOT)} -> {raw_target}",
                )


def require_indexed(index: Path, files: list[Path], errors: list[str]) -> None:
    if not index.is_file():
        fail(errors, f"index is missing: {index.relative_to(ROOT)}")
        return
    text = index.read_text(encoding="utf-8")
    for path in files:
        relative = path.relative_to(index.parent).as_posix()
        if relative not in text:
            fail(errors, f"artifact is not indexed: {path.relative_to(ROOT)}")


def validate_indexes(scope: dict, errors: list[str]) -> None:
    if not scope:
        return
    version_root = ROOT / scope["version_dir"]
    behavior_root = version_root / "behavior-changes"
    behavior_index = behavior_root / "README.md"
    excluded_names = {"README.md", "APPLICABILITY_CLASSIFICATION.md"}
    separately_indexed = {"version-comparisons", "implementation-examples"}
    behavior_files = [
        path
        for path in behavior_root.rglob("*.md")
        if path.name not in excluded_names
        and not (set(path.relative_to(behavior_root).parts) & separately_indexed)
    ]
    require_indexed(behavior_index, behavior_files, errors)

    for directory in separately_indexed:
        child_root = behavior_root / directory
        if child_root.is_dir():
            require_indexed(
                child_root / "README.md",
                [path for path in child_root.glob("*.md") if path.name != "README.md"],
                errors,
            )

    summaries_root = version_root / "summaries"
    require_indexed(
        summaries_root / "README.md",
        [path for path in summaries_root.rglob("*.md") if path.name != "README.md"],
        errors,
    )

    app_reports_root = version_root / "app-reports"
    require_indexed(
        app_reports_root / "README.md",
        list(app_reports_root.glob("*/investigation-report.md")),
        errors,
    )


def validate_operational_wording(errors: list[str]) -> None:
    paths = list((ROOT / "docs/workflow").glob("*.md"))
    paths += list((ROOT / "docs/translation").glob("*.md"))
    paths += [
        ROOT / "android17/AGENTS.md",
        ROOT / "android17/behavior-changes/APPLICABILITY_CLASSIFICATION.md",
    ]
    patterns = (
        re.compile(r"Android 17.{0,50}(?:tag|タグ).{0,30}(?:未公開|なく|存在しな|not available|unavailable)", re.I),
        re.compile(r"Android 17.{0,50}(?:tag|タグ).{0,30}(?:公開後|入手後|available)", re.I),
    )
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for pattern in patterns:
            if pattern.search(text):
                fail(errors, f"stale Android 17 pre-tag wording: {path.relative_to(ROOT)}")
                break


def validate_build_evidence_policy(errors: list[str]) -> None:
    canonical = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    required_order = """1. Entry point release notes
2. Official Documentation
3. Compatibility Matrix
4. API Reference / Migration Guide
5. Issue Tracker
6. 実機・実プロジェクト検証
7. Blog"""
    if required_order not in canonical:
        fail(errors, "canonical Build System evidence hierarchy is missing from AGENTS.md")

    reference_files = (
        ROOT / "build-system/AGENTS.md",
        ROOT / "build-system/README.md",
        ROOT / ".codex/prompts/investigation.md",
        ROOT / ".codex/prompts/build-system-design.md",
        ROOT / "docs/overview/SOURCES.md",
    )
    for path in reference_files:
        text = path.read_text(encoding="utf-8")
        if "AGENTS.md" not in text:
            fail(errors, f"Build System evidence policy does not reference AGENTS.md: {path.relative_to(ROOT)}")
        if "1. Official Documentation" in text or "1. Entry point release notes" in text:
            fail(errors, f"duplicate Build System evidence hierarchy: {path.relative_to(ROOT)}")


def validate_ignored_workspaces(errors: list[str]) -> None:
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for entry in ("frameworks-base/", "tmp/aosp-checkouts/", "tmp/research-prompts/"):
        if entry not in ignore:
            fail(errors, f"temporary workspace is not ignored: {entry}")


def main() -> int:
    errors: list[str] = []
    scopes = [load_scope(path, errors) for path in SCOPE_FILES]
    for scope in scopes:
        validate_scope(scope, errors)
        validate_indexes(scope, errors)
    validate_markdown_links(errors)
    validate_operational_wording(errors)
    validate_build_evidence_policy(errors)
    validate_ignored_workspaces(errors)

    if errors:
        print("Repository structure validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Repository structure validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate repository scope, evidence metadata, links, and artifact coverage."""

from __future__ import annotations

import argparse
import datetime
import html
import json
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
STANDARD_TAG = re.compile(r"^android-(\d+)\.0\.0_r([1-9]\d*)$")
INLINE_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
REFERENCE_DEFINITION = re.compile(r"^\s*\[([^\]]+)\]:\s*(<[^>]+>|\S+)", re.MULTILINE)
REFERENCE_USE = re.compile(r"(?<!!)\[([^\]]+)\]\[([^\]]*)\]")
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$", re.MULTILINE)
EXPLICIT_ANCHOR = re.compile(r"<a\s+(?:name|id)=[\"']([^\"']+)[\"']\s*></a>", re.I)
REQUIRED_SCOPE_KEYS = {
    "schema_version",
    "android_version",
    "version_dir",
    "baseline",
    "target",
    "default_reference_repository",
    "official_refs_url",
    "official_documentation",
    "output_roots",
    "scope_files",
    "artifact_policy",
    "analysis_metadata",
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def repository_path(root: Path, value: object, errors: list[str], label: str) -> Path | None:
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        fail(errors, f"{label} must be a non-empty repository-relative path")
        return None
    path = (root / value).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        fail(errors, f"{label} escapes the repository: {value}")
        return None
    return path


def discover_scope_files(root: Path) -> list[Path]:
    return sorted(root.glob("android*/research-scope.json"))


def load_json(path: Path, root: Path, errors: list[str], label: str) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(errors, f"{label} cannot be read: {relative(path, root)}: {exc}")
        return {}
    if not isinstance(data, dict):
        fail(errors, f"{label} must be a JSON object: {relative(path, root)}")
        return {}
    return data


def validate_tag(value: object, expected_version: int, errors: list[str], label: str) -> None:
    if not isinstance(value, str):
        fail(errors, f"{label} must be a string")
        return
    match = STANDARD_TAG.fullmatch(value)
    if not match:
        fail(errors, f"{label} is not a standard release tag: {value}")
    elif int(match.group(1)) != expected_version:
        fail(errors, f"{label} Android version does not match {expected_version}: {value}")


def validate_scope_file_values(path: Path, scope: dict, root: Path, errors: list[str]) -> None:
    if not path.is_file():
        fail(errors, f"scope file is missing: {relative(path, root)}")
        return
    text = path.read_text(encoding="utf-8")
    for label, value in (
        ("baseline tag", scope["baseline"]["aosp_tag"]),
        ("target tag", scope["target"]["aosp_tag"]),
    ):
        if value not in text:
            fail(errors, f"{label} {value!r} is missing from {relative(path, root)}")
    target_sdk = scope["target"]["target_sdk"]
    sdk_pattern = re.compile(rf"targetSdkVersion(?:\s*(?:>=|=|:)?\s*){target_sdk}\b")
    if not sdk_pattern.search(text):
        fail(errors, f"targetSdkVersion {target_sdk} is missing from {relative(path, root)}")


def validate_scope(scope: dict, scope_path: Path, root: Path, errors: list[str]) -> None:
    if not scope:
        return
    missing = sorted(REQUIRED_SCOPE_KEYS - scope.keys())
    if missing:
        fail(errors, f"scope keys are missing from {relative(scope_path, root)}: {', '.join(missing)}")
        return
    if scope.get("schema_version") != 1:
        fail(errors, f"unsupported scope schema_version in {relative(scope_path, root)}")
    android_version = scope.get("android_version")
    version_dir = scope.get("version_dir")
    if not isinstance(android_version, int) or isinstance(android_version, bool):
        fail(errors, f"android_version must be an integer: {relative(scope_path, root)}")
        return
    expected_dir = f"android{android_version}"
    if version_dir != expected_dir or scope_path.parent.name != expected_dir:
        fail(errors, f"version_dir must match scope location and android_version: {relative(scope_path, root)}")

    baseline = scope.get("baseline")
    target = scope.get("target")
    if not isinstance(baseline, dict) or not isinstance(target, dict):
        fail(errors, f"baseline and target must be objects: {relative(scope_path, root)}")
        return
    baseline_version = baseline.get("android_version")
    if baseline_version != android_version - 1:
        fail(errors, f"baseline android_version must be {android_version - 1}: {relative(scope_path, root)}")
    validate_tag(baseline.get("aosp_tag"), baseline_version, errors, "baseline.aosp_tag")
    validate_tag(target.get("aosp_tag"), android_version, errors, "target.aosp_tag")
    baseline_sdk = baseline.get("target_sdk")
    target_sdk = target.get("target_sdk")
    if not isinstance(target_sdk, int) or isinstance(target_sdk, bool) or target_sdk <= 0:
        fail(errors, f"target.target_sdk must be a positive integer: {relative(scope_path, root)}")
    if not isinstance(baseline_sdk, int) or isinstance(baseline_sdk, bool) or baseline_sdk != target_sdk - 1:
        fail(errors, f"baseline.target_sdk must immediately precede target.target_sdk: {relative(scope_path, root)}")
    if not isinstance(target.get("codename"), str) or not target["codename"]:
        fail(errors, f"target.codename must be a non-empty string: {relative(scope_path, root)}")

    if scope.get("default_reference_repository") != "platform/frameworks/base":
        fail(errors, f"default_reference_repository must be platform/frameworks/base: {relative(scope_path, root)}")
    refs_url = scope.get("official_refs_url")
    if not isinstance(refs_url, str) or not refs_url.startswith("https://android.googlesource.com/"):
        fail(errors, f"official_refs_url must be an Android Gitiles HTTPS URL: {relative(scope_path, root)}")

    documentation = scope.get("official_documentation")
    required_documentation = {"all_apps", "target_sdk", "compat_framework"}
    if not isinstance(documentation, dict) or not required_documentation <= set(documentation):
        fail(errors, f"official_documentation must define all_apps, target_sdk, and compat_framework: {relative(scope_path, root)}")
    else:
        for name, item in documentation.items():
            if not isinstance(item, dict):
                fail(errors, f"official_documentation.{name} must be an object")
                continue
            if item.get("availability") not in {"published", "unpublished"}:
                fail(errors, f"official_documentation.{name}.availability is invalid")
            if not isinstance(item.get("url"), str) or not item["url"].startswith("https://developer.android.com/"):
                fail(errors, f"official_documentation.{name}.url must be an official Android URL")
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(item.get("checked_at", ""))):
                fail(errors, f"official_documentation.{name}.checked_at must be YYYY-MM-DD")
            if item.get("availability") == "unpublished" and not item.get("fallback"):
                fail(errors, f"official_documentation.{name} needs a fallback while unpublished")

    expected_roots = {
        "reports": f"{version_dir}/behavior-changes",
        "summaries": f"{version_dir}/summaries",
        "intermediate_prompts": f"tmp/research-prompts/{version_dir}",
    }
    if scope.get("output_roots") != expected_roots:
        fail(errors, f"output_roots do not match {version_dir}: {relative(scope_path, root)}")

    scope_files = scope.get("scope_files")
    if not isinstance(scope_files, list) or not scope_files or not all(isinstance(item, str) for item in scope_files):
        fail(errors, f"scope_files must be a non-empty string list: {relative(scope_path, root)}")
    else:
        for item in scope_files:
            path = repository_path(root, item, errors, "scope_files entry")
            if path is not None:
                validate_scope_file_values(path, scope, root, errors)

    for name in ("AGENTS.md", "README.md", "GETTING_STARTED.md"):
        path = root / version_dir / name
        if not path.is_file() or "research-scope.json" not in path.read_text(encoding="utf-8"):
            fail(errors, f"scope metadata is not referenced from {relative(path, root)}")

    policy = scope.get("artifact_policy")
    if not isinstance(policy, dict):
        fail(errors, f"artifact_policy must be an object: {relative(scope_path, root)}")
    else:
        for name in ("separately_indexed_directories", "summary_exempt_directories", "summary_exempt_files"):
            values = policy.get(name)
            if not isinstance(values, list) or not all(isinstance(value, str) and value for value in values):
                fail(errors, f"artifact_policy.{name} must be a string list")


def parse_destination(raw: str) -> tuple[str, str]:
    value = raw.strip()
    if value.startswith("<") and ">" in value:
        value = value[1 : value.index(">")]
    else:
        value = value.split(maxsplit=1)[0]
    value = unquote(value)
    if "#" in value:
        target, fragment = value.split("#", 1)
    else:
        target, fragment = value, ""
    return target, fragment


def markdown_destinations(path: Path) -> tuple[list[tuple[str, str]], list[str]]:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"```.*?```|~~~.*?~~~", "", text, flags=re.DOTALL)
    text = re.sub(r"`[^`\n]*`", "", text)
    destinations = [parse_destination(raw) for raw in INLINE_LINK.findall(text)]
    definitions = {label.casefold(): target for label, target in REFERENCE_DEFINITION.findall(text)}
    unresolved: list[str] = []
    for label, reference in REFERENCE_USE.findall(text):
        key = (reference or label).casefold()
        if key.startswith("^"):
            continue
        target = definitions.get(key)
        if target is None:
            unresolved.append(reference or label)
        else:
            destinations.append(parse_destination(target))
    return destinations, unresolved


def github_slug(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    value = value.replace("`", "").strip().casefold()
    value = re.sub(r"[^\w\- ]", "", value)
    return value.replace(" ", "-")


def markdown_anchors(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    anchors = set(EXPLICIT_ANCHOR.findall(text))
    counts: dict[str, int] = {}
    for _, title in HEADING.findall(text):
        base = github_slug(title)
        count = counts.get(base, 0)
        anchors.add(base if count == 0 else f"{base}-{count}")
        counts[base] = count + 1
    return anchors


def local_target(markdown: Path, target: str, root: Path) -> Path | None:
    if not target:
        return markdown
    if urlsplit(target).scheme:
        return None
    candidate = root / target.lstrip("/") if target.startswith("/") else markdown.parent / target
    return candidate.resolve()


def linked_paths(markdown: Path, root: Path) -> set[Path]:
    destinations, _ = markdown_destinations(markdown)
    return {path for target, _ in destinations if (path := local_target(markdown, target, root)) is not None}


def validate_markdown_links(root: Path, errors: list[str]) -> None:
    anchor_cache: dict[Path, set[str]] = {}
    for markdown in root.rglob("*.md"):
        parts = markdown.relative_to(root).parts
        if parts[0] in {"frameworks-base", "tmp"} or ".git" in parts:
            continue
        destinations, unresolved = markdown_destinations(markdown)
        for label in unresolved:
            fail(errors, f"unresolved reference link: {relative(markdown, root)} -> [{label}]")
        for target_value, fragment in destinations:
            target = local_target(markdown, target_value, root)
            if target is None:
                continue
            try:
                target.relative_to(root.resolve())
            except ValueError:
                fail(errors, f"Markdown link escapes repository: {relative(markdown, root)} -> {target_value}")
                continue
            if not target.exists():
                fail(errors, f"broken Markdown link: {relative(markdown, root)} -> {target_value}")
                continue
            if fragment and target.is_file() and target.suffix.lower() == ".md":
                anchors = anchor_cache.setdefault(target, markdown_anchors(target))
                if fragment not in anchors:
                    fail(errors, f"broken Markdown anchor: {relative(markdown, root)} -> {target_value}#{fragment}")


def require_indexed(index: Path, files: list[Path], root: Path, errors: list[str]) -> None:
    if not index.is_file():
        fail(errors, f"index is missing: {relative(index, root)}")
        return
    links = linked_paths(index, root)
    for path in files:
        if path.resolve() not in links:
            fail(errors, f"artifact is not indexed: {relative(path, root)}")


def validate_android_artifacts(scope: dict, root: Path, errors: list[str]) -> None:
    if not scope or not isinstance(scope.get("artifact_policy"), dict):
        return
    version_root = root / scope["version_dir"]
    behavior_root = version_root / "behavior-changes"
    policy = scope["artifact_policy"]
    separate = set(policy["separately_indexed_directories"])
    for directory in separate | set(policy["summary_exempt_directories"]):
        if not (behavior_root / directory).is_dir():
            fail(errors, f"artifact policy directory does not exist: {scope['version_dir']}/behavior-changes/{directory}")
    for value in policy["summary_exempt_files"]:
        exempt = behavior_root / value
        if not exempt.is_file():
            fail(errors, f"summary exemption does not exist: {relative(exempt, root)}")
            continue
        exempt_relative = exempt.relative_to(behavior_root)
        unexpected_summary = version_root / "summaries" / exempt_relative.parent / f"{exempt.stem}-summary.md"
        if unexpected_summary.is_file():
            fail(errors, f"summary exemption hides an existing report-summary pair: {relative(exempt, root)}")
    excluded_names = {"README.md", "APPLICABILITY_CLASSIFICATION.md"}
    behavior_files = [
        path
        for path in behavior_root.rglob("*.md")
        if path.name not in excluded_names
        and not any(part in separate for part in path.relative_to(behavior_root).parts)
    ]
    require_indexed(behavior_root / "README.md", behavior_files, root, errors)
    for directory in separate:
        child_root = behavior_root / directory
        if child_root.is_dir():
            require_indexed(
                child_root / "README.md",
                [path for path in child_root.rglob("*.md") if path.name != "README.md"],
                root,
                errors,
            )

    summaries_root = version_root / "summaries"
    require_indexed(
        summaries_root / "README.md",
        [path for path in summaries_root.rglob("*.md") if path.name != "README.md"],
        root,
        errors,
    )
    exempt_directories = set(policy["summary_exempt_directories"])
    exempt_files = set(policy["summary_exempt_files"])
    for report in behavior_root.rglob("*.md"):
        report_relative = report.relative_to(behavior_root)
        if report.name in excluded_names or any(part in exempt_directories for part in report_relative.parts) or report_relative.as_posix() in exempt_files:
            continue
        expected = summaries_root / report_relative.parent / f"{report.stem}-summary.md"
        if not expected.is_file():
            fail(errors, f"primary report has no one-page summary: {relative(report, root)}")

    app_reports_root = version_root / "app-reports"
    if app_reports_root.is_dir():
        require_indexed(
            app_reports_root / "README.md",
            list(app_reports_root.glob("*/investigation-report.md")),
            root,
            errors,
        )


def validate_analysis_metadata(scope: dict, root: Path, errors: list[str]) -> None:
    path = repository_path(root, scope.get("analysis_metadata"), errors, "analysis_metadata")
    if path is None:
        return
    metadata = load_json(path, root, errors, "analysis metadata")
    if not metadata:
        return
    required = {
        "schema_version", "generated_at", "aosp_project", "official_remote_url", "checkout_path",
        "working_tree", "baseline", "target", "comparison_command", "dirty_risk",
    }
    if required - metadata.keys():
        fail(errors, f"analysis metadata keys are missing: {relative(path, root)}")
        return
    if metadata.get("schema_version") != 1 or metadata.get("aosp_project") != scope["default_reference_repository"]:
        fail(errors, f"analysis metadata identity does not match scope: {relative(path, root)}")
    try:
        generated_at = datetime.datetime.fromisoformat(str(metadata.get("generated_at", "")))
    except ValueError:
        fail(errors, f"analysis metadata generated_at is not ISO-8601: {relative(path, root)}")
    else:
        if generated_at.tzinfo is None:
            fail(errors, f"analysis metadata generated_at must include a timezone: {relative(path, root)}")
    expected_remote = f"https://android.googlesource.com/{scope['default_reference_repository']}"
    if str(metadata.get("official_remote_url", "")).removesuffix(".git") != expected_remote:
        fail(errors, f"analysis metadata remote is not official: {relative(path, root)}")
    if metadata.get("working_tree") not in {"clean", "dirty"}:
        fail(errors, f"analysis metadata working_tree is invalid: {relative(path, root)}")
    checkout = metadata.get("checkout_path")
    repository_path(root, checkout, errors, f"analysis metadata checkout_path in {relative(path, root)}")
    if metadata.get("working_tree") == "clean" and metadata.get("dirty_risk") != "none":
        fail(errors, f"clean analysis metadata must record dirty_risk as none: {relative(path, root)}")
    for side, scope_side in (("baseline", "baseline"), ("target", "target")):
        item = metadata.get(side)
        if not isinstance(item, dict) or item.get("tag") != scope[scope_side]["aosp_tag"]:
            fail(errors, f"analysis metadata {side} tag does not match scope: {relative(path, root)}")
        elif not re.fullmatch(r"[0-9a-f]{40}", str(item.get("resolved_commit", ""))):
            fail(errors, f"analysis metadata {side} commit is invalid: {relative(path, root)}")
    command = str(metadata.get("comparison_command", ""))
    if scope["baseline"]["aosp_tag"] not in command or scope["target"]["aosp_tag"] not in command:
        fail(errors, f"analysis metadata comparison command does not contain the scope tags: {relative(path, root)}")


def validate_build_artifacts(root: Path, errors: list[str]) -> None:
    build_root = root / "build-system"
    if not build_root.is_dir():
        fail(errors, "build-system directory is missing")
        return
    for area in sorted(path for path in build_root.iterdir() if path.is_dir() and path.name != "templates"):
        area_index = area / "README.md"
        if not area_index.is_file():
            fail(errors, f"Build System area has no README: {relative(area, root)}")
            continue
        for artifact_type in ("versions", "summaries", "checklists"):
            artifact_root = area / artifact_type
            if artifact_root.is_dir():
                require_indexed(
                    artifact_root / "README.md",
                    [path for path in artifact_root.rglob("*.md") if path.name != "README.md"],
                    root,
                    errors,
                )
        versions = area / "versions"
        if not versions.is_dir():
            continue
        for report in versions.glob("*-to-*.md"):
            lowered = report.stem.casefold()
            if any(channel in lowered for channel in ("preview", "alpha", "beta", "-rc")):
                continue
            summary = area / "summaries" / f"{report.stem}-summary.md"
            if not summary.is_file():
                fail(errors, f"stable Build System report has no summary: {relative(report, root)}")
            checklist_root = area / "checklists"
            if checklist_root.is_dir():
                checklist = checklist_root / f"{report.stem}-migration-checklist.md"
                if not checklist.is_file():
                    fail(errors, f"stable Build System report has no migration checklist: {relative(report, root)}")


def validate_agp_research_registry(root: Path, errors: list[str]) -> None:
    path = root / "build-system/agp/research-scope.json"
    registry = load_json(path, root, errors, "AGP research registry")
    if not registry:
        return
    if registry.get("schema_version") != 1:
        fail(errors, "unsupported AGP research registry schema_version")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(registry.get("checked_at", ""))):
        fail(errors, "AGP research registry checked_at must be YYYY-MM-DD")
    source = registry.get("official_channel_source")
    if not isinstance(source, str) or not source.startswith("https://developer.android.com/"):
        fail(errors, "AGP research registry official_channel_source must be an official Android URL")
    items = registry.get("items")
    current = registry.get("current")
    if not isinstance(items, list) or not items or not isinstance(current, dict):
        fail(errors, "AGP research registry must define non-empty items and current")
        return

    required = {
        "id", "purpose", "release_channel", "from_version", "to_version", "entry_point_url",
        "detail", "summary", "checklist", "research_status", "decision_status",
    }
    by_id: dict[str, dict] = {}
    identities: set[tuple[str, str, str]] = set()
    artifact_owners: dict[Path, str] = {}
    registered: set[Path] = set()
    for item in items:
        if not isinstance(item, dict) or required - item.keys():
            fail(errors, "AGP research registry item is malformed")
            continue
        item_id = item["id"]
        if not isinstance(item_id, str) or not item_id or item_id in by_id:
            fail(errors, f"AGP research registry item id is invalid or duplicated: {item_id}")
            continue
        by_id[item_id] = item
        target = item.get("to_version")
        match = re.match(r"^(\d+\.\d+)", str(target))
        if not match:
            fail(errors, f"AGP registry to_version is invalid: {item_id}")
            continue
        channel = item.get("release_channel")
        if channel not in {"stable", "alpha", "beta", "rc", "preview"}:
            fail(errors, f"AGP registry release_channel is invalid: {item_id}")
        channel_group = "stable" if channel == "stable" else "preview"
        identity = (match.group(1), channel_group, str(item.get("purpose")))
        if identity in identities:
            fail(errors, f"AGP research identity is duplicated: {identity}")
        identities.add(identity)
        if item.get("research_status") not in {"research_complete", "in_progress"}:
            fail(errors, f"AGP research_status is invalid: {item_id}")
        if item.get("decision_status") not in {"pending_human_decision", "decision_complete"}:
            fail(errors, f"AGP decision_status is invalid: {item_id}")
        if not str(item.get("entry_point_url", "")).startswith("https://developer.android.com/"):
            fail(errors, f"AGP entry_point_url is not official: {item_id}")
        for field in ("detail", "summary", "checklist"):
            value = item.get(field)
            if value is None:
                continue
            artifact = repository_path(root, value, errors, f"AGP registry {item_id}.{field}")
            if artifact is None:
                continue
            if not artifact.is_file():
                fail(errors, f"AGP registered artifact is missing: {value}")
            owner = artifact_owners.get(artifact)
            if owner is not None and owner != item_id:
                fail(errors, f"AGP artifact path is shared by {owner} and {item_id}: {value}")
            artifact_owners[artifact] = item_id
            registered.add(artifact)
        if item.get("purpose") == "version-diff" and channel == "stable":
            if item.get("summary") is None or item.get("checklist") is None:
                fail(errors, f"stable AGP version diff lacks summary or checklist in registry: {item_id}")
        if item.get("purpose") == "preview-watch" and (item.get("summary") is not None or item.get("checklist") is not None):
            fail(errors, f"AGP preview watch must not reuse stable summary/checklist paths: {item_id}")

    for name, expected_group in (("stable", "stable"), ("preview", "preview")):
        item_id = current.get(name)
        if not isinstance(item_id, str):
            fail(errors, f"AGP current.{name} must be a registry item id")
            continue
        item = by_id.get(item_id)
        if item is None:
            fail(errors, f"AGP current.{name} does not reference a registry item")
            continue
        actual_group = "stable" if item["release_channel"] == "stable" else "preview"
        if actual_group != expected_group or item["research_status"] != "research_complete":
            fail(errors, f"AGP current.{name} must reference a research_complete {expected_group} item")

    agp_root = root / "build-system/agp"
    actual = {
        artifact
        for directory in ("versions", "summaries", "checklists")
        for artifact in (agp_root / directory).glob("*.md")
        if artifact.name != "README.md"
    }
    for artifact in sorted(actual - registered):
        fail(errors, f"AGP artifact is not registered: {relative(artifact, root)}")
    readme = agp_root / "README.md"
    if not readme.is_file() or path.resolve() not in linked_paths(readme, root):
        fail(errors, "AGP README does not link the machine-readable research registry")
    elif all(isinstance(item_id, str) and item_id in by_id for item_id in current.values()):
        text = readme.read_text(encoding="utf-8")
        for item_id in current.values():
            version = by_id[item_id]["to_version"]
            if version not in text:
                fail(errors, f"AGP README does not show current registry version {version}")


def validate_operational_wording(root: Path, errors: list[str]) -> None:
    paths = list((root / "docs/workflow").glob("*.md"))
    paths += list((root / "docs/translation").glob("*.md"))
    paths += [root / "android17/AGENTS.md", root / "android17/behavior-changes/APPLICABILITY_CLASSIFICATION.md"]
    patterns = (
        re.compile(r"Android 17.{0,50}(?:tag|タグ).{0,30}(?:未公開|なく|存在しな|not available|unavailable)", re.I),
        re.compile(r"Android 17.{0,50}(?:tag|タグ).{0,30}(?:公開後|入手後|available)", re.I),
    )
    for path in paths:
        if not path.is_file():
            fail(errors, f"operational instruction is missing: {relative(path, root)}")
            continue
        text = path.read_text(encoding="utf-8")
        if any(pattern.search(text) for pattern in patterns):
            fail(errors, f"stale Android 17 pre-tag wording: {relative(path, root)}")


def validate_build_evidence_policy(root: Path, errors: list[str]) -> None:
    agents = root / "AGENTS.md"
    if not agents.is_file():
        fail(errors, "AGENTS.md is missing")
        return
    canonical = agents.read_text(encoding="utf-8")
    required_order = """1. Entry point release notes
2. Official Documentation
3. Compatibility Matrix
4. API Reference / Migration Guide
5. Issue Tracker
6. 実機・実プロジェクト検証
7. Blog"""
    if required_order not in canonical:
        fail(errors, "canonical Build System evidence hierarchy is missing from AGENTS.md")
    for item in (
        "build-system/AGENTS.md", "build-system/README.md", ".codex/prompts/investigation.md",
        ".codex/prompts/build-system-design.md", "docs/overview/SOURCES.md",
    ):
        path = root / item
        if not path.is_file():
            fail(errors, f"Build System evidence policy file is missing: {item}")
            continue
        text = path.read_text(encoding="utf-8")
        if "AGENTS.md" not in text:
            fail(errors, f"Build System evidence policy does not reference AGENTS.md: {item}")
        if "1. Official Documentation" in text or "1. Entry point release notes" in text:
            fail(errors, f"duplicate Build System evidence hierarchy: {item}")


def validate_templates(root: Path, scopes: list[dict], errors: list[str]) -> None:
    required_terms = ("Official remote URL", "Checkout path", "resolved commit", "Comparison command", "Dirty risk")
    for scope in scopes:
        path = root / scope["version_dir"] / "templates/customer-report-template.md"
        text = path.read_text(encoding="utf-8")
        for term in required_terms:
            if term not in text:
                fail(errors, f"AOSP provenance field {term!r} is missing from {relative(path, root)}")


def validate_ignored_workspaces(root: Path, errors: list[str]) -> None:
    path = root / ".gitignore"
    if not path.is_file():
        fail(errors, ".gitignore is missing")
        return
    ignore = path.read_text(encoding="utf-8")
    for entry in ("frameworks-base/", "tmp/aosp-checkouts/", "tmp/research-prompts/"):
        if entry not in ignore:
            fail(errors, f"temporary workspace is not ignored: {entry}")


def fetch_url(url: str) -> tuple[int, str]:
    request = Request(url, headers={"User-Agent": "android-platform-research-validator/1.0"})
    try:
        with urlopen(request, timeout=20) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")


def validate_online_scope(scope: dict, scope_path: Path, root: Path, errors: list[str]) -> None:
    refs_url = scope["official_refs_url"]
    separator = "&" if "?" in refs_url else "?"
    try:
        status, body = fetch_url(f"{refs_url}{separator}format=TEXT")
    except (OSError, URLError) as exc:
        fail(errors, f"official refs cannot be checked for {relative(scope_path, root)}: {exc}")
        return
    if status != 200:
        fail(errors, f"official refs returned HTTP {status}: {refs_url}")
    else:
        for side in ("baseline", "target"):
            android_version = scope[side].get("android_version", scope["android_version"])
            revisions = [int(value) for value in re.findall(rf"android-{android_version}\.0\.0_r([1-9]\d*)", body)]
            if not revisions:
                fail(errors, f"no standard Android {android_version} tags found at {refs_url}")
                continue
            expected = f"android-{android_version}.0.0_r{max(revisions)}"
            if scope[side]["aosp_tag"] != expected:
                fail(errors, f"stale {side} tag in {relative(scope_path, root)}: expected {expected}")

    for name, item in scope["official_documentation"].items():
        try:
            status, _ = fetch_url(item["url"])
        except (OSError, URLError) as exc:
            fail(errors, f"official documentation cannot be checked ({name}): {exc}")
            continue
        if item["availability"] == "published" and not 200 <= status < 400:
            fail(errors, f"published official documentation returned HTTP {status}: {item['url']}")
        if item["availability"] == "unpublished" and status != 404:
            fail(errors, f"documentation availability is stale ({name} returned HTTP {status}): {item['url']}")


def validate_online_agp_registry(root: Path, errors: list[str]) -> None:
    path = root / "build-system/agp/research-scope.json"
    registry = load_json(path, root, errors, "AGP research registry")
    if not registry:
        return
    try:
        status, body = fetch_url(registry["official_channel_source"])
    except (KeyError, OSError, URLError) as exc:
        fail(errors, f"official AGP channel source cannot be checked: {exc}")
        return
    if status != 200:
        fail(errors, f"official AGP channel source returned HTTP {status}: {registry['official_channel_source']}")
        return
    plain = html.unescape(re.sub(r"<[^>]+>", " ", body))
    plain = re.sub(r"\s+", " ", plain)
    patterns = {
        "stable": re.compile(r"Current Release\s+(\d+\.\d+\.\d+(?:-(?:alpha|beta|rc)\d+)?)", re.I),
        "preview": re.compile(r"Preview Releases?\s+(\d+\.\d+\.\d+(?:-(?:alpha|beta|rc)\d+)?)", re.I),
    }
    items = {item.get("id"): item for item in registry.get("items", []) if isinstance(item, dict)}
    for name, pattern in patterns.items():
        match = pattern.search(plain)
        if not match:
            fail(errors, f"official AGP {name} version cannot be parsed from {registry['official_channel_source']}")
            continue
        item = items.get(registry.get("current", {}).get(name))
        if item is None or item.get("to_version") != match.group(1):
            fail(errors, f"stale AGP current.{name}: official {match.group(1)}")


def scope_is_usable(scope: dict) -> bool:
    policy = scope.get("artifact_policy")
    return (
        REQUIRED_SCOPE_KEYS <= scope.keys()
        and isinstance(scope.get("version_dir"), str)
        and isinstance(scope.get("baseline"), dict)
        and isinstance(scope.get("target"), dict)
        and isinstance(scope.get("official_documentation"), dict)
        and isinstance(policy, dict)
        and all(isinstance(policy.get(name), list) for name in (
            "separately_indexed_directories", "summary_exempt_directories", "summary_exempt_files"
        ))
    )


def validate_repository(root: Path, online: bool = False) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    scope_paths = discover_scope_files(root)
    if not scope_paths:
        fail(errors, "no android*/research-scope.json files were found")
        return errors
    scopes: list[dict] = []
    valid_scopes: list[dict] = []
    for path in scope_paths:
        scope = load_json(path, root, errors, "scope metadata")
        scopes.append(scope)
        error_count = len(errors)
        validate_scope(scope, path, root, errors)
        if len(errors) == error_count and scope_is_usable(scope):
            valid_scopes.append(scope)
            validate_android_artifacts(scope, root, errors)
            validate_analysis_metadata(scope, root, errors)
            if online:
                validate_online_scope(scope, path, root, errors)
    validate_markdown_links(root, errors)
    validate_build_artifacts(root, errors)
    agp_error_count = len(errors)
    validate_agp_research_registry(root, errors)
    if online and len(errors) == agp_error_count:
        validate_online_agp_registry(root, errors)
    validate_operational_wording(root, errors)
    validate_build_evidence_policy(root, errors)
    validate_templates(root, valid_scopes, errors)
    validate_ignored_workspaces(root, errors)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="repository root (used by tests and fixtures)")
    parser.add_argument("--online", action="store_true", help="also verify official refs and documentation availability")
    args = parser.parse_args(argv)
    errors = validate_repository(args.root, online=args.online)
    if errors:
        print("Repository structure validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    suffix = " (including online freshness checks)" if args.online else ""
    print(f"Repository structure validation passed{suffix}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

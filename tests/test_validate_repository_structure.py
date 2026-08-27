from __future__ import annotations

import datetime
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_repository_structure.py"
SPEC = importlib.util.spec_from_file_location("repository_validator", MODULE_PATH)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class RepositoryValidatorTest(unittest.TestCase):
    def test_implementation_examples_must_use_dedicated_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            behavior_root = root / "android16" / "behavior-changes"
            misplaced = behavior_root / "case-guides" / "sample-implementation-examples.md"
            misplaced.parent.mkdir(parents=True)
            misplaced.write_text("# Misplaced\n", encoding="utf-8")

            errors: list[str] = []
            validator.validate_implementation_example_locations(behavior_root, root, errors)
            self.assertEqual(
                errors,
                [
                    "implementation example must be under behavior-changes/implementation-examples: "
                    "android16/behavior-changes/case-guides/sample-implementation-examples.md"
                ],
            )

            correct = behavior_root / "implementation-examples" / misplaced.name
            correct.parent.mkdir()
            misplaced.rename(correct)
            errors.clear()
            validator.validate_implementation_example_locations(behavior_root, root, errors)
            self.assertEqual(errors, [])

    def test_checked_date_must_be_real_and_not_future(self) -> None:
        errors: list[str] = []
        validator.validate_checked_date("2026-02-30", errors, "checked_at")
        self.assertEqual(errors, ["checked_at must be a valid YYYY-MM-DD date"])
        errors.clear()
        validator.validate_checked_date("20260820", errors, "checked_at")
        self.assertEqual(errors, ["checked_at must be a valid YYYY-MM-DD date"])
        errors.clear()
        future = f"{datetime.date.today().year + 1}-01-01"
        validator.validate_checked_date(future, errors, "checked_at")
        self.assertEqual(errors, ["checked_at cannot be in the future"])

    def test_agp_version_order_accepts_patch_and_release_line_updates(self) -> None:
        patch_from = validator.parse_agp_version("9.3.0")
        patch_to = validator.parse_agp_version("9.3.1")
        line_from = validator.parse_agp_version("8.7.x")
        line_to = validator.parse_agp_version("9.3.1")
        alpha = validator.parse_agp_version("9.4.0-alpha02")
        rc = validator.parse_agp_version("9.4.0-rc01")
        stable = validator.parse_agp_version("9.4.0")
        self.assertIsNotNone(patch_from)
        self.assertIsNotNone(patch_to)
        self.assertIsNotNone(line_from)
        self.assertIsNotNone(line_to)
        self.assertIsNotNone(alpha)
        self.assertIsNotNone(rc)
        self.assertIsNotNone(stable)
        self.assertTrue(validator.agp_version_is_earlier(patch_from, patch_to))
        self.assertTrue(validator.agp_version_is_earlier(line_from, line_to))
        self.assertTrue(validator.agp_version_is_earlier(alpha, rc))
        self.assertTrue(validator.agp_version_is_earlier(rc, stable))
        self.assertFalse(validator.agp_version_is_earlier(line_to, line_to))

    def test_scope_discovery_is_not_version_hardcoded(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for version in (16, 17, 18):
                path = root / f"android{version}" / "research-scope.json"
                path.parent.mkdir()
                path.write_text("{}\n", encoding="utf-8")
            self.assertEqual(
                [path.parent.name for path in validator.discover_scope_files(root)],
                ["android16", "android17", "android18"],
            )

    def test_malformed_scope_is_reported_without_crashing_repository_validation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scope_path = root / "android18" / "research-scope.json"
            scope_path.parent.mkdir()
            scope_path.write_text('{"schema_version": 1}\n', encoding="utf-8")
            errors = validator.validate_repository(root)
            self.assertTrue(any("scope keys are missing" in error for error in errors), errors)

    def test_target_sdk_must_be_explicit_and_cannot_match_tag_revision(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            version_root = root / "android16"
            version_root.mkdir()
            scope = self.scope(version_root)
            for name in ("AGENTS.md", "README.md", "GETTING_STARTED.md"):
                (version_root / name).write_text(
                    "research-scope.json android-15.0.0_r36 android-16.0.0_r4\n",
                    encoding="utf-8",
                )
            scope_file = version_root / "scope.md"
            scope_file.write_text(
                "android-15.0.0_r36 android-16.0.0_r4\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            validator.validate_scope(scope, version_root / "research-scope.json", root, errors)
            self.assertTrue(any("targetSdkVersion 36 is missing" in error for error in errors), errors)

    def test_index_requires_a_real_markdown_link(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            index = root / "README.md"
            artifact = root / "report.md"
            artifact.write_text("# Report\n", encoding="utf-8")
            index.write_text("report.md is mentioned but not linked.\n", encoding="utf-8")
            errors: list[str] = []
            validator.require_indexed(index, [artifact], root, errors)
            self.assertEqual(errors, ["artifact is not indexed: report.md"])
            index.write_text("[Report](report.md)\n", encoding="utf-8")
            errors.clear()
            validator.require_indexed(index, [artifact], root, errors)
            self.assertEqual(errors, [])

    def test_reference_links_and_anchors_are_validated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.md"
            target.write_text("# 日本語 Heading\n", encoding="utf-8")
            source = root / "source.md"
            source.write_text(
                "[Target][doc]\n\n[doc]: target.md#日本語-heading\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            validator.validate_markdown_links(root, errors)
            self.assertEqual(errors, [])
            source.write_text("[Target](target.md#missing)\n", encoding="utf-8")
            validator.validate_markdown_links(root, errors)
            self.assertTrue(any("broken Markdown anchor" in error for error in errors), errors)
            errors.clear()
            source.write_text("![Missing image](missing.png)\n", encoding="utf-8")
            validator.validate_markdown_links(root, errors)
            self.assertTrue(any("broken Markdown link" in error for error in errors), errors)

    def test_stable_build_report_requires_summary_and_checklist(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            area = root / "build-system" / "tool"
            for child in ("versions", "summaries", "checklists"):
                (area / child).mkdir(parents=True, exist_ok=True)
                (area / child / "README.md").write_text("# Index\n", encoding="utf-8")
            (area / "README.md").write_text("# Tool\n", encoding="utf-8")
            report = area / "versions" / "tool-1.0-to-2.0.md"
            report.write_text("# Diff\n", encoding="utf-8")
            (area / "versions" / "README.md").write_text(
                "[Diff](tool-1.0-to-2.0.md)\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            validator.validate_build_artifacts(root, errors)
            self.assertTrue(any("has no summary" in error for error in errors), errors)
            self.assertTrue(any("has no migration checklist" in error for error in errors), errors)

    def test_android_primary_report_requires_revalidation_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            version_root = root / "android16"
            report_root = version_root / "behavior-changes" / "target" / "category"
            summary_root = version_root / "summaries" / "target" / "category"
            report_root.mkdir(parents=True)
            summary_root.mkdir(parents=True)
            report = report_root / "change.md"
            report.write_text(
                """# Change

Investigation Date
Original Documentation
https://developer.android.com/about/versions/16/behavior-changes-16#change
AOSP Evidence Workspaces
Official remote URL
Checkout path
resolved commit
Comparison command
Dirty risk
android-15.0.0_r36
android-16.0.0_r4
Source Context Reviewed
Diff Interpretation
Facts
Observations
Hypotheses
Conclusions
Human Decision
""",
                encoding="utf-8",
            )
            companion = report_root / "guide.md"
            companion.write_text("# Guide\n", encoding="utf-8")
            behavior_index = version_root / "behavior-changes" / "README.md"
            behavior_index.write_text(
                "[Change](target/category/change.md)\n[Guide](target/category/guide.md)\n",
                encoding="utf-8",
            )
            summary = summary_root / "change-summary.md"
            summary.write_text("# Summary\n\n主レポート\n\n## 再検証記録\n", encoding="utf-8")
            (version_root / "summaries" / "README.md").write_text(
                "[Summary](target/category/change-summary.md)\n",
                encoding="utf-8",
            )
            scope = self.scope(version_root)
            scope["artifact_policy"]["summary_exempt_files"] = ["target/category/guide.md"]

            errors: list[str] = []
            validator.validate_android_artifacts(scope, root, errors)
            self.assertEqual(errors, [])

            report.write_text(
                report.read_text(encoding="utf-8").replace("Dirty risk\n", ""),
                encoding="utf-8",
            )
            validator.validate_android_artifacts(scope, root, errors)
            self.assertTrue(any("'Dirty risk' is missing" in error for error in errors), errors)

    def test_agp_registry_rejects_stable_preview_path_collision(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            agp = root / "build-system" / "agp"
            for child in ("versions", "summaries", "checklists"):
                (agp / child).mkdir(parents=True, exist_ok=True)
            shared = agp / "versions" / "shared.md"
            shared.write_text("# Shared\n", encoding="utf-8")
            (agp / "README.md").write_text(
                "[Registry](research-scope.json) stable 1.0.0 preview 2.0.0-alpha01 2026-08-19\n",
                encoding="utf-8",
            )
            base = {
                "detail": "build-system/agp/versions/shared.md",
                "summary": None,
                "checklist": None,
                "research_status": "in_progress",
                "decision_status": "pending_human_decision",
            }
            registry = {
                "schema_version": 1,
                "checked_at": "2026-08-19",
                "official_channel_source": "https://developer.android.com/reference/tools/gradle-api",
                "current": {"stable": "stable", "preview": "preview"},
                "items": [
                    {
                        **base,
                        "id": "stable",
                        "purpose": "single-version-inventory",
                        "release_channel": "stable",
                        "from_version": None,
                        "to_version": "1.0.0",
                        "entry_point_url": "https://developer.android.com/build/releases/agp-1-0-0-release-notes",
                    },
                    {
                        **base,
                        "id": "preview",
                        "purpose": "preview-watch",
                        "release_channel": "alpha",
                        "from_version": "1.0.0",
                        "to_version": "2.0.0-alpha01",
                        "entry_point_url": "https://developer.android.com/build/releases/agp-2-0-0-release-notes",
                    },
                ],
            }
            (agp / "research-scope.json").write_text(json.dumps(registry), encoding="utf-8")
            errors: list[str] = []
            validator.validate_agp_research_registry(root, errors)
            self.assertTrue(any("artifact path is shared" in error for error in errors), errors)

    def test_online_check_uses_highest_standard_tag(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scope_path = root / "android16" / "research-scope.json"
            scope_path.parent.mkdir()
            scope = self.scope(scope_path.parent)

            def fake_fetch(url: str) -> tuple[int, str]:
                if "android.googlesource.com" in url:
                    return 200, "refs/tags/android-15.0.0_r36\nrefs/tags/android-16.0.0_r4\n"
                return 200, "published"

            errors: list[str] = []
            with mock.patch.object(validator, "fetch_url", side_effect=fake_fetch):
                validator.validate_online_scope(scope, scope_path, root, errors)
            self.assertEqual(errors, [])

    def test_online_agp_check_parses_current_and_preview_channels(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            agp = root / "build-system" / "agp"
            agp.mkdir(parents=True)
            registry = {
                "official_channel_source": "https://developer.android.com/reference/tools/gradle-api",
                "current": {"stable": "stable", "preview": "preview"},
                "items": [
                    {"id": "stable", "to_version": "9.3.1"},
                    {"id": "preview", "to_version": "9.4.0-rc01"},
                ],
            }
            (agp / "research-scope.json").write_text(json.dumps(registry), encoding="utf-8")
            page = "<div>Current Release</div><div>9.3.1</div><div>Preview Releases</div><div>9.4.0-rc01</div>"
            errors: list[str] = []
            with mock.patch.object(validator, "fetch_url", return_value=(200, page)):
                validator.validate_online_agp_registry(root, errors)
            self.assertEqual(errors, [])

    @staticmethod
    def scope(version_root: Path) -> dict:
        version_dir = version_root.name
        return {
            "schema_version": 1,
            "android_version": 16,
            "version_dir": version_dir,
            "baseline": {
                "android_version": 15,
                "aosp_tag": "android-15.0.0_r36",
                "target_sdk": 35,
            },
            "target": {
                "aosp_tag": "android-16.0.0_r4",
                "target_sdk": 36,
                "codename": "BAKLAVA",
            },
            "default_reference_repository": "platform/frameworks/base",
            "official_refs_url": "https://android.googlesource.com/platform/frameworks/base/+refs",
            "official_documentation": {
                name: {
                    "url": f"https://developer.android.com/{name}",
                    "availability": "published",
                    "checked_at": "2026-08-19",
                }
                for name in ("all_apps", "target_sdk", "compat_framework")
            },
            "output_roots": {
                "reports": f"{version_dir}/behavior-changes",
                "summaries": f"{version_dir}/summaries",
                "intermediate_prompts": f"tmp/research-prompts/{version_dir}",
            },
            "scope_files": [f"{version_dir}/scope.md"],
            "artifact_policy": {
                "separately_indexed_directories": [],
                "summary_exempt_directories": [],
                "summary_exempt_files": [],
            },
            "analysis_metadata": f"{version_dir}/analysis/metadata.json",
        }


if __name__ == "__main__":
    unittest.main()

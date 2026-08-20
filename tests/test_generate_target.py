from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "generate_target.sh"


class GenerateTargetTest(unittest.TestCase):
    def run_generator(self, root: Path, **overrides: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment.update(overrides)
        return subprocess.run(
            ["bash", str(SCRIPT)],
            cwd=root,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def write_scope(self, root: Path) -> None:
        version_root = root / "android18"
        version_root.mkdir()
        scope = {
            "version_dir": "android18",
            "baseline": {"aosp_tag": "android-17.0.0_r1"},
            "target": {"aosp_tag": "android-18.0.0_r1", "codename": "DESSERT"},
            "default_reference_repository": "platform/frameworks/base",
        }
        (version_root / "research-scope.json").write_text(json.dumps(scope), encoding="utf-8")

    def test_rejects_version_directory_outside_root_convention(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_generator(Path(directory), VERSION_DIR="../android18")
        self.assertEqual(result.returncode, 2)
        self.assertIn("VERSION_DIR must be", result.stderr)

    def test_rejects_scope_override_before_using_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_scope(root)
            result = self.run_generator(
                root,
                VERSION_DIR="android18",
                OLD_TAG="android-17.0.0_r99",
            )
        self.assertEqual(result.returncode, 2)
        self.assertIn("update the scope instead of overriding", result.stderr)

    def test_rejects_symlinked_analysis_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_scope(root)
            sink = root / "outside-analysis"
            sink.mkdir()
            (root / "android18" / "analysis").symlink_to(sink, target_is_directory=True)
            result = self.run_generator(root, VERSION_DIR="android18")
        self.assertEqual(result.returncode, 2)
        self.assertIn("must not be a symbolic link", result.stderr)

    def test_generates_tag_pinned_analysis_and_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_scope(root)
            checkout = root / "aosp"
            subprocess.run(["git", "init", "-q", str(checkout)], check=True)
            tracked = checkout / "core" / "java" / "android" / "app" / "Tracked.java"
            tracked.parent.mkdir(parents=True)
            tracked.write_text("baseline\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(checkout), "add", "."], check=True)
            commit = [
                "git", "-C", str(checkout), "-c", "user.name=Test", "-c",
                "user.email=test@example.com", "commit", "-qm", "baseline",
            ]
            subprocess.run(commit, check=True)
            subprocess.run(["git", "-C", str(checkout), "tag", "android-17.0.0_r1"], check=True)
            tracked.write_text("target\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(checkout), "add", "."], check=True)
            subprocess.run([*commit[:-1], "target"], check=True)
            subprocess.run(["git", "-C", str(checkout), "tag", "android-18.0.0_r1"], check=True)
            subprocess.run(
                [
                    "git", "-C", str(checkout), "remote", "add", "origin",
                    "https://android.googlesource.com/platform/frameworks/base",
                ],
                check=True,
            )

            result = self.run_generator(root, VERSION_DIR="android18", AOSP_DIR="aosp")
            self.assertEqual(result.returncode, 0, result.stderr)
            analysis = root / "android18" / "analysis"
            metadata = json.loads((analysis / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["baseline"]["tag"], "android-17.0.0_r1")
            self.assertEqual(metadata["target"]["tag"], "android-18.0.0_r1")
            self.assertEqual(metadata["working_tree"], "clean")
            baseline_commit = subprocess.run(
                ["git", "-C", str(checkout), "rev-list", "-n", "1", "android-17.0.0_r1"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.strip()
            target_commit = subprocess.run(
                ["git", "-C", str(checkout), "rev-list", "-n", "1", "android-18.0.0_r1"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.strip()
            self.assertEqual(metadata["baseline"]["resolved_commit"], baseline_commit)
            self.assertEqual(metadata["target"]["resolved_commit"], target_commit)
            self.assertEqual(
                (analysis / "changed_files.txt").read_text(encoding="utf-8"),
                "core/java/android/app/Tracked.java\n",
            )

            tracked.write_text("uncommitted local change\n", encoding="utf-8")
            dirty_result = self.run_generator(root, VERSION_DIR="android18", AOSP_DIR="aosp")
            self.assertEqual(dirty_result.returncode, 0, dirty_result.stderr)
            dirty_metadata = json.loads((analysis / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(dirty_metadata["working_tree"], "dirty")
            self.assertIn("explicit tag objects", dirty_metadata["dirty_risk"])
            self.assertEqual(
                (analysis / "changed_files.txt").read_text(encoding="utf-8"),
                "core/java/android/app/Tracked.java\n",
            )
            self.assertEqual(
                (analysis / "app.txt").read_text(encoding="utf-8"),
                "core/java/android/app/Tracked.java\n",
            )


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env bash
set -euo pipefail

AOSP_DIR="${AOSP_DIR:-frameworks-base}"
VERSION_DIR="${VERSION_DIR:-}"
OLD_TAG="${OLD_TAG:-}"
NEW_TAG="${NEW_TAG:-}"
TARGET_CODENAME="${TARGET_CODENAME:-<target-codename>}"

usage() {
  cat <<'USAGE'
Usage:
  VERSION_DIR=<android-version-dir> OLD_TAG=<from-tag> NEW_TAG=<to-tag> TARGET_CODENAME=<codename> scripts/generate_target.sh

Optional:
  AOSP_DIR=frameworks-base
USAGE
}

if [[ -z "$VERSION_DIR" || -z "$OLD_TAG" || -z "$NEW_TAG" ]]; then
  usage >&2
  exit 2
fi

ANALYSIS_DIR="$VERSION_DIR/analysis"

if [[ ! -d "$AOSP_DIR/.git" ]]; then
  echo "AOSP checkout not found: $AOSP_DIR" >&2
  exit 1
fi

if ! git -C "$AOSP_DIR" rev-parse --verify --quiet "$OLD_TAG" >/dev/null; then
  echo "Missing OLD_TAG in $AOSP_DIR: $OLD_TAG" >&2
  exit 1
fi

if ! git -C "$AOSP_DIR" rev-parse --verify --quiet "$NEW_TAG" >/dev/null; then
  echo "Missing NEW_TAG in $AOSP_DIR: $NEW_TAG" >&2
  exit 1
fi

mkdir -p "$ANALYSIS_DIR"

git -C "$AOSP_DIR" diff --no-renames --name-only "$OLD_TAG" "$NEW_TAG" \
  > "$ANALYSIS_DIR/changed_files.txt"

grep -Ev '(^|/)(OWNERS|OWNERS\.md|TEST_MAPPING|lint-baseline\.xml)$|(^|/)(tests?|apct-tests|ravenwood/tests|core/tests|libs/.*/tests?)(/|$)' \
  "$ANALYSIS_DIR/changed_files.txt" > "$ANALYSIS_DIR/relevant_changed_files.txt" || true

grep -E '(^|/)core/api/' "$ANALYSIS_DIR/relevant_changed_files.txt" \
  > "$ANALYSIS_DIR/api.txt" || true

grep -E '(^|/)core/java/android/app/' "$ANALYSIS_DIR/relevant_changed_files.txt" \
  > "$ANALYSIS_DIR/app.txt" || true

grep -E '(^|/)core/java/android/(os|content|permission|provider|security)/' "$ANALYSIS_DIR/relevant_changed_files.txt" \
  > "$ANALYSIS_DIR/platform.txt" || true

grep -E '(^|/)core/java/android/(view|window|widget)/' "$ANALYSIS_DIR/relevant_changed_files.txt" \
  > "$ANALYSIS_DIR/ui.txt" || true

grep -E '(^|/)core/java/android/companion/' "$ANALYSIS_DIR/relevant_changed_files.txt" \
  > "$ANALYSIS_DIR/companion.txt" || true

grep -E '(^|/)core/java/android/hardware/' "$ANALYSIS_DIR/relevant_changed_files.txt" \
  > "$ANALYSIS_DIR/hardware.txt" || true

grep -E '(^|/)apex/jobscheduler/' "$ANALYSIS_DIR/relevant_changed_files.txt" \
  > "$ANALYSIS_DIR/jobscheduler.txt" || true

grep -E '(^|/)(core/java|services/core|apex|packages/modules)/' "$ANALYSIS_DIR/relevant_changed_files.txt" \
  > "$ANALYSIS_DIR/runtime_candidates.txt" || true

grep -E '(^|/)(compat|app_compat|platform_compat|AppCompat|CompatChanges|ChangeId)$|(^|/).*compat.*\.(java|kt|xml)$' "$ANALYSIS_DIR/relevant_changed_files.txt" \
  > "$ANALYSIS_DIR/compat_candidates.txt" || true

grep -E '(^|/)(core/api/current.txt|core/api/system-current.txt|core/api/test-current.txt|api/current.txt|api/system-current.txt|api/module-lib-current.txt)$' "$ANALYSIS_DIR/relevant_changed_files.txt" \
  > "$ANALYSIS_DIR/api_surface_candidates.txt" || true

{
  cat "$ANALYSIS_DIR/api.txt"
  cat "$ANALYSIS_DIR/api_surface_candidates.txt"
  cat "$ANALYSIS_DIR/app.txt"
  cat "$ANALYSIS_DIR/companion.txt"
  cat "$ANALYSIS_DIR/compat_candidates.txt"
  cat "$ANALYSIS_DIR/hardware.txt"
  cat "$ANALYSIS_DIR/jobscheduler.txt"
  cat "$ANALYSIS_DIR/platform.txt"
  cat "$ANALYSIS_DIR/runtime_candidates.txt"
  cat "$ANALYSIS_DIR/ui.txt"
} | sort -u > "$ANALYSIS_DIR/target.txt"

echo
echo "===== Summary ====="
for file in "$ANALYSIS_DIR"/*.txt; do
  printf "%-25s %5d\n" "$(basename "$file")" "$(wc -l < "$file")"
done

echo
echo "===== Applicability gate search hints ====="
echo "Run these against files listed in runtime_candidates.txt and compat_candidates.txt:"
echo "git -C \"$AOSP_DIR\" grep -n \"targetSdkVersion\\|ApplicationInfo.targetSdkVersion\\|Build.VERSION_CODES.$TARGET_CODENAME\\|CompatChanges.isChangeEnabled\\|@ChangeId\\|@EnabledAfter\\|@EnabledSince\" \"$NEW_TAG\" -- <file-or-dir>"

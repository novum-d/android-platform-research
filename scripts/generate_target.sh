#!/usr/bin/env bash
set -euo pipefail

AOSP_DIR="${AOSP_DIR:-frameworks-base}"
VERSION_DIR="${VERSION_DIR:-}"
REQUESTED_OLD_TAG="${OLD_TAG:-}"
REQUESTED_NEW_TAG="${NEW_TAG:-}"
REQUESTED_TARGET_CODENAME="${TARGET_CODENAME:-}"

usage() {
  cat <<'USAGE'
Usage:
  VERSION_DIR=<android-version-dir> scripts/generate_target.sh

Optional:
  AOSP_DIR=frameworks-base

Tags and codename are read from:
  <android-version-dir>/research-scope.json

OLD_TAG, NEW_TAG, and TARGET_CODENAME may be repeated only when they equal the
scope. Historical comparisons should use explicit git commands and must not
overwrite the current generated analysis.
USAGE
}

if [[ -z "$VERSION_DIR" ]]; then
  usage >&2
  exit 2
fi

if [[ ! "$VERSION_DIR" =~ ^android[1-9][0-9]*$ ]]; then
  echo "VERSION_DIR must be a repository-root Android version directory such as android17: $VERSION_DIR" >&2
  exit 2
fi

if [[ -L "$VERSION_DIR" ]]; then
  echo "VERSION_DIR must not be a symbolic link: $VERSION_DIR" >&2
  exit 2
fi

SCOPE_FILE="$VERSION_DIR/research-scope.json"

if [[ ! -f "$SCOPE_FILE" ]]; then
  echo "Missing scope metadata: $SCOPE_FILE" >&2
  usage >&2
  exit 2
fi

IFS=$'\t' read -r SCOPE_VERSION OLD_TAG NEW_TAG TARGET_CODENAME AOSP_PROJECT < <(
  python3 -c 'import json,sys; s=json.load(open(sys.argv[1])); print(s["version_dir"], s["baseline"]["aosp_tag"], s["target"]["aosp_tag"], s["target"]["codename"], s["default_reference_repository"], sep="\t")' "$SCOPE_FILE"
)

if [[ "$SCOPE_VERSION" != "$VERSION_DIR" ]]; then
  echo "Scope version_dir mismatch: expected $VERSION_DIR, found $SCOPE_VERSION" >&2
  exit 2
fi

check_override() {
  local name="$1"
  local requested="$2"
  local scoped="$3"
  if [[ -n "$requested" && "$requested" != "$scoped" ]]; then
    echo "$name differs from $SCOPE_FILE; update the scope instead of overriding generated analysis" >&2
    exit 2
  fi
}

check_override OLD_TAG "$REQUESTED_OLD_TAG" "$OLD_TAG"
check_override NEW_TAG "$REQUESTED_NEW_TAG" "$NEW_TAG"
check_override TARGET_CODENAME "$REQUESTED_TARGET_CODENAME" "$TARGET_CODENAME"

if [[ "$AOSP_DIR" = /* || "$AOSP_DIR" == *".."* ]]; then
  echo "AOSP_DIR must be a repository-relative evidence workspace: $AOSP_DIR" >&2
  exit 2
fi

ANALYSIS_DIR="$VERSION_DIR/analysis"

if [[ -L "$ANALYSIS_DIR" ]]; then
  echo "Analysis output directory must not be a symbolic link: $ANALYSIS_DIR" >&2
  exit 2
fi

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

AOSP_REMOTE="$(git -C "$AOSP_DIR" remote get-url origin)"
EXPECTED_REMOTE="https://android.googlesource.com/$AOSP_PROJECT"
if [[ "${AOSP_REMOTE%.git}" != "${EXPECTED_REMOTE%.git}" ]]; then
  echo "Unexpected AOSP origin: $AOSP_REMOTE (expected $EXPECTED_REMOTE)" >&2
  exit 1
fi

OLD_COMMIT="$(git -C "$AOSP_DIR" rev-list -n 1 "$OLD_TAG")"
NEW_COMMIT="$(git -C "$AOSP_DIR" rev-list -n 1 "$NEW_TAG")"
if [[ -n "$(git -C "$AOSP_DIR" status --short)" ]]; then
  WORKING_TREE="dirty"
  DIRTY_RISK="Generated files use explicit tag objects; local working-tree changes were not used."
else
  WORKING_TREE="clean"
  DIRTY_RISK="none"
fi

mkdir -p "$ANALYSIS_DIR"

python3 - "$ANALYSIS_DIR/metadata.json" "$AOSP_PROJECT" "$AOSP_REMOTE" "$AOSP_DIR" "$WORKING_TREE" "$OLD_TAG" "$OLD_COMMIT" "$NEW_TAG" "$NEW_COMMIT" "$DIRTY_RISK" <<'PY'
import datetime
import json
import os
import sys

(
    output,
    project,
    remote,
    checkout,
    working_tree,
    old_tag,
    old_commit,
    new_tag,
    new_commit,
    dirty_risk,
) = sys.argv[1:]
data = {
    "schema_version": 1,
    "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    "aosp_project": project,
    "official_remote_url": remote,
    "checkout_path": checkout,
    "working_tree": working_tree,
    "baseline": {"tag": old_tag, "resolved_commit": old_commit},
    "target": {"tag": new_tag, "resolved_commit": new_commit},
    "comparison_command": f"git -C {checkout} diff --no-renames --name-only {old_tag} {new_tag}",
    "dirty_risk": dirty_risk,
}
temporary = f"{output}.tmp"
with open(temporary, "w", encoding="utf-8") as stream:
    json.dump(data, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
os.replace(temporary, output)
PY

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

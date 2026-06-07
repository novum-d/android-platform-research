# AOSP Checkout

このリポジトリでは、AOSP source checkout を調査根拠の確認に使います。

`frameworks-base/` は成果物ではなく、一時的な evidence workspace として扱います。

## 方針

- `frameworks-base/` は Git 管理対象にしない
- `frameworks-base/` の working tree 変更を platform evidence として扱わない
- 調査では必ず `<from-tag>` と `<to-tag>` の明示的な tag 比較を使う
- `frameworks-base/` が dirty でも、tag 比較に基づく evidence だけを採用する

## 事前確認

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list '<from-tag>'
git -C frameworks-base tag --list '<to-tag>'
```

`status --short` に大量の差分が出る場合は、調査レポートの confidence に影響しないよう、ローカル working tree を evidence に使っていないことを明記します。

## 推奨する確認方法

ファイル一覧:

```bash
git -C frameworks-base diff --name-only <from-tag> <to-tag>
```

特定ファイルの差分:

```bash
git -C frameworks-base diff <from-tag> <to-tag> -- <path>
```

対象 tag の中で gate evidence を検索:

```bash
git -C frameworks-base grep -n "targetSdkVersion\|ApplicationInfo.targetSdkVersion\|CompatChanges.isChangeEnabled\|@ChangeId\|@EnabledAfter\|@EnabledSince" <to-tag> -- <file-or-dir>
```

## Analysis Files

候補ファイル一覧を生成する場合は、共通スクリプトに対象バージョンの値を渡します。

```bash
VERSION_DIR=<android-version-dir> \
OLD_TAG=<from-tag> \
NEW_TAG=<to-tag> \
TARGET_CODENAME=<codename> \
scripts/generate_target.sh
```

生成物は `<android-version-dir>/analysis/` に出力します。

## 避けること

以下は platform evidence として扱いません。

- `frameworks-base/` の unstaged / staged local change
- untracked files
- `.DS_Store`
- ローカルで生成した analysis file
- tag 比較ではなく working tree 差分だけから得た結論

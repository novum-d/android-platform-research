# AOSP checkout の扱い（AOSP Checkout）

このリポジトリでは、AOSP source checkout を調査根拠の確認に使います。

`frameworks-base/`と`tmp/aosp-checkouts/<project>`は成果物ではなく、一時的な
evidence workspaceとして扱います。

## 方針

- `platform/frameworks/base`は`frameworks-base/`、その他のAOSP projectは`tmp/aosp-checkouts/<project>`に置く
- evidenceに使う各projectの公式project pathとremote URLを記録する
- checkoutのworking tree変更をplatform evidenceとして扱わない
- 調査では各projectについて`<from-tag>`と`<to-tag>`の明示的なtag比較を使う
- checkoutがdirtyでも、tag比較に基づくevidenceだけを採用する
- 新規・更新調査では、ルート `AGENTS.md` の tag freshness rule に従い、公式 refs 上の各バージョンの最新通常リリースタグを確認する
- 既存レポートのタグは、そのタグで evidence を再検証するまでは書き換えない

## 事前確認

```bash
git -C <checkout-dir> status --short
git -C <checkout-dir> remote get-url origin
git -C <checkout-dir> tag --list '<from-tag>'
git -C <checkout-dir> tag --list '<to-tag>'
git -C <checkout-dir> rev-list -n 1 '<from-tag>'
git -C <checkout-dir> rev-list -n 1 '<to-tag>'
```

レポートにはAOSP project path、checkout path、remote URL、tag pair、両tagの
resolved commit hash、比較commandを記録します。`status --short`に差分が出る場合は、
ローカルworking treeをevidenceに使っていないこととconfidenceへの影響を明記します。

`platform/frameworks/base`でtagを確認できても、別projectに同じtagや実装があるとは
限りません。Bluetooth、ART、libcore、ContactsProvider、Conscryptなど、根拠に使う
projectごとに確認します。

## 推奨する確認方法

ファイル一覧:

```bash
git -C <checkout-dir> diff --name-only <from-tag> <to-tag>
```

特定ファイルの差分:

```bash
git -C <checkout-dir> diff <from-tag> <to-tag> -- <path>
```

対象 tag の中で gate evidence を検索:

```bash
git -C <checkout-dir> grep -n "targetSdkVersion\|ApplicationInfo.targetSdkVersion\|CompatChanges.isChangeEnabled\|@ChangeId\|@EnabledAfter\|@EnabledSince" <to-tag> -- <file-or-dir>
```

## 分析補助ファイル（Analysis Files）

`platform/frameworks/base`の候補ファイル一覧を生成する場合は、共通スクリプトへ
version directoryを渡します。tagとcodenameは`research-scope.json`から読み取ります。

```bash
VERSION_DIR=<android-version-dir> scripts/generate_target.sh
```

生成物は `<android-version-dir>/analysis/` に出力します。

記入例:
- Android 17調査では`VERSION_DIR=android17 scripts/generate_target.sh`を使い、`android17/research-scope.json`からtag pairを取得する。
- 生成された `analysis/*.txt` は候補一覧であり、最終的な根拠は tag diff と source context に記録する。

## 避けること

以下は platform evidence として扱いません。

- 任意のAOSP checkoutのunstaged / staged local change
- untracked files
- `.DS_Store`
- ローカルで生成した analysis file
- tag 比較ではなく working tree 差分だけから得た結論

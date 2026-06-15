# バージョニング（Versioning）

このリポジトリでは、`docs/` と `android<version>/` の責務を分ける。

## ルール（Rule）

`docs/` はバージョン非依存の運用知識だけを置く。

例:
- 調査原則
- 調査プレイブック
- レビュー観点
- confidence の考え方
- 情報源の優先順位
- 用語集
- cross-version の未解決質問や仮説

Android バージョン固有のものは `android<version>/` に置く。

例:
- Behavior Change 一覧
- applicability classification
- report / summary templates
- targetSdkVersion 固有のチェック項目
- AOSP tag pair
- analysis outputs
- release-specific backlog / roadmap
- release-specific knowledge graph
- decision log

## Android 16

現在のバージョン固有ディレクトリ:

```text
android16/
  analysis/
  behavior-changes/
  decisions/
  knowledge/
  planning/
  summaries/
  templates/
```

バージョンスコープ:

```text
From: android-15.0.0_r36
To:   android-16.0.0_r1
```

Target SDK focus:

```text
targetSdkVersion 36
```

## Android 17

Android 17 調査ディレクトリ:

```text
android17/
  analysis/
  behavior-changes/
  decisions/
  knowledge/
  planning/
  summaries/
  templates/
```

現在の状態:

```text
From: android-16.0.0_r4
To:   TBD: Android 17 AOSP tag
```

Android 17 official Behavior Change documentation is available, but the local
`frameworks-base` checkout currently has no `android-17*` tag.

Until the target Android 17 AOSP tag is available, do not assign High confidence
to AOSP-backed conclusions.

When the Android 17 AOSP tag is available, update all release-specific fields:

- Android version name
- API level / targetSdkVersion
- AOSP `From` tag
- AOSP `To` tag
- official Behavior Change URLs
- compat framework links
- classification rules if Android 17 changes the wording or applicability model
- templates and verification matrices

## 実用ルール（Practical Rule）

If a file contains `Android 16`, `targetSdkVersion 36`, `android-16.0.0_r1`,
or Android 16-specific topic prioritization, it should usually live under
`android16/`, not `docs/`.

例:
- `targetSdkVersion 37` の検証マトリクスは `android17/templates/` または `android17/behavior-changes/` に置く。
- すべての Android バージョンで使う「AOSP checkout の扱い」は `docs/workflow/` に置く。

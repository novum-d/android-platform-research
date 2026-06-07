# Versioning

このリポジトリでは、`docs/` と `android<version>/` の責務を分ける。

## Rule

`docs/` はバージョン非依存の運用知識だけを置く。

Examples:
- 調査原則
- 調査プレイブック
- レビュー観点
- confidence の考え方
- 情報源の優先順位
- 用語集
- cross-version の未解決質問や仮説

Android バージョン固有のものは `android<version>/` に置く。

Examples:
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

Current version-specific directory:

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

Version scope:

```text
From: android-15.0.0_r36
To:   android-16.0.0_r1
```

Target SDK focus:

```text
targetSdkVersion 36
```

## Android 17

When Android 17 research starts, create:

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

Copy Android 16 structure only as a starting point. Update all release-specific fields:

- Android version name
- API level / targetSdkVersion
- AOSP `From` tag
- AOSP `To` tag
- official Behavior Change URLs
- compat framework links
- classification rules if Android 17 changes the wording or applicability model
- templates and verification matrices

Do not edit Android 16 files to represent Android 17 behavior.

## Practical Rule

If a file contains `Android 16`, `targetSdkVersion 36`, `android-16.0.0_r1`,
or Android 16-specific topic prioritization, it should usually live under
`android16/`, not `docs/`.

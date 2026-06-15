# Android 17 調査（Android 17 Research）

このディレクトリは Android 17 固有の Behavior Change 調査を管理する。

## バージョンスコープ（Version Scope）

Current status:
- Android 17 Beta documentation is available.
- Local `frameworks-base` does not currently have an `android-17*` tag.
- AOSP evidence must use explicit tag comparisons once the target Android 17 tag is available.

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP tag

Target SDK focus:
- targetSdkVersion 37

## 読み進め方

Android 17 固有の読み進め方は以下を参照する。

```text
android17/GETTING_STARTED.md
```

Codex / agent 向けの Android 17 固有指示は以下を参照する。

```text
android17/AGENTS.md
```

## ディレクトリ構成（Layout）

| ディレクトリ（Directory） | 目的（Purpose） |
| --- | --- |
| `analysis/` | AOSP diff から生成した候補ファイル、分類補助ファイル |
| `behavior-changes/` | Behavior Change セクションごとの調査レポートと applicability classification |
| `decisions/` | Android 17 調査に関する人間の判断ログ |
| `knowledge/` | Android 17 固有の関連概念や調査テーマ |
| `planning/` | Android 17 固有の backlog / roadmap |
| `summaries/` | 顧客説明・社内共有用の 1ページ要約 |
| `templates/` | Android 17 用 report / summary templates |

## バージョニング（Versioning）

Android 16 調査結果は上書きしない。

Use:

```text
../docs/VERSIONING.md
```

# Android 16 Research

このディレクトリは Android 16 固有の Behavior Change 調査を管理する。

## Version Scope

From:
- android-15.0.0_r36

To:
- android-16.0.0_r1

Target SDK focus:
- targetSdkVersion 36

## 読み進め方

Android 16 固有の読み進め方は以下を参照する。

```text
android16/GETTING_STARTED.md
```

Codex / agent 向けの Android 16 固有指示は以下を参照する。

```text
android16/AGENTS.md
```

## Layout

| Directory | Purpose |
| --- | --- |
| `analysis/` | AOSP diff から生成した候補ファイル、分類補助ファイル |
| `behavior-changes/` | Behavior Change セクションごとの調査レポートと applicability classification |
| `decisions/` | Android 16 調査に関する人間の判断ログ |
| `knowledge/` | Android 16 固有の関連概念や調査テーマ |
| `planning/` | Android 16 固有の backlog / roadmap |
| `summaries/` | 顧客説明・社内共有用の 1ページ要約 |
| `templates/` | Android 16 用 report / summary templates |

## Versioning

Android 17 調査ではこのディレクトリを上書きしない。

Use:

```text
../docs/VERSIONING.md
```

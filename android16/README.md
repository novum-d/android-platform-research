# Android 16 Research

このディレクトリは Android 16 固有の Behavior Change 調査を管理する。

## Version Scope

Default scope:
- From: `android-15.0.0_r36`
- To: `android-16.0.0_r1`

Investigation override:
- 多くの個別調査では、依頼スコープに従い公開済み tag `android-16.0.0_r4` を To tag として使用している。
- 各 report の Metadata / Scope note を正とし、README の default scope と差がある場合は report 側に scope 差分を記録する。

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

## Primary Indexes

| Index | Purpose |
| --- | --- |
| [behavior-changes/README.md](behavior-changes/README.md) | Behavior Change section ごとの調査レポート一覧と適用分類 |
| [summaries/README.md](summaries/README.md) | 1ページ要約一覧 |
| [app-reports/wireless-camera-companion/investigation-report.md](app-reports/wireless-camera-companion/investigation-report.md) | カメラ連携アプリ向け Android 16 影響調査 |
| [behavior-changes/APPLICABILITY_CLASSIFICATION.md](behavior-changes/APPLICABILITY_CLASSIFICATION.md) | Android 16 用 applicability classification |

## Layout

| Directory | Purpose |
| --- | --- |
| `analysis/` | AOSP diff から生成した候補ファイル、分類補助ファイル |
| `app-reports/` | 特定アプリ種別向けの横断調査レポート |
| `behavior-changes/` | Behavior Change セクションごとの調査レポートと applicability classification |
| `decisions/` | Android 16 調査に関する人間の判断ログ |
| `knowledge/` | Android 16 固有の関連概念や調査テーマ |
| `planning/` | Android 16 固有の backlog / roadmap |
| `summaries/` | 顧客説明・社内共有用の 1ページ要約 |
| `templates/` | Android 16 用 report / summary templates |

## Current App-Specific Reports

| Report | Scope |
| --- | --- |
| [Wireless camera companion](app-reports/wireless-camera-companion/investigation-report.md) | カメラ連携アプリ向けに、Bluetooth、local network、CDM、Intent security、native / ART、大画面 UI などを横断評価 |

## Versioning

Android 17 調査ではこのディレクトリを上書きしない。

Use:

```text
../docs/VERSIONING.md
```

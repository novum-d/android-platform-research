# Android 16 調査

このディレクトリは Android 16 固有の Behavior Change 調査を管理する。

## バージョンスコープ

既定の比較範囲:
- 比較元: `android-15.0.0_r36`
- 比較先: `android-16.0.0_r1`

個別調査での上書き:
- 多くの個別調査では、依頼された範囲に従い、公開済みの `android-16.0.0_r4` タグを比較先として使用している。
- 各レポートのメタデータとスコープ注記を正とする。README の既定範囲と異なる場合は、レポート側にその差を記録する。

主な targetSdkVersion:
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

## 主な索引

| 索引 | 目的 |
| --- | --- |
| [behavior-changes/README.md](behavior-changes/README.md) | Behavior Change セクションごとの調査レポート一覧と適用条件分類 |
| [summaries/README.md](summaries/README.md) | 1ページ要約一覧 |
| [app-reports/wireless-camera-companion/investigation-report.md](app-reports/wireless-camera-companion/investigation-report.md) | カメラ連携アプリ向け Android 16 影響調査 |
| [behavior-changes/APPLICABILITY_CLASSIFICATION.md](behavior-changes/APPLICABILITY_CLASSIFICATION.md) | Android 16 用の適用条件分類 |

## ディレクトリ構成

| ディレクトリ | 目的 |
| --- | --- |
| `analysis/` | AOSP 差分から生成した候補ファイル、分類補助ファイル |
| `app-reports/` | 特定アプリ種別向けの横断調査レポート |
| `behavior-changes/` | Behavior Change セクションごとの調査レポートと適用条件分類 |
| `decisions/` | Android 16 調査に関する人間の判断ログ |
| `knowledge/` | Android 16 固有の関連概念や調査テーマ |
| `planning/` | Android 16 固有のバックログ / ロードマップ |
| `summaries/` | 顧客説明・社内共有用の 1ページ要約 |
| `templates/` | Android 16 用のレポート / 要約テンプレート |

## 現在のアプリ別レポート

| レポート | 対象範囲 |
| --- | --- |
| [Wireless camera companion](app-reports/wireless-camera-companion/investigation-report.md) | カメラ連携アプリ向けに、Bluetooth、local network、CDM、Intent security、native / ART、大画面 UI などを横断評価 |

## Versioning

Android 17 調査ではこのディレクトリを上書きしない。

参照:

```text
../docs/VERSIONING.md
```

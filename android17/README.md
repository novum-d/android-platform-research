# Android 17 調査

このディレクトリでは、Android 17 固有の Behavior Change 調査を管理する。

## バージョンスコープ

現在の状況:
- Android 17 の公式ドキュメントと release tag は公開済み。
- ローカルの `frameworks-base` には `android-17.0.0_r1` タグが存在する。
- AOSP 根拠は、`android-16.0.0_r4` と `android-17.0.0_r1` の明示的なタグ比較で確認する。

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

主な targetSdkVersion:
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

## ディレクトリ構成

| ディレクトリ | 目的 |
| --- | --- |
| `analysis/` | AOSP 差分から生成した候補ファイル、分類補助ファイル |
| `behavior-changes/` | Behavior Changeセクションごとの調査レポート、挙動比較、Android 17対応例 |
| `decisions/` | Android 17 調査に関する人間の判断ログ |
| `knowledge/` | Android 17 固有の関連概念や調査テーマ |
| `planning/` | Android 17 固有のバックログ / ロードマップ |
| `summaries/` | 顧客説明・社内共有用の 1ページ要約 |
| `templates/` | Android 17 用のレポート / 要約テンプレート |

## バージョニング

Android 16 調査結果は上書きしない。

参照:

```text
../docs/VERSIONING.md
```

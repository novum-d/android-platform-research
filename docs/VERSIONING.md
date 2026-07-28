# バージョニング

このリポジトリでは、`docs/` と `android<version>/` の責務を分ける。

## ルール

`docs/` はバージョン非依存の運用知識だけを置く。

例:
- 調査原則
- 調査プレイブック
- レビュー観点
- confidence の考え方
- 情報源の優先順位
- 用語集
- 複数の Android バージョンで再利用する比較テンプレート
- バージョン横断の未解決質問や仮説

Android バージョン固有のものは `android<version>/` に置く。

例:
- Behavior Change 一覧
- 適用条件分類
- レポート / Summary テンプレート
- targetSdkVersion 固有のチェック項目
- AOSP タグの組み合わせ
- 分析出力
- リリース固有のバックログ / ロードマップ
- リリース固有のナレッジグラフ
- 判断ログ

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
比較元: android-15.0.0_r36
比較先: android-16.0.0_r1
```

主な targetSdkVersion:

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
比較元: android-16.0.0_r4
比較先: android-17.0.0_r1
```

Android 17 の公式 Behavior Change 文書と `android-17.0.0_r1` は公開済み。
AOSP 根拠は両 tag の明示的な比較を使う。

Android 17 の追加 release tag または QPR tag を比較対象に採用する場合は、リリース固有の以下の項目を更新する。

- Android version name
- API level / targetSdkVersion
- AOSP `From` tag
- AOSP `To` tag
- 公式 Behavior Change URL
- compat framework link
- Android 17 で文言や適用条件モデルが変わる場合は、分類ルール
- テンプレートと検証マトリクス

## 実用ルール

ファイルに `Android 16`、`targetSdkVersion 36`、`android-16.0.0_r1`、または Android 16 固有の調査優先度が含まれる場合、そのファイルは通常 `docs/` ではなく `android16/` 配下に置く。

例:
- `targetSdkVersion 37` の検証マトリクスは `android17/templates/` または `android17/behavior-changes/` に置く。
- すべての Android バージョンで使う「AOSP checkout の扱い」は `docs/workflow/` に置く。
- Android 15→16、Android 16→17 の両方で使う OS 挙動比較テンプレートは `docs/templates/` に置き、比較結果は対象の `android<version>/behavior-changes/` に置く。

# アプリのメモリ上限 - 1ページ要約

## 対象（Target）

Android 17 挙動変更

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP タグ

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

## 適用条件（Applicability）

- 主分類（Primary classification）: UNKNOWN_NEEDS_MORE_EVIDENCE
- OS アップデート / 全アプリ: 公式文書上は該当候補。`behavior-changes-all` ページに掲載されている。
- targetSdkVersion 37 以上: 公式文書上は不要と読める。ただし AOSP 適用ゲートは未確認。
- その他の必須条件: 一部の Android 端末のみ。端末の総 RAM 容量、メモリ使用量、プロセス状態、メモリリミッター対象端末条件が関係する可能性。
- Compat Change ID: 未確認
- Compat default state: 未確認

## 早見マトリクス

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 公式文書上は全アプリ向け変更のため、対象端末ではアプリのメモリ上限が適用される可能性がある。AOSP 適用ゲートは未確認。 |
| Android 17 / targetSdkVersion 37 | targetSdkVersion 36 と同様に、対象端末ではアプリのメモリ上限が適用される可能性がある。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | メモリリミッター対象端末でアプリが上限に達すると、`REASON_OTHER` / `MemoryLimiter:AnonSwap` として観測される可能性がある。 |

## 要約

Android 17 では、端末の総 RAM 容量に基づくアプリのメモリ上限が導入される、と公式文書は説明している。主な目的は、極端なメモリリークやメモリ外れ値によるシステム全体の不安定化を抑えることである。

## 顧客影響

- 要確認

## 影響対象

- 対象アプリ: Android 17 上で動作し、メモリリミッター対象端末上で実行されるアプリ。
- 対象機能: 大きなメモリ使用量、画像 / 動画処理、ML inference、WebView、大きなキャッシュ、バックグラウンド同期、ネイティブヒープ使用量。
- 対象条件: アプリセッションがメモリ上限に到達する場合。

## 対応要否

- 必須対応: メモリ基準値を測定し、`ApplicationExitInfo` で `REASON_OTHER` / `MemoryLimiter:AnonSwap` を収集できるようにする。
- 推奨対応: `am memory-limiter status`、`manual <pid> <limit>|max|none`、`ignore <uid>|none|all` とトリガーベースのプロファイリングを使って、上限到達時の挙動とヒープダンプを確認する。
- 不要: メモリリミッター非対象端末、または上限に到達しないアプリセッションでは直接影響は限定的。ただし対象条件は AOSP タグ待ち。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 36 | Android 17 のアプリメモリ上限は対象外。メモリの基準挙動を測定する。 |
| Android 17 | 36 | 公式文書上は全アプリ向け変更のため、対象端末ではメモリリミッターが適用される可能性がある。 |
| Android 17 | 37 | targetSdkVersion 36 と同様に、対象端末ではメモリリミッターが適用される可能性がある。 |

## 検証サブセクション

`Test your app's behavior under the memory constraints` は `App memory limits` の検証手段であり、別の挙動変更としては扱わない。公式文書は、メモリ上限を課す端末上でのみ `am memory-limiter` コマンドが効果を持つと説明している。

| コマンド | 用途 |
| --- | --- |
| `am memory-limiter ignore <uid>|none|all` | UID または全アプリ単位でメモリリミッターの適用を無視 / リセットする |
| `am memory-limiter manual <pid> <limit>|max|none` | PID 単位で MB 指定の手動メモリ上限を課す、または解除する |
| `am memory-limiter status` | 表示中 / 非表示プロセスを含む現在のメモリリミッター状態を確認する |

## 顧客向け説明

Android 17 では、一部の端末でアプリごとのメモリ上限が導入されます。これは、極端なメモリリークや大きなメモリ外れ値が、端末全体の不安定化、UI のカクつき、バッテリー消費、アプリ強制終了につながる前に制御するための変更です。

この項目は全アプリ向けページに掲載されているため、targetSdkVersion 37 への更新有無に関係なく Android 17 端末で影響する可能性があります。ただし、すべての端末で必ず適用されるわけではなく、公式文書は一部の Android 端末のみに課されると説明しています。

影響確認には `ApplicationExitInfo.getDescription()` を使い、`REASON_OTHER` と `MemoryLimiter:AnonSwap` を確認します。検証時はまず `am memory-limiter status` で対象端末か確認し、必要に応じて `manual <pid> <limit>` で上限到達を再現し、`ignore <uid>|none|all` で適用差分を確認します。`TRIGGER_TYPE_ANOMALY` によるトリガーベースのプロファイリングでヒープダンプを取得することも推奨されます。

## 根拠

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-all
- 検証対象の原文: Android 17 では、端末の総 RAM 容量に基づくアプリのメモリ上限が導入され、メモリ上限は一部の Android 端末にのみ課される。
- 検証サブセクション: `am memory-limiter ignore` / `manual` / `status` は公式のテスト制御であり、メモリ上限を課さない端末では効果がない。
- AOSP ファイル: 未確認。ローカルの `frameworks-base` に `android-17*` タグがない。
- AOSP ソース文脈: 未確認。タグ間差分が実行できない。
- 差分解釈: 未分類。公式文書上は、追加された挙動 / 変更された条件と読めるが、AOSP 差分による確認は Android 17 タグ待ち。
- 適用ゲートの結論: 未確認。公式文書上は Android 17 全アプリ + 一部端末条件。targetSdkVersion 適用ゲート / Compat framework の根拠は未取得。

## 人間の判断欄

最終優先度（Final Priority）:
- Human decision required

判断:
- Android 17 AOSP タグが利用可能になった後に追加調査が必要

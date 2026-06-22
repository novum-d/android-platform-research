# App memory limits - 1ページ要約

## 対象

Android 17 Behavior Change

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

## 適用条件

- 主分類（Primary classification）: OS_UPDATE_ALL_APPS
- OS アップデート / 全アプリ: はい / 条件付き。AOSP に targetSdkVersion ゲートは確認されず、端末 / ベンダー設定条件で有効化される。
- targetSdkVersion 37 以上: 不要。targetSdkVersion ゲートは確認されない。
- その他の必須条件: 一部の Android 端末のみ。`/vendor/etc/memory-limiter-config.xml`、端末 RAM、プロセス状態、メモリ使用量が関係する。
- Compat Change ID: 確認されず
- Compat default state: compat framework ではなく feature flag / ベンダー設定 / DeviceConfig に依存

## 早見マトリクス

| シナリオ | 影響 |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 対象端末では app memory limits が適用され得る。targetSdkVersion ゲートは確認されない。 |
| Android 17 / targetSdkVersion 37 | targetSdkVersion 36 と同様に、対象端末では app memory limits が適用される可能性がある。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | memory limiter 対象端末でアプリが制限値に達すると、`REASON_OTHER` / `MemoryLimiter:AnonSwap` として観測される可能性がある。 |

## 要約

Android 17 では、端末の合計 RAM に基づくアプリごとのメモリ制限が導入される。AOSP では `MemoryLimiter` が `ActivityManagerService` / `ProcessRecord` に接続され、プロセス状態に応じたメモリ / swap 制限を native cgroup 層に渡す。

## 顧客影響

- 対象端末で極端なメモリリーク / メモリ使用量の外れ値があるセッションは、`REASON_OTHER` / `MemoryLimiter:AnonSwap` としてプロセス終了する可能性がある。

## 影響対象

- 対象アプリ: Android 17 上で動作し、memory limiter 対象端末上で実行されるアプリ。
- 対象機能: 大きなメモリ使用、画像 / 動画処理、ML inference、WebView、大量 cache、background sync、native heap usage。
- 対象条件: アプリ セッションがメモリ制限に到達する場合。

## 対応要否

- 必須対応: メモリ使用量のベースラインを測定し、`ApplicationExitInfo` で `REASON_OTHER` / `MemoryLimiter:AnonSwap` を収集できるようにする。
- 推奨対応: `am memory-limiter status`、`manual <pid> <percent>|none`、`ignore <uid>|none|all` と trigger-based profiling を使って、制限到達時の挙動と heap dump を確認する。
- 不要: memory limiter 非対象端末、または制限に到達しないアプリ セッションでは直接影響は限定的。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 36 | Android 17 app memory limits は対象外。メモリ挙動のベースラインを測定する。 |
| Android 17 | 36 | 公式文書上は all apps change のため、対象端末では memory limiter が適用される可能性がある。 |
| Android 17 | 37 | targetSdkVersion 36 と同様に、対象端末では memory limiter が適用される可能性がある。 |

## 検証サブセクション（Test your app's behavior under the memory constraints）

`Test your app's behavior under the memory constraints` は `App memory limits` の検証手段であり、別 Behavior Change としては扱わない。公式文書は、メモリ制限を課す端末上でのみ `am memory-limiter` コマンドが効果を持つと説明している。

| コマンド | 用途 |
| --- | --- |
| `am memory-limiter ignore <uid>|none|all` | UID または全アプリ単位で memory limiter の制限適用を無視 / リセットする |
| `am memory-limiter manual <pid> <percent>|none` | PID 単位で合計 RAM 比率の手動メモリ制限を課す、または解除する |
| `am memory-limiter status` | 表示中 / 非表示のプロセスを含む現在の memory limiter 状態を確認する |

## 顧客向け説明

Android 17 では、一部の端末でアプリごとのメモリ制限が導入されます。これは極端なメモリリークや大きなメモリ使用量の外れ値が端末全体の不安定化、UI のカクつき、バッテリー消費、アプリ kill につながる前に制御するための変更です。

この項目は all apps ページに掲載されているため、targetSdkVersion 37 への更新有無に関係なく Android 17 端末で影響する可能性があります。ただし、すべての端末で必ず適用されるわけではなく、公式文書は一部の Android 端末にのみ適用されると説明しています。

影響確認には `ApplicationExitInfo.getDescription()` を使い、`REASON_OTHER` と `MemoryLimiter:AnonSwap` を確認します。検証時はまず `am memory-limiter status` で対象端末か確認し、必要に応じて `manual <pid> <limit>` で制限到達を再現し、`ignore <uid>|none|all` で制限適用の差分を確認します。`TRIGGER_TYPE_ANOMALY` を使う trigger-based profiling で heap dump を取得することも推奨されます。

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-all
- 検証対象の原文: Android 17 introduces app memory limits based on device total RAM, and memory limits are imposed only on a subset of Android devices.
- 検証サブセクション: `am memory-limiter ignore` / `manual` / `status` are official test controls, and they have no effect on devices that do not impose memory limits.
- AOSP ファイル: `MemoryLimiter.java`, `com_android_server_am_MemoryLimiter.cpp`, `ActivityManagerService.java`, `ActivityManagerShellCommand.java`, `ProcessRecord.java`, `memory-limiter-config.xsd`, `MemoryLimiter.md`
- AOSP ソース文脈: アプリ プロセス ライフサイクル -> `ProcessRecord` -> `MemoryLimiter.Limiter` -> native cgroup 制限 / event -> anomaly profiling trigger -> `MemoryLimiter:AnonSwap` による delayed kill。
- 差分解釈: added behavior / changed condition。MemoryLimiter 本体、JNI、ベンダー設定 schema、shell command が追加され、ベンダー設定と RAM 条件で対象端末が決まる。
- ゲート結論: Android 17 上で MemoryLimiter が feature enabled、`system_server` 内で動作し、ベンダー設定と RAM 条件を満たす端末で、対象アプリ プロセスが設定済み制限値に達した場合に適用される。targetSdkVersion ゲート / compat Change ID は確認されない。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 人間による判断が必要

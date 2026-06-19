# App memory limits - 1ページ要約

## 対象（Target）

Android 17 Behavior Change

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

## 適用条件（Applicability）

- 主分類（Primary classification）: OS_UPDATE_ALL_APPS
- OS アップデート / 全アプリ（OS update / all apps）: Yes / Conditional。AOSP に targetSdkVersion gate は確認されず、device / vendor config 条件で有効化される。
- targetSdkVersion 37 以上: 不要。targetSdkVersion gate は確認されない。
- その他の必須条件（Other required conditions）: 一部の Android devices のみ。`/vendor/etc/memory-limiter-config.xml`、device RAM、process state、memory usage が関係する。
- Compat Change ID: 確認されず
- Compat default state: compat framework ではなく feature flag / vendor config / DeviceConfig に依存

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 対象 device では app memory limits が適用され得る。targetSdkVersion gate は確認されない。 |
| Android 17 / targetSdkVersion 37 | targetSdkVersion 36 と同様に、対象 device では app memory limits が適用される可能性がある。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | memory limiter 対象 device で app が limit に達すると、`REASON_OTHER` / `MemoryLimiter:AnonSwap` として観測される可能性がある。 |

## 要約（Summary）

Android 17 では、device total RAM に基づく app memory limits が導入される。AOSP では `MemoryLimiter` が `ActivityManagerService` / `ProcessRecord` に接続され、process state に応じた memory / swap limits を native cgroup layer に渡す。

## 顧客影響（Customer Impact）

- 対象 device で extreme memory leak / memory outlier がある session は、`REASON_OTHER` / `MemoryLimiter:AnonSwap` として process exit する可能性がある。

## 影響対象（Who Is Affected）

- 対象アプリ: Android 17 上で動作し、memory limiter 対象 device 上で実行されるアプリ。
- 対象機能: large memory usage、画像 / 動画処理、ML inference、WebView、large cache、background sync、native heap usage。
- 対象条件: app session が memory limit に到達する場合。

## 対応要否（Required Action）

- 必須対応: memory baseline を測定し、`ApplicationExitInfo` で `REASON_OTHER` / `MemoryLimiter:AnonSwap` を収集できるようにする。
- 推奨対応: `am memory-limiter status`、`manual <pid> <percent>|none`、`ignore <uid>|none|all` と trigger-based profiling を使って、limit hit 時の挙動と heap dump を確認する。
- 不要: memory limiter 非対象 device、または limit に到達しない app sessions では直接影響は限定的。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 16 | 36 | Android 17 app memory limits は対象外。baseline memory behavior を測定する。 |
| Android 17 | 36 | 公式文書上は all apps change のため、対象 device では memory limiter が適用される可能性がある。 |
| Android 17 | 37 | targetSdkVersion 36 と同様に、対象 device では memory limiter が適用される可能性がある。 |

## 検証サブセクション（Test your app's behavior under the memory constraints）

`Test your app's behavior under the memory constraints` は `App memory limits` の検証手段であり、別 Behavior Change としては扱わない。公式文書は、memory limits を impose する device 上でのみ `am memory-limiter` commands が効果を持つと説明している。

| Command | 用途 |
| --- | --- |
| `am memory-limiter ignore <uid>|none|all` | UID または全アプリ単位で memory limiter enforcement を ignore / reset する |
| `am memory-limiter manual <pid> <percent>|none` | PID 単位で total RAM 比率の manual memory limit を課す、または解除する |
| `am memory-limiter status` | visible / non-visible process を含む current memory limiter status を確認する |

## 顧客向け説明（Explanation for Customers）

Android 17 では、一部の端末でアプリごとの memory limit が導入されます。これは extreme memory leak や大きな memory outlier が端末全体の不安定化、UI のカクつき、battery drain、アプリ kill につながる前に制御するための変更です。

この項目は all apps ページに掲載されているため、targetSdkVersion 37 への更新有無に関係なく Android 17 端末で影響する可能性があります。ただし、すべての端末で必ず適用されるわけではなく、公式文書は一部の Android devices のみに imposed されると説明しています。

影響確認には `ApplicationExitInfo.getDescription()` を使い、`REASON_OTHER` と `MemoryLimiter:AnonSwap` を確認します。検証時はまず `am memory-limiter status` で対象 device か確認し、必要に応じて `manual <pid> <limit>` で limit hit を再現し、`ignore <uid>|none|all` で enforcement 差分を確認します。trigger-based profiling with `TRIGGER_TYPE_ANOMALY` で heap dump を取得することも推奨されます。

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-all
- 検証対象の原文: Android 17 introduces app memory limits based on device total RAM, and memory limits are imposed only on a subset of Android devices.
- 検証サブセクション: `am memory-limiter ignore` / `manual` / `status` are official test controls, and they have no effect on devices that do not impose memory limits.
- AOSP ファイル: `MemoryLimiter.java`, `com_android_server_am_MemoryLimiter.cpp`, `ActivityManagerService.java`, `ActivityManagerShellCommand.java`, `ProcessRecord.java`, `memory-limiter-config.xsd`, `MemoryLimiter.md`
- AOSP ソース文脈: app process lifecycle -> `ProcessRecord` -> `MemoryLimiter.Limiter` -> native cgroup limit / event -> anomaly profiling trigger -> delayed kill with `MemoryLimiter:AnonSwap`.
- 差分解釈: added behavior / changed condition。MemoryLimiter 本体、JNI、vendor config schema、shell command が追加され、vendor config と RAM 条件で対象 device が決まる。
- Gate conclusion: Android 17 上で MemoryLimiter が feature enabled、system_server 内で動作し、vendor config と RAM 条件を満たす device で、対象 app process が configured limit に達した場合に適用される。targetSdkVersion gate / compat Change ID は確認されない。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 人間による判断が必要

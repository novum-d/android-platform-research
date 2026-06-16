# App memory limits - 1ページ要約（One Page Summary）

## 対象（Target）

Android 17 Behavior Change

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP tag

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

## 適用条件（Applicability）

- 主分類（Primary classification）: UNKNOWN_NEEDS_MORE_EVIDENCE
- OS アップデート / 全アプリ（OS update / all apps）: 公式文書上は該当候補。`behavior-changes-all` ページに掲載されている。
- targetSdkVersion 37 以上: 公式文書上は不要と読める。ただし AOSP gate 未確認。
- その他の必須条件（Other required conditions）: 一部の Android devices のみ。device total RAM、memory usage、process state、memory limiter 対象 device 条件が関係する可能性。
- Compat Change ID: Unknown
- Compat default state: Unknown

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 公式文書上は all apps change のため、対象 device では app memory limits が適用される可能性がある。AOSP gate 未確認。 |
| Android 17 / targetSdkVersion 37 | targetSdkVersion 36 と同様に、対象 device では app memory limits が適用される可能性がある。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | memory limiter 対象 device で app が limit に達すると、`REASON_OTHER` / `MemoryLimiter:AnonSwap` として観測される可能性がある。 |

## 要約（Summary）

Android 17 では、device total RAM に基づく app memory limits が導入される、と公式文書は説明している。主な目的は extreme memory leak や memory outlier による system-wide instability を抑えることである。

## 顧客影響（Customer Impact）

- 要確認

## 影響対象（Who Is Affected）

- 対象アプリ: Android 17 上で動作し、memory limiter 対象 device 上で実行されるアプリ。
- 対象機能: large memory usage、画像 / 動画処理、ML inference、WebView、large cache、background sync、native heap usage。
- 対象条件: app session が memory limit に到達する場合。

## 対応要否（Required Action）

- 必須対応: memory baseline を測定し、`ApplicationExitInfo` で `REASON_OTHER` / `MemoryLimiter:AnonSwap` を収集できるようにする。
- 推奨対応: `am memory-limiter status`、`manual <pid> <limit>|max|none`、`ignore <uid>|none|all` と trigger-based profiling を使って、limit hit 時の挙動と heap dump を確認する。
- 不要: memory limiter 非対象 device、または limit に到達しない app sessions では直接影響は限定的。ただし対象条件は AOSP tag 待ち。

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
| `am memory-limiter manual <pid> <limit>|max|none` | PID 単位で MB 指定の manual memory limit を課す、または解除する |
| `am memory-limiter status` | visible / non-visible process を含む current memory limiter status を確認する |

## 顧客向け説明（Explanation for Customers）

Android 17 では、一部の端末でアプリごとの memory limit が導入されます。これは extreme memory leak や大きな memory outlier が端末全体の不安定化、UI のカクつき、battery drain、アプリ kill につながる前に制御するための変更です。

この項目は all apps ページに掲載されているため、targetSdkVersion 37 への更新有無に関係なく Android 17 端末で影響する可能性があります。ただし、すべての端末で必ず適用されるわけではなく、公式文書は一部の Android devices のみに imposed されると説明しています。

影響確認には `ApplicationExitInfo.getDescription()` を使い、`REASON_OTHER` と `MemoryLimiter:AnonSwap` を確認します。検証時はまず `am memory-limiter status` で対象 device か確認し、必要に応じて `manual <pid> <limit>` で limit hit を再現し、`ignore <uid>|none|all` で enforcement 差分を確認します。trigger-based profiling with `TRIGGER_TYPE_ANOMALY` で heap dump を取得することも推奨されます。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-all
- Original statement: Android 17 introduces app memory limits based on device total RAM, and memory limits are imposed only on a subset of Android devices.
- Verification subsection: `am memory-limiter ignore` / `manual` / `status` are official test controls, and they have no effect on devices that do not impose memory limits.
- AOSP files: 未確認。local `frameworks-base` に `android-17*` tag がない。
- AOSP source context: 未確認。tag 間 diff が実行できない。
- Diff interpretation: 未分類。公式文書上は added behavior / changed condition と読めるが、AOSP diff による確認は Android 17 tag 待ち。
- Gate conclusion: Unknown。公式文書上は Android 17 all apps + device subset condition。targetSdkVersion gate / compat framework evidence は未取得。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Human decision required

判断（Decision）:
- Further investigation required after Android 17 AOSP tag is available

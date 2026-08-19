# Ordered broadcast priority scope no longer global - 1ページ要約（One Page Summary）

## 対象（Target）

Android 16 Behavior Change:
- Ordered broadcast priority scope no longer global

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:

## 適用条件（Applicability）

- 主分類（Primary classification）: `OS_UPDATE_ALL_APPS`
- OS アップデート / 全アプリ（OS update / all apps）: Yes。Android 16 上で ordered broadcast / priority receiver を使うアプリに targetSdkVersion と無関係に影響し得る。
- targetSdkVersion 36 以上: No。AOSP `BroadcastRecord` / `BroadcastFilter` に targetSdkVersion 36 gate は見つからない。
- その他の必須条件（Other required conditions）: `android:priority`、`IntentFilter#setPriority()`、ordered broadcast、または broadcast receiver priority による process 間順序制御に依存すること。
- Compat Change ID:
  - `LIMIT_PRIORITY_SCOPE` = `371307720`
  - `RESTRICT_PRIORITY_VALUES` = `371309185`
- Compat default state: AOSP test では enabled として扱われる。公式 compat framework 一覧では確認できず、developer 向け toggle command も確認できない。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 16 / targetSdkVersion 35 | 影響あり。OS update だけで priority scope が変わる。 |
| Android 16 / targetSdkVersion 36 | 影響あり。targetSdkVersion 35 と同じ platform policy。 |
| Android 15 / targetSdkVersion 36 | Android 16 の標準挙動は適用されない。 |
| 同一 process 内の receiver priority | priority ordering は尊重される。 |
| 同一 app だが別 process | cross-process 扱い。priority order は保証されない。 |
| 別 app / 別 uid | cross-process / cross-app 扱い。priority order は保証されない。 |
| non-system app が `SYSTEM_HIGH_PRIORITY` / `SYSTEM_LOW_PRIORITY` を要求 | context-registered receiver では app range 内に補正される。 |
| system component が `SYSTEM_HIGH_PRIORITY` / `SYSTEM_LOW_PRIORITY` を使う | system / core uid では保持される。 |

## 要約（Summary）

Android 16 では、broadcast receiver priority は global な順序制御ではなくなる。`android:priority` と `IntentFilter#setPriority()` は残るが、異なる process 間で delivery order を保証する用途には使えない。

## 顧客影響（Customer Impact）

- 影響あり / 要確認。
- 複数 process や複数 app 間で ordered broadcast priority により初期化順序、依存順序、result extras、abort を制御している場合に影響し得る。
- targetSdkVersion 36 化の影響ではなく、Android 16 へ OS アップデートした時の影響として説明する。

## 影響対象（Who Is Affected）

- ordered broadcast を送受信するアプリ。
- manifest receiver で `android:priority` を指定するアプリ。
- context-registered receiver で `IntentFilter#setPriority()` を使うアプリ。
- 複数 process に receiver を分けているアプリ。
- receiver priority で初期化順序 / 依存順序を制御しているアプリ。
- `abortBroadcast()` や ordered broadcast result extras の順序に依存するアプリ。
- SDK / library / plugin が receiver priority を設定するアプリ。

## 対応要否（Required Action）

- 必須対応: cross-process / cross-app の receiver priority ordering に依存する設計を棚卸しする。
- 推奨対応: process 間協調は bound service、ContentProvider、明示的 IPC、WorkManager、app-internal queue などへ移行する。
- 推奨対応: `SYSTEM_HIGH_PRIORITY` / `SYSTEM_LOW_PRIORITY` を app が使っていないか確認する。
- 不要: ordered broadcast を使わない、または同一 process 内の priority order だけに依存するアプリ。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 15 | 35 | 既存 baseline。Android 16 の priority scope 変更なし。 |
| Android 16 | 35 | priority scope change が適用される。OS update impact を確認。 |
| Android 16 | 36 | targetSdkVersion 35 と同じ挙動。targetSdkVersion gate はなし。 |
| Android 15 | 36 | targetSdkVersion 36 だけでは Android 16 behavior が発生しないことを比較。 |

追加テスト:

| 観点 | 期待確認 |
| --- | --- |
| `sendOrderedBroadcast()` | receiver delivery order と result propagation を確認。 |
| manifest receiver `android:priority` | same process と cross-process を分けて確認。 |
| context-registered receiver `IntentFilter#setPriority()` | priority clamp と same process ordering を確認。 |
| same app different process | priority order が保証されない前提で動くか確認。 |
| different app / different uid | priority order に依存しないことを確認。 |
| `SYSTEM_HIGH_PRIORITY` / `SYSTEM_LOW_PRIORITY` | non-system app と system component の差を確認。 |
| `abortBroadcast()` / `setResultExtras()` | cross-process priority 順序前提がないか確認。 |
| migration path | explicit IPC / service / provider / WorkManager / app-internal queue への置換を検証。 |

## 顧客向け説明（Explanation for Customers）

Android 16 へ OS アップデートすると、broadcast receiver priority は別 process / 別 app をまたぐ順序保証として使えなくなります。これは targetSdkVersion 36 に上げた時だけの変更ではなく、targetSdkVersion 35 のままでも Android 16 端末上では影響し得ます。

同一 process 内の receiver order だけに依存する場合は影響が限定的ですが、複数 process や複数アプリ間の協調を `android:priority` / `IntentFilter#setPriority()` に任せている場合は、明示的な IPC や queue に移行してください。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/16/behavior-changes-all#ordered-broadcast-priority
- AOSP files:
  - `frameworks-base/core/java/android/content/IntentFilter.java`
  - `frameworks-base/core/java/android/content/pm/PackageParser.java`
  - `frameworks-base/services/core/java/com/android/server/am/BroadcastRecord.java`
  - `frameworks-base/services/core/java/com/android/server/am/BroadcastFilter.java`
  - `frameworks-base/services/core/java/com/android/server/am/BroadcastProcessQueue.java`
  - `frameworks-base/services/core/java/com/android/server/am/BroadcastQueueImpl.java`
  - `frameworks-base/services/core/java/com/android/server/pm/resolution/ComponentResolver.java`
  - `frameworks-base/services/core/java/com/android/server/am/broadcasts_flags.aconfig`
- AOSP source context:
  - `BroadcastRecord.LIMIT_PRIORITY_SCOPE` は priority values の scope を process level に限定する ChangeId。
  - `BroadcastRecord.calculateBlockedUntilBeyondCount()` は Android 16 で旧 global priority tranche blocking fallback を持たない。
  - `BroadcastFilter.RESTRICT_PRIORITY_VALUES` は context-registered receiver priority を app range に補正する。
  - `PackageParser` / `ComponentResolver` は manifest receiver priority の parse / sort 経路。
- Diff interpretation:
  - Android 16 で priority scope が global ではなく process level になる。
  - Android 16 で context-registered receiver の priority restriction が feature flag なしの標準経路になる。
  - targetSdkVersion gate は見つからない。
- Caveat:
  - manifest-declared receiver の priority value clamp は、今回確認した範囲では context-registered receiver ほど直接的な実装根拠を確認できなかった。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Critical / High / Medium / Low

判断（Decision）:
- Explain / Monitor / Ignore / Further investigation required

補足:
- 最終優先度、顧客通知要否、release readiness は repository owner が判断する。

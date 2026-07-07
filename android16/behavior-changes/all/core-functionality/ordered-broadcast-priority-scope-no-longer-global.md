# Ordered broadcast priority scope no longer global 調査レポート

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:
- `android16/AGENTS.md` は To tag を `android-16.0.0_r1` としているが、本調査では依頼スコープに従い公開済み Android 16 tag として `android-16.0.0_r4` を使用した。

Previous targetSdkVersion:
- 35

Target targetSdkVersion:
- 36

### Behavior Change 文書（Behavior Change Source）

Document:
- https://developer.android.com/about/versions/16/behavior-changes-all#ordered-broadcast-priority

Page:
- Behavior changes: all apps

Category:
- Core functionality

Section:
- Ordered broadcast priority scope no longer global

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `OS_UPDATE_ALL_APPS`

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 16 に OS アップデートしただけで適用されるか | Yes | 公式 all apps ページは Android 16 で実行される全アプリに適用される変更として掲載している。AOSP `BroadcastRecord` / `BroadcastFilter` の Android 16 実装に targetSdkVersion 36 gate は見つからない。 |
| targetSdkVersion 36 以上が必要か | No | `LIMIT_PRIORITY_SCOPE` / `RESTRICT_PRIORITY_VALUES` は `PlatformCompat` ChangeId として存在するが、targetSdkVersion 36 annotation は確認できない。 |
| 追加の実行時条件があるか | Yes | ordered broadcast または priority 付き broadcast receiver を使い、特に process 境界をまたいだ receiver priority ordering に依存すること。 |
| Compat Change ID が関係するか | Yes | AOSP hidden ChangeId として `LIMIT_PRIORITY_SCOPE` = `371307720`、`RESTRICT_PRIORITY_VALUES` = `371309185` を確認した。公式 compat framework 一覧では検索確認できなかった。 |

### 調査日（Investigation Date）

2026-07-05

### 信頼度（Confidence）

- Medium-High

理由:
- 公式文書は all apps 変更として明記している。
- AOSP `BroadcastRecord` 差分で priority scope を process level に限定する実装と、Android 15 の旧 global priority tranche blocking が Android 16 で削除されたことを確認した。
- AOSP `BroadcastFilter` 差分で context-registered receiver の priority clamp が Android 16 で feature flag なしに適用されることを確認した。
- manifest-declared receiver の priority は `PackageParser` / `ComponentResolver` で parse / sort される経路を確認したが、`SYSTEM_HIGH_PRIORITY` / `SYSTEM_LOW_PRIORITY` 境界への単純な clamp は context-registered receiver ほど直接的な実装根拠を確認できなかった。この点は Facts / Observations で分けて記録する。

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [x] OS update / all apps on Android 16 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 36 on Android 16+
- [ ] targetSdkVersion >= 36, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [ ] Unknown / needs more evidence

必要な実行時条件（Required runtime conditions）:
- Android version: Android 16
- targetSdkVersion: 条件なし。35 と 36 の両方で同じ platform broadcast policy が適用される見込み。
- Device/form factor: 条件なし。
- Permission/API/component condition: ordered broadcast、manifest receiver `android:priority`、context-registered receiver `IntentFilter#setPriority()`、または priority に依存する broadcast coordination を使うこと。
- App state/process condition: 同一 process 内の複数 receiver、同一 app の別 process、別 app / 別 uid などの receiver 配置。

Compat framework:
- Change ID: `371307720`
- Change name: `LIMIT_PRIORITY_SCOPE`
- Default state: AOSP test default は enabled として扱われる。公式 compat framework 一覧では確認できなかった。
- Toggleable for testing: 公式 testing command は確認できない。AOSP annotation では `@Overridable` は確認できない。

- Change ID: `371309185`
- Change name: `RESTRICT_PRIORITY_VALUES`
- Default state: AOSP test default は enabled として扱われる。公式 compat framework 一覧では確認できなかった。
- Toggleable for testing: 公式 testing command は確認できない。AOSP annotation では `@Overridable` は確認できない。

分類信頼度（Classification confidence）:
- Medium-High

分類根拠（Classification evidence）:
- Official documentation page: `behavior-changes-all` の Ordered broadcast priority scope no longer global。
- Original applicability statement: Android 16 all apps ページは、Android 16 上で実行される全アプリに適用される変更として説明している。
- AOSP targetSdk gate: 見つからない。
- Compat framework entry: AOSP `@ChangeId` は確認したが、公式 compat framework 一覧には見つからない。

---

# エグゼクティブサマリー（Executive Summary）

Android 16 では、ordered broadcast / priority 付き broadcast receiver の priority scope が global ではなくなる。`android:priority` や `IntentFilter#setPriority()` による priority は、同一 application process 内では順序制御として扱われるが、別 process / 別 app をまたぐ delivery order は保証されない。

この変更は Android 16 の all apps 変更であり、targetSdkVersion 36 への更新だけで発生する変更ではない。targetSdkVersion 35 のまま Android 16 端末で動くアプリでも、broadcast receiver priority を使って process 間の初期化順序、依存順序、result extras、abort などを制御している場合は影響し得る。

複数 process や複数 app の協調を ordered broadcast priority に依存している場合は、bound service、ContentProvider、明示的 IPC、WorkManager、app-internal queue、共有 storage と lock など、明示的な coordination channel へ移行する必要がある。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statement）

公式文書では、Android 16 について以下を説明している。

- アプリは manifest receiver の `android:priority`、context-registered receiver の `IntentFilter#setPriority()` で broadcast receiver priority を定義できる。
- broadcast は通常、priority の高い receiver から低い receiver へ配信される。
- Android 16 では、異なる process 間で `android:priority` または `IntentFilter#setPriority()` に基づく broadcast delivery order は保証されない。
- Broadcast priority は global ではなく、同じ application process 内でのみ尊重される。
- Broadcast priority は自動的に `(SYSTEM_LOW_PRIORITY + 1, SYSTEM_HIGH_PRIORITY - 1)` の範囲に制限される。
- `SYSTEM_LOW_PRIORITY` / `SYSTEM_HIGH_PRIORITY` を broadcast priority として設定できるのは system component のみ。
- 複数 process に同じ broadcast intent の receiver を宣言して priority 順を期待しているアプリ、または他 process と broadcast priority 順序で協調しているアプリは影響を受ける可能性がある。
- process 間で協調が必要な場合は、別の coordination channel を使うべきである。

## 解釈（Interpretation）

この項目は targetSdkVersion 36 化の挙動変更ではなく、Android 16 OS 側の broadcast delivery / priority handling 変更である。`android:priority` / `IntentFilter#setPriority()` 自体は API として残るが、それを process 境界をまたいだ global ordering の仕組みとして使う前提は Android 16 では成立しない。

---

# 変更内容（What Changed）

## 変更点

- Android 16 の `BroadcastRecord` は `LIMIT_PRIORITY_SCOPE` ChangeId を持ち、priority values の影響範囲を process level に限定する。
- Android 15 では `Flags.limitPriorityScope()` が無効な場合、priority tranche ごとに前の tranche の receiver 完了を待つ旧 global priority blocking が残っていた。Android 16 ではこの fallback が削除され、`PlatformCompat` の change state に基づく process-scoped logic が常に使われる。
- Android 16 の `BroadcastFilter` は context-registered receiver の初期 priority を `calculateAdjustedPriority()` で補正する。non-core uid の priority が `SYSTEM_HIGH_PRIORITY` 以上なら `SYSTEM_HIGH_PRIORITY - 1`、`SYSTEM_LOW_PRIORITY` 以下なら `SYSTEM_LOW_PRIORITY + 1` に補正される。
- Android 15 では `BroadcastFilter.calculateAdjustedPriority()` の前に `Flags.restrictPriorityValues()` gate があった。Android 16 ではこの feature flag gate が削除される。
- Android 16 では `broadcasts_flags.aconfig` から `limit_priority_scope` と `restrict_priority_values` が削除され、これらの rollout flag による旧挙動分岐は見えなくなっている。

## 適用条件（Applicability）

### OS アップデート時の挙動（OS Update Behavior）

- Android 16 にアップデートしただけで適用されるか: Yes。公式 all apps ページの変更であり、AOSP の該当実装にも targetSdkVersion 36 gate は見つからない。
- targetSdkVersion に依存しない根拠: `BroadcastRecord.calculateBlockedUntilBeyondCount()` と `BroadcastFilter.calculateAdjustedPriority()` は receiver の `ApplicationInfo` を使って `PlatformCompat` ChangeId を確認するが、API 36 以上を条件にする annotation や targetSdkVersion 判定は確認できない。
- Android 15 以前での挙動: Android 15 tag には feature flag による旧挙動分岐が残っている。Android 16 では旧 fallback が削除され、priority scope / priority restriction が標準経路になっている。

### targetSdkVersion 36 以上での挙動（targetSdkVersion 36 Behavior）

- targetSdkVersion 36 以上で適用されるか: targetSdkVersion 36 は必要条件ではない。
- Android 16 / targetSdkVersion 35 と Android 16 / targetSdkVersion 36 の差: AOSP evidence 上、この項目では差を確認できない。
- Android 15 / targetSdkVersion 36 の挙動: Android 15 platform 上では Android 16 の `BroadcastRecord` / `BroadcastFilter` 差分は存在しない。targetSdkVersion 36 の値だけで Android 16 behavior が発生する evidence はない。

### その他の条件（Other Conditions）

- API usage: `Context#sendOrderedBroadcast()`、manifest receiver `android:priority`、runtime receiver `IntentFilter#setPriority()`。
- Process condition: 同一 process 内の priority ordering は維持されると公式文書は説明する。別 process / 別 app / 同一 app の別 process をまたぐ priority order は保証されない。
- Priority value condition: non-system app が `SYSTEM_HIGH_PRIORITY` / `SYSTEM_LOW_PRIORITY` またはそれを超える priority を使う場合、少なくとも context-registered receiver では app range 内に補正される。

---

# AOSP 調査（AOSP Investigation）

## 関連ファイル（Related Files）

- `frameworks-base/core/java/android/content/IntentFilter.java`
- `frameworks-base/core/java/android/content/pm/PackageParser.java`
- `frameworks-base/core/res/res/values/attrs_manifest.xml`
- `frameworks-base/services/core/java/com/android/server/am/BroadcastRecord.java`
- `frameworks-base/services/core/java/com/android/server/am/BroadcastFilter.java`
- `frameworks-base/services/core/java/com/android/server/am/BroadcastProcessQueue.java`
- `frameworks-base/services/core/java/com/android/server/am/BroadcastQueueImpl.java`
- `frameworks-base/services/core/java/com/android/server/am/BroadcastController.java`
- `frameworks-base/services/core/java/com/android/server/am/broadcasts_flags.aconfig`
- `frameworks-base/services/core/java/com/android/server/pm/resolution/ComponentResolver.java`
- `frameworks-base/services/tests/mockingservicestests/src/com/android/server/am/BroadcastRecordTest.java`
- `frameworks-base/services/tests/mockingservicestests/src/com/android/server/am/BroadcastFilterTest.java`
- `frameworks-base/core/api/current.txt`

## AOSP checkout hygiene

確認結果:
- `git -C frameworks-base status --short`: clean
- `git -C frameworks-base tag --list android-15.0.0_r36`: tag exists
- `git -C frameworks-base tag --list android-16.0.0_r4`: tag exists

ローカル未コミット変更を platform evidence と誤認するリスクは確認されなかった。

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル（File / symbol） | Android 15 の基準挙動（baseline） | Android 16 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `IntentFilter#setPriority(int)` / `getPriority()` | public API は priority を保持する。`SYSTEM_HIGH_PRIORITY` = 1000、`SYSTEM_LOW_PRIORITY` = -1000。 | public API signature は同等。setter 自体は clamp しない。 | アプリが runtime receiver priority を設定する API surface。 |
| `PackageParser#parseIntent()` | manifest の `android:priority` を読み、intent filter に設定する。 | 同等。 | manifest-declared receiver の priority 入力経路。 |
| `ComponentResolver.RESOLVE_PRIORITY_SORTER` | `ResolveInfo.priority` を high-to-low で sort する。 | 同等。 | manifest receiver の priority sort 経路。Android 16 でも receiver list 自体は priority を持つ。 |
| `BroadcastRecord.LIMIT_PRIORITY_SCOPE` | `Flags.limitPriorityScope()` が true の場合に process-scoped logic、false の場合に旧 global priority tranche blocking。 | feature flag fallback が削除され、`PlatformCompat` ChangeId state に基づく logic が標準経路になる。 | cross-process priority ordering が保証されなくなる中核実装。 |
| `BroadcastRecord.calculateBlockedUntilBeyondCount()` | 非 ordered prioritized broadcast では、旧 fallback が priority tranche ごとに前 tranche 完了を待たせる。 | change enabled の receiver だけなら `blockedUntilBeyondCount` は `-1` になり、priority tranche による global blocking を行わない。 | process 境界をまたいだ priority order 保証の有無を決める。 |
| `BroadcastProcessQueue` / `BroadcastQueueImpl` | `blockedUntilBeyondCount` に従って runnable / blocked を決める。 | `blockedUntilBeyondCount = -1` なら priority tranche blocking がない。 | BroadcastRecord の計算結果が実際の delivery scheduling に使われる根拠。 |
| `BroadcastFilter.RESTRICT_PRIORITY_VALUES` | `Flags.restrictPriorityValues()` が false なら priority を補正しない。 | feature flag gate が削除され、ChangeId enabled かつ non-core uid なら priority を app range に補正する。 | context-registered receiver の priority clamp 根拠。 |
| `BroadcastController#registerReceiverWithFeature()` | runtime receiver 登録時に `BroadcastFilter` を作成する。 | 同等。`BroadcastFilter` constructor で priority 補正が走る。 | `IntentFilter#setPriority()` で設定した値が system server に登録される経路。 |
| `broadcasts_flags.aconfig` | `limit_priority_scope` / `restrict_priority_values` fixed read-only flags が存在する。 | 2 flag が削除される。 | Android 16 で旧 feature flag 分岐が取り除かれたことの根拠。 |
| `BroadcastRecordTest` | Android 15 では flag enabled / disabled の test がある。 | Android 16 では `LIMIT_PRIORITY_SCOPE` enabled を default とする test があり、異なる priority の receiver でも prioritized 扱いにならないことを検証する。 | behavior の unit test evidence。 |
| `BroadcastFilterTest` | priority restriction の flag gate が存在する。 | app uid の `SYSTEM_HIGH_PRIORITY` / `SYSTEM_LOW_PRIORITY` が app range に補正され、system uid は保持される test がある。 | priority clamp と system exception の unit test evidence。 |

必須記入項目（Required context）:
- Entry point / caller: アプリが `sendOrderedBroadcast()` などで broadcast を送信し、ActivityManager / BroadcastQueue が receiver list を作成して各 process queue に配信する。
- Relevant class or service responsibility: `BroadcastRecord` は broadcast 1 件の receiver list、ordered / prioritized state、blocking state を保持する。`BroadcastFilter` は runtime registered receiver を表し、`ResolveInfo` は manifest-declared receiver を表す。
- Runtime path from app API / system event to changed code: manifest parse / runtime register -> receiver priority を保持 -> broadcast enqueue -> `BroadcastRecord.calculateBlockedUntilBeyondCount()` -> `BroadcastProcessQueue` が runnable / blocked を判定 -> receiver process へ dispatch。
- Why unrelated code paths were excluded: sticky broadcast、delivery group policy、background execution restriction、protected broadcast permission は broadcast delivery 全体には関係するが、本件の priority scope / priority clamp の主要 gate ではないため、必要範囲に限定して確認した。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
| Android 16 `BroadcastRecord.calculateBlockedUntilBeyondCount()` から `Flags.limitPriorityScope()` false 時の旧 global priority tranche blocking が削除される。 | Removed behavior / changed default。priority tranche による global waiting を標準では行わない。 | 「cross-process priority order is not guaranteed」を支持する。 | High |
| Android 16 `BroadcastRecord.LIMIT_PRIORITY_SCOPE` の javadoc は priority value の影響範囲を process level に限定すると説明する。 | Added / clarified behavior。AOSP 内の ChangeId 名とコメントが公式文書と一致する。 | 「same application process 内でのみ priority が尊重される」を支持する。 | High |
| Android 16 `BroadcastFilter.calculateAdjustedPriority()` から `Flags.restrictPriorityValues()` gate が削除される。 | Removed gate / changed default。context-registered receiver priority restriction が標準経路になる。 | 「priority clamping」を runtime receiver について支持する。 | High |
| `BroadcastFilterTest` は app uid の `SYSTEM_HIGH_PRIORITY` / `SYSTEM_LOW_PRIORITY` を app range に補正し、system uid は補正しないことを検証する。 | Test evidence。system component exception を確認できる。 | 「Only system components can set SYSTEM_* priority」を context-registered receiver について支持する。 | High |
| `PackageParser#parseIntent()` と `ComponentResolver` は manifest receiver priority を parse / sort するが、reviewed path では `SYSTEM_*` 境界への単純 clamp は見つからない。 | Missing / partial evidence。manifest priority の scope change は `BroadcastRecord` で確認できるが、manifest priority value clamp は追加確認余地がある。 | 公式の priority clamping 文言のうち manifest receiver clamp は Medium confidence。 | Medium |
| `IntentFilter` public API / `current.txt` に priority 関連 signature change は見つからない。 | No API signature change。runtime/server behavior change。 | 既存 API の意味合いが Android 16 system behavior で変わる。 | High |

必須分類（Required interpretation）:
- Added behavior: `LIMIT_PRIORITY_SCOPE` / `RESTRICT_PRIORITY_VALUES` による behavior が Android 16 の標準経路になる。
- Removed behavior: Android 15 の feature flag fallback と旧 global priority tranche blocking が Android 16 で削除される。
- Changed condition / gate: targetSdkVersion ではなく OS version / platform implementation / hidden ChangeId state に依存する。
- Changed default: priority scope は global ではなく process level。context-registered receiver priority は app range に補正される。
- No behavior change found: `IntentFilter#setPriority()` / `getPriority()` の public API signature 自体は変わらない。

---

# Facts / Observations / Hypotheses / Conclusions

## Facts

- 公式文書は Android 16 all apps 変更として、broadcast priority が process 境界をまたぐ delivery order を保証しなくなると説明している。
- `IntentFilter.SYSTEM_HIGH_PRIORITY` は 1000、`SYSTEM_LOW_PRIORITY` は -1000 である。
- `IntentFilter#setPriority(int)` は public API として priority を設定するが、setter 自体では clamp しない。
- `PackageParser#parseIntent()` は manifest `android:priority` を `IntentInfo` に設定する。
- `ComponentResolver.RESOLVE_PRIORITY_SORTER` は `ResolveInfo.priority` を high-to-low で sort する。
- `BroadcastRecord.LIMIT_PRIORITY_SCOPE` は ChangeId `371307720` で、priority values の scope を process level に限定するとコメントされている。
- `BroadcastRecord.calculateBlockedUntilBeyondCount()` は Android 16 で `Flags.limitPriorityScope()` 分岐を持たず、ChangeId state に基づいて blocking を計算する。
- `BroadcastFilter.RESTRICT_PRIORITY_VALUES` は ChangeId `371309185` で、non-system app の priority value を `SYSTEM_LOW_PRIORITY` と `SYSTEM_HIGH_PRIORITY` の内側に制限する。
- `BroadcastFilter.calculateAdjustedPriority()` は non-core uid の priority が `SYSTEM_HIGH_PRIORITY` 以上なら `SYSTEM_HIGH_PRIORITY - 1`、`SYSTEM_LOW_PRIORITY` 以下なら `SYSTEM_LOW_PRIORITY + 1` にする。
- Android 16 compat framework 公式一覧ページでは、`LIMIT_PRIORITY_SCOPE` / `RESTRICT_PRIORITY_VALUES` の entries は検索確認できなかった。

## Observations

- Android 16 の変更は targetSdkVersion 36 gate ではなく、all apps 向けの platform behavior change と見るのが妥当である。
- 同一 process 内では receiver list / process queue の中で priority order が意味を持つが、別 process では `blockedUntilBeyondCount = -1` により priority tranche が global blocking を作らない。
- 同一 app でも receiver を別 process に置く場合、`processName` が異なるため same application process ではなく、cross-process non-guarantee の対象になる。
- context-registered receiver の priority clamp は AOSP source と unit test で明確に確認できる。
- manifest-declared receiver の priority は parse / sort されるが、今回確認した範囲では context-registered receiver と同じ `BroadcastFilter.calculateAdjustedPriority()` 経路は通らない。
- `abortBroadcast()`、`setResultCode()`、`setResultData()`、`setResultExtras()` のような ordered broadcast result 操作を cross-process priority ordering と組み合わせる設計は、Android 16 では順序前提を置くべきではない。

## Hypotheses

- manifest-declared receiver の priority clamp は、AOSP の別 module / PackageManager policy / platform compat state で補完されている可能性がある。ただし、`frameworks-base` の reviewed path では context-registered receiver ほど直接的な証拠は得られていない。
- Android 16 で cross-process delivery order が非保証になる主な実害は、receiver 実行順の揺らぎそのものよりも、priority を coordination primitive として使っていた初期化順、result extras、abort、依存更新の前提が崩れることにある。
- system component の priority exception は `UserHandle.isCore(owningUid)` を使う runtime receiver 経路で明確だが、manifest receiver では privileged / protected action policy と組み合わさる可能性がある。

## Conclusions

- この変更の primary classification は `OS_UPDATE_ALL_APPS` である。
- Android 16 では、broadcast receiver priority を process 境界をまたいだ global ordering mechanism として使ってはいけない。
- targetSdkVersion 36 に上げた時の影響ではなく、Android 16 OS 上で ordered broadcast / priority receiver を使う場合の影響として顧客に説明する必要がある。
- 同一 process 内の receiver ordering は維持される前提で扱えるが、同一 app の別 process、別 app、別 uid では priority order を保証しない設計に変更する必要がある。
- process 間協調は broadcast priority ではなく、明示的な IPC / service / provider / queue / WorkManager などに移行するべきである。

---

# 期待挙動マトリクス（Expected Behavior Matrix）

## OS / targetSdkVersion matrix

| OS / targetSdkVersion | 期待挙動（Expected behavior） | 顧客説明 |
| --- | --- | --- |
| Android 16 / targetSdkVersion 35 | ordered broadcast priority scope change が適用される。cross-process priority order は保証されない。 | OS update impact。targetSdkVersion 36 化ではない。 |
| Android 16 / targetSdkVersion 36 | targetSdkVersion 35 と同じ platform behavior。 | targetSdkVersion 36 にしたことだけで追加差分が出る evidence はない。 |
| Android 15 / targetSdkVersion 36 | Android 16 の標準経路は存在しない。Android 15 tag には feature flag 分岐が残る。 | Android 15 上で targetSdkVersion 36 にしても Android 16 behavior とは同一視しない。 |

## Required scenario matrix

| Scenario | Android 16 期待挙動 | Notes |
| --- | --- | --- |
| Android 16 / targetSdkVersion 35 / ordered broadcast | 影響あり。targetSdkVersion と無関係に platform policy が適用される。 | `OS_UPDATE_ALL_APPS`。 |
| Android 16 / targetSdkVersion 36 / ordered broadcast | 影響あり。targetSdkVersion 35 と同じ。 | target gate evidence なし。 |
| Android 16 / unordered broadcast | priority による順序前提は置けない。 | manifest doc でも async broadcasts は priority order を無視する。 |
| Android 16 / manifest-declared receiver / `android:priority` | receiver list は priority を持つが、cross-process order は保証されない。 | priority clamp は reviewed evidence が partial。 |
| Android 16 / context-registered receiver / `IntentFilter#setPriority()` | priority は登録時に app range へ補正され得る。cross-process order は保証されない。 | `BroadcastFilter` evidence。 |
| Android 16 / same process receivers with different priorities | priority は同一 process 内で尊重される。 | 公式文書 + process queue model。 |
| Android 16 / same app but different process receivers | cross-process 扱い。priority order は保証されない。 | `processName` が異なる。 |
| Android 16 / different apps / different uids receivers | cross-process / cross-app 扱い。priority order は保証されない。 | global coordination には使えない。 |
| Android 16 / cross-process priority ordering expected by app | 互換性リスクあり。順序依存を除去する必要がある。 | 明示的 IPC へ移行。 |
| Android 16 / priority within allowed app range | 同一 process 内では意味を持つ。cross-process では保証されない。 | app range 内でも scope は local。 |
| Android 16 / priority above `SYSTEM_HIGH_PRIORITY` | non-system context-registered receiver では `SYSTEM_HIGH_PRIORITY - 1` に補正される。 | manifest receiver は追加検証余地。 |
| Android 16 / priority below `SYSTEM_LOW_PRIORITY` | non-system context-registered receiver では `SYSTEM_LOW_PRIORITY + 1` に補正される。 | manifest receiver は追加検証余地。 |
| Android 16 / `SYSTEM_HIGH_PRIORITY` requested by non-system app | non-system context-registered receiver では使用不可。 | app range に補正。 |
| Android 16 / `SYSTEM_LOW_PRIORITY` requested by non-system app | non-system context-registered receiver では使用不可。 | app range に補正。 |
| Android 16 / `SYSTEM_HIGH_PRIORITY` used by system component | system / core uid では保持される。 | `UserHandle.isCore()` evidence。 |
| Android 16 / `SYSTEM_LOW_PRIORITY` used by system component | system / core uid では保持される。 | `UserHandle.isCore()` evidence。 |
| Android 16 / `abortBroadcast()` dependency | cross-process priority ordering に依存する abort 前提は危険。 | ordered broadcast semantics と順序前提を分けて検証。 |
| Android 16 / `setResultExtras()` ordering dependency | cross-process priority ordering に依存する result mutation は危険。 | result propagation の実機確認が必要。 |
| Android 15 / targetSdkVersion 36 / same app behavior | Android 16 behavior は適用されない。 | technically comparable な baseline として検証。 |
| app migrates to explicit IPC / coordination channel | 推奨。順序保証を明示的な protocol に移す。 | service / provider / queue など。 |
| app continues relying on cross-process priority ordering | 互換性リスクあり。 | Android 16 で順序非保証。 |

---

# 影響対象（Who Is Affected）

- ordered broadcast を送信するアプリ。
- ordered broadcast を受信するアプリ。
- `android:priority` を指定する manifest receiver を持つアプリ。
- `IntentFilter#setPriority()` を使う context-registered receiver を持つアプリ。
- 複数 process に receiver を分けているアプリ。
- 同一 broadcast intent を複数 process / 複数 app で処理するアプリ。
- receiver priority で初期化順序 / 依存順序を制御しているアプリ。
- `abortBroadcast()` に依存するアプリ。
- ordered broadcast result extras / result code / result data の順序に依存するアプリ。
- SDK / library / plugin が broadcast receiver priority を設定するアプリ。
- system / privileged component と連携するアプリ。
- cross-process coordination を broadcast priority に依存しているアプリ。
- explicit IPC / service / provider / WorkManager / app-internal queue へ移行すべきアプリ。

低影響または非影響になりやすいケース:
- ordered broadcast を使わないアプリ。
- unordered broadcast で順序に依存しないアプリ。
- explicit broadcast で単一 receiver のみを対象にするアプリ。
- receiver が同一 application process 内にあり、その process 内の priority order だけに依存するアプリ。
- priority を設定していても cross-process order / result / abort sequencing に依存しないアプリ。
- 明示的 IPC や app-internal queue で順序制御しているアプリ。

---

# 推奨対応（Recommended Action Candidates）

- broadcast receiver priority を process 間 coordination の仕組みとして使っている箇所を棚卸しする。
- 同一 app の複数 process receiver、別 app receiver、SDK / plugin receiver が同じ intent を処理している場合、delivery order への依存を削除する。
- 初期化順序や依存順序が必要な場合は、bound service、ContentProvider、AIDL / Messenger、明示的 intent service、WorkManager chain、app-internal queue、shared storage + lock などに移行する。
- `abortBroadcast()` や `setResultExtras()` を priority order 前提で使っている場合、同一 process 内に閉じるか、明示的 protocol に置き換える。
- `SYSTEM_HIGH_PRIORITY` / `SYSTEM_LOW_PRIORITY` を app が使っていないか確認し、普通の app priority range に収める。
- SDK / library が `IntentFilter#setPriority()` や manifest `android:priority` を設定していないか確認する。

---

# テスト観点（Test Guidance）

- Android 15 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 36。
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較。
- `sendOrderedBroadcast()`。
- unordered broadcast。
- manifest receiver `android:priority`。
- context-registered receiver `IntentFilter#setPriority()`。
- same process receiver ordering。
- same app different process receiver ordering。
- different app / different uid receiver ordering。
- priority high-to-low ordering within same process。
- cross-process ordering non-guarantee。
- priority clamping above `SYSTEM_HIGH_PRIORITY`。
- priority clamping below `SYSTEM_LOW_PRIORITY`。
- `SYSTEM_HIGH_PRIORITY` / `SYSTEM_LOW_PRIORITY` use by non-system app。
- `SYSTEM_HIGH_PRIORITY` / `SYSTEM_LOW_PRIORITY` use by system component。
- `abortBroadcast()` behavior。
- `setResultCode()` / `setResultData()` / `setResultExtras()` propagation。
- protected broadcast / privileged receiver cases。
- process startup timing / cold start receiver timing。
- logs / `dumpsys activity broadcasts` / broadcast delivery trace。
- migration to explicit IPC / service / provider / WorkManager / app-internal queue。

---

# 顧客向け説明（Customer-facing Explanation）

Android 16 では、broadcast receiver priority は global な順序制御として扱えなくなります。`android:priority` や `IntentFilter#setPriority()` による順序は同じ application process 内では意味を持ちますが、別 process や別アプリをまたぐ delivery order は保証されません。

これは targetSdkVersion 36 に上げた時だけの変更ではなく、Android 16 に OS アップデートした端末上で ordered broadcast / priority receiver を使うアプリに影響し得ます。targetSdkVersion 35 のままでも、複数 process や複数アプリ間の順序を broadcast priority に依存している場合は見直しが必要です。

process 間の順序制御や依存関係は、broadcast priority ではなく、明示的な IPC、service、ContentProvider、WorkManager、app-internal queue などで表現してください。

---

# 未確認点・リスク（Open Questions / Residual Risk）

- manifest-declared receiver の `android:priority` について、公式文書は priority clamping を述べているが、今回確認した `frameworks-base` 経路では context-registered receiver と同じ単純な `SYSTEM_*` 境界 clamp は直接確認できなかった。manifest receiver については process-scope 変更の evidence はあるが、priority value clamp は追加調査余地がある。
- `LIMIT_PRIORITY_SCOPE` / `RESTRICT_PRIORITY_VALUES` は AOSP `@ChangeId` として確認できるが、Android 16 compat framework 公式一覧では検索確認できなかった。app developer が一般的な compat toggle として扱えるとは判断しない。
- `abortBroadcast()` / result extras の影響は、アプリがどの broadcast をどの receiver 配置で使っているかに依存する。特定アプリの migration 判断には実機または integration test が必要である。

---

# Human Decision

最終優先度（Final Priority）:
- Critical / High / Medium / Low

判断（Decision）:
- Explain / Monitor / Ignore / Further investigation required

補足:
- 最終優先度、顧客通知要否、release readiness は repository owner が判断する。

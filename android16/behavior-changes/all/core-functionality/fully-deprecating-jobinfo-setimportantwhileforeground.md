# Fully deprecating JobInfo#setImportantWhileForeground 調査レポート

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:

Previous targetSdkVersion:
- 35

Target targetSdkVersion:
- 36

### Behavior Change 文書（Behavior Change Source）

Document:
- https://developer.android.com/about/versions/16/behavior-changes-all#jobinfo-setimportantwhileforeground

Page:
- Behavior changes: all apps

Category:
- Core functionality

Section:
- Fully deprecating JobInfo#setImportantWhileForeground

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `OS_UPDATE_ALL_APPS`

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 16 に OS アップデートしただけで適用されるか | Yes | 公式 all apps ページに掲載。Android 16 の `JobInfo.Builder#setImportantWhileForeground()` は targetSdkVersion を見ず常に ignored。 |
| targetSdkVersion 36 以上が必要か | No | AOSP の `JobInfo` / JobScheduler controller 経路に targetSdkVersion 36 gate は見つからない。 |
| 追加の実行時条件があるか | Yes | `JobInfo.Builder#setImportantWhileForeground(true)` または `JobInfo#isImportantWhileForeground()` を使う場合。 |
| `setImportantWhileForeground(true)` は flag を立てるか | No | Android 16 の builder は warning log を出して `return this` するだけで、`FLAG_IMPORTANT_WHILE_FOREGROUND` を set しない。 |
| `isImportantWhileForeground()` は true を返すか | No | Android 16 の実装は常に `return false`。 |
| Compat Change ID が関係するか | No public compat entry found | 公式 compat framework ページでは該当 Change ID を確認できない。Android 15 にあった exported aconfig flag は Android 16 でも残るが、public API 実装は flag 条件なしで no-op 化されている。 |

### 調査日（Investigation Date）

2026-07-04

### 信頼度（Confidence）

- High

理由:
- 公式 all apps 文書の該当セクションを再確認し、依頼された Original statements と一致することを確認した。
- AOSP `JobInfo` の Android 15 / Android 16 tag 差分で、`setImportantWhileForeground()` が conditional behavior から unconditional no-op に変わり、`isImportantWhileForeground()` が unconditional false に変わったことを確認した。
- `DeviceIdleJobsController`、`QuotaController`、`ThermalStatusRestriction` から important-while-foreground 参照が削除されたことを確認した。
- targetSdkVersion 36 gate は該当経路に見つからない。

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
- targetSdkVersion: 条件なし。35 と 36 の両方で同じ platform behavior が期待される。
- API condition: `JobInfo.Builder#setImportantWhileForeground(boolean)` または `JobInfo#isImportantWhileForeground()` を使う。
- Impact condition: important-while-foreground による priority / quota / doze relaxation / thermal restriction 例外を期待している。

Compat framework:
- Public compat framework page: 2026-07-04 時点で `setImportantWhileForeground`、`ImportantWhileForeground`、`ignore_important_while_foreground`、`374175032` の該当 entry は見つからない。
- AOSP aconfig flag:
  - `android.app.job.ignore_important_while_foreground`
  - bug: `374175032`
  - description: important-while-foreground flag と関連 API を effective でなくする。
- Android 15 tag ではこの aconfig flag が API / controller 経路の条件として使われていた。
- Android 16 tag では public API 実装が flag 条件なしで no-op / false になっている。

分類信頼度（Classification confidence）:
- High

分類根拠（Classification evidence）:
- Official documentation page: `behavior-changes-all` の `Fully deprecating JobInfo#setImportantWhileForeground`。
- AOSP targetSdk gate: `JobInfo`、`DeviceIdleJobsController`、`QuotaController`、`ThermalStatusRestriction` の該当経路には見つからない。
- Expected behavior: Android 16 / targetSdkVersion 35 と Android 16 / targetSdkVersion 36 で同じ。

---

# エグゼクティブサマリー（Executive Summary）

Android 16では、`JobInfo.Builder#setImportantWhileForeground(true)`は呼び出しても動作を変えなくなる。`FLAG_IMPORTANT_WHILE_FOREGROUND`は設定されず、warning logを出してbuilder自体を返すだけになる。`JobInfo#isImportantWhileForeground()`も常に`false`を返す。

これは targetSdkVersion 36 化による変更ではなく、Android 16 all apps の OS behavior change として扱う。targetSdkVersion 35 のままでも、Android 16 上では同じ挙動が期待される。

Android 12以降、このAPIは既にdeprecatedだった。今回のポイントはdeprecation warningではなく、Android 15ではflag状態によって残っていたimportant-while-foregroundの処理経路が、Android 16でAPIとJobScheduler controllerの両方から除去されたこと。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statements）

公式文書では次を説明している。

- `JobInfo.Builder#setImportantWhileForeground(boolean)` は、scheduling app が foreground にいる間、または background restriction から一時的に exempt されている間の job の重要性を示す。
- この method は Android 12 / API level 31 から deprecated。
- Android 16以降、このmethodは実際の動作を変えず、呼び出しはignoredになる。
- この functionality removal は `JobInfo#isImportantWhileForeground()` にも適用される。
- Android 16 以降、`JobInfo#isImportantWhileForeground()` を呼ぶと `false` を返す。

## ドキュメント差分確認（Documentation Delta）

- 依頼された Original statements と、2026-07-04 時点で確認した公式本文に実質的な差分はない。
- 公式ページは `behavior-changes-all` であり、targetSdkVersion 36 専用ページではない。
- 公式本文は targetSdkVersion gate を述べていない。

---

# 変更内容（What Changed）

## Android 12 からの deprecation と Android 16 の functional removal は別

`setImportantWhileForeground(boolean)` は Android 12 から deprecated だった。Android 15 tag の API surface でも `setImportantWhileForeground(boolean)` と `isImportantWhileForeground()` は `@Deprecated` として公開されている。

Android 16の変更は、deprecated APIが残っていること自体ではなく、runtimeで挙動を変える処理が削除されたこと。Android 16 tagでは:

- `setImportantWhileForeground(boolean)` は `importantWhileForeground` の値に関係なく warning log を出して `return this` する。
- `isImportantWhileForeground()` は内部 flags を読まず、常に `false` を返す。
- JobScheduler controller 側も `FLAG_IMPORTANT_WHILE_FOREGROUND` を特別扱いしない。

## Android 15 baseline

Android 15 tag では、`Flags.ignoreImportantWhileForeground()` が false の場合、従来挙動が残っていた。

- `isImportantWhileForeground()` は `Flags.ignoreImportantWhileForeground()` が true なら false、false なら `flags & FLAG_IMPORTANT_WHILE_FOREGROUND` を返す。
- `setImportantWhileForeground(true)` は `mFlags |= FLAG_IMPORTANT_WHILE_FOREGROUND` し、priority が default の場合は `PRIORITY_HIGH` に上げる。
- `setImportantWhileForeground(false)` は flag を落とし、必要に応じて priority を default に戻す。
- `DeviceIdleJobsController` は flag が立っている job を foreground uid / temp whitelist 条件で doze 中に許可する `allowInIdle` 経路を持つ。
- `QuotaController` は privileged state かつ important job の判定に `FLAG_IMPORTANT_WHILE_FOREGROUND` を含め、runtime-free quota max limit を返す経路を持つ。
- `ThermalStatusRestriction` は foreground-service bias と important-while-foreground の組み合わせを thermal restriction 判定に使う経路を持つ。

## Android 16 target

Android 16 tagでは、上記の実際に挙動へ影響する処理経路が削除または無効化されている。

- `JobInfo#isImportantWhileForeground()` は `return false` のみ。
- `Builder#setImportantWhileForeground(boolean)` は warning log のみで、`mFlags` や `mPriority` を変更しない。
- `DeviceIdleJobsController` は `allowInIdle` の important-while-foreground 判定を削除し、doze 中に許可する条件は device idle mode ではないこと、または power allowlist だけになる。
- `QuotaController` は important job 判定から `FLAG_IMPORTANT_WHILE_FOREGROUND` を削除し、`jobStatus.getEffectivePriority() >= JobInfo.PRIORITY_HIGH` のみを見る。
- `ThermalStatusRestriction` は `job.getJob().isImportantWhileForeground()` を使った foreground job exception を削除する。

## API surface

- Android 15 `core/api/current.txt`:
  - `isImportantWhileForeground()` は `@Deprecated @FlaggedApi("android.app.job.ignore_important_while_foreground")`。
  - `setImportantWhileForeground(boolean)` は `@Deprecated`。
- Android 16 `core/api/current.txt`:
  - `isImportantWhileForeground()` は `@Deprecated` のみ。`@FlaggedApi` が外れている。
  - `setImportantWhileForeground(boolean)` は引き続き `@Deprecated`。

この API surface 差分は、Android 16 で `isImportantWhileForeground()` が flagged optional API ではなく public deprecated API として存在しつつ、常に false を返すことを示す。

---

# AOSP 調査（AOSP Investigation）

## 関連ファイル（Related Files）

- `frameworks-base/apex/jobscheduler/framework/java/android/app/job/JobInfo.java`
- `frameworks-base/apex/jobscheduler/framework/aconfig/job.aconfig`
- `frameworks-base/apex/jobscheduler/service/java/com/android/server/job/controllers/DeviceIdleJobsController.java`
- `frameworks-base/apex/jobscheduler/service/java/com/android/server/job/controllers/QuotaController.java`
- `frameworks-base/apex/jobscheduler/service/java/com/android/server/job/restrictions/ThermalStatusRestriction.java`
- `frameworks-base/core/api/current.txt`

## Checkout hygiene

- `frameworks-base` は status 確認時点で clean。
- `android-15.0.0_r36` と `android-16.0.0_r4` tag が存在することを確認した。
- local working tree の未追跡ファイルや別作業ファイルは AOSP evidence として扱っていない。

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル（File / symbol） | Android 15 baseline | Android 16 behavior | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `JobInfo#isImportantWhileForeground()` | `Flags.ignoreImportantWhileForeground()` が true なら false、false なら `FLAG_IMPORTANT_WHILE_FOREGROUND` を返す。`@FlaggedApi` 付き。 | `return false` のみ。`@FlaggedApi` は外れ、`@Deprecated` の public API。 | 公式文書の「Starting in Android 16 ... returns false」を直接実装している。 |
| `JobInfo.Builder#setImportantWhileForeground(boolean)` | flag が無効なら `mFlags` を更新し、true の場合は default priority を high にする。flag が有効なら ignored。 | 常に warning log を出し、`mFlags` / `mPriority` を変更せず `return this`。 | 公式文書の「calling this method will be ignored」を直接実装している。 |
| `JobInfo.FLAG_IMPORTANT_WHILE_FOREGROUND` | hidden flag として存在し、builder / controller が参照する。 | hidden flag 自体は残るが、public builder は通常この flag を立てない。 | 互換上の定数残存と runtime no-op を分ける根拠。 |
| `JobInfo` parcel / flags | `flags` は parcel / builder / copy constructor で保持される。 | 同様に `flags` は保持されるが、`setImportantWhileForeground()` は flag を立てない。 | 既存 serialized / internal flag と public API behavior を分ける根拠。 |
| `job.aconfig` `ignore_important_while_foreground` | exported flag として存在し、API / controller 経路の条件。 | exported flag は残るが、public API 実装は flag 条件なしの no-op / false。 | Android 15 の flagged behavior と Android 16 の unconditional behavior を分ける根拠。 |
| `DeviceIdleJobsController#updateTaskStateLocked()` | `allowInIdle` に important-while-foreground flag を含める。 | `allowInIdle` 経路が削除され、whitelist / idle mode のみを見る。 | doze relaxation と temporary allowlist 期待が無効になる根拠。 |
| `QuotaController#getMaxJobExecutionTimeMsLocked()` | privileged state かつ high priority、または important-while-foreground flag の job に runtime-free quota max limit を返す。 | important 判定は effective priority >= high のみ。flag 参照は削除。 | important-while-foreground による quota / runtime 特別扱いが消える根拠。 |
| `ThermalStatusRestriction#isJobRestricted()` | thermal restrictionのforeground job例外に`isImportantWhileForeground()`を使う。 | `isImportantWhileForeground()`を使う分岐が削除。 | thermal restrictionの例外として扱われなくなる根拠。 |
| `core/api/current.txt` | `isImportantWhileForeground()` は `@Deprecated @FlaggedApi(...)`。 | `isImportantWhileForeground()` は `@Deprecated` のみ。 | API surface 上の Android 16 public behavior 固定化の根拠。 |

必須記入項目（Required context）:
- Entry point / caller: app または library が `new JobInfo.Builder(...).setImportantWhileForeground(true).build()` で `JobInfo` を作成し、`JobScheduler#schedule(JobInfo)` に渡す。
- Runtime path: `JobInfo.Builder` -> `JobInfo` -> `JobSchedulerService` / `DeviceIdleJobsController` / `QuotaController` / `ThermalStatusRestriction`。
- Why relevant: 公式文書が述べるAPI call ignored、getter false、jobをforeground importanceに基づいて特別扱いする挙動を直接実装・参照している経路。
- Excluded code paths: Android 16 JobScheduler quota optimizations の top-started job / foreground-service-concurrent job quota enforcement は別 Behavior Change。`setImportantWhileForeground()` の代替ではなく、foreground state と quota の一般的な扱いなので混同しない。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 種別 | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- | --- |
| `isImportantWhileForeground()` が flag 条件つき getter から unconditional `return false` に変更。 | Changed default / removed behavior | getter は Android 16 で常に false。 | 公式の「method returns false」を支持。 | High |
| `setImportantWhileForeground()` が flag を set / clear する実装から warning log + `return this` に変更。 | Removed behavior | setter は引数に関係なく ignored。priority も変えない。 | 公式の「calling this method will be ignored」を支持。 | High |
| `DeviceIdleJobsController` から `allowInIdle` と flag tracking が削除。 | Removed behavior | doze 中の important-while-foreground 例外がなくなる。 | foreground / temp allowlist 中の relaxation 期待に影響。 | High |
| `QuotaController` の important 判定から `FLAG_IMPORTANT_WHILE_FOREGROUND` が削除。 | Removed behavior | quota-free max limit 判定に important-while-foreground flag が使われない。 | priority / quota 期待に影響。 | High |
| `ThermalStatusRestriction`から`isImportantWhileForeground()`分岐が削除。 | Removed behavior | thermal restrictionの例外に使われない。 | scheduler restrictionへ実際に与える影響を補強。 | Medium |
| API surface で `isImportantWhileForeground()` の `@FlaggedApi` が外れ、deprecated public API として残る。 | API surface changed | API は削除ではなく残存し、戻り値 behavior が固定化。 | migration では compile break ではなく runtime behavior 変更として説明する根拠。 | High |
| targetSdkVersion 36 gate が見つからない。 | No target gate | Android 16 上の all-apps behavior。 | `OS_UPDATE_ALL_APPS` を支持。 | High |

---

# Original Statements Verification

| Original statement | 判定 | Evidence | Notes |
| --- | --- | --- | --- |
| `setImportantWhileForeground(boolean)` indicates job importance while scheduling app is foreground or temporarily exempted. | Verified for historical semantics | Android 15 `JobInfo` javadoc and implementation; `DeviceIdleJobsController` / `QuotaController` historical use. | Android 16ではこのsemanticsに基づく特別扱いは残らない。 |
| Deprecated since Android 12. | Verified by API docs / source javadoc | `@Deprecated` is present in Android 15 and Android 16 API surface. | Android 12 tag までは今回の tag diff 対象外だが、AOSP current API でも deprecated 状態は確認。 |
| Starting Android 16, no longer functions effectively and call is ignored. | Verified | Android 16 `setImportantWhileForeground()` logs warning and returns without touching `mFlags` / `mPriority`. | targetSdkVersion 条件なし。 |
| Removal also applies to `JobInfo#isImportantWhileForeground()`. | Verified | Android 16 getter no longer checks flags. | API remains present. |
| Starting Android 16, getter returns false. | Verified | Android 16 `isImportantWhileForeground()` is `return false;`. | targetSdkVersion 条件なし。 |

---

# Facts / Observations / Hypotheses / Conclusions

## Facts

- 公式文書は all apps ページにこの項目を掲載している。
- Android 16 `JobInfo.Builder#setImportantWhileForeground(boolean)` は `importantWhileForeground` の引数を使わず、warning log を出して `return this` する。
- Android 16 `JobInfo#isImportantWhileForeground()` は常に false を返す。
- Android 16のJobScheduler controller側から、important-while-foreground flagを実際の判定に使う参照が削除されている。
- Android 16 の該当経路に targetSdkVersion 36 gate は見つからない。
- `JobInfo.Builder#setExpedited(boolean)` と `JobInfo.Builder#setUserInitiated(boolean)` は Android 16 API surface に存在し、`setUserInitiated(boolean)` は `RUN_USER_INITIATED_JOBS` permission を要求する。

## Observations

- Android 15 tag にも `ignore_important_while_foreground` aconfig flag は存在し、flag enabled の場合は API no-op / false の準備があった。
- Android 16 では API 実装が aconfig flag 条件から外れ、常に ignored / false になる。
- hidden `FLAG_IMPORTANT_WHILE_FOREGROUND` は Android 16 にも残るが、public builder が flag を立てないため、通常の app scheduling path では新規 job に反映されない。
- `JobInfo`の`flags` fieldはparcel / copyで保持されるため、内部的・互換的に古いflagが存在する可能性はある。ただしcontroller側で特別扱いされないため、実際のスケジューリング動作には影響しない。

## Hypotheses

- WorkManager は通常 direct `setImportantWhileForeground()` を developer API として露出しないため、影響は direct JobScheduler または古い SDK / library が内部でこの deprecated API を呼ぶケースに偏る可能性が高い。
- Android 15 でも device の aconfig flag 状態によっては同様に no-op 化されていた可能性があるが、本調査では Android 16 all apps 変更として、Android 16 tag の unconditional behavior を確認した。
- 既存 persisted job に important-while-foreground flag が含まれていても、Android 16 controller 側で特別扱いされないため、期待された doze / quota / thermal の例外は得られない可能性が高い。

## Conclusions

- 本項目は `OS_UPDATE_ALL_APPS` と分類する。Android 16 上では targetSdkVersion 35 / 36 に関係なく、該当 API は ignored / false になる。
- 顧客向けには「targetSdkVersion 36に上げた時の影響」ではなく、「Android 16 OS上でdeprecated JobInfo APIを呼び出してもスケジューリング動作が変わらなくなる影響」として説明する。
- `setImportantWhileForeground(true)` による優先度上げ、doze 中の relaxation、quota / thermal restriction 例外を期待する設計は見直す必要がある。
- 代替候補は用途に応じて `setExpedited(true)`、`setUserInitiated(true)`、foreground service、または通常 job + stop reason / pending reason logging で検討する。

---

# 期待挙動マトリクス（Expected Behavior Matrix）

## OS / targetSdkVersion matrix

| OS / targetSdkVersion | 期待挙動 | 分類上の扱い |
| --- | --- | --- |
| Android 15 / targetSdkVersion 35 | tag 上は deprecated API。`ignore_important_while_foreground` flag 状態により挙動が変わり得る。 | Android 16 behavior change の baseline。 |
| Android 16 / targetSdkVersion 35 | `setImportantWhileForeground()` は ignored。`isImportantWhileForeground()` は false。 | OS update impact。 |
| Android 16 / targetSdkVersion 36 | target 35 と同じ。 | targetSdkVersion 36 固有 impact ではない。 |
| Android 15 / targetSdkVersion 36 | 技術的には compile SDK / target SDK と platform 実装を分けて検証。Android 16 unconditional behavior は期待しない。 | 比較用。 |

## Detailed scenario matrix

| シナリオ | Android 16 期待挙動 |
| --- | --- |
| targetSdkVersion 35 / `setImportantWhileForeground(true)` | ignored。flag / priority は変更されない。 |
| targetSdkVersion 36 / `setImportantWhileForeground(true)` | target 35 と同じ。 |
| `setImportantWhileForeground(false)` | ignored。既にbuilder上でflagが立っていない限り、実際の動作に変化なし。 |
| `JobInfo#isImportantWhileForeground()` | 常に false。 |
| direct JobScheduler job | deprecated API を使っても important-while-foreground の特別扱いは得られない。 |
| WorkManager task | AOSP では Jetpack 内部実装までは確認不可。WorkManager がこの deprecated API に依存していなければ低影響。 |
| app in foreground when scheduling | この API による特別扱いはない。Android 16 JobScheduler quota optimizations の top state behavior は別項目。 |
| app in background when scheduling | この API による特別扱いはない。 |
| temporary background restriction exemption | `setImportantWhileForeground(true)` では doze relaxation を期待できない。 |
| job expected to be important while foreground | 期待は成立しない。expedited / user-initiated / FGS 等へ設計変更を検討。 |
| priority / quota relying on important-while-foreground | `FLAG_IMPORTANT_WHILE_FOREGROUND` は quota 判定の important condition から外れる。 |
| expedited job alternative | `setExpedited(true)` は引き続き API として存在。用途・quota・制約を別途評価。 |
| user-initiated data transfer job alternative | `setUserInitiated(true)` は `RUN_USER_INITIATED_JOBS` permission が必要。user-visible transfer に適用候補。 |
| foreground service alternative | ユーザー可視の継続処理では候補。ただし FGS policy と Android 16 quota optimizations は別途確認。 |
| Android 15 / targetSdkVersion 36 / `setImportantWhileForeground(true)` | baseline。flag 状態により従来挙動が残る可能性あり。 |
| Android 15 / targetSdkVersion 36 / `isImportantWhileForeground()` | baseline。flag 状態により false または flag value。 |
| Android 12-15 deprecated API baseline | deprecated API として扱う。Android 16 の functional removal とは分ける。 |

---

# 影響対象（Affected Apps）

- `JobScheduler` を直接使うアプリ。
- `JobInfo.Builder#setImportantWhileForeground(true)` を呼ぶアプリ。
- `JobInfo#isImportantWhileForeground()` の戻り値に依存するアプリ。
- foreground 中の job を重要扱いにする前提のアプリ。
- temporary background restriction exemption 中の job behavior に依存するアプリ。
- priority / quota / timing を important-while-foreground に依存しているアプリ。
- legacy JobScheduler code を持つアプリ。
- SDK / library が `setImportantWhileForeground(true)` を内部で呼ぶアプリ。
- WorkManager を使うアプリ。ただし影響は WorkManager または SDK が deprecated API を内部利用している場合に限定して確認する。
- expedited jobs / user-initiated data transfer jobs / foreground services へ移行すべきアプリ。
- battery optimization / background execution 制限に敏感なアプリ。

---

# 非影響・低影響ケース（Expected Non-impact / Lower-impact Cases）

- `setImportantWhileForeground()` を使っていないアプリ。
- Android 12 以降の deprecation に従って既に移行済みのアプリ。
- important-while-foreground による priority / quota / doze relaxation を前提にしていない job。
- 用途に応じて expedited job、user-initiated data transfer job、foreground service へ既に移行済みのアプリ。
- WorkManager を使っていて、内部的にもこの deprecated API に依存していないケース。

---

# 推奨アクション候補（Recommended Action Candidates）

最終優先度や採用判断は repository owner / 開発チームが決める。

1. `setImportantWhileForeground(` と `isImportantWhileForeground(` の利用箇所をコード検索する。
2. SDK / library dependency も含めて deprecated API の内部利用有無を確認する。
3. API 呼び出しが見つかった場合、その job が何を期待していたかを分類する。
4. 「すぐ実行すべき短時間 work」は `setExpedited(true)` への移行を検討する。
5. 「ユーザーが明示的に開始した data transfer」は `setUserInitiated(true)` と `RUN_USER_INITIATED_JOBS` permission を検討する。
6. 「ユーザー可視で継続する処理」は foreground service が適切かを policy と合わせて確認する。
7. Android 16 実機 / emulator で `dumpsys jobscheduler`、execution timing、quota、stop reason を比較する。
8. Android 16 JobScheduler quota optimizations と混同せず、top state / FGS concurrent job quota は別項目として評価する。

---

# テスト観点（Test Points）

| 観点 | 確認内容 |
| --- | --- |
| OS / targetSdkVersion | Android 15 target 35、Android 16 target 35、Android 16 target 36、可能なら Android 15 target 36 を比較。 |
| setter true | `setImportantWhileForeground(true)` 後に `JobInfo#isImportantWhileForeground()` が false になること。 |
| setter false | `setImportantWhileForeground(false)` が behavior change を起こさないこと。 |
| dumpsys / parcel / persistence | scheduled job の flags / priority / dumpsys 表示を確認。 |
| app foreground state | foreground scheduling でもこの API による特別扱いがないこと。 |
| app background state | background scheduling でも同様に no-op であること。 |
| temporary allowlist | temporary background restriction exemption 中に doze relaxation を期待できないこと。 |
| job execution | execution timing / quota / stop reason が deprecated API に依存していないこと。 |
| alternatives | expedited job、user-initiated data transfer job、foreground service と比較。 |
| WorkManager / SDK | deprecated API を内部利用していないか。 |
| logs | warning log、job stop reason、user-visible delay、retry behavior を確認。 |

---

# 顧客向け説明（Customer-facing Explanation）

Android 16 では、`JobInfo.Builder#setImportantWhileForeground(true)` を呼んでも job は important-while-foreground として扱われません。`JobInfo#isImportantWhileForeground()` も常に `false` を返します。

これは targetSdkVersion 36 化による影響ではなく、Android 16 に OS アップデートした端末上で、該当 API を使う全アプリに関係する可能性があります。

この API は Android 12 から deprecated でしたが、Android 16 では deprecation warning に留まらず、priority / doze relaxation / quota / thermal restriction などの特別扱いに使われなくなります。必要な work の性質に応じて expedited job、user-initiated data transfer job、foreground service、または通常 job へ整理し直してください。

---

# 残課題（Open Questions / Missing Evidence）

- WorkManager の現行 version が内部で `setImportantWhileForeground()` を呼ぶかどうかは、Jetpack 側 source / dependency version ごとに別途確認が必要。
- Android 15 製品ビルドで `ignore_important_while_foreground` aconfig flag がどの状態だったかは device / module build に依存し得る。本調査では Android 15 tag の conditional implementation と Android 16 tag の unconditional implementation を evidence とした。
- 既存 persisted job に古い `FLAG_IMPORTANT_WHILE_FOREGROUND` が残る場合の migration は、実機で `dumpsys jobscheduler` と execution behavior を確認するのが望ましい。ただし Android 16 controller 側の特別扱いは削除済み。

---

# Human Decision Placeholder

最終優先度（Final Priority）:
- Critical / High / Medium / Low

判断（Decision）:
- Explain / Monitor / Ignore / Further investigation required

補足:
- 最終優先度、顧客通知要否、release readiness は repository owner が判断する。

---

## 再検証記録（2026-08-22）

### 調査日（Investigation Date）

- 2026-08-22

### 公式ドキュメント再確認（Original Documentation Recheck）

- Android 16 の all-apps / target Behavior Change ページを再取得し、このレポートが参照する公式 section の掲載と適用範囲を再確認した。
- 公式ページの最終更新表示: all-apps: 2026-08-14 UTC / target: 2026-08-17 UTC。
- Android 16 compat framework 一覧も 2026-08-22 に再取得した。
- 既存の引用は短い要約として扱い、適用条件は公式ページ種別と AOSP gate の両方で再評価した。

### AOSP 証拠ワークスペース（AOSP Evidence Workspaces）

| AOSP project | Official remote URL | Checkout path | Working tree | From tag / resolved commit | To tag / resolved commit | Comparison command | Dirty risk / limitations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `platform/frameworks/base` | `https://android.googlesource.com/platform/frameworks/base` | `frameworks-base/` | Clean | `android-15.0.0_r36` / `396d32905ded85c082232bc510b525c9e372e585` | `android-16.0.0_r4` / `45034f0663f960d9ee5fb0a101a4732b71f6e2f4` | `git -C frameworks-base diff --no-renames --name-only android-15.0.0_r36 android-16.0.0_r4` | なし。明示タグ比較のため working tree の内容は根拠に含めない。 |

### ソース文脈・差分解釈の再確認（Source Context Reviewed / Diff Interpretation）

- 各 official remote で Android 15 / 16 の最新通常リリースタグが `android-15.0.0_r36` / `android-16.0.0_r4` のままであることを確認した。
- 上表の project-level `--name-only` 比較を再実行し、既存本文の path / symbol 別 source context、gate、追加・削除・条件変更・既定値変更・差分なしの解釈を再確認した。
- タグと解決済み commit が既存調査の比較対象から変わっていないため、本文の evidence record を別タグへ機械的に置換していない。
- 実機 Observed は新規実施していない。既存の「未実施」「未確認」および不足根拠はそのまま維持した。

### 事実（Facts）

- `android-15.0.0_r36` と `android-16.0.0_r4` は 2026-08-22 時点の最新通常リリースタグである。
- 上表に再検証時の working tree 状態を記録し、official remote、両タグ、解決済み commit を確認した。展開中または dirty の working tree は根拠に使用していない。
- 公式 section と AOSP evidence の比較 pair は一致している。

### 観察（Observations）

- 最新タグが変わっていないため、今回の再検証で既存の source diff 解釈を変更する新しい AOSP tag evidence は生じなかった。
- report 内に残る Medium / Low confidence、OEM / Mainline / QPR 条件、未確認の module enforcement は解消したものとして扱わない。

### 仮説（Hypotheses）

- 新しい仮説は追加しない。既存本文で仮説または可能性として記載した事項は、実機・製品 build・未確認 module の evidence が得られるまで事実へ昇格しない。

### 結論（Conclusions）

- 既存本文の主分類、confidence、対応候補を維持する。既存の不足根拠がある場合はその制約も維持する。
- 全件再検証の横断記録は [`android16/analysis/REVALIDATION_2026-08-22.md`](../../../analysis/REVALIDATION_2026-08-22.md) を参照する。

### Human Decision

- この再検証では最終 priority、severity、release readiness、顧客説明優先度を変更していない。
- 人間の判断は [Android 16 Decision Log](../../../decisions/DECISION_LOG.md) を正とする。

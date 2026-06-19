# App memory limits

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

### Behavior Change 文書（Behavior Change Source）

文書:
- https://developer.android.com/about/versions/17/behavior-changes-all

関連文書:
- https://developer.android.com/topic/performance/memory
- https://developer.android.com/tools/adb
- https://developer.android.com/tools/dumpsys#uid_stats
- https://developer.android.com/reference/android/app/ApplicationExitInfo
- https://developer.android.com/reference/android/app/ApplicationExitInfo#getDescription%28%29
- https://developer.android.com/reference/android/app/ApplicationExitInfo#REASON_OTHER
- https://developer.android.com/topic/performance/tracing/profiling-manager/trigger-based-capture
- https://developer.android.com/about/versions/17/features#anomaly-profiling-trigger

セクション:
- App memory limits

ページ種別:
- Behavior changes: all apps

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- OS_UPDATE_ALL_APPS

公式文書からの初期適用条件判断:
- 公式文書は Android 17 の `Behavior changes: all apps` ページにこの項目を掲載しているため、一次判断では `OS_UPDATE_ALL_APPS` 候補である。
- AOSP では `MemoryLimiter` が `system_server` 内の Java component と JNI component として追加され、`ActivityManagerService` / `ProcessRecord` に接続されている。targetSdkVersion gate は確認されず、feature flag、system_server、vendor config、device RAM 条件、DeviceConfig runtime disable flags により有効可否が決まる。
- 公式文書は「一部の Android devices のみで memory limits が課される」と明記しているため、OS update impact であっても device 条件付きの挙動として扱う必要がある。

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | Yes / Conditional | all apps ページに掲載。AOSP では targetSdkVersion gate は確認されず、device / vendor config 条件で有効化される。 |
| targetSdkVersion 37 以上が必要か | No | `MemoryLimiter` / `ProcessRecord` / `ActivityManagerService` path に targetSdkVersion gate は確認されない。 |
| 追加の実行時条件があるか | ある | 公式文書は memory limits が一部の Android devices のみに課されると説明している。 |
| Compat Change ID が関係するか | No evidence | compat framework Change ID ではなく `Flags.memoryLimiterEnable()`、vendor config、DeviceConfig flags で制御される。 |

### 調査日（Investigation Date）

2026-06-15

### 信頼度（Confidence）

- High

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [x] targetSdkVersion に関係なく Android 17 の全アプリへ適用
- [ ] Android 17 以上かつ targetSdkVersion 37 以上で適用
- [ ] targetSdkVersion 37 以上かつ追加の実行時条件を満たす場合に適用
- [ ] Mainline / Google Play system update に依存
- [ ] API 追加のみであり、挙動変更ではない
- [ ] 未確認 / 追加 evidence が必要

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 であることが前提。
- targetSdkVersion: 条件なし。AOSP evidence 上、targetSdkVersion gate は確認されない。
- Device/form factor: 一部の Android devices のみ。`/vendor/etc/memory-limiter-config.xml` が存在し、現在の `memTotal` に適用可能な config があることが必要。
- Permission/API/component condition: アプリが制限値を超える memory usage、特に extreme memory leak / outlier に該当する場合に影響が顕在化する。
- App state/process condition: process state により visible / not-visible / cached / unrestricted の limit が割り当てられる。

Compat framework:
- Change ID: 確認されず
- 変更名: 該当なし
- 既定状態: compat framework ではなく `Flags.memoryLimiterEnable()`、vendor config、DeviceConfig `memory_limiter_disable_limits` / `memory_limiter_disable_kill` に依存
- テスト時の切り替え可否: `am memory-limiter ignore` / `manual` / `status` による test controls がある。

分類信頼度（Classification confidence）:
- High

分類根拠（Classification evidence）:
- 公式ドキュメントページ: `behavior-changes-all`
- 検証対象の適用条件文: Android 17 all-apps page states that its changes apply to all apps running on Android 17 regardless of targetSdkVersion.
- AOSP targetSdk gate: なし。確認した `MemoryLimiter` / `ActivityManagerService` / `ProcessRecord` path に targetSdkVersion gate は見つからない。
- Compat framework entry: なし。compat framework ではなく feature flag / vendor config / DeviceConfig で制御。

---

# エグゼクティブサマリー（Executive Summary）

Android 17 では、device total RAM に基づく app memory limits が導入され、極端な memory leak や outlier が system-wide instability、UI stutter、battery drain、app kill につながる前に制御される、と公式文書は説明している。

この項目は Android 17 の all apps ページに掲載されているため、targetSdkVersion 37 への更新有無に関係なく Android 17 上で影響する可能性がある。ただし、公式文書は memory limits が一部の Android devices のみに課されると説明しているため、全端末で必ず発生する変更ではない。

AOSP では `MemoryLimiter` 実装、`ActivityManagerService` への組み込み、process state に応じた limit 割り当て、`MemoryLimiter:AnonSwap` exit description、`am memory-limiter` test controls が確認できる。適用は Android 17 上の all apps change だが、`/vendor/etc/memory-limiter-config.xml` と device RAM 条件を満たす device に限定される。

---

# 公式ドキュメント確認

## 原文（Statement）

ページタイトル:
- Behavior changes: all apps

ページ URL:
- https://developer.android.com/about/versions/17/behavior-changes-all

ページ種別:
- all apps

セクションタイトル:
- App memory limits

検証対象の原文:
- Android 17 introduces app memory limits based on device total RAM.
- The limits are intended to make the environment more stable and deterministic for apps and users.
- The limits target extreme memory leaks and outliers before they cause system-wide instability.
- Memory limits are imposed only on a subset of Android devices.
- Affected sessions can be diagnosed through `ApplicationExitInfo.getDescription()` containing `MemoryLimiter:AnonSwap`, with exit reason `REASON_OTHER`.
- Trigger-based profiling with `TRIGGER_TYPE_ANOMALY` can collect heap dumps when the limit is hit.

検証対象のサブセクション:
- `Test your app's behavior under the memory constraints` is a verification subsection under `App memory limits`, not a separate Behavior Change.
- Developers can use ADB and the shell command `am` to adjust or disable memory limits on devices that impose memory limits.
- AOSP の `am memory-limiter` subcommands are `ignore <UID|none|all>`, `manual <PID> <PERCENT|none>`, and `status`.
- These commands have no effect on devices that do not impose memory limits.
- `ignore <uid>` ignores enforcement for all processes associated with that UID; `all` ignores all apps; `none` clears previous ignore settings.
- Even if a UID is ignored, `manual` can still apply a memory limit to a process in that app.
- AOSP の `am memory-limiter manual <PID> <PERCENT|none>` は、PID 単位で total RAM に対する percentage based manual memory limit を課す。`none` は manual override を解除する。
- `status` reports current memory limiter status, including limits imposed on visible and non-visible processes.

## 解釈（Interpretation）

公式文書は、この変更を Android 17 上で動作する全アプリ向けの Behavior Change として掲載している。したがって一次判断では、targetSdkVersion 37 化ではなく Android 17 OS update 側の影響候補である。

ただし、適用は「一部の Android devices」のみに限定される。顧客説明では「Android 17 で全アプリが対象になり得る」が、「全 device / 全 session で必ず memory limit による kill が発生する」わけではない、と分けて説明する必要がある。

アプリ側で観測できる signal は、`ApplicationExitInfo.getDescription()` 内の `MemoryLimiter:AnonSwap` と `REASON_OTHER` である。開発・検証では `am memory-limiter` subcommands により制限の ignore / manual limit / status 確認を行う、と公式文書は説明している。

`Test your app's behavior under the memory constraints` は、Behavior Change 本体ではなく検証手段の説明である。したがって分類を別項目として分けず、`App memory limits` の検証方法として扱う。顧客向けには、`am memory-limiter` は production mitigation ではなく、対象端末上で memory limiter の有無・manual limit・ignore 状態を切り替えて挙動を確認するための開発 / QA 手段として説明する。

---

# 変更内容（What Changed）

公式文書上の変更点:
- Android 17 で device total RAM に基づく app memory limits が導入される。
- 制限値は Android 17 では conservative に設定され、system baseline を作る目的と説明されている。
- 主な対象は extreme memory leaks や memory outliers。
- 問題が system-wide instability、UI stuttering、battery drain、apps being killed につながる前に制御することが目的。
- 影響を受けた app session は `ApplicationExitInfo` で診断できる。
- `am memory-limiter` command で test controls が提供される。
- `am memory-limiter` commands は memory limits を impose する device 上でのみ効果を持つ。memory limits を impose しない device では効果がない。
- `ignore` は UID 単位または全アプリ単位で enforcement を無視させる。
- `manual` は PID 単位で total RAM に対する percent 指定の memory constraint を課す。
- `status` は visible / non-visible process に課される memory limit 状態を報告する。

AOSP で確認した点 / 未確認の点:
- `MemoryLimiter.java` は app process memory usage を monitor / limit し、Java layer から native layer へ process 情報と limit を渡す。
- `com_android_server_am_MemoryLimiter.cpp` は cgroup v2 の `memory.high` / `memory.swap.max` と inotify event を扱う native component。
- `ActivityManagerService` は `MemoryLimiter.getDefaultMemoryLimiter(mContext)` を保持し、`ProcessRecord` は process ごとの `MemoryLimiter.Limiter` を持つ。
- `ProcessRecord` は UID、PID、process state update を MemoryLimiter に渡す。
- `MemoryLimiter.isMemoryLimiterSupported()` は `/vendor/etc/memory-limiter-config.xml` の存在と、現在の `memTotal` に適用できる config を条件にする。
- over-limit type `LIMIT_TYPE_ANON_SWAP` では `ProfilingTrigger.TRIGGER_TYPE_ANOMALY` を通知し、30 秒後に `"MemoryLimiter:AnonSwap"` description 付きで kill を request する。
- `am memory-limiter ignore` / `manual` / `status` が ActivityManager shell command に追加されている。
- 未確認: vendor config の実端末別 default、native cgroup event の実機挙動、端末ごとの limit 値。

## 適用条件（Applicability）

この変更がいつ適用されるかを OS 条件と targetSdkVersion 条件に分けて説明する。

### OS アップデート時の挙動（OS Update Behavior）

- Android 17 にアップデートしただけで適用されるか: Yes / Conditional。`behavior-changes-all` ページに掲載され、AOSP 実装に targetSdkVersion gate は確認されない。
- targetSdkVersion に依存しない根拠: `MemoryLimiter` は `ActivityManagerService` / `ProcessRecord` の process lifecycle path に接続され、targetSdkVersion を参照しない。
- Android 16 以前での挙動: Android 16 baseline には `MemoryLimiter.java`、MemoryLimiter JNI、`am memory-limiter` command、memory-limiter config schema が存在しない。

### targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- targetSdkVersion 37 以上で適用されるか: 公式文書上、targetSdkVersion 37 は必要条件として示されていない。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: 未確認。公式文書は Android 17 all apps change として説明しているため、Android 17 platform / device condition が前提と考えられる。
- opt-out / temporary override の有無: compat opt-out は確認されない。開発 / QA 用に `am memory-limiter ignore <UID|none|all>` と `manual <PID> <PERCENT|none>` がある。DeviceConfig `memory_limiter_disable_limits` / `memory_limiter_disable_kill` による runtime disable flags もある。

### その他の条件（Other Conditions）

- device/form factor: 一部の Android devices のみ。device total RAM と device eligibility が関係する。
- permission: 公式文書からは特定 permission 条件は確認できない。
- API usage: 診断には `ApplicationExitInfo.getDescription()`、`ApplicationExitInfo.REASON_OTHER`、trigger-based profiling / `TRIGGER_TYPE_ANOMALY` が関連する。
- manifest attribute: 公式文書からは確認できない。
- component boundary: process / UID 単位。`ignore` は UID または all UIDs、`manual` は PID を指定し、実装は PID から UID を引いて `MemoryLimiter.setManualLimit(pid, uid, limitPercent)` を呼ぶ。

---

# AOSP 調査（AOSP Investigation）

## checkout 状態（Checkout Status）

確認コマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list 'android-16.0.0_r4'
git -C frameworks-base tag --list 'android-17*'
```

結果:
- `frameworks-base` の `status --short` は空で、dirty working tree は確認されなかった。
- `android-16.0.0_r4` tag は存在する。
- `android-17.0.0_r1` tag は local checkout に存在する。

根拠上の制約:
- source evidence は `android-16.0.0_r4` と `android-17.0.0_r1` の明示的な tag 比較、および `android-17.0.0_r1` 上の symbol 確認に限定した。
- `frameworks-base` working tree は clean のため、local working tree changes を platform evidence として誤採用するリスクは確認されていない。

## 関連ファイル（Related Files）

- `services/core/java/com/android/server/am/` 以下の process / memory management path
- `services/core/java/com/android/server/am/MemoryLimiter.java`
- `services/core/jni/com_android_server_am_MemoryLimiter.cpp`
- `services/core/java/com/android/server/am/ActivityManagerService.java`
- `services/core/java/com/android/server/am/ActivityManagerShellCommand.java`
- `services/core/java/com/android/server/am/ProcessRecord.java`
- `services/core/xsd/memory-limiter-config/memory-limiter-config.xsd`
- `core/java/android/app/ApplicationExitInfo.java`
- `services/core/java/com/android/server/am/MemoryLimiter.md`

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `MemoryLimiter.java` | file なし。 | app process memory usage を monitor / limit し、over-limit 時に statsd / profiling / delayed kill を行う。 | Behavior Change 本体の framework-side controller。 |
| `com_android_server_am_MemoryLimiter.cpp` | file なし。 | cgroup v2 の `memory.high` / `memory.swap.max` を扱う native component。 | 実際に kernel cgroup へ limit を適用し event を監視する layer。 |
| `ActivityManagerService` / `mMemoryLimiter` | MemoryLimiter 接続なし。 | `MemoryLimiter.getDefaultMemoryLimiter(mContext)` を保持し system ready で初期化する。 | AMS が system_server 内で limiter を所有する根拠。 |
| `ProcessRecord.mMemoryLimiter` | process ごとの limiter なし。 | UID / PID / process state update を limiter に伝える。 | process lifecycle と limit assignment の接点。 |
| `ActivityManagerShellCommand.runMemoryLimiter()` | command なし。 | `ignore` / `manual` / `status` subcommands を実装。 | 公式 test controls の実装根拠。 |
| `MemoryLimiter.isMemoryLimiterSupported()` | 該当なし。 | `/vendor/etc/memory-limiter-config.xml` と current RAM に合う config が必要。 | 「一部 devices のみ」を裏付ける device eligibility gate。 |
| `MemoryLimiter.onLimitExceeded()` | 該当なし。 | `LIMIT_TYPE_ANON_SWAP` で `TRIGGER_TYPE_ANOMALY` を通知し、`MemoryLimiter:AnonSwap` description 付き kill を遅延 request。 | 開発者が `ApplicationExitInfo` で観測する signal の根拠。 |

必須記入項目:
- Entry point / caller: app process lifecycle -> `ProcessRecord` -> `MemoryLimiter.Limiter` -> native cgroup limit; test path は `adb shell am memory-limiter ...` -> `ActivityManagerShellCommand.runMemoryLimiter()` -> `MemoryLimiter`。
- Relevant class or service responsibility: process memory limit enforcement、exit reason / description recording、developer diagnostics。
- Runtime path from app API / system event to changed code: app process が起動し `ProcessRecord` が PID / UID / proc state を limiter に渡す -> native layer が cgroup limit を設定 / 監視 -> anon+swap limit exceeded で Java callback -> anomaly profiling trigger -> delayed kill with `"MemoryLimiter:AnonSwap"` description。
- Why unrelated code paths were excluded: existing heap dump notification strings and generic image decode memory limits are別機能であり、app process memory limiter enforcement ではないため primary evidence から除外。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
| `MemoryLimiter.java` / JNI / config schema / shell command が追加される | added behavior | Android 17 に app process memory limiter が導入された直接根拠。 | High |
| `MemoryLimiter.isMemoryLimiterSupported()` が vendor config と current RAM を確認する | changed condition / device gate | 「一部 devices のみ」を AOSP で裏付ける。 | High |
| `ProcessRecord` が UID / PID / proc state を `MemoryLimiter` に通知する | added behavior / process lifecycle integration | app process に state-based memory limits を適用する runtime path。 | High |
| `onLimitExceeded()` が `TRIGGER_TYPE_ANOMALY` と `"MemoryLimiter:AnonSwap"` delayed kill を行う | added behavior / diagnostic signal | 公式文書の `ApplicationExitInfo` / profiling 診断と一致。 | High |

必須分類:
- Added behavior: Android 17 で `MemoryLimiter`、JNI component、vendor config schema、`am memory-limiter` command が追加される。
- Removed behavior: 該当なし。
- Changed condition / gate: `Flags.memoryLimiterEnable()`、system_server、vendor config file、current RAM matching config、DeviceConfig runtime flags が gate。
- Changed default: MemoryLimiter 対象 device では process state に応じた limit が default path に組み込まれる。
- No behavior change found: 該当しない。

## 事実（Evidence）

事実:
- 公式文書は `App memory limits` を Android 17 `Behavior changes: all apps` ページに掲載している。
- 公式文書は Android 17 が device total RAM に基づく app memory limits を導入すると説明している。
- 公式文書は limits が conservative に設定され、system baseline を作る目的だと説明している。
- 公式文書は対象を extreme memory leaks と memory outliers と説明している。
- 公式文書は memory limits が一部の Android devices のみに課されると説明している。
- 公式文書は影響を受けた session の exit reason が `REASON_OTHER` になり、description に `MemoryLimiter:AnonSwap` が含まれると説明している。
- 公式文書は `TRIGGER_TYPE_ANOMALY` による trigger-based profiling を診断手段として挙げている。
- 公式文書は `am memory-limiter ignore`、`manual`、`status` を test commands として挙げている。
- 公式文書は `am memory-limiter` commands が memory limits を impose しない device では効果を持たないと説明している。
- 公式文書は `ignore <uid>` がその UID に属する全 processes の enforcement を ignore し、`all` が全アプリ、`none` が以前の ignore 設定解除を意味すると説明している。
- 公式文書は UID を ignore していても、同じ app 内 process には `manual` memory limit を適用できると説明している。
- AOSP は `manual <PID> <PERCENT|none>` が PID 単位で percentage based manual memory limit を課し、`none` が manual override を解除すると説明している。
- 公式文書は `status` が visible / non-visible processes に課される memory limits を含む current status を報告すると説明している。
- local `frameworks-base` には `android-16.0.0_r4` tag がある。
- local `frameworks-base` には `android-17.0.0_r1` tag がある。
- 調査時点で `frameworks-base` working tree は clean。
- Android 17 tag には `MemoryLimiter.java`、`com_android_server_am_MemoryLimiter.cpp`、`MemoryLimiter.md`、memory-limiter config schema、`am memory-limiter` command が存在する。

観察:
- all apps ページ掲載であり、AOSP に targetSdkVersion gate が見つからないため、primary classification は `OS_UPDATE_ALL_APPS` とする。
- device subset condition があるため、顧客向けには「Android 17 全アプリ対象候補」かつ「対象 device 条件付き」と説明する必要がある。
- test command は compat framework ではなく ActivityManager shell command として提供される。
- `ignore` と `manual` の UID / PID split から、app-level ignore と process-level manual limit は別の control plane として扱われる。
- `MemoryLimiter` は visible / not-visible / cached / unrestricted process state ごとの limit を持つ。

仮説:
- `MemoryLimiter:AnonSwap` は anon+swap が memory.high + memory.swap.max を超えたことに対応する enforcement reason と解釈できる。
- `am memory-limiter` subcommands は shell / ADB 経由の developer-facing test hook であり、通常の app production mitigation ではない。

結論:
- 公式文書と AOSP evidence が一致するため、primary classification は `OS_UPDATE_ALL_APPS`、confidence は High とする。ただし実際に適用されるかは device / vendor config / RAM 条件に依存する。

## 適用ゲート根拠（Applicability Gate Evidence）

- targetSdkVersion gate: なし。確認した path では targetSdkVersion / compat gate は使われていない。
- CompatChanges.isChangeEnabled / ChangeId: 確認されず。
- @EnabledAfter / @EnabledSince / default state: 該当なし。
- Build.VERSION / SDK_INT gate: 明示的な runtime SDK_INT gate は主根拠ではない。Android 17 platform implementation として追加。
- DeviceConfig / resources config: DeviceConfig `memory_limiter_disable_limits` / `memory_limiter_disable_kill` が runtime disable flags。vendor config `/vendor/etc/memory-limiter-config.xml` が device eligibility gate。
- Permission/AppOps gate: 公式文書からは確認できない。
- Manifest/property gate: 公式文書からは確認できない。
- No gate found: targetSdkVersion gate / compat gate は見つからない。
- Gate conclusion: Android 17 上で MemoryLimiter が feature enabled、system_server 内で動作し、vendor config と RAM 条件を満たす device で、対象 app process が configured limit に達した場合に適用される。
- Reasoning from source context: `ProcessRecord` が process lifecycle を limiter に渡し、native cgroup layer が memory / swap limits を監視し、anon+swap over-limit で profiling trigger と delayed kill を行う。

---

# 影響分析（Impact Analysis）

## 影響を受けるアプリ（Affected Apps）

- Android 17 上で動作するアプリ。
- 対象 device subset 上で実行されるアプリ。
- extreme memory leak、large anonymous memory usage、memory outlier があるアプリ。
- 長時間稼働、画像 / 動画処理、ML inference、大量 cache、WebView / native heap / bitmap などで memory usage が増えやすいアプリ。
- background process や non-visible process で memory を保持し続けるアプリ。

## 影響を受けないアプリ（Non-Affected Apps）

- Android 17 以外の端末上で動作する場合。
- memory limits が imposed されない device subset 上で動作する場合。
- memory baseline が安定しており、extreme leak / outlier がない場合。
- memory limit に達していない app sessions。
- target device に `/vendor/etc/memory-limiter-config.xml` がない、または current RAM に一致する limit set がない場合。

---

# 顧客影響（Customer Impact）

## 影響度（Impact Level）

- 要確認

※ 最終 severity / priority は人間が判断する。このレポートでは確定しない。

## ビジネス影響（Business Impact）

- ユーザー影響: memory limit に達した session では app process が終了し、ユーザーには app restart、作業中断、状態消失として見える可能性がある。
- 運用影響: crash reporting だけでは通常の crash として分類されない可能性があるため、`ApplicationExitInfo` と exit description の収集が必要になる。
- 開発影響: memory baseline、leak detection、heap dump、large cache / native heap / bitmap usage の見直しが必要になる。

---

# サービス影響例（Service Impact Examples）

このセクションは、公式文書と AOSP evidence から導いた「起こりうる影響例」を記録する。
特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: 画像 / 動画編集アプリ

- 対象サービス例: 画像加工、動画編集、media generation、large bitmap を扱う editor。
- 影響を受ける実装パターン: 高解像度画像、temporary bitmap、decoded frame、native buffer を長時間保持する。
- 発生条件: Android 17、memory limiter 対象 device、process memory が limit に到達する。
- ユーザーに見える症状: 編集中の app restart、作業中断、未保存状態の喪失。
- 開発・運用への影響: memory baseline 測定、bitmap / native buffer lifecycle、autosave / restore path の確認が必要。
- 推奨対応候補: heap dump、trigger-based profiling、large allocation path の棚卸し、`ApplicationExitInfo` collection。
- 根拠: 公式文書は extreme memory leaks / outliers を対象とし、`MemoryLimiter:AnonSwap` で診断可能と説明している。
- Confidence（信頼度）: High。発生有無は対象 device / memory usage に依存する。
- 注意: 実サービスで発生確認した事実ではない。

## 例2（Example 2）: 長時間 background 同期 / cache 保持アプリ

- 対象サービス例: file sync、offline cache、document scanner、map / media cache。
- 影響を受ける実装パターン: background process が large cache、queue、native heap、decoded data を保持し続ける。
- 発生条件: Android 17、memory limiter 対象 device、visible / non-visible process の limit に到達する。
- ユーザーに見える症状: background task 中断、次回起動時の同期や処理のやり直し。
- 開発・運用への影響: background work の checkpoint、idempotency、memory pressure handling の確認が必要。
- 推奨対応候補: WorkManager / foreground work の状態復旧、cache eviction、memory leak monitoring、`am memory-limiter manual` を使った再現試験。
- 根拠: 公式文書は status command が visible / non-visible process の memory limits を報告すると説明している。
- Confidence（信頼度）: High。process state 別 limit assignment は AOSP evidence で確認済み。
- 注意: 実サービスで発生確認した事実ではない。

---

# 対応候補（Required Actions）

## 必須対応（Must）

- Android 17 target device で memory baseline を測定する。
- `ApplicationExitInfo` の取得・保存・分析 path を確認し、`REASON_OTHER` と `MemoryLimiter:AnonSwap` を検出できるようにする。
- memory leak / large allocation / unbounded cache / native heap growth の既知 issue を棚卸しする。
- app restart や process death に備えて、重要な user state の保存・復元を確認する。

## 推奨対応（Recommended）

- `am memory-limiter status` で対象 device の memory limiter 状態を確認する。
- `am memory-limiter manual <pid> <percent>` を使い、memory limit 到達時の app behavior を再現する。
- `am memory-limiter ignore <uid>|none|all` を使い、memory limiter 有無による差分を検証する。
- trigger-based profiling with `TRIGGER_TYPE_ANOMALY` を設定し、limit hit 時の heap dump を取得する。
- Android Developers の memory best practices に沿って memory usage を最適化する。

## 任意対応（Optional）

- large memory feature に対する feature flag / graceful degradation を検討する。
- device RAM class / memory class / low RAM device condition に応じた cache size tuning を見直す。
- QA matrix に memory limiter 対象 device と非対象 device の比較を追加する。

---

# 検証方法（Verification Method）

変更を確認する方法。

## 検証マトリクス（Matrix）

| 端末 OS（Device OS） | targetSdkVersion | Compat flag / test control | 期待挙動（Expected behavior） |
| --- | --- | --- | --- |
| Android 16 | 36 | default | Android 17 app memory limits は対象外。baseline memory behavior を測定する。 |
| Android 17 | 36 | default | 対象 device では memory limiter が適用され得る。targetSdkVersion gate は確認されない。 |
| Android 17 | 37 | default | targetSdkVersion 36 と同様に、対象 device では memory limiter が適用される可能性がある。 |
| Android 17 | 36 | `am memory-limiter manual <pid> <percent>` | manual limit により memory limit hit 時の process behavior を再現する。 |
| Android 17 | 37 | `am memory-limiter ignore <uid>` | memory limiter ignore により enforcement 差分を確認する。 |

## `am memory-limiter` subcommands

| Command | 入力単位 | 目的 | 注意 |
| --- | --- | --- | --- |
| `am memory-limiter ignore <uid>` | UID | 指定 UID に属する全 process の enforcement を ignore する | UID を ignore していても、同じ app 内 process に `manual` limit は適用できる |
| `am memory-limiter ignore all` | all apps | 全アプリの enforcement を ignore する | QA 中に system-wide に影響するため、検証後に戻す |
| `am memory-limiter ignore none` | none | 以前の ignore 設定を解除する | cleanup |
| `am memory-limiter manual <pid> <percent>` | PID / percent | 指定 process に total RAM 比率の manual memory limit を課す | AOSP help は `PERCENT: percentage of total RAM (1-99)` と説明する |
| `am memory-limiter manual <pid> none` | PID | manual limit override を解除する | default limit の有無は対象 device 依存 |
| `am memory-limiter status` | device state | memory limiter の現在状態を表示する | visible / non-visible process limits を含む |

## 手順（Steps）

- targetSdk変更: targetSdkVersion 36 / 37 の両方で検証し、targetSdkVersion 差分ではなく OS / device / memory condition 差分として観測されるか確認する。
- compat framework command: 公式文書上 compat flag は未確認。代わりに `am memory-limiter` commands を使う。
- テスト方法:
  - `am memory-limiter status`
  - `am memory-limiter manual <pid> <percent>|none`
  - `am memory-limiter ignore <uid>|none|all`
  - `ApplicationExitInfo.getDescription()` の collection
  - trigger-based profiling with `TRIGGER_TYPE_ANOMALY`
- 再現手順:
  - Android 17 対象 device で app を起動する。
  - `am memory-limiter status` を実行し、その device が memory limits を impose しているか確認する。impose しない device では commands は効果を持たない。
  - memory baseline を測定する。
  - manual memory limit を設定する。
  - 必要に応じて `am memory-limiter ignore <uid>` / `am memory-limiter ignore none` で enforcement 有無の差分を確認する。
  - large allocation / known memory intensive flow を実行する。
  - process exit 後、`ApplicationExitInfo` の reason / description を確認する。
- 期待結果:
  - limit hit 時に app session が影響を受ける。
  - exit reason は `REASON_OTHER`。
  - description に `MemoryLimiter:AnonSwap` が含まれる。
  - heap dump / profiling artifact が取得できる場合、memory growth の原因を分析できる。

---

# 結論（Conclusion）

App memory limits は、Android 17 all apps ページに掲載され、AOSP でも targetSdkVersion gate が確認されないため、targetSdkVersion 更新ではなく Android 17 OS update 側の影響である。ただし、一部 devices のみで imposed される条件付き変更であり、vendor config と device RAM 条件に依存する。

Android app developer は、Android 17 対応の一環として memory baseline、leak / outlier detection、`ApplicationExitInfo` による診断、`am memory-limiter` を使った再現検証を準備する必要がある。

---

# 人間の判断欄

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 人間による判断が必要

判断理由候補:
- 公式文書と AOSP evidence は all apps change を支持するが、顧客影響は device subset condition と memory usage pattern に依存する。
- 顧客影響は memory usage pattern に依存するため、実サービスの memory baseline と crash / exit telemetry を見て判断する必要がある。

---

# 参照（References）

## ドキュメント（Documentation）

- https://developer.android.com/about/versions/17/behavior-changes-all
- https://developer.android.com/topic/performance/memory
- https://developer.android.com/tools/adb
- https://developer.android.com/tools/dumpsys#uid_stats
- https://developer.android.com/reference/android/app/ApplicationExitInfo
- https://developer.android.com/reference/android/app/ApplicationExitInfo#getDescription%28%29
- https://developer.android.com/reference/android/app/ApplicationExitInfo#REASON_OTHER
- https://developer.android.com/topic/performance/tracing/profiling-manager/trigger-based-capture
- https://developer.android.com/about/versions/17/features#anomaly-profiling-trigger

## AOSP

- `services/core/java/com/android/server/am/MemoryLimiter.java`
- `services/core/jni/com_android_server_am_MemoryLimiter.cpp`
- `services/core/java/com/android/server/am/ActivityManagerService.java`
- `services/core/java/com/android/server/am/ActivityManagerShellCommand.java`
- `services/core/java/com/android/server/am/ProcessRecord.java`
- `services/core/xsd/memory-limiter-config/memory-limiter-config.xsd`
- `services/core/java/com/android/server/am/MemoryLimiter.md`

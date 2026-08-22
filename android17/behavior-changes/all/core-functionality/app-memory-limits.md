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
- AOSP では `MemoryLimiter` が `system_server` 内の Java コンポーネントと JNI コンポーネントとして追加され、`ActivityManagerService` / `ProcessRecord` に接続されている。targetSdkVersion ゲートは確認されず、feature flag、`system_server`、ベンダー設定、端末 RAM 条件、DeviceConfig の実行時無効化フラグにより有効可否が決まる。
- 公式文書は「一部の Android 端末のみにメモリ制限が課される」と明記しているため、OS アップデート影響であっても端末条件付きの挙動として扱う必要がある。

早見表（影響の早見）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | はい / 条件付き | all apps ページに掲載。AOSP では targetSdkVersion ゲートは確認されず、端末 / ベンダー設定条件で有効化される。 |
| targetSdkVersion 37 以上が必要か | いいえ | `MemoryLimiter` / `ProcessRecord` / `ActivityManagerService` のコードパスに targetSdkVersion ゲートは確認されない。 |
| 追加の実行時条件があるか | ある | 公式文書はメモリ制限が一部の Android 端末のみに課されると説明している。 |
| Compat Change ID が関係するか | 根拠なし | compat framework Change ID ではなく `Flags.memoryLimiterEnable()`、ベンダー設定、DeviceConfig フラグで制御される。 |

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
- [ ] 未確認 / 追加根拠が必要

必要な実行時条件（Required runtime conditions）:
- Android バージョン: Android 17 であることが前提。
- targetSdkVersion: 条件なし。AOSP 根拠上、targetSdkVersion ゲートは確認されない。
- 端末 / フォーム ファクタ: 一部の Android 端末のみ。`/vendor/etc/memory-limiter-config.xml` が存在し、現在の `memTotal` に適用可能な設定があることが必要。
- 権限 / API / コンポーネント条件: アプリが制限値を超えるメモリ使用量、特に極端なメモリリーク / 外れ値に該当する場合に影響が顕在化する。
- アプリ状態 / プロセス条件: プロセス状態により表示中 / 非表示 / キャッシュ済み / 無制限の制限値が割り当てられる。

Compat framework:
- Change ID: 確認されず
- 変更名: 該当なし
- 既定状態: compat framework ではなく `Flags.memoryLimiterEnable()`、ベンダー設定、DeviceConfig `memory_limiter_disable_limits` / `memory_limiter_disable_kill` に依存
- テスト時の切り替え可否: `am memory-limiter ignore` / `manual` / `status` によるテスト制御がある。

分類信頼度（Classification confidence）:
- High

分類根拠（Classification evidence）:
- 公式ドキュメントページ: `behavior-changes-all`
- 検証対象の適用条件文: Android 17 all-apps page states that its changes apply to all apps running on Android 17 regardless of targetSdkVersion.
- AOSP targetSdk ゲート: なし。確認した `MemoryLimiter` / `ActivityManagerService` / `ProcessRecord` のコードパスに targetSdkVersion ゲートは見つからない。
- Compat framework entry: なし。compat framework ではなく feature flag / ベンダー設定 / DeviceConfig で制御。

---

# エグゼクティブサマリー

Android 17 では、端末の合計 RAM に基づくアプリごとのメモリ制限が導入され、極端なメモリリークや外れ値が端末全体の不安定化、UI のカクつき、バッテリー消費、アプリ kill につながる前に制御される、と公式文書は説明している。

この項目は Android 17 の all apps ページに掲載されているため、targetSdkVersion 37 への更新有無に関係なく Android 17 上で影響する可能性がある。ただし、公式文書はメモリ制限が一部の Android 端末のみに課されると説明しているため、全端末で必ず発生する変更ではない。

AOSP では `MemoryLimiter` 実装、`ActivityManagerService` への組み込み、プロセス状態に応じた制限値の割り当て、`MemoryLimiter:AnonSwap` の終了説明、`am memory-limiter` テスト制御が確認できる。適用は Android 17 上の all apps change だが、`/vendor/etc/memory-limiter-config.xml` と端末 RAM 条件を満たす端末に限定される。

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
- AOSP の `am memory-limiter` サブコマンドは `ignore <UID|none|all>`、`manual <PID> <PERCENT|none>`、`status` である。
- These commands have no effect on devices that do not impose memory limits.
- `ignore <uid>` ignores enforcement for all processes associated with that UID; `all` ignores all apps; `none` clears previous ignore settings.
- Even if a UID is ignored, `manual` can still apply a memory limit to a process in that app.
- AOSP の `am memory-limiter manual <PID> <PERCENT|none>` は、PID 単位で合計 RAM に対する比率指定の手動メモリ制限を課す。`none` は手動 override を解除する。
- `status` は、表示中 / 非表示のプロセスに適用されている制限を含む、現在の memory limiter 状態を報告する。

## 解釈（Interpretation）

公式文書は、この変更を Android 17 上で動作する全アプリ向けの Behavior Change として掲載している。したがって一次判断では、targetSdkVersion 37 化ではなく Android 17 OS update 側の影響候補である。

ただし、適用は「一部の Android 端末」のみに限定される。顧客説明では「Android 17 で全アプリが対象になり得る」が、「すべての端末 / すべてのセッションで必ずメモリ制限による kill が発生する」わけではない、と分けて説明する必要がある。

アプリ側で観測できるシグナルは、`ApplicationExitInfo.getDescription()` 内の `MemoryLimiter:AnonSwap` と `REASON_OTHER` である。開発・検証では `am memory-limiter` サブコマンドにより、制限の無視、手動制限、状態確認を行う、と公式文書は説明している。

`Test your app's behavior under the memory constraints` は、Behavior Change 本体ではなく検証手段の説明である。したがって分類を別項目として分けず、`App memory limits` の検証方法として扱う。顧客向けには、`am memory-limiter` は本番環境での緩和策ではなく、対象端末上で memory limiter の有無、手動制限、無視状態を切り替えて挙動を確認するための開発 / QA 手段として説明する。

---

# 変更内容（What Changed）

公式文書上の変更点:
- Android 17 で端末の合計 RAM に基づくアプリごとのメモリ制限が導入される。
- 制限値は Android 17 では保守的に設定され、システムの基準値を作る目的と説明されている。
- 主な対象は極端なメモリリークやメモリ使用量の外れ値。
- 問題が端末全体の不安定化、UI のカクつき、バッテリー消費、アプリ kill につながる前に制御することが目的。
- 影響を受けたアプリ セッションは `ApplicationExitInfo` で診断できる。
- `am memory-limiter` コマンドでテスト制御が提供される。
- `am memory-limiter` コマンドはメモリ制限を課す端末上でのみ効果を持つ。メモリ制限を課さない端末では効果がない。
- `ignore` は UID 単位または全アプリ単位で制限適用を無視させる。
- `manual` は PID 単位で合計 RAM に対する比率指定のメモリ制約を課す。
- `status` は表示中 / 非表示のプロセスに課されるメモリ制限状態を報告する。

AOSP で確認した点 / 未確認の点:
- `MemoryLimiter.java` はアプリ プロセスのメモリ使用量を監視 / 制限し、Java 層から native 層へプロセス情報と制限値を渡す。
- `com_android_server_am_MemoryLimiter.cpp` は cgroup v2 の `memory.high` / `memory.swap.max` と inotify event を扱う native コンポーネント。
- `ActivityManagerService` は `MemoryLimiter.getDefaultMemoryLimiter(mContext)` を保持し、`ProcessRecord` はプロセスごとの `MemoryLimiter.Limiter` を持つ。
- `ProcessRecord` は UID、PID、プロセス状態更新を MemoryLimiter に渡す。
- `MemoryLimiter.isMemoryLimiterSupported()` は `/vendor/etc/memory-limiter-config.xml` の存在と、現在の `memTotal` に適用できる設定を条件にする。
- over-limit type `LIMIT_TYPE_ANON_SWAP` では `ProfilingTrigger.TRIGGER_TYPE_ANOMALY` を通知し、30 秒後に `"MemoryLimiter:AnonSwap"` の説明付きで kill を要求する。
- `am memory-limiter ignore` / `manual` / `status` が ActivityManager shell command に追加されている。
- 未確認: ベンダー設定の実端末別デフォルト、native cgroup event の実機挙動、端末ごとの制限値。

## 適用条件

この変更がいつ適用されるかを OS 条件と targetSdkVersion 条件に分けて説明する。

### OS アップデート時の挙動（OS Update Behavior）

- Android 17 にアップデートしただけで適用されるか: はい / 条件付き。`behavior-changes-all` ページに掲載され、AOSP 実装に targetSdkVersion ゲートは確認されない。
- targetSdkVersion に依存しない根拠: `MemoryLimiter` は `ActivityManagerService` / `ProcessRecord` のプロセス ライフサイクルのコードパスに接続され、targetSdkVersion を参照しない。
- Android 16 以前での挙動: Android 16 の基準挙動には `MemoryLimiter.java`、MemoryLimiter JNI、`am memory-limiter` コマンド、memory-limiter 設定 schema が存在しない。

### targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- targetSdkVersion 37 以上で適用されるか: 公式文書上、targetSdkVersion 37 は必要条件として示されていない。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: 未確認。公式文書は Android 17 all apps change として説明しているため、Android 17 platform / 端末条件が前提と考えられる。
- opt-out / 一時 override の有無: compat opt-out は確認されない。開発 / QA 用に `am memory-limiter ignore <UID|none|all>` と `manual <PID> <PERCENT|none>` がある。DeviceConfig `memory_limiter_disable_limits` / `memory_limiter_disable_kill` による実行時無効化フラグもある。

### その他の条件（Other Conditions）

- 端末 / フォーム ファクタ: 一部の Android 端末のみ。端末の合計 RAM と対象端末条件が関係する。
- 権限: 公式文書からは特定権限条件は確認できない。
- API 利用: 診断には `ApplicationExitInfo.getDescription()`、`ApplicationExitInfo.REASON_OTHER`、trigger-based profiling / `TRIGGER_TYPE_ANOMALY` が関連する。
- manifest 属性: 公式文書からは確認できない。
- コンポーネント境界: プロセス / UID 単位。`ignore` は UID または全 UID、`manual` は PID を指定し、実装は PID から UID を引いて `MemoryLimiter.setManualLimit(pid, uid, limitPercent)` を呼ぶ。

---

# AOSP 調査（AOSP Investigation）

## チェックアウト状態

確認コマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list 'android-16.0.0_r4'
git -C frameworks-base tag --list 'android-17*'
```

結果:
- `frameworks-base` の `status --short` は空で、未コミット変更は確認されなかった。
- `android-16.0.0_r4` tag は存在する。
- `android-17.0.0_r1` tag は local checkout に存在する。

根拠上の制約:
- ソース根拠は `android-16.0.0_r4` と `android-17.0.0_r1` の明示的なタグ比較、および `android-17.0.0_r1` 上のシンボル確認に限定した。
- `frameworks-base` working tree は clean のため、ローカル作業ツリーの変更を platform 根拠として誤採用するリスクは確認されていない。

## 関連ファイル（Related Files）

- `services/core/java/com/android/server/am/` 以下のプロセス / メモリ管理コードパス
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
| `MemoryLimiter.java` | ファイルなし。 | アプリ プロセスのメモリ使用量を監視 / 制限し、制限超過時に statsd / profiling / delayed kill を行う。 | Behavior Change 本体の framework-side controller。 |
| `com_android_server_am_MemoryLimiter.cpp` | ファイルなし。 | cgroup v2 の `memory.high` / `memory.swap.max` を扱う native コンポーネント。 | 実際に kernel cgroup へ制限を適用し event を監視する層。 |
| `ActivityManagerService` / `mMemoryLimiter` | MemoryLimiter 接続なし。 | `MemoryLimiter.getDefaultMemoryLimiter(mContext)` を保持し system ready で初期化する。 | AMS が system_server 内で limiter を所有する根拠。 |
| `ProcessRecord.mMemoryLimiter` | プロセスごとの limiter なし。 | UID / PID / プロセス状態更新を limiter に伝える。 | プロセス ライフサイクルと制限値割り当ての接点。 |
| `ActivityManagerShellCommand.runMemoryLimiter()` | コマンドなし。 | `ignore` / `manual` / `status` サブコマンドを実装。 | 公式テスト制御の実装根拠。 |
| `MemoryLimiter.isMemoryLimiterSupported()` | 該当なし。 | `/vendor/etc/memory-limiter-config.xml` と現在の RAM に合う設定が必要。 | 「一部端末のみ」を裏付ける端末適格性ゲート。 |
| `MemoryLimiter.onLimitExceeded()` | 該当なし。 | `LIMIT_TYPE_ANON_SWAP` で `TRIGGER_TYPE_ANOMALY` を通知し、`MemoryLimiter:AnonSwap` description 付き kill を遅延要求。 | 開発者が `ApplicationExitInfo` で観測するシグナルの根拠。 |

必須記入項目:
- Entry point / caller: アプリ プロセス ライフサイクル -> `ProcessRecord` -> `MemoryLimiter.Limiter` -> native cgroup 制限。テスト用コードパスは `adb shell am memory-limiter ...` -> `ActivityManagerShellCommand.runMemoryLimiter()` -> `MemoryLimiter`。
- Relevant class or service responsibility: プロセス メモリ制限の適用、終了 reason / description の記録、開発者向け診断。
- Runtime path from app API / system event to changed code: アプリ プロセスが起動し `ProcessRecord` が PID / UID / proc state を limiter に渡す -> native 層が cgroup 制限を設定 / 監視 -> anon+swap の制限超過で Java callback -> anomaly profiling trigger -> `"MemoryLimiter:AnonSwap"` description 付き delayed kill。
- Why unrelated code paths were excluded: 既存の heap dump 通知文字列と汎用画像 decode メモリ制限は別機能であり、アプリ プロセスの memory limiter 適用ではないため主要根拠から除外。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
| `MemoryLimiter.java` / JNI / 設定 schema / shell command が追加される | 挙動追加 | Android 17 にアプリ プロセス memory limiter が導入された直接根拠。 | High |
| `MemoryLimiter.isMemoryLimiterSupported()` がベンダー設定と現在の RAM を確認する | 条件変更 / 端末ゲート | 「一部端末のみ」を AOSP で裏付ける。 | High |
| `ProcessRecord` が UID / PID / proc state を `MemoryLimiter` に通知する | 挙動追加 / プロセス ライフサイクル統合 | アプリ プロセスに状態別メモリ制限を適用する実行時コードパス。 | High |
| `onLimitExceeded()` が `TRIGGER_TYPE_ANOMALY` と `"MemoryLimiter:AnonSwap"` delayed kill を行う | 挙動追加 / 診断シグナル | 公式文書の `ApplicationExitInfo` / profiling 診断と一致。 | High |

必須分類:
- Added behavior: Android 17 で `MemoryLimiter`、JNI コンポーネント、ベンダー設定 schema、`am memory-limiter` コマンドが追加される。
- Removed behavior: 該当なし。
- Changed condition / gate: `Flags.memoryLimiterEnable()`、`system_server`、ベンダー設定ファイル、現在の RAM に一致する設定、DeviceConfig 実行時フラグがゲート。
- Changed default: MemoryLimiter 対象端末ではプロセス状態に応じた制限値がデフォルトのコードパスに組み込まれる。
- No behavior change found: 該当しない。

## 事実（Evidence）

事実:
- 公式文書は `App memory limits` を Android 17 `Behavior changes: all apps` ページに掲載している。
- 公式文書は Android 17 が端末の合計 RAM に基づくアプリごとのメモリ制限を導入すると説明している。
- 公式文書は制限値が保守的に設定され、システムの基準値を作る目的だと説明している。
- 公式文書は対象を極端なメモリリークとメモリ使用量の外れ値と説明している。
- 公式文書はメモリ制限が一部の Android 端末のみに課されると説明している。
- 公式文書は影響を受けたセッションの exit reason が `REASON_OTHER` になり、description に `MemoryLimiter:AnonSwap` が含まれると説明している。
- 公式文書は `TRIGGER_TYPE_ANOMALY` による trigger-based profiling を診断手段として挙げている。
- 公式文書は `am memory-limiter ignore`、`manual`、`status` をテスト コマンドとして挙げている。
- 公式文書は `am memory-limiter` コマンドがメモリ制限を課さない端末では効果を持たないと説明している。
- 公式文書は `ignore <uid>` がその UID に属する全プロセスの制限適用を無視し、`all` が全アプリ、`none` が以前の ignore 設定解除を意味すると説明している。
- 公式文書は UID を ignore していても、同じアプリ内プロセスには `manual` memory limit を適用できると説明している。
- AOSP は `manual <PID> <PERCENT|none>` が PID 単位で比率指定の手動メモリ制限を課し、`none` が手動 override を解除すると説明している。
- 公式文書は `status` が表示中 / 非表示のプロセスに課されるメモリ制限を含む現在状態を報告すると説明している。
- local `frameworks-base` には `android-16.0.0_r4` タグがある。
- local `frameworks-base` には `android-17.0.0_r1` タグがある。
- 調査時点で `frameworks-base` working tree は clean。
- Android 17 タグには `MemoryLimiter.java`、`com_android_server_am_MemoryLimiter.cpp`、`MemoryLimiter.md`、memory-limiter 設定 schema、`am memory-limiter` コマンドが存在する。

観察:
- all apps ページ掲載であり、AOSP に targetSdkVersion ゲートが見つからないため、primary classification は `OS_UPDATE_ALL_APPS` とする。
- 対象端末の条件があるため、顧客向けには「Android 17 全アプリ対象候補」かつ「対象端末の条件付き」と説明する必要がある。
- テスト コマンドは compat framework ではなく ActivityManager shell command として提供される。
- `ignore` と `manual` の UID / PID の分離から、アプリ単位の ignore とプロセス単位の手動制限は別の制御経路として扱われる。
- `MemoryLimiter` は表示中 / 非表示 / キャッシュ済み / 無制限のプロセス状態ごとの制限値を持つ。

仮説:
- `MemoryLimiter:AnonSwap` は anon+swap が memory.high + memory.swap.max を超えたことに対応する制限適用理由と解釈できる。
- `am memory-limiter` サブコマンドは shell / ADB 経由の開発者向けテスト hook であり、通常の本番アプリ向け緩和策ではない。

結論:
- 公式文書と AOSP 根拠が一致するため、primary classification は `OS_UPDATE_ALL_APPS`、confidence は High とする。ただし実際に適用されるかは端末 / ベンダー設定 / RAM 条件に依存する。

## 適用ゲート根拠（Applicability Gate Evidence）

- targetSdkVersion ゲート: なし。確認したコードパスでは targetSdkVersion / compat ゲートは使われていない。
- CompatChanges.isChangeEnabled / ChangeId: 確認されず。
- @EnabledAfter / @EnabledSince / デフォルト状態: 該当なし。
- Build.VERSION / SDK_INT ゲート: 明示的な runtime SDK_INT ゲートは主根拠ではない。Android 17 platform 実装として追加。
- DeviceConfig / resources config: DeviceConfig `memory_limiter_disable_limits` / `memory_limiter_disable_kill` が実行時無効化フラグ。ベンダー設定 `/vendor/etc/memory-limiter-config.xml` が端末適格性ゲート。
- Permission/AppOps ゲート: 公式文書からは確認できない。
- Manifest/property ゲート: 公式文書からは確認できない。
- No gate found: targetSdkVersion ゲート / compat ゲートは見つからない。
- ゲート結論: Android 17 上で MemoryLimiter が feature enabled、`system_server` 内で動作し、ベンダー設定と RAM 条件を満たす端末で、対象アプリ プロセスが設定済み制限値に達した場合に適用される。
- ソース文脈からの推論: `ProcessRecord` がプロセス ライフサイクルを limiter に渡し、native cgroup 層がメモリ / swap 制限を監視し、anon+swap の制限超過で profiling trigger と delayed kill を行う。

---

# 影響分析

## 影響を受けるアプリ（Affected Apps）

- Android 17 上で動作するアプリ。
- 対象端末の条件を満たす端末上で実行されるアプリ。
- 極端なメモリリーク、大きな anonymous memory 使用、メモリ使用量の外れ値があるアプリ。
- 長時間稼働、画像 / 動画処理、ML inference、大量 cache、WebView / native heap / bitmap などでメモリ使用量が増えやすいアプリ。
- バックグラウンド プロセスや非表示プロセスでメモリを保持し続けるアプリ。

## 影響を受けないアプリ（Non-Affected Apps）

- Android 17 以外の端末上で動作する場合。
- メモリ制限が適用されない端末群で動作する場合。
- メモリ使用量のベースラインが安定しており、extreme leak / outlier がない場合。
- メモリ制限に達していないアプリ セッション。
- 対象端末に `/vendor/etc/memory-limiter-config.xml` がない、または現在の RAM に一致する制限セットがない場合。

---

# 顧客影響

## 影響度

- 要確認

※ 最終 severity / priority は人間が判断する。このレポートでは確定しない。

## ビジネス影響

- ユーザー影響: メモリ制限に達したセッションではアプリ プロセスが終了し、ユーザーにはアプリ再起動、作業中断、状態消失として見える可能性がある。
- 運用影響: crash reporting だけでは通常のクラッシュとして分類されない可能性があるため、`ApplicationExitInfo` と exit description の収集が必要になる。
- 開発影響: メモリ使用量のベースライン、leak detection、heap dump、large cache / native heap / bitmap usage の見直しが必要になる。

---

# サービス影響例

このセクションは、公式文書と AOSP 根拠から導いた「起こりうる影響例」を記録する。
特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: Google Photos / Adobe Lightroom / CapCut のような画像・動画編集機能

- 具体サービス例: Google Photos の写真編集、Adobe Lightroom の RAW / 高解像度画像編集、CapCut の動画編集。
- 影響を受ける実装パターン: 高解像度画像、一時 bitmap、decode 済み frame、native buffer、編集履歴を長時間保持する。
- 発生条件: Android 17、memory limiter 対象端末、プロセス メモリが制限値に到達する。
- ユーザーに見える症状: 編集中のアプリ再起動、作業中断、未保存状態の喪失。
- 技術的に起きていること: anonymous memory + swap の使用量が端末設定の上限に達し、memory limiter が profiling trigger と delayed kill の対象にする。
- 開発・運用への影響: メモリ使用量のベースライン測定、bitmap / native buffer lifecycle、autosave / restore path の確認が必要。
- 推奨対応候補: heap dump、trigger-based profiling、大量割り当てコードパスの棚卸し、`ApplicationExitInfo` の収集。
- 根拠: 公式文書は extreme memory leaks / outliers を対象とし、`MemoryLimiter:AnonSwap` で診断可能と説明している。
- Confidence（信頼度）: High。発生有無は対象端末 / メモリ使用量に依存する。
- 注意: 上記サービスで発生確認した事実ではない。実在サービスの機能パターンを元にした影響シーンである。

## 例2（Example 2）: Google Drive / Dropbox / Google Maps のような同期・オフライン cache 機能

- 具体サービス例: Google Drive / Dropbox のファイル同期、Google Maps のオフライン map、OneDrive の camera upload。
- 影響を受ける実装パターン: バックグラウンド プロセスが large cache、queue、native heap、decode 済みデータを保持し続ける。
- 発生条件: Android 17、memory limiter 対象端末、表示中 / 非表示プロセスの制限値に到達する。
- ユーザーに見える症状: バックグラウンド タスク中断、次回起動時の同期や処理のやり直し。
- 技術的に起きていること: visible / perceptible / cached などの process state に応じた制限を超え、プロセス終了後に work queue の復旧が必要になる。
- 開発・運用への影響: background work の checkpoint、idempotency、memory pressure handling の確認が必要。
- 推奨対応候補: WorkManager / foreground work の状態復旧、cache eviction、memory leak monitoring、`am memory-limiter manual` を使った再現試験。
- 根拠: 公式文書は status command が表示中 / 非表示プロセスのメモリ制限を報告すると説明している。
- Confidence（信頼度）: High。プロセス状態別の制限値割り当ては AOSP 根拠で確認済み。
- 注意: 上記サービスで発生確認した事実ではない。実在サービスの機能パターンを元にした影響シーンである。

---

# 対応候補（Required Actions）

## 必須対応（Must）

- Android 17 対象端末でメモリ使用量のベースラインを測定する。
- `ApplicationExitInfo` の取得・保存・分析コードパスを確認し、`REASON_OTHER` と `MemoryLimiter:AnonSwap` を検出できるようにする。
- memory leak / large allocation / unbounded cache / native heap growth の既知 issue を棚卸しする。
- アプリ再起動やプロセス終了に備えて、重要なユーザー状態の保存・復元を確認する。

## 推奨対応（Recommended）

- `am memory-limiter status` で対象端末の memory limiter 状態を確認する。
- `am memory-limiter manual <pid> <percent>` を使い、メモリ制限到達時のアプリ挙動を再現する。
- `am memory-limiter ignore <uid>|none|all` を使い、memory limiter 有無による差分を検証する。
- `TRIGGER_TYPE_ANOMALY` を使う trigger-based profiling を設定し、制限到達時の heap dump を取得する。
- Android Developers の memory best practices に沿ってメモリ使用量を最適化する。

## 任意対応（Optional）

- 大きなメモリを使う機能に対する feature flag / graceful degradation を検討する。
- 端末 RAM class / memory class / low RAM device condition に応じた cache size tuning を見直す。
- QA matrix に memory limiter 対象端末と非対象端末の比較を追加する。

---

# 検証方法（Verification Method）

変更を確認する方法。

## 検証マトリクス（Matrix）

| 端末 OS | targetSdkVersion | Compat flag / test control | 期待挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | default | Android 17 app memory limits は対象外。メモリ挙動のベースラインを測定する。 |
| Android 17 | 36 | default | 対象端末では memory limiter が適用され得る。targetSdkVersion ゲートは確認されない。 |
| Android 17 | 37 | default | targetSdkVersion 36 と同様に、対象端末では memory limiter が適用される可能性がある。 |
| Android 17 | 36 | `am memory-limiter manual <pid> <percent>` | manual limit によりメモリ制限到達時のプロセス挙動を再現する。 |
| Android 17 | 37 | `am memory-limiter ignore <uid>` | memory limiter ignore により制限適用の差分を確認する。 |

## `am memory-limiter` サブコマンド

| コマンド | 入力単位 | 目的 | 注意 |
| --- | --- | --- | --- |
| `am memory-limiter ignore <uid>` | UID | 指定 UID に属する全プロセスの制限適用を無視する | UID を ignore していても、同じアプリ内プロセスに `manual` limit は適用できる |
| `am memory-limiter ignore all` | 全アプリ | 全アプリの制限適用を無視する | QA 中に system-wide に影響するため、検証後に戻す |
| `am memory-limiter ignore none` | なし | 以前の ignore 設定を解除する | cleanup |
| `am memory-limiter manual <pid> <percent>` | PID / percent | 指定プロセスに合計 RAM 比率の手動メモリ制限を課す | AOSP help は `PERCENT: percentage of total RAM (1-99)` と説明する |
| `am memory-limiter manual <pid> none` | PID | 手動制限 override を解除する | デフォルト制限の有無は対象端末依存 |
| `am memory-limiter status` | 端末状態 | memory limiter の現在状態を表示する | 表示中 / 非表示プロセスの制限値を含む |

## 手順（Steps）

- targetSdk 変更: targetSdkVersion 36 / 37 の両方で検証し、targetSdkVersion 差分ではなく OS / 端末 / メモリ条件の差分として観測されるか確認する。
- compat framework command: 公式文書上 compat flag は未確認。代わりに `am memory-limiter` コマンドを使う。
- テスト方法:
  - `am memory-limiter status`
  - `am memory-limiter manual <pid> <percent>|none`
  - `am memory-limiter ignore <uid>|none|all`
  - `ApplicationExitInfo.getDescription()` の収集
  - `TRIGGER_TYPE_ANOMALY` を使う trigger-based profiling
- 再現手順:
  - Android 17 対象端末でアプリを起動する。
  - `am memory-limiter status` を実行し、その端末がメモリ制限を課しているか確認する。メモリ制限を課さない端末ではコマンドは効果を持たない。
  - メモリ使用量のベースラインを測定する。
  - 手動メモリ制限を設定する。
  - 必要に応じて `am memory-limiter ignore <uid>` / `am memory-limiter ignore none` で制限適用の有無による差分を確認する。
  - 大量割り当て / 既知のメモリ集中フローを実行する。
  - プロセス終了後、`ApplicationExitInfo` の reason / description を確認する。
- 期待結果:
  - 制限到達時にアプリ セッションが影響を受ける。
  - exit reason は `REASON_OTHER`。
  - description に `MemoryLimiter:AnonSwap` が含まれる。
  - heap dump / profiling artifact が取得できる場合、メモリ増加の原因を分析できる。

---

# 結論（Conclusion）

App memory limits は、Android 17 all apps ページに掲載され、AOSP でも targetSdkVersion ゲートが確認されないため、targetSdkVersion 更新ではなく Android 17 OS アップデート側の影響である。ただし、一部の端末にのみ適用される条件付き変更であり、ベンダー設定と端末 RAM 条件に依存する。

Android アプリ開発者は、Android 17 対応の一環としてメモリ使用量のベースライン、leak / outlier detection、`ApplicationExitInfo` による診断、`am memory-limiter` を使った再現検証を準備する必要がある。

---

# 人間の判断欄

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 人間による判断が必要

判断理由候補:
- 公式文書と AOSP 根拠は all apps change を支持するが、顧客影響は対象端末の条件とメモリ使用パターンに依存する。
- 顧客影響はメモリ使用パターンに依存するため、実サービスのメモリ使用量のベースラインとクラッシュ / プロセス終了の計測データを見て判断する必要がある。

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

---

## 再検証記録（2026-08-22）

### 調査日（Investigation Date）

- 2026-08-22

### 公式ドキュメント再確認（Original Documentation Recheck）

- Android 17 の all-apps / target Behavior Change ページを再取得し、このレポートが参照する公式 section の掲載と適用範囲を再確認した。
- 公式ページの最終更新表示: all-apps / target: 2026-08-14 UTC。
- Android 17 compat framework 一覧は 2026-08-22 時点でも HTTP 404 のため、公式 Behavior Change 文書と AOSP annotation / gate を正とした。
- 既存の引用は短い要約として扱い、適用条件は公式ページ種別と AOSP gate の両方で再評価した。

### AOSP 証拠ワークスペース（AOSP Evidence Workspaces）

| AOSP project | Official remote URL | Checkout path | Working tree | From tag / resolved commit | To tag / resolved commit | Comparison command | Dirty risk / limitations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `platform/frameworks/base` | `https://android.googlesource.com/platform/frameworks/base` | `frameworks-base/` | Clean | `android-16.0.0_r4` / `45034f0663f960d9ee5fb0a101a4732b71f6e2f4` | `android-17.0.0_r1` / `94b4c163b7dfe5ce3607f7bb8456f9573f7de57d` | `git -C frameworks-base diff --no-renames --name-only android-16.0.0_r4 android-17.0.0_r1` | なし。明示タグ比較のため working tree の内容は根拠に含めない。 |

### ソース文脈・差分解釈の再確認（Source Context Reviewed / Diff Interpretation）

- 各 official remote で Android 16 / 17 の最新通常リリースタグが `android-16.0.0_r4` / `android-17.0.0_r1` のままであることを確認した。
- 上表の project-level `--name-only` 比較を再実行し、既存本文の path / symbol 別 source context、gate、追加・削除・条件変更・既定値変更・差分なしの解釈を再確認した。
- タグと解決済み commit が既存調査の比較対象から変わっていないため、本文の evidence record を別タグへ機械的に置換していない。
- 実機 Observed は新規実施していない。既存の「未実施」「未確認」および不足根拠はそのまま維持した。

### 事実（Facts）

- `android-16.0.0_r4` と `android-17.0.0_r1` は 2026-08-22 時点の最新通常リリースタグである。
- 上表に再検証時の working tree 状態を記録し、official remote、両タグ、解決済み commit を確認した。展開中または dirty の working tree は根拠に使用していない。
- 公式 section と AOSP evidence の比較 pair は一致している。

### 観察（Observations）

- 最新タグが変わっていないため、今回の再検証で既存の source diff 解釈を変更する新しい AOSP tag evidence は生じなかった。
- report 内に残る Medium / Low confidence、OEM / Mainline / QPR 条件、未確認の module enforcement は解消したものとして扱わない。

### 仮説（Hypotheses）

- 新しい仮説は追加しない。既存本文で仮説または可能性として記載した事項は、実機・製品 build・未確認 module の evidence が得られるまで事実へ昇格しない。

### 結論（Conclusions）

- 既存本文の主分類、confidence、対応候補を維持する。既存の不足根拠がある場合はその制約も維持する。
- 全件再検証の横断記録は [`android17/analysis/REVALIDATION_2026-08-22.md`](../../../analysis/REVALIDATION_2026-08-22.md) を参照する。

### Human Decision

- この再検証では最終 priority、severity、release readiness、顧客説明優先度を変更していない。
- 人間の判断は [Android 17 Decision Log](../../../decisions/DECISION_LOG.md) を正とする。

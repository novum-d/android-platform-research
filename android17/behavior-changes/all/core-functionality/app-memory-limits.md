# App memory limits

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

比較元:
- android-16.0.0_r4

比較先:
- TBD: Android 17 AOSP tag

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
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- 公式文書は Android 17 の `Behavior changes: all apps` ページにこの項目を掲載しているため、一次判断では `OS_UPDATE_ALL_APPS` 候補である。
- ただし、local `frameworks-base` に Android 17 AOSP tag がないため、memory limiter 実装、targetSdkVersion gate の有無、device eligibility gate、DeviceConfig / resource config、compat framework default state は未確認である。
- 公式文書は「一部の Android devices のみで memory limits が課される」と明記しているため、OS update impact であっても device 条件付きの挙動として扱う必要がある。

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 可能性は高いが条件付き、かつ未検証 | `behavior-changes-all` ページに掲載。公式文書は all apps 対象ページであるが、AOSP gate 未確認。 |
| targetSdkVersion 37 以上が必要か | 不要と考えられるが未検証 | all apps ページの説明から targetSdkVersion 非依存と読むのが自然。ただし AOSP targetSdkVersion gate 未確認。 |
| 追加の実行時条件があるか | ある | 公式文書は memory limits が一部の Android devices のみに課されると説明している。 |
| Compat Change ID が関係するか | 未確認 | Android 17 tag と compat framework evidence が未確認。 |

### 調査日（Investigation Date）

2026-06-15

### 信頼度（Confidence）

- Low

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] targetSdkVersion に関係なく Android 17 の全アプリへ適用
- [ ] Android 17 以上かつ targetSdkVersion 37 以上で適用
- [ ] targetSdkVersion 37 以上かつ追加の実行時条件を満たす場合に適用
- [ ] Mainline / Google Play system update に依存
- [ ] API 追加のみであり、挙動変更ではない
- [x] 未確認 / 追加 evidence が必要

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 であることが前提。Android 17 AOSP tag 未取得のため実装上の OS gate は未確認。
- targetSdkVersion: 公式文書上は targetSdkVersion に依存しない all apps change と読める。AOSP gate 未確認。
- Device/form factor: 一部の Android devices のみ。device total RAM、device eligibility、config / DeviceConfig 条件は AOSP tag 待ち。
- Permission/API/component condition: アプリが制限値を超える memory usage、特に extreme memory leak / outlier に該当する場合に影響が顕在化する。
- App state/process condition: visible / non-visible process 別の limit が存在する可能性があると公式 test command の `status` 説明から読めるが、実装未確認。

Compat framework:
- Change ID: 未確認
- 変更名: 未確認
- 既定状態: 未確認
- テスト時の切り替え可否: 公式文書は compat flag ではなく `am memory-limiter` command による test controls を説明している。compat framework entry は未確認。

分類信頼度（Classification confidence）:
- Low

分類根拠（Classification evidence）:
- 公式ドキュメントページ: `behavior-changes-all`
- 検証対象の適用条件文: Android 17 all-apps page states that its changes apply to all apps running on Android 17 regardless of targetSdkVersion.
- AOSP targetSdk gate: 未確認。local `frameworks-base` に `android-17*` tag がない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# エグゼクティブサマリー（Executive Summary）

Android 17 では、device total RAM に基づく app memory limits が導入され、極端な memory leak や outlier が system-wide instability、UI stutter、battery drain、app kill につながる前に制御される、と公式文書は説明している。

この項目は Android 17 の all apps ページに掲載されているため、targetSdkVersion 37 への更新有無に関係なく Android 17 上で影響する可能性がある。ただし、公式文書は memory limits が一部の Android devices のみに課されると説明しているため、全端末で必ず発生する変更ではない。

現時点では local `frameworks-base` に Android 17 AOSP tag がないため、memory limiter の実装、device eligibility、targetSdkVersion gate の不存在、compat framework entry は未確認である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とし、Android 17 AOSP tag 公開後に再調査する。

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
- The `am memory-limiter` subcommands are `ignore <uid>|none|all`, `manual <pid> <limit>|max|none`, and `status`.
- These commands have no effect on devices that do not impose memory limits.
- `ignore <uid>` ignores enforcement for all processes associated with that UID; `all` ignores all apps; `none` clears previous ignore settings.
- Even if a UID is ignored, `manual` can still apply a memory limit to a process in that app.
- `manual <pid> <limit>` imposes a MB-based memory constraint on a process; `max` removes all memory limits for that process; `none` removes manual limits and restores the system default if any.
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
- `manual` は PID 単位で MB 指定の memory constraint を課す。
- `status` は visible / non-visible process に課される memory limit 状態を報告する。

AOSP で未確認の点:
- memory limiter の実装ファイル、service / daemon / LMKD との関係。
- limit がどの process state、UID、cgroup、anon swap accounting、visible / non-visible process に適用されるか。
- device total RAM から limit を算出する具体式。
- 一部 devices の判定条件。
- targetSdkVersion gate が本当に存在しないか。
- compat framework Change ID の有無。

## 適用条件（Applicability）

この変更がいつ適用されるかを OS 条件と targetSdkVersion 条件に分けて説明する。

### OS アップデート時の挙動（OS Update Behavior）

- Android 17 にアップデートしただけで適用されるか: 公式文書上は Yes / Conditional。`behavior-changes-all` ページに掲載されているため、targetSdkVersion に依存しない all apps change と読む。
- targetSdkVersion に依存しない根拠: 公式ページ全体が「Android 17 上で動作する全アプリに適用される」と説明している。
- Android 16 以前での挙動: この Behavior Change としての app memory limits は公式文書上 Android 17 introduced とされる。AOSP baseline 実装差分は未確認。

### targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- targetSdkVersion 37 以上で適用されるか: 公式文書上、targetSdkVersion 37 は必要条件として示されていない。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: 未確認。公式文書は Android 17 all apps change として説明しているため、Android 17 platform / device condition が前提と考えられる。
- opt-out / temporary override の有無: compat opt-out は未確認。公式文書は `am memory-limiter ignore <uid>|none|all` と manual limits による test controls を説明している。

### その他の条件（Other Conditions）

- device/form factor: 一部の Android devices のみ。device total RAM と device eligibility が関係する。
- permission: 公式文書からは特定 permission 条件は確認できない。
- API usage: 診断には `ApplicationExitInfo.getDescription()`、`ApplicationExitInfo.REASON_OTHER`、trigger-based profiling / `TRIGGER_TYPE_ANOMALY` が関連する。
- manifest attribute: 公式文書からは確認できない。
- component boundary: process / UID 単位で制限される可能性がある。`am memory-limiter ignore <uid>` と `manual <pid>` から UID / PID 境界の test control があることは読み取れるが、実装境界は AOSP tag 待ち。

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
- `android-17*` tag は local checkout に存在しない。

根拠上の制約:
- Android 17 AOSP tag が local `frameworks-base` にないため、`android-16.0.0_r4` と Android 17 tag の明示的な source diff は実行できない。
- そのため、local working tree や未確定 branch を platform evidence として扱わない。
- 本レポートの AOSP-backed conclusion は Low confidence に留める。

## 関連ファイル（Related Files）

Android 17 AOSP tag 未取得のため、tag diff に基づく related files は未確定。

Android 17 tag 公開後に確認すべき候補:
- `services/core/java/com/android/server/am/` 以下の process / memory management path
- `services/core/java/com/android/server/` 以下の memory limiter command / shell command implementation
- `cmds/am/` または ActivityManager shell command の `memory-limiter` subcommands
- UID / PID lookup、shell permission、caller permission、user boundary を扱う command path
- LMKD / ProcessList / OOM adjustment / cgroup / memory pressure 関連 path
- `core/java/android/app/ApplicationExitInfo.java`
- trigger-based profiling / `ProfilingManager` / anomaly trigger 関連 API surface

## 確認したソース文脈（Source Context Reviewed）

AOSP tag diff は未実行。以下は公式文書から見た確認予定の source context であり、AOSP evidence ではない。

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| ActivityManager / process memory management path | 未確認 | device total RAM に基づく app memory limits の enforcement が存在する可能性 | app process に memory limit を課す中心 path と考えられる |
| ActivityManager shell command `am memory-limiter` | 未確認 | `ignore` / `manual` / `status` subcommands が提供されると公式文書が説明 | developer test controls の実装 root になる可能性 |
| UID / PID command handling | 未確認 | `ignore` は UID、`manual` は PID を受け取ると公式文書が説明 | app 全体の ignore と process 単位 manual limit の境界を確認するため |
| visible / non-visible process status reporting | 未確認 | `status` が visible / non-visible process limits を報告すると公式文書が説明 | process state ごとの limit が存在するかを確認するため |
| `ApplicationExitInfo.getDescription()` / `REASON_OTHER` | 未確認 | memory limiter 影響時に `MemoryLimiter:AnonSwap` を含む description を返すと公式文書が説明 | app developer が影響を観測する public API |
| trigger-based profiling / `TRIGGER_TYPE_ANOMALY` | 未確認 | memory limit hit 時に heap dump collection に使えると公式文書が説明 | memory limit hit の診断 path |

必須記入項目:
- Entry point / caller: 未確認。Android 17 tag 公開後に `adb shell am memory-limiter ...` -> ActivityManager shell command -> memory limiter service / controller の command path、process memory accounting / kill path、`ApplicationExitInfo` recording path を確認する。
- Relevant class or service responsibility: process memory limit enforcement、exit reason / description recording、developer diagnostics。
- Runtime path from app API / system event to changed code: アプリ process の memory usage が limit を超える -> system memory limiter が enforcement -> process exit / record -> app が後続起動時に `ApplicationExitInfo` から診断、という path が想定される。検証 path としては、`adb shell am memory-limiter status` で対象 device / current limits を確認し、`adb shell am memory-limiter manual <pid> <limit>` で process 単位の manual limit を設定する。
- Why unrelated code paths were excluded: tag diff 未実行のため、除外判断は未完了。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
| Android 17 tag 未取得のため source diff 未確認 | 公式文書上は added behavior / changed condition と読める | app memory limits の新規導入、device subset condition、diagnostic signal が説明されている | Low |

必須分類:
- Added behavior: 公式文書上、Android 17 で app memory limits が導入される。
- Removed behavior: 未確認。
- Changed condition / gate: 公式文書上、一部 devices でのみ imposed。AOSP gate 未確認。
- Changed default: 未確認。Android 17 の platform default として有効になる可能性があるが、device / config default は AOSP tag 待ち。
- No behavior change found: 未確認。

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
- 公式文書は `manual <pid> <limit>` が PID 単位で MB 指定の memory constraint を課し、`max` が全 memory limits を削除し、`none` が manual limit を解除して system default limit があれば復元すると説明している。
- 公式文書は `status` が visible / non-visible processes に課される memory limits を含む current status を報告すると説明している。

観察:
- all apps ページ掲載のため、一次分類は `OS_UPDATE_ALL_APPS` 候補である。
- device subset condition があるため、顧客向けには「Android 17 全アプリ対象候補」かつ「対象 device 条件付き」と説明する必要がある。
- test command は compat framework ではなく ActivityManager shell command として提供される可能性がある。
- `ignore` と `manual` の UID / PID split から、app-level ignore と process-level manual limit は別の control plane として扱われる可能性がある。
- `status` が visible / non-visible process limits を報告することから、process state ごとの limit が存在する可能性がある。

仮説:
- enforcement は targetSdkVersion 37 gate ではなく、Android 17 platform / device config / process state / memory usage により制御される可能性が高い。
- visible / non-visible process に異なる limit がある可能性がある。
- `MemoryLimiter:AnonSwap` は anon swap usage または memory accounting に基づく enforcement reason を示している可能性がある。
- `am memory-limiter` subcommands は shell / ADB 経由の developer-facing test hook であり、通常の app production mitigation ではない可能性が高い。

結論:
- 現時点の確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE`。公式文書上は `OS_UPDATE_ALL_APPS` 候補だが、AOSP tag 未取得のため High confidence にできない。

## 適用ゲート根拠（Applicability Gate Evidence）

- targetSdkVersion gate: 未確認。公式文書上は targetSdkVersion 条件なし。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。
- @EnabledAfter / @EnabledSince / default state: 未確認。
- Build.VERSION / SDK_INT gate: 未確認。公式文書上は Android 17 introduced。
- DeviceConfig / resources config: 未確認。一部 devices のみという条件から、device config / resource config / feature flag が存在する可能性がある。
- Permission/AppOps gate: 公式文書からは確認できない。
- Manifest/property gate: 公式文書からは確認できない。
- No gate found: 未確認。AOSP tag 未取得のため gate search 未実行。
- Gate conclusion: 公式文書上は Android 17 all apps + device subset condition。AOSP evidence 未取得のため `UNKNOWN_NEEDS_MORE_EVIDENCE`。
- Reasoning from source context: source context は未確認。公式文書の page type と statement のみから一次判断している。

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
- ただし、AOSP tag 未取得のため正確な non-affected condition は未確定。

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
- Confidence（信頼度）: Low。AOSP enforcement condition 未確認。
- 注意: 実サービスで発生確認した事実ではない。

## 例2（Example 2）: 長時間 background 同期 / cache 保持アプリ

- 対象サービス例: file sync、offline cache、document scanner、map / media cache。
- 影響を受ける実装パターン: background process が large cache、queue、native heap、decoded data を保持し続ける。
- 発生条件: Android 17、memory limiter 対象 device、visible / non-visible process の limit に到達する。
- ユーザーに見える症状: background task 中断、次回起動時の同期や処理のやり直し。
- 開発・運用への影響: background work の checkpoint、idempotency、memory pressure handling の確認が必要。
- 推奨対応候補: WorkManager / foreground work の状態復旧、cache eviction、memory leak monitoring、`am memory-limiter manual` を使った再現試験。
- 根拠: 公式文書は status command が visible / non-visible process の memory limits を報告すると説明している。
- Confidence（信頼度）: Low。process state 別 enforcement は AOSP tag 待ち。
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
- `am memory-limiter manual <pid> <limit>` を使い、memory limit 到達時の app behavior を再現する。
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
| Android 17 | 36 | default | 公式文書上は all apps change のため、対象 device では memory limiter が適用される可能性がある。AOSP gate 未確認。 |
| Android 17 | 37 | default | targetSdkVersion 36 と同様に、対象 device では memory limiter が適用される可能性がある。 |
| Android 17 | 36 | `am memory-limiter manual <pid> <limit>` | manual limit により memory limit hit 時の process behavior を再現する。 |
| Android 17 | 37 | `am memory-limiter ignore <uid>` | memory limiter ignore により enforcement 差分を確認する。 |

## `am memory-limiter` subcommands

| Command | 入力単位 | 目的 | 注意 |
| --- | --- | --- | --- |
| `am memory-limiter ignore <uid>` | UID | 指定 UID に属する全 process の enforcement を ignore する | UID を ignore していても、同じ app 内 process に `manual` limit は適用できる |
| `am memory-limiter ignore all` | all apps | 全アプリの enforcement を ignore する | QA 中に system-wide に影響するため、検証後に戻す |
| `am memory-limiter ignore none` | none | 以前の ignore 設定を解除する | cleanup |
| `am memory-limiter manual <pid> <limit>` | PID / MB | 指定 process に MB 単位の memory constraint を課す | 例: `30` = 30MB |
| `am memory-limiter manual <pid> max` | PID | 指定 process の全 memory limits を削除する | system default との差分は AOSP tag 公開後に確認する |
| `am memory-limiter manual <pid> none` | PID | manual limit を解除し、system default limit があれば復元する | default limit の有無は対象 device 依存 |
| `am memory-limiter status` | device state | memory limiter の現在状態を表示する | visible / non-visible process limits を含む |

## 手順（Steps）

- targetSdk変更: targetSdkVersion 36 / 37 の両方で検証し、targetSdkVersion 差分ではなく OS / device / memory condition 差分として観測されるか確認する。
- compat framework command: 公式文書上 compat flag は未確認。代わりに `am memory-limiter` commands を使う。
- テスト方法:
  - `am memory-limiter status`
  - `am memory-limiter manual <pid> <limit>|max|none`
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

App memory limits は、Android 17 all apps ページに掲載されているため、targetSdkVersion 更新ではなく Android 17 OS update 側の影響候補である。ただし、一部 devices のみで imposed される条件付き変更であり、AOSP tag 未取得のため確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

Android app developer は、Android 17 対応の一環として memory baseline、leak / outlier detection、`ApplicationExitInfo` による診断、`am memory-limiter` を使った再現検証を準備する必要がある。

---

# 人間の判断欄

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- Android 17 AOSP tag 公開後に追加調査が必要

判断理由候補:
- 公式文書上は all apps change だが、device subset condition と AOSP gate 未確認が残っている。
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

- 未確認。local `frameworks-base` に Android 17 AOSP tag がないため、tag diff による source evidence は未取得。

# Restoring default IME visibility after rotation

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP tag

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

### Behavior Change 文書（Behavior Change Source）

Document:
- https://developer.android.com/about/versions/17/behavior-changes-all

Related documents:
- https://developer.android.com/guide/topics/manifest/activity-element#wsoft
- https://developer.android.com/reference/android/app/Activity#onCreate(android.os.Bundle)
- https://developer.android.com/reference/android/app/Activity#onConfigurationChanged(android.content.res.Configuration)
- https://developer.android.com/reference/android/view/WindowInsetsController#show(int)

Section:
- Restoring default IME visibility after rotation

Page type:
- Behavior changes: all apps

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- 公式文書は Android 17 の `Behavior changes: all apps` ページにこの項目を掲載している。
- 原文は、Android 17 から device configuration change、たとえば rotation が発生し、それを app 自身が処理しない場合、以前の IME visibility は復元されないと説明している。
- 原文には targetSdkVersion 条件は記載されていない。
- ただし、local `frameworks-base` に Android 17 AOSP tag がないため、Activity recreation / WindowManager / Insets / IME visibility restoration / compat framework entry は未確認である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | Likely Yes / Conditional, but unverified | 公式文書は all apps ページに掲載し、targetSdkVersion 条件を示していない。AOSP gate 未確認。 |
| targetSdkVersion 37 以上が必要か | Likely No, but unverified | 原文に targetSdkVersion 条件はない。AOSP targetSdkVersion gate 未確認。 |
| 追加の実行時条件があるか | Yes | configuration change が発生し、app がそれを自身で処理せず、以前の IME visibility の自動復元を期待している場合。 |
| Compat Change ID が関係するか | Unknown | Android 17 tag と compat framework evidence が未確認。 |

### 調査日（Investigation Date）

2026-06-15

### 信頼度（Confidence）

- Low

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] OS update / all apps on Android 17 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 37 on Android 17+
- [ ] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [x] Unknown / needs more evidence

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 以上。AOSP tag 未取得のため実装上の OS gate は未確認。
- targetSdkVersion: 公式文書上は条件なし。AOSP targetSdkVersion gate 未確認。
- Device/form factor: rotation など configuration change が発生する端末状態。
- Permission/API/component condition: IME / soft keyboard、focused text field、`android:windowSoftInputMode`、`stateAlwaysVisible`、`Activity.onCreate()`、`Activity.onConfigurationChanged()`、`WindowInsetsController.show()`、`InputMethodManager`。
- App state/process condition: app が configuration change を自身で処理せず、Activity recreation 後に以前の IME visibility が自動復元されることを期待している場合。

Compat framework:
- Change ID: Unknown
- Change name: Unknown
- Default state: Unknown
- Toggleable for testing: Unknown

分類信頼度（Classification confidence）:
- Low

分類根拠（Classification evidence）:
- Official documentation page: `behavior-changes-all`
- Original applicability statement: Android 17 から、app が処理しない configuration change 後に previous IME visibility は復元されない。
- AOSP targetSdk gate: 未確認。local `frameworks-base` に `android-17*` tag がない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# エグゼクティブサマリー（Executive Summary）

Android 17 では、rotation などの configuration change が発生し、その変更を app 自身が処理しない場合、変更前に表示されていた IME / soft keyboard visibility が自動復元されない、と公式文書は説明している。

影響を受けるのは、画面回転などで Activity が再生成された後も keyboard が表示されたままであることを前提にしている入力画面である。たとえば検索、ログイン、チャット、業務入力フォームで、rotation 後もすぐ入力継続できることを期待している場合は、明示的な keyboard 表示要求が必要になる。

公式文書は targetSdkVersion 条件を示していないため、初期判断では OS update / all apps 型の候補である。ただし現時点では local `frameworks-base` に Android 17 AOSP tag がなく、実装上の gate、compat Change ID、targetSdkVersion 分岐の有無を確認できない。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とし、信頼度は Low とする。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statement）

Page title:
- Behavior changes: all apps

Page URL:
- https://developer.android.com/about/versions/17/behavior-changes-all

Page type:
- all apps

Section title:
- Restoring default IME visibility after rotation

Original statement being verified:
- Beginning with Android 17, when the device's configuration changes, for example through rotation, and this is not handled by the app itself, the previous IME visibility is not restored.
- If the app needs the keyboard to be visible after an unhandled configuration change, the app must explicitly request it.
- Mitigation options are setting `android:windowSoftInputMode` to `stateAlwaysVisible`, requesting the soft keyboard in `Activity.onCreate()`, or adding / using `onConfigurationChanged()`.

## 解釈（Interpretation）

この変更は、configuration change 後の IME visibility restoration default を変える挙動変更である。Android 16 以前では、rotation 前に keyboard が表示されていた状態が Activity recreation 後に復元されるケースがあったと読み取れる。一方 Android 17 では、app が configuration change を処理していない場合、system は previous IME visibility を復元しない。

顧客向けには「IME が表示できなくなる」ではなく、「未処理の configuration change 後に、以前表示されていた IME を system が自動で戻さない」と説明する必要がある。keyboard が必要な screen では、manifest または code で明示的に表示要求を行う。

---

# 変更内容（What Changed）

公式文書上の変更点:
- Android 17 から、app が処理しない configuration change 後に previous IME visibility は復元されない。
- rotation は代表例であり、configuration change 全般が対象候補になる。
- app が変更後も keyboard 表示を必要とする場合は、明示的に request する必要がある。
- 対応候補は `android:windowSoftInputMode="stateAlwaysVisible"`、`Activity.onCreate()` での programmatic request、または `onConfigurationChanged()` の利用。

AOSP で未確認の点:
- IME visibility restoration を抑止する実装箇所。
- Activity recreation / configuration change handling のどの段階で previous IME visibility state を破棄または無視するか。
- targetSdkVersion gate の有無。
- compat framework Change ID と default state。
- `windowSoftInputMode=stateAlwaysVisible` と programmatic request の適用順序、focus / window attachment timing による差分。
- app が `configChanges` を宣言して `onConfigurationChanged()` で処理する場合の実装上の扱い。

## 適用条件（Applicability）

この変更がいつ適用されるかを OS 条件と targetSdkVersion 条件に分けて説明する。

### OS アップデート時の挙動（OS Update Behavior）

- Android 17 に OS アップデートしただけで適用されるか: 公式文書上は Yes / Conditional。all apps ページに掲載され、targetSdkVersion 条件は示されていない。ただし AOSP gate 未確認。
- targetSdkVersion に依存しない根拠: 原文に targetSdkVersion 条件がない。
- Android 16 以前での挙動: 公式文書は Android 17 から previous IME visibility が復元されないと説明している。Android 16 baseline の restoration path は AOSP diff 未確認。

### targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- targetSdkVersion 37 以上で適用されるか: 公式文書上、targetSdkVersion 37 は必要条件ではない。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: Unknown。公式文書は Android 17 platform behavior として説明している。
- opt-out / temporary override の有無: 未確認。公式文書には opt-out は記載されていない。

### その他の条件（Other Conditions）

- device/form factor: rotation など configuration change が発生する端末状態。
- app configuration handling: app が configuration change を自身で処理しない場合が主対象。`configChanges` と `onConfigurationChanged()` を使う場合は別途確認が必要。
- UI state: text input があり、変更後も keyboard を表示しておく必要がある screen。
- API usage: `android:windowSoftInputMode`、`WindowInsetsController.show(WindowInsets.Type.ime())`、`InputMethodManager.showSoftInput()`、focus management。
- not affected / lower risk: rotation 後に keyboard 表示を必要としない screen、入力欄がない screen、app 側で configuration change と IME 表示を明示的に制御している screen。

---

# AOSP 調査（AOSP Investigation）

## checkout 状態（Checkout Status）

確認コマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list 'android-17*'
```

結果:
- `frameworks-base` の `status --short` は空で、dirty working tree は確認されなかった。
- `android-16.0.0_r4` tag は存在する。
- `android-17*` tag は local checkout に存在しない。

Evidence limitation:
- Android 17 AOSP tag が local `frameworks-base` にないため、`android-16.0.0_r4` と Android 17 tag の明示的な source diff は実行できない。
- そのため、local working tree や未確定 branch を platform evidence として扱わない。
- 本レポートの AOSP-backed conclusion は Low confidence に留める。

## 関連ファイル（Related Files）

Android 17 AOSP tag 未取得のため、tag diff に基づく related files は未確定。

Android 17 tag 公開後に確認すべき候補:
- `core/java/android/app/Activity.java`
- `core/java/android/app/ActivityThread.java`
- `core/java/android/view/WindowInsetsController.java`
- `core/java/android/view/inputmethod/InputMethodManager.java`
- `services/core/java/com/android/server/inputmethod/` 以下の InputMethodManagerService path
- `services/core/java/com/android/server/wm/` 以下の Activity / Window / Insets / configuration change path
- compat framework 定義ファイル内の IME visibility / rotation / configuration change 関連 Change ID

## 確認したソース文脈（Source Context Reviewed）

AOSP tag diff は未実行。以下は公式文書から見た確認予定の source context であり、AOSP evidence ではない。

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| Activity recreation / configuration change path | 未確認 | unhandled configuration change 後に previous IME visibility を復元しないと公式文書が説明 | rotation などで app process / Activity lifecycle が進む入口になるため |
| Window / Insets IME visibility restoration path | 未確認 | previous IME visibility restoration が抑止される可能性 | keyboard visibility state の保存 / 復元を扱う可能性が高いため |
| InputMethodManager / InputMethodManagerService path | 未確認 | app が明示的に IME 表示を request した場合は表示できると公式文書が説明 | programmatic request の到達先であり mitigation の実効性確認に必要なため |
| `android:windowSoftInputMode` / `stateAlwaysVisible` handling | 未確認 | manifest attribute による明示要求が mitigation とされている | declarative mitigation の適用条件と timing を確認するため |
| compat framework entry | 未確認 | targetSdkVersion gate の有無は不明 | all apps 型か targetSdkVersion gate 型かの確定に必要なため |

必須記入項目（Required context）:
- Entry point / caller: 未確認。想定される entry point は device rotation / configuration change -> Activity recreation or `onConfigurationChanged()` -> window focus / insets state -> IME visibility decision。
- Relevant class or service responsibility: Activity lifecycle、configuration change dispatch、Window / Insets state、IME show / hide control。
- Runtime path from app API / system event to changed code: rotation などで configuration change 発生 -> app が change を処理しない場合 Activity recreation -> Android 17 は previous IME visibility を自動復元しない -> app が必要なら `stateAlwaysVisible` または programmatic show で表示要求、という path が想定される。AOSP evidence としては未確認。
- Why unrelated code paths were excluded: tag diff 未実行のため、除外判断は未完了。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
| Android 17 tag 未取得のため source diff 未確認 | 公式文書上は changed default / changed condition と読める | unhandled configuration change 後に previous IME visibility が復元されないと説明されている | Low |

必須分類（Required interpretation）:
- Added behavior: 未確認。previous IME visibility restoration を抑止する条件が追加された可能性がある。
- Removed behavior: 未確認。rotation 後の implicit IME restoration が削除または限定された可能性がある。
- Changed condition: 未確認。configuration change handling 状態によって restoration が分岐する可能性がある。
- Changed default: 公式文書上は該当候補。以前の IME visibility を自動復元しない default に変わったと読める。
- No behavior change: 現時点では公式文書上の説明と矛盾するため候補ではないが、AOSP tag diff で確認が必要。

---

# 影響分析（Impact Analysis）

## 影響を受ける可能性があるアプリ（Potentially Affected Apps）

- 検索画面、ログイン画面、チャット画面、メモ入力、業務入力フォームなど、rotation 後も keyboard 表示を継続したい screen。
- `EditText` / text field に focus がある状態で rotation し、Activity recreation 後に keyboard が自動で戻ることを期待している app。
- form 入力中の orientation change を許容している app。
- tablet / foldable / desktop mode など configuration change が起きやすい UI を持つ app。

## 影響を受けにくいアプリ（Less Likely Affected）

- rotation 後に keyboard 表示を必要としない app。
- 入力欄がない screen。
- orientation を固定しており、該当 configuration change が通常発生しない screen。
- app 側で `onConfigurationChanged()` や lifecycle restore 後の focus / IME request を明示的に制御している screen。ただし実装の timing は検証が必要。

## 顧客向けリスク（Customer-facing Risk）

- rotation 後に keyboard が閉じたままになり、ユーザーが再度 text field を tap する必要が出る。
- 入力継続を前提にした workflow で操作ステップが増える。
- 自動テストや E2E テストが「rotation 後に keyboard が表示されている」前提の場合、Android 17 で失敗する可能性がある。
- form validation、focus restore、IME action handling など keyboard visibility に依存する UI 状態の再確認が必要になる。

---

# 対応候補（Recommended Action Candidates）

## 実装対応（Implementation）

- rotation / configuration change 後も keyboard 表示が必要な screen を棚卸しする。
- Activity 単位で常に keyboard 表示が適切な場合は、`android:windowSoftInputMode="stateAlwaysVisible"` を検討する。
- 特定条件でのみ keyboard 表示が必要な場合は、`Activity.onCreate()` で focus restore 後に `WindowInsetsController.show(WindowInsets.Type.ime())` などを使って明示的に request する。
- app が `configChanges` を宣言して自身で configuration change を処理する場合は、`onConfigurationChanged()` 内またはその後の UI 更新後に必要な IME request を行う。
- keyboard を不要な screen で強制表示しないよう、画面単位・状態単位で条件を分ける。

## 検証対応（Testing）

- Android 16 / targetSdkVersion 36 で baseline を確認する。
- Android 17 / targetSdkVersion 36 と Android 17 / targetSdkVersion 37 の両方で、rotation 前後の focus と IME visibility を確認する。
- `windowSoftInputMode=stateAlwaysVisible`、`onCreate()` での programmatic request、`onConfigurationChanged()` での request を別々に検証する。
- phone、tablet、foldable など configuration change の頻度や windowing behavior が異なる device state で確認する。
- keyboard 表示 request の timing が早すぎて無視されないか、window focus / view attachment 後に有効かを確認する。

## 顧客説明候補（Customer Explanation）

Android 17 では、画面回転などで app が処理しない configuration change が発生した後、変更前に表示されていた keyboard は system によって自動復元されません。rotation 後も keyboard を表示したい画面では、manifest の `android:windowSoftInputMode="stateAlwaysVisible"` または Activity lifecycle 内の明示的な IME 表示要求を追加してください。

---

# 検証マトリクス（Verification Matrix）

| Device OS | targetSdkVersion | App condition | Expected behavior |
| --- | --- | --- | --- |
| Android 16 | 36 | keyboard 表示中に rotation、app は configuration change を処理しない | baseline。previous IME visibility restoration の有無を確認。 |
| Android 17 | 36 | keyboard 表示中に rotation、app は configuration change を処理しない | previous IME visibility は自動復元されない可能性。公式文書上の変更対象。AOSP gate 未確認。 |
| Android 17 | 37 | keyboard 表示中に rotation、app は configuration change を処理しない | targetSdkVersion 36 と同様の可能性。公式文書に targetSdkVersion 条件なし。 |
| Android 17 | 36 / 37 | `windowSoftInputMode=stateAlwaysVisible` を設定 | keyboard が明示要求により表示されることを確認する。 |
| Android 17 | 36 / 37 | `onCreate()` または `onConfigurationChanged()` で IME 表示を request | focus / window readiness 後に keyboard が表示されることを確認する。 |

---

# 未解決事項（Open Questions）

- Android 17 AOSP tag 上で、どの code path が previous IME visibility restoration を変更しているか。
- targetSdkVersion gate または compat Change ID が存在するか。
- `configChanges` を宣言して app が configuration change を処理する場合に、system 側でどのような restoration / suppression が行われるか。
- `stateAlwaysVisible`、`WindowInsetsController.show()`、`InputMethodManager.showSoftInput()` の推奨 timing と失敗条件。
- foldable / multi-window / hardware keyboard 接続時など、rotation 以外の configuration change で同じ扱いになるか。

---

# 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Human decision required

最終影響度（Final Severity）:
- Human decision required

顧客通知要否（Customer Communication Required）:
- Human decision required

リリース判断（Release Readiness）:
- Human decision required

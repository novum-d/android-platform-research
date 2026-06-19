# Rotation 後の default IME visibility 復元

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
- https://developer.android.com/guide/topics/manifest/activity-element#wsoft
- https://developer.android.com/reference/android/app/Activity#onCreate(android.os.Bundle)
- https://developer.android.com/reference/android/app/Activity#onConfigurationChanged(android.content.res.Configuration)
- https://developer.android.com/reference/android/view/WindowInsetsController#show(int)

セクション:
- Restoring default IME visibility after rotation

ページ種別:
- Behavior changes: all apps

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- OS_UPDATE_ALL_APPS

公式文書からの初期適用条件判断:
- 公式文書は Android 17 の `Behavior changes: all apps` ページにこの項目を掲載している。
- 原文は、Android 17 から device configuration change、たとえば rotation が発生し、それを app 自身が処理しない場合、以前の IME visibility は復元されないと説明している。
- 原文には targetSdkVersion 条件は記載されていない。
- Android 17 AOSP evidence 上も `targetSdkVersion` / compat ChangeId gate は確認できなかった。

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | Yes / 条件付き | `behavior-changes-all` 掲載項目であり、AOSP の IME restore 判断に targetSdkVersion gate は見つからない。 |
| targetSdkVersion 37 以上が必要か | No | `WindowManagerService.shouldRestoreImeVisibility()` と `ImeVisibilityStateComputer.shouldRestoreImeVisibility()` に targetSdkVersion 分岐はない。 |
| 追加の実行時条件があるか | ある | configuration change 後の Activity recreation、focused editor、IME visibility restore 判断、明示的な IME 表示要求の有無に依存する。 |
| Compat Change ID が関係するか | 確認できず | `@ChangeId` / `CompatChanges.isChangeEnabled` は該当 path で確認できなかった。実装は aconfig flag `disable_ime_restore_on_activity_create` を参照する。 |

### 調査日（Investigation Date）

2026-06-18

### 信頼度（Confidence）

- Medium

理由:
- 公式文書と Android 17 `frameworks-base` 上の実装 path は一致している。
- 実装 path に targetSdkVersion gate は見つからない。
- ただし `disable_ime_restore_on_activity_create` は `android-16.0.0_r4` にも存在し、`android-16.0.0_r4` -> `android-17.0.0_r1` の `frameworks-base` 差分だけでは flag default / release config の有効化差分を確認できない。そのため High confidence にはしない。

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [x] OS update / all apps on Android 17 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 37 on Android 17+
- [ ] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [ ] Unknown / 追加根拠が必要

必要な実行時条件（Required runtime conditions）:
- Android version: 公式文書上は Android 17 以上。
- targetSdkVersion: 条件なし。AOSP の確認済み path に targetSdkVersion gate はない。
- Device/form factor: rotation など configuration change が発生する端末状態。
- Permission/API/component condition: IME / soft keyboard、focused text field、`android:windowSoftInputMode`、`WindowInsetsController.show()`、`InputMethodManager`。
- App state/process condition: app が configuration change を自身で処理せず、Activity recreation 後に以前の IME visibility が自動復元されることを期待している場合。変更後も keyboard が必要なら app が明示的に表示要求する必要がある。

Compat framework:
- Change ID: 確認できず
- 変更名: なし
- 既定状態: compat framework では確認できず
- テスト時の切り替え可否: compat change としての切り替えは未確認。実装は aconfig flag `disable_ime_restore_on_activity_create` を参照する。

分類信頼度（Classification confidence）:
- Medium

分類根拠（Classification evidence）:
- 公式ドキュメントページ: `behavior-changes-all`
- 検証対象の適用条件文: Android 17 から、app が処理しない configuration change 後に previous IME visibility は復元されない。
- AOSP targetSdk gate: 確認した IME restore path では見つからない。
- Compat framework entry: 見つからない。
- 補足: `frameworks-base` 上では Android 16 tag にも同じ aconfig flag と `WindowManagerService` 分岐が存在するため、Android 17 での実効有効化は release flag/config 側の差分で説明される可能性がある。

---

# エグゼクティブサマリー（Executive Summary）

Android 17 では、rotation などの configuration change が発生し、その変更を app 自身が処理しない場合、変更前に表示されていた IME / soft keyboard visibility が自動復元されない、と公式文書は説明している。

Android 17 AOSP の `WindowManagerService.shouldRestoreImeVisibility()` は、`disable_ime_restore_on_activity_create` flag が有効な場合、Activity に保存された `mLastImeShown` ではなく、対象 window が明示的に IME visibility を request しているかを確認する。つまり、Activity recreation 後に「前回 IME が表示されていた」という状態だけでは復元根拠にならず、app 側の明示的な表示要求が重要になる。

確認済みの source path には targetSdkVersion gate がないため、分類は `OS_UPDATE_ALL_APPS` とする。ただし同じ flag と分岐は `android-16.0.0_r4` にも存在し、`frameworks-base` の tag diff だけでは Android 17 release での flag default 有効化を確認できないため、信頼度は Medium とする。

---

# 公式ドキュメント確認

## 原文（Statement）

Page title:
- Behavior changes: all apps

Page URL:
- https://developer.android.com/about/versions/17/behavior-changes-all

ページ種別:
- all apps

Section title:
- Restoring default IME visibility after rotation

検証対象の原文:
- Beginning with Android 17, when the device's configuration changes, for example through rotation, and this is not handled by the app itself, the previous IME visibility is not restored.
- If the app needs the keyboard to be visible after an unhandled configuration change, the app must explicitly request it.
- Mitigation options are setting `android:windowSoftInputMode` to `stateAlwaysVisible`, requesting the soft keyboard in `Activity.onCreate()`, or adding / using `onConfigurationChanged()`.

## 解釈（Interpretation）

この変更は、configuration change 後の IME visibility restoration default を変える挙動変更である。Android 17 では、app が configuration change を処理していない場合、system は previous IME visibility を自動復元しない。keyboard が必要な screen では、manifest または code で明示的に表示要求を行う。

---

# AOSP 調査（AOSP Investigation）

## checkout 状態（Checkout Status）

確認コマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list android-17.0.0_r1
```

結果:
- `frameworks-base` の `status --short` は空で、dirty working tree は確認されなかった。
- `android-16.0.0_r4` tag は存在する。
- `android-17.0.0_r1` tag は存在する。

## 関連ファイル（Related Files）

確認した主なファイル:
- `core/java/android/view/inputmethod/flags.aconfig`
- `services/core/java/com/android/server/inputmethod/ImeVisibilityStateComputer.java`
- `services/core/java/com/android/server/wm/WindowManagerInternal.java`
- `services/core/java/com/android/server/wm/WindowManagerService.java`
- `services/core/java/com/android/server/wm/ActivityRecord.java`

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `core/java/android/view/inputmethod/flags.aconfig` / `disable_ime_restore_on_activity_create` | flag 定義は存在する | flag 定義は存在する。説明は Activity recreation、たとえば rotation 後の明示 request なし IME restore を無効化するもの | Behavior Change の文言と直接一致する feature flag |
| `ImeVisibilityStateComputer.computeState()` | focused editor かつ `shouldRestoreImeVisibility(state)` が true の場合、`SHOW_RESTORE_IME_VISIBILITY` で IME 表示を復元する | 同じ caller path | IME visibility restore を実際に show decision へ変換する entry point |
| `ImeVisibilityStateComputer.shouldRestoreImeVisibility()` | `SOFT_INPUT_STATE_ALWAYS_HIDDEN`、または forward navigation 付き `SOFT_INPUT_STATE_HIDDEN` では restore しない。その後 WM に問い合わせる | 同じ condition。targetSdkVersion gate はない | `windowSoftInputMode` の hidden 系例外を反映し、WM 側 restore 判断へ接続する |
| `WindowManagerInternal.shouldRestoreImeVisibility()` | IME target window について restore 可否を WM に問い合わせる抽象 API | 同じ API | inputmethod service と window manager の境界 |
| `WindowManagerService.shouldRestoreImeVisibility()` | `disableImeRestoreOnActivityCreate()` が true の場合は `imeTargetWindow.isRequestedVisible(WindowInsets.Type.ime())` を優先し、false の場合は `ActivityRecord.mLastImeShown` を restore 根拠にする。その後 task snapshot の IME surface も確認する | 同じ構造。targetSdkVersion gate はない | previous IME visibility を復元するかどうかの中心判断。flag 有効時は明示 request がある場合だけ Activity recreate 後の restore を許す方向になる |
| `ActivityRecord.mLastImeShown` | Activity 非表示時に IME がその Activity に表示されていたかを記録する | 同じ state | flag 無効時に previous IME visibility restore の根拠になる保存状態 |

## 実装 path（Runtime Path）

想定される path:
1. rotation などの configuration change が発生する。
2. app が configuration change を自身で処理しない場合、Activity recreation が起きる。
3. 新しい window が focused editor を持つと、`ImeVisibilityStateComputer.computeState()` が IME visibility を計算する。
4. `shouldRestoreImeVisibility()` が true の場合だけ `SHOW_RESTORE_IME_VISIBILITY` として IME を表示する。
5. `WindowManagerService.shouldRestoreImeVisibility()` では、`disable_ime_restore_on_activity_create` が有効な場合、`mLastImeShown` ではなく `isRequestedVisible(WindowInsets.Type.ime())` を restore 根拠として扱う。
6. app が `stateAlwaysVisible` や `WindowInsetsController.show(WindowInsets.Type.ime())` などで明示的に要求していない場合、previous IME visibility は復元されにくくなる。

## 差分確認（Diff Review）

確認コマンド:

```bash
git -C frameworks-base diff android-16.0.0_r4 android-17.0.0_r1 -- \
  core/java/android/view/inputmethod/flags.aconfig \
  services/core/java/com/android/server/inputmethod/ImeVisibilityStateComputer.java \
  services/core/java/com/android/server/wm/WindowManagerService.java
```

確認結果:
- `disable_ime_restore_on_activity_create` flag は Android 17 tag に存在する。
- 同じ flag は `android-16.0.0_r4` にも存在する。
- `WindowManagerService.shouldRestoreImeVisibility()` の core condition も `android-16.0.0_r4` と `android-17.0.0_r1` の両方に存在する。
- 確認済み path では `targetSdkVersion`、`@ChangeId`、`CompatChanges.isChangeEnabled` は見つからない。

差分解釈:
- Source diff type: changed default / changed condition の候補。ただし `frameworks-base` の比較だけでは flag default の release 有効化差分は確認できない。
- Behavior Change を支える evidence: Android 17 tag 上の code path は、flag 有効時に previous `mLastImeShown` ではなく明示的な IME visibility request を restore 根拠にする。
- 分類を支える evidence: targetSdkVersion gate が見つからないため、公式文書の all apps 記述と合わせて `OS_UPDATE_ALL_APPS` と判断する。

## 関連しない / 除外した path

- `WindowManagerService.shouldRestoreImeVisibility()` 内の task snapshot `hasImeSurface()` は、task snapshot に IME surface が残っている場合の restore 判断であり、targetSdkVersion gate ではない。
- `SOFT_INPUT_STATE_ALWAYS_HIDDEN` と forward navigation 付き `SOFT_INPUT_STATE_HIDDEN` は既存の softInputMode 例外であり、Android 17 固有の targetSdk gate ではない。
- `InputMethodUtils.isSoftInputModeStateVisibleAllowed(int targetSdkVersion, ...)` は soft input mode state visible の別制約であり、本項目の Activity recreation 後の previous IME visibility restore 抑止 path とは分けて扱う。

---

# 適用条件（Applicability）

## OS アップデート時の挙動（OS Update Behavior）

- Android 17 に OS アップデートしただけで適用されるか: Yes / 条件付き。
- targetSdkVersion に依存しない根拠: 公式文書は all apps ページに掲載し、targetSdkVersion 条件を示していない。AOSP の確認済み path に targetSdkVersion gate はない。
- Android 16 以前での挙動: tag 上の `frameworks-base` には同じ flag と分岐が存在するため、Android 16 release での実効挙動は flag default / release config に依存する可能性がある。公式文書は Android 17 からの挙動変更として説明している。

## targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- targetSdkVersion 37 以上で適用されるか: targetSdkVersion 37 は必要条件ではない。
- Android 17 / targetSdkVersion 36: 条件を満たす場合、previous IME visibility は自動復元されない想定。
- Android 17 / targetSdkVersion 37: targetSdkVersion 36 と同じ想定。
- opt-out / temporary override の有無: 公式文書に app 向け opt-out は記載されていない。対応は明示的な IME 表示要求。

## その他の条件（Other Conditions）

- device/form factor: rotation など configuration change が発生する端末状態。
- app configuration handling: app が configuration change を自身で処理しない場合が主対象。
- UI state: text input があり、変更後も keyboard を表示しておく必要がある screen。
- API usage: `android:windowSoftInputMode`、`WindowInsetsController.show(WindowInsets.Type.ime())`、`InputMethodManager.showSoftInput()`、focus management。
- not affected / lower risk: rotation 後に keyboard 表示を必要としない screen、入力欄がない screen、app 側で configuration change と IME 表示を明示的に制御している screen。

---

# 開発者影響（Developer Impact）

影響を受ける可能性がある app:
- 検索画面、ログイン画面、チャット画面、メモ入力、業務入力フォームなど、rotation 後も keyboard 表示を継続したい screen。
- `EditText` / text field に focus がある状態で rotation し、Activity recreation 後に keyboard が自動で戻ることを期待している app。
- E2E テストや UI テストで「rotation 後も keyboard が表示されている」ことを前提にしている app。

影響が限定的な app:
- rotation 後に keyboard 表示を必要としない app。
- 入力欄がない screen。
- app 側で configuration change を処理し、必要なタイミングで明示的に IME 表示を request している app。

ユーザー影響:
- rotation 後に keyboard が閉じたままになり、ユーザーが再度 text field を tap する必要が出る。
- 入力継続が重要な画面では、手戻り感や入力中断として見える可能性がある。

---

# 推奨対応候補（Recommended Action Candidates）

開発者向け対応候補:
- rotation / configuration change 後も keyboard 表示が必要な screen を棚卸しする。
- manifest で妥当な場合は `android:windowSoftInputMode="stateAlwaysVisible"` を検討する。
- Activity recreation 後に keyboard が必要な場合は、focus 設定後に `WindowInsetsController.show(WindowInsets.Type.ime())` などで明示 request する。
- app が `configChanges` を処理する場合は、`onConfigurationChanged()` 内で focus と IME visibility の期待状態を再適用する。
- Android 17 / targetSdkVersion 36 と Android 17 / targetSdkVersion 37 の両方で、rotation 前後の focus と IME visibility を確認する。

---

# テスト観点（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 条件 | 期待挙動（Expected behavior） |
| --- | --- | --- | --- |
| Android 16 | 36 | keyboard 表示中に rotation、app は configuration change を処理しない | baseline。release flag/config により restore 挙動が異なる可能性があるため実機確認する。 |
| Android 17 | 36 | keyboard 表示中に rotation、app は configuration change を処理しない | previous IME visibility は自動復元されない想定。 |
| Android 17 | 37 | keyboard 表示中に rotation、app は configuration change を処理しない | targetSdkVersion 36 と同じ想定。 |
| Android 17 | 37 | `stateAlwaysVisible` または programmatic show を使用 | keyboard が必要な画面では明示 request により表示される想定。 |

---

# 顧客向け説明（Customer-facing Explanation）

Android 17 では、画面回転などで app が処理しない configuration change が発生した後、変更前に表示されていた keyboard は system によって自動復元されません。

rotation 後も keyboard を表示したい画面では、`android:windowSoftInputMode="stateAlwaysVisible"` を設定するか、Activity lifecycle 内で `WindowInsetsController.show(WindowInsets.Type.ime())` などを使って明示的に IME 表示を request してください。targetSdkVersion 37 への変更だけで発生する差分ではなく、Android 17 端末上で条件を満たす入力画面に影響する可能性があります。

---

# 未解決事項（Open Questions）

- Android 17 release build で `disable_ime_restore_on_activity_create` がどの release flag/config により有効化されるか。
- Android 16 release build で同 flag が無効だったことを、frameworks-base 以外の release config evidence で確認できるか。
- foldable / multi-window / hardware keyboard 接続時など、rotation 以外の configuration change で同じ扱いになるか。

---

# 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断

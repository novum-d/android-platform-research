# Rotation 後の default IME visibility 復元 - 1ページ要約

## 対象

Android 17 Behavior Change

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

## 適用条件

- 主分類（Primary classification）: OS_UPDATE_ALL_APPS
- OS アップデート / 全アプリ（OS update / all apps）: 該当。Android 17 の all apps ページに掲載され、AOSP の確認済み path に targetSdkVersion ゲートは見つからない。
- targetSdkVersion 37 以上: 不要。Android 17 / targetSdkVersion 36 と 37 で同じ扱いになる想定。
- その他の必須条件（Other required conditions）: rotation など configuration change が発生し、app がそれを自身で処理せず、previous IME visibility の自動復元を期待していること。
- Compat Change ID: 確認できず
- Compat default state: compat framework では確認できず。実装は aconfig flag `disable_ime_restore_on_activity_create` を参照する。
- Confidence: Medium

## 早見マトリクス

| シナリオ | 影響 |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 条件を満たす場合、unhandled configuration change 後に previous IME visibility は自動復元されない想定。 |
| Android 17 / targetSdkVersion 37 | targetSdkVersion 36 と同じ想定。targetSdkVersion 37 は必要条件ではない。 |
| Android 17 / targetSdkVersion 37 + 明示 IME 表示要求 | `stateAlwaysVisible` や programmatic show により、必要な画面で keyboard 表示を request できる。 |

## 要約

Android 17 では、rotation などの configuration change が発生し、その変更を app 自身が処理しない場合、以前表示されていた IME / soft keyboard は自動復元されない。rotation 後も keyboard を表示したい screen では、app が明示的に request する必要がある。

AOSP では `WindowManagerService.shouldRestoreImeVisibility()` が `disable_ime_restore_on_activity_create` flag を参照する。flag 有効時は `ActivityRecord.mLastImeShown` ではなく、対象 window が `WindowInsets.Type.ime()` の visibility を明示 request しているかを restore 根拠にする。確認済み path に targetSdkVersion ゲートはない。

## 顧客影響

- rotation 後に keyboard が閉じたままになり、ユーザーが再度 text field を tap する必要が出る可能性がある。
- 検索、ログイン、チャット、メモ入力、業務入力フォームなど、入力継続が重要な画面で影響が見える可能性がある。
- UI / E2E テストが「rotation 後も keyboard が表示されている」前提の場合、Android 17 で失敗する可能性がある。

## 影響対象（Who Is Affected）

- 対象アプリ: 入力画面で rotation 後も keyboard 表示を継続したいアプリ。
- 対象機能: 検索、ログイン、チャット、メモ入力、業務入力フォーム。
- 対象条件: keyboard 表示中に configuration change が発生し、Activity recreation 後の IME 自動復元を期待している場合。

## 対応要否

- 必須対応: rotation / configuration change 後も keyboard が必要な screen を棚卸しする。
- 推奨対応: `android:windowSoftInputMode="stateAlwaysVisible"`、`Activity.onCreate()`、または `onConfigurationChanged()` で明示的に IME 表示を request する。
- 不要: rotation 後に keyboard 表示が不要な screen、入力欄がない screen、すでに focus / IME visibility を明示制御している screen では直接影響は限定的。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 36 | baseline。release flag/config により restore 挙動が異なる可能性があるため実機確認する。 |
| Android 17 | 36 | previous IME visibility は自動復元されない想定。 |
| Android 17 | 37 | targetSdkVersion 36 と同じ期待。targetSdkVersion 条件は確認されていない。 |

## 顧客向け説明

Android 17 では、画面回転などで app が処理しない configuration change が発生した後、変更前に表示されていた keyboard は system によって自動復元されません。

rotation 後も keyboard を表示したい場合は、`android:windowSoftInputMode="stateAlwaysVisible"` を設定するか、`Activity.onCreate()` または `onConfigurationChanged()` で明示的に IME 表示を request してください。

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-all
- 検証対象の原文: Android 17 から、app が処理しない configuration change 後に previous IME visibility は復元されない。
- AOSP ファイル: `core/java/android/view/inputmethod/flags.aconfig`, `services/core/java/com/android/server/inputmethod/ImeVisibilityStateComputer.java`, `services/core/java/com/android/server/wm/WindowManagerService.java`, `services/core/java/com/android/server/wm/ActivityRecord.java`
- AOSP ソース文脈: `ImeVisibilityStateComputer.computeState()` が restore 判断を show decision へ変換し、`WindowManagerService.shouldRestoreImeVisibility()` が `disableImeRestoreOnActivityCreate()` 有効時に明示的な IME visibility request を restore 根拠にする。
- 差分解釈: changed default / changed condition の候補。ただし同 flag と分岐は `android-16.0.0_r4` にも存在し、`frameworks-base` だけでは release flag/config の有効化差分を確認できない。
- ゲート結論: targetSdkVersion ゲートと compat ChangeId は確認できない。分類は `OS_UPDATE_ALL_APPS`、confidence は Medium。

## 人間の判断欄

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断

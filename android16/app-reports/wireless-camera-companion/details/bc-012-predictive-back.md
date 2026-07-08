# BC-012: Predictive back default enabled

## 基本情報

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/16/behavior-changes-16#predictive-back
- Section: Migration or opt-out required for predictive back

既存調査:
- [android16/behavior-changes/target/user-experience-and-system-ui/migration-or-opt-out-required-for-predictive-back.md](../../../behavior-changes/target/user-experience-and-system-ui/migration-or-opt-out-required-for-predictive-back.md)
- [android16/summaries/target/user-experience-and-system-ui/migration-or-opt-out-required-for-predictive-back-summary.md](../../../summaries/target/user-experience-and-system-ui/migration-or-opt-out-required-for-predictive-back-summary.md)

## 対象アプリとの関係

関連するアプリ機能:
- camera setup wizard。
- pairing / connection flow。
- image viewer。
- transfer cancel / unsaved operation confirmation。
- custom back handling。

アプリが該当する可能性:
- Conditional。legacy `onBackPressed()` / `KEYCODE_BACK` / custom intercept に依存する場合に該当。

## 適用条件分類

主分類:
- `TARGET_SDK_36_CONDITIONAL`

必要条件:
- Android 16。
- targetSdkVersion 36 以上。
- legacy back handling 依存。

Confidence:
- High。

## AOSP / 公式根拠

既存 Android16 調査で確認済み:
- package parsing で `targetSdk > VANILLA_ICE_CREAM` の場合 `enableOnBackInvokedCallback` default true。
- window dispatcher / input stage が back event を `OnBackInvokedCallback` path に切り替える。
- public compat Change ID は見つからない。

## アプリ影響

想定される影響:
- `onBackPressed()` / `KEYCODE_BACK` が呼ばれない。
- connection flow / pairing flow / transfer cancel の確認 UI が出ない可能性。
- custom image viewer の back navigation が broken になる可能性。

推奨対応:
- AndroidX Activity / Navigation / Compose BackHandler の対応版へ移行する。
- `OnBackInvokedCallback` path を確認する。
- temporary opt-out は対象 Activity に限定する。
- 実装例は [Predictive back implementation examples](../../../behavior-changes/target/user-experience-and-system-ui/migration-or-opt-out-required-for-predictive-back-implementation-examples.md) を参照する。

代表例:

```kotlin
onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
    override fun handleOnBackPressed() {
        if (viewModel.hasUnsavedChanges) {
            showDiscardConfirmDialog()
            return
        }

        isEnabled = false
        onBackPressedDispatcher.onBackPressed()
    }
})
```

## テスト観点

- Android 16 / targetSdkVersion 35。
- Android 16 / targetSdkVersion 36。
- setup wizard。
- connection retry。
- image viewer。
- unsaved transfer / cancel confirmation。
- gesture navigation / 3-button navigation。

## Human Decision

- Final priority: TBD by human
- Release readiness impact: TBD by human

# BC-006: Safer Intents

## 基本情報

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/16/behavior-changes-16#safer-intents
- Section: Safer Intents

既存調査:
- [android16/behavior-changes/target/security/safer-intents.md](../../../behavior-changes/target/security/safer-intents.md)
- [android16/summaries/target/security/safer-intents-summary.md](../../../summaries/target/security/safer-intents-summary.md)

## 対象アプリとの関係

関連するアプリ機能:
- external app / SDK から起動される Activity。
- share / file open / image import。
- receiver / service 連携。
- old app から new app への explicit Intent。

アプリが該当する可能性:
- Conditional。`android:intentMatchingFlags` で strict intent filter matching に opt-in する場合に該当。

## 適用条件分類

主分類:
- `TARGET_SDK_36_CONDITIONAL`

補足:
- 既存調査では AOSP enforcement path に明確な targetSdkVersion 36 gate は確認できず、実装上の直接条件は manifest opt-in / feature flag / cross-app intent。
- 実務上は Android 16 SDK で public attr として使うため targetSdkVersion 36 移行時に確認する。

Confidence:
- Medium。

## AOSP / 公式根拠

既存 Android16 調査で確認済み:
- `android:intentMatchingFlags`
- `enforceIntentFilter`
- `allowNullAction`
- same-app skip。
- system/root caller skip。
- target component の intent filter mismatch で block。

## アプリ影響

想定される影響:
- opt-in した component に、intent filter と合わない explicit Intent が届かなくなる。
- action なし Intent は `allowNullAction` がなければ match しない。
- 外部 SDK / 古いアプリからの explicit launch が filter mismatch になる可能性。

推奨対応:
- opt-in 前に external entry point の action / data / categories を棚卸しする。
- intent filter を正確に定義する。
- old app / SDK / partner app との連携テストを行う。

## テスト観点

- same-app explicit Intent。
- cross-app explicit Intent。
- action null Intent。
- `enforceIntentFilter` / `allowNullAction` / `none`。
- activity / receiver / service。

## Human Decision

- Final priority: TBD by human
- Release readiness impact: TBD by human

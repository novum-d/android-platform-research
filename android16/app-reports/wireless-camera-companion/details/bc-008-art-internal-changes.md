# BC-008: ART internal changes

## 基本情報

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/16/behavior-changes-all#art-changes
- Section: ART internal changes

既存調査:
- [android16/behavior-changes/all/core-functionality/art-internal-changes.md](../../../behavior-changes/all/core-functionality/art-internal-changes.md)
- [android16/summaries/all/core-functionality/art-internal-changes-summary.md](../../../summaries/all/core-functionality/art-internal-changes-summary.md)

## 対象アプリとの関係

関連するアプリ機能:
- third-party SDK。
- crash reporting / profiling / monitoring。
- obfuscation / anti-tamper / hotfix。
- plugin / dynamic loading。
- JNI runtime assumptions。

アプリが該当する可能性:
- Conditional。public API のみなら低リスク。runtime internals 依存 SDK がある場合は高リスク。

## 適用条件分類

主分類:
- `MAINLINE_OR_PLAY_SYSTEM_UPDATE`

OS update と targetSdkVersion:
- Android 16 OS update で updated ART が入る。
- Android 12+ の ART Mainline update でも影響し得る。
- targetSdkVersion 36 は主要 gate ではない。

Confidence:
- High。

## AOSP / 公式根拠

既存 Android16 調査で確認済み:
- ART module / APEX boundary。
- hidden API / non-SDK interface risk。
- known issues: HiddenApiBypass / FlyCore before specific version。
- targetSdkVersion 36 gate なし。

## アプリ影響

想定される影響:
- hidden API / ART internals 依存 SDK の crash。
- JNI method / field lookup failure。
- instrumentation / hotfix / hooking SDK 初期化失敗。
- Android 16 以外の ART module update device でも再現する可能性。

推奨対応:
- SDK / library の ART internal usage を棚卸しする。
- known issue library version を確認する。
- public API alternative へ移行する。
- ART APEX / module version を test record に残す。

## テスト観点

- Android 16 / targetSdkVersion 35。
- Android 16 / targetSdkVersion 36。
- Android 12+ / updated ART module。
- app startup / class loading。
- reflection / hidden API warning。
- JNI failure / native crash。
- SDK initialization。

## Human Decision

- Final priority: TBD by human
- Release readiness impact: TBD by human

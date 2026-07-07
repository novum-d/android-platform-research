# BC-004: Companion apps no longer notified of discovery timeouts

## 基本情報

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/16/behavior-changes-all#companion-device-timeout
- Section: Companion apps no longer notified of discovery timeouts

既存調査:
- [android16/behavior-changes/all/security/companion-apps-no-longer-notified-of-discovery-timeouts.md](../../../behavior-changes/all/security/companion-apps-no-longer-notified-of-discovery-timeouts.md)
- [android16/summaries/all/security/companion-apps-no-longer-notified-of-discovery-timeouts-summary.md](../../../summaries/all/security/companion-apps-no-longer-notified-of-discovery-timeouts-summary.md)

## 対象アプリとの関係

関連するアプリ機能:
- CompanionDeviceManager によるカメラ pairing / association。
- 初回 onboarding。
- BLE / Bluetooth / Wi-Fi filter discovery。
- timeout / retry / analytics。

アプリが該当する可能性:
- Conditional。CDM association flow を使う場合に該当。

## 適用条件分類

主分類:
- `OS_UPDATE_ALL_APPS`

OS update と targetSdkVersion:
- Android 16 OS 上の CDM discovery flow に影響し得る。
- targetSdkVersion 36 は必要条件ではない。

Confidence:
- High。

## AOSP / 公式根拠

既存 Android16 調査で確認済み:
- Android 15: 20 秒 timeout direct `RESULT_DISCOVERY_TIMEOUT` path。
- Android 16: soft timeout message UI / hard timeout / user cancel path。
- app には `RESULT_USER_REJECTED` が返る。
- 20 秒以内に device が 1 件以上見つかると追加探索を停止。

## アプリ影響

想定される影響:
- `RESULT_DISCOVERY_TIMEOUT` に基づく retry / UI / analytics が動かない。
- `RESULT_USER_REJECTED` が user cancellation と timeout dialog dismissal の両方を含み得る。
- app 独自 timeout UI と system timeout message が重複する可能性。

推奨対応:
- CDM flow の result handling を見直す。
- `RESULT_USER_REJECTED` を generic association failure として扱い、retry 導線を出す。
- analytics では Android 16 の timeout dialog dismissal を別扱いできるか確認する。

## テスト観点

- no device discovered。
- one or more devices discovered within first 20 seconds。
- user dismisses timeout dialog。
- user manually stops discovery。
- app custom timeout UI。

## Human Decision

- Final priority: TBD by human
- Release readiness impact: TBD by human

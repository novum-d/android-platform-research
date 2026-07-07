# Companion apps no longer notified of discovery timeouts - 1ページ要約（One Page Summary）

## 対象（Target）

Android 16 Behavior Change

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Behavior Change:
- Companion apps no longer notified of discovery timeouts

Official documentation:
- https://developer.android.com/about/versions/16/behavior-changes-all#companion-device-timeout

Category:
- Security

## 適用条件（Applicability）

- 主分類（Primary classification）: `OS_UPDATE_ALL_APPS`
- OS アップデート / 全アプリ（OS update / all apps）: Yes / Conditional。Android 16 上で CDM association discovery flow を使う app に影響し得る。
- targetSdkVersion 36 以上: No。targetSdkVersion 36 は必要条件ではない。
- その他の必須条件（Other required conditions）: `CompanionDeviceManager#associate()` / `AssociationRequest` による companion device discovery flow を使い、discovery timeout / user cancellation / retry / analytics に依存すること。
- Compat Change ID: 見つからない。
- Compat default state: N/A

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 16 / targetSdkVersion 35 | CDM timeout direct callback は `RESULT_DISCOVERY_TIMEOUT` ではなく、system UI dismissal 後の `RESULT_USER_REJECTED` になる |
| Android 16 / targetSdkVersion 36 | targetSdkVersion 35 と同様。targetSdkVersion 36 固有ではない |
| Android 15 / targetSdkVersion 36 | Android 15 baseline では 20 秒 timeout direct `RESULT_DISCOVERY_TIMEOUT` path がある |
| CDM pairing flow 不使用 | 今回の変更は基本的に影響しない |
| 20 秒以内に device が 0 件 | Android 16 は soft timeout message を表示し、探索継続 |
| 20 秒以内に device が 1 件以上 | Android 16 は追加探索を停止 |
| user dismiss / manual stop | app は `RESULT_USER_REJECTED` を受ける |

## 要約（Summary）

Android 16 では、Companion Device Manager の discovery timeout が app に `RESULT_DISCOVERY_TIMEOUT` として直接返らない。CDM の system UI が timeout message を表示し、ユーザーが閉じると app には `RESULT_USER_REJECTED` が返る。

AOSP では Android 15 の 20 秒 timeout direct result path が削除され、Android 16 で 20 秒 soft timeout / 5 分 hard timeout / timeout message UI に変更されている。

## 顧客影響（Customer Impact）

- 影響あり: CDM pairing flow で `RESULT_DISCOVERY_TIMEOUT` を retry / UI / analytics / support log に使うアプリ。
- 影響軽微: CDM を使わないアプリ、または `RESULT_USER_REJECTED` を generic failure として graceful に扱えるアプリ。
- 要確認: app 独自 timeout UI と CDM system timeout message が重複しないか。

## 影響対象（Who Is Affected）

- `CompanionDeviceManager` / `AssociationRequest` を使うアプリ。
- wearable / earbuds / health device / IoT / camera / tracker / automotive accessory を CDM で pairing するアプリ。
- `RESULT_DISCOVERY_TIMEOUT` に依存するアプリ。
- `RESULT_USER_REJECTED` を純粋な user cancellation として扱うアプリ。
- pairing timeout / retry / fallback UI / onboarding analytics を持つアプリ。

## 対応要否（Required Action）

- 必須対応: `RESULT_DISCOVERY_TIMEOUT` だけで timeout retry / UI を分岐している場合は Android 16 動作確認と修正候補。
- 推奨対応: `RESULT_USER_REJECTED` を timeout dialog dismissal と user cancellation の両方を含み得る generic association failure として扱い、retry 導線を安全に出す。
- 不要: CDM pairing flow を使っていない場合。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 15 | 35 | 20 秒 timeout で `RESULT_DISCOVERY_TIMEOUT` が返る baseline |
| Android 16 | 35 | timeout message 表示後、dismiss / cancel で `RESULT_USER_REJECTED` |
| Android 16 | 36 | targetSdkVersion 35 と同様 |
| Android 15 | 36 | 技術的に検証可能なら比較。Android 16 OS update impact と混同しない |

追加テスト:
- no device discovered
- one or more devices discovered within first 20 seconds
- multiple devices discovered after first 20 seconds
- user dismisses timeout dialog
- user manually stops discovery
- BLE / Bluetooth classic / Wi-Fi filters
- app custom timeout UI
- analytics mapping before / after

## 顧客向け説明（Explanation for Customers）

この変更は targetSdkVersion 36 化だけで発生するものではなく、Android 16 OS 上で CDM の companion device pairing flow を使う場合に影響します。Android 16 では discovery timeout が app に直接 `RESULT_DISCOVERY_TIMEOUT` として返らず、system UI が timeout を表示した後、ユーザーが flow を閉じると app には `RESULT_USER_REJECTED` が返ります。

そのため、`RESULT_DISCOVERY_TIMEOUT` を retry、analytics、customer support reason に使っている場合は、Android 16 で timeout が user rejection として見える可能性を前提に動作確認してください。

## 根拠（Evidence）

- Official documentation: Android 16 all apps / Security / Companion apps no longer notified of discovery timeouts
- AOSP files:
  - `core/java/android/companion/CompanionDeviceManager.java`
  - `core/api/current.txt`
  - `packages/CompanionDeviceManager/src/com/android/companiondevicemanager/CompanionAssociationActivity.java`
  - `packages/CompanionDeviceManager/src/com/android/companiondevicemanager/CompanionDeviceDiscoveryService.java`
  - `packages/CompanionDeviceManager/res/layout/activity_confirmation.xml`
  - `packages/CompanionDeviceManager/res/values/strings.xml`
- AOSP source context:
  - Android 15: `FINISHED_TIMEOUT` -> `cancel(RESULT_DISCOVERY_TIMEOUT, null)`
  - Android 16: `IN_PROGRESS_EXTENDED` / `FINISHED_STOPPED` -> timeout message UI -> user cancel path `RESULT_USER_REJECTED`
- Diff interpretation:
  - removed behavior: direct `RESULT_DISCOVERY_TIMEOUT` timeout callback path
  - added behavior: soft / hard timeout and visual timeout message
  - changed condition: 20 秒時点で device 0 件なら探索継続、1 件以上なら追加探索停止
- Gate conclusion:
  - Android 16 OS 上、CDM discovery flow を使う全アプリに targetSdkVersion と無関係に影響し得る。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Critical / High / Medium / Low

判断（Decision）:
- Explain / Monitor / Ignore / Further investigation required

顧客説明優先度（Customer communication priority）:
- TBD by human

リリース判定（Release readiness decision）:
- TBD by human

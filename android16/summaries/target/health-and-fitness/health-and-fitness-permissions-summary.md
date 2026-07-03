# Health and fitness permissions - 1ページ要約（One Page Summary）

## 対象（Target）

Android 16 Behavior Change

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:
- `android16/AGENTS.md` の既定 scope は `android-16.0.0_r1` だが、この調査では依頼に従い `android-16.0.0_r4` を使用した。

## 適用条件（Applicability）

- 主分類（Primary classification）: `TARGET_SDK_36_CONDITIONAL`
- OS アップデート / 全アプリ（OS update / all apps）: No。Android 16 へ OS アップデートしただけで targetSdkVersion 35 以下の全アプリに同じ強制が既定適用されるとは判断しない。
- targetSdkVersion 36 以上: Yes。`Sensor.TYPE_HEART_RATE` doc は SDK < 36 と SDK >= 36 で必要 permission を分ける。
- 影響条件: `BODY_SENSORS` / `BODY_SENSORS_BACKGROUND` 前提で heart rate / SpO2 / skin temperature / background health data / health FGS / Health Connect read permission を扱う。
- Compat Change ID: health permission 専用の compat framework Change ID は見つからない。
- AOSP flag: `replace_body_sensor_permission_enabled` は fixed read-only aconfig flag。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ | 期待挙動 |
| --- | --- |
| Android 16 / targetSdkVersion 35 | legacy app として BODY_SENSORS 系との同期・互換が働く |
| Android 16 / targetSdkVersion 36 / `BODY_SENSORS` only | Android 16 target の heart rate requirement を満たさない |
| Android 16 / targetSdkVersion 36 / `BODY_SENSORS_BACKGROUND` only | background health access requirement を満たさない |
| Android 16 / targetSdkVersion 36 / `READ_HEART_RATE` declared | while-in-use heart rate access の候補 permission |
| Android 16 / targetSdkVersion 36 / `READ_HEALTH_DATA_IN_BACKGROUND` declared | background health data access の候補 permission |
| Android 16 / targetSdkVersion 36 / `Sensor.TYPE_HEART_RATE` | SDK >= 36 では `READ_HEART_RATE` が必要 |
| Android 16 / targetSdkVersion 36 / `FOREGROUND_SERVICE_TYPE_HEALTH` | `FOREGROUND_SERVICE_HEALTH` + allowed health/activity/sensor permission が必要 |
| Android 16 / targetSdkVersion 36 / privacy policy activity missing | health permissions が revoke され得る |
| Android 15 / targetSdkVersion 36 | Android 16 と同一とは結論しない |

## 要約（Summary）

Android 16 / targetSdkVersion 36 以上では、`BODY_SENSORS` / `BODY_SENSORS_BACKGROUND` 前提の health / body sensor access が、granular `android.permission.health.*` permission へ移行する。
`Sensor.TYPE_HEART_RATE` は SDK >= 36 で `READ_HEART_RATE` を要求する。
background access には `READ_HEALTH_DATA_IN_BACKGROUND`、SpO2 には `READ_OXYGEN_SATURATION`、skin temperature には `READ_SKIN_TEMPERATURE` を確認する。

## 顧客影響（Customer Impact）

- 要確認

理由:
- `BODY_SENSORS` を宣言しているだけでは Android 16 target の対象 API requirement を満たさない。
- mobile app は Health Connect health permission grant のため privacy policy / rationale activity が必要。
- Wear OS Health Services / ProtoLayout は公式文書上対象だが、Wear / Jetpack 側で追加検証が必要。

## 影響対象（Who Is Affected）

- `BODY_SENSORS` を宣言しているアプリ。
- `BODY_SENSORS_BACKGROUND` を宣言しているアプリ。
- `Sensor.TYPE_HEART_RATE` を使うアプリ。
- foreground service type health を使うアプリ。
- background health / sensor monitoring を行うアプリ。
- Heart Rate / SpO2 / Skin Temperature を while-in-use で読むアプリ。
- Health Connect と platform sensor permissions の両方を扱うアプリ。
- Wear OS Health Services を使うアプリ。
- ProtoLayout の `heartRateAccuracy` / `heartRateBpm` を使う Wear OS アプリ。
- mobile app で privacy policy activity / rationale を未実装のアプリ。
- permission migration 済みアプリ。

## 対応要否（Required Action）

- 必須対応: targetSdkVersion 36 化する app で `BODY_SENSORS` / `BODY_SENSORS_BACKGROUND` 前提の API を使う場合。
- 推奨対応: data type ごとの granular permission に manifest / runtime request を移行する。
- mobile app: `ACTION_VIEW_PERMISSION_USAGE` + `CATEGORY_HEALTH_PERMISSIONS` に対応する privacy policy / rationale activity を宣言する。
- Wear OS: Health Services / ProtoLayout は Wear 実機または emulator と該当 SDK version で検証する。

## テストマトリクス（Test Matrix）

| 端末 OS | targetSdkVersion | 条件 | 期待挙動 / 確認点 |
| --- | --- | --- | --- |
| Android 15 | 35 | baseline | 従来挙動 |
| Android 16 | 35 | OS update only | legacy sync / compatibility を確認 |
| Android 16 | 36 | `BODY_SENSORS` only | heart rate access が失敗しないか確認 |
| Android 16 | 36 | `READ_HEART_RATE` | `Sensor.TYPE_HEART_RATE` access を確認 |
| Android 16 | 36 | `BODY_SENSORS_BACKGROUND` only | background access が失敗しないか確認 |
| Android 16 | 36 | `READ_HEALTH_DATA_IN_BACKGROUND` | background access を確認 |
| Android 16 | 36 | health FGS | `FOREGROUND_SERVICE_HEALTH` + allowed permission を確認 |
| Android 16 | 36 | privacy policy activity missing | permission revoke を確認 |

追加テスト:
- Android 15 / targetSdkVersion 36 が検証可能な場合の比較。
- Heart Rate / SpO2 / Skin Temperature の while-in-use permission request。
- permission grant / denial / revoke flow。
- Health Connect permission UI / platform permission UI の表示差。
- Wear OS Health Services / ProtoLayout 該当 API。
- permission migration 後の既存ユーザー upgrade path。

## 顧客向け説明（Explanation for Customers）

Android 16 へ OS アップデートしただけの targetSdkVersion 35 アプリと、targetSdkVersion 36 化したアプリを混ぜて説明しません。
targetSdkVersion 36 以上では、`BODY_SENSORS` / `BODY_SENSORS_BACKGROUND` ではなく、`READ_HEART_RATE`、`READ_OXYGEN_SATURATION`、`READ_SKIN_TEMPERATURE`、`READ_HEALTH_DATA_IN_BACKGROUND` などの granular health permission に移行してください。
mobile app は privacy policy / rationale activity 未実装だと health permissions が revoke されるリスクがあります。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/16/behavior-changes-16#health-fitness-permissions
- AOSP files: `Sensor.java`、`ServiceInfo.java`、`ForegroundServiceTypePolicy.java`、`AppOpsManager.java`、`AppIdPermissionUpgrade.kt`、`AppIdPermissionPolicy.kt`。
- HealthFitness files: `HealthPermissions.java`、`HealthPermissionsManifest.xml`、`HealthConnectPermissionHelper.java`、`PermissionPackageChangesOrchestrator.java`。
- Diff interpretation: Android 16 tag で `Sensor.TYPE_HEART_RATE` doc と FGS health policy が granular permission へ変化。legacy app 向け permission state sync が追加。
- Gate conclusion: Android 16 以上 + targetSdkVersion 36 以上 + 対象 health / sensor API 利用。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 未判断

判断（Decision）:
- 未判断

Owner notes:
- 最終優先度、severity、release readiness、顧客 communication priority は repository owner が判断する。

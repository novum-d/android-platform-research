# Mobile apps - 1ページ要約（One Page Summary）

## 対象（Target）

Android 16 Behavior Change

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:

## 適用条件（Applicability）

- 主分類（Primary classification）: `TARGET_SDK_36_CONDITIONAL`
- OS アップデート / 全アプリ（OS update / all apps）: No。Android 16 へ OS アップデートしただけで targetSdkVersion 35 以下の全アプリに同じ強制が既定適用されるとは判断しない。
- targetSdkVersion 36 以上: Yes。親項目の granular health permission migration が前提。
- 追加条件: mobile app、granular `android.permission.health.*` permissions の明示 request、privacy policy / rationale activity の有無。
- Compat Change ID: health permission / mobile rationale 専用の compat framework Change ID は見つからない。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ | 期待挙動 |
| --- | --- |
| Android 16 / targetSdkVersion 35 | legacy / split permission migration として扱われ得る |
| Android 16 / targetSdkVersion 36 / mobile app / `READ_HEART_RATE` / privacy policy activity declared | health permission grant / 維持が可能 |
| Android 16 / targetSdkVersion 36 / mobile app / `READ_HEART_RATE` / privacy policy activity missing | grant されない、または revoke され得る |
| Android 16 / targetSdkVersion 36 / mobile app / `READ_HEALTH_DATA_IN_BACKGROUND` / activity declared | background health permission flow の前提を満たす |
| Android 16 / targetSdkVersion 36 / mobile app / `READ_HEALTH_DATA_IN_BACKGROUND` / activity missing | grant されない、または revoke され得る |
| Android 16 / targetSdkVersion 36 / mobile app / `BODY_SENSORS` only | parent permission migration の target behavior を満たさない |
| Android 16 / targetSdkVersion 36 / permission initially granted then activity removed | package change handling で health permissions revoke |
| Android 16 / targetSdkVersion 36 / Wear OS app | AOSP evidence 上 rationale intent は Wear device では required ではない |

## 要約（Summary）

`Mobile apps` は、Android 16 の health permission migration に伴う追加要件を扱う節である。
mobile app が `READ_HEART_RATE` などの granular health permissions へ移行する場合、Health Connect と同じく privacy policy / rationale activity を宣言する必要がある。
AOSP HealthFitness module は `ACTION_VIEW_PERMISSION_USAGE` + `CATEGORY_HEALTH_PERMISSIONS` の activity support を確認し、support がない場合に health permissions を revoke する経路を持つ。

## 顧客影響（Customer Impact）

- 要確認

理由:
- permission 名を `BODY_SENSORS` から `READ_HEART_RATE` へ置き換えるだけでは不十分。
- mobile app では privacy policy / rationale activity が grant 維持の条件になる。
- activity が app update で消えた場合も revoke され得る。

## 影響対象（Who Is Affected）

- mobile app で `READ_HEART_RATE` を要求するアプリ。
- mobile app で `READ_HEALTH_DATA_IN_BACKGROUND` を要求するアプリ。
- mobile app でその他 `android.permission.health.*` granular permissions を要求するアプリ。
- `BODY_SENSORS` から granular permissions へ移行中のアプリ。
- privacy policy activity / rationale を未宣言の mobile app。
- Health Connect permission flow を使う mobile app。
- `Sensor.TYPE_HEART_RATE` / `FOREGROUND_SERVICE_TYPE_HEALTH` を使う mobile app。
- Wear OS Health Services を使う app。

## 対応要否（Required Action）

- 必須対応: targetSdkVersion 36 化し、mobile app で granular health permission を明示 request する場合。
- manifest に `Intent.ACTION_VIEW_PERMISSION_USAGE` + `HealthConnectManager.CATEGORY_HEALTH_PERMISSIONS` に対応する activity を追加する。
- app update 後も activity が enabled / resolvable であることを確認する。
- `BODY_SENSORS` から granular permission への移行テストと、Health Connect permission UI のテストを分けて行う。

## テストマトリクス（Test Matrix）

| 端末 OS | targetSdkVersion | 条件 | 期待挙動 / 確認点 |
| --- | --- | --- | --- |
| Android 15 | 35 | baseline | 従来挙動 |
| Android 16 | 35 | OS update only | legacy / split permission migration を確認 |
| Android 16 | 36 | `READ_HEART_RATE` + activity declared | grant / access を確認 |
| Android 16 | 36 | `READ_HEART_RATE` + activity missing | denial / revoke を確認 |
| Android 16 | 36 | `READ_HEALTH_DATA_IN_BACKGROUND` + activity declared | background permission flow を確認 |
| Android 16 | 36 | `READ_HEALTH_DATA_IN_BACKGROUND` + activity missing | denial / revoke を確認 |
| Android 16 | 36 | granted 後に activity removed | package update 後の revoke を確認 |
| Android 16 | 36 | Wear OS app | mobile requirement と分けて検証 |

追加テスト:
- Android 15 / targetSdkVersion 36 が検証可能な場合の比較。
- activity declared / missing / disabled / not exported の違い。
- Health Connect permission UI / platform permission UI の表示差。
- `Sensor.TYPE_HEART_RATE` access。
- foreground service type health 起動。
- background sensor access。
- existing user upgrade path。

## 顧客向け説明（Explanation for Customers）

Android 16 へ OS アップデートしただけの targetSdkVersion 35 アプリと、targetSdkVersion 36 化したアプリを混ぜて説明しません。
targetSdkVersion 36 以上の mobile app で `READ_HEART_RATE` などへ移行する場合、permission 名の変更に加えて privacy policy / rationale activity の宣言が必要です。
宣言がない、または app update で利用できなくなると、health permissions が revoke される可能性があります。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/16/behavior-changes-16#mobile
- AOSP files: `Sensor.java`、`ServiceInfo.java`、`ForegroundServiceTypePolicy.java`、`AppIdPermissionUpgrade.kt`、`AppIdPermissionPolicy.kt`。
- HealthFitness files: `HealthPermissions.java`、`HealthPermissionIntentAppsTracker.java`、`HealthConnectPermissionHelper.java`、`PermissionPackageChangesOrchestrator.java`。
- Source context: manifest activity intent support -> HealthPermissionIntentAppsTracker -> HealthConnectPermissionHelper -> revokeAllHealthPermissions。
- Gate conclusion: Android 16 以上 + targetSdkVersion 36 以上 + mobile app + explicit granular health permission request + rationale activity requirement。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 未判断

判断（Decision）:
- 未判断

Owner notes:
- 最終優先度、severity、release readiness、顧客 communication priority は repository owner が判断する。

## 再検証記録（2026-08-22）

- Android 16 の公式 Behavior Change 一覧と最新通常AOSPタグを再確認した。
- 対応する[主レポート](../../../behavior-changes/target/health-and-fitness/mobile-apps-health-fitness-permissions.md)で official section、AOSP project / remote / checkout、解決済み commit、比較 command、dirty risk を再検証した。
- 主レポートの分類、confidence、未確認事項を維持し、実機未実施の項目を Observed 済みへ変更していない。
- 全件の結果は[再検証台帳](../../../analysis/REVALIDATION_2026-08-22.md)を参照する。

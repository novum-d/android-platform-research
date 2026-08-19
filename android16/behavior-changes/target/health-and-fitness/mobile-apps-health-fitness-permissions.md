# Mobile apps 調査レポート

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:
- `frameworks-base` checkout は clean。指定 tag `android-15.0.0_r36` / `android-16.0.0_r4` はどちらも存在する。
- AOSP evidence は `frameworks-base` local checkout と、`tmp/aosp-checkouts/HealthFitness` に shallow clone した `platform/packages/modules/HealthFitness` の `android-16.0.0_r4` tag を参照した。

### Behavior Change 文書（Behavior Change Source）

Document:
- https://developer.android.com/about/versions/16/behavior-changes-16#mobile

Section:
- Mobile apps

Parent section:
- Health and fitness permissions

Category:
- Health and fitness

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `TARGET_SDK_36_CONDITIONAL`

補足:
- この項目は `BODY_SENSORS` から granular health permission へ移行する base behavior そのものではなく、mobile apps が granular health permission を使う場合の privacy policy / rationale activity requirement を扱う。
- 依頼時の初期仮説は `TARGET_SDK_36_CONDITIONAL_WITH_ADDITIONAL_MANIFEST_REQUIREMENT` だが、`android16/behavior-changes/APPLICABILITY_CLASSIFICATION.md` の既定 label としては `TARGET_SDK_36_CONDITIONAL` を使い、additional manifest / intent requirement を本文で明示する。

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 16 へ OS アップデートしただけで targetSdkVersion 35 以下の全アプリに適用されるか | No | 親項目は Android 16 / API 36 以上 target が前提。legacy app 向け permission sync がある |
| targetSdkVersion 36 以上が必要か | Yes | 親項目の granular permission migration と同じ gate |
| mobile app の追加要件か | Yes | HealthFitness は phone では rationale intent enforcement を行い、Wear では不要と分岐 |
| privacy policy / rationale activity の検出方法 | `ACTION_VIEW_PERMISSION_USAGE` + `HealthConnectManager.CATEGORY_HEALTH_PERMISSIONS` | `HealthPermissionIntentAppsTracker` が該当 intent を作成して PackageManager で確認 |
| missing 時の挙動 | health permissions revoke | `PermissionPackageChangesOrchestrator` が intent support removed / missing 時に `revokeAllHealthPermissions()` を呼ぶ |
| Health Connect と同じ要件か | Yes | `HealthPermissions` class comment が read/write health data permission grant の前提として同じ intent support を要求 |
| Wear OS app と分離できるか | Partially yes | `HealthConnectPermissionHelper` は `FEATURE_WATCH` なら rationale intent は required ではないと返す |
| Compat framework Change ID | Not found | 公式 compat framework changes に health permission / mobile rationale 専用 Change ID は見つからない |

### 調査日（Investigation Date）

2026-07-03

### 信頼度（Confidence）

- High for mobile privacy policy / rationale activity requirement and revoke path.
- Medium for Wear OS Health Services / ProtoLayout details.

理由:
- 公式文書、HealthFitness `HealthPermissions`、`HealthPermissionIntentAppsTracker`、`HealthConnectPermissionHelper`、`PermissionPackageChangesOrchestrator` が同じ requirement と revoke path を示している。
- Wear OS Health Services / ProtoLayout は公式文書上の対象だが、実装詳細は Wear / Jetpack 側に属するため、AOSP evidence としては mobile rationale enforcement から Wear が除外される点までを確認範囲にする。

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] OS update / all apps on Android 16 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 36 on Android 16+
- [x] targetSdkVersion >= 36, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [ ] Unknown / needs more evidence

必要な実行時条件（Required runtime conditions）:
- Android version: Android 16 以上。
- targetSdkVersion: 36 以上。
- App type: mobile app。AOSP evidence 上、Wear device は rationale intent requirement から除外される。
- App behavior: `READ_HEART_RATE`、`READ_HEALTH_DATA_IN_BACKGROUND`、その他 `android.permission.health.*` granular permission を明示 request する。
- Manifest / component: `Intent.ACTION_VIEW_PERMISSION_USAGE` と `HealthConnectManager.CATEGORY_HEALTH_PERMISSIONS` に対応する activity を提供する。

Compat framework:
- Mobile apps / health rationale 専用の compat framework Change ID は公式 compat framework changes では確認できなかった。
- 親項目の permission migration には `replace_body_sensor_permission_enabled` aconfig flag があるが、`is_fixed_read_only: true` であり app compat toggle ではない。

---

# エグゼクティブサマリー（Executive Summary）

Android 16 / targetSdkVersion 36 以上で mobile app が `READ_HEART_RATE` などの granular `android.permission.health.*` permission へ移行する場合、permission 名を置き換えるだけでは不十分である。Health Connect と同じく、アプリの privacy policy / rationale を表示する activity を宣言する必要がある。

AOSP HealthFitness module では、`HealthPermissions` の class comment が health data permissions を grant される前提として `Intent.ACTION_VIEW_PERMISSION_USAGE` + `HealthConnectManager.CATEGORY_HEALTH_PERMISSIONS` の対応を要求している。`HealthPermissionIntentAppsTracker` はこの intent を作成して support を追跡し、`PermissionPackageChangesOrchestrator` は app update などで support がなくなった場合に `revokeAllHealthPermissions()` を呼ぶ。

この項目は「granular health permission への移行」と「mobile app の additional manifest / intent requirement」を分けて説明する必要がある。Wear OS app については HealthFitness service が `FEATURE_WATCH` で rationale intent requirement を不要とする分岐を持つため、mobile app と Wear OS app を混ぜない。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statement）

検証対象 statement:

```text
Mobile apps migrating to use the READ_HEART_RATE and other granular permissions must also declare an activity to display the app's privacy policy.
```

```text
This is the same requirement as Health Connect.
```

```text
Failure to provide the rationale for mobile apps will result in the permission being revoked.
```

## 最新本文との差分（Documentation drift）

調査開始時に公式 URL の `#mobile` section を再確認した。確認時点の公式本文は、ユーザー提示の Original statements と実質差分はなかった。

確認した現行本文の要点:
- mobile apps が `READ_HEART_RATE` とその他 granular permissions へ移行する場合、privacy policy を表示する activity を declare する必要がある。
- これは Health Connect と同じ requirement。
- mobile apps が rationale を提供しない場合、permission は revoke される。

## 解釈（Interpretation）

この section は permission migration の子項目であり、`BODY_SENSORS` から `READ_HEART_RATE` へ移ること自体ではなく、mobile app が health permission grant を維持するために必要な additional declaration を説明している。

---

# 変更内容（What Changed）

- Android 16 / targetSdkVersion 36 以上では、親項目により `BODY_SENSORS` / `BODY_SENSORS_BACKGROUND` 前提の API が granular `android.permission.health.*` を要求する。
- mobile app が granular health permission を明示 request する場合、Health Connect と同じ privacy policy / rationale activity support が必要になる。
- HealthFitness service は `ACTION_VIEW_PERMISSION_USAGE` + `CATEGORY_HEALTH_PERMISSIONS` に対応する activity support を確認する。
- activity support がなく、enforcement 対象の場合、HealthFitness service は all health permissions を revoke する。
- Wear devices では rationale intent は現在 required ではないという分岐がある。
- split permission migration 由来の implicit health permission だけなら、phone でも rationale intent enforcement から除外される場合がある。

---

# 適用条件（Applicability）

## OS アップデート時の挙動（OS Update Behavior）

- Android 16 に OS アップデートしただけで targetSdkVersion 35 以下の全アプリに同じ強制が適用されるか: No。
- legacy app については親項目の permission migration code が `BODY_SENSORS` / `READ_HEART_RATE`、`BODY_SENSORS_BACKGROUND` / `READ_HEALTH_DATA_IN_BACKGROUND` の state sync を行う。
- HealthFitness 側も split permission migration 由来の permission のみなら rationale intent enforcement を除外する経路がある。

## targetSdkVersion 36 以上での挙動（targetSdkVersion 36 Behavior）

- Android 16 / targetSdkVersion 36 以上で mobile app が granular health permission を明示 request する場合、privacy policy / rationale activity support が必要。
- `READ_HEART_RATE`、`READ_HEALTH_DATA_IN_BACKGROUND`、その他 Health Connect style read permissions を request する mobile app は対象になり得る。
- `BODY_SENSORS` only のままでは、親項目の Android 16 target behavior を満たさない。さらに `READ_HEART_RATE` へ移行すると mobile rationale requirement の対象になり得る。

## Android 15 / targetSdkVersion 36

- Android 15 baseline では `Sensor.TYPE_HEART_RATE` doc は `BODY_SENSORS` のみを示していた。
- HealthFitness / Health Connect requirement 自体は以前から存在するが、Android 16 target の granular permission migration により mobile apps の該当範囲が広がる。
- Android 15 / targetSdkVersion 36 は Android 16 の公式 Behavior Change と同一とは結論しない。検証可能な場合は Android 16 / targetSdkVersion 36 と比較する。

## Mobile app と Wear OS app

- HealthFitness `HealthConnectPermissionHelper` は `PackageManager.FEATURE_WATCH` を持つ device では rationale intent は currently required ではないと返す。
- したがって公式文書の `Mobile apps` requirement は mobile / phone class の app に重点がある。
- Wear OS Health Services / ProtoLayout は親項目の公式 statement 上は対象だが、本 section の rationale activity requirement とは分けて検証する。

---

# AOSP 調査（AOSP Investigation）

## 関連ファイル（Related Files）

frameworks/base:
- `core/res/AndroidManifest.xml`
- `core/java/android/hardware/Sensor.java`
- `core/java/android/content/pm/ServiceInfo.java`
- `core/java/android/app/ForegroundServiceTypePolicy.java`
- `core/java/android/permission/flags.aconfig`
- `services/permission/java/com/android/server/permission/access/permission/AppIdPermissionUpgrade.kt`
- `services/permission/java/com/android/server/permission/access/permission/AppIdPermissionPolicy.kt`

HealthFitness module:
- `framework/java/android/health/connect/HealthPermissions.java`
- `apk/HealthPermissionsManifest.xml`
- `service/java/com/android/server/healthconnect/permission/HealthConnectPermissionHelper.java`
- `service/java/com/android/server/healthconnect/permission/PermissionPackageChangesOrchestrator.java`
- `service/java/com/android/server/healthconnect/permission/HealthPermissionIntentAppsTracker.java`

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル | Android 15 baseline | Android 16 target | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `Sensor.TYPE_HEART_RATE` | `BODY_SENSORS` が必要 | SDK < 36 は `BODY_SENSORS`、SDK >= 36 は `READ_HEART_RATE` | parent permission migration の targetSdkVersion 36 gate |
| `HealthPermissions.java` | Health Connect permission class | `ACTION_VIEW_PERMISSION_USAGE` + health category support を health permission grant の前提として記載 | Health Connect と同じ requirement の根拠 |
| `HealthPermissionsManifest.xml` | granular health permissions | `READ_HEART_RATE` / `READ_HEALTH_DATA_IN_BACKGROUND` などが HEALTH group / dangerous | mobile app が request する permission 定義 |
| `HealthPermissionIntentAppsTracker` | intent tracker | `ACTION_VIEW_PERMISSION_USAGE` + `CATEGORY_HEALTH_PERMISSIONS` intent support を追跡 | privacy policy / rationale activity 検出経路 |
| `HealthConnectPermissionHelper#shouldEnforcePermissionUsageIntent` | helper | Wear exemption、explicit health permission request 判定、split permission exemption | mobile / Wear / migration 由来の分離 |
| `PermissionPackageChangesOrchestrator` | package changes | intent support removed / missing 時に `revokeAllHealthPermissions()` | permission revoked statement の根拠 |
| `HealthConnectPermissionHelper#revokeAllHealthPermissionsUnchecked` | revoke helper | granted health permissions と legacy BODY_SENSORS 系を revoke | missing rationale 時の revoke 対象 |
| `AppIdPermissionUpgrade` / `AppIdPermissionPolicy` | legacy permission sync | target < BAKLAVA の old/new permission state sync / mismatch revoke | OS update impact と targetSdk impact の分離 |

必須記入項目（Required context）:
- Entry point / caller: app manifest activity intent filter -> PackageManager query -> `HealthPermissionIntentAppsTracker` -> `HealthConnectPermissionHelper#shouldEnforcePermissionUsageIntent()` -> `PermissionPackageChangesOrchestrator` -> `revokeAllHealthPermissions()`。
- Relevant class or service responsibility: HealthFitness / Health Connect permission controller は health permissions の grant / revoke、permission usage intent support、legacy permission migration を扱う。
- Baseline Android behavior: Android 15 では Android 16 target の `BODY_SENSORS` replacement はまだ公式 target behavior ではない。Health Connect requirement は存在するが、platform sensor permission migration と結び付く範囲は Android 16 で広がる。
- Target Android behavior: Android 16 / targetSdkVersion 36 以上の mobile app が granular health permission を明示 request する場合、privacy policy / rationale activity support が必要。
- Diff kind: changed condition / added requirement through parent migration。mobile requirement 自体は Health Connect mechanism だが、Android 16 target の permission migration により `READ_HEART_RATE` などへ移行する mobile app が対象になる。
- Classification support: targetSdkVersion 36 gate と mobile + explicit granular health permission request + rationale activity condition があるため `TARGET_SDK_36_CONDITIONAL`。
- Unrelated or excluded paths: Wear OS Health Services / ProtoLayout の API 実装詳細は Wear / Jetpack 側。ここでは mobile rationale requirement と分ける。

## privacy policy / rationale activity の宣言方法

HealthFitness `HealthPermissions`:

```text
Apps must support Intent.ACTION_VIEW_PERMISSION_USAGE with
HealthConnectManager.CATEGORY_HEALTH_PERMISSIONS category to be granted read/write health data permissions.
```

HealthFitness `HealthPermissionIntentAppsTracker`:

```text
Intent healthIntent = new Intent(Intent.ACTION_VIEW_PERMISSION_USAGE);
healthIntent.addCategory(HealthConnectManager.CATEGORY_HEALTH_PERMISSIONS);
```

解釈:
- AndroidManifest に、上記 action / category に応答する activity を宣言する必要がある。
- 公式文書はこの activity を privacy policy を表示する activity と説明している。
- exported / enabled / resolvable などの component state は実機で確認が必要。少なくとも PackageManager が intent support ありと判断できる必要がある。

## missing / removed 時の revoke 経路

`PermissionPackageChangesOrchestrator` は package change 時に intent support を更新し、support がなく enforcement 対象なら permission を revoke する。

```text
if (supportsIntent || !mPermissionHelper.shouldEnforcePermissionUsageIntent(packageName, userHandle)) {
    return;
}

mPermissionHelper.revokeAllHealthPermissions(
        packageName,
        "Health permissions usage activity has been removed.",
        userHandle);
```

`HealthConnectPermissionHelper#revokeAllHealthPermissionsUnchecked()` は granted health permissions を revoke し、legacy app の `BODY_SENSORS` / `BODY_SENSORS_BACKGROUND` も条件により revoke する。

解釈:
- 公式 statement の「Failure to provide the rationale ... permission being revoked」は AOSP evidence と整合する。
- permission initially granted 後に app update で activity が消えた場合も revoke path がある。

## mobile app / Wear OS app の分離

`HealthConnectPermissionHelper#shouldEnforcePermissionUsageIntent()`:

```text
if (mPackageManager.hasSystemFeature(PackageManager.FEATURE_WATCH)) {
    return false;
}
```

解釈:
- Wear device では rationale intent は currently required ではない。
- Mobile apps section の customer-facing explanation では、phone / mobile app と Wear OS app を分ける。

## split permission migration との関係

HealthFitness helper は、split permission migration 由来の `READ_HEART_RATE` / `READ_HEALTH_DATA_IN_BACKGROUND` だけの場合は rationale enforcement を除外する経路を持つ。

```text
When flag is enabled, and is requesting split permission, do not enforce permission usage intent on Phone.
```

解釈:
- OS update によって implicit に health permission が付与 / 同期される legacy app と、targetSdkVersion 36 化により granular permission を明示 request する app を分ける必要がある。
- 本 section の主対象は後者の mobile app。

## parent permission migration の根拠

`Sensor.TYPE_HEART_RATE`:

```text
This sensor requires permission android.permission.BODY_SENSORS for SDK < 36 and
android.permission.health.READ_HEART_RATE for SDK >= 36.
```

`ServiceInfo.FOREGROUND_SERVICE_TYPE_HEALTH` / `ForegroundServiceTypePolicy` は `READ_HEART_RATE`、`READ_SKIN_TEMPERATURE`、`READ_OXYGEN_SATURATION` を health FGS の allowed permission として含む。

解釈:
- mobile rationale requirement は parent migration と密接に関連するが、permission enforcement そのものとは別の Health Connect requirement である。

---

# 期待挙動マトリクス（Expected Behavior Matrix）

## OS / targetSdkVersion Matrix

| シナリオ | 期待挙動 | 根拠 / 注意 |
| --- | --- | --- |
| Android 16 / targetSdkVersion 35 | legacy app として permission sync / split permission migration の対象になり得る | rationale enforcement は split permission only なら除外され得る |
| Android 16 / targetSdkVersion 36 | granular health permission を明示 request する mobile app は rationale activity requirement 対象 | 公式文書 / HealthFitness evidence |
| Android 15 / targetSdkVersion 36 | Android 16 の parent permission migration と同一とは結論しない | Android 15 baseline では `TYPE_HEART_RATE` doc は `BODY_SENSORS` |

## Mobile Requirement Matrix

| シナリオ | 期待挙動 / 確認点 |
| --- | --- |
| Android 16 / targetSdkVersion 36 / mobile app / `READ_HEART_RATE` / privacy policy activity declared | health permission grant / 유지が可能 |
| Android 16 / targetSdkVersion 36 / mobile app / `READ_HEART_RATE` / privacy policy activity missing | grant されない、または revoke され得る |
| Android 16 / targetSdkVersion 36 / mobile app / `READ_HEALTH_DATA_IN_BACKGROUND` / privacy policy activity declared | background health permission flow の前提を満たす |
| Android 16 / targetSdkVersion 36 / mobile app / `READ_HEALTH_DATA_IN_BACKGROUND` / privacy policy activity missing | grant されない、または revoke され得る |
| Android 16 / targetSdkVersion 36 / mobile app / `BODY_SENSORS` only | parent migration の target behavior を満たさない |
| Android 16 / targetSdkVersion 36 / mobile app / migrated granular permissions | rationale activity requirement を確認 |
| Android 16 / targetSdkVersion 36 / mobile app / Health Connect read permission flow | Health Connect と同じ rationale / privacy policy activity が必要 |
| Android 16 / targetSdkVersion 36 / mobile app / permission initially granted then privacy policy activity removed | package change handling で health permissions revoke |
| Android 16 / targetSdkVersion 36 / Wear OS app / Health Services flow | AOSP evidence 上 rationale intent は Wear device では required ではない。Wear SDK 側で別途検証 |
| Android 16 / targetSdkVersion 36 / foreground service type health | parent migration により granular health permissions を確認 |
| Android 16 / targetSdkVersion 36 / `Sensor.TYPE_HEART_RATE` | parent migration により `READ_HEART_RATE` を確認 |

---

# 影響対象（Affected App Categories）

- mobile app で `READ_HEART_RATE` を要求するアプリ。
- mobile app で `READ_HEALTH_DATA_IN_BACKGROUND` を要求するアプリ。
- mobile app でその他 `android.permission.health.*` granular permissions を要求するアプリ。
- `BODY_SENSORS` から granular permissions へ移行中のアプリ。
- privacy policy activity / rationale を未宣言の mobile app。
- privacy policy activity / rationale を宣言済みの mobile app。
- Health Connect permission flow を使う mobile app。
- `Sensor.TYPE_HEART_RATE` を使う mobile app。
- `FOREGROUND_SERVICE_TYPE_HEALTH` を使う mobile app。
- Wear OS Health Services を使う app。
- permission migration 済みアプリ。

---

# テスト観点（Test Considerations）

必須比較:
- Android 15 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 36。
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較。

mobile rationale / privacy policy:
- `READ_HEART_RATE` request with privacy policy activity declared。
- `READ_HEART_RATE` request without privacy policy activity。
- `READ_HEALTH_DATA_IN_BACKGROUND` request with privacy policy activity declared。
- `READ_HEALTH_DATA_IN_BACKGROUND` request without privacy policy activity。
- privacy policy activity declared / missing / disabled / not exported の違い。
- permission grant / denial / revoke flow。
- permission initially granted 後に app update で privacy policy activity が消えた場合。
- Health Connect permission UI / platform permission UI の表示差。

parent permission migration:
- `BODY_SENSORS` only の既存挙動。
- `BODY_SENSORS` から `READ_HEART_RATE` へ移行後の permission request UX。
- `Sensor.TYPE_HEART_RATE` access。
- foreground service type health 起動。
- background sensor access。
- runtime permission request fallback behavior。
- existing user upgrade path。

---

# Facts / Observations / Hypotheses / Conclusions

## Facts

- 公式 `Mobile apps` section は、granular permissions へ移行する mobile apps に privacy policy activity declaration を求めている。
- `HealthPermissions` は health data permissions の grant 前提として `ACTION_VIEW_PERMISSION_USAGE` + `CATEGORY_HEALTH_PERMISSIONS` support を求める。
- `HealthPermissionIntentAppsTracker` は上記 action / category の intent を作って support を追跡する。
- `PermissionPackageChangesOrchestrator` は support がなく enforcement 対象なら `revokeAllHealthPermissions()` を呼ぶ。
- `HealthConnectPermissionHelper` は Wear device では rationale intent は currently required ではないとする。
- `HealthConnectPermissionHelper` は split permission migration 由来の `READ_HEART_RATE` / `READ_HEALTH_DATA_IN_BACKGROUND` だけなら enforcement を除外し得る。

## Observations

- 公式文書の「same requirement as Health Connect」は、HealthFitness `HealthPermissions` の class comment と実装で確認できる。
- 「permission being revoked」は package change 時の support removal / missing による revoke path と整合する。
- mobile app requirement は parent permission migration とは別レイヤーの Health Connect permission controller requirement である。
- health permission 専用 compat Change ID は見つからなかった。

## Hypotheses

- activity が manifest にあっても disabled / not exported / intent filter 不一致の場合、PackageManager query で support なしになり revoke 対象になる可能性がある。
- `READ_HEART_RATE` と `READ_HEALTH_DATA_IN_BACKGROUND` が split permission migration 由来で付与された targetSdkVersion 35 app は、明示 request する targetSdkVersion 36 app と異なる UX になる可能性がある。
- Health Connect permission UI と platform runtime permission UI の差により、permission migration 後の user education / fallback behavior が必要になる可能性がある。

## Conclusions

- 本項目の主分類は `TARGET_SDK_36_CONDITIONAL`。
- Android 16 / targetSdkVersion 36 以上の mobile app が granular health permission を明示 request する場合、permission 名の移行に加えて privacy policy / rationale activity の宣言が必要になる。
- missing / removed の場合は health permissions が revoke され得る。
- Wear OS app は AOSP evidence 上、この mobile rationale requirement から分離して扱う。
- 顧客向けには「Android 16 OS update だけ」「targetSdkVersion 36 化」「granular permission migration」「mobile app additional activity requirement」を混ぜない。

---

# 推奨対応候補（Recommended Action Candidates）

- `READ_HEART_RATE`、`READ_HEALTH_DATA_IN_BACKGROUND`、その他 `android.permission.health.*` を request する mobile app は、manifest に `ACTION_VIEW_PERMISSION_USAGE` + `CATEGORY_HEALTH_PERMISSIONS` 対応 activity を追加する。
- app update で privacy policy activity が消えないよう、manifest merge と enabled/exported/intent-filter を確認する。
- `BODY_SENSORS` から `READ_HEART_RATE` へ移行する際は、runtime permission request UX と Health Connect permission UI の両方をテストする。
- Wear OS app は mobile app requirement と分け、Wear Health Services / ProtoLayout の SDK guidance に従って検証する。

---

# Human Decision

最終優先度（Final Priority）:
- 未判断

最終 severity（Final Severity）:
- 未判断

Release readiness:
- 未判断

Customer communication priority:
- 未判断

Owner notes:
- 最終優先度、severity、release readiness、顧客 communication priority は repository owner が判断する。

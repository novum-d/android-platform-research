# Health and fitness permissions 調査レポート

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:
- `android16/AGENTS.md` の既定 scope は `android-16.0.0_r1` だが、この調査では依頼に従い、公開済み Android 16 tag として `android-16.0.0_r4` を使った。
- `frameworks-base` checkout は clean。指定 tag `android-15.0.0_r36` / `android-16.0.0_r4` はどちらも存在する。
- AOSP evidence は `frameworks-base` local checkout と、`tmp/aosp-checkouts/HealthFitness` に shallow clone した `platform/packages/modules/HealthFitness` の `android-16.0.0_r4` tag を参照した。

### Behavior Change 文書（Behavior Change Source）

Document:
- https://developer.android.com/about/versions/16/behavior-changes-16#health-fitness-permissions

Section:
- Health and fitness permissions

Category:
- Health and fitness

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `TARGET_SDK_36_CONDITIONAL`

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 16 へ OS アップデートしただけで targetSdkVersion 35 以下の全アプリに適用されるか | No | 公式文書は Android 16 / API 36 以上 target が条件。AOSP は legacy app 向け同期処理を持つ |
| targetSdkVersion 36 以上が必要か | Yes | `Sensor.TYPE_HEART_RATE` doc は SDK < 36 と SDK >= 36 で必要 permission を分岐 |
| `BODY_SENSORS` は廃止されたか | No | API surface / manifest 定義は残るが、Android 16 target では該当 API が granular health permission を要求 |
| `READ_HEART_RATE` は platform sensor path に接続されるか | Yes | `Sensor.TYPE_HEART_RATE` doc、AppOps `OP_READ_HEART_RATE`、FGS health policy が参照 |
| `READ_HEALTH_DATA_IN_BACKGROUND` は background access に接続されるか | Yes | HealthFitness `HealthPermissions` / manifest と permission migration code が参照 |
| FGS health は granular permission を見るか | Yes | `ForegroundServiceTypePolicy#getAllowedHealthPermissions()` が `READ_HEART_RATE` / `READ_SKIN_TEMPERATURE` / `READ_OXYGEN_SATURATION` を許可候補に追加 |
| Compat framework Change ID | Not found | 公式 compat framework changes に health permission 専用 Change ID は見つからない。AOSP aconfig flag は存在 |
| Mobile privacy policy / rationale activity requirement | Yes | HealthFitness `HealthPermissions` と permission helper / package changes orchestrator が `ACTION_VIEW_PERMISSION_USAGE` + `CATEGORY_HEALTH_PERMISSIONS` を確認し、未対応時に revoke |
| Wear OS Health Services / ProtoLayout | 公式文書上は対象 | AOSP platform evidence ではなく Wear / Jetpack 側に属するため、report では evidence scope を分離 |

### 調査日（Investigation Date）

2026-07-03

### 信頼度（Confidence）

- High for platform permissions / Sensor.TYPE_HEART_RATE / FGS health / Health Connect permission mechanism.
- Medium for Wear OS Health Services / ProtoLayout API details.

理由:
- 公式文書、AOSP permission 定義、HealthFitness module の `HealthPermissions`、Sensor API doc、FGS policy、AppOps、permission migration、rationale activity enforcement が揃っている。
- Wear OS Health Services と ProtoLayout は AOSP platform `frameworks-base` の実装ではなく Wear / Jetpack 依存側に属するため、公式文書 statement と関連 API 名の確認に留める。

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
- App behavior: `BODY_SENSORS` / `BODY_SENSORS_BACKGROUND` 前提で heart rate / SpO2 / skin temperature / background health sensor access / health FGS / Health Connect read permissions を使う。
- Mobile apps: Health Connect health permission を明示 request する場合は `ACTION_VIEW_PERMISSION_USAGE` + `HealthConnectManager.CATEGORY_HEALTH_PERMISSIONS` の rationale / privacy policy activity 対応が必要。

Compat framework:
- Health permission 専用の compat framework Change ID は公式 compat framework changes では確認できなかった。
- AOSP には `replace_body_sensor_permission_enabled` aconfig flag があり、description は `BODY_SENSORS` / `BODY_SENSORS_BACKGROUND` を `READ_HEART_RATE`、`READ_SKIN_TEMPERATURE`、`READ_OXYGEN_SATURATION`、`READ_HEALTH_DATA_IN_BACKGROUND` へ置き換えると説明する。
- `replace_body_sensor_permission_enabled` は `is_fixed_read_only: true` のため、app compat framework の force-enable / force-disable 対象とは扱わない。

---

# エグゼクティブサマリー（Executive Summary）

Android 16 では、targetSdkVersion 36 以上のアプリに対して、従来 `BODY_SENSORS` / `BODY_SENSORS_BACKGROUND` が担っていた health / body sensor access が、`android.permission.health.*` の granular permission へ移行する。

AOSP evidence では、`Sensor.TYPE_HEART_RATE` の API doc が SDK < 36 では `BODY_SENSORS`、SDK >= 36 では `android.permission.health.READ_HEART_RATE` を要求すると明記している。`FOREGROUND_SERVICE_TYPE_HEALTH` も `FOREGROUND_SERVICE_HEALTH` に加え、`ACTIVITY_RECOGNITION` / `HIGH_SAMPLING_RATE_SENSORS` / `READ_HEART_RATE` / `READ_SKIN_TEMPERATURE` / `READ_OXYGEN_SATURATION` のいずれかを要求する形に変わっている。

Health Connect 側では `READ_HEART_RATE`、`READ_OXYGEN_SATURATION`、`READ_SKIN_TEMPERATURE`、`READ_HEALTH_DATA_IN_BACKGROUND` が `android.permission-group.HEALTH` の dangerous permission として定義され、mobile apps は health permission を grant されるために privacy policy / rationale activity を宣言する必要がある。未対応の場合、HealthFitness service は health permissions を revoke する経路を持つ。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statement）

検証対象 statement:

```text
For apps targeting Android 16 (API level 36) or higher, BODY_SENSORS permissions use more granular permissions under android.permissions.health, which Health Connect also uses.
```

```text
As of Android 16, any API previously requiring BODY_SENSORS or BODY_SENSORS_BACKGROUND requires the corresponding android.permissions.health permission instead.
```

```text
This affects ... HEART_RATE_BPM from Health Services on Wear OS, Sensor.TYPE_HEART_RATE from Android Sensor Manager, heartRateAccuracy and heartRateBpm from ProtoLayout on Wear OS, FOREGROUND_SERVICE_TYPE_HEALTH ...
```

```text
For while-in-use monitoring of Heart Rate, SpO2, or Skin Temperature: request the granular permission under android.permissions.health, such as READ_HEART_RATE instead of BODY_SENSORS.
```

```text
For background sensor access: request READ_HEALTH_DATA_IN_BACKGROUND instead of BODY_SENSORS_BACKGROUND.
```

```text
Mobile apps migrating to use the READ_HEART_RATE and other granular permissions must also declare an activity to display the app's privacy policy.
```

```text
Failure to provide the rationale for mobile apps will result in the permission being revoked.
```

## 最新本文との差分（Documentation drift）

調査開始時に公式 URL の該当 section を再確認した。ユーザー提示の Original statements / Applicability details と、確認時点の公式本文に実質差分はなかった。

## 解釈（Interpretation）

この変更は「permission 名の移行」と「permission enforcement の移行」を分けて読む必要がある。`BODY_SENSORS` / `BODY_SENSORS_BACKGROUND` は Android 16 tag にも残るが、targetSdkVersion 36 以上で対象 API を使う場合は granular health permission が必要になる。

---

# 変更内容（What Changed）

- `Sensor.TYPE_HEART_RATE` は SDK < 36 では `BODY_SENSORS`、SDK >= 36 では `READ_HEART_RATE` を要求すると API doc が更新された。
- `FOREGROUND_SERVICE_TYPE_HEALTH` は health FGS の allowed permission として `READ_HEART_RATE`、`READ_SKIN_TEMPERATURE`、`READ_OXYGEN_SATURATION` を含む。
- `AppOpsManager` は `OP_READ_HEART_RATE` / `OP_READ_SKIN_TEMPERATURE` / `OP_READ_OXYGEN_SATURATION` を granular health permission に対応付ける。
- `HealthPermissions` / `HealthPermissionsManifest.xml` は `READ_HEART_RATE`、`READ_OXYGEN_SATURATION`、`READ_SKIN_TEMPERATURE`、`READ_HEALTH_DATA_IN_BACKGROUND` を dangerous health permission として定義する。
- permission service は legacy `BODY_SENSORS` と new `READ_HEART_RATE`、legacy `BODY_SENSORS_BACKGROUND` と `READ_HEALTH_DATA_IN_BACKGROUND` の grant state を同期・保守する移行処理を持つ。
- HealthFitness service は mobile apps の health permission grant に `ACTION_VIEW_PERMISSION_USAGE` + `CATEGORY_HEALTH_PERMISSIONS` 対応を要求し、対応が外れた場合は health permissions を revoke する。

---

# 適用条件（Applicability）

## OS アップデート時の挙動（OS Update Behavior）

- Android 16 に OS アップデートしただけで targetSdkVersion 35 以下の全アプリに同じ強制が適用されるか: No。
- AOSP `AppIdPermissionUpgrade` は targetSdkVersion が `BAKLAVA` 未満の legacy apps について、旧 permission と新 permission の状態を同期し、既存アプリが壊れないようにする処理を持つ。
- ただし permission state が不整合な場合は conservative に revoke して再 prompt を促す可能性がある。

## targetSdkVersion 36 以上での挙動（targetSdkVersion 36 Behavior）

- Android 16 / targetSdkVersion 36 以上では、対象 API は granular health permission を要求する。
- `BODY_SENSORS` のみでは `Sensor.TYPE_HEART_RATE` などの Android 16 target behavior を満たさない。
- `BODY_SENSORS_BACKGROUND` のみでは background access の Android 16 target behavior を満たさない。
- background health data access には `READ_HEALTH_DATA_IN_BACKGROUND` が必要になる。
- mobile apps は Health Connect permission grant のために rationale / privacy policy activity を宣言する必要がある。

## Android 15 / targetSdkVersion 36

- Android 15 tag では `Sensor.TYPE_HEART_RATE` doc は `BODY_SENSORS` のみを示していた。
- Android 16 tag で SDK < 36 / SDK >= 36 の permission 分岐が追加された。
- Android 15 / targetSdkVersion 36 は Android 16 の公式 Behavior Change と同一とは結論しない。検証可能な場合は Android 16 / targetSdkVersion 36 と比較する。

---

# AOSP 調査（AOSP Investigation）

## 関連ファイル（Related Files）

frameworks/base:
- `core/res/AndroidManifest.xml`
- `core/java/android/hardware/Sensor.java`
- `core/java/android/content/pm/ServiceInfo.java`
- `core/java/android/app/ForegroundServiceTypePolicy.java`
- `core/java/android/app/AppOpsManager.java`
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
| `core/res/AndroidManifest.xml` / `BODY_SENSORS` | dangerous、background permission は `BODY_SENSORS_BACKGROUND` | 同じ定義は残る | legacy permission は削除されていない |
| `BODY_SENSORS_BACKGROUND` | dangerous + hardRestricted | 同じ | background legacy permission の属性 |
| `Sensor.TYPE_HEART_RATE` | `BODY_SENSORS` が必要 | SDK < 36 は `BODY_SENSORS`、SDK >= 36 は `READ_HEART_RATE` | targetSdkVersion 36 gate の直接 evidence |
| `ServiceInfo.FOREGROUND_SERVICE_TYPE_HEALTH` | health FGS permission に `BODY_SENSORS` 分岐あり | `READ_HEART_RATE` / `READ_SKIN_TEMPERATURE` / `READ_OXYGEN_SATURATION` を要求候補に含む | FGS health の migration evidence |
| `ForegroundServiceTypePolicy#getAllowedHealthPermissions()` | flag 分岐で `BODY_SENSORS` または granular | Android 16 r4 では granular permission を直接追加 | FGS enforcement policy |
| `AppOpsManager` | body sensors app op 中心 | `OP_READ_HEART_RATE` 等が granular permission に対応 | AppOps 接続 |
| `HealthPermissions.java` | Health Connect permission class | granular health permissions を定義 | Health Connect と platform permission の接続 |
| `HealthPermissionsManifest.xml` | module manifest | granular permission が `android.permission-group.HEALTH` / dangerous として定義 | permission group / protection level |
| `AppIdPermissionUpgrade` | legacy sync なし | target < BAKLAVA 向けに legacy / granular permission state を同期 | OS update / legacy app 互換 |
| `AppIdPermissionPolicy` | package update sync なし | legacy / granular permission mismatch を revoke して再 prompt | existing user upgrade path |
| `HealthConnectPermissionHelper` | Health permission helper | rationale intent enforcement、Wear exemption、split permission exemption、revoke logic | mobile privacy policy / rationale evidence |
| `PermissionPackageChangesOrchestrator` | package changes handling | rationale intent support removed 時に all health permissions revoke | missing privacy policy activity behavior |

必須記入項目（Required context）:
- Entry point / caller: `SensorManager` API exposure -> `Sensor.TYPE_HEART_RATE` permission doc / AppOps、foreground service start -> `ForegroundServiceTypePolicy`、Health Connect grant / revoke -> HealthFitness permission helper。
- Relevant class or service responsibility: framework permission definitions、AppOps、FGS type enforcement、PermissionManager migration、Health Connect permission controller。
- Baseline Android behavior: Android 15 では `TYPE_HEART_RATE` は `BODY_SENSORS` を要求する説明。FGS health は `BODY_SENSORS` を含む分岐があった。
- Target Android behavior: Android 16 では targetSdkVersion 36 以上で granular health permission を要求する説明・policy に変わる。
- Diff kind: changed condition / changed default / API surface addition。`Sensor.TYPE_HEART_RATE` doc と FGS health policy が granular permission へ変化。HealthFitness module に granular health permissions が存在。
- Classification support: targetSdkVersion 36 gate が公式文書と `Sensor.TYPE_HEART_RATE` doc にあるため `TARGET_SDK_36_CONDITIONAL`。
- Unrelated or excluded paths: Wear OS Health Services / ProtoLayout は platform `frameworks-base` ではなく Wear / Jetpack 側。AOSP platform evidence としては扱わず公式 statement として分離する。

## Permission 定義

`BODY_SENSORS`:

```text
android.permission.BODY_SENSORS
permissionGroup="android.permission-group.UNDEFINED"
backgroundPermission="android.permission.BODY_SENSORS_BACKGROUND"
protectionLevel="dangerous"
```

`BODY_SENSORS_BACKGROUND`:

```text
android.permission.BODY_SENSORS_BACKGROUND
protectionLevel="dangerous"
permissionFlags="hardRestricted"
```

HealthFitness `HealthPermissions`:

```text
READ_HEART_RATE = "android.permission.health.READ_HEART_RATE"
READ_OXYGEN_SATURATION = "android.permission.health.READ_OXYGEN_SATURATION"
READ_SKIN_TEMPERATURE = "android.permission.health.READ_SKIN_TEMPERATURE"
READ_HEALTH_DATA_IN_BACKGROUND = "android.permission.health.READ_HEALTH_DATA_IN_BACKGROUND"
```

HealthFitness `HealthPermissionsManifest.xml`:

```text
READ_HEART_RATE / READ_OXYGEN_SATURATION / READ_SKIN_TEMPERATURE:
protectionLevel="dangerous"
backgroundPermission="android.permission.health.READ_HEALTH_DATA_IN_BACKGROUND"
permissionGroup="android.permission-group.HEALTH"

READ_HEALTH_DATA_IN_BACKGROUND:
protectionLevel="dangerous"
permissionGroup="android.permission-group.HEALTH"
```

## Sensor.TYPE_HEART_RATE enforcement path

`Sensor.TYPE_HEART_RATE` の Android 16 doc:

```text
This sensor requires permission android.permission.BODY_SENSORS for SDK < 36 and
android.permission.health.READ_HEART_RATE for SDK >= 36.
It will not be returned by SensorManager.getSensorsList nor
SensorManager.getDefaultSensor if the application doesn't have this permission.
```

解釈:
- Android 16 / targetSdkVersion 36 以上では `READ_HEART_RATE` が必要。
- `BODY_SENSORS` only のアプリは、heart rate sensor を取得できない可能性がある。
- 低レイヤーの SensorService 実装詳細までは `frameworks-base` 内で完全には追跡できなかったが、public API doc と permission / AppOps 接続は一致する。

## Foreground service type health

`ServiceInfo.FOREGROUND_SERVICE_TYPE_HEALTH` は `FOREGROUND_SERVICE_HEALTH` と、以下のいずれかを要求する。

- `ACTIVITY_RECOGNITION`
- `HIGH_SAMPLING_RATE_SENSORS`
- `READ_HEART_RATE`
- `READ_SKIN_TEMPERATURE`
- `READ_OXYGEN_SATURATION`

`ForegroundServiceTypePolicy#getAllowedHealthPermissions()` も同じ granular health permissions を許可候補に追加する。

解釈:
- health FGS を使うアプリは、実際の health data access に応じた granular permission を持つ必要がある。
- Android 15 baseline との差分では、`BODY_SENSORS` 分岐が除去され、granular permissions が直接追加されている。

## Health Connect / privacy policy activity / revoke behavior

`HealthPermissions` は health permissions grant の条件として以下を求める。

```text
Apps must support Intent.ACTION_VIEW_PERMISSION_USAGE with
HealthConnectManager.CATEGORY_HEALTH_PERMISSIONS category to be granted read/write health data permissions.
```

`HealthPermissionIntentAppsTracker` は `ACTION_VIEW_PERMISSION_USAGE` + `CATEGORY_HEALTH_PERMISSIONS` を持つ intent を作る。

`PermissionPackageChangesOrchestrator` は package が存在し、かつ health permission usage intent を support せず、enforcement 対象であれば、all health permissions を revoke する。

`HealthConnectPermissionHelper` は次を分ける。
- Wear devices では rationale intent は現在 required ではない。
- split permission migration 由来の `READ_HEART_RATE` / `READ_HEALTH_DATA_IN_BACKGROUND` だけなら Phone でも rationale intent enforcement を除外。
- health permission を明示 request する package は rationale intent enforcement 対象。

解釈:
- 公式の「mobile apps は privacy policy activity を declare」「missing なら permission revoked」は HealthFitness service evidence と整合する。
- Wear OS app は AOSP evidence 上、少なくともこの rationale intent enforcement から除外される。

## Permission migration / existing user upgrade path

`AppIdPermissionUpgrade`:

```text
Starting in BAKLAVA, the BODY_SENSORS and BODY_SENSORS_BACKGROUND permissions are being
replaced by the READ_HEART_RATE and READ_HEALTH_DATA_IN_BACKGROUND permissions respectively.
```

target < BAKLAVA の older apps では、`BODY_SENSORS` / `READ_HEART_RATE`、`BODY_SENSORS_BACKGROUND` / `READ_HEALTH_DATA_IN_BACKGROUND` の grant state を同期する。

`AppIdPermissionPolicy` は package update 時に mismatch があると両方 revoke して re-prompt を促す。

解釈:
- OS update だけで既存 targetSdkVersion 35 app を即座に target 36 挙動へ変えるのではなく、legacy compatibility と permission state synchronization がある。
- ただし migration 中に old/new permission の grant state が食い違うと revoke され得る。

---

# 期待挙動マトリクス（Expected Behavior Matrix）

## OS / targetSdkVersion Matrix

| シナリオ | 期待挙動 | 根拠 / 注意 |
| --- | --- | --- |
| Android 16 / targetSdkVersion 35 | legacy app として `BODY_SENSORS` 系との同期・互換が働く | `AppIdPermissionUpgrade` は target < BAKLAVA を対象に sync |
| Android 16 / targetSdkVersion 36 | 対象 API は granular health permission を要求 | 公式文書 / `Sensor.TYPE_HEART_RATE` doc |
| Android 15 / targetSdkVersion 36 | Android 16 と同一とは結論しない | Android 15 baseline では `TYPE_HEART_RATE` doc は `BODY_SENSORS` |

## Permission / API Matrix

| シナリオ | 期待挙動 / 確認点 |
| --- | --- |
| Android 16 / targetSdkVersion 36 / `BODY_SENSORS` only | `Sensor.TYPE_HEART_RATE` 等の Android 16 target requirement を満たさない |
| Android 16 / targetSdkVersion 36 / `BODY_SENSORS_BACKGROUND` only | background health access requirement を満たさない |
| Android 16 / targetSdkVersion 36 / `READ_HEART_RATE` declared | while-in-use heart rate access の候補 permission |
| Android 16 / targetSdkVersion 36 / `READ_HEALTH_DATA_IN_BACKGROUND` declared | background health data access の候補 permission |
| Android 16 / targetSdkVersion 36 / while-in-use heart rate monitoring | `READ_HEART_RATE` を request / grant する |
| Android 16 / targetSdkVersion 36 / background heart rate monitoring | `READ_HEART_RATE` + `READ_HEALTH_DATA_IN_BACKGROUND` を確認 |
| Android 16 / targetSdkVersion 36 / SpO2 monitoring | `READ_OXYGEN_SATURATION` を request / grant する |
| Android 16 / targetSdkVersion 36 / Skin Temperature monitoring | `READ_SKIN_TEMPERATURE` を request / grant する |
| Android 16 / targetSdkVersion 36 / `Sensor.TYPE_HEART_RATE` | SDK >= 36 では `READ_HEART_RATE` が必要 |
| Android 16 / targetSdkVersion 36 / `FOREGROUND_SERVICE_TYPE_HEALTH` | `FOREGROUND_SERVICE_HEALTH` + allowed health/activity/sensor permission が必要 |
| Android 16 / targetSdkVersion 36 / privacy policy activity declared | mobile health permission grant の前提を満たす |
| Android 16 / targetSdkVersion 36 / privacy policy activity missing | health permissions が grant されない / revoke され得る |
| Android 16 / targetSdkVersion 36 / Health Connect read permission flow | Health Connect permission UI / `android.permission-group.HEALTH` を使う |
| Android 16 / targetSdkVersion 36 / Wear OS Health Services flow | 公式文書上は対象。Wear / Jetpack 側実装で別途検証 |

---

# 影響対象（Affected App Categories）

- `BODY_SENSORS` を宣言しているアプリ: Android 16 target では `READ_HEART_RATE` などへの移行が必要。
- `BODY_SENSORS_BACKGROUND` を宣言しているアプリ: `READ_HEALTH_DATA_IN_BACKGROUND` への移行が必要。
- `Sensor.TYPE_HEART_RATE` を使うアプリ: targetSdkVersion 36 で `READ_HEART_RATE` が必要。
- foreground service type health を使うアプリ: `FOREGROUND_SERVICE_HEALTH` と granular health / activity / high sampling sensor permission を確認する。
- background health / sensor monitoring を行うアプリ: background permission と foreground permission の組み合わせを確認する。
- Heart Rate / SpO2 / Skin Temperature を while-in-use で読むアプリ: data type ごとの granular permission が必要。
- Health Connect と platform sensor permissions の両方を扱うアプリ: Health Connect UI と platform runtime permission UX を分けて設計する。
- Wear OS Health Services を使うアプリ: 公式文書上は `HEART_RATE_BPM` が対象。Wear 実機 / SDK 側で検証する。
- ProtoLayout の `heartRateAccuracy` / `heartRateBpm` を使う Wear OS アプリ: 公式文書上は対象。ProtoLayout dependency 側で検証する。
- mobile app で privacy policy activity / rationale を未実装のアプリ: health permission revoke のリスク。
- permission migration 済みアプリ: manifest、runtime request、privacy policy activity、upgrade path を確認する。

---

# テスト観点（Test Considerations）

必須比較:
- Android 15 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 36。
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較。

permission / API:
- `BODY_SENSORS` only で `Sensor.TYPE_HEART_RATE` にアクセスした場合。
- `READ_HEART_RATE` で `Sensor.TYPE_HEART_RATE` にアクセスした場合。
- `BODY_SENSORS_BACKGROUND` only で background sensor access した場合。
- `READ_HEALTH_DATA_IN_BACKGROUND` で background sensor access した場合。
- `FOREGROUND_SERVICE_TYPE_HEALTH` 起動時の permission requirement。
- Heart Rate / SpO2 / Skin Temperature の while-in-use permission request。
- background access permission request。
- permission grant / denial / revoke flow。
- privacy policy activity declared / missing。
- Health Connect permission UI / platform permission UI の表示差。
- Wear OS 実機または emulator で Health Services / ProtoLayout 該当 API を使う場合の挙動。
- permission migration 後の既存ユーザー upgrade path。
- runtime permission request UX / fallback behavior。

---

# Facts / Observations / Hypotheses / Conclusions

## Facts

- 公式文書は Android 16 / API 36 以上 target の app に granular health permission 移行を求めている。
- `Sensor.TYPE_HEART_RATE` doc は SDK < 36 は `BODY_SENSORS`、SDK >= 36 は `READ_HEART_RATE` と明記する。
- `BODY_SENSORS` / `BODY_SENSORS_BACKGROUND` は Android 16 tag に残る。
- `READ_HEART_RATE`、`READ_OXYGEN_SATURATION`、`READ_SKIN_TEMPERATURE`、`READ_HEALTH_DATA_IN_BACKGROUND` は HealthFitness module で dangerous health permissions として定義される。
- `FOREGROUND_SERVICE_TYPE_HEALTH` は granular health permissions を allowed permission に含める。
- mobile health permission grant には `ACTION_VIEW_PERMISSION_USAGE` + `CATEGORY_HEALTH_PERMISSIONS` support が必要。
- rationale intent support が外れると HealthFitness service は health permissions を revoke する経路を持つ。

## Observations

- Health permission 専用 compat Change ID は公式 compat framework changes では見つからなかった。
- AOSP aconfig `replace_body_sensor_permission_enabled` は fixed read-only であり、app compat toggle とは異なる。
- legacy apps の permission state を同期する migration code があり、OS update だけの影響と targetSdkVersion 36 化の影響を分ける必要がある。
- Wear devices は rationale intent enforcement から除外される実装がある。

## Hypotheses

- targetSdkVersion 36 app が `BODY_SENSORS` only のまま heart rate sensor を読むと、sensor list / default sensor 取得または access が失敗する可能性が高い。
- `READ_HEALTH_DATA_IN_BACKGROUND` は単独では十分でなく、data type の foreground read permission と組み合わせて検証する必要がある。
- Health Connect permission UI と platform runtime permission UI はユーザー体験が異なるため、migration 後の permission request UX が変わる可能性がある。

## Conclusions

- 本項目の主分類は `TARGET_SDK_36_CONDITIONAL`。
- Android 16 / targetSdkVersion 36 以上では、`BODY_SENSORS` / `BODY_SENSORS_BACKGROUND` 前提の実装を granular `android.permission.health.*` permission へ移行する必要がある。
- `Sensor.TYPE_HEART_RATE`、FGS health、Health Connect permission flow は AOSP evidence で変更根拠を確認できる。
- Wear OS Health Services / ProtoLayout は公式文書上の対象だが、AOSP platform evidence ではなく Wear / Jetpack 側検証として分離する。
- mobile app は privacy policy / rationale activity 未実装だと health permission revoke リスクがある。

---

# 推奨対応候補（Recommended Action Candidates）

- manifest の `BODY_SENSORS` / `BODY_SENSORS_BACKGROUND` 利用箇所を洗い出し、`READ_HEART_RATE`、`READ_OXYGEN_SATURATION`、`READ_SKIN_TEMPERATURE`、`READ_HEALTH_DATA_IN_BACKGROUND` に置き換える。
- `Sensor.TYPE_HEART_RATE` 利用箇所は targetSdkVersion 36 で `READ_HEART_RATE` grant を前提にテストする。
- background monitoring は foreground read permission と `READ_HEALTH_DATA_IN_BACKGROUND` の両方を確認する。
- health FGS は `FOREGROUND_SERVICE_HEALTH` と allowed permission の組み合わせを確認する。
- mobile apps は `ACTION_VIEW_PERMISSION_USAGE` + `CATEGORY_HEALTH_PERMISSIONS` に対応する privacy policy / rationale activity を宣言する。
- Wear OS Health Services / ProtoLayout は Wear 実機または emulator と該当 SDK version で別途検証する。

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

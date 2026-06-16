# Per-app keystore limits

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

比較元:
- android-16.0.0_r4

比較先:
- TBD: Android 17 AOSP tag

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

### Behavior Change 文書（Behavior Change Source）

文書:
- https://developer.android.com/about/versions/17/behavior-changes-all

関連文書:
- https://developer.android.com/reference/android/security/KeyStoreException
- https://developer.android.com/reference/android/security/KeyStoreException#getNumericErrorCode()
- https://developer.android.com/reference/android/security/KeyStoreException#ERROR_TOO_MANY_KEYS
- https://developer.android.com/reference/android/security/KeyStoreException#ERROR_INCORRECT_USAGE
- https://developer.android.com/privacy-and-security/keystore

セクション:
- Per-app keystore limits

ページ種別:
- Behavior changes: all apps

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- 公式文書は Android 17 の `Behavior changes: all apps` ページにこの項目を掲載しており、Android 17 から app が所有できる Android Keystore key 数に limit を enforcement すると説明している。
- ただし、limit 値は app type と targetSdkVersion により分岐する。non-system app targeting Android 17 / API level 37 or higher は 50,000 keys、all other apps は 200,000 keys、system apps は target API level に関係なく 200,000 keys。
- limit 超過時は key creation が `KeyStoreException` で失敗し、exception message に key limit information が含まれる。
- `getNumericErrorCode()` の戻り値は target API level に依存し、targetSdkVersion 37 以上では `ERROR_TOO_MANY_KEYS`、それ以外では `ERROR_INCORRECT_USAGE` と説明されている。
- All apps ページ掲載の OS update impact と、targetSdkVersion 37 以上での stricter limit / numeric error code が混在しているため、AOSP gate evidence なしに primary classification を確定しない。
- local `frameworks-base` に Android 17 AOSP tag がないため、Keystore limit enforcement、system app 判定、targetSdkVersion gate、exception mapping、compat framework entry は未確認である。

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 可能性は高いが条件付き、かつ未検証 | All apps page に掲載され、all other apps に 200,000 key limit があると説明。AOSP gate 未確認。 |
| targetSdkVersion 37 以上が必要か | より厳しい non-system limit と新しい numeric error code では必要、ただし未検証 | 公式文書は non-system apps targeting Android 17+ は 50,000 keys、`getNumericErrorCode()` は `ERROR_TOO_MANY_KEYS` と説明。 |
| 追加の実行時条件があるか | ある | Android Keystore keys を作成し、per-app key ownership limit を超える場合。system / non-system app 判定も関係する。 |
| Compat Change ID が関係するか | 未確認 | Android 17 tag と compat framework evidence が未確認。 |

### 調査日（Investigation Date）

2026-06-15

### 信頼度（Confidence）

- Low

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] targetSdkVersion に関係なく Android 17 の全アプリへ適用
- [ ] Android 17 以上かつ targetSdkVersion 37 以上で適用
- [ ] targetSdkVersion 37 以上かつ追加の実行時条件を満たす場合に適用
- [ ] Mainline / Google Play system update に依存
- [ ] API 追加のみであり、挙動変更ではない
- [x] 未確認 / 追加 evidence が必要

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 であることが前提。AOSP tag 未取得のため実装上の OS gate は未確認。
- targetSdkVersion: 公式文書上、non-system apps targeting Android 17 / API level 37 or higher は 50,000 key limit と `ERROR_TOO_MANY_KEYS`。all other apps は 200,000 key limit と `ERROR_INCORRECT_USAGE`。
- Device/form factor: 公式文書からは条件なし。
- Permission/API/component condition: Android Keystore key creation、`KeyStoreException`、`getNumericErrorCode()`。
- App state/process condition: app が所有 key 数の limit を超えて新規 key を作成しようとする場合。

Compat framework:
- Change ID: 未確認
- 変更名: 未確認
- 既定状態: 未確認
- テスト時に切り替え可能か: 未確認

分類信頼度（Classification confidence）:
- Low

分類根拠（Classification evidence）:
- 公式ドキュメントページ: `behavior-changes-all`
- 検証対象の適用条件文: Android 17 で per-app keystore key ownership limit を enforce。limit 値と numeric error code は app type / targetSdkVersion で分岐。
- AOSP targetSdk gate: 未確認。local `frameworks-base` に `android-17*` tag がない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# エグゼクティブサマリー（Executive Summary）

Android 17 では、Android Keystore が device-wide shared resource であることを踏まえ、app が所有できる key 数に per-app limit が導入される、と公式文書は説明している。limit を超えて key を作成しようとすると `KeyStoreException` で失敗する。

影響条件は targetSdkVersion と app type で分かれる。non-system app が targetSdkVersion 37 以上の場合は 50,000 keys、all other apps は 200,000 keys、system apps は target API level に関係なく 200,000 keys が limit と説明されている。さらに `getNumericErrorCode()` は targetSdkVersion 37 以上で `ERROR_TOO_MANY_KEYS`、それ以外で `ERROR_INCORRECT_USAGE` を返す。

現時点では local `frameworks-base` に Android 17 AOSP tag がないため、Keystore enforcement path、targetSdkVersion gate、system app 判定、exception error code mapping、compat framework entry は未確認である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とし、Android 17 AOSP tag 公開後に再調査する。

---

# 公式ドキュメント確認

## 原文（Statement）

ページタイトル:
- Behavior changes: all apps

ページ URL:
- https://developer.android.com/about/versions/17/behavior-changes-all

ページ種別:
- all apps

セクションタイトル:
- Per-app keystore limits

検証対象の原文:
- Apps should avoid creating excessive numbers of keys in Android Keystore because it is a shared resource for all apps on the device.
- Beginning with Android 17, the system enforces a limit on the number of keys an app can own.
- The limit is 50,000 keys for non-system apps targeting Android 17 / API level 37 or higher.
- The limit is 200,000 keys for all other apps.
- System apps have a 200,000 key limit regardless of target API level.
- If an app attempts to create keys beyond the limit, key creation fails with `KeyStoreException`.
- The exception message contains information about the key limit.
- `getNumericErrorCode()` returns `ERROR_TOO_MANY_KEYS` for apps targeting Android 17 / API level 37 or higher.
- `getNumericErrorCode()` returns `ERROR_INCORRECT_USAGE` for all other apps.

## 解釈（Interpretation）

この変更は、Android Keystore に大量の keys を作成するアプリに対する resource limit である。通常の少数 key 利用では影響しにくいが、per-user / per-device / per-document / per-session などで unbounded に key を作成する設計では、Android 17 以降で key creation failure が顕在化する可能性がある。

分類上の注意点は、All apps ページ掲載でありながら、limit 値と error code が targetSdkVersion 37 で分岐する点である。Android 17 上の targetSdkVersion 36 app も 200,000 key limit の対象になり得る一方、targetSdkVersion 37 以上の non-system app は 50,000 key limit と `ERROR_TOO_MANY_KEYS` の対象になる、と分けて説明する必要がある。

---

# 変更内容（What Changed）

公式文書上の変更点:
- Android 17 で app-owned Android Keystore keys に per-app limit が enforcement される。
- non-system apps targeting Android 17 / API level 37 or higher の limit は 50,000 keys。
- all other apps の limit は 200,000 keys。
- system apps は target API level に関係なく 200,000 keys。
- limit 超過時、key creation は `KeyStoreException` で失敗する。
- exception message には key limit information が含まれる。
- targetSdkVersion 37 以上では `getNumericErrorCode()` が new `ERROR_TOO_MANY_KEYS` を返す。
- all other apps では `getNumericErrorCode()` が `ERROR_INCORRECT_USAGE` を返す。

AOSP で未確認の点:
- per-app key count がどの namespace / UID / user / profile / alias 単位で集計されるか。
- Android Keystore / keystore2 / KeyMint / system server のどこで enforcement されるか。
- system app 判定の条件。
- targetSdkVersion 37 以上で 50,000 limit に入る gate。
- all other apps の 200,000 limit gate。
- `KeyStoreException` message と numeric error code mapping。
- `ERROR_TOO_MANY_KEYS` API surface の追加。
- compat framework Change ID と default state。

## 適用条件（Applicability）

この変更がいつ適用されるかを OS 条件と targetSdkVersion 条件に分けて説明する。

### OS アップデート時の挙動（OS Update Behavior）

- Android 17 に OS アップデートしただけで適用されるか: 公式文書上は Yes / Conditional。Android 17 で per-app key ownership limit を enforce と説明されている。targetSdkVersion 36 など all other apps には 200,000 key limit が適用される可能性がある。AOSP gate 未確認。
- targetSdkVersion に依存しない根拠: All apps page に掲載され、all other apps / system apps にも 200,000 key limit があると説明されている。
- Android 16 以前での挙動: 未確認。公式文書は Android 17 から enforce と説明しているが、AOSP baseline diff は未確認。

### targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- targetSdkVersion 37 以上で適用されるか: 公式文書上、non-system apps targeting Android 17 / API level 37 or higher は stricter 50,000 key limit の対象。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: Unknown。公式文書は Android 17 Behavior Change として説明している。
- opt-out / temporary override の有無: 未確認。公式文書からは app developer が opt out できる仕組みは確認できない。compat framework entry は未確認。

### その他の条件（Other Conditions）

- device/form factor: 公式文書からは条件なし。
- permission: Android Keystore key creation API を利用すること。特定 permission 条件は公式文書からは確認できない。
- API usage: Android Keystore、key generation / import、`KeyStoreException`、`getNumericErrorCode()`。
- manifest attribute: 公式文書からは条件なし。
- component boundary: app process、Android Keystore API、keystore service、key ownership accounting、exception translation にまたがる可能性。

---

# AOSP 調査（AOSP Investigation）

## checkout 状態（Checkout Status）

確認コマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list 'android-17*'
```

結果:
- `frameworks-base` の `status --short` は空で、dirty working tree は確認されなかった。
- `android-16.0.0_r4` tag は存在する。
- `android-17*` tag は local checkout に存在しない。

根拠上の制約:
- Android 17 AOSP tag が local `frameworks-base` にないため、`android-16.0.0_r4` と Android 17 tag の明示的な source diff は実行できない。
- そのため、local working tree や未確定 branch を platform evidence として扱わない。
- 本レポートの AOSP-backed conclusion は Low confidence に留める。

## 関連ファイル（Related Files）

Android 17 AOSP tag 未取得のため、tag diff に基づく related files は未確定。

Android 17 tag 公開後に確認すべき候補:
- `keystore/` または `system/security/keystore2/` 相当の keystore service / key ownership accounting path
- `core/java/android/security/KeyStoreException.java`
- `core/java/android/security/keystore/` 以下の Android Keystore API wrapper
- `frameworks/base/core/api/current.txt` / removed / system API surface
- package / UID / system app 判定を keystore service に渡す path
- compat framework 定義ファイル内の keystore key limit / `ERROR_TOO_MANY_KEYS` 関連 Change ID

Note:
- Android Keystore enforcement は `frameworks-base` 以外の AOSP project にある可能性が高い。Android 17 tag 入手後は、keystore2 / system/security 側も evidence 対象として確認する必要がある。

## 確認したソース文脈（Source Context Reviewed）

AOSP tag diff は未実行。以下は公式文書から見た確認予定の source context であり、AOSP evidence ではない。

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| Keystore key creation / import path | 未確認 | limit 超過時に key creation が `KeyStoreException` で失敗すると公式文書が説明 | app が直接影響を受ける enforcement point |
| Key ownership accounting | 未確認 | app-owned keys に 50,000 / 200,000 の limit があると公式文書が説明 | どの単位で key 数を数えるかが影響範囲を決めるため |
| targetSdkVersion / system app gate | 未確認 | non-system target 37+ は 50,000、all other apps / system apps は 200,000 と公式文書が説明 | OS update impact と targetSdkVersion impact を分ける根拠になるため |
| `KeyStoreException.getNumericErrorCode()` | 未確認 | target 37+ は `ERROR_TOO_MANY_KEYS`、all other apps は `ERROR_INCORRECT_USAGE` と公式文書が説明 | app が error handling で観測する public API |

必須記入項目:
- Entry point / caller: 未確認。想定される entry point は app の Android Keystore key generation / import API -> framework wrapper -> keystore service -> key count check -> exception translation。
- Relevant class or service responsibility: key ownership accounting、key creation limit enforcement、system / non-system app 判定、targetSdkVersion gate、exception error mapping。
- Runtime path from app API / system event to changed code: app が key generation / import を要求 -> keystore service が app-owned key count と limit を比較 -> 超過時に failure -> framework が `KeyStoreException` と message / numeric error code を返す、という path が想定される。AOSP evidence としては未確認。
- Why unrelated code paths were excluded: tag diff 未実行のため、除外判断は未完了。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
| Android 17 tag 未取得のため source diff 未確認 | 公式文書上は added behavior / changed condition と読める | per-app key limit enforcement、targetSdkVersion / app type による limit 分岐、numeric error code 分岐が説明されている | Low |

必須分類:
- Added behavior: 公式文書上、Android 17 で per-app keystore key ownership limit enforcement が追加される。
- Removed behavior: 未確認。
- Changed condition / gate: 公式文書上、non-system target 37+ / all other apps / system apps で limit が分岐する。AOSP gate 未確認。
- Changed default: 未確認。key creation が limit 超過時に失敗する default behavior が導入される可能性があるが、AOSP tag 待ち。
- No behavior change found: 未確認。tag 不在のため「no behavior change」とは判断しない。

## 事実（Evidence）

事実:
- 公式文書は `Per-app keystore limits` を Android 17 `Behavior changes: all apps` ページに掲載している。
- 公式文書は、Android Keystore が device 上の全アプリに共有される resource であるため、過剰な key 作成を避けるべきと説明している。
- 公式文書は、Android 17 から app が所有できる keys の数に system が limit を enforce すると説明している。
- 公式文書は、non-system apps targeting Android 17 / API level 37 or higher の limit を 50,000 keys と説明している。
- 公式文書は、all other apps の limit を 200,000 keys と説明している。
- 公式文書は、system apps は target API level に関係なく 200,000 keys の limit と説明している。
- 公式文書は、limit 超過時に key creation が `KeyStoreException` で失敗すると説明している。
- 公式文書は、exception message に key limit information が含まれると説明している。
- 公式文書は、targetSdkVersion 37 以上では `getNumericErrorCode()` が `ERROR_TOO_MANY_KEYS` を返すと説明している。
- 公式文書は、all other apps では `getNumericErrorCode()` が `ERROR_INCORRECT_USAGE` を返すと説明している。

観察:
- All apps ページ掲載のため、per-app key limit introduction は `OS_UPDATE_ALL_APPS` 候補である。
- ただし、non-system target 37+ では limit が 50,000 keys へ厳しくなり、numeric error code も new `ERROR_TOO_MANY_KEYS` になるため、`TARGET_SDK_37_CONDITIONAL` 相当の側面もある。
- repo の分類は primary label を1つだけ要求しているため、AOSP gate が未確認の現時点では `UNKNOWN_NEEDS_MORE_EVIDENCE` が妥当である。

仮説:
- key limit enforcement は keystore service 側で UID / namespace / app identity 単位の key count を参照して行われる可能性が高い。
- targetSdkVersion 37 以上の stricter limit と `ERROR_TOO_MANY_KEYS` は framework wrapper または keystore service の caller metadata に基づき分岐する可能性がある。
- system app 判定は package manager metadata または keystore access control metadata に基づく可能性がある。

結論:
- 現時点の確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE`。公式文書上は Android 17 all apps の per-app limit と targetSdkVersion 37 conditional の stricter behavior が混在しており、AOSP gate 未取得のため primary を確定しない。
- 顧客向けには、Android 17 で key count limit が導入され、targetSdkVersion 37 以上の non-system app では limit と error handling がより厳しくなる、と分けて説明する。

## 適用ゲート根拠（Applicability Gate Evidence）

- targetSdkVersion gate: 未確認。公式文書上、non-system apps targeting Android 17 / API level 37 or higher は 50,000 keys と `ERROR_TOO_MANY_KEYS`。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。
- @EnabledAfter / @EnabledSince / default state: 未確認。
- Build.VERSION / SDK_INT gate: 未確認。公式文書上は Android 17 introduced。
- DeviceConfig / resources config: 未確認。
- Permission/AppOps gate: 公式文書からは確認できない。
- Manifest/property gate: system / non-system app 判定が関係する可能性はあるが、manifest property としては未確認。
- No gate found: 未確認。AOSP tag 未取得のため gate search 未実行。
- Gate conclusion: 公式文書上は Android 17 all apps + app type + targetSdkVersion + key count condition。AOSP evidence 未取得のため `UNKNOWN_NEEDS_MORE_EVIDENCE`。
- Reasoning from source context: source context は未確認。公式文書の page type と statement のみから一次判断している。

---

# 影響分析（Impact Analysis）

## 影響を受けるアプリ（Affected Apps）

- Android Keystore keys を大量に作成するアプリ。
- per-user、per-account、per-document、per-message、per-session などで key を作成し、削除 / reuse をしないアプリ。
- non-system app で targetSdkVersion 37 以上に上げ、50,000 key limit に近いまたは超える可能性があるアプリ。
- key creation failure を `KeyStoreException` / numeric error code で処理しているアプリ。
- enterprise / security / wallet / encrypted storage / DRM-like workflows などで key 数が増えやすいアプリ。

## 影響を受けないアプリ（Non-Affected Apps）

- Android Keystore を使わないアプリ。
- Keystore keys の数が limit より十分少ないアプリ。
- keys を再利用し、不要 keys を削除しているアプリ。
- system app で 200,000 key limit に到達しない場合。
- ただし、AOSP tag 未取得のため正確な non-affected condition は未確定。

---

# 顧客影響（Customer Impact）

## 影響度（Impact Level）

- 要確認

※ 最終 severity / priority は人間が判断する。このレポートでは確定しない。

## ビジネス影響（Business Impact）

- ユーザー影響: key creation が失敗すると、login credential 作成、encrypted data setup、payment / wallet setup、secure storage initialization などが失敗する可能性がある。
- セキュリティ影響: Keystore が shared resource であるため、過剰な key 作成を抑制し device 全体の resource exhaustion を防ぐ意図がある。
- 開発影響: key lifecycle、alias reuse、key deletion、key count telemetry、`KeyStoreException` handling の見直しが必要になる。
- 運用影響: key creation failure rate、`ERROR_TOO_MANY_KEYS` / `ERROR_INCORRECT_USAGE` の発生、targetSdkVersion 37 rollout 後の failure spike を監視する必要がある。

---

# サービス影響例（Service Impact Examples）

このセクションは、公式文書と未確認の AOSP 調査観点から導いた「起こりうる影響例」を記録する。
特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: per-record encryption key を作成するアプリ

- 対象サービス例: encrypted notes、document vault、enterprise secure storage。
- 影響を受ける実装パターン: document / record ごとに Android Keystore key を作成し、削除しない。
- 発生条件: Android 17、key count が app の limit を超える、特に non-system targetSdkVersion 37+ で 50,000 keys を超える場合。
- ユーザーに見える症状: 新規 document 作成、暗号化保存、初期化が失敗する。
- 開発・運用への影響: key reuse / key wrapping / data key hierarchy / old key cleanup の設計見直しが必要。
- 推奨対応候補: per-record Keystore key を避け、Keystore key で data encryption key を wrap する設計を検討する。
- 根拠: 公式文書は limit 超過時に key creation が `KeyStoreException` で失敗すると説明している。
- Confidence（信頼度）: Low。AOSP enforcement condition 未確認。
- 注意: 実サービスで発生確認した事実ではない。

## 例2（Example 2）: targetSdkVersion 37 rollout 後の error handling 差分

- 対象サービス例: wallet、banking、identity verification、credential storage。
- 影響を受ける実装パターン: key creation failure を numeric error code で分類している。
- 発生条件: Android 17、targetSdkVersion 37 以上、limit 超過時に `getNumericErrorCode()` を参照する場合。
- ユーザーに見える症状: error handling が未対応だと、適切な recovery / cleanup / user messaging ができない。
- 開発・運用への影響: `ERROR_TOO_MANY_KEYS` を明示的に扱い、既存の `ERROR_INCORRECT_USAGE` handling と分ける必要がある。
- 推奨対応候補: `KeyStoreException.getNumericErrorCode()` の handling table に `ERROR_TOO_MANY_KEYS` を追加する。
- 根拠: 公式文書は targetSdkVersion 37 以上では `ERROR_TOO_MANY_KEYS`、それ以外では `ERROR_INCORRECT_USAGE` を返すと説明している。
- Confidence（信頼度）: Low。AOSP exception mapping 未確認。
- 注意: 実サービスで発生確認した事実ではない。

---

# 対応候補（Required Actions）

## 必須対応（Must）

- Android Keystore key creation 箇所を棚卸しする。
- app が作成 / 所有する Keystore key 数を測定できる telemetry または diagnostic を用意する。
- key lifecycle を確認し、不要 key を削除しているか、alias を再利用しているか確認する。
- targetSdkVersion 37 以上で `ERROR_TOO_MANY_KEYS` を handling できるようにする。
- limit 超過時の user-facing recovery、cleanup、retry policy を定義する。

## 推奨対応（Recommended）

- per-record / per-session に Keystore key を増やす設計を避ける。
- 必要に応じて、少数の Keystore master key と data encryption keys の key hierarchy を検討する。
- 50,000 / 200,000 の limit に近づいた場合の alerting を追加する。
- Android 17 / targetSdkVersion 36 と Android 17 / targetSdkVersion 37 で key creation failure behavior を比較する。
- system app / non-system app の扱いが顧客環境に関係する場合は別途確認する。

## 任意対応（Optional）

- app uninstall / account removal / logout / data deletion 時の key cleanup を再確認する。
- long-running enterprise deployment で key count が累積するケースをモデル化する。
- Android 17 AOSP tag 公開後に enforcement path と compat flag を再確認する。

---

# 検証方法（Verification Method）

変更を確認する方法。

## 検証マトリクス（Matrix）

| 端末 OS（Device OS） | targetSdkVersion | Compat flag / test control | 期待挙動（Expected behavior） |
| --- | --- | --- | --- |
| Android 16 | 36 | default | baseline。per-app key limit enforcement の有無と key creation failure behavior を確認する。 |
| Android 17 | 36 | default | 公式文書上、all other apps として 200,000 key limit の対象になる可能性がある。 |
| Android 17 | 37 | default | non-system app では 50,000 key limit、limit 超過時は `ERROR_TOO_MANY_KEYS` と公式文書は説明。 |
| Android 17 | 36 | force-enabled if available | Compat flag 未確認。存在する場合は key limit enforcement 単体の影響を確認する。 |
| Android 17 | 37 | force-disabled if available | Compat flag 未確認。存在する場合は rollback / opt-out 可能性を確認する。 |

## 手順（Steps）

- targetSdk変更: targetSdkVersion 36 / 37 の両方で検証し、limit 値と numeric error code の差分を確認する。
- compat framework command: 未確認。Android 17 tag 公開後に Change ID が存在する場合のみ force-enable / force-disable を検証する。
- テスト方法:
  - non-system app / system app を分ける。
  - targetSdkVersion 36 / 37 を分ける。
  - key count を limit 付近まで増やす test harness を用意する。
  - key creation failure の exception type、message、`getNumericErrorCode()` を記録する。
- 再現手順:
  - test app で Android Keystore key を連続作成する。
  - key count が 50,000 / 200,000 に近づいた時点で creation result を記録する。
  - limit 超過時の `KeyStoreException` message と numeric error code を確認する。
  - targetSdkVersion 36 / 37 で同じ操作を比較する。
- 期待結果:
  - targetSdkVersion 37 以上の non-system app では 50,000 keys を超える key creation が失敗する。
  - all other apps では 200,000 keys が limit として扱われる。
  - targetSdkVersion 37 以上では `ERROR_TOO_MANY_KEYS`、それ以外では `ERROR_INCORRECT_USAGE` が返る。

---

# 結論（Conclusion）

`Per-app keystore limits` は Android 17 all apps ページに掲載されており、Android 17 で app-owned Keystore keys の per-app limit が導入されると公式文書は説明している。一方で、limit 値と numeric error code は targetSdkVersion と app type によって分岐する。

そのため、Android 17 OS update による全体 limit introduction と、targetSdkVersion 37 以上の non-system app に対する stricter 50,000 key limit / `ERROR_TOO_MANY_KEYS` を分けて扱う必要がある。Android 17 AOSP tag が local `frameworks-base` に存在しないため、確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

Android app developer は、Keystore key creation 数を棚卸しし、key lifecycle / cleanup / error handling を見直し、targetSdkVersion 37 更新時には `ERROR_TOO_MANY_KEYS` を扱えるように準備する必要がある。

---

# 人間の判断欄

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- Android 17 AOSP tag 公開後に追加調査が必要

判断理由候補:
- 公式文書上は all apps change と targetSdkVersion 37 conditional behavior が混在している。
- 顧客影響は Android Keystore key 数、non-system / system app、targetSdkVersion、key creation failure handling に依存する。

---

# 参照（References）

## ドキュメント（Documentation）

- https://developer.android.com/about/versions/17/behavior-changes-all
- https://developer.android.com/reference/android/security/KeyStoreException
- https://developer.android.com/reference/android/security/KeyStoreException#getNumericErrorCode()
- https://developer.android.com/reference/android/security/KeyStoreException#ERROR_TOO_MANY_KEYS
- https://developer.android.com/reference/android/security/KeyStoreException#ERROR_INCORRECT_USAGE
- https://developer.android.com/privacy-and-security/keystore

## AOSP

- 未確認。local `frameworks-base` に Android 17 AOSP tag がないため、tag diff による source evidence は未取得。

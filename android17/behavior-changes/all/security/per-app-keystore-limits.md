# Per-app keystore limits

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

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
- https://developer.android.com/privacy-and-security/keystore

セクション:
- Per-app keystore limits

ページ種別:
- Behavior changes: all apps

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- OS_UPDATE_ALL_APPS

公式文書からの初期適用条件判断:
- 公式文書は Android 17 の `Behavior changes: all apps` ページにこの項目を掲載しており、Android 17 から app が所有できる Android Keystore key 数に limit を enforce すると説明している。
- Android 17 / targetSdkVersion 36 など "all other apps" にも 200,000 key limit があるため、OS update 影響を持つ。
- non-system app が targetSdkVersion 37 以上の場合は、より厳しい 50,000 key limit と `ERROR_TOO_MANY_KEYS` numeric error code が関係する。
- Android 17 `frameworks-base` では `KeyStoreException.ERROR_TOO_MANY_KEYS` と keystore service response code 29 / 30 から public error code への mapping が追加されている。

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | Yes / 条件付き | 公式文書は all other apps に 200,000 key limit があると説明。 |
| targetSdkVersion 37 以上が必要か | stricter limit と新 error code では Yes | non-system target 37+ は 50,000 keys。`ERROR_TOO_MANY_KEYS` は target SDK >= 37 向けと AOSP comment にある。 |
| 追加の実行時条件があるか | ある | Android Keystore key を作成し、app-owned key count が limit を超える場合。 |
| Compat Change ID が関係するか | framework 側では未確認 | public error mapping は確認済み。limit enforcement 本体は keystore2 service 側の追加 evidence が必要。 |

### 調査日（Investigation Date）

2026-06-18

### 信頼度（Confidence）

- Medium

理由:
- 公式文書と一致する `ERROR_TOO_MANY_KEYS` API surface と response code mapping は Android 17 tag で確認できた。
- `frameworks-base` checkout には keystore2 service 本体がなく、50,000 / 200,000 の key count enforcement、system app 判定、targetSdkVersion ゲートの実装本体は確認できない。

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [x] OS update / all apps on Android 17 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 37 on Android 17+
- [ ] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [ ] Unknown / 追加根拠が必要

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 以上。
- targetSdkVersion: targetSdkVersion に関係なく 200,000 key limit の対象になり得る。non-system targetSdkVersion 37 以上では 50,000 key limit と `ERROR_TOO_MANY_KEYS` が関係する。
- Device/form factor: 公式文書からは条件なし。
- Permission/API/component condition: Android Keystore key creation、`KeyStoreException`、`getNumericErrorCode()`。
- App state/process condition: app-owned key count が limit に達した状態で新規 key を作成しようとする場合。

Compat framework:
- Change ID: framework API 側では確認できず
- 変更名: なし
- 既定状態: 未確認
- テスト時の切り替え可否: 未確認

分類信頼度（Classification confidence）:
- Medium

---

# エグゼクティブサマリー

Android 17 では、Android Keystore が device-wide shared resource であることを踏まえ、app が所有できる key 数に per-app limit が導入される、と公式文書は説明している。limit を超えて key を作成しようとすると `KeyStoreException` で失敗する。

影響条件は targetSdkVersion と app type で分かれる。non-system app が targetSdkVersion 37 以上の場合は 50,000 keys、all other apps は 200,000 keys、system apps は target API level に関係なく 200,000 keys が limit と説明されている。さらに `getNumericErrorCode()` は targetSdkVersion 37 以上で `ERROR_TOO_MANY_KEYS`、それ以外で `ERROR_INCORRECT_USAGE` を返す。

Android 17 AOSP tag では、`KeyStoreException.ERROR_TOO_MANY_KEYS` と keystore service response code `TOO_MANY_APP_KEYS` / `TOO_MANY_APP_KEYS_SDK37` 相当の mapping が追加されている。ただし、この checkout では keystore2 service の enforcement 本体は確認できないため、confidence は Medium とする。

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
- Beginning with Android 17, the system enforces a limit on the number of keys an app can own.
- The limit is 50,000 keys for non-system apps targeting Android 17 / API level 37 or higher.
- The limit is 200,000 keys for all other apps.
- System apps have a 200,000 key limit regardless of target API level.
- If an app attempts to create keys beyond the limit, key creation fails with `KeyStoreException`.
- `getNumericErrorCode()` returns `ERROR_TOO_MANY_KEYS` for apps targeting Android 17 / API level 37 or higher.
- `getNumericErrorCode()` returns `ERROR_INCORRECT_USAGE` for all other apps.

## 解釈（Interpretation）

この変更は、Android Keystore に大量の keys を作成するアプリに対する resource limit である。通常の少数 key 利用では影響しにくいが、record / account / session ごとに unbounded に key を作成する設計では、Android 17 以降で key creation failure が顕在化する可能性がある。

分類上は、OS update で 200,000 key limit が導入される all-apps 影響と、targetSdkVersion 37 以上の non-system app に対する 50,000 key limit / `ERROR_TOO_MANY_KEYS` を分けて説明する必要がある。

---

# AOSP 調査（AOSP Investigation）

## チェックアウト状態

確認コマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list android-17.0.0_r1
```

結果:
- `frameworks-base` の `status --short` は空で、未コミット変更 は確認されなかった。
- `android-16.0.0_r4` tag は存在する。
- `android-17.0.0_r1` tag は存在する。

## 関連ファイル（Related Files）

確認した主なファイル:
- `keystore/java/android/security/KeyStoreException.java`
- `keystore/java/android/security/KeyStore2.java`
- `keystore/java/android/security/KeyStoreSecurityLevel.java`
- `core/api/current.txt`

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `KeyStoreException.ERROR_TOO_MANY_KEYS` | なし | `@FlaggedApi(android.security.keystore2.Flags.FLAG_LIMIT_KEYS_PER_UID)` 付きで追加。comment は target SDK >= 37 の apps にのみ emitted と説明 | 公式文書の new numeric error code と一致 |
| `KeyStoreException.getNumericErrorCode()` | service error を public error code に変換 | `ResponseCode.TOO_MANY_APP_KEYS` 相当の 29 を `ERROR_INCORRECT_USAGE`、`TOO_MANY_APP_KEYS_SDK37` 相当の 30 を `ERROR_TOO_MANY_KEYS` に mapping | targetSdkVersion による numeric error code 差分を支える |
| `KeyStore2.getKeyStoreException()` | keystore service positive error code を `KeyStoreException` に変換 | unknown positive response code は `KeyStoreException(errorCode, String.valueOf(errorCode), serviceErrorMessage)` として返す | keystore2 service から返る limit error が framework exception へ伝播する入口 |
| `KeyStoreSecurityLevel` | key generation / import の remote request を keystore service に送る | service error は `KeyStore2.getKeyStoreException()` で framework exception に変換される | key creation failure が `KeyStoreException` になる path |

## 実装 path（Runtime Path）

1. app が Android Keystore 経由で key generation / import を行う。
2. keystore2 service 側で app-owned key count が limit を超えると、positive response code を返すと推定される。
3. framework keystore layer は `KeyStore2.getKeyStoreException()` を通じて `KeyStoreException` を作る。
4. `KeyStoreException.getNumericErrorCode()` は response code 29 を `ERROR_INCORRECT_USAGE`、response code 30 を `ERROR_TOO_MANY_KEYS` として公開する。
5. targetSdkVersion 37 以上の app では `ERROR_TOO_MANY_KEYS` を処理対象にする必要がある。

## 差分確認（Diff Review）

確認コマンド:

```bash
git -C frameworks-base diff android-16.0.0_r4 android-17.0.0_r1 -- \
  keystore/java/android/security/KeyStoreException.java \
  keystore/java/android/security/KeyStore2.java \
  keystore/java/android/security/KeyStoreSecurityLevel.java \
  core/api/current.txt
```

確認結果:
- `KeyStoreException.ERROR_TOO_MANY_KEYS = 18` が追加された。
- `core/api/current.txt` に `@FlaggedApi("android.security.keystore2.limit_keys_per_uid") public static final int ERROR_TOO_MANY_KEYS` が追加された。
- `KeyStoreException` の error mapping に response code 29 -> `ERROR_INCORRECT_USAGE`、response code 30 -> `ERROR_TOO_MANY_KEYS` が追加された。
- comment には response code 名がまだ利用可能でないため numeric literal を使う TODO がある。

差分解釈:
- Source diff type: added API surface / changed error-code mapping。
- Behavior Change を支える evidence: limit 超過時の public error code 差分が framework API に追加されている。
- 分類を支える evidence: Android 17 all-apps 文書は targetSdkVersion に関係なく key limit が導入されると説明し、AOSP は targetSdkVersion 37 以上向けの `ERROR_TOO_MANY_KEYS` mapping を追加している。

## 関連しない / 除外した path

- `KeymasterDefs.KM_ERROR_KEY_MAX_OPS_EXCEEDED` は key operation count に関する既存 error であり、per-app key ownership limit とは別。
- `FEATURE_KEYSTORE_LIMITED_USE_KEY` / `setMaxUsageCount()` は key 使用回数制限であり、app-owned key 数 limit とは別。
- `keystore2` service 本体はこの checkout に含まれないため、50,000 / 200,000 の enforcement 実装 evidence としては扱わない。

---

# 適用条件（Applicability）

## OS アップデート時の挙動（OS Update Behavior）

- Android 17 に OS アップデートしただけで適用されるか: Yes / Conditional。公式文書上、all other apps には 200,000 key limit がある。
- targetSdkVersion に依存しない根拠: All apps page に掲載され、targetSdkVersion 37 未満も "all other apps" として limit 対象になる。
- Android 16 以前での挙動: 公式文書は Android 17 から limit enforcement と説明している。AOSP framework API には Android 17 で new error mapping が追加された。

## targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- targetSdkVersion 37 以上で適用されるか: non-system app では stricter 50,000 key limit と `ERROR_TOO_MANY_KEYS` が関係する。
- Android 17 / targetSdkVersion 36: 200,000 key limit、limit 超過時は `ERROR_INCORRECT_USAGE` と公式文書は説明。
- Android 17 / targetSdkVersion 37: non-system app は 50,000 key limit、limit 超過時は `ERROR_TOO_MANY_KEYS`。
- opt-out / temporary override の有無: 公式文書に app developer 向け opt-out は記載されていない。

## その他の条件（Other Conditions）

- device/form factor: 公式文書からは条件なし。
- app type: system apps は target API level に関係なく 200,000 key limit。
- API usage: Android Keystore、key generation / import、`KeyStoreException`、`getNumericErrorCode()`。
- app state: app-owned key count が 50,000 または 200,000 の limit に近い / 超える場合。

---

# 開発者影響

影響を受ける可能性がある app:
- Android Keystore keys を大量に作成するアプリ。
- secure storage、wallet、credential、encrypted document、enterprise security、per-record encryption などで key 数が増え続ける設計のアプリ。

影響が限定的な app:
- Android Keystore を使わないアプリ。
- Keystore key count が十分少ないアプリ。
- key lifecycle / cleanup / reuse を適切に実装しているアプリ。

ユーザー影響:
- limit 超過時、新規 key creation が失敗し、認証、暗号化保存、証明書発行、credential 登録などが失敗する可能性がある。

---

# サービス影響例

このセクションは、公式文書と AOSP 根拠から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: 1Password / Bitwarden / enterprise password vault の credential 保存

- 具体サービス例: 1Password、Bitwarden、Keeper、企業向け password vault / credential manager。
- 影響を受ける実装パターン: account、vault item、device enrollment、credential record ごとに Android Keystore key を無制限に作成し、削除・再利用しない設計。
- 発生条件: Android 17 上で app-owned key count が targetSdkVersion / app type ごとの limit に到達する場合。
- ユーザーに見える症状: 新しい credential 登録、vault item 保存、device key 発行が失敗する可能性。
- 技術的に起きていること: Keystore key creation が limit 超過で `KeyStoreException` になり、targetSdkVersion 37 以上の non-system app では `ERROR_TOO_MANY_KEYS` が返る。
- 推奨対応シーン: secure storage、credential sync、device enrollment、per-record encryption の key lifecycle review。
- 検証観点: app-owned key count、key deletion / rotation / reuse、targetSdkVersion 36 / 37、numeric error code handling。
- 根拠: 公式文書の 50,000 / 200,000 key limit、`KeyStoreException.ERROR_TOO_MANY_KEYS` API surface。
- Confidence（信頼度）: Medium。keystore2 service 側 enforcement 実装は追加確認が必要。
- 注意: 上記サービスで発生確認した事実ではない。通常の key reuse 設計では影響しにくい。

## 例2（Example 2）: E2EE メッセージ / ノート / 文書アプリの per-record encryption

- 具体サービス例: Signal、WhatsApp、Standard Notes、Proton Drive のような暗号化データを扱うアプリ。
- 影響を受ける実装パターン: conversation、file、note、attachment、session ごとに Android Keystore key を作り続ける独自暗号化設計。
- 発生条件: 長期間利用、複数アカウント、同期・再登録の繰り返しで key count が増え、limit を超える場合。
- ユーザーに見える症状: 新規チャット / ファイル / ノートの暗号化保存が失敗する、再登録や復元が進まない可能性。
- 技術的に起きていること: app-owned key count limit により key generation / import が拒否される。
- 推奨対応シーン: per-item key strategy、cleanup job、logout / account deletion / migration 時の key deletion。
- 検証観点: synthetic large-account test、key alias naming、orphan key cleanup、error fallback。
- 根拠: 公式文書の per-app key ownership limit と report の API usage / app state condition。
- Confidence（信頼度）: Medium。
- 注意: 上記サービスで発生確認した事実ではない。暗号化設計はサービスごとに異なるため個別確認が必要。

---

# 推奨対応候補（Recommended Action Candidates）

開発者向け対応候補:
- Keystore key creation 箇所と app-owned key count を棚卸しする。
- per-record / per-session など unbounded な key creation を避け、key reuse / rotation / cleanup を設計する。
- targetSdkVersion 37 以上では `KeyStoreException.ERROR_TOO_MANY_KEYS` を handling する。
- targetSdkVersion 36 以前も `ERROR_INCORRECT_USAGE` と message を確認し、limit 超過を識別できるようにする。
- key deletion / migration / cleanup の運用を用意する。

---

# テスト観点（Test Matrix）

| 端末 OS | targetSdkVersion | 条件 | 期待挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | 大量 key creation | baseline。limit enforcement の有無を確認する。 |
| Android 17 | 36 | app-owned key count が 200,000 超 | key creation が `KeyStoreException` で失敗し、numeric error は `ERROR_INCORRECT_USAGE` の想定。 |
| Android 17 | 37 | non-system app / key count が 50,000 超 | key creation が `KeyStoreException` で失敗し、numeric error は `ERROR_TOO_MANY_KEYS` の想定。 |
| Android 17 | 37 | system app / key count が 200,000 超 | system app limit は 200,000 と公式文書は説明。 |

---

# 顧客向け説明（Customer-facing Explanation）

Android 17 では、Android Keystore に app ごとの key ownership limit が導入されます。limit を超えて key を作成しようとすると `KeyStoreException` で失敗します。通常の少数 key 利用では影響しにくい一方、record / account / session ごとに Keystore key を増やし続ける設計では、key creation failure が発生する可能性があります。

targetSdkVersion 37 以上の non-system app は 50,000 key limit と説明されており、limit 超過時の `getNumericErrorCode()` は `ERROR_TOO_MANY_KEYS` になります。targetSdkVersion 36 など all other apps では 200,000 key limit と `ERROR_INCORRECT_USAGE` が説明されているため、OS update 影響と targetSdkVersion 37 影響を分けて検証してください。

---

# 未解決事項（Open Questions）

- keystore2 service 側の 50,000 / 200,000 key count enforcement 実装。
- app-owned key count の集計単位。
- system app 判定の exact condition。
- `limit_keys_per_uid` feature flag の release default。

---

# 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断

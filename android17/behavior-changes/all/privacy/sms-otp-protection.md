# SMS OTP protection

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
- https://developer.android.com/reference/android/provider/Telephony.Sms.Intents#SMS_RECEIVED_ACTION
- https://developer.android.com/reference/android/provider/Telephony.Sms
- https://developer.android.com/identity/sms-retriever
- https://developers.google.com/identity/sms-retriever/user-consent/overview
- https://developer.android.com/about/versions/17/behavior-changes-17#sms-otp-protection

セクション:
- SMS OTP protection

ページ種別:
- Behavior changes: all apps

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- OS_UPDATE_ALL_APPS

公式文書からの初期適用条件判断:
- 公式文書は Android 17 の `Behavior changes: all apps` ページにこの項目を掲載している。
- 本項目では、Android 17 から WebOTP format messages にも SMS OTP protection が適用される、と説明している。
- WebOTP 側の保護は、公式文書上 targetSdkVersion 条件を持たない。
- Android 17 AOSP evidence では WebOTP OTP subtype、TextClassifier entity、domain verification query API、OTP trusted package 判定 API が追加されている。
- targetSdkVersion 37 以上で standard SMS messages にも保護が拡張される点は、`behavior-changes-17` 側の別項目として分離する。

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | Yes / 条件付き | `behavior-changes-all` 掲載項目。AOSP に WebOTP subtype / trusted package / domain verification API が追加されている。 |
| targetSdkVersion 37 以上が必要か | WebOTP protection では No | all apps 文書に targetSdkVersion 条件はない。standard SMS 拡張は別項目。 |
| 追加の実行時条件があるか | ある | SMS read permission、WebOTP format message、intended recipient ではないこと、domain verification、3 時間以内、exempted app ではないこと。 |
| Compat Change ID が関係するか | WebOTP 側では確認できず | standard/generic SMS 側には `SmsManager.FILTER_GENERIC_OTP = 437043173L` があるが、これは targetSdkVersion 37 側の別項目。 |

### 調査日（Investigation Date）

2026-06-18

### 信頼度（Confidence）

- Medium

理由:
- 公式文書と一致する WebOTP / domain verification / trusted packages の AOSP API surface は確認できた。
- `frameworks-base` 上で targetSdkVersion gate は WebOTP all-apps path には見つからない。
- ただし `SMS_RECEIVED_ACTION` broadcast withholding、SMS provider query filtering、3 時間 delay の実装本体は Telephony provider / module 側にまたがるため、この checkout だけでは完全な runtime enforcement を確認できない。

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
- targetSdkVersion: WebOTP format messages への追加保護では条件なし。
- Device/form factor: 公式文書からは device / form factor 条件は確認できない。
- Permission/API/component condition: app が SMS messages を読む permission を持つこと、WebOTP format message、intended recipient ではないこと、domain verification により recipient が判定されること、`SMS_RECEIVED_ACTION` broadcast または SMS provider query 経路を使うこと。
- App state/process condition: SMS 受信後 3 時間以内に、対象 app が WebOTP message を programmatically read しようとする場合。

Compat framework:
- Change ID: WebOTP all-apps 側では確認できず
- 変更名: なし
- 既定状態: compat framework では確認できず
- 補足: `SmsManager.FILTER_GENERIC_OTP = 437043173L` は `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.CINNAMON_BUN)` で、standard/generic SMS protection の targetSdkVersion 37 側に関係する evidence として扱う。

分類信頼度（Classification confidence）:
- Medium

---

# エグゼクティブサマリー（Executive Summary）

Android 17 では、SMS OTP protection が WebOTP format messages にも拡張される。SMS を読む permission を持つアプリであっても、domain verification で WebOTP message の intended recipient と判定されない場合、受信後 3 時間はその message にアクセスできない、と公式文書は説明している。

Android 17 AOSP では、`TextClassifier.TYPE_SMS_WEB_OTP`、`Telephony.Sms.OTP_SUBTYPE_WEB_OTP`、`DomainVerificationManager.getVerifiedOwnersForDomain()`、`SmsManager.getSmsOtpTrustedPackages()` / `isAppTrustedForSmsOtp()` など、WebOTP の識別、domain verification、trusted package 判定に必要な framework API surface が追加されている。

ただし、broadcast withholding、SMS provider database query filtering、3 時間 delay の enforcement 本体は Telephony provider / module 側にまたがる。今回の `frameworks-base` 調査では API と判定補助 path までは確認できたが、runtime enforcement 全体は未完了のため confidence は Medium とする。

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
- SMS OTP protection

検証対象の原文:
- Beginning with Android 17, Android is expanding its protection for SMS messages containing one-time passwords.
- In previous versions, protection was primarily focused on SMS Retriever format messages.
- Beginning with Android 17, protection is also applied to WebOTP format messages.
- If an app can read SMS messages but is not the intended recipient of a WebOTP message, as determined by domain verification, the message is not accessible to the app until three hours after receipt.
- During the delay, `SMS_RECEIVED_ACTION` broadcast is withheld and SMS provider database queries are filtered.
- This change applies to all apps, regardless of target API level.
- Certain apps, such as the default SMS assistant app and connected device companion apps, are exempted.
- Apps that rely on reading SMS messages for OTP extraction should transition to SMS Retriever or SMS User Consent APIs.
- If an app targets Android 17 / API level 37 or higher, the protection is also extended to standard SMS messages; that targetSdkVersion 37 behavior is documented separately.

## 解釈（Interpretation）

この変更は、OTP を含む SMS をアプリが直接読む経路を制限する privacy / security behavior change である。Android 17 では、従来の SMS Retriever format message に加えて WebOTP format message も、intended recipient ではないアプリから 3 時間隠される。

All apps ページ上の変更として WebOTP format messages への保護が targetSdkVersion に依存しない点が重要である。Android 17 / targetSdkVersion 36 のままでも、SMS read permission を持ち、WebOTP message の intended recipient ではないアプリは、3 時間以内に broadcast / provider query から message を読めない可能性がある。

---

# AOSP 調査（AOSP Investigation）

## checkout 状態（Checkout Status）

確認コマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list android-17.0.0_r1
```

結果:
- `frameworks-base` の `status --short` は空で、dirty working tree は確認されなかった。
- `android-16.0.0_r4` tag は存在する。
- `android-17.0.0_r1` tag は存在する。

## 関連ファイル（Related Files）

確認した主なファイル:
- `core/java/android/view/textclassifier/TextClassifier.java`
- `core/java/android/provider/Telephony.java`
- `core/java/android/content/pm/verify/domain/DomainVerificationManager.java`
- `core/res/AndroidManifest.xml`
- `core/java/android/view/flags/view_flags.aconfig`
- `telephony/java/android/telephony/SmsManager.java`
- `core/java/android/app/AppOpsManager.java`

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `TextClassifier.TYPE_SMS_WEB_OTP` | なし | `@FlaggedApi(android.view.flags.Flags.FLAG_REDACT_WEB_OTP_SMS_API)` 付きで `sms_web_otp` entity type が追加 | WebOTP SMS を OTP subtype として分類する framework API surface |
| `TextClassifier.EXTRA_OTP_TRUSTED_PACKAGES` | なし | OTP を受信 / view できる trusted packages の extra が追加 | classifier が intended / trusted recipient 情報を返すための surface |
| `Telephony.Sms.OTP_SUBTYPE_WEB_OTP` | なし | `OTP_SUBTYPE_WEB_OTP = 2 << OTP_SUBTYPE_SHIFT` が追加 | SMS provider の OTP metadata に WebOTP subtype を表現できる |
| `Telephony.ReadRestriction.appendReadRestrictionToQuery()` | なし | caller が restricted messages を読めない場合、`read_restriction` bit を使って query に filter を追加できる helper が追加 | 公式文書の provider query filtering と対応する framework helper。ただし OTP 専用 enforcement 本体は provider 側確認が必要 |
| `DomainVerificationManager.getVerifiedOwnersForDomain()` | なし | `QUERY_DOMAIN_VERIFICATION` permission 下で verified owners を返す SystemApi が追加 | 公式文書の「domain verification により intended recipient を判定」に対応する API |
| `AndroidManifest.xml` / `QUERY_DOMAIN_VERIFICATION` | なし | `signature|module` permission として追加され、ExtService / internal packages 用と説明される | domain verification query を内部 / module component に限定する gate |
| `SmsManager.getSmsOtpTrustedPackages()` | 既存の OTP trusted package 判定がある | system apps、role holders、`RECEIVE_SENSITIVE_NOTIFICATIONS` holders、carrier privileged apps、companion device associations、`OP_READ_OTP_SMS` allowed packages を trusted として集約 | 公式文書の exempted apps / connected device companion apps と対応する判定 surface |
| `SmsManager.isAppTrustedForSmsOtp()` | 既存の per-app trusted 判定がある | package 単位で OTP SMS を読める trusted app かを判定 | broadcast / provider 側 enforcement が呼び出す候補になる trusted-app helper |
| `AppOpsManager.OP_READ_OTP_SMS` | あり | OTP SMS を読むための app op として利用される | trusted package 判定で app op exemption を表現する |

## 実装 path（Runtime Path）

公式文書と AOSP evidence から推定できる path:
1. SMS が受信され、TextClassifier / Telephony 側で OTP かつ WebOTP subtype と判定される。
2. WebOTP message の domain に対して `DomainVerificationManager.getVerifiedOwnersForDomain()` などで verified owner / intended recipient が判定される。
3. `SmsManager.getSmsOtpTrustedPackages()` / `isAppTrustedForSmsOtp()` により、default SMS / assistant / companion device / carrier privileged / app op allowed などの trusted packages が判定される。
4. intended recipient または trusted package ではない app について、受信後 3 時間は `SMS_RECEIVED_ACTION` broadcast が withheld され、SMS provider query が filtered される。
5. 3 時間後、対象 message が利用可能になる。

上記のうち 1-3 の framework API surface は確認済み。4-5 の exact enforcement は Telephony provider / module 側の追加調査が必要。

## 差分確認（Diff Review）

確認コマンド:

```bash
git -C frameworks-base diff android-16.0.0_r4 android-17.0.0_r1 -- \
  core/java/android/view/textclassifier/TextClassifier.java \
  core/java/android/provider/Telephony.java \
  core/java/android/content/pm/verify/domain/DomainVerificationManager.java \
  core/res/AndroidManifest.xml \
  telephony/java/android/telephony/SmsManager.java
```

確認結果:
- `TextClassifier.TYPE_SMS_WEB_OTP` と `EXTRA_OTP_TRUSTED_PACKAGES` が追加された。
- `Telephony.Sms.OTP_SUBTYPE_WEB_OTP` が追加された。
- `Telephony.ReadRestriction` helper が追加され、restricted message を読めない caller の query に filter を追加できるようになった。
- `DomainVerificationManager.getVerifiedOwnersForDomain()` と `QUERY_DOMAIN_VERIFICATION` permission が追加された。
- `SmsManager` には trusted OTP SMS package 判定があり、system apps、role holders、`RECEIVE_SENSITIVE_NOTIFICATIONS` holders、carrier privileged apps、companion device associations、`OP_READ_OTP_SMS` allowed packages を扱う。

差分解釈:
- Source diff type: added behavior / added API surface / changed condition の evidence。
- Behavior Change を支える evidence: WebOTP subtype、domain verification、trusted package 判定、provider query filtering helper が Android 17 tag に存在する。
- 分類を支える evidence: WebOTP all-apps path に targetSdkVersion gate は確認できず、公式文書も all apps / regardless of target API level と説明している。

## 関連しない / 除外した path

- `SmsManager.FILTER_GENERIC_OTP = 437043173L` は `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.CINNAMON_BUN)` の compat ChangeId であり、standard/generic SMS protection の targetSdkVersion 37 側に関係する。本 all-apps WebOTP 項目とは分離する。
- `Telephony.ReadRestriction` は RCS restricted message 用の API も含むため、すべてを WebOTP evidence として扱わない。本項目では provider query filtering の helper として関係する範囲だけを参照する。

---

# 適用条件（Applicability）

## OS アップデート時の挙動（OS Update Behavior）

- Android 17 に OS アップデートしただけで適用されるか: Yes / Conditional。
- targetSdkVersion に依存しない根拠: 公式文書は all apps ページに掲載し、WebOTP protection は target API level に関係なく適用されると説明している。確認済み WebOTP API surface に targetSdkVersion gate は見つからない。
- Android 16 以前での挙動: 公式文書は、以前は主に SMS Retriever format messages が保護対象だったと説明している。Android 17 diff では WebOTP subtype / domain verification query / trusted package extra が追加されている。

## targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- targetSdkVersion 37 以上で適用されるか: WebOTP protection では targetSdkVersion 37 は必要条件ではない。
- Android 17 / targetSdkVersion 36: WebOTP format message について、intended recipient / trusted app でなければ 3 時間 access できない想定。
- Android 17 / targetSdkVersion 37: WebOTP protection に加えて、standard/generic SMS protection の別 Behavior Change も確認が必要。
- opt-out / temporary override の有無: 一般 app 向け opt-out は確認できない。exempted app categories と trusted package 判定がある。

## その他の条件（Other Conditions）

- device/form factor: 公式文書からは条件なし。
- permission: app が SMS messages を読む permission を持つ場合に関係する。SMS permission がなければ従来通り SMS は読めない。
- API usage: `SMS_RECEIVED_ACTION` broadcast、`Telephony.Sms` provider query、WebOTP format message、SMS Retriever API、SMS User Consent API。
- exemption: system apps、role holders、`RECEIVE_SENSITIVE_NOTIFICATIONS` holders、carrier privileged apps、companion device associated apps、`OP_READ_OTP_SMS` allowed packages などが trusted 判定に含まれる。

---

# 開発者影響（Developer Impact）

影響を受ける可能性がある app:
- SMS inbox、SMS provider、`SMS_RECEIVED_ACTION` broadcast から OTP を直接抽出しているアプリ。
- ログイン、サインアップ、本人確認、決済、アカウント復旧などで OTP 自動入力を行うアプリ。
- WebOTP format message を受信するが、その domain の intended recipient ではないアプリ。

影響が限定的な app:
- SMS を直接読まないアプリ。
- SMS Retriever API または SMS User Consent API に移行済みのアプリ。
- WebOTP message の intended recipient として domain verification で判定されるアプリ。
- trusted / exempted category に該当するシステム、role、companion、carrier privileged などのアプリ。

ユーザー影響:
- OTP 自動入力が 3 時間以内に動作せず、手入力が必要になる可能性がある。
- SMS inbox から直接 OTP を読んでいた補助アプリや認証連携が失敗する可能性がある。

---

# 推奨対応候補（Recommended Action Candidates）

開発者向け対応候補:
- SMS を直接読んで OTP を抽出している箇所、`SMS_RECEIVED_ACTION` receiver、`Telephony.Sms` provider query の利用を棚卸しする。
- SMS Retriever API または SMS User Consent API へ移行する。
- WebOTP / SMS Retriever / standard SMS format を分けて Android 17 で検証する。
- WebOTP を使う場合、domain verification と intended recipient の状態を確認する。
- targetSdkVersion 37 以上では standard SMS protection の別項目も合わせて検証する。

---

# テスト観点（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 条件 | 期待挙動（Expected behavior） |
| --- | --- | --- | --- |
| Android 16 | 36 | WebOTP format message / SMS read app | baseline。公式文書上、主保護対象は SMS Retriever format messages。 |
| Android 17 | 36 | WebOTP format message / intended recipient ではない / 受信後 3 時間以内 | `SMS_RECEIVED_ACTION` broadcast withheld、SMS provider query filtered の想定。 |
| Android 17 | 37 | WebOTP format message / intended recipient ではない / 受信後 3 時間以内 | targetSdkVersion 36 と同じ WebOTP protection に加え、standard SMS protection も別途確認する。 |
| Android 17 | 37 | SMS Retriever API または SMS User Consent API 使用 | 直接 SMS read に依存しない flow として検証する。 |

---

# 顧客向け説明（Customer-facing Explanation）

Android 17 では、OTP を含む SMS の保護が WebOTP format messages にも拡張されます。SMS を読む permission があるアプリでも、domain verification でその WebOTP message の intended recipient ではないと判断される場合、受信後 3 時間は `SMS_RECEIVED_ACTION` broadcast が配信されず、SMS provider query でも対象 message が filtered されます。

OTP を SMS 本文から直接抽出している実装は、ログインや本人確認の自動入力に影響する可能性があります。継続して OTP 取得を行う場合は、SMS Retriever API または SMS User Consent API への移行を検討してください。targetSdkVersion 37 以上では standard SMS messages にも別の保護が適用されるため、WebOTP と standard SMS を分けて検証する必要があります。

---

# 未解決事項（Open Questions）

- `SMS_RECEIVED_ACTION` broadcast withholding の正確な実装箇所。
- SMS provider query filtering と 3 時間 delay の exact implementation。
- WebOTP domain parser / TextClassifier model 側の exact behavior。
- Telephony provider / module 側の release flag default。

---

# 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断

# SMS OTP protection - 1ページ要約

## 対象

Android 17 Behavior Change

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

## 適用条件

- 主分類（Primary classification）: OS_UPDATE_ALL_APPS
- OS アップデート / 全アプリ（OS update / all apps）: 該当。`behavior-changes-all` ページに掲載され、WebOTP format messages への追加保護は target API level に関係なく適用されると説明されている。
- targetSdkVersion 37 以上: WebOTP protection では不要。standard SMS protection は targetSdkVersion 37+ の別項目。
- その他の必須条件（Other required conditions）: SMS read permission、WebOTP format message、intended recipient ではないこと、domain verification、受信後 3 時間以内、exempted app ではないこと。
- Compat Change ID: WebOTP all-apps 側では確認できず
- Compat default state: compat framework では確認できず
- Confidence: Medium

## 早見マトリクス

| シナリオ | 影響 |
| --- | --- |
| Android 17 / targetSdkVersion 36 | WebOTP format message は intended recipient ではない app から 3 時間 access できない想定。 |
| Android 17 / targetSdkVersion 37 | WebOTP protection に加え、standard SMS protection の別条件も発生する可能性がある。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | `SMS_RECEIVED_ACTION` broadcast withheld、SMS provider query filtered、3 時間後に利用可能と公式文書は説明。 |

## 要約

Android 17 では、SMS OTP protection が WebOTP format messages にも拡張される。SMS を読む permission があるアプリでも、domain verification 上の intended recipient ではない場合、受信後 3 時間は broadcast / provider query から message を利用できない。

AOSP では `TextClassifier.TYPE_SMS_WEB_OTP`、`Telephony.Sms.OTP_SUBTYPE_WEB_OTP`、`DomainVerificationManager.getVerifiedOwnersForDomain()`、`SmsManager.getSmsOtpTrustedPackages()` / `isAppTrustedForSmsOtp()` など、WebOTP の識別、domain verification、trusted package 判定に必要な framework API surface が追加されている。

## 顧客影響

- SMS 本文や provider query から OTP を直接抽出しているログイン / 本人確認 flow が失敗する可能性がある。
- 3 時間以内に OTP 自動入力できず、ユーザーが手入力を求められる可能性がある。
- Android 17 / targetSdkVersion 37 では standard SMS protection も別途確認が必要。

## 影響対象（Who Is Affected）

- 対象アプリ: SMS inbox、SMS provider、`SMS_RECEIVED_ACTION` broadcast から OTP を直接抽出しているアプリ。
- 対象機能: ログイン、サインアップ、本人確認、決済、アカウント復旧などの OTP 自動入力。
- 対象条件: Android 17、WebOTP format message、SMS read permission、intended recipient ではないこと、exempted app ではないこと、受信後 3 時間以内。

## 対応要否

- 必須対応: SMS を直接読んで OTP を抽出している箇所、`SMS_RECEIVED_ACTION` receiver、`Telephony.Sms` provider query の利用を棚卸しする。
- 推奨対応: SMS Retriever API または SMS User Consent API へ移行し、WebOTP / SMS Retriever / standard SMS format を分けて Android 17 で検証する。
- 不要: SMS を直接読まないアプリ、または公式 API に移行済みの OTP flow では直接影響は限定的。ただし認証基盤の SMS format は確認する。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 36 | Android 16 baseline。公式文書上、主保護対象は SMS Retriever format messages。 |
| Android 17 | 36 | WebOTP format message は intended recipient ではない app から 3 時間 access できない想定。 |
| Android 17 | 37 | WebOTP protection と standard SMS protection の両方を分けて確認する。 |

## 顧客向け説明

Android 17 では、OTP を含む SMS の保護が WebOTP format messages にも拡張されます。SMS を読む permission があるアプリでも、domain verification でその WebOTP message の intended recipient ではないと判断される場合、受信後 3 時間は `SMS_RECEIVED_ACTION` broadcast が配信されず、SMS provider query でも対象 message が filtered されます。

OTP を SMS 本文から直接抽出している実装は、SMS Retriever API または SMS User Consent API への移行を検討してください。

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-all
- 検証対象の原文: Android 17 から WebOTP format messages にも SMS OTP protection が適用され、intended recipient ではない app では受信後 3 時間まで access できない。
- AOSP ファイル: `core/java/android/view/textclassifier/TextClassifier.java`, `core/java/android/provider/Telephony.java`, `core/java/android/content/pm/verify/domain/DomainVerificationManager.java`, `telephony/java/android/telephony/SmsManager.java`, `core/res/AndroidManifest.xml`
- AOSP ソース文脈: WebOTP subtype、trusted package extra、domain verification query、OTP trusted package 判定、provider query filtering helper を確認。
- 差分解釈: added behavior / added API surface / changed condition の evidence。
- ゲート結論: WebOTP all-apps path に targetSdkVersion ゲートは確認できない。broadcast withholding / 3 時間 delay の exact enforcement は Telephony provider / module 側の追加確認が必要。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断

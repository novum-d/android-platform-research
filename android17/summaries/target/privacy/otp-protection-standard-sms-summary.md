# 標準 SMS メッセージに対する OTP 保護 - 1ページ要約

## 対象（Target）

Android 17 Behavior Change

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

## 適用条件（Applicability）

- 主分類（Primary classification）: TARGET_SDK_37_CONDITIONAL
- OS アップデート / 全アプリ（OS update / all apps）: standard SMS OTP については主条件ではない。WebOTP / SMS Retriever OTP の all-apps protection は別項目。
- targetSdkVersion 37 以上: 該当。`SmsManager.FILTER_GENERIC_OTP` は `@EnabledSince(CINNAMON_BUN)`。
- その他の必須条件（Other required conditions）: generic OTP SMS、WebOTP / SMS Retriever subtype ではないこと、受信後 3 時間以内、trusted / exempted app ではないこと。
- Compat Change ID: `437043173L`
- Compat default state: `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.CINNAMON_BUN)`

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | generic OTP SMS の receive/read は引き続き許可される想定。 |
| Android 17 / targetSdkVersion 37 | untrusted app では standard SMS OTP が受信後 3 時間まで利用不可。 |
| Android 17 / targetSdkVersion 37 + exempted app | system app、trusted role、carrier privileged、companion association、`READ_OTP_SMS` app op などは許可対象。 |

## 要約（Summary）

Android 17 では、targetSdkVersion 37 以上の多くのアプリで、WebOTP / SMS Retriever format ではない generic OTP SMS が受信後 3 時間まで broadcast / provider query から利用できなくなる。

AOSP では `SmsManager.FILTER_GENERIC_OTP = 437043173L` が `@EnabledSince(CINNAMON_BUN)` として定義され、targetSdkVersion 37 以上で generic OTP protection が strict enforce されることを直接示している。

## 顧客影響（Customer Impact）

- SMS inbox、SMS provider、`SMS_RECEIVED_ACTION` broadcast から OTP を直接抽出するログイン / サインアップ / 本人確認フローに影響する。
- 3 時間後に読めても OTP は通常期限切れのため、認証用途では実質利用できない可能性が高い。
- SMS Retriever API または SMS User Consent API への移行が推奨される。

## 対応要否（Required Action）

- 必須対応候補: OTP SMS 文面と読み取り経路を棚卸しする。
- 推奨対応: SMS Retriever API / SMS User Consent API への移行、または trusted role / exemption に依存しない認証 UX を設計する。
- テスト: targetSdkVersion 36 / 37、generic OTP / SMS Retriever / WebOTP、trusted / untrusted app を分けて検証する。

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-17
- AOSP: `telephony/java/android/telephony/SmsManager.java` の `FILTER_GENERIC_OTP = 437043173L`
- AOSP: `FILTER_GENERIC_OTP` は `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.CINNAMON_BUN)`
- AOSP: `core/java/android/provider/Telephony.java` の `CONTAINS_OTP` / `OTP_SUBTYPE_SMS_RETRIEVER_OTP` / `OTP_SUBTYPE_WEB_OTP`
- AOSP: subtype field が unset の OTP は generic OTP と扱われる。
- AOSP: `core/java/android/app/AppOpsManager.java` の `OP_READ_OTP_SMS`
- AOSP: `SmsManager.isAppTrustedForSmsOtp` が system app、role holder、carrier privileged app、companion association、`READ_OTP_SMS` app op allowed package を trusted とする。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断

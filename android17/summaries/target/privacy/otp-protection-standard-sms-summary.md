# OTP protection for standard SMS messages - 1ページ要約（One Page Summary）

## 対象（Target）

Android 17 Behavior Change

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP tag

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

## 適用条件（Applicability）

- 主分類（Primary classification）: UNKNOWN_NEEDS_MORE_EVIDENCE
- OS アップデート / 全アプリ（OS update / all apps）: Unknown。この section は targetSdkVersion 37+ 向けページにあるが、AOSP gate 未確認。WebOTP / SMS Retriever format messages の all-apps protection は別項目。
- targetSdkVersion 37 以上: 公式文書上は該当。AOSP gate 未確認。
- その他の必須条件（Other required conditions）: OTP を含む standard SMS、WebOTP / SMS Retriever format ではないこと、exempted app ではないこと、受信後 3 時間以内。
- Compat Change ID: Unknown
- Compat default state: Unknown

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | Unknown。この section は targetSdkVersion 37+ 向けだが、AOSP gate 未確認。all-apps SMS OTP protection は別途確認が必要。 |
| Android 17 / targetSdkVersion 37 | 公式文書上は、most apps で standard SMS OTP が受信後 3 時間まで利用不可。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | `SMS_RECEIVED_ACTION` broadcast は withheld、SMS provider database query は filtered。3 時間後に利用可能。 |

## 要約（Summary）

Android 17 では、targetSdkVersion 37 以上の多くのアプリで、OTP を含む標準 SMS が受信後 3 時間まで broadcast / provider query から利用できなくなる、と公式文書は説明している。

## 顧客影響（Customer Impact）

- 要確認

## 影響対象（Who Is Affected）

- 対象アプリ: SMS inbox、SMS provider、`SMS_RECEIVED_ACTION` broadcast から OTP を直接抽出しているアプリ。
- 対象機能: ログイン、サインアップ、本人確認、決済、アカウント復旧などの OTP 自動入力。
- 対象条件: targetSdkVersion 37 以上、OTP を含む standard SMS、WebOTP / SMS Retriever format ではない SMS、exempted app ではないこと。

## 対応要否（Required Action）

- 必須対応: SMS を直接読んで OTP を抽出している箇所を棚卸しし、SMS Retriever API または SMS User Consent API への移行計画を作る。
- 推奨対応: targetSdkVersion 36 / 37、standard SMS / SMS Retriever / WebOTP format、受信直後 / 3 時間後を分けて Android 17 で検証する。
- 不要: OTP SMS を読まないアプリでは直接影響は限定的。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 16 | 36 | Android 16 baseline。具体挙動は Android 17 tag 比較待ち。 |
| Android 17 | 36 | Unknown。この section は targetSdkVersion 37+ 向けだが、AOSP gate 未確認。 |
| Android 17 | 37 | standard SMS OTP は受信後 3 時間まで利用不可、broadcast withheld、provider query filtered と公式文書は説明。 |

## 顧客向け説明（Explanation for Customers）

Android 17 では、targetSdkVersion 37 以上の多くのアプリに対し、OTP を含む標準 SMS を直接読む経路が制限されます。受信後 3 時間は `SMS_RECEIVED_ACTION` broadcast が配信されず、SMS provider query でも対象 SMS が filtered されるため、SMS 本文を直接読んで OTP を自動入力する実装は認証フローに影響する可能性があります。

継続して OTP 自動入力を行う場合は、SMS Retriever API または SMS User Consent API への移行を検討してください。現時点では local AOSP checkout に Android 17 tag がないため、targetSdkVersion gate、exemption 条件、compat flag の有無は未確認です。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-17
- Original statement: Android 17 から standard SMS messages に SMS OTP protection を拡張し、most apps targeting Android 17 / API level 37 or higher では受信後 3 時間まで対象 SMS が利用不可。遅延中は `SMS_RECEIVED_ACTION` broadcast が withheld され、SMS provider database queries が filtered される。
- AOSP files: 未確認。local `frameworks-base` に `android-17*` tag がない。
- AOSP source context: 未確認。tag 間 diff が実行できない。
- Diff interpretation: 未分類。added behavior / changed condition / changed default の判定は Android 17 tag 待ち。
- Gate conclusion: Unknown。公式文書は targetSdkVersion 37+ と standard SMS OTP / exemption 条件を示すが、AOSP gate evidence は未取得。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Human decision required

判断（Decision）:
- Further investigation required

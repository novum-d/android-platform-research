# SMS OTP protection - 1ページ要約

## 対象（Target）

Android 17 Behavior Change

比較元:
- android-16.0.0_r4

比較先:
- TBD: Android 17 AOSP tag

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

## 適用条件（Applicability）

- 主分類（Primary classification）: UNKNOWN_NEEDS_MORE_EVIDENCE
- OS アップデート / 全アプリ（OS update / all apps）: 公式文書上は該当候補。`behavior-changes-all` ページに掲載され、WebOTP format messages への追加保護は target API level に関係なく適用されると説明されている。
- targetSdkVersion 37 以上: WebOTP protection では公式文書上は不要と読める。ただし AOSP gate 未確認。standard SMS protection は targetSdkVersion 37+ の別項目。
- その他の必須条件（Other required conditions）: SMS read permission、WebOTP format message、intended recipient ではないこと、domain verification、受信後 3 時間以内、exempted app ではないこと。
- Compat Change ID: 未確認
- Compat default state: 未確認

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 公式文書上、WebOTP format message は intended recipient ではない app から 3 時間 access できない可能性がある。AOSP gate 未確認。 |
| Android 17 / targetSdkVersion 37 | WebOTP protection に加え、standard SMS protection の別条件も発生する可能性がある。両者を分けて確認する。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | `SMS_RECEIVED_ACTION` broadcast withheld、SMS provider query filtered、3 時間後に利用可能と公式文書は説明。 |

## 要約（Summary）

Android 17 では、SMS OTP protection が WebOTP format messages にも拡張される。SMS を読む permission があるアプリでも、domain verification 上の intended recipient ではない場合、受信後 3 時間は broadcast / provider query から message を利用できない。

## 顧客影響（Customer Impact）

- 要確認

## 影響対象（Who Is Affected）

- 対象アプリ: SMS inbox、SMS provider、`SMS_RECEIVED_ACTION` broadcast から OTP を直接抽出しているアプリ。
- 対象機能: ログイン、サインアップ、本人確認、決済、アカウント復旧などの OTP 自動入力。
- 対象条件: Android 17、WebOTP format message、SMS read permission、intended recipient ではないこと、exempted app ではないこと、受信後 3 時間以内。

## 対応要否（Required Action）

- 必須対応: SMS を直接読んで OTP を抽出している箇所、`SMS_RECEIVED_ACTION` receiver、`Telephony.Sms` provider query の利用を棚卸しする。
- 推奨対応: SMS Retriever API または SMS User Consent API へ移行し、WebOTP / SMS Retriever / standard SMS format を分けて Android 17 で検証する。
- 不要: SMS を直接読まないアプリ、または公式 API に移行済みの OTP flow では直接影響は限定的。ただし認証基盤の SMS format は確認する。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 16 | 36 | Android 16 baseline。SMS Retriever hash delay は公式文書上存在。WebOTP baseline は AOSP tag 比較待ち。 |
| Android 17 | 36 | WebOTP format message は intended recipient ではない app から 3 時間 access できない可能性がある。 |
| Android 17 | 37 | WebOTP protection と standard SMS protection の両方を分けて確認する。 |

## 顧客向け説明（Explanation for Customers）

Android 17 では、OTP を含む SMS の保護が WebOTP format messages にも拡張されます。SMS を読む permission があるアプリでも、domain verification でその WebOTP message の intended recipient ではないと判断される場合、受信後 3 時間は `SMS_RECEIVED_ACTION` broadcast が配信されず、SMS provider query でも対象 message が filtered されます。

OTP を SMS 本文から直接抽出している実装は、ログインや本人確認の自動入力に影響する可能性があります。継続して OTP 取得を行う場合は、SMS Retriever API または SMS User Consent API への移行を検討してください。targetSdkVersion 37 以上では standard SMS messages にも別の保護が適用されるため、WebOTP と standard SMS を分けて検証する必要があります。

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-all
- 検証対象の原文: Android 17 から WebOTP format messages にも SMS OTP protection が適用され、intended recipient ではない app では受信後 3 時間まで access できない。遅延中は `SMS_RECEIVED_ACTION` broadcast が withheld され、SMS provider database queries が filtered される。
- AOSP ファイル: 未確認。local `frameworks-base` に `android-17*` tag がない。
- AOSP ソース文脈: 未確認。tag 間 diff が実行できない。
- 差分解釈: 未分類。公式文書上は added behavior / changed condition と読めるが、AOSP diff による確認は Android 17 tag 待ち。
- Gate conclusion: 未確認。公式文書上は Android 17 all apps + WebOTP / SMS read permission / domain verification / 3 hour delay / exemption 条件。targetSdkVersion gate / compat framework evidence は未取得。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- Android 17 AOSP tag 公開後に追加調査が必要

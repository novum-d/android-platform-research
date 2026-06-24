# 標準 SMS メッセージに対する OTP 保護

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
https://developer.android.com/about/versions/17/behavior-changes-17

関連文書:
- https://developer.android.com/reference/android/provider/Telephony.Sms.Intents#SMS_RECEIVED_ACTION
- https://developer.android.com/reference/android/provider/Telephony.Sms
- https://developer.android.com/identity/sms-retriever
- https://developers.google.com/identity/sms-retriever/user-consent/overview
- https://developer.android.com/about/versions/17/behavior-changes-all#sms-otp-all-apps

セクション:
- OTP protection for standard SMS messages

ページ種別:
- Android 17 以上をターゲットにするアプリ

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- TARGET_SDK_37_CONDITIONAL

公式文書からの適用条件判断:
- 公式文書は、Android 17 / targetSdkVersion 37 以上の多くのアプリでは、WebOTP / SMS Retriever format ではない standard SMS OTP が受信後 3 時間まで利用できないと説明している。
- 3 時間の遅延中は `SMS_RECEIVED_ACTION` broadcast が withheld され、SMS provider database query が filtered される。
- 追加条件は、SMS が OTP を含むこと、subtype が WebOTP / SMS Retriever ではない generic OTP であること、app が trusted / exempted category ではないこと。
- AOSP `SmsManager.FILTER_GENERIC_OTP` は `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.CINNAMON_BUN)` を持ち、targetSdkVersion 37 gate を直接裏付ける。

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | WebOTP / SMS Retriever OTP の all-apps 保護は別項目。standard SMS OTP は targetSdkVersion 37 gate が主条件。 | `FILTER_GENERIC_OTP` comment は pre-CINNAMON_BUN package には generic OTP SMS の receive/read を許すと説明。 |
| targetSdkVersion 37 以上が必要か | Yes | `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.CINNAMON_BUN)` on `SmsManager.FILTER_GENERIC_OTP`。 |
| 追加の実行時条件があるか | ある | generic OTP SMS、受信後 3 時間以内、trusted / exempted app ではないこと。 |
| Compat Change ID が関係するか | Yes | `SmsManager.FILTER_GENERIC_OTP = 437043173L`。 |

### 調査日（Investigation Date）

2026-06-18

### 信頼度（Confidence）

- High

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] targetSdkVersion に関係なく Android 17 の全アプリへ適用
- [ ] Android 17 以上かつ targetSdkVersion 37 以上で適用
- [x] targetSdkVersion 37 以上かつ追加の実行時条件を満たす場合に適用
- [ ] Mainline / Google Play system update に依存
- [ ] API 追加のみであり、挙動変更ではない
- [ ] 未確認 / 追加 evidence が必要

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 以上。
- targetSdkVersion: 37 以上。
- Message condition: SMS body が OTP を含む。`Telephony.Sms.CONTAINS_OTP` の type bit が OTP を示す。
- Subtype condition: WebOTP / SMS Retriever OTP ではない generic OTP。`Telephony.Sms` comment は subtype field が unset の場合 generic OTP と扱うと説明する。
- Time condition: 受信後 3 時間以内。
- App exemption condition: trusted / exempted app ではないこと。AOSP は system app、SMS / assistant / dialer / device policy management role holder、`RECEIVE_SENSITIVE_NOTIFICATIONS` holder、carrier privileged app、current companion device association、`READ_OTP_SMS` app op allowed package を trusted として扱う。

Compat framework:
- Change ID: `437043173L`
- 変更名: `FILTER_GENERIC_OTP`
- 既定状態: `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.CINNAMON_BUN)`
- テスト時に切り替え可能か: compat change として切り替え可能

分類信頼度（Classification confidence）:
- High

分類根拠（Classification evidence）:
- 公式 Behavior Change 文書は targetSdkVersion 37 以上で standard SMS OTP の 3 時間 delay を説明している。
- AOSP `SmsManager.FILTER_GENERIC_OTP` は `@EnabledSince(CINNAMON_BUN)` を持ち、pre-CINNAMON_BUN package には generic OTP SMS の receive/read を許すと comment している。
- AOSP `Telephony.Sms.CONTAINS_OTP` と OTP type / subtype constants が、generic OTP と SMS Retriever / WebOTP subtype を表現する。
- AOSP `SmsManager.isAppTrustedForSmsOtp` と related helper が trusted / exempted app categories を実装している。
- AOSP `AppOpsManager.OP_READ_OTP_SMS` が明示的に OTP SMS read exemption を表現する。

---

# エグゼクティブサマリー

Android 17 では、targetSdkVersion 37 以上の多くのアプリに対し、OTP を含む標準 SMS は受信後 3 時間まで利用できなくなる。対象は WebOTP / SMS Retriever format ではない generic OTP SMS であり、遅延中は `SMS_RECEIVED_ACTION` broadcast が withheld され、SMS provider database query からも filtered される。

AOSP `frameworks-base` では、`SmsManager.FILTER_GENERIC_OTP = 437043173L` が `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.CINNAMON_BUN)` として定義されている。comment は、targetSdkVersion 37 以上では generic OTP protection を strict に enforce し、それ未満では generic OTP SMS の receive/read を引き続き許すと説明している。

この変更により、SMS inbox、SMS provider、SMS broadcast を直接読んで OTP を抽出する認証フローは、targetSdkVersion 37 更新後に実質利用できなくなる可能性が高い。OTP 自動入力は SMS Retriever API または SMS User Consent API への移行が必要になる。

---

# 公式ドキュメント確認

## 原文（Statement）

ページタイトル:
- Behavior changes: Apps targeting Android 17 or higher

ページ URL:
- https://developer.android.com/about/versions/17/behavior-changes-17

セクションタイトル:
- OTP protection for standard SMS messages

検証対象の原文:
- Android 17 は SMS OTP protection を standard SMS messages に拡張する。
- most apps targeting Android 17 / API level 37 or higher では、これらの SMS は受信後 3 時間まで利用可能にならない。
- 3 時間の遅延中は `SMS_RECEIVED_ACTION` broadcast が withheld され、SMS provider database queries が filtered される。

## 解釈（Interpretation）

この変更は、OTP を含む SMS を app が直接読む経路を targetSdkVersion 37 以上で制限する security / privacy behavior change である。WebOTP / SMS Retriever format を使うメッセージの all-apps 保護とは別に、標準 SMS の generic OTP にも同様の保護を広げる。

---

# 変更内容（What Changed）

公式文書上の変更点:
- Android 17 は standard SMS messages に SMS OTP protection を拡張する。
- 対象は OTP を含むが WebOTP / SMS Retriever format ではない SMS message。
- most apps targeting Android 17 / API level 37 or higher では、対象 SMS は受信後 3 時間まで利用不可。
- 遅延中は `SMS_RECEIVED_ACTION` broadcast が withheld され、SMS provider database query が filtered される。
- default SMS assistant app、connected device companion apps など一部アプリは exempted。
- OTP 抽出には SMS Retriever API または SMS User Consent API への移行が推奨される。

AOSP で確認した変更点:
- `SmsManager.FILTER_GENERIC_OTP` compat ChangeId が追加され、`@EnabledSince(targetSdkVersion = Build.VERSION_CODES.CINNAMON_BUN)` で targetSdkVersion 37 gate を定義する。
- `Telephony.Sms.CONTAINS_OTP` と OTP type / subtype constants が追加され、OTP 判定状態と WebOTP / SMS Retriever / generic OTP の subtype を表現する。
- `AppOpsManager.OP_READ_OTP_SMS` / `OPSTR_READ_OTP_SMS` が追加され、OTP SMS read exemption を app op として表現する。
- `SmsManager.isAppTrustedForSmsOtp` が trusted app 判定を提供し、system app、role holder、carrier privileged app、companion association、`READ_OTP_SMS` app op allowed package を許可する。

---

# AOSP 調査（AOSP Investigation）

## チェックアウト状態

根拠利用前に確認したコマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list android-17.0.0_r1
```

結果:
- `frameworks-base` working tree: clean at the time of investigation.
- From tag: `android-16.0.0_r4` exists.
- To tag: `android-17.0.0_r1` exists.

## 関連ファイル（Related Files）

- `telephony/java/android/telephony/SmsManager.java`
- `core/java/android/provider/Telephony.java`
- `core/java/android/app/AppOpsManager.java`
- `core/api/current.txt`
- `core/api/test-current.txt`

## 確認したソース文脈（Source Context Reviewed）

| File / symbol | Android 16 baseline | Android 17 behavior | 関連性 |
| --- | --- | --- | --- |
| `SmsManager.FILTER_GENERIC_OTP` | ChangeId なし | `437043173L` として追加。`@EnabledSince(CINNAMON_BUN)`。comment は targetSdkVersion 37 以上で strict enforcement と説明 | targetSdkVersion ゲートの中核 evidence。 |
| `Telephony.Sms.CONTAINS_OTP` | OTP metadata column なし | SMS provider が message body の OTP type / subtype を記録する hidden/test API を追加 | provider query filtering と OTP classifier の連携点。 |
| `Telephony.Sms.OTP_SUBTYPE_*` | subtype constants なし | SMS Retriever OTP / WebOTP subtype と、subtype unset の generic OTP を表現 | standard SMS OTP と WebOTP / SMS Retriever OTP を分離する evidence。 |
| `AppOpsManager.OP_READ_OTP_SMS` | app op なし | OTP SMS read を許可する app op を追加。comment は `READ_SMS` app op の必要性を消さないと説明 | trusted / exempted app の明示的な escape hatch。 |
| `SmsManager.SMS_OTP_READING_ROLES` | role allowlist なし | SMS / assistant / dialer / device policy management roles を trusted とする | 公式文書の exempted app categories に対応。 |
| `SmsManager.isAppTrustedForSmsOtp` | trusted 判定なし | system app、role holder、`RECEIVE_SENSITIVE_NOTIFICATIONS`、device-managed、carrier privileged、companion association、`READ_OTP_SMS` app op を許可 | exempted app 判定の実装。 |

Source context の補足:
- Entry point / caller: SMS 受信後の broadcast dispatch、SMS provider query、OTP classification、trusted package 判定。
- 関連性: app が SMS broadcast / provider 経由で OTP SMS を読むかどうかを判定するための API / compat / app op / trusted app 判定が `frameworks-base` 内にある。
- Baseline Android behavior: Android 16 tag では `FILTER_GENERIC_OTP`、`CONTAINS_OTP`、`OP_READ_OTP_SMS` が存在しない。
- Target Android behavior: Android 17 tag では generic OTP を targetSdkVersion 37 以上で filter する compat gate と、OTP metadata / trusted app 判定が追加される。
- Source diff type: added behavior、changed condition。
- Excluded code paths: Notification OTP redaction は同じ OTP 用語を含むが、SMS broadcast / provider filtering とは別経路のため、この target Behavior Change の主要 evidence から除外した。

## 差分解釈（Diff Interpretation）

| 観測した diff | 解釈 | Behavior Change との関連 | 信頼度 |
| --- | --- | --- | --- |
| `FILTER_GENERIC_OTP` + `@EnabledSince(CINNAMON_BUN)` 追加 | changed condition / gate | targetSdkVersion 37 以上で generic OTP protection を strict enforce する | High |
| `Telephony.Sms.CONTAINS_OTP` / subtype constants 追加 | added behavior | SMS provider が OTP / generic OTP / WebOTP / SMS Retriever OTP を分類できるようにする | High |
| `OP_READ_OTP_SMS` 追加 | added behavior | exempted app に OTP SMS read を許可する app op を追加 | High |
| `isAppTrustedForSmsOtp` trusted 判定追加 | added behavior | 公式文書の exempted app categories に対応 | High |

---

# 事実・観察・仮説・結論

## 事実（Facts）

- `frameworks-base` の `android-16.0.0_r4` と `android-17.0.0_r1` tag は存在し、調査時点の working tree は clean。
- `SmsManager.FILTER_GENERIC_OTP = 437043173L` は `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.CINNAMON_BUN)` を持つ。
- `FILTER_GENERIC_OTP` の comment は、targetSdkVersion 37 以上では generic OTP protection を strict enforce し、それ未満の package は generic OTP SMS の receive/read を許すと説明している。
- `Telephony.Sms.CONTAINS_OTP` は message body が OTP を含むか、分類が pending か、SMS Retriever / WebOTP subtype かを bit field で表現する。
- subtype field が unset の OTP は generic OTP と扱われる。
- `SmsManager.isAppTrustedForSmsOtp` は trusted app 判定を実装している。
- `AppOpsManager.OP_READ_OTP_SMS` は OTP SMS read を許可する app op であり、`READ_SMS` app op の必要性は残る。

## 観察（Observations）

- AOSP 根拠 は、targetSdkVersion ゲート、generic OTP 判定、trusted app exemption、app op escape hatch をすべて `frameworks-base` 内で確認できる。
- 公式文書の「standard SMS messages」は、AOSP 上では WebOTP / SMS Retriever subtype が付かない generic OTP と対応する。
- 3 時間 delay の timer / provider filtering / broadcast withholding 本体は provider / telephony pipeline 側にある可能性が高いが、`frameworks-base` の gate evidence だけで適用分類は十分に確定できる。

## 仮説（Hypotheses）

- SMS provider または telephony provider は `Telephony.Sms.CONTAINS_OTP` を参照して、generic OTP かつ untrusted caller かつ compat change enabled の場合に query result / broadcast delivery を抑制する。
- 3 時間経過後は provider 側の availability 判定により filtered state が解除される。

## 結論（Conclusions）

- この Behavior Change は `TARGET_SDK_37_CONDITIONAL` と分類する。
- Android 17 / targetSdkVersion 37 以上で、generic OTP SMS を直接読む untrusted app は、受信後 3 時間まで broadcast / provider query から対象 SMS を利用できない。
- SMS OTP を使う認証機能は、SMS Retriever API または SMS User Consent API への移行を推奨する。
- 信頼度は High。AOSP targetSdk gate、OTP metadata、trusted app exemption、AppOps evidence がそろっている。

---

# 開発者影響

影響を受ける可能性が高いアプリ:
- SMS inbox / provider query から OTP を抽出するアプリ
- `SMS_RECEIVED_ACTION` broadcast receiver で OTP を読み取るアプリ
- WebOTP / SMS Retriever format ではない独自 SMS 文面で認証しているアプリ

対応候補:
- OTP SMS 文面と読み取り経路を棚卸しする。
- SMS Retriever API または SMS User Consent API へ移行する。
- targetSdkVersion 37 で、generic OTP、SMS Retriever OTP、WebOTP、trusted/exempted role の有無を分けて検証する。
- 直接 SMS を読む fallback は、受信直後には使えない前提で UX / error handling を設計する。

---

# サービス影響例

このセクションは、公式文書と AOSP 根拠から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: PayPay / LINE / メルカリの独自 SMS 文面 OTP

- 具体サービス例: PayPay、LINE、メルカリ、Yahoo! JAPAN ID など、ログイン・本人確認で SMS OTP を使うサービス。
- 影響を受ける実装パターン: SMS Retriever / WebOTP format ではない標準 SMS 文面から、`SMS_RECEIVED_ACTION` receiver または SMS provider query で OTP を抽出する実装。
- 発生条件: Android 17 / targetSdkVersion 37 以上、generic OTP SMS、受信後 3 時間以内、trusted / exempted app ではない場合。
- ユーザーに見える症状: OTP 自動入力が動作せず、ユーザーが SMS アプリから OTP を手入力する必要がある可能性。
- 技術的に起きていること: `FILTER_GENERIC_OTP` compat change が有効になり、generic OTP の broadcast / provider access が一時的に制限される。
- 推奨対応シーン: targetSdkVersion 37 更新前の認証フロー QA、旧式 SMS parser の棚卸し。
- 検証観点: generic OTP、SMS Retriever OTP、WebOTP、trusted role / companion app、3 時間経過後の access。
- 根拠: `SmsManager.FILTER_GENERIC_OTP = 437043173L`、`@EnabledSince(CINNAMON_BUN)`、`Telephony.Sms.CONTAINS_OTP`、trusted app 判定。
- Confidence（信頼度）: High。
- 注意: 上記サービスで発生確認した事実ではない。実際の影響は SMS 文面と OTP 取得 API に依存する。

## 例2（Example 2）: 銀行 / 証券 / クレジットカードのアカウント復旧 SMS

- 具体サービス例: 三井住友銀行、楽天銀行、SBI証券、楽天カードなどの本人確認・アカウント復旧フロー。
- 影響を受ける実装パターン: 独自 SMS parser や認証 SDK が標準 SMS を直接読み、OTP を自動入力する実装。
- 発生条件: targetSdkVersion 37 のアプリが trusted / exempted category ではなく、受信直後に generic OTP SMS を読む場合。
- ユーザーに見える症状: アカウント復旧や高リスク取引の確認で、自動入力ではなく手入力が必要になる可能性。
- 技術的に起きていること: generic OTP は WebOTP / SMS Retriever subtype ではないため、targetSdkVersion 37 gate の対象になる。
- 推奨対応シーン: 金融・決済・通信キャリア系の本人確認、端末変更、パスワード再設定。
- 検証観点: SMS Retriever API / SMS User Consent API の採用可否、手入力 fallback、timeout 設計、role / app op exemption の有無。
- 根拠: 公式文書の standard SMS OTP protection と AOSP の compat ChangeId / OTP metadata / AppOps evidence。
- Confidence（信頼度）: High。
- 注意: 上記サービスで発生確認した事実ではない。金融サービスの実装は個別検証が必要。

---

# テスト観点（Test Matrix）

| 端末 OS | targetSdkVersion | Message type | App state | 期待挙動 |
| --- | --- | --- | --- | --- |
| Android 17 | 36 | generic OTP SMS | untrusted app | `FILTER_GENERIC_OTP` disabled のため receive/read が許される想定。 |
| Android 17 | 37 | generic OTP SMS | untrusted app | 受信後 3 時間まで broadcast withheld / provider query filtered。 |
| Android 17 | 37 | SMS Retriever OTP | untrusted app | standard SMS OTP target change ではなく、別項目の SMS OTP protection として扱う。 |
| Android 17 | 37 | generic OTP SMS | trusted role / system / companion / carrier privileged / `READ_OTP_SMS` app op | exemption により read / receive が許可される想定。 |

---

# 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断

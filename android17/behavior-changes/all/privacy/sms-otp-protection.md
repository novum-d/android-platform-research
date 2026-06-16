# SMS OTP protection

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
- https://developer.android.com/reference/android/provider/Telephony.Sms.Intents#SMS_RECEIVED_ACTION
- https://developer.android.com/reference/android/provider/Telephony.Sms
- https://developer.android.com/identity/sms-retriever
- https://developers.google.com/identity/sms-retriever/user-consent/overview
- https://developer.android.com/about/versions/17/behavior-changes-17#sms-otp-protection
- https://developer.android.com/about/versions/17/behavior-changes-17

セクション:
- SMS OTP protection

ページ種別:
- Behavior changes: all apps

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- 公式文書は Android 17 の `Behavior changes: all apps` ページにこの項目を掲載しており、ページ冒頭は Android 17 上で動作する全アプリに targetSdkVersion に関係なく適用されると説明している。
- 本項目では、Android 17 から WebOTP format messages にも SMS OTP protection が適用される、と説明している。
- 対象条件は、アプリが SMS を読む permission を持つこと、WebOTP message の intended recipient ではないこと、intended recipient 判定が domain verification によること、受信後 3 時間以内であること。
- ただし、local `frameworks-base` に Android 17 AOSP tag がないため、WebOTP 判定、domain verification 連携、broadcast withholding、provider filtering、exemption 条件、targetSdkVersion gate の不存在、Compat Change ID は未確認である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。
- Android 17 / targetSdkVersion 37 以上では standard SMS messages にも保護が拡張されるが、これは `behavior-changes-17` 側の別項目として分離する。

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 可能性は高いが条件付き、かつ未検証 | `behavior-changes-all` ページに掲載。ページ冒頭は all apps / regardless of targetSdkVersion と説明。AOSP gate 未確認。 |
| targetSdkVersion 37 以上が必要か | WebOTP protection では不要と考えられるが未検証 | All apps page の項目は target API level に関係なく適用されると説明。standard SMS 拡張は targetSdkVersion 37+ 側の別項目。 |
| 追加の実行時条件があるか | ある | SMS read permission、WebOTP format message、intended recipient ではないこと、domain verification、3 時間以内、exempted app ではないこと。 |
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
- Android version: Android 17 が前提。AOSP tag 未取得のため実装上の OS gate は未確認。
- targetSdkVersion: 公式文書上は WebOTP format messages への追加保護は targetSdkVersion に依存しない all apps change と読める。AOSP targetSdkVersion gate 未確認。
- Device/form factor: 公式文書からは device / form factor 条件は確認できない。
- Permission/API/component condition: app が SMS messages を読む permission を持つこと、WebOTP format message、intended recipient ではないこと、domain verification により recipient が判定されること、`SMS_RECEIVED_ACTION` broadcast または SMS provider query 経路を使うこと。
- App state/process condition: SMS 受信後 3 時間以内に、対象 app が WebOTP message を programmatically read しようとする場合。

Compat framework:
- Change ID: 未確認
- 変更名: 未確認
- 既定状態: 未確認
- テスト時に切り替え可能か: 未確認

分類信頼度（Classification confidence）:
- Low

分類根拠（Classification evidence）:
- 公式ドキュメントページ: `behavior-changes-all`
- 検証対象の適用条件文: all apps page は Android 17 上の全アプリに targetSdkVersion に関係なく適用されると説明し、本項目は WebOTP format messages にも 3 時間 delay / broadcast withholding / provider filtering が適用されると説明している。
- AOSP targetSdk gate: 未確認。local `frameworks-base` に `android-17*` tag がない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# エグゼクティブサマリー（Executive Summary）

Android 17 では、SMS OTP protection が WebOTP format messages にも拡張される、と公式文書は説明している。SMS を読む permission を持つアプリであっても、domain verification で WebOTP message の intended recipient と判定されない場合、受信後 3 時間はその message にアクセスできない。

この制限中は `SMS_RECEIVED_ACTION` broadcast が withheld され、SMS provider database query も filtered される。OTP を SMS inbox / broadcast / provider query から直接抽出しているアプリは、SMS Retriever API または SMS User Consent API への移行を検討する必要がある。

現時点では local `frameworks-base` に Android 17 AOSP tag がないため、実装差分、domain verification 連携、exemption 条件、targetSdkVersion gate の不存在、compat framework entry は未確認である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とし、Android 17 AOSP tag 公開後に再調査する。

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
- Delivery of messages containing an SMS Retriever hash was delayed for most apps for three hours, with exemptions such as the default SMS handler and the app that owned the hash.
- Beginning with Android 17, protection is also applied to WebOTP format messages.
- If an app can read SMS messages but is not the intended recipient of a WebOTP message, as determined by domain verification, the message is not accessible to the app until three hours after receipt.
- During the delay, `SMS_RECEIVED_ACTION` broadcast is withheld and SMS provider database queries are filtered.
- The message becomes available to these apps after the delay.
- This change applies to all apps, regardless of target API level.
- Certain apps, such as the default SMS assistant app and connected device companion apps, are exempted.
- Apps that rely on reading SMS messages for OTP extraction should transition to SMS Retriever or SMS User Consent APIs.
- If an app targets Android 17 / API level 37 or higher, the protection is also extended to standard SMS messages; that targetSdkVersion 37 behavior is documented separately.

## 解釈（Interpretation）

この変更は、OTP を含む SMS をアプリが直接読む経路を制限する privacy / security behavior change である。Android 17 では、従来の SMS Retriever format message に加えて WebOTP format message も、intended recipient ではないアプリから 3 時間隠される。

重要なのは、All apps ページ上の変更として WebOTP format messages への保護が targetSdkVersion に依存しないと説明されている点である。Android 17 / targetSdkVersion 36 のままでも、SMS read permission を持ち、WebOTP message の intended recipient ではないアプリは、3 時間以内に broadcast / provider query から message を読めない可能性がある。

一方、standard SMS messages への拡張は「target Android 17 / API level 37 以上」の別項目である。顧客説明では、WebOTP format messages への all-apps protection と、targetSdkVersion 37 以上の standard SMS protection を混同しない必要がある。

---

# 変更内容（What Changed）

公式文書上の変更点:
- Android 17 で SMS OTP protection が WebOTP format messages にも適用される。
- Android 16 以前の保護は主に SMS Retriever format message に焦点があり、SMS Retriever hash を含む message は多くのアプリで 3 時間遅延されていた。
- Android 17 では、SMS を読む permission を持つアプリでも、WebOTP message の intended recipient ではない場合、受信後 3 時間は message にアクセスできない。
- intended recipient は domain verification により判定される。
- 3 時間の遅延中、`SMS_RECEIVED_ACTION` broadcast は withheld される。
- 3 時間の遅延中、SMS provider database queries は filtered される。
- 3 時間後、対象アプリにも SMS message が利用可能になる。
- default SMS assistant app、connected device companion apps など一部アプリは exempted される。
- OTP extraction に SMS を直接読むアプリは SMS Retriever API または SMS User Consent API への移行が推奨される。
- targetSdkVersion 37 以上では standard SMS messages にも保護が拡張されるが、これは別 Behavior Change として扱う。

AOSP で未確認の点:
- WebOTP format message を識別する parser / classifier。
- domain verification と intended recipient 判定の連携。
- SMS read permission、AppOps、default SMS assistant、companion app など exemption 判定。
- `SMS_RECEIVED_ACTION` broadcast withholding path。
- SMS provider database query filtering path。
- 3 時間 delay の timer / availability state。
- Android 17 all-apps behavior と targetSdkVersion 37 standard SMS behavior の分岐。
- targetSdkVersion gate が WebOTP format messages 側に存在しないこと。
- Compat Change ID と default state。

## 適用条件（Applicability）

この変更がいつ適用されるかを OS 条件と targetSdkVersion 条件に分けて説明する。

### OS アップデート時の挙動（OS Update Behavior）

- Android 17 に OS アップデートしただけで適用されるか: 公式文書上は Yes / Conditional。All apps ページに掲載され、ページ冒頭は targetSdkVersion に関係なく Android 17 上の全アプリに適用されると説明している。ただし AOSP gate 未確認。
- targetSdkVersion に依存しない根拠: 公式文書は WebOTP format messages への追加 SMS OTP protection が all apps に適用されると説明している。targetSdkVersion 37 以上の standard SMS extension は別項目。
- Android 16 以前での挙動: 公式文書は、以前は主に SMS Retriever format messages が保護対象で、SMS Retriever hash を含む message は多くのアプリで 3 時間遅延されていたと説明している。AOSP baseline diff は未確認。

### targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- targetSdkVersion 37 以上で適用されるか: WebOTP format messages への保護は公式文書上、targetSdkVersion 37 は必要条件ではないと読める。AOSP gate 未確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: Unknown。公式文書は Android 17 Behavior Change として説明している。
- opt-out / temporary override の有無: app developer が任意に opt out できる仕組みは公式抜粋からは確認できない。exempted app categories はある。compat framework toggle は未確認。

### その他の条件（Other Conditions）

- device/form factor: 公式文書からは条件なし。
- permission: app が SMS messages を読む permission を持つ場合に関係する。正確な permission / AppOps gate は AOSP 未確認。
- API usage: `SMS_RECEIVED_ACTION` broadcast、`Telephony.Sms` provider query、WebOTP format message、SMS Retriever API、SMS User Consent API。
- manifest attribute: SMS receiver、SMS read / receive permission、domain verification 設定が関係する可能性があるが、AOSP 未確認。
- component boundary: telephony message receive pipeline、broadcast dispatch、SMS provider、domain verification、default SMS assistant / companion app exemption にまたがる。

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
- `core/java/android/provider/Telephony.java`
- `Telephony.Sms.Intents.SMS_RECEIVED_ACTION` の API surface / docs source
- SMS provider query filtering に関係する provider implementation
- SMS broadcast dispatch / receiver filtering に関係する telephony / framework path
- WebOTP / SMS Retriever format classifier / parser
- domain verification / intended recipient 判定 path
- default SMS assistant app / connected device companion app exemption 判定 path
- compat framework 定義ファイル内の SMS OTP / WebOTP / targetSdkVersion 37 関連 Change ID

Note:
- 実際の SMS receive pipeline、SMS provider、WebOTP parser は `frameworks-base` 以外の AOSP project にある可能性がある。Android 17 tag 入手後は、該当 project も evidence 対象として確認する必要がある。

## 確認したソース文脈（Source Context Reviewed）

AOSP tag diff は未実行。以下は公式文書から見た確認予定の source context であり、AOSP evidence ではない。

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| SMS receive / OTP classification path | SMS Retriever format message が主な保護対象と公式文書は説明 | WebOTP format message も保護対象になると公式文書が説明 | WebOTP / SMS Retriever / standard SMS の分類境界を確認するため |
| `SMS_RECEIVED_ACTION` broadcast dispatch | 未確認 | 3 時間 delay 中は broadcast が withheld されると公式文書が説明 | アプリが OTP SMS を broadcast で受け取れるかを決める app-facing path |
| SMS provider query filtering | 未確認 | 3 時間 delay 中は SMS provider database queries が filtered されると公式文書が説明 | `ContentResolver.query()` 経由で SMS を読むアプリへの影響を確認するため |
| domain verification / intended recipient 判定 | 未確認 | WebOTP message の intended recipient を domain verification で判定すると公式文書が説明 | 対象アプリと非対象アプリを分ける gate になるため |
| exemption 判定 | default SMS handler などが SMS Retriever hash delay から exempt されていたと公式文書は説明 | default SMS assistant app、connected device companion apps などが delay から exempted と公式文書が説明 | 顧客アプリが影響対象外になる条件を確認するため |

必須記入項目:
- Entry point / caller: 未確認。想定される entry point は SMS 受信 -> OTP / WebOTP 判定 -> intended recipient 判定 -> broadcast dispatch / SMS provider query filtering。
- Relevant class or service responsibility: 未確認。SMS message classification、domain verification、broadcast withholding、provider query filtering、exemption 判定。
- Runtime path from app API / system event to changed code: 想定 path は、SMS 受信 -> system が WebOTP / OTP message と判定 -> app が intended recipient か確認 -> 対象外 app には `SMS_RECEIVED_ACTION` を withheld し、SMS provider query 結果から filtered する。AOSP evidence としては未確認。
- Why unrelated code paths were excluded: tag diff 未実行のため、除外判断は未完了。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
| Android 17 tag 未取得のため source diff 未確認 | 公式文書上は added behavior / changed condition と読める | WebOTP format messages への SMS OTP protection 拡張、3 時間 delay、broadcast withholding、provider filtering、domain verification condition が説明されている | Low |

必須分類:
- Added behavior: 公式文書上、Android 17 で WebOTP format messages にも SMS OTP protection が適用される。
- Removed behavior: 未確認。
- Changed condition / gate: 公式文書上、intended recipient 判定に domain verification が使われ、対象外 app には 3 時間 delay が適用される。AOSP gate 未確認。
- Changed default: 未確認。Android 17 platform behavior として有効になる可能性があるが、implementation default は AOSP tag 待ち。
- No behavior change found: 未確認。tag 不在のため「no behavior change」とは判断しない。

## 事実（Evidence）

事実:
- 公式文書は `SMS OTP protection` を Android 17 `Behavior changes: all apps` ページに掲載している。
- All apps ページ冒頭は、記載された変更が Android 17 上で動作する全アプリに targetSdkVersion に関係なく適用されると説明している。
- 公式文書は、Android 17 から SMS messages containing OTP への protection を拡張すると説明している。
- 公式文書は、以前の保護が主に SMS Retriever format に焦点を置いていたと説明している。
- 公式文書は、SMS Retriever hash を含む message delivery が多くのアプリで 3 時間遅延されていたと説明している。
- 公式文書は、Android 17 で WebOTP format messages にも保護が適用されると説明している。
- 公式文書は、SMS を読む permission を持つアプリでも、domain verification により WebOTP message の intended recipient ではない場合、受信後 3 時間まで message にアクセスできないと説明している。
- 公式文書は、3 時間の遅延中に `SMS_RECEIVED_ACTION` broadcast が withheld され、SMS provider database queries が filtered されると説明している。
- 公式文書は、message が 3 時間後に対象アプリにも利用可能になると説明している。
- 公式文書は、default SMS assistant app、connected device companion apps などが delay から exempted と説明している。
- 公式文書は、SMS を読んで OTP extraction するアプリに SMS Retriever API または SMS User Consent API への移行を推奨している。
- 公式文書は、targetSdkVersion 37 以上では standard SMS messages にも protection が拡張されると案内している。

観察:
- All apps ページ掲載のため、一次分類は `OS_UPDATE_ALL_APPS` 候補である。
- ただし、permission、WebOTP format、intended recipient、domain verification、exemption、3 時間以内という追加条件があるため、実際の影響はすべての SMS 利用アプリに一律ではない。
- WebOTP protection と standard SMS protection は隣接しているが、適用条件が異なる。WebOTP protection は all apps、standard SMS protection は targetSdkVersion 37+ の別項目として扱う必要がある。
- OTP は通常短時間で期限切れになるため、3 時間後に message が読めるようになっても認証用途としては実質的に使えない可能性が高い。

仮説:
- enforcement は SMS receive pipeline 上で message type / recipient / exemption を判定し、broadcast dispatch と provider query の両方に同じ availability state を適用している可能性がある。
- WebOTP intended recipient 判定には domain verification の platform state または関連 service が使われる可能性がある。
- SMS Retriever API / SMS User Consent API は、この制限を回避する裏口ではなく、ユーザー保護に沿った OTP retrieval path として推奨されている可能性が高い。

結論:
- 現時点の確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE`。公式文書上は `OS_UPDATE_ALL_APPS` 候補だが、AOSP tag 未取得のため High confidence にできない。
- 顧客向けには、Android 17 上では targetSdkVersion 36 のままでも WebOTP format messages の直接読み取りに影響する可能性がある、と条件付きで説明する。

## 適用ゲート根拠（Applicability Gate Evidence）

- targetSdkVersion gate: 未確認。公式文書上は WebOTP protection は targetSdkVersion 条件なし。standard SMS extension は targetSdkVersion 37+ の別項目。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。
- @EnabledAfter / @EnabledSince / default state: 未確認。
- Build.VERSION / SDK_INT gate: 未確認。公式文書上は Android 17 introduced。
- DeviceConfig / resources config: 未確認。
- Permission/AppOps gate: 公式文書は「app has permission to read SMS messages」と説明。正確な permission / AppOps gate は AOSP 未確認。
- Manifest/property gate: domain verification と SMS receiver / permission declaration が関係する可能性があるが、AOSP 未確認。
- No gate found: 未確認。AOSP tag 未取得のため gate search 未実行。
- Gate conclusion: 公式文書上は Android 17 all apps + SMS read permission + WebOTP format + not intended recipient + domain verification + 3 hour delay + exemption condition。AOSP evidence 未取得のため `UNKNOWN_NEEDS_MORE_EVIDENCE`。
- Reasoning from source context: source context は未確認。公式文書の page type と statement のみから一次判断している。

---

# 影響分析（Impact Analysis）

## 影響を受けるアプリ（Affected Apps）

- Android 17 上で動作するアプリ。
- SMS read permission を持ち、SMS provider query または `SMS_RECEIVED_ACTION` broadcast から OTP を直接抽出するアプリ。
- WebOTP format messages を受け取るが、domain verification 上その message の intended recipient ではないアプリ。
- OTP autofill、login、sign-up、account recovery、payment verification などで SMS text を直接 parse しているアプリ。
- targetSdkVersion 37 以上では、standard SMS OTP protection の別条件にも該当する可能性があるアプリ。

## 影響を受けないアプリ（Non-Affected Apps）

- Android 17 以外で動作している場合。
- SMS を直接読まないアプリ。
- SMS Retriever API または SMS User Consent API に移行済みで、SMS inbox / broadcast / provider query から直接 OTP を抽出していない場合。
- WebOTP message の intended recipient として domain verification により判定される場合。
- default SMS assistant app、connected device companion apps など exempted app に該当する場合。
- SMS 受信から 3 時間経過後に読む場合。ただし OTP の有効期限上、認証用途としては実質的に遅すぎる可能性がある。
- ただし、AOSP tag 未取得のため正確な non-affected condition は未確定。

---

# 顧客影響（Customer Impact）

## 影響度（Impact Level）

- 要確認

※ 最終 severity / priority は人間が判断する。このレポートでは確定しない。

## ビジネス影響（Business Impact）

- ユーザー影響: OTP 自動入力やログイン / sign-up / account recovery が失敗し、ユーザーが手動入力や再送を求められる可能性がある。
- セキュリティ影響: intended recipient ではないアプリが verification code を programmatically read できる範囲が狭まり、OTP hijacking リスク低減が期待される。
- 開発影響: SMS inbox / broadcast / provider query から OTP を直接 parse する実装を棚卸しし、SMS Retriever API または SMS User Consent API への移行を検討する必要がある。
- 運用影響: Android 17 端末で OTP extraction success rate、login conversion、SMS resend rate、manual input rate を監視する必要がある。

---

# サービス影響例（Service Impact Examples）

このセクションは、公式文書と未確認の AOSP 調査観点から導いた「起こりうる影響例」を記録する。
特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: OTP 自動入力ログイン

- 対象サービス例: 電話番号ログイン、二要素認証、account recovery。
- 影響を受ける実装パターン: `SMS_RECEIVED_ACTION` receiver で SMS 本文を取得し、正規表現などで OTP を抽出する。
- 発生条件: Android 17、WebOTP format message、app が SMS read permission を持つ、domain verification 上 intended recipient ではない、exempted app ではない、受信後 3 時間以内。
- ユーザーに見える症状: OTP が自動入力されない、認証画面で待ち続ける、再送が増える。
- 開発・運用への影響: SMS Retriever / SMS User Consent API への移行、domain verification 状態確認、fallback UI の確認が必要。
- 推奨対応候補: OTP extraction path の棚卸し、Android 17 端末で WebOTP / SMS Retriever / standard SMS を分けた検証、login conversion monitoring。
- 根拠: 公式文書は 3 時間 delay 中に `SMS_RECEIVED_ACTION` broadcast が withheld されると説明している。
- Confidence（信頼度）: Low。AOSP enforcement condition 未確認。
- 注意: 実サービスで発生確認した事実ではない。

## 例2（Example 2）: SMS inbox query によるOTP取得

- 対象サービス例: banking、payment、enterprise authentication、identity verification。
- 影響を受ける実装パターン: SMS provider database query で inbox から OTP message を検索する。
- 発生条件: Android 17、WebOTP format message、app が intended recipient ではない、受信後 3 時間以内、exempted app ではない。
- ユーザーに見える症状: provider query で message が見つからず、自動認証が失敗する。
- 開発・運用への影響: provider query 依存の OTP extraction を廃止し、公式 API へ移行する必要がある。
- 推奨対応候補: `Telephony.Sms` query 依存箇所の削除、SMS Retriever / User Consent flow の導入、manual OTP input fallback の改善。
- 根拠: 公式文書は 3 時間 delay 中に SMS provider database queries が filtered されると説明している。
- Confidence（信頼度）: Low。AOSP provider filtering path 未確認。
- 注意: 実サービスで発生確認した事実ではない。

---

# 対応候補（Required Actions）

## 必須対応（Must）

- SMS を直接読んで OTP を抽出している箇所を棚卸しする。
- `SMS_RECEIVED_ACTION` receiver と `Telephony.Sms` provider query の利用箇所を確認する。
- WebOTP format message、SMS Retriever format message、standard SMS message を分けて現在の認証基盤がどの format を送っているか確認する。
- Android 17 で、targetSdkVersion 36 / 37 の両方を使って WebOTP protection と standard SMS protection を分離して検証する。
- OTP 自動入力が失敗した場合の manual input、resend、state recovery、error messaging を確認する。

## 推奨対応（Recommended）

- OTP extraction は SMS Retriever API または SMS User Consent API へ移行する。
- WebOTP を使う場合は、message に含まれる domain と app / site の domain verification 状態を確認する。
- default SMS assistant app / connected device companion apps など exemption に依存した設計になっていないか確認する。
- Android 17 端末で、受信直後、3 時間以内、3 時間後の broadcast / provider query 結果を比較する。
- login conversion、OTP read success、manual OTP input、SMS resend、認証失敗率を Android 17 端末で監視する。

## 任意対応（Optional）

- OTP message format を SMS Retriever / User Consent API に適合させるため、server-side SMS template を見直す。
- targetSdkVersion 37 以上の standard SMS protection と併せて、SMS OTP extraction 全体の移行計画を作る。
- Android 17 AOSP tag 公開後に、compat flag や exemption 判定を追加確認する。

---

# 検証方法（Verification Method）

変更を確認する方法。

## 検証マトリクス（Matrix）

| 端末 OS（Device OS） | targetSdkVersion | Compat flag / test control | 期待挙動（Expected behavior） |
| --- | --- | --- | --- |
| Android 16 | 36 | default | Android 16 baseline。SMS Retriever hash delay は公式文書上存在。WebOTP protection の baseline は AOSP tag 比較待ち。 |
| Android 17 | 36 | default | 公式文書上、WebOTP format message は intended recipient ではない app から 3 時間 access できない。AOSP gate 未確認。 |
| Android 17 | 37 | default | WebOTP protection に加え、standard SMS protection の別条件も発生する可能性がある。両者を分けて検証する。 |
| Android 17 | 36 | force-enabled if available | Compat flag 未確認。存在する場合は WebOTP protection 単体の影響を確認する。 |
| Android 17 | 37 | force-disabled if available | Compat flag 未確認。存在する場合は rollback / opt-out 可能性を確認する。 |

## 手順（Steps）

- targetSdk変更: targetSdkVersion 36 / 37 の両方で検証し、WebOTP all-apps protection と standard SMS targetSdkVersion 37 protection を分ける。
- compat framework command: 未確認。Android 17 tag 公開後に Change ID が存在する場合のみ force-enable / force-disable を検証する。
- テスト方法:
  - WebOTP format SMS、SMS Retriever format SMS、standard SMS OTP を分けて送信する。
  - app が intended recipient である domain verification 状態と、intended recipient ではない状態を分ける。
  - `SMS_RECEIVED_ACTION` receiver が呼ばれるか確認する。
  - SMS provider query で message が返るか確認する。
  - 受信直後、3 時間以内、3 時間後を比較する。
  - exempted app category に該当する場合としない場合を分ける。
- 再現手順:
  - Android 17 device で test app をインストールする。
  - SMS read / receive permission を付与する。
  - domain verification 状態を確認する。
  - WebOTP format message を送信する。
  - 受信直後に broadcast / provider query の結果を記録する。
  - 3 時間後に同じ query を実行し、message が利用可能になるか確認する。
- 期待結果:
  - intended recipient ではない app では、3 時間以内に broadcast が withheld され、provider query から message が filtered される。
  - 3 時間後には message が利用可能になる。
  - intended recipient または exempted app では delay 対象外になる可能性があるが、AOSP / 実機確認が必要。

---

# 結論（Conclusion）

SMS OTP protection は、Android 17 all apps ページに掲載されているため、WebOTP format messages については targetSdkVersion 更新ではなく Android 17 OS update 側の影響候補である。追加条件として、SMS read permission、WebOTP format、intended recipient ではないこと、domain verification、3 時間 delay、exemption 条件がある。

ただし、Android 17 AOSP tag が local `frameworks-base` に存在しないため、実装差分、targetSdkVersion gate の不存在、compat framework entry、exemption 判定は未確認である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

Android app developer は、SMS を直接読んで OTP extraction している実装を棚卸しし、SMS Retriever API または SMS User Consent API への移行、WebOTP / standard SMS の format 切り分け、Android 17 での broadcast / provider query 検証を準備する必要がある。

---

# 人間の判断欄

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- Android 17 AOSP tag 公開後に追加調査が必要

判断理由候補:
- 公式文書上は all apps change だが、実装 gate、domain verification 連携、exemption 条件、compat framework evidence が未確認である。
- 認証導線への影響は、顧客アプリが SMS を直接読むか、SMS Retriever / SMS User Consent API に移行済みか、message format が WebOTP / standard SMS のどちらかに依存する。

---

# 参照（References）

## ドキュメント（Documentation）

- https://developer.android.com/about/versions/17/behavior-changes-all
- https://developer.android.com/reference/android/provider/Telephony.Sms.Intents#SMS_RECEIVED_ACTION
- https://developer.android.com/reference/android/provider/Telephony.Sms
- https://developer.android.com/identity/sms-retriever
- https://developers.google.com/identity/sms-retriever/user-consent/overview
- https://developer.android.com/about/versions/17/behavior-changes-17#sms-otp-protection
- https://developer.android.com/about/versions/17/behavior-changes-17

## AOSP

- 未確認。local `frameworks-base` に Android 17 AOSP tag がないため、tag diff による source evidence は未取得。

# OTP protection for standard SMS messages

## Metadata

### Android Versions

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP tag

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

### Behavior Change Source

Document:
https://developer.android.com/about/versions/17/behavior-changes-17

Related documents:
- https://developer.android.com/reference/android/provider/Telephony.Sms.Intents#SMS_RECEIVED_ACTION
- https://developer.android.com/reference/android/provider/Telephony.Sms
- https://developer.android.com/identity/sms-retriever
- https://developers.google.com/identity/sms-retriever/user-consent/overview
- https://developer.android.com/about/versions/17/behavior-changes-all#sms-otp-all-apps
- https://developer.android.com/about/versions/17/behavior-changes-all

Section:
OTP protection for standard SMS messages

Page type:
- Apps targeting Android 17 or higher

### Classification Snapshot

Primary classification:
- UNKNOWN_NEEDS_MORE_EVIDENCE

Initial applicability assumption from official documentation:
- 公式文書は、Android 17 以降で targetSdkVersion 37 以上の多くのアプリに対し、WebOTP / SMS Retriever format ではない標準 SMS のうち OTP を含むものを、受信後 3 時間は利用できないようにすると説明している。
- 3 時間の遅延中は `SMS_RECEIVED_ACTION` broadcast が withheld され、SMS provider database query が filtered される。
- 追加条件として、対象 SMS が OTP を含む standard SMS であること、アプリが exempted app ではないこと、WebOTP / SMS Retriever format ではないことがある。
- ただし、local `frameworks-base` に Android 17 AOSP tag がないため、OTP 判定、broadcast 抑止、provider filtering、targetSdkVersion gate、exemption 条件、Compat Change ID、default state は未検証である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

At-a-glance impact:

| Question | Answer | Evidence |
| --- | --- | --- |
| Android 17 OS update only? | Unknown | 公式文書は apps targeting Android 17 / API level 37 or higher と述べるが、AOSP gate 未確認。 |
| targetSdkVersion 37 required? | Likely, but unverified | 原文は most apps targeting Android 17 / API level 37 or higher と述べている。 |
| Additional runtime conditions? | Yes | OTP を含む standard SMS、WebOTP / SMS Retriever format ではない SMS、exempted app ではないこと。 |
| Compat Change ID involved? | Unknown | Android 17 tag と compat framework evidence が未確認。 |

### Investigation Date

2026-06-10

### Confidence

- Low

### Applicability Classification

Applies when:
- [ ] OS update / all apps on Android 17 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 37 on Android 17+
- [ ] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [x] Unknown / needs more evidence

Required runtime conditions:
- Android version: Android 17 以上が前提と考えられるが、AOSP tag 未取得。
- targetSdkVersion: 公式文書上は 37 以上。
- Device/form factor: 公式抜粋では条件なし。
- Permission/API/component condition: standard SMS message に OTP が含まれること、`SMS_RECEIVED_ACTION` broadcast、SMS provider database query、WebOTP / SMS Retriever format ではないこと、SMS Retriever / SMS User Consent APIs への移行。
- App state/process condition: SMS 受信後 3 時間以内に、対象アプリが SMS broadcast または SMS provider query から OTP SMS を読もうとする場合。

Compat framework:
- Change ID: Unknown
- Change name: Unknown
- Default state: Unknown
- Toggleable for testing: Unknown

Classification confidence:
- Low

Classification evidence:
- Official documentation page: `behavior-changes-17`
- Original applicability statement: most apps targeting Android 17 / API level 37 or higher, standard SMS messages containing an OTP, three-hour delay, exempted appsあり。
- AOSP targetSdk gate: 未確認。local `frameworks-base` に `android-17*` tag がない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# Executive Summary

Android 17 では、targetSdkVersion 37 以上の多くのアプリに対し、OTP を含む標準 SMS は受信から 3 時間経過するまで利用できない、と公式文書は説明している。遅延中は `SMS_RECEIVED_ACTION` broadcast が配信されず、SMS provider database query でも対象メッセージが filtered される。

この変更は、SMS inbox や SMS broadcast を直接読んで OTP を抽出しているアプリに影響する可能性がある。公式文書は、継続的な OTP 取得には SMS Retriever API または SMS User Consent API への移行を推奨している。

ただし、現時点の local `frameworks-base` には Android 17 AOSP tag がないため、実装差分、targetSdkVersion gate、OTP 判定、exemption 条件、Compat Change ID は未確認である。

---

# Original Documentation

## Statement

Page title:
- Behavior changes: Apps targeting Android 17 or higher

Page URL:
- https://developer.android.com/about/versions/17/behavior-changes-17

Page type:
- apps targeting Android 17

Section title:
- OTP protection for standard SMS messages

Original statement being verified:

> Beginning with Android 17, Android is extending its SMS OTP protection to apply to standard SMS messages (SMS messages containing an OTP that do not use the WebOTP or SMS Retriever formats). For most apps targeting Android 17 (API level 37) or higher, these SMS messages do not become available until three hours after receipt.

The supplied official text also states that during the three-hour delay, the `SMS_RECEIVED_ACTION` broadcast is withheld and SMS provider database queries are filtered. It lists exempted app categories such as the default SMS assistant app and connected device companion apps, and recommends SMS Retriever or SMS User Consent APIs for OTP extraction.

## Interpretation

この変更は、OTP を含む SMS をアプリが直接読む経路を制限する security / privacy behavior change である。従来、WebOTP / SMS Retriever format の OTP message に対して適用されていた保護を、Android 17 では標準 SMS にも広げる、と公式文書は説明している。

アプリ開発者にとって重要なのは、SMS inbox、SMS provider、`SMS_RECEIVED_ACTION` broadcast を利用して OTP を自動抽出する設計が、targetSdkVersion 37 更新後に 3 時間遅延する可能性がある点である。OTP は通常短時間で期限切れになるため、3 時間後に読めるようになっても認証用途としては実質的に利用できない可能性が高い。

---

# What Changed

公式文書上の変更点:
- Android 17 は SMS OTP protection を standard SMS messages に拡張する。
- 対象は OTP を含むが WebOTP format または SMS Retriever format を使わない SMS message。
- most apps targeting Android 17 / API level 37 or higher では、対象 SMS は受信後 3 時間経過するまで利用できない。
- 3 時間の遅延中、`SMS_RECEIVED_ACTION` broadcast は withheld される。
- 3 時間の遅延中、SMS provider database queries は filtered される。
- 対象 SMS は 3 時間経過後に利用可能になる。
- default SMS assistant app、connected device companion apps など一部アプリは遅延対象から exempted される。
- OTP 抽出に SMS を読むアプリは、SMS Retriever API または SMS User Consent API へ移行すべきと説明されている。
- WebOTP / SMS Retriever format messages に対する追加 SMS OTP protection は、target API level に関係なく全アプリへ適用される別項目として説明されている。

AOSP で未確認の点:
- Android 16 baseline で standard SMS の OTP が `SMS_RECEIVED_ACTION` と SMS provider query に即時反映されるか。
- Android 17 で standard SMS OTP を判定する classifier / parser。
- 受信時の broadcast withholding path。
- SMS provider query filtering path。
- 3 時間 delay の timer / availability state。
- targetSdkVersion 37 gate の実装箇所。
- exempted app の判定条件。
- WebOTP / SMS Retriever format と standard SMS の分岐条件。
- Compat Change ID と default state。

## Applicability

公式文書の一次判断では、Android 17 以上、targetSdkVersion 37 以上、OTP を含む standard SMS、WebOTP / SMS Retriever format ではないこと、exempted app ではないことが条件になる。AOSP tag が未取得のため、確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

### OS Update Behavior

- Android 17 にアップデートしただけで適用されるか: Unknown
- targetSdkVersion に依存しない根拠: この section の原文は most apps targeting Android 17 / API level 37 or higher と述べるため、targetSdkVersion 37 条件があると読むのが自然。ただし AOSP gate は未確認。
- Android 16 以前での挙動: 未確認。Android 17 tag との明示的な比較ができないため、Android 16 source だけから platform evidence として断定しない。

### targetSdkVersion 37 Behavior

- targetSdkVersion 37 以上で適用されるか: 公式文書上は Yes と読めるが、AOSP gate 未確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: Unknown。公式文書は Android 17 Behavior Changes として説明しているため、Android 17 platform behavior として扱う。
- opt-out / temporary override の有無: Unknown。公式文書は exempted app categories を示すが、app developer が任意に opt out できる仕組みは抜粋からは確認できない。compat framework による force enable / disable は未確認。

### Other Conditions

- device/form factor: 公式抜粋では条件なし。
- permission: SMS read / receive 関連 permission を持つ、または SMS provider / broadcast 経路を使うアプリが関係する可能性がある。正確な permission / AppOps gate は AOSP 未確認。
- API usage: `SMS_RECEIVED_ACTION` broadcast、`Telephony.Sms` provider query、OTP extraction、SMS Retriever API、SMS User Consent API。
- manifest attribute: `SMS_RECEIVED_ACTION` receiver、SMS / telephony permission declaration が関係する可能性があるが、AOSP 未確認。
- component boundary: telephony message receive pipeline、broadcast dispatch、SMS provider、app process、default SMS / companion app exemption にまたがる。

---

# AOSP Investigation

## Checkout Status

Commands checked before evidence use:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list 'android-17*'
```

Result:
- `frameworks-base` working tree: clean at the time of investigation.
- From tag: `android-16.0.0_r4` exists.
- To tag: no local `android-17*` tag found.

Evidence limitation:
- Android 17 AOSP tag が local `frameworks-base` に存在しないため、`git -C frameworks-base diff android-16.0.0_r4 <android-17-tag> -- ...` による明示的な tag 比較を実行できない。
- Repository rule に従い、Android 17 working tree や推測による source evidence は採用しない。
- この制約により、AOSP-backed conclusion は High confidence にできない。

## Related Files

未確認。Android 17 AOSP tag 取得後に、少なくとも以下の候補を tag 比較で確認する必要がある。

- `core/java/android/provider/Telephony.java`
- `core/java/android/provider/Telephony.Sms.Intents` 相当の API reference source
- broadcast / SMS provider access control に関係する `frameworks-base` 内の app-facing API definitions
- compat framework 定義ファイル内の SMS OTP / standard SMS / targetSdkVersion 37 関連 Change ID

Note:
- 実際の SMS 受信処理、SMS provider、telephony stack、OTP classifier は `frameworks-base` 以外の AOSP project にある可能性がある。ただし、この mission は `frameworks-base` evidence を対象としているため、Android 17 tag 入手後も `frameworks-base` 内で確認できる API surface、compat framework、broadcast / provider 関連定義を優先して記録する。

## Source Context Reviewed

Android 17 AOSP tag がないため、source context は未レビュー。

| File / symbol | Android 16 baseline | Android 17 behavior | Why this code path matters |
| --- | --- | --- | --- |
| Not reviewed | Not reviewed | Not reviewed | Android 17 tag がないため、公式文書の記述を AOSP diff で検証できない。 |

Required context:
- Entry point / caller: 未確認。想定される entry point は SMS 受信、`SMS_RECEIVED_ACTION` broadcast dispatch、`Telephony.Sms` provider query、OTP extraction だが、AOSP evidence としては未採用。
- Relevant class or service responsibility: 未確認。
- Runtime path from app API / system event to changed code: 未確認。
- Why unrelated code paths were excluded: Android 17 tag 不在のため、source path の採否判断自体を保留。

## Diff Interpretation

| Observed diff | Interpretation | Behavior Change relevance | Confidence |
| --- | --- | --- | --- |
| No Android 17 tag diff available | Source diff type cannot be classified yet | 公式文書の SMS OTP protection extension、broadcast withholding、provider filtering、3-hour delay、targetSdkVersion gate を source diff で裏取りできていない | Low |

Required interpretation:
- Added behavior: 未確認。
- Removed behavior: 未確認。
- Changed condition / gate: 未確認。
- Changed default: 未確認。
- No behavior change found: 未確認。tag 不在のため「no behavior change」とは判断しない。

## Evidence

Facts:
- 公式 Behavior Change 文書は、Android 17 から SMS OTP protection を standard SMS messages に拡張すると述べている。
- 公式文書は、standard SMS messages を「OTP を含み、WebOTP または SMS Retriever formats を使わない SMS messages」と説明している。
- 公式文書は、most apps targeting Android 17 / API level 37 or higher では、対象 SMS が受信後 3 時間まで利用可能にならないと述べている。
- 公式文書は、3 時間の遅延中に `SMS_RECEIVED_ACTION` broadcast が withheld され、SMS provider database queries が filtered されると述べている。
- 公式文書は、default SMS assistant app、connected device companion apps など一部アプリが exempted されると述べている。
- 公式文書は、OTP 抽出に SMS を読むアプリに SMS Retriever または SMS User Consent APIs への移行を推奨している。
- 公式文書は、WebOTP / SMS Retriever format messages に対する追加 SMS OTP protections は、target API level に関係なく全アプリへ適用される別項目として案内している。
- local `frameworks-base` には `android-16.0.0_r4` tag がある。
- local `frameworks-base` には `android-17*` tag がない。
- 調査時点で `frameworks-base` working tree は clean。

Observations:
- 公式ページ種別は targetSdkVersion 37 以上向けである。
- この項目は targetSdkVersion 37 条件に加えて、SMS message format、OTP 含有、exemption category、3 時間 delay という runtime / app category condition を含む。
- OTP の有効期限は一般に短いため、3 時間後に利用可能になっても OTP 自動入力機能としては成立しない可能性が高い。
- WebOTP / SMS Retriever format messages への保護は all apps page の別項目であり、この section の standard SMS behavior と混同しない必要がある。
- AOSP tag がないため、実装が本当に targetSdkVersion 37 gate で制御されているかは未確認。
- Compat framework entry の有無も未確認。

Hypotheses:
- Android 17 / targetSdkVersion 37 以上では、標準 SMS から OTP を直接抽出するアプリは、受信直後の broadcast と provider query の両方で対象 SMS を取得できなくなる可能性が高い。
- Android 17 / targetSdkVersion 36 のアプリでは、少なくともこの `behavior-changes-17` section の standard SMS delay は適用されない可能性があるが、AOSP gate 未確認のため断定しない。
- WebOTP / SMS Retriever format messages は別の all-apps 保護が適用されるため、targetSdkVersion 36 でも追加制限を受ける可能性がある。ただし、このレポートの主対象は standard SMS messages である。

Conclusions:
- 現時点で顧客向けに確定できるのは、「公式文書上は Android 17 / targetSdkVersion 37 以上の多くのアプリで、OTP を含む標準 SMS が受信後 3 時間まで broadcast / provider query 経由で利用できなくなる」という範囲まで。
- AOSP gate、OTP 判定、broadcast withholding、provider filtering、exemption 条件、compat framework default state が未確認のため、primary classification は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

## Applicability Gate Evidence

- targetSdkVersion gate: 未確認。公式文書は targetSdkVersion 37 以上を示すが、AOSP gate evidence はない。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。Android 17 tag がないため検索未実施。
- @EnabledAfter / @EnabledSince / default state: 未確認。Android 17 tag がないため検索未実施。
- Build.VERSION / SDK_INT gate: 未確認。
- DeviceConfig / resources config: 未確認。
- Permission/AppOps gate: 未確認。SMS provider / broadcast access と exemption 判定に permission / role / AppOps が関係する可能性はあるが、AOSP evidence はない。
- Manifest/property gate: 未確認。
- No gate found: 未確認。Android 17 tag がないため「gate がない」とは判断しない。
- Gate conclusion: Unknown。公式文書の wording から targetSdkVersion 37 + runtime conditions と推定されるが、AOSP で検証できていない。
- Reasoning from source context: source context 未レビューのため未確定。

---

# Impact Analysis

## Affected Apps

影響を受ける可能性があるアプリ:
- SMS inbox、SMS provider、または `SMS_RECEIVED_ACTION` broadcast から OTP を直接抽出しているアプリ。
- `READ_SMS` / `RECEIVE_SMS` 相当の SMS access を前提に、ログイン、本人確認、決済、アカウント復旧の OTP を自動入力しているアプリ。
- SMS Retriever / SMS User Consent API ではなく、独自 parser で標準 SMS 本文から OTP を抽出しているアプリ。
- targetSdkVersion 37 への更新を予定しており、OTP SMS 受信直後の処理に依存するアプリ。

## Non-Affected Apps

影響が限定的または対象外と考えられるケース:
- OTP SMS を読まないアプリ。
- SMS Retriever API または SMS User Consent API を使って OTP を取得しているアプリ。
- WebOTP / SMS Retriever format messages の扱いだけを確認している場合。ただし、これらには all-apps page の別保護があるため別途確認が必要。
- default SMS assistant app、connected device companion apps など公式文書が exempted と説明するカテゴリ。ただし、具体的な exemption 判定は AOSP 未確認。

---

# Customer Impact

顧客説明用。

## Impact Level

- Human decision required

※ 仮評価。最終判断は人間が行う。

## Business Impact

- ユーザー影響: OTP 自動入力が受信直後に動作せず、ログイン、サインアップ、本人確認、アカウント復旧の完了率が下がる可能性がある。
- 運用影響: OTP 配信 SMS の format、認証フロー、サポート問い合わせ、障害時の切り分け手順を見直す必要がある可能性がある。
- 開発影響: SMS Retriever API または SMS User Consent API への移行、SMS permission 依存の削減、targetSdkVersion 37 環境での認証テストが必要になる可能性がある。

---

# Required Actions

## Must

- SMS inbox、SMS provider query、`SMS_RECEIVED_ACTION` broadcast を使って OTP を読む箇所を棚卸しする。
- OTP 抽出に標準 SMS 本文の直接読み取りを使っている場合、SMS Retriever API または SMS User Consent API への移行計画を作る。
- Android 17 / targetSdkVersion 37 のテスト環境が利用可能になったら、OTP SMS 受信直後、3 時間未満、3 時間後の挙動を検証する。
- Android 17 AOSP tag 入手後に、targetSdkVersion gate、exemption 条件、compat Change ID を再確認する。

## Recommended

- OTP SMS format が SMS Retriever / WebOTP の要件を満たせるか、認証基盤側と確認する。
- OTP の有効期限が 3 時間 delay と整合しないことを前提に、直接 SMS 読み取りに依存しない fallback UX を設計する。
- default SMS / companion app のような exemption に依存する設計を避け、一般アプリとして成立する認証経路を採用する。
- Android 17 の all-apps SMS OTP protection と、この targetSdkVersion 37 向け standard SMS protection を別項目としてテストする。

## Optional

- SMS 権限を削減できる場合は、認証用途のためだけに SMS permission を保持していないか見直す。
- OTP 自動入力失敗時のログ、メトリクス、サポート文言を整備する。

---

# Verification Method

## Matrix

| Device OS | targetSdkVersion | Compat flag | Expected behavior |
| --- | --- | --- | --- |
| Android 16 | 36 | default | Android 16 baseline。standard SMS OTP が broadcast / provider query で即時利用できるかは Android 17 tag 比較待ち。 |
| Android 17 | 36 | default | Unknown。この section は targetSdkVersion 37+ 向けだが、AOSP gate 未確認。all-apps SMS OTP protection は別項目として確認が必要。 |
| Android 17 | 37 | default | 公式文書上は、most apps で standard SMS OTP が受信後 3 時間まで利用不可。`SMS_RECEIVED_ACTION` は withheld、SMS provider query は filtered。 |
| Android 17 | 36 | force-enabled if available | Unknown。Compat Change ID 未確認。 |
| Android 17 | 37 | force-disabled if available | Unknown。Compat Change ID 未確認。 |

## Steps

- targetSdk変更: targetSdkVersion 36 と 37 の test build を用意する。
- compat framework command: 未確認。Android 17 compat framework entry / Change ID が判明後に記録する。
- テスト方法: OTP を含む standard SMS、SMS Retriever format SMS、WebOTP format SMS を分けて送信し、broadcast 受信、provider query 結果、3 時間後の可視化を比較する。
- 再現手順: Android 17 device / emulator で対象アプリを install し、SMS 受信直後に `SMS_RECEIVED_ACTION` receiver と `Telephony.Sms` query の両方を確認する。3 時間経過後に再度 query する。
- 期待結果: targetSdkVersion 37 の most apps では、standard SMS OTP が 3 時間以内に broadcast / provider query から取得できない。exempted app と SMS Retriever / SMS User Consent path は別条件として確認する。

---

# Conclusion

公式文書上、Android 17 / targetSdkVersion 37 以上の多くのアプリでは、OTP を含む標準 SMS を直接読む OTP 自動抽出が受信後 3 時間遅延する可能性がある。SMS broadcast と SMS provider query の両方が制限対象として説明されているため、SMS Retriever API または SMS User Consent API への移行が主要な対応候補になる。

ただし、Android 17 AOSP tag が local checkout にないため、実装 gate、exemption、compat framework の確認は未完了である。最終的な適用分類と顧客向け確定説明は、Android 17 AOSP tag 入手後に再調査が必要である。

---

# Human Decision Placeholder

Final Priority:
- Human decision required

Final Severity:
- Human decision required

Release Readiness:
- Human decision required

Customer Communication Priority:
- Human decision required

Decision:
- Further investigation required

Decision notes:
- Android 17 AOSP tag 入手後に、AOSP evidence と compat framework evidence を確認してから最終判断する。

---

# References

## Documentation

- https://developer.android.com/about/versions/17/behavior-changes-17
- https://developer.android.com/reference/android/provider/Telephony.Sms.Intents#SMS_RECEIVED_ACTION
- https://developer.android.com/reference/android/provider/Telephony.Sms
- https://developer.android.com/identity/sms-retriever
- https://developers.google.com/identity/sms-retriever/user-consent/overview
- https://developer.android.com/about/versions/17/behavior-changes-all#sms-otp-all-apps
- https://developer.android.com/about/versions/17/behavior-changes-all

## AOSP

- Not available for Android 17 in local `frameworks-base`.
- From tag checked: `android-16.0.0_r4`
- To tag checked: no local `android-17*` tag found.

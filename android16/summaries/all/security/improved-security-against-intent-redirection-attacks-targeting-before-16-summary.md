# For applications compiling against Android 15 (API level 35) or lower - 1ページ要約（One Page Summary）

## 対象（Target）

Android 16 Behavior Change subsection

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Parent Behavior Change:
- Improved security against Intent redirection attacks

Grandparent subsection:
- Opt out of Intent redirection handling

Subsection:
- For applications compiling against Android 15 (API level 35) or lower

Official documentation:
- https://developer.android.com/about/versions/16/behavior-changes-all#targeting-before-16

Category:
- Security

## 適用条件（Applicability）

- 主分類（Primary classification）: `OS_UPDATE_ALL_APPS`
- OS アップデート / 全アプリ（OS update / all apps）: Yes / Conditional。親項目の Android 16 Intent redirection hardening に関係する。
- targetSdkVersion 36 以上: No。targetSdkVersion 36 は reflection fallback の runtime gate ではない。
- compileSdkVersion 35 以下: この subsection の中心条件。direct API 参照ができない場合の reflection fallback。
- compileSdkVersion 36 以上: sibling subsection の direct API path。
- runtime 条件: nested / sub-level Intent launch が default hardening 対象になり、アプリが reflection で `removeLaunchSecurityProtection()` を呼ぶ場合。

## 要約（Summary）

この subsection は Android 16 default hardening そのものではなく、compileSdkVersion 35 以下のアプリが `Intent#removeLaunchSecurityProtection()` を reflection で呼ぶ fallback guidance である。

公式文書は reflection を「可能だが非推奨」とし、将来 API 変更に弱いこと、可能なら compileSdkVersion 36 以上に更新して direct API を使うことを勧めている。AOSP では method body が missing / invalid creator token flag と creator token info を削除することを確認した。

## Anchor / Documentation Note

- requested anchor: `#targeting-before-16`
- 現行公式 HTML では `targeting-before-16` 文字列は確認できなかった。
- 最寄りの公式内容は `Opt out of Intent redirection handling` 配下の “For applications compiling against Android 15 (API level 35) or lower” subsection。

## Facts / Observations / Hypotheses / Conclusions

Facts:
- Android 16 `Intent#removeLaunchSecurityProtection()` は public flagged API として存在する。
- 実装は `EXTENDED_FLAG_MISSING_CREATOR_OR_INVALID_TOKEN` と creator token info を削除する。
- Android 15 / Android 16 の両 AOSP tag の `current.txt` に flagged method が見える。

Observations:
- reflection fallback は compile-time API availability の回避策であり、security risk の回避策ではない。
- opt-out は app-wide ではなく specific Intent object/state に対する操作である。

Hypotheses:
- Android 16 実機では reflection lookup / invocation が成功すれば direct API と同等に opt-out し得る。
- Android 15 実機での挙動は SDK artifact / device image / flag state の検証が必要。

Conclusions:
- reflection fallback は例外的・暫定的対応に限定すべき。
- 長期対応は compileSdkVersion 36 への移行と nested Intent validation、最終的には opt-out 削除である。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ | 期待挙動 |
| --- | --- |
| Android 16 / targetSdkVersion 35 / compileSdkVersion 35 以下 / no opt-out | default hardening が残る |
| Android 16 / targetSdkVersion 36 / compileSdkVersion 35 以下 / no opt-out | targetSdkVersion 35 と同様 |
| Android 16 / targetSdkVersion 35 / reflection opt-out | reflection 成功時のみ opt-out |
| Android 16 / targetSdkVersion 36 / reflection opt-out | targetSdkVersion 35 と同様 |
| Android 16 / compileSdkVersion 36 以上 | direct API path。reflection 不要 |
| Android 16 / reflection succeeds | missing flag / creator token info が削除され得る |
| Android 16 / reflection fails | opt-out されない。fallback 必須 |
| Android 16 / untrusted nested Intent | reflection opt-out すべきではない |
| Android 16 / allowlisted first-party nested Intent | 例外候補。security review 必須 |
| Android 15 / targetSdkVersion 36 | 実機比較が必要 |

## 影響対象（Who Is Affected）

- compileSdkVersion 35 以下のアプリ
- compileSdkVersion 36 へまだ更新できないアプリ
- nested Intent forwarding を持つアプリ
- Intent router / dispatcher Activity を持つアプリ
- auth callback / deep link / SSO / payment flow を中継するアプリ
- URI grant / ClipData を伴う Intent を forwarding するアプリ
- reflection fallback を検討しているアプリ
- security review なしに opt-out すると危険なアプリ

## 推奨対応候補（Recommended Action Candidates）

- reflection fallback を使う前に nested Intent validation を修正する。
- reflection opt-out は first-party / allowlisted flow に限定する。
- reflection failure を log / telemetry に残す。
- compileSdkVersion 36 へ移行し、direct API path にする。
- direct API 化後も opt-out を広げず、最終的には opt-out 削除を目指す。

## テスト観点（Test Viewpoints）

- Android 15 / targetSdkVersion 35
- Android 16 / targetSdkVersion 35
- Android 16 / targetSdkVersion 36
- Android 15 / targetSdkVersion 36
- compileSdkVersion 35 以下 reflection fallback
- compileSdkVersion 36 direct API
- `getDeclaredMethod()` success / failure
- `NoSuchMethodException` / `InvocationTargetException` / `IllegalAccessException`
- trusted / untrusted nested Intent
- URI grant flags / ClipData URI
- `startActivity()` / `startActivityForResult()`
- PendingIntent / chooser / selector
- validation before launch / forwarding without validation
- opt-out scope が想定 flow に限定されていること
- compileSdkVersion 36 移行後に同等挙動になること

## Human Decision Placeholder

最終優先度（Final Priority）:
- TBD by human

最終 severity（Final Severity）:
- TBD by human

顧客説明優先度（Customer communication priority）:
- TBD by human

reflection fallback 許可方針（Reflection fallback approval policy）:
- TBD by human

リリース判定（Release readiness decision）:
- TBD by human

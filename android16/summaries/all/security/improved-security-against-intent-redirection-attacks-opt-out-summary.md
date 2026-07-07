# Opt out of Intent redirection handling - 1ページ要約（One Page Summary）

## 対象（Target）

Android 16 Behavior Change

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Parent Behavior Change:
- Improved security against Intent redirection attacks

Subsection:
- Opt out of Intent redirection handling

Official documentation:
- https://developer.android.com/about/versions/16/behavior-changes-all#opt-out

Category:
- Security

## 適用条件（Applicability）

- 主分類（Primary classification）: `OS_UPDATE_ALL_APPS`
- OS アップデート / 全アプリ（OS update / all apps）: Yes / Conditional。Android 16 default Intent redirection hardening の一部として扱う。
- targetSdkVersion 36 以上: No。targetSdkVersion 36 は opt-out API の runtime gate ではない。
- compileSdkVersion 36 以上: `Intent#removeLaunchSecurityProtection()` を直接呼べる。
- compileSdkVersion 35 以下: reflection fallback は公式文書上可能だが非推奨。
- その他の必須条件（Other required conditions）: nested / sub-level Intent launch に Android 16 hardening がかかり、アプリが対象 Intent object に明示的に opt-out を行う場合。

## 要約（Summary）

Android 16 は Intent redirection attack に対する launch security protection を既定で提供する。`Opt out of Intent redirection handling` は、その protection が正当な互換性 flow を妨げる場合に、対象 Intent object から protection を外すための例外 API を説明する subsection である。

AOSP では `Intent#removeLaunchSecurityProtection()` が `EXTENDED_FLAG_MISSING_CREATOR_OR_INVALID_TOKEN` を消し、creator token info を削除することを確認した。これは security protection を弱める操作なので、通常の推奨対応は opt-out ではなく nested Intent の allowlist validation である。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 期待挙動（Expected behavior） |
| --- | --- |
| Android 16 / targetSdkVersion 35 / no opt-out | nested Intent Activity launch が default hardening 対象になり得る |
| Android 16 / targetSdkVersion 36 / no opt-out | targetSdkVersion 35 と同様 |
| Android 16 / `removeLaunchSecurityProtection()` called | 対象 Intent object の creator token protection を外す |
| Android 16 / compileSdkVersion 36 | direct API call が可能 |
| Android 16 / compileSdkVersion 35 以下 | reflection fallback は可能とされるが非推奨 |
| Android 15 / targetSdkVersion 36 | 要検証。AOSP tag には flagged symbol があるが、Android 16 公式挙動とは分ける |
| nested Intent from untrusted external source | opt-out すべきではない |
| allowlisted first-party nested Intent | 例外的 opt-out 候補。ただし security review 必須 |
| startActivity nested Intent | confirmed Activity launch enforcement path |
| startService / bindService / sendBroadcast nested Intent | Activity と同等 enforcement は未確認 |

## 顧客影響（Customer Impact）

影響を受けやすいのは、外部または SDK から受け取った Intent extras から nested Intent を取り出し、`startActivity()` などで launch するアプリである。互換性問題が出た場合でも、広く opt-out するのではなく、Intent の origin / component / package / action / data / flags / ClipData / URI grants を検証する必要がある。

## Facts / Observations / Hypotheses / Conclusions

Facts:
- `Intent#removeLaunchSecurityProtection()` は Android 16 AOSP に public flagged API として存在する。
- 実装は missing / invalid creator token flag と creator token info を削除する。
- `ActivityStarter` には Change ID `29623414` の hardening action path がある。

Observations:
- opt-out は app-wide ではなく specific Intent object/state に対する操作である。
- compileSdkVersion 36 は直接 API 参照の条件で、targetSdkVersion 36 gate ではない。

Hypotheses:
- Android 15 実機での direct / reflection call は device image と flag state に依存するため実機確認が必要。
- service / broadcast での同等 enforcement は追加調査が必要。

Conclusions:
- opt-out は例外的な互換性回避策であり、通常の修正方針ではない。
- broad opt-out は Intent redirection vulnerability risk を増やす。

## 推奨対応候補（Recommended Action Candidates）

- nested Intent forwarding 箇所を棚卸しする。
- allowlist validation または `IntentSanitizer` 相当の sanitizer を使う。
- URI grant flags / ClipData URI を必要最小限にする。
- `removeLaunchSecurityProtection()` は first-party / allowlisted flow に限定する。
- opt-out 使用箇所は threat model と code review を必須にする。

## テスト観点（Test Viewpoints）

- Android 15 / targetSdkVersion 35
- Android 16 / targetSdkVersion 35
- Android 16 / targetSdkVersion 36
- Android 15 / targetSdkVersion 36 が検証可能な場合
- compileSdkVersion 36 direct API
- compileSdkVersion 35 以下 reflection fallback
- trusted / untrusted nested Intent
- explicit component / implicit action / package set
- `exported=false` / permission-protected component targeting
- URI grant flags / ClipData URI
- opt-out called / not called
- validation before launch / forwarding without validation
- logcat / exception / launch failure / user-visible fallback

## Human Decision Placeholder

最終優先度（Final Priority）:
- TBD by human

最終 severity（Final Severity）:
- TBD by human

顧客説明優先度（Customer communication priority）:
- TBD by human

opt-out 許可方針（Opt-out approval policy）:
- TBD by human

リリース判定（Release readiness decision）:
- TBD by human

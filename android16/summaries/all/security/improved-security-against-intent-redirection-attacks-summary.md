# Improved security against Intent redirection attacks - 1ページ要約（One Page Summary）

## 対象（Target）

Android 16 Behavior Change

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Behavior Change:
- Improved security against Intent redirection attacks

Official documentation:
- https://developer.android.com/about/versions/16/behavior-changes-all#intent-redirect-attacks

Category:
- Security

## 適用条件（Applicability）

- 主分類（Primary classification）: `OS_UPDATE_ALL_APPS`
- OS アップデート / 全アプリ（OS update / all apps）: Yes。Android 16 all apps ページ掲載で、AOSP confirmed path に targetSdkVersion 36 gate は見つからない。
- targetSdkVersion 36 以上: No。targetSdkVersion 36 は適用条件ではない。
- その他の必須条件（Other required conditions）: untrusted / external input 由来の top-level Intent から extras / ClipData 内の nested Intent を取り出し、Activity launch する flow。
- Compat Change ID: `29623414` (`ENABLE_PREVENT_INTENT_REDIRECT_TAKE_ACTION`)
- Compat default state: AOSP annotation は `@ChangeId` / `@Overridable`。公式 compat framework 一覧では未確認。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 16 / targetSdkVersion 35 | nested Intent activity launch hardening の対象になり得る |
| Android 16 / targetSdkVersion 36 | targetSdkVersion 35 と同様。targetSdkVersion 36 固有ではない |
| Android 15 / targetSdkVersion 36 | 要検証。AOSP tag には flagged implementation があるが、Android 16 公式挙動とは分ける |
| compileSdkVersion 36 | `Intent#removeLaunchSecurityProtection()` を直接呼べる |
| compileSdkVersion 35 以下 | reflection fallback は可能と公式文書にあるが非推奨 |
| removeLaunchSecurityProtection() called | その Intent object の launch security protection を弱めるため要 security review |

## 要約（Summary）

Android 16 は、攻撃者が制御する top-level Intent の extras / ClipData 内にある nested Intent を、被害アプリが自分の context で Activity launch する Intent redirection attack に対して既定の hardening を提供する。

AOSP では nested Intent creator token、missing / invalid token flag、creator UID/package に基づく Activity launch permission / URI grant 再検証、`removeLaunchSecurityProtection()` opt-out API を確認した。

## 顧客影響（Customer Impact）

- 影響あり: nested Intent forwarding / router / dispatcher pattern を持つアプリ。
- 影響軽微: 通常の explicit / implicit Intent launch だけのアプリ。
- 要確認: service / bind / broadcast で nested Intent forwarding を使うアプリ。今回 confirmed enforcement は Activity launch path。

## 影響対象（Who Is Affected）

- deep link router / navigation router
- OAuth / SSO / authentication redirect handler
- notification click / workflow router
- share target / file open / document handoff
- nested Intent extras を受け取って launch するアプリ
- private / non-exported component を内部 Intent で起動するアプリ
- URI permission grant / ClipData を伴う Intent forwarding
- plugin framework / mini app / SDK dispatcher / cross-app workflow
- SDK / library が nested Intent forwarding を内部利用するアプリ

## 対応要否（Required Action）

- 必須対応: untrusted nested Intent をそのまま launch している箇所は修正候補。
- 推奨対応: component / package / action / data / categories / flags / ClipData / URI grants を allowlist validation する。`IntentSanitizer` または同等の sanitizer を検討する。
- 非推奨: 互換性問題を広く `removeLaunchSecurityProtection()` で回避すること。必要な場合も first-party / allowlisted flow に限定する。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 15 | 35 | Android 16 公式挙動とは分けて baseline を確認 |
| Android 16 | 35 | unsafe nested Intent Activity launch が hardening 対象になり得る |
| Android 16 | 36 | targetSdkVersion 35 と同様 |
| Android 15 | 36 | 技術的に検証可能なら比較。Android 16 OS update impact と混同しない |

追加テスト:
- nested Intent in extras / Parcelable array / Parcelable list / ClipData
- exported / non-exported / permission-protected component
- URI grant flags / ClipData URI
- `removeLaunchSecurityProtection()` called / not called
- compileSdkVersion 36 direct API / compileSdkVersion 35 reflection fallback
- malicious input blocked / legitimate flow still works

## 顧客向け説明（Explanation for Customers）

この変更は targetSdkVersion 36 化だけで発生するものではなく、Android 16 OS 上で unsafe nested Intent forwarding を行う場合に影響します。外部アプリから受け取った Intent の extras に入っている Intent をそのまま `startActivity()` するような実装は、Android 16 で block / exception / abort の対象になる可能性があります。

対応は opt-out API の利用ではなく、nested Intent を launch する前に allowlist validation することが基本です。`removeLaunchSecurityProtection()` は互換性上どうしても必要な例外 flow に限定し、security review を行ってください。

## 根拠（Evidence）

- Official documentation: Android 16 all apps / Security / Improved security against Intent redirection attacks
- AOSP files:
  - `core/java/android/content/Intent.java`
  - `core/java/android/content/ClipData.java`
  - `core/java/android/app/ContextImpl.java`
  - `core/java/android/app/Instrumentation.java`
  - `services/core/java/com/android/server/am/ActivityManagerService.java`
  - `services/core/java/com/android/server/wm/ActivityStarter.java`
  - `core/java/android/security/responsible_apis_flags.aconfig`
  - `core/tests/coretests/src/android/content/IntentTest.java`
  - `services/tests/mockingservicestests/src/com/android/server/am/ActivityManagerServiceTest.java`
- AOSP source context:
  - `Intent#collectExtraIntentKeys()` / `checkCreatorToken()` / `removeLaunchSecurityProtection()`
  - `ActivityManagerService#addCreatorToken()`
  - `ActivityStarter` Activity launch permission / URI grant / token enforcement
- Diff interpretation:
  - Android 16 diff adds server-side nested-key collection, ClipData token verification, structured stats logging.
  - targetSdkVersion 36 gate は見つからない。
  - Android 15 tag にも flagged implementation があるため baseline は要注意。
- Gate conclusion:
  - Android 16 OS 上、nested Intent Activity launch pattern を持つ全アプリに影響し得る。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Critical / High / Medium / Low

判断（Decision）:
- Explain / Monitor / Ignore / Further investigation required

顧客説明優先度（Customer communication priority）:
- TBD by human

リリース判定（Release readiness decision）:
- TBD by human

## 再検証記録（2026-08-22）

- Android 16 の公式 Behavior Change 一覧と最新通常AOSPタグを再確認した。
- 対応する[主レポート](../../../behavior-changes/all/security/improved-security-against-intent-redirection-attacks.md)で official section、AOSP project / remote / checkout、解決済み commit、比較 command、dirty risk を再検証した。
- 主レポートの分類、confidence、未確認事項を維持し、実機未実施の項目を Observed 済みへ変更していない。
- 全件の結果は[再検証台帳](../../../analysis/REVALIDATION_2026-08-22.md)を参照する。

# Enforce strict SQL checks in CP2 - One Page Summary

## Target

Android 17 Behavior Change

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP tag

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

## Applicability

- Primary classification: UNKNOWN_NEEDS_MORE_EVIDENCE
- OS update / all apps: Unknown。原文は targetSdkVersion 37+ を明示しているが、AOSP gate 未確認。
- targetSdkVersion 37+: 公式文書上は該当。AOSP gate 未確認。
- Other required conditions: `READ_CONTACTS` permission なし、`ContactsContract.Data` table query、strict columns / strict grammar と互換性のない query pattern。
- Compat Change ID: Unknown
- Compat default state: Unknown

## At-a-Glance Matrix

| Scenario | Impact |
| --- | --- |
| Android 17 / targetSdkVersion 36 | Unknown。この section は targetSdkVersion 37+ 向けだが、AOSP gate 未確認。 |
| Android 17 / targetSdkVersion 37 | 公式文書上、`READ_CONTACTS` なしの `ContactsContract.Data` query に strict SQL validation が適用される。 |
| Android 17 / targetSdkVersion 37 + required conditions | strict columns / grammar と非互換の query は rejected され、exception が発生する。 |

## Summary

Android 17 では、targetSdkVersion 37 以上のアプリが `READ_CONTACTS` なしで `ContactsContract.Data` table を query する場合、CP2 が strict SQL checks を強制する、と公式文書は説明している。

## Customer Impact

- 要確認

## Who Is Affected

- 対象アプリ: `READ_CONTACTS` permission なしで Contacts Provider の `ContactsContract.Data` を query しているアプリ。
- 対象機能: contacts search、lookup、候補表示、matching、連携機能。
- 対象条件: targetSdkVersion 37 以上、permission denied / not granted、strict SQL と互換性のない projection / selection / sort order。

## Required Action

- 必須対応: `ContactsContract.Data` query と `READ_CONTACTS` permission なしで実行される path を棚卸しする。
- 推奨対応: query を documented columns と parameterized selection に寄せ、strict columns / strict grammar と互換性のある形へ修正する。
- 不要: Contacts Provider を使わないアプリ、または `ContactsContract.Data` を permission なしで query しないアプリでは直接影響は限定的。

## Test Matrix

| Device OS | targetSdkVersion | Expected behavior |
| --- | --- | --- |
| Android 16 | 36 | Android 16 baseline。具体挙動は Android 17 tag 比較待ち。 |
| Android 17 | 36 | Unknown。この section は targetSdkVersion 37+ 向けだが、AOSP gate 未確認。 |
| Android 17 | 37 | `READ_CONTACTS` なし Data query で strict validation が適用され、非互換 query は exception と公式文書は説明。 |

## Explanation for Customers

Android 17 では、targetSdkVersion 37 以上のアプリが `READ_CONTACTS` permission を持たずに `ContactsContract.Data` table を query する場合、CP2 が `StrictColumns` と `StrictGrammar` を有効にします。これにより、provider が許容しない column や SQL grammar に依存した query は拒否され、exception が発生します。

Contacts Provider への query は documented columns と安全な selection pattern に寄せ、permission なしで動く path を targetSdkVersion 37 環境で検証してください。現時点では local AOSP checkout に Android 17 tag がないため、targetSdkVersion gate、実際の exception type、compat flag の有無は未確認です。

## Evidence

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-17
- Original statement: targetSdkVersion 37 以上のアプリでは、`READ_CONTACTS` なしで `ContactsContract.Data` table にアクセスする場合、CP2 が strict SQL query validation を強制し、非互換 query は rejected され exception が throw される。
- AOSP files: 未確認。local `frameworks-base` に `android-17*` tag がない。
- AOSP source context: 未確認。tag 間 diff が実行できない。
- Diff interpretation: 未分類。公式文書上は added behavior / changed condition と読めるが、AOSP diff による確認は Android 17 tag 待ち。
- Gate conclusion: Unknown。公式文書は targetSdkVersion 37+ と `READ_CONTACTS` permission condition を示すが、AOSP gate evidence は未取得。

## Human Decision

Final Priority:
- Human decision required

Decision:
- Further investigation required

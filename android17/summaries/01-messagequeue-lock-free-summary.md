# New lock-free implementation of MessageQueue - One Page Summary

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
- OS update / all apps: Unknown。公式文書は all apps ページではなく、apps targeting Android 17 or higher ページに掲載。
- targetSdkVersion 37+: 公式文書上は該当。ただし AOSP gate 未確認。
- Other required conditions: `MessageQueue` private field / private method への reflection が互換性リスク条件。
- Compat Change ID: Unknown
- Compat default state: Unknown

## At-a-Glance Matrix

| Scenario | Impact |
| --- | --- |
| Android 17 / targetSdkVersion 36 | Unknown。公式文書上は targetSdkVersion 37 以上向けだが、AOSP gate 未確認。 |
| Android 17 / targetSdkVersion 37 | 新しい lock-free `MessageQueue` 実装が適用されると公式文書は説明。private reflection は破損リスクあり。 |
| Android 17 / targetSdkVersion 37 + required conditions | `MessageQueue` private field / private method を reflection している場合、crash や監視機能不具合の可能性がある。 |

## Summary

Android 17 では、targetSdkVersion 37 以上のアプリに新しい lock-free `android.os.MessageQueue` 実装が適用される、と公式文書は説明している。通常の public API 利用よりも、private field / private method への reflection が互換性リスクになる。

## Customer Impact

- 要確認

## Who Is Affected

- 対象アプリ: targetSdkVersion 37 への更新を予定している Android アプリ。
- 対象機能: main thread monitoring、message queue instrumentation、ANR / jank monitoring、performance diagnostics。
- 対象条件: 自社コードまたは SDK が `MessageQueue` の private implementation detail に reflection している場合。

## Required Action

- 必須対応: `MessageQueue` private field / private method への reflection 利用を棚卸しする。
- 推奨対応: 該当箇所を public API ベースに移行し、SDK を Android 17 対応版に更新する。
- 不要: public API のみを使っており、関連 SDK も private reflection していないことを確認できる場合は、互換性対応は限定的。

## Test Matrix

| Device OS | targetSdkVersion | Expected behavior |
| --- | --- | --- |
| Android 16 | 36 | Android 16 baseline。Android 17 の lock-free implementation は対象外。 |
| Android 17 | 36 | Unknown。公式文書上は旧挙動維持が期待されるが、AOSP gate 未確認。 |
| Android 17 | 37 | 公式文書上は新しい lock-free `MessageQueue` 実装が適用される。 |

## Explanation for Customers

Android 17 では、targetSdkVersion 37 以上のアプリに対して `MessageQueue` の内部実装が変わる予定です。性能改善が目的の変更ですが、`MessageQueue` の private field や private method を reflection で参照しているコードは、内部構造の変更により壊れる可能性があります。まず自社コードと組み込み SDK の reflection 利用を確認し、targetSdkVersion 37 更新前に Android 17 で実機または emulator テストを行う必要があります。

ただし、現時点では local AOSP checkout に Android 17 tag がないため、targetSdkVersion gate や compat flag の有無は未確認です。最終的な適用分類は Android 17 AOSP tag 公開後に再確認が必要です。

## Evidence

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-17
- Related guidance: https://developer.android.com/about/versions/17/changes/messagequeue
- API reference: https://developer.android.com/reference/android/os/MessageQueue
- Original statement: Android 17 から targetSdkVersion 37 以上のアプリが新しい lock-free `MessageQueue` 実装を受け取り、private field / method reflection client が壊れる可能性がある。
- AOSP files: 未確認。local `frameworks-base` に `android-17*` tag がない。
- AOSP source context: 未確認。tag 間 diff が実行できない。
- Diff interpretation: 未分類。added behavior / changed condition / changed default の判定は Android 17 tag 待ち。
- Gate conclusion: Unknown。公式文書は targetSdkVersion 37 以上を示すが、AOSP gate evidence は未取得。

## Human Decision

Final Priority:
- Human decision required

Decision:
- Further investigation required

# Static final fields are now unmodifiable - One Page Summary

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
- OS update / all apps: Unknown。公式文書は Android 17+ と targetSdkVersion 37+ の両方を条件としている。
- targetSdkVersion 37+: 公式文書上は該当。ただし AOSP gate 未確認。
- Other required conditions: static final field を reflection または JNI で変更しようとする場合。
- Compat Change ID: Unknown
- Compat default state: Unknown

## At-a-Glance Matrix

| Scenario | Impact |
| --- | --- |
| Android 17 / targetSdkVersion 36 | Unknown。公式文書上は targetSdkVersion 37 以上向けだが、AOSP gate 未確認。 |
| Android 17 / targetSdkVersion 37 | static final field 変更が拒否されると公式文書は説明。 |
| Android 17 / targetSdkVersion 37 + required conditions | reflection では `IllegalAccessException`、JNI では app crash の可能性がある。 |

## Summary

Android 17 では、Android 17 以上で動作し targetSdkVersion 37 以上のアプリが static final field を実行時に変更できなくなる、と公式文書は説明している。影響は reflection または JNI で static final field を書き換えるコードに集中する。

## Customer Impact

- 要確認

## Who Is Affected

- 対象アプリ: targetSdkVersion 37 への更新を予定している Android アプリ。
- 対象機能: feature flag override、SDK 内部値の変更、hot patch、mocking、hooking、diagnostics、native instrumentation。
- 対象条件: 自社コードまたは SDK が reflection / JNI で static final field を変更している場合。

## Required Action

- 必須対応: static final field の runtime write を棚卸しする。
- 推奨対応: mutable config、dependency injection、server-side config など、static final field 書き換えに依存しない設計へ移行する。
- 不要: static final field を読み取るだけで変更せず、関連 SDK も runtime write していないことを確認できる場合は、互換性対応は限定的。

## Test Matrix

| Device OS | targetSdkVersion | Expected behavior |
| --- | --- | --- |
| Android 16 | 36 | Android 16 baseline。具体挙動は Android 17 tag 比較待ち。 |
| Android 17 | 36 | Unknown。公式文書上は旧挙動維持が期待されるが、AOSP gate 未確認。 |
| Android 17 | 37 | 公式文書上は static final field 変更が拒否される。 |

## Explanation for Customers

Android 17 では、targetSdkVersion 37 以上のアプリに対して static final field の実行時変更が禁止される予定です。reflection で変更しようとした場合は `IllegalAccessException`、JNI API で変更しようとした場合はアプリ crash になると公式文書は説明しています。自社コードだけでなく、組み込み SDK や native library が static final field を書き換えていないか確認する必要があります。

ただし、現時点では local AOSP checkout に Android 17 tag がないため、targetSdkVersion gate や compat flag の有無は未確認です。最終的な適用分類は Android 17 AOSP tag 公開後に再確認が必要です。

## Evidence

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-17
- Original statement: Android 17+ で動作し targetSdkVersion 37+ のアプリは static final field を変更できない。reflection では `IllegalAccessException`、JNI では crash。
- AOSP files: 未確認。local `frameworks-base` に `android-17*` tag がない。
- AOSP source context: 未確認。tag 間 diff が実行できない。
- Diff interpretation: 未分類。added behavior / changed condition / changed default の判定は Android 17 tag 待ち。
- Gate conclusion: Unknown。公式文書は Android 17+ / targetSdkVersion 37+ / static final field write を条件として示すが、AOSP gate evidence は未取得。

## Human Decision

Final Priority:
- Human decision required

Decision:
- Further investigation required

# Platform API changes to ignore orientation, resizability and aspect ratio constraints on large screens (sw>=600dp) - One Page Summary

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
- OS update / all apps: Unknown。原文は Android 17 / targetSdkVersion 37+ で opt-out unavailable と述べるが、AOSP gate 未確認。
- targetSdkVersion 37+: 公式文書上は該当。AOSP gate 未確認。
- Other required conditions: large screens (`sw >= 600dp`)、orientation / resizability / aspect ratio constraints、Android 16 opt-out 利用。
- Compat Change ID: Unknown
- Compat default state: Unknown

## At-a-Glance Matrix

| Scenario | Impact |
| --- | --- |
| Android 17 / targetSdkVersion 36 | Unknown。Android 16 / SDK 36 opt-out が維持されるか AOSP 未確認。 |
| Android 17 / targetSdkVersion 37 | 公式文書上、SDK 36 で使えた opt-out が利用不可。 |
| Android 17 / targetSdkVersion 37 + required conditions | large screen で orientation / resizability / aspect ratio constraints が無視される可能性。 |

## Summary

Android 17 では、targetSdkVersion 37 以上のアプリで、Android 16 / SDK 36 では可能だった large screen 制約無視への opt-out が利用できなくなる、と公式文書は説明している。

## Customer Impact

- 要確認

## Who Is Affected

- 対象アプリ: large screen で固定向き、固定 aspect ratio、non-resizable を前提にしているアプリ。
- 対象機能: tablet / foldable / desktop windowing / multi-window 上の Activity 表示。
- 対象条件: `sw >= 600dp`、targetSdkVersion 37 以上、Android 16 opt-out 依存、orientation / resizability / aspect ratio constraints の指定。

## Required Action

- 必須対応: Android 16 opt-out 利用状況と manifest の orientation / resizability / aspect ratio 制約を棚卸しする。
- 推奨対応: large screen で adaptive layout、configuration change、multi-window resize、fold / unfold を検証する。
- 不要: large screen で利用されず、固定向き・固定比率・非リサイズ制約に依存しないアプリでは直接影響は限定的。

## Test Matrix

| Device OS | targetSdkVersion | Expected behavior |
| --- | --- | --- |
| Android 16 | 36 | 公式文書上、large screen 制約無視は導入済みだが opt-out 可能。 |
| Android 17 | 36 | Unknown。SDK 36 opt-out が維持されるか AOSP 未確認。 |
| Android 17 | 37 | opt-out は利用不可。large screen 上で orientation / resizability / aspect ratio restrictions が無視されると公式文書は説明。 |

## Explanation for Customers

Android 16 では、targetSdkVersion 36 以上のアプリについて、`sw >= 600dp` の large screen で orientation、resizability、aspect ratio constraints を platform が無視する変更が導入されました。SDK 36 では opt-out が可能でしたが、Android 17 / targetSdkVersion 37 以上ではその opt-out が利用できなくなります。

固定 portrait、non-resizable、固定 aspect ratio を前提にした UI は、tablet、foldable、desktop windowing で表示崩れや想定外のリサイズが起きる可能性があります。現時点では local AOSP checkout に Android 17 tag がないため、targetSdkVersion gate、opt-out removal の実装、compat flag の有無は未確認です。

## Evidence

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-17
- Original statement: Android 16 で API level 36+ 向けに large screens (`sw >= 600dp`) で orientation / aspect ratio / resizability restrictions を無視する変更が導入され、SDK 36 では opt-out 可能だったが、Android 17 / API level 37+ では opt-out 不可。
- AOSP files: 未確認。local `frameworks-base` に `android-17*` tag がない。
- AOSP source context: 未確認。tag 間 diff が実行できない。
- Diff interpretation: 未分類。公式文書上は opt-out removal / changed condition と読めるが、AOSP diff による確認は Android 17 tag 待ち。
- Gate conclusion: Unknown。公式文書は targetSdkVersion 37+ と large screen condition を示すが、AOSP gate evidence は未取得。

## Human Decision

Final Priority:
- Human decision required

Decision:
- Further investigation required

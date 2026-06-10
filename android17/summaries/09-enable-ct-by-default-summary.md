# Enable CT by default - One Page Summary

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
- Other required conditions: TLS / HTTPS 通信、certificate transparency policy、Network Security Config、証明書チェーン。
- Compat Change ID: Unknown
- Compat default state: Unknown

## At-a-Glance Matrix

| Scenario | Impact |
| --- | --- |
| Android 17 / targetSdkVersion 36 | Unknown。この section は targetSdkVersion 37+ 向けだが、AOSP gate 未確認。 |
| Android 17 / targetSdkVersion 37 | 公式文書上は CT が default enabled。 |
| Android 17 / targetSdkVersion 37 + required conditions | CT 要件を満たさない証明書チェーンを使う HTTPS 接続で失敗する可能性。 |

## Summary

Android 17 では、targetSdkVersion 37 以上のアプリで certificate transparency (CT) が default enabled になる、と公式文書は説明している。

## Customer Impact

- 要確認

## Who Is Affected

- 対象アプリ: targetSdkVersion 37 へ更新し、platform TLS / HTTPS 通信を行うアプリ。
- 対象機能: API 通信、ログイン、決済、コンテンツ取得、staging / internal endpoint への接続。
- 対象条件: CT 要件を満たさない証明書チェーン、Network Security Config の CT 設定、証明書 pinning / private PKI との組み合わせ。

## Required Action

- 必須対応: HTTPS 接続先の証明書チェーンが CT 要件を満たすか棚卸しする。
- 推奨対応: Android 16 の opt-in または Android 17 / targetSdkVersion 37 環境で CT 有効時の接続テストを行う。
- 不要: ネットワーク通信を行わないアプリ、または全接続先が CT 要件を満たすことを確認済みのアプリでは直接影響は限定的。

## Test Matrix

| Device OS | targetSdkVersion | Expected behavior |
| --- | --- | --- |
| Android 16 | 36 | 公式文書上、CT は available だが app opt-in が必要。 |
| Android 17 | 36 | Unknown。この section は targetSdkVersion 37+ 向けだが、AOSP gate 未確認。 |
| Android 17 | 37 | CT が default enabled。CT 要件を満たさない証明書チェーンでは接続影響の可能性。 |

## Explanation for Customers

Android 17 では、targetSdkVersion 37 以上のアプリで certificate transparency が既定で有効になります。Android 16 ではアプリが明示的に opt in した場合だけ CT が使われていましたが、Android 17 / targetSdkVersion 37 では opt in していない接続にも CT policy が適用される可能性があります。

そのため、公開 HTTPS endpoint、staging endpoint、private PKI、証明書 pinning を利用する通信について、証明書チェーンが CT 要件を満たしているか確認してください。現時点では local AOSP checkout に Android 17 tag がないため、targetSdkVersion gate、例外条件、compat flag の有無は未確認です。

## Evidence

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-17
- Original statement: targetSdkVersion 37 以上のアプリでは certificate transparency が default enabled。Android 16 では CT は available だが opt in が必要。
- AOSP files: 未確認。local `frameworks-base` に `android-17*` tag がない。
- AOSP source context: 未確認。tag 間 diff が実行できない。
- Diff interpretation: 未分類。公式文書上は changed default と読めるが、AOSP diff による確認は Android 17 tag 待ち。
- Gate conclusion: Unknown。公式文書は targetSdkVersion 37+ を示すが、AOSP gate evidence は未取得。

## Human Decision

Final Priority:
- Human decision required

Decision:
- Further investigation required

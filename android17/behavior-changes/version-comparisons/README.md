# Android 16 → 17 挙動比較一覧

このディレクトリは、Android 17 の親 Behavior Change ごとに、同じ初期状態と操作を
Android 16 / 17 で比較する companion index である。

[Android OS バージョン間挙動比較テンプレート](../../../docs/templates/android-os-version-behavior-comparison-template.md)
の比較軸を使う。classification、confidence、AOSP evidence、Human Decision は各主レポートを正とする。

比較後に具体的なKotlin、Manifest、XML、native、testへ落とす場合は、
[Android 17対応例一覧](../implementation-examples/README.md)を参照する。

## 比較スコープ

| 項目 | Baseline | Target |
| --- | --- | --- |
| Android OS | Android 16 | Android 17 |
| AOSP tag | `android-16.0.0_r4` | `android-17.0.0_r1` |
| 基本 targetSdkVersion | 36 | 36 |
| targetSdk比較 | 必要な項目だけ target 37 buildを追加 | target 36 / 37を分離 |
| App build | 同一build | 同一build |
| 公式文書確認日 | 2026-07-28 | 2026-07-28 |
| Observed | 実機未実施 | 実機未実施 |

`git ls-remote` で確認した `frameworks/base` の最新 Android 17 release tag は
2026-07-28時点で `android-17.0.0_r1`。

公式 Entry Point:

- [Behavior changes: all apps](https://developer.android.com/about/versions/17/behavior-changes-all)
- [Behavior changes: apps targeting Android 17+](https://developer.android.com/about/versions/17/behavior-changes-17)
- [Android 17 features and changes list](https://developer.android.com/about/versions/17/summary)
- [AOSP android-17.0.0_r1](https://android.googlesource.com/platform/frameworks/base/+/android-17.0.0_r1)

## 分冊

| 分冊 | 収録項目 |
| --- | --- |
| [Core functionality](core-functionality.md) | app memory limits、MessageQueue、static final fields |
| [Connectivity and security](connectivity-and-security.md) | Bluetooth、cleartext / URI grants、Keystore、cross-profile、Activity Security、CT、native DCL、Contacts Provider |
| [Privacy and media](privacy-and-media.md) | SMS OTP、local network、ECH、physical password、background audio |
| [UI, input and device form factors](ui-input-and-device-form-factors.md) | IME visibility、touchpad pointer capture、CJKV accessibility、large screen |

## 最新公式一覧との差分

既存の主レポートがまだない項目は、
[追加調査待ちの公式項目](latest-documentation-gaps.md)に分離した。
この一覧は公式文書の変更 inventory であり、AOSP finding や確定 classification ではない。

## 読み方

1. OS updateだけか、targetSdkVersion 37が必要かを確認する。
2. device、permission、API、process state、QPRなどの追加条件を固定する。
3. Android 16 / 17のSystem behaviorとApp-visible signalを分けて比較する。
4. Expectedを確認し、実機Observedを別欄へ記録する。
5. 最終判断は主レポートとdecision logで行う。

## Human Decision

この比較一覧では最終priority、severity、release readinessを決定しない。
[Android 17 decision log](../../decisions/DECISION_LOG.md)を参照する。

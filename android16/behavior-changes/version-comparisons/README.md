# Android 15 → 16 挙動比較一覧

このディレクトリは、Android 16 の親 Behavior Change ごとに、同じアプリ操作・初期状態を
Android 15 と Android 16 で比較するための companion index である。

[Android OS バージョン間挙動比較テンプレート](../../../docs/templates/android-os-version-behavior-comparison-template.md)
の比較軸を使用する。classification、confidence、AOSP evidence、Human Decision は各主レポートを正とする。

## 共通比較条件

| 項目 | Baseline | Target |
| --- | --- | --- |
| Android OS | Android 15 | Android 16 |
| AOSP tag | `android-15.0.0_r36` | `android-16.0.0_r4` |
| 基本 targetSdkVersion | 35 | 35 |
| targetSdk 比較 | 必要な項目だけ target 36 build を追加 | target 35 / 36 を分離 |
| アプリ build | 同一 build | 同一 build |
| 公式文書確認日 | 2026-08-22 | 2026-08-22 |
| Observed | 実機未実施 | 実機未実施 |

QPR、Mainline、OEM、GPU、window size、permission、manifest opt-in などの追加条件は、
各分冊の項目ごとに固定または分離して比較する。

2026-08-22 時点で `frameworks/base` と各利用AOSP projectの最新通常リリースタグは
`android-15.0.0_r36` / `android-16.0.0_r4` のままである。

## 分冊

| 分冊 | 収録する親項目 |
| --- | --- |
| [Core functionality](core-functionality.md) | JobScheduler quota、abandoned job、important-while-foreground、fixed-rate、ordered broadcast、ART、16 KB page size |
| [Connectivity and security](connectivity-and-security.md) | bond loss、CDM timeout、Intent redirection、Safer Intents、GPU syscall、MediaStore version |
| [Privacy and health](privacy-and-health.md) | health permissions、app-owned photos、Local Network Permission |
| [UI and device form factors](ui-and-device-form-factors.md) | adaptive layouts、virtual device owner、edge-to-edge、Predictive Back、3-button Back、accessibility、font、themed icons |

## 読み方

1. 「適用」で OS update、targetSdkVersion、opt-in、device 条件を確認する。
2. Android 15 / 16 の欄を同じ初期状態と操作で比較する。
3. 「App signal」でアプリから実際に判定できる情報を確認する。
4. 「対応」で移行または fallback を選ぶ。
5. 「比較試験」の Expected と実機の Observed を別々に記録する。

## Companion 統合方針

次は独立した runtime change として重複掲載せず、親項目へ統合する。

- JobScheduler quota testing
- Virtual device owner の per-app overrides / common breaking changes / references
- Adaptive layouts の implementation details / common breaking changes / exceptions / temporary opt-out
- Intent redirection の opt-out / compileSdk 35 以下
- Safer Intents の impact / testing and debugging
- Local Network Permission の release plan / impact / developer guidance / errors / definition
- GPU syscall filtering FAQ
- Bluetooth の new intents / OEM differences / manual unpair
- Predictive Back の implementation examples / runtime comparison / Dispatcher animation guide

## Human Decision

この比較一覧では最終 priority、severity、release readiness を決定しない。
[Android 16 decision log](../../decisions/DECISION_LOG.md) と各主レポートを参照する。

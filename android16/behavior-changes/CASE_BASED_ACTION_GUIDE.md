# Android 16 Behavior Changes - ケース別対応手順ガイド

## 位置づけ（Scope）

このガイドは、Android 16 の各 Behavior Change について、アプリの実装・利用 API・端末条件・targetSdkVersion ごとに対応手順を選ぶための運用資料である。
根拠、適用条件分類、confidence、AOSP source context、人間の判断は各調査レポートを正とする。

対象:
- Android 16 上の全アプリ向け Behavior Changes。
- Android 16 / targetSdkVersion 36 以上向け Behavior Changes。
- Android 16 時点で opt-in testing の変更。
- ART Mainline、OEM、QPR、端末条件に依存する変更。

Entry Point:
- https://developer.android.com/about/versions/16/behavior-changes-all
- https://developer.android.com/about/versions/16/behavior-changes-16

公式文書確認日:
- 2026-08-22

## 使い方（How to Use）

各項目は次の順序で使用する。

1. Detection に従って対象 API、manifest、SDK、端末機能を棚卸しする。
2. Case table から現在のアプリ状態に一致するケースを選ぶ。
3. 対応手順を実施する。
4. 最低限の検証を Android 15 / 16、targetSdkVersion 35 / 36、追加条件あり / なしで比較する。
5. 詳細な根拠と例外はリンク先の調査レポートで確認する。
6. 最終 priority、severity、release readiness、customer communication priority は人間が決定する。

## Applicability の先行判定

| 分類 | 最初に確認する条件 | 基本方針 |
| --- | --- | --- |
| `OS_UPDATE_ALL_APPS` | Android 16 上で動作するか | targetSdkVersion を据え置いても対象として回帰試験する |
| `TARGET_SDK_36_CONDITIONAL` | Android 16 + target 36 + API / device / runtime 条件 | 条件を満たす画面・機能だけを分離して検証する |
| `OPT_IN_ONLY` | manifest / compat flag を明示的に有効化したか | opt-in 前に partner / error / denial を記録し、段階導入する |
| `MAINLINE_OR_PLAY_SYSTEM_UPDATE` | platform OS だけでなく module version | Android 12 以降の更新済み module 端末も試験対象にする |
| QPR / OEM dependent | QPR version、launcher、GPU、OEM 実装 | AOSP 端末だけで結論を一般化せず device matrix を持つ |

## 分冊

| 分冊 | 主な項目 |
| --- | --- |
| [Core functionality](case-guides/core-functionality.md) | JobScheduler、fixed-rate、ART、16 KB page、ordered broadcast |
| [Connectivity and security](case-guides/connectivity-and-security.md) | Bluetooth bond loss、CDM timeout、Intent hardening、Safer Intents、GPU、MediaStore |
| [Privacy and health](case-guides/privacy-and-health.md) | health permissions、app-owned photos、Local Network Permission |
| [UI and device form factors](case-guides/ui-and-device-form-factors.md) | adaptive layouts、virtual display、edge-to-edge、Predictive Back、accessibility、font、icons |

## 収録項目（Coverage）

| 公式項目 | ケース別手順 |
| --- | --- |
| JobScheduler quota optimizations | [Core](case-guides/core-functionality.md#jobscheduler-quota-optimizations) |
| Abandoned empty jobs stop reason | [Core](case-guides/core-functionality.md#abandoned-empty-jobs-stop-reason) |
| Fully deprecating `JobInfo#setImportantWhileForeground` | [Core](case-guides/core-functionality.md#fully-deprecating-setimportantwhileforeground) |
| Ordered broadcast priority scope no longer global | [Core](case-guides/core-functionality.md#ordered-broadcast-priority-scope) |
| ART internal changes | [Core](case-guides/core-functionality.md#art-internal-changes) |
| 16 KB page size compatibility mode | [Core](case-guides/core-functionality.md#16-kb-page-size-compatibility-mode) |
| Fixed rate work scheduling optimization | [Core](case-guides/core-functionality.md#fixed-rate-work-scheduling-optimization) |
| Improved bond loss handling | [Connectivity / Security](case-guides/connectivity-and-security.md#bluetooth-bond-loss--encryption--unpair) |
| New intents to handle bond loss and encryption changes | [Connectivity / Security](case-guides/connectivity-and-security.md#bluetooth-bond-loss--encryption--unpair) |
| New way to remove Bluetooth bond | [Connectivity / Security](case-guides/connectivity-and-security.md#bluetooth-bond-loss--encryption--unpair) |
| Companion apps no longer notified of discovery timeouts | [Connectivity / Security](case-guides/connectivity-and-security.md#companion-device-manager-discovery-timeout) |
| Improved security against Intent redirection attacks | [Connectivity / Security](case-guides/connectivity-and-security.md#intent-redirection-hardening) |
| Safer Intents | [Connectivity / Security](case-guides/connectivity-and-security.md#safer-intents) |
| GPU syscall filtering | [Connectivity / Security](case-guides/connectivity-and-security.md#gpu-syscall-filtering) |
| MediaStore version lockdown | [Connectivity / Security](case-guides/connectivity-and-security.md#mediastore-version-lockdown) |
| Health and fitness permissions | [Privacy / Health](case-guides/privacy-and-health.md#health-and-fitness-permissions) |
| App-owned photos | [Privacy / Health](case-guides/privacy-and-health.md#app-owned-photos) |
| Local Network Permission | [Privacy / Health](case-guides/privacy-and-health.md#local-network-permission) |
| Adaptive layouts | [UI / Device](case-guides/ui-and-device-form-factors.md#adaptive-layouts) |
| Virtual device owner overrides | [UI / Device](case-guides/ui-and-device-form-factors.md#virtual-device-owner-overrides) |
| Edge to edge opt-out going away | [UI / Device](case-guides/ui-and-device-form-factors.md#edge-to-edge-opt-out-going-away) |
| Migration or opt-out required for Predictive Back | [UI / Device](case-guides/ui-and-device-form-factors.md#predictive-back) |
| Support for 3-button navigation | [UI / Device](case-guides/ui-and-device-form-factors.md#3-button-predictive-back) |
| Deprecating disruptive accessibility announcements | [UI / Device](case-guides/ui-and-device-form-factors.md#accessibility-announcements) |
| Elegant font APIs deprecated and disabled | [UI / Device](case-guides/ui-and-device-form-factors.md#elegant-font-apis) |
| Automatic themed app icons | [UI / Device](case-guides/ui-and-device-form-factors.md#automatic-themed-app-icons) |

## Companion の統合方針

次の資料は独立した runtime change として重複掲載せず、親項目のケースへ統合する。

- JobScheduler quota testing。
- Virtual device owner の per-app overrides / common breaking changes / references。
- Adaptive layouts の implementation details / common breaking changes / exceptions / temporary opt-out。
- Intent redirection の opt-out / compileSdk 35 以下。
- Safer Intents の impact / testing and debugging。
- Local Network Permission の release plan / impact / developer guidance / errors / definition。
- GPU syscall filtering FAQ。
- Bluetooth の new intents / OEM differences。
- Predictive Back の implementation examples / runtime comparison / Dispatcher animation guide。

## 現時点の制約

- このガイドは既存レポートの事実と公式文書から対応分岐を整理したものであり、対象アプリの実装・実機結果は未確認である。
- 公式ページの `New way to remove bluetooth bond` は Bluetooth ケースへ含めたが、独立した traceability report は未作成である。正式な finding として扱う場合は AOSP context、classification、summary を別途完成させる。
- documentation-only cross-reference は runtime change ではないためケース対象外とする。

## 共通完了条件

- 対象コード / manifest / dependency の検出結果を記録した。
- 選択したケースと、そのケースを選んだ条件を記録した。
- Android 15 / 16 と targetSdkVersion 35 / 36 の必要な組み合わせを比較した。
- compat flag、permission、device state、OEM / QPR 条件を記録した。
- failure signal、fallback、rollback または temporary mitigation を記録した。
- 実機未検証の項目を「未実施」のまま残し、推測を observed result として扱っていない。
- Human Decision を agent が確定していない。

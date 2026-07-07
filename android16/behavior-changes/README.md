# Android 16 Behavior Changes

Behavior Changes の各セクションごとに、顧客説明向け調査レポートを作成する。

## Quick View

最初にここを見る。各 Behavior Change は必ず 1 つの primary classification に入れる。

| Classification | When it applies | Customer-facing meaning | List |
| --- | --- | --- | --- |
| [`OS_UPDATE_ALL_APPS`](APPLICABILITY_CLASSIFICATION.md#os_update_all_apps) | Android 16 上の全アプリ。targetSdkVersion に依存しない | OS アップデートだけで影響する可能性がある | [OS update / all apps](#os-update--all-apps) |
| [`TARGET_SDK_36`](APPLICABILITY_CLASSIFICATION.md#target_sdk_36) | Android 16+ で targetSdkVersion >= 36 | targetSdkVersion 36 化で有効になる | [targetSdkVersion 36](#targetsdkversion-36) |
| [`TARGET_SDK_36_CONDITIONAL`](APPLICABILITY_CLASSIFICATION.md#target_sdk_36_conditional) | targetSdkVersion >= 36 に加えて追加条件あり | targetSdkVersion 36 化だけでは不十分。端末条件、API 利用、権限なども必要 | [targetSdkVersion 36 + conditions](#targetsdkversion-36--conditions) |
| [`MAINLINE_OR_PLAY_SYSTEM_UPDATE`](APPLICABILITY_CLASSIFICATION.md#mainline_or_play_system_update) | Mainline / Google Play system update に依存 | Android 16 platform image だけで決まらない | [Mainline / Play system update](#mainline--play-system-update) |
| [`API_ADDITION_ONLY`](APPLICABILITY_CLASSIFICATION.md#api_addition_only) | 既存挙動変更ではなく API 追加 | 互換性リスクではなく採用機会 | [API addition only](#api-addition-only) |
| [`UNKNOWN_NEEDS_MORE_EVIDENCE`](APPLICABILITY_CLASSIFICATION.md#unknown_needs_more_evidence) | 根拠不足、または許可ラベルに合わない documentation / opt-in testing item | 顧客向け結論には条件を明記する | [Unknown / needs evidence](#unknown--needs-evidence) |

## Template

Use:

```text
android16/templates/customer-report-template.md
```

## OS Update / All Apps

Android 16 へ OS アップデートすると、targetSdkVersion を変更していないアプリにも影響する可能性がある項目。

| Report | Summary | Notes | Status |
| --- | --- | --- | --- |
| [Improved bond loss handling](all/connectivity/improved-bond-loss-handling.md) | [Summary](../summaries/all/connectivity/improved-bond-loss-handling-summary.md) | Bluetooth remote bond loss handling | Draft |
| [16 KB page size compatibility mode](all/core-functionality/16-kb-page-size-compatibility-mode.md) | [Summary](../summaries/all/core-functionality/16-kb-page-size-compatibility-mode-summary.md) | 16 KB page-size device / native library alignment | Draft |
| [Abandoned empty jobs stop reason](all/core-functionality/abandoned-empty-jobs-stop-reason.md) | [Summary](../summaries/all/core-functionality/abandoned-empty-jobs-stop-reason-summary.md) | JobScheduler stop reason | Draft |
| [Fully deprecating JobInfo#setImportantWhileForeground](all/core-functionality/fully-deprecating-jobinfo-setimportantwhileforeground.md) | [Summary](../summaries/all/core-functionality/fully-deprecating-jobinfo-setimportantwhileforeground-summary.md) | JobScheduler API deprecation behavior | Draft |
| [JobScheduler quota optimizations](all/core-functionality/jobscheduler-quota-optimizations.md) | [Summary](../summaries/all/core-functionality/jobscheduler-quota-optimizations-summary.md) | JobScheduler quota accounting | Draft |
| [JobScheduler quota optimizations testing](all/core-functionality/jobscheduler-quota-optimizations-testing.md) | [Summary](../summaries/all/core-functionality/jobscheduler-quota-optimizations-testing-summary.md) | Testing / debug controls | Draft |
| [Ordered broadcast priority scope no longer global](all/core-functionality/ordered-broadcast-priority-scope-no-longer-global.md) | [Summary](../summaries/all/core-functionality/ordered-broadcast-priority-scope-no-longer-global-summary.md) | Ordered broadcast priority scope | Draft |
| [Virtual device owner overrides](all/device-form-factors/virtual-device-owner-overrides.md) | [Summary](../summaries/all/device-form-factors/virtual-device-owner-overrides-summary.md) | Projected display / virtual device owner | Draft |
| [Virtual device owner overrides - Per-app overrides](all/device-form-factors/virtual-device-owner-overrides-per-app-overrides.md) | [Summary](../summaries/all/device-form-factors/virtual-device-owner-overrides-per-app-overrides-summary.md) | Orientation / aspect ratio / resizability override | Draft |
| [Virtual device owner overrides - Common breaking changes](all/device-form-factors/virtual-device-owner-overrides-common-breaking-changes.md) | [Summary](../summaries/all/device-form-factors/virtual-device-owner-overrides-common-breaking-changes-summary.md) | Large screen projected UI impact | Draft |
| [Virtual device owner overrides - References](all/device-form-factors/virtual-device-owner-overrides-references.md) | [Summary](../summaries/all/device-form-factors/virtual-device-owner-overrides-references-summary.md) | Documentation pointer only / companion app streaming | Draft |
| [Companion apps no longer notified of discovery timeouts](all/security/companion-apps-no-longer-notified-of-discovery-timeouts.md) | [Summary](../summaries/all/security/companion-apps-no-longer-notified-of-discovery-timeouts-summary.md) | CompanionDeviceManager discovery timeout | Draft |
| [Improved security against Intent redirection attacks](all/security/improved-security-against-intent-redirection-attacks.md) | [Summary](../summaries/all/security/improved-security-against-intent-redirection-attacks-summary.md) | Nested Intent launch hardening | Draft |
| [Intent redirection handling opt-out](all/security/improved-security-against-intent-redirection-attacks-opt-out.md) | [Summary](../summaries/all/security/improved-security-against-intent-redirection-attacks-opt-out-summary.md) | `Intent#removeLaunchSecurityProtection()` | Draft |
| [Intent redirection handling for apps compiling against Android 15 or lower](all/security/improved-security-against-intent-redirection-attacks-targeting-before-16.md) | [Summary](../summaries/all/security/improved-security-against-intent-redirection-attacks-targeting-before-16-summary.md) | Reflection fallback guidance | Draft |
| [Deprecating disruptive accessibility announcements](all/user-experience-and-system-ui/deprecating-disruptive-accessibility-announcements.md) | [Summary](../summaries/all/user-experience-and-system-ui/deprecating-disruptive-accessibility-announcements-summary.md) | API deprecation / accessibility guidance | Draft |
| [Support for 3-button navigation](all/user-experience-and-system-ui/support-for-3-button-navigation-predictive-back.md) | [Summary](../summaries/all/user-experience-and-system-ui/support-for-3-button-navigation-predictive-back-summary.md) | 3-button predictive back long-press | Draft |
| [Automatic themed app icons](all/user-experience-and-system-ui/automatic-themed-app-icons.md) | [Summary](../summaries/all/user-experience-and-system-ui/automatic-themed-app-icons-summary.md) | Android 16 QPR2 / launcher-dependent | Draft |
| [New intents to handle bond loss and encryption changes](target/connectivity/new-intents-to-handle-bond-loss-and-encryption-changes.md) | [Summary](../summaries/target/connectivity/new-intents-to-handle-bond-loss-and-encryption-changes-summary.md) | Target-page item, but AOSP evidence indicates OS-gated broadcast path | Draft |
| [Adapting to varying OEM implementations of bond loss](target/connectivity/adapting-to-varying-oem-implementations-bond-loss.md) | [Summary](../summaries/target/connectivity/adapting-to-varying-oem-implementations-bond-loss-summary.md) | Target-page subsection, OEM variability / all-app runtime context | Draft |
| [GPU syscall filtering](target/security/gpu-syscall-filtering.md) | [Summary](../summaries/target/security/gpu-syscall-filtering-summary.md) | Target-page item, but classified as OS_UPDATE_ALL_APPS | Draft |
| [GPU syscall filtering FAQ](target/security/gpu-syscall-filtering-faq.md) | [Summary](../summaries/target/security/gpu-syscall-filtering-faq-summary.md) | Documentation / FAQ companion | Draft |

## targetSdkVersion 36

Android 16+ で targetSdkVersion を 36 以上にした場合に有効になる項目。

| Report | Summary | Notes | Status |
| --- | --- | --- | --- |
| 現在、primary label が `TARGET_SDK_36` の tracked report はありません。 |  | 多くの targetSdkVersion 36 項目は追加条件を持つため `TARGET_SDK_36_CONDITIONAL` に分類。 |  |

## targetSdkVersion 36 + Conditions

targetSdkVersion 36 以上に加えて、端末条件、権限、API 利用、manifest property、process state などの追加条件を満たす場合に影響する項目。

| Report | Summary | Notes | Status |
| --- | --- | --- | --- |
| [Fixed rate work scheduling optimization](target/core-functionality/fixed-rate-work-scheduling-optimization.md) | [Summary](../summaries/target/core-functionality/fixed-rate-work-scheduling-optimization-summary.md) | `ScheduledThreadPoolExecutor` fixed-rate missed task behavior | Draft |
| [Adaptive layouts](target/device-form-factors/adaptive-layouts.md) | [Summary](../summaries/target/device-form-factors/adaptive-layouts-summary.md) | Large screen orientation / resizability / aspect ratio behavior | Draft |
| [Adaptive layouts - Implementation details](target/device-form-factors/implementation-details-adaptive-layouts.md) | [Summary](../summaries/target/device-form-factors/implementation-details-adaptive-layouts-summary.md) | Implementation detail subsection | Draft |
| [Adaptive layouts - Common breaking changes](target/device-form-factors/common-breaking-changes-adaptive-layouts.md) | [Summary](../summaries/target/device-form-factors/common-breaking-changes-adaptive-layouts-summary.md) | Large screen UI risks | Draft |
| [Adaptive layouts - Ignore orientation / resizability / aspect ratio restrictions](target/device-form-factors/ignore-orientation-resizability-and-aspect-ratio-restrictions.md) | [Summary](../summaries/target/device-form-factors/ignore-orientation-resizability-and-aspect-ratio-restrictions-summary.md) | Core behavior subsection | Draft |
| [Adaptive layouts - Exceptions](target/device-form-factors/exceptions-adaptive-layouts.md) | [Summary](../summaries/target/device-form-factors/exceptions-adaptive-layouts-summary.md) | Exceptions / opt-out conditions | Draft |
| [Adaptive layouts - Temporary opt-out](target/device-form-factors/temporary-opt-out-adaptive-layouts.md) | [Summary](../summaries/target/device-form-factors/temporary-opt-out-adaptive-layouts-summary.md) | Temporary opt-out property | Draft |
| [Health and fitness permissions](target/health-and-fitness/health-and-fitness-permissions.md) | [Summary](../summaries/target/health-and-fitness/health-and-fitness-permissions-summary.md) | Health permissions migration | Draft |
| [Mobile apps health and fitness permissions](target/health-and-fitness/mobile-apps-health-fitness-permissions.md) | [Summary](../summaries/target/health-and-fitness/mobile-apps-health-fitness-permissions-summary.md) | Mobile app subsection | Draft |
| [App-owned photos](target/privacy/app-owned-photos.md) | [Summary](../summaries/target/privacy/app-owned-photos-summary.md) | Photo / MediaStore ownership behavior | Draft |
| [MediaStore version lockdown](target/security/mediastore-version-lockdown.md) | [Summary](../summaries/target/security/mediastore-version-lockdown-summary.md) | `MediaStore#getVersion()` opaque token | Draft |
| [Safer Intents](target/security/safer-intents.md) | [Summary](../summaries/target/security/safer-intents-summary.md) | Receiving app strict intent matching opt-in | Draft |
| [Safer Intents - Impact](target/security/safer-intents-impact.md) | [Summary](../summaries/target/security/safer-intents-impact-summary.md) | Impact subsection | Draft |
| [Safer Intents - Testing and debugging](target/security/safer-intents-testing-and-debugging.md) | [Summary](../summaries/target/security/safer-intents-testing-and-debugging-summary.md) | Debugging subsection | Draft |
| [Edge to edge opt-out going away](target/user-experience-and-system-ui/edge-to-edge-opt-out-going-away.md) | [Summary](../summaries/target/user-experience-and-system-ui/edge-to-edge-opt-out-going-away-summary.md) | Edge-to-edge opt-out disabled for targetSdkVersion 36 | Draft |
| [Migration or opt-out required for predictive back](target/user-experience-and-system-ui/migration-or-opt-out-required-for-predictive-back.md) | [Summary](../summaries/target/user-experience-and-system-ui/migration-or-opt-out-required-for-predictive-back-summary.md) | Predictive back default enabled for targetSdkVersion 36 | Draft |
| [Elegant font APIs deprecated and disabled](target/user-experience-and-system-ui/elegant-font-apis-deprecated-and-disabled.md) | [Summary](../summaries/target/user-experience-and-system-ui/elegant-font-apis-deprecated-and-disabled-summary.md) | Elegant text height APIs disabled | Draft |

## Mainline / Play System Update

Mainline module または Google Play system update の配信状態に依存する項目。

| Report | Summary | Notes | Status |
| --- | --- | --- | --- |
| [ART internal changes](all/core-functionality/art-internal-changes.md) | [Summary](../summaries/all/core-functionality/art-internal-changes-summary.md) | Android 16 platform and Android 12+ ART Mainline update | Draft |

## API Addition Only

既存アプリの挙動変更ではなく、新 API の利用機会として扱う項目。

| Report | Summary | Notes | Status |
| --- | --- | --- | --- |
| 現在、primary label が `API_ADDITION_ONLY` の tracked report はありません。 |  | 新 API を含む item も互換性影響または OS / target 条件を伴う場合は別 classification に分類。 |  |

## Unknown / Needs Evidence

分類根拠が不足している、または documentation cross-reference / opt-in testing など許可ラベルに完全には合わない項目。

| Report | Summary | Missing / caveat | Status |
| --- | --- | --- | --- |
| [Apps targeting Android 16 cross-reference](all/overview/apps-targeting-android-16-cross-reference.md) | [Summary](../summaries/all/overview/apps-targeting-android-16-cross-reference-summary.md) | Documentation cross-reference only; independent runtime behavior ではない | Draft |
| [Local Network Permission](target/privacy/local-network-permission.md) | [Summary](../summaries/target/privacy/local-network-permission-summary.md) | Android 16 current stage は `RESTRICT_LOCAL_NETWORK` opt-in testing / default disabled | Draft |
| [Local Network Permission - Release plan](target/privacy/local-network-permission-release-plan.md) | [Summary](../summaries/target/privacy/local-network-permission-release-plan-summary.md) | Future enforcement plan / current default disabled | Draft |
| [Local Network Permission - Impact](target/privacy/local-network-permission-impact.md) | [Summary](../summaries/target/privacy/local-network-permission-impact-summary.md) | Opt-in testing impact | Draft |
| [Local Network Permission - Developer guidance opt-in](target/privacy/local-network-permission-developer-guidance-opt-in.md) | [Summary](../summaries/target/privacy/local-network-permission-developer-guidance-opt-in-summary.md) | Opt-in testing workflow | Draft |
| [Local Network Permission - Errors](target/privacy/local-network-permission-errors.md) | [Summary](../summaries/target/privacy/local-network-permission-errors-summary.md) | Error surface under opt-in restriction | Draft |
| [Local Network Permission - Local network definition](target/privacy/local-network-permission-local-network-definition.md) | [Summary](../summaries/target/privacy/local-network-permission-local-network-definition-summary.md) | Address / interface definition; enforcement gate remains opt-in | Draft |

## App-Specific Reports

| Report | Scope | Status |
| --- | --- | --- |
| [Wireless camera companion](../app-reports/wireless-camera-companion/investigation-report.md) | カメラ連携アプリ向け Android 16 横断影響調査 | Draft |

## Link Targets For Reports

各レポートを追加したら、上の一覧から該当箇所へ直接飛べるように以下の形式でリンクする。

| Destination | Link format |
| --- | --- |
| Report top | `Title -> relative-report-path.md` |
| One page summary | `Summary -> ../summaries/relative-summary-path.md` |

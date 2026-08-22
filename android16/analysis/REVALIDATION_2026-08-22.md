# Android 16 全項目再検証台帳（2026-08-22）

## 目的

Android 16 の既存 Behavior Change 調査へ、最新のレビュー済みルールが反映されているかを全件確認した記録である。個別レポートの分類、confidence、AOSP source context、Human Decision を置き換えない。

## 公式文書とタグ

- all-apps: https://developer.android.com/about/versions/16/behavior-changes-all
- target: https://developer.android.com/about/versions/16/behavior-changes-16
- 比較: `android-15.0.0_r36` -> `android-16.0.0_r4`
- 公式refs確認日: 2026-08-22
- 結果: baseline / target とも、各利用AOSP projectで上記が最新通常リリースタグ。
- Android 16 の公式ページ最終更新: all-apps 2026-08-14 UTC、target 2026-08-17 UTC、compat 2026-08-14 UTC。

## AOSP workspace と再実行結果

`git status --short` または展開中の index lock、official remote、タグ存在、解決済みcommitを確認し、working tree に依存しない次の比較を各projectで再実行した。

```bash
git -C <checkout> diff --no-renames --name-only android-15.0.0_r36 android-16.0.0_r4
```

| AOSP project | Official remote URL | Checkout path | From commit | To commit | Changed paths | Inventory SHA-256 | Working tree |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| `platform/frameworks/base` | `https://android.googlesource.com/platform/frameworks/base` | `frameworks-base/` | `396d32905ded85c082232bc510b525c9e372e585` | `45034f0663f960d9ee5fb0a101a4732b71f6e2f4` | 21487 | `daeb27f27074f12dcca433f9d0952fbc02ac1c57e0c1fa06c1c689c3970d77b2` | Clean |
| `platform/packages/modules/Bluetooth` | `https://android.googlesource.com/platform/packages/modules/Bluetooth` | `tmp/aosp-checkouts/Bluetooth/` | `810eacb8454c957255fec9328e6e41b30a054033` | `5323f31677c7dfa04de2e6e9fce1012ef4edaff2` | 4692 | `aebe39956220159f3dc5a0f405250b41b78806f61aaac13664bb21c4edba63ec` | 展開中 |
| `platform/packages/apps/Settings` | `https://android.googlesource.com/platform/packages/apps/Settings` | `tmp/aosp-checkouts/Settings/` | `d56148b315549a7f9759e32565cff83cc9bcc3c1` | `f6ec09afb00fb635e247687e032c39ed0c1ec21b` | 4487 | `0128e79690afaeb9d425d5326fcbadd1ba9d0d54a28a5234743d6851db58686c` | 展開中 |
| `platform/packages/apps/Launcher3` | `https://android.googlesource.com/platform/packages/apps/Launcher3` | `tmp/aosp-checkouts/Launcher3/` | `5a7ed4b586cf4c17e5e5712be68f08283c8e03ae` | `bbd0e27be08cf2f957b62f5af95669b3203b92a0` | 2203 | `dc66c20ff9c8926fdbf4e970beaaa40dd79fc94f869407b18f310020fe2773ea` | 展開中 |
| `platform/frameworks/libs/systemui` | `https://android.googlesource.com/platform/frameworks/libs/systemui` | `tmp/aosp-checkouts/systemui-libs/` | `5fddbfb7e009894264b76a1354eac5e2a3cf44df` | `ca0ae237ed2d67f5b05f2572ddbcc6e10b550b92` | 441 | `e8a204041a3d0d9415ea0ccd1d72be445a7da64e0ce06de8d25c8ed868e4d00e` | Clean |
| `platform/packages/modules/Connectivity` | `https://android.googlesource.com/platform/packages/modules/Connectivity` | `tmp/aosp-checkouts/Connectivity/` | `64cd443febd3ee0fd5c90b47089d82b96850c1e9` | `f930245ec39a510f37a9a7dfaded96d287491a61` | 955 | `10ad914503b5396412a0402618cf3183ac6e06dd84f5a6b11893b27c3170729b` | 展開中 |
| `platform/packages/providers/MediaProvider` | `https://android.googlesource.com/platform/packages/providers/MediaProvider` | `tmp/aosp-checkouts/MediaProvider/` | `6c6fe3157b6e54d27e8c199ed062fecb7f2707d9` | `217515852d78543d1d7da39bd69d4e03957ee118` | 1217 | `fccba377d00a2a6e95141edaf0326ee86503fe6ac0acd545c889dc04b161b6ed` | 展開中 |
| `platform/packages/modules/HealthFitness` | `https://android.googlesource.com/platform/packages/modules/HealthFitness` | `tmp/aosp-checkouts/HealthFitness/` | `99359dc599434b1f00118ab1b701b12afc75cb30` | `894d57b85aff1a3a854f95397654a1cf0d6a9451` | 2971 | `1c2b35586f9bc18d65d14fc978d1c66e9a11b1f90d5a714c296a6499119fb5e2` | 展開中 |
| `platform/system/sepolicy` | `https://android.googlesource.com/platform/system/sepolicy` | `tmp/aosp-checkouts/sepolicy/` | `e4a36f4174b17bbab9dc043f4a65dc8d87377290` | `43e4494a5a78317819dcc2766a11927c12ef3dfd` | 802 | `92e9f63dffef8a3909dd59811a74dcc27aeb26547815da674299d3660105d603` | Clean |
| `platform/art` | `https://android.googlesource.com/platform/art` | `tmp/aosp-checkouts/art/` | `795d594fd825385562da6b089ea9b2033f3abf5a` | `1690c6912a7972c9e62c39b48c706de9b8b18b4a` | 1302 | `434febd44b2a2e1add8805e7d1ebe6f7277156a66e22bf8cdb5d648ddbe02c94` | 展開中 |
| `platform/libcore` | `https://android.googlesource.com/platform/libcore` | `tmp/aosp-checkouts/libcore/` | `89a6322812dc8573315e60046e7959c50dad91d4` | `1c599b67bcd3de5c50c79d0622e40b6de99b4cb4` | 457 | `c014f934874ca94c873bfa99b7c5f13312772d8f0349a0819b85a333b5ae600e` | 展開中 |

## 項目別結果

全レポートで、公式 section、OS / targetSdkVersion の分離、AOSP project provenance、source context、diff interpretation、Facts / Observations / Hypotheses / Conclusions、Human Decision の参照を確認した。タグが同一だったため、既存の結論や confidence は機械的に引き上げず、未確認事項を維持した。

| レポート | 1ページ要約 | 主分類 | AOSP project | 結果 |
| --- | --- | --- | --- | --- |
| [Improved bond loss handling 調査レポート](../behavior-changes/all/connectivity/improved-bond-loss-handling.md) | [要約](../summaries/all/connectivity/improved-bond-loss-handling-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base`<br>`platform/packages/modules/Bluetooth`<br>`platform/packages/apps/Settings` | 再検証済み |
| [16 KB page size compatibility mode 調査レポート](../behavior-changes/all/core-functionality/16-kb-page-size-compatibility-mode.md) | [要約](../summaries/all/core-functionality/16-kb-page-size-compatibility-mode-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base` | 再検証済み |
| [Abandoned empty jobs stop reason 調査レポート](../behavior-changes/all/core-functionality/abandoned-empty-jobs-stop-reason.md) | [要約](../summaries/all/core-functionality/abandoned-empty-jobs-stop-reason-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base` | 再検証済み |
| [ART internal changes 調査レポート](../behavior-changes/all/core-functionality/art-internal-changes.md) | [要約](../summaries/all/core-functionality/art-internal-changes-summary.md) | `MAINLINE_OR_PLAY_SYSTEM_UPDATE` | `platform/art`<br>`platform/libcore` | 再検証済み |
| [Fully deprecating JobInfo#setImportantWhileForeground 調査レポート](../behavior-changes/all/core-functionality/fully-deprecating-jobinfo-setimportantwhileforeground.md) | [要約](../summaries/all/core-functionality/fully-deprecating-jobinfo-setimportantwhileforeground-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base` | 再検証済み |
| [JobScheduler quota optimizations - Testing 調査レポート](../behavior-changes/all/core-functionality/jobscheduler-quota-optimizations-testing.md) | [要約](../summaries/all/core-functionality/jobscheduler-quota-optimizations-testing-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base` | 再検証済み |
| [JobScheduler quota optimizations 調査レポート](../behavior-changes/all/core-functionality/jobscheduler-quota-optimizations.md) | [要約](../summaries/all/core-functionality/jobscheduler-quota-optimizations-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base` | 再検証済み |
| [Ordered broadcast priority scope no longer global 調査レポート](../behavior-changes/all/core-functionality/ordered-broadcast-priority-scope-no-longer-global.md) | [要約](../summaries/all/core-functionality/ordered-broadcast-priority-scope-no-longer-global-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base` | 再検証済み |
| [Common breaking changes 調査レポート](../behavior-changes/all/device-form-factors/virtual-device-owner-overrides-common-breaking-changes.md) | [要約](../summaries/all/device-form-factors/virtual-device-owner-overrides-common-breaking-changes-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base` | 再検証済み |
| [Per-app overrides 調査レポート](../behavior-changes/all/device-form-factors/virtual-device-owner-overrides-per-app-overrides.md) | [要約](../summaries/all/device-form-factors/virtual-device-owner-overrides-per-app-overrides-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base` | 再検証済み |
| [References 調査レポート](../behavior-changes/all/device-form-factors/virtual-device-owner-overrides-references.md) | [要約](../summaries/all/device-form-factors/virtual-device-owner-overrides-references-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base` | 再検証済み |
| [Virtual device owner overrides 調査レポート](../behavior-changes/all/device-form-factors/virtual-device-owner-overrides.md) | [要約](../summaries/all/device-form-factors/virtual-device-owner-overrides-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base` | 再検証済み |
| [Apps targeting Android 16 cross-reference 調査レポート](../behavior-changes/all/overview/apps-targeting-android-16-cross-reference.md) | [要約](../summaries/all/overview/apps-targeting-android-16-cross-reference-summary.md) | `UNKNOWN_NEEDS_MORE_EVIDENCE` | `platform/frameworks/base` | 再検証済み |
| [Companion apps no longer notified of discovery timeouts 調査レポート](../behavior-changes/all/security/companion-apps-no-longer-notified-of-discovery-timeouts.md) | [要約](../summaries/all/security/companion-apps-no-longer-notified-of-discovery-timeouts-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base` | 再検証済み |
| [Opt out of Intent redirection handling 調査レポート](../behavior-changes/all/security/improved-security-against-intent-redirection-attacks-opt-out.md) | [要約](../summaries/all/security/improved-security-against-intent-redirection-attacks-opt-out-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base` | 再検証済み |
| [For applications compiling against Android 15 (API level 35) or lower 調査レポート](../behavior-changes/all/security/improved-security-against-intent-redirection-attacks-targeting-before-16.md) | [要約](../summaries/all/security/improved-security-against-intent-redirection-attacks-targeting-before-16-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base` | 再検証済み |
| [Improved security against Intent redirection attacks 調査レポート](../behavior-changes/all/security/improved-security-against-intent-redirection-attacks.md) | [要約](../summaries/all/security/improved-security-against-intent-redirection-attacks-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base` | 再検証済み |
| [Automatic themed app icons](../behavior-changes/all/user-experience-and-system-ui/automatic-themed-app-icons.md) | [要約](../summaries/all/user-experience-and-system-ui/automatic-themed-app-icons-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base`<br>`platform/packages/apps/Launcher3`<br>`platform/frameworks/libs/systemui` | 再検証済み |
| [Deprecating disruptive accessibility announcements 調査レポート](../behavior-changes/all/user-experience-and-system-ui/deprecating-disruptive-accessibility-announcements.md) | [要約](../summaries/all/user-experience-and-system-ui/deprecating-disruptive-accessibility-announcements-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base` | 再検証済み |
| [Support for 3-button navigation 調査レポート](../behavior-changes/all/user-experience-and-system-ui/support-for-3-button-navigation-predictive-back.md) | [要約](../summaries/all/user-experience-and-system-ui/support-for-3-button-navigation-predictive-back-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base` | 再検証済み |
| [Adapting to varying OEM implementations 調査レポート](../behavior-changes/target/connectivity/adapting-to-varying-oem-implementations-bond-loss.md) | [要約](../summaries/target/connectivity/adapting-to-varying-oem-implementations-bond-loss-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base`<br>`platform/packages/modules/Bluetooth` | 再検証済み |
| [New intents to handle bond loss and encryption changes 調査レポート](../behavior-changes/target/connectivity/new-intents-to-handle-bond-loss-and-encryption-changes.md) | [要約](../summaries/target/connectivity/new-intents-to-handle-bond-loss-and-encryption-changes-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base`<br>`platform/packages/modules/Bluetooth` | 再検証済み |
| [CompanionDeviceManager による Bluetooth bond 削除 API](../behavior-changes/target/connectivity/new-way-to-remove-bluetooth-bond.md) | [要約](../summaries/target/connectivity/new-way-to-remove-bluetooth-bond-summary.md) | `API_ADDITION_ONLY` | `platform/frameworks/base` | 再検証済み |
| [固定間隔処理のスケジューリング最適化（Fixed rate work scheduling optimization）調査レポート](../behavior-changes/target/core-functionality/fixed-rate-work-scheduling-optimization.md) | [要約](../summaries/target/core-functionality/fixed-rate-work-scheduling-optimization-summary.md) | `TARGET_SDK_36_CONDITIONAL` | `platform/frameworks/base`<br>`platform/libcore` | 再検証済み |
| [Adaptive layouts 調査レポート](../behavior-changes/target/device-form-factors/adaptive-layouts.md) | [要約](../summaries/target/device-form-factors/adaptive-layouts-summary.md) | `TARGET_SDK_36_CONDITIONAL` | `platform/frameworks/base` | 再検証済み |
| [Common breaking changes 調査レポート](../behavior-changes/target/device-form-factors/common-breaking-changes-adaptive-layouts.md) | [要約](../summaries/target/device-form-factors/common-breaking-changes-adaptive-layouts-summary.md) | `TARGET_SDK_36_CONDITIONAL` | `platform/frameworks/base` | 再検証済み |
| [Exceptions 調査レポート](../behavior-changes/target/device-form-factors/exceptions-adaptive-layouts.md) | [要約](../summaries/target/device-form-factors/exceptions-adaptive-layouts-summary.md) | `TARGET_SDK_36_CONDITIONAL` | `platform/frameworks/base` | 再検証済み |
| [Ignore orientation, resizability, and aspect ratio restrictions 調査レポート](../behavior-changes/target/device-form-factors/ignore-orientation-resizability-and-aspect-ratio-restrictions.md) | [要約](../summaries/target/device-form-factors/ignore-orientation-resizability-and-aspect-ratio-restrictions-summary.md) | `TARGET_SDK_36_CONDITIONAL` | `platform/frameworks/base` | 再検証済み |
| [Implementation details 調査レポート](../behavior-changes/target/device-form-factors/implementation-details-adaptive-layouts.md) | [要約](../summaries/target/device-form-factors/implementation-details-adaptive-layouts-summary.md) | `TARGET_SDK_36_CONDITIONAL` | `platform/frameworks/base` | 再検証済み |
| [Temporary opt-out 調査レポート](../behavior-changes/target/device-form-factors/temporary-opt-out-adaptive-layouts.md) | [要約](../summaries/target/device-form-factors/temporary-opt-out-adaptive-layouts-summary.md) | `TARGET_SDK_36_CONDITIONAL` | `platform/frameworks/base` | 再検証済み |
| [Health and fitness permissions 調査レポート](../behavior-changes/target/health-and-fitness/health-and-fitness-permissions.md) | [要約](../summaries/target/health-and-fitness/health-and-fitness-permissions-summary.md) | `TARGET_SDK_36_CONDITIONAL` | `platform/frameworks/base`<br>`platform/packages/modules/HealthFitness` | 再検証済み |
| [Mobile apps 調査レポート](../behavior-changes/target/health-and-fitness/mobile-apps-health-fitness-permissions.md) | [要約](../summaries/target/health-and-fitness/mobile-apps-health-fitness-permissions-summary.md) | `TARGET_SDK_36_CONDITIONAL` | `platform/frameworks/base`<br>`platform/packages/modules/HealthFitness` | 再検証済み |
| [App-owned photos](../behavior-changes/target/privacy/app-owned-photos.md) | [要約](../summaries/target/privacy/app-owned-photos-summary.md) | `TARGET_SDK_36_CONDITIONAL` | `platform/frameworks/base`<br>`platform/packages/providers/MediaProvider` | 再検証済み |
| [Local Network Permission - Developer Guidance (Opt-in)](../behavior-changes/target/privacy/local-network-permission-developer-guidance-opt-in.md) | [要約](../summaries/target/privacy/local-network-permission-developer-guidance-opt-in-summary.md) | `OPT_IN_ONLY` | `platform/frameworks/base`<br>`platform/packages/modules/Connectivity` | 再検証済み |
| [Local Network Permission - Errors](../behavior-changes/target/privacy/local-network-permission-errors.md) | [要約](../summaries/target/privacy/local-network-permission-errors-summary.md) | `OPT_IN_ONLY` | `platform/frameworks/base`<br>`platform/packages/modules/Connectivity` | 再検証済み |
| [Local Network Permission - Impact](../behavior-changes/target/privacy/local-network-permission-impact.md) | [要約](../summaries/target/privacy/local-network-permission-impact-summary.md) | `OPT_IN_ONLY` | `platform/frameworks/base`<br>`platform/packages/modules/Connectivity` | 再検証済み |
| [Local Network Permission - Local Network Definition](../behavior-changes/target/privacy/local-network-permission-local-network-definition.md) | [要約](../summaries/target/privacy/local-network-permission-local-network-definition-summary.md) | `OPT_IN_ONLY` | `platform/frameworks/base`<br>`platform/packages/modules/Connectivity` | 再検証済み |
| [Local Network Permission - Release plan](../behavior-changes/target/privacy/local-network-permission-release-plan.md) | [要約](../summaries/target/privacy/local-network-permission-release-plan-summary.md) | `OPT_IN_ONLY` | `platform/frameworks/base`<br>`platform/packages/modules/Connectivity` | 再検証済み |
| [Local Network Permission](../behavior-changes/target/privacy/local-network-permission.md) | [要約](../summaries/target/privacy/local-network-permission-summary.md) | `OPT_IN_ONLY` | `platform/frameworks/base`<br>`platform/packages/modules/Connectivity` | 再検証済み |
| [GPU syscall filtering: FAQ](../behavior-changes/target/security/gpu-syscall-filtering-faq.md) | [要約](../summaries/target/security/gpu-syscall-filtering-faq-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base`<br>`platform/system/sepolicy` | 再検証済み |
| [GPU syscall filtering](../behavior-changes/target/security/gpu-syscall-filtering.md) | [要約](../summaries/target/security/gpu-syscall-filtering-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/system/sepolicy` | 再検証済み |
| [MediaStore version lockdown](../behavior-changes/target/security/mediastore-version-lockdown.md) | [要約](../summaries/target/security/mediastore-version-lockdown-summary.md) | `TARGET_SDK_36_CONDITIONAL` | `platform/frameworks/base`<br>`platform/packages/providers/MediaProvider` | 再検証済み |
| [Safer Intents: Impact](../behavior-changes/target/security/safer-intents-impact.md) | [要約](../summaries/target/security/safer-intents-impact-summary.md) | `OPT_IN_ONLY` | `platform/frameworks/base` | 再検証済み |
| [Safer Intents: Testing and debugging](../behavior-changes/target/security/safer-intents-testing-and-debugging.md) | [要約](../summaries/target/security/safer-intents-testing-and-debugging-summary.md) | `OPT_IN_ONLY` | `platform/frameworks/base` | 再検証済み |
| [Safer Intents](../behavior-changes/target/security/safer-intents.md) | [要約](../summaries/target/security/safer-intents-summary.md) | `OPT_IN_ONLY` | `platform/frameworks/base` | 再検証済み |
| [Edge to edge opt-out going away 調査レポート](../behavior-changes/target/user-experience-and-system-ui/edge-to-edge-opt-out-going-away.md) | [要約](../summaries/target/user-experience-and-system-ui/edge-to-edge-opt-out-going-away-summary.md) | `TARGET_SDK_36_CONDITIONAL` | `platform/frameworks/base` | 再検証済み |
| [Elegant font APIs deprecated and disabled 調査レポート](../behavior-changes/target/user-experience-and-system-ui/elegant-font-apis-deprecated-and-disabled.md) | [要約](../summaries/target/user-experience-and-system-ui/elegant-font-apis-deprecated-and-disabled-summary.md) | `TARGET_SDK_36_CONDITIONAL` | `platform/frameworks/base` | 再検証済み |
| [Predictive Back への移行または opt-out が必要 - 調査レポート](../behavior-changes/target/user-experience-and-system-ui/migration-or-opt-out-required-for-predictive-back.md) | [要約](../summaries/target/user-experience-and-system-ui/migration-or-opt-out-required-for-predictive-back-summary.md) | `TARGET_SDK_36_CONDITIONAL` | `platform/frameworks/base` | 再検証済み |

## 変更点と制約

- 公式 section inventory との照合により、未収録だった `New way to remove bluetooth bond` の主レポートと1ページ要約を追加した。
- 実機試験は今回実施していない。Expected と Observed を混同せず、未実施状態を維持した。
- 最終判断は [`DECISION_LOG.md`](../decisions/DECISION_LOG.md) のみが正本である。

# Android 15 → 16 UI and Device Form Factors 挙動比較

## 1. 比較範囲

- [比較一覧](README.md)
- [ケース別対応手順](../case-guides/ui-and-device-form-factors.md)
- Baseline: Android 15 / `android-15.0.0_r36`
- Target: Android 16 / `android-16.0.0_r4`
- QPR項目: Automatic themed app icons は Android 16 QPR2 をtargetとする
- Observed: screenshot、screen recording、assistive technology、projection端末で未実施

## 2. 先に結論

UI系では OS、targetSdkVersion、window size、navigation mode、QPR / launcher を混ぜないことが重要である。
target 36 で変わる adaptive layouts、edge-to-edge、Predictive Back、font と、OS updateだけでも
条件付きで変わる virtual projection、3-button Back、QPR2 themed icons を別々に比較する。

## 3. 項目別比較

### Adaptive layouts

- [主レポート](../target/device-form-factors/adaptive-layouts.md)
- [要約](../../summaries/target/device-form-factors/adaptive-layouts-summary.md)
- 適用: `TARGET_SDK_36_CONDITIONAL` + `sw >= 600dp`

| 観点 | Android 15 | Android 16 / target 36 |
| --- | --- | --- |
| System behavior | 固定方向、サイズ変更不可、aspect ratio制約によりpillarbox / compat表示し得る | large screenでは制約を既定で無視し、利用可能window全体へ |
| App signal | 要求した画面の向き / 固定された領域に近いlayout | rotation、resize、configuration change、広いbounds |
| 対応 | phone固定前提を検出 | WindowMetrics、adaptive pane、state保存、resize / rotate試験 |

game、user aspect ratio、temporary opt-out などの例外は主レポートで確認する。

### Virtual device owner overrides

- [主レポート](../all/device-form-factors/virtual-device-owner-overrides.md)
- [要約](../../summaries/all/device-form-factors/virtual-device-owner-overrides-summary.md)
- 適用: `OS_UPDATE_ALL_APPS` + privileged virtual device owner projection

| 観点 | Android 15 | Android 16 |
| --- | --- | --- |
| System behavior | appのorientation / aspect / resizability制約がprojectionでも効く前提 | trusted ownerがselect virtual device上で制約をoverride可能 |
| App signal | portrait / fixed boundsになりやすい | remote displayのlandscape / large / resizable bounds |
| 対応 | projection有無を棚卸し | owner / display条件を記録し、keyboard / mouse / controllerも含めadaptive化 |

通常のphone local displayには一般化しない。

### Edge-to-edge opt-out going away

- [主レポート](../target/user-experience-and-system-ui/edge-to-edge-opt-out-going-away.md)
- [要約](../../summaries/target/user-experience-and-system-ui/edge-to-edge-opt-out-going-away-summary.md)
- 適用: `TARGET_SDK_36_CONDITIONAL`

| 観点 | Android 15 / target 36 | Android 16 / target 36 |
| --- | --- | --- |
| System behavior | `windowOptOutEdgeToEdgeEnforcement=true` が機能 | Change ID `377864165` により同opt-outを無視 |
| App signal | contentはsystem bar内側に留められる | contentがsystem bar / cutout背後へ。未処理controlが重なり得る |
| 対応 | opt-out依存画面をinventory | Compose / Viewsでbar、cutout、IME、gesture insetを処理 |

### Predictive Back

- [主レポート](../target/user-experience-and-system-ui/migration-or-opt-out-required-for-predictive-back.md)
- [Dispatcher / animation guide](../target/user-experience-and-system-ui/migration-or-opt-out-required-for-predictive-back-dispatcher-animation-guide.md)
- [要約](../../summaries/target/user-experience-and-system-ui/migration-or-opt-out-required-for-predictive-back-summary.md)
- 適用: `TARGET_SDK_36_CONDITIONAL`

| 観点 | Android 15 | Android 16 / target 36 |
| --- | --- | --- |
| System behavior | target36 default enableはflag依存 | predictive backがdefault enabled |
| App signal | legacy `onBackPressed()` / `KEYCODE_BACK`へ届き得る | supported Back callback path。legacy hookは通常呼ばれない |
| Animation | edge gestureは移行状態に依存 | system predictive animation。custom UIはprogress callbackで追従 |
| 対応 | legacy interceptionを検出 | AndroidX / `OnBackInvokedCallback`へ移行。未移行Activityだけ一時opt-out |

toolbarやcustom buttonからDispatcherを呼ぶ操作はgesture progressを持たないため、
edge swipeと同じpredictive animationを期待しない。

### 3-button Predictive Back

- [主レポート](../all/user-experience-and-system-ui/support-for-3-button-navigation-predictive-back.md)
- [要約](../../summaries/all/user-experience-and-system-ui/support-for-3-button-navigation-predictive-back-summary.md)
- 適用: Android 16 + 3-button navigation + predictive back移行状態

| 観点 | Android 15 | Android 16 |
| --- | --- | --- |
| System behavior | Back button long-pressのpredictive previewなし | long-pressでhome / task / previous Activityをpreview |
| App signal | short press中心 | short press commitに加えlong-press preview |
| 対応 | gesture navigationだけのQAになりやすい | 3-button short / long press、deep link、task stackを画面録画 |

### Accessibility announcements

- [主レポート](../all/user-experience-and-system-ui/deprecating-disruptive-accessibility-announcements.md)
- [要約](../../summaries/all/user-experience-and-system-ui/deprecating-disruptive-accessibility-announcements-summary.md)
- 適用: all-apps documentation / API deprecation。runtime blockではない

| 観点 | Android 15 | Android 16 |
| --- | --- | --- |
| System behavior | `announceForAccessibility()` / `TYPE_ANNOUNCEMENT`をdispatch | dispatch pathは残るがAPI / patternがdeprecated |
| App signal | assistive technologyがannouncementを読む |同様に届き得る。compileSdk 36でwarning |
| 対応 | announcement用途を分類 | pane title、live region、error semanticsなど文脈付き代替へ |

「Android 16で突然届かなくなる」とは扱わない。

### Elegant font APIs

- [主レポート](../target/user-experience-and-system-ui/elegant-font-apis-deprecated-and-disabled.md)
- [要約](../../summaries/target/user-experience-and-system-ui/elegant-font-apis-deprecated-and-disabled-summary.md)
- 適用: `TARGET_SDK_36_CONDITIONAL`

| 観点 | Android 15 | Android 16 / target 36 |
| --- | --- | --- |
| System behavior | `elegantTextHeight=false`でcompact metricsへopt-out可能 | `false` overrideを無効化し、scriptに適したmetricsを使用 |
| App signal |固定高さ内に収まる前提 | line height / baseline変化、clipping、wrap |
| 対応 | fixed-height textと対象言語を検出 | dynamic height、padding、line spacing、scrollとscreenshot test |

対象言語には Arabic、Lao、Myanmar、Tamil、Gujarati、Kannada、Malayalam、Odia、
Telugu、Thai を含める。

### Automatic themed app icons

- [主レポート](../all/user-experience-and-system-ui/automatic-themed-app-icons.md)
- [要約](../../summaries/all/user-experience-and-system-ui/automatic-themed-app-icons-summary.md)
- 適用: `OS_UPDATE_ALL_APPS` + Android 16 QPR2 + supported launcher + themed icons enabled

| 観点 | Android 15 | Android 16 QPR2 |
| --- | --- | --- |
| System behavior | app提供monochrome layerがthemed iconの基本 | monochrome未提供でもlauncherがfallback bitmapを自動生成可能 |
| App signal | standard iconまたはapp制御のmonochrome | brand color / shape / contrastがlauncher生成結果へ変化 |
| 対応 | icon variantsをinventory | adaptive iconへ明示`<monochrome>`を追加し、launcher別preview / cacheを確認 |

Android 16 base releaseとQPR2を同一条件にしない。targetSdkVersion gateはない。

## 4. OS / targetSdk / device マトリクス

| 項目 | Android 15 | Android 16 / target35 | Android 16 / target36 | 追加条件 |
| --- | --- | --- | --- | --- |
| Adaptive layouts | manifest制約 | target35はbaseline | large screenで制約無視 | `sw>=600dp`、exceptions |
| Virtual owner | baseline projection | owner override可能 | target35と同じ | privileged virtual device |
| Edge-to-edge | opt-out機能 | target35はbaseline | opt-out無効 | opt-out使用 |
| Predictive Back | defaultはflag依存 | target35はbaseline | default enabled | opt-out / migration |
| 3-button Back | long-press previewなし | predictive対応時preview |対象flow増加 | navigation mode |
| Accessibility | dispatch | dispatch継続 / deprecation |同左 | compileSdk / usage |
| Elegant font | false override可 | target35はbaseline | false override無効 | script / layout |
| Themed icons | launcher baseline | base release対象外 | base release対象外 | QPR2 / launcher |

## 5. 比較試験

| Case | 固定条件 | Expected Android 15 | Expected Android 16 | Observed |
| --- | --- | --- | --- | --- |
| U1 | fixed portrait app / tablet | pillarbox等 | target36でfull bounds | 未実施 |
| U2 | edge opt-out theme | opt-out機能 | target36で無視 | 未実施 |
| U3 | legacy Back hook | callback受信 | target36 defaultで非受信 | 未実施 |
| U4 | 3-button long press | previewなし | predictive preview | 未実施 |
| U5 | elegant=false /対象言語 | compact metrics | target36で適切なmetrics | 未実施 |
| U6 | monochromeなしicon | standard / launcher依存 | QPR2でauto theme | 未実施 |

visual testではwindow size、orientation、font scale、navigation mode、IME、cutout、
input modality、QPR、launcherを記録する。

## 6. Evidence / Human Decision

Facts、AOSP gate、例外、confidence は各主レポートを正とする。
この資料は Expected behavior の synthesis であり、Observed result と Human Decision は確定しない。

# Android 16 UI and Device Form Factors - ケース別対応手順

## 位置づけ

このファイルは Android 16 の UI / device form factor 変更をケース別に実装・検証へ落とす companion guide である。
適用条件と根拠はリンク先の調査レポートを正とする。

## Adaptive layouts

Report: [Adaptive layouts](../target/device-form-factors/adaptive-layouts.md)

| ケース | 判定条件 | 対応手順 | 最低限の検証 |
| --- | --- | --- | --- |
| `< sw600dp` | small screen | 従来挙動を baseline とする | portrait / landscape |
| `>= sw600dp` + responsive | orientation / aspect ratio 制約に非依存 | target 36 で通常 regression | tablet / foldable / desktop |
| Fixed orientation / non-resizable | manifest / runtime restriction に依存 | WindowMetrics と adaptive layout へ移行し state preservation を実装 | rotate / resize / split screen |
| Off-screen / stretched UI | fixed dimensions / animation assumptions | constraint、scroll、pane、dialog位置を修正 | extreme aspect ratio |
| Game exception | `appCategory=game` | exception 適用を確認し、将来適応の backlog を残す | category有無 |
| Temporary opt-out | 未移行 Activity がある | Activity単位 property を優先し、理由と削除条件を記録 | opt-out有無。API 37では無効予定 |

## Virtual device owner overrides

Report: [Virtual device owner overrides](../all/device-form-factors/virtual-device-owner-overrides.md)

| ケース | 判定条件 | 対応手順 | 最低限の検証 |
| --- | --- | --- | --- |
| Projection なし | virtual / external display use case なし | 対応不要 | feature inventory |
| Untrusted / ordinary display | owner override 条件外 | 通常 display behavior を確認 | display owner / trust |
| Privileged virtual device owner | projection app が制約を override | fixed orientation 等を信用せず adaptive UI にする | remote bounds / rotation |
| Small portrait-only layout | projected large / landscape で破綻 | pane、scroll、responsive breakpointsを追加 | car / PC / XR-like bounds |
| Input modality changes | keyboard / mouse / controller | touch-only assumption を除去 | focus / hover / key / controller |

## Edge-to-edge opt-out going away

Report: [Edge to edge opt-out going away](../target/user-experience-and-system-ui/edge-to-edge-opt-out-going-away.md)

| ケース | 判定条件 | 対応手順 | 最低限の検証 |
| --- | --- | --- | --- |
| 既に対応済み | opt-out なし + insets処理済み | regression のみ | gesture / 3-button、IME |
| Android 15 / target 36 | opt-out がまだ機能 | baseline として残すが属性依存を削除 | Android 15 target 36 |
| Android 16 / target 36 | opt-out disabled | Compose / Views guidance で system bar / cutout insets を適用 | top / bottom controls |
| Mixed screens | 一部だけ opt-out 依存 | Activity / screen ごとに migration inventory を作る | all entry points |
| Custom drawing / immersive | overlay / media / camera | content領域と tappable controls の insetsを分離 | rotation / IME / cutout |

## Predictive Back

Reports:
- [Primary report](../target/user-experience-and-system-ui/migration-or-opt-out-required-for-predictive-back.md)
- [Dispatcher animation guide](../target/user-experience-and-system-ui/migration-or-opt-out-required-for-predictive-back-dispatcher-animation-guide.md)
- [Implementation examples](migration-or-opt-out-required-for-predictive-back-implementation-examples.md)

| ケース | 判定条件 | 対応手順 | 最低限の検証 |
| --- | --- | --- | --- |
| Supported Navigation のみ | AndroidX / Navigation built-in integration | root consuming callback を追加せず library に委ねる | in-app / home / cross-activity |
| Legacy Back interception | `onBackPressed` / `KEYCODE_BACK` | supported callback API へ移行 | target 35 / 36 |
| UI state の独自 Back | drawer / dialog / selection | state中だけ callback enabled | state open / closed |
| Gesture追従 custom UI | progress animation が必要 | `PredictiveBackHandler` または Views progress callback | start / progress / cancel / commit |
| Toolbar / custom button | programmatic invocation | Upなら `navigateUp()`。Dispatcher呼出しにgesture animationを期待しない | toolbar vs edge swipe |
| 未移行 Activity | migration が間に合わない | Activity単位 temporary opt-out と削除条件 | opt-out有無 |

## 3-button Predictive Back

Report: [Support for 3-button navigation](../all/user-experience-and-system-ui/support-for-3-button-navigation-predictive-back.md)

| ケース | 判定条件 | 対応手順 | 最低限の検証 |
| --- | --- | --- | --- |
| Gesture navigation のみ検証済み | 3-button 未試験 | Android 16 QA に追加 | short press / long press |
| Properly migrated app | predictive support 有効 | preview destination を画面録画で確認 | home / task / Activity |
| Legacy interception | old callback / key handling | Predictive Back migration と同じ棚卸しを実施 | animation + final destination |
| Deep link entry | task / Activity stack が通常と異なる | long press preview と commit先を確認 | cold / warm deep link |

## Accessibility announcements

Report: [Deprecating disruptive accessibility announcements](../all/user-experience-and-system-ui/deprecating-disruptive-accessibility-announcements.md)

| ケース | 判定条件 | 対応手順 | 最低限の検証 |
| --- | --- | --- | --- |
| Usage なし | announcement API 未使用 | 対応不要 | code search |
| Window / screen change | title通知が目的 | Activity title / pane title へ移行 | focus / spoken context |
| Dialog / pane / section | semantic領域変更 | `accessibilityPaneTitle` / Compose `paneTitle` | open / close |
| Critical dynamic update | 状態更新を通知 | live region を必要最小限で使用 | repeated update noise |
| Error | validation failure | node / TextView error semantics を使う | focus移動 / error reading |
| Custom announcement が残る | 代替困難 |理由を記録し複数 assistive technology で検証 | TalkBack以外も含む |

## Elegant font APIs

Report: [Elegant font APIs deprecated and disabled](../target/user-experience-and-system-ui/elegant-font-apis-deprecated-and-disabled.md)

| ケース | 判定条件 | 対応手順 | 最低限の検証 |
| --- | --- | --- | --- |
| API 未使用 | elegant height 非依存 | 通常 typography regression | target 35 / 36 |
| `false` override 依存 | compact metrics 前提 | override削除を前提に container / padding / line spacing を調整 | 対象言語 screenshot |
| Fixed-height text | clipping risk | dynamic height / wrapping / scroll を導入 | large font / multiple lines |
| Custom font | system UI font と別 | font metrics を実測して対象外と断定 | script別 rendering |

対象言語:
- Arabic、Lao、Myanmar、Tamil、Gujarati、Kannada、Malayalam、Odia、Telugu、Thai。

## Automatic themed app icons

Report: [Automatic themed app icons](../all/user-experience-and-system-ui/automatic-themed-app-icons.md)

| ケース | 判定条件 | 対応手順 | 最低限の検証 |
| --- | --- | --- | --- |
| Monochrome layer あり | adaptive icon に定義済み | brand contrast を維持し regression | light / dark / wallpaper |
| Monochrome layer なし | Android 16 QPR2+ で自動生成 | previewと実機を確認し、不適切なら専用 layer を追加 | themed on / off |
| Legacy bitmap icon | adaptive icon 未整備 | adaptive + monochrome resource への移行を評価 | launcher別表示 |
| Activity alias / dynamic icon |複数 resource を切替 | 全 icon variant を個別に用意・確認 | enable / disable / cache |
| OEM launcher差 | AOSP / Pixel以外 | launcher dependency を記録し主要OEMでQA | icon cache / palette |

## Verification status

- この分冊は documentation synthesis であり、対象アプリの screenshot、screen recording、assistive technology、projection device の observed result は未実施。
- Visual change は phone 1台だけで完了とせず、window size、orientation、input、font scale、navigation mode を記録する。

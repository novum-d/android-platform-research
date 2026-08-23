# Ignore orientation, resizability, and aspect ratio restrictions - 1ページ要約（One Page Summary）

## 対象（Target）

Android 16 Behavior Change

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:

## 適用条件（Applicability）

- 主分類（Primary classification）: `TARGET_SDK_36_CONDITIONAL`
- OS アップデート / 全アプリ（OS update / all apps）: No。Android 16 へ OS アップデートしただけで targetSdkVersion 35 以下の全アプリに既定適用されるとは判断しない。
- targetSdkVersion 36 以上: Yes。`UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415 が targetSdkVersion 36 以上で default enabled。
- その他の必須条件（Other required conditions）: Android 16 以上、display `sw >= 600dp`、game ではない、temporary opt-out なし、user aspect ratio setting exception なし。
- 表示状態: full-screen または multi-window のどちらでも対象。multi-window には split screen と desktop windowing が含まれる。
- `sw` の意味: 現在のアプリウィンドウ幅ではなく表示先ディスプレイの `smallestScreenWidthDp`。ウィンドウ幅が 600dp 未満になったことだけでは対象外にならない。
- Compat Change ID: `UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415
- Compat default state: Android 16 / API level 36 以上を target するアプリで enabled。AOSP annotation は `@EnabledAfter(VANILLA_ICE_CREAM)`。
- Temporary opt-out: `android.window.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY=true` を application または activity property として指定。ただし公式文書と AOSP TODO は API 37 以降で使えなくなる予定を示す。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ | 期待挙動 |
| --- | --- |
| Android 16 / targetSdkVersion 35 | 本 Behavior Change の既定適用対象外。従来の orientation / aspect ratio / compatibility mode を維持する想定 |
| Android 16 / targetSdkVersion 36 / `sw >= 600dp` / opt-outなし | 固定方向、サイズ変更不可、min/max aspect ratioの制約が無視され、pillarboxingなしでwindow全体を使用 |
| 上記条件 / full-screen | 制約無視の対象 |
| 上記条件 / split screen | multi-window の一形態として制約無視の対象 |
| 上記条件 / desktop windowing | multi-window の一形態として制約無視の対象。現在のwindow幅が600dp未満でもdisplayの`sw`条件は変わらない |
| Android 16 / targetSdkVersion 36 / `sw < 600dp` | large screen 条件を満たさないため対象外 |
| Android 16 / targetSdkVersion 36 / game app | `ApplicationInfo.CATEGORY_GAME` により対象外 |
| Android 16 / targetSdkVersion 36 / user aspect ratio setting exception | user preferenceがサイズ変更不可と互換な場合は、あらゆるウィンドウサイズへ変更可能とする判定から外れる |
| Android 16 / targetSdkVersion 36 / opt-out あり | Android 16 では従来の compatibility mode 側へ一時的に戻せる |
| Android 15 / targetSdkVersion 36 | Android 16 の large screen default ignore 差分はないため、同一挙動とは結論しない |

## 要約（Summary）

Android 16 では、targetSdkVersion 36 以上のアプリが large screen（`sw >= 600dp`）で実行される場合、orientation、resizability、aspect ratio の制約が既定で無視される。アプリは user preferred orientation や manifest aspect ratio に関係なく display window 全体を使う。

ここで公式文書の「full-screen and multi-window modes」は、両方を同時に満たすという意味ではなく、full-screen と multi-window のどちらでも制約が無視されるという意味である。desktop windowing は multi-window の一形態として対象に含まれる。`sw >= 600dp` は表示先ディスプレイの条件であり、現在のアプリウィンドウ幅や端末の向きだけでは変わらない。

この変更は Android 16 への OS アップデートだけの影響ではなく、Android 16 端末上で targetSdkVersion 36 化した場合の large screen behavior change として扱う。

## 顧客影響（Customer Impact）

- 要確認

理由:
- 影響は targetSdkVersion 36 化、Android 16、`sw >= 600dp`、非 game、opt-out なし、user exception なしが重なった場合に発生する。
- 固定方向、サイズ変更不可、min/max aspect ratio、pillarboxingを前提とするUIではvisual regressionが起きやすい。
- opt-out は一時的で、API 37 以降を見据えた adaptive layout 対応が必要。

## 影響対象（Who Is Affected）

- portrait / landscape 固定に依存するアプリ。
- `resizeableActivity=false` に依存するアプリ。
- `minAspectRatio` / `maxAspectRatio` に依存するアプリ。
- pillarboxing / compatibility mode に依存するアプリ。
- `setRequestedOrientation()` を runtime に呼ぶアプリ。
- `getRequestedOrientation()`の戻り値と、システムが実際に採用した画面の向きを混同しているアプリ。
- preferred orientation / user orientation 前提の UI を持つアプリ。
- fixed aspect ratio 前提の UI を持つアプリ。
- large screen / tablet / foldable / desktop windowing 対応が不十分なアプリ。
- Compose UI / View UI のどちらも対象。window bounds の問題なので UI toolkit だけでは回避できない。

## 対応要否（Required Action）

- 必須対応: targetSdkVersion 36化するアプリで、large screen上の固定方向 / サイズ変更不可 / aspect ratio / pillarboxingの前提がある場合。
- 推奨対応: adaptive layout、state preservation、split screen、desktop windowing、foldable posture、visual regression の確認。
- 一時対応: Android 16 target では `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY=true` を activity または application に指定できるが、恒久対応として扱わない。
- 不要に近い: large screen でも既に responsive に動作し、orientation / aspect ratio / non-resizable 制約に依存していないアプリ。

## テストマトリクス（Test Matrix）

| 端末 OS | targetSdkVersion | 条件 | 期待挙動 |
| --- | --- | --- | --- |
| Android 15 | 35 | baseline | 従来挙動 |
| Android 16 | 35 | OS update only | 本 Behavior Change の既定適用対象外 |
| Android 16 | 36 | `sw >= 600dp` / opt-out なし | 制約無視、window 全体を使用 |
| Android 16 | 36 | `sw >= 600dp` / Activity opt-out | 該当 activity は一時的に従来挙動 |
| Android 16 | 36 | `sw >= 600dp` / Application opt-out | package 全体で一時的に従来挙動 |
| Android 16 | 36 | `sw < 600dp` | 対象外 |
| Android 16 | 36 | game category | 対象外 |
| Android 16 | 36 | user aspect ratio setting exception | user preferenceにより、あらゆるウィンドウサイズへ変更可能とする判定から外れる |

追加テスト:
- Android 15 / targetSdkVersion 36 が検証可能な場合の比較。
- portrait / landscape / reverse / sensor / user orientation 指定。
- `setRequestedOrientation()` 呼び出し後の orientation、configuration、activity recreation。
- `getRequestedOrientation()`の戻り値と、アプリに実際に割り当てられたウィンドウ領域。
- `resizeableActivity=false`、`minAspectRatio`、`maxAspectRatio` 指定あり / なし。
- full-screen、multi-window、split screen、desktop windowing。
- user aspect ratio settings。
- stretched layout、off-screen component、固定アスペクト比 UI、Activity state preservation、screenshot regression。

## 顧客向け説明（Explanation for Customers）

Android 16 へ OS アップデートしただけで、targetSdkVersion 35 以下のアプリにこの変更が既定適用されるとは説明しません。
targetSdkVersion 36 以上に上げると、Android 16 端末の large screen では固定 orientation、非 resizable、min/max aspect ratio、pillarboxing の前提が効かなくなります。
この制約無視は full-screen と multi-window の両方に適用され、multi-window には split screen と desktop windowing が含まれます。`sw600dp` は表示先ディスプレイの判定であり、現在のアプリウィンドウ幅が 600dp 未満になっただけでは対象外になりません。
対象アプリは tablet / foldable / desktop windowing / split screen で、画面全体または可変windowに表示されたときの layout、state preservation、visual regression を確認してください。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/16/behavior-changes-16#ignore-orientation
- Multi-window definition: https://developer.android.com/develop/adaptive-apps/guides/support-multi-window-mode
- Compat framework: `UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415、Android 16 / API 36 以上 target で enabled。
- AOSP files: `ActivityInfo.java`、`WindowManager.java`、`DisplayContent.java`、`ActivityRecord.java`、`AppCompatResizeOverrides.java`、`AppCompatAspectRatioPolicy.java`、`AppCompatAspectRatioOverrides.java`。
- AOSP source context: `DisplayContent#getIgnoreOrientationRequest()` -> `ActivityRecord#isUniversalResizeable()` -> orientation / resizability / aspect ratio policy。
- Diff interpretation: Android 16 tag で large screen default ignore 経路が追加。compat gate は targetSdkVersion 36、game / opt-out / user setting は例外。
- Gate conclusion: Android 16 以上 + targetSdkVersion 36 以上 + `sw >= 600dp` + non-game + opt-out なし + user exception なし。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 未判断

判断（Decision）:
- 未判断

Owner notes:
- 最終優先度、severity、release readiness、顧客 communication priority は repository owner が判断する。

## 再検証記録（2026-08-22）

- Android 16 の公式 Behavior Change 一覧と最新通常AOSPタグを再確認した。
- 対応する[主レポート](../../../behavior-changes/target/device-form-factors/ignore-orientation-resizability-and-aspect-ratio-restrictions.md)で official section、AOSP project / remote / checkout、解決済み commit、比較 command、dirty risk を再検証した。
- 主レポートの分類、confidence、未確認事項を維持し、実機未実施の項目を Observed 済みへ変更していない。
- 全件の結果は[再検証台帳](../../../analysis/REVALIDATION_2026-08-22.md)を参照する。

## 追補確認（2026-08-23）

- full-screen / multi-window のOR条件、desktop windowing の位置づけ、display `sw` と現在のwindow幅の違いを主レポートと同期した。
- AOSP tag pair、主分類、confidence、Human Decision に変更なし。

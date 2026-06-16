# 大画面で画面向き・リサイズ可否・アスペクト比制約を無視するプラットフォーム API の変更（sw >= 600dp） - 1ページ要約

## 対象

Android 17 Behavior Change

比較元:
- android-16.0.0_r4

比較先:
- TBD: Android 17 AOSP タグ

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

## 適用条件

- 主分類（Primary classification）: UNKNOWN_NEEDS_MORE_EVIDENCE
- OS アップデート / 全アプリ: 未確認。原文は Android 17 / targetSdkVersion 37+ で opt-out unavailable と述べるが、AOSP gate は未確認。
- targetSdkVersion 37 以上: 公式文書上は該当。AOSP gate は未確認。
- その他の必須条件: 大画面、orientation / resizability / aspect ratio constraints、Android 16 opt-out 利用。詳細ページは smallest width が 600dp より大きい display と説明している。
- Compat Change ID: 未確認
- Compat default state: 未確認

## 早見マトリクス

| シナリオ | 影響 |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 未確認。Android 16 / SDK 36 opt-out が維持されるか AOSP 未確認。 |
| Android 17 / targetSdkVersion 37 | 公式文書上、SDK 36 で使えた opt-out が利用不可。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | large screen で orientation / resizability / aspect ratio constraints が無視される可能性。 |

## 要約

Android 17 では、targetSdkVersion 37 以上のアプリで、Android 16 / SDK 36 では可能だった large screen 制約無視への opt-out が利用できなくなる、と公式文書は説明している。

## 顧客影響

- 要確認

## 影響対象

- 対象アプリ: large screen で固定向き、固定 aspect ratio、non-resizable を前提にしているアプリ。
- 対象機能: tablet / foldable / desktop windowing / multi-window 上の Activity 表示。
- 対象条件: `sw >= 600dp`、targetSdkVersion 37 以上、Android 16 opt-out 依存、orientation / resizability / aspect ratio constraints の指定。

## 対応要否

- 必須対応: Android 16 opt-out 利用状況と manifest の orientation / resizability / aspect ratio 制約を棚卸しする。
- 推奨対応: large screen で adaptive layout、configuration change、multi-window resize、fold / unfold を検証する。`setRequestedOrientation()` / `getRequestedOrientation()` 依存、games 例外、user aspect ratio setting opt-in、`sw600dp` 未満 screen 例外も確認する。
- 不要: large screen で利用されず、固定向き・固定比率・非リサイズ制約に依存しないアプリでは直接影響は限定的。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 36 | 公式文書上、large screen 制約無視は導入済みだが opt-out 可能。 |
| Android 17 | 36 | 未確認。SDK 36 opt-out が維持されるか AOSP 未確認。 |
| Android 17 | 37 | opt-out は利用不可。large screen 上で orientation / resizability / aspect ratio restrictions が無視されると公式文書は説明。 |

## 顧客向け説明

Android 16 では、targetSdkVersion 36 以上のアプリについて、`sw >= 600dp` の large screen で orientation、resizability、aspect ratio constraints を platform が無視する変更が導入されました。SDK 36 では opt-out が可能でしたが、Android 17 / targetSdkVersion 37 以上ではその opt-out が利用できなくなります。

詳細ページでは、`screenOrientation`、`resizableActivity`、`minAspectRatio`、`maxAspectRatio`、`setRequestedOrientation()`、`getRequestedOrientation()` が large screen の full-screen / multi-window modes で ignored と説明されています。`UNIVERSAL_RESIZABLE_BY_DEFAULT` compat flag で test できる点も確認対象です。

固定 portrait、non-resizable、固定 aspect ratio を前提にした UI は、tablet、foldable、desktop windowing で表示崩れや想定外のリサイズが起きる可能性があります。現時点ではローカル AOSP checkout に Android 17 タグがないため、targetSdkVersion gate、opt-out removal の実装、compat flag の有無は未確認です。

## 根拠

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-17
- 検証対象の原文: Android 16 で API level 36+ 向けに large screens (`sw >= 600dp`) で orientation / aspect ratio / resizability restrictions を無視する変更が導入され、SDK 36 では opt-out 可能だったが、Android 17 / API level 37+ では opt-out 不可。
- AOSP ファイル: 未確認。ローカル `frameworks-base` に `android-17*` タグがない。
- AOSP ソース文脈: 未確認。タグ間 diff が実行できない。
- 差分解釈: 未分類。公式文書上は opt-out removal / changed condition と読めるが、AOSP diff による確認は Android 17 タグ待ち。
- 適用ゲートの結論: 未確認。公式文書は targetSdkVersion 37+ と large screen condition を示すが、AOSP gate evidence は未取得。

## 人間の判断欄

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 追加調査が必要

# 大画面で画面向き・リサイズ可否・アスペクト比制約を無視するプラットフォーム API の変更（sw >= 600dp） - 1ページ要約

## 対象

Android 17 挙動変更

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP タグ

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

## 適用条件

- 主分類（Primary classification）: UNKNOWN_NEEDS_MORE_EVIDENCE
- OS アップデート / 全アプリ: 未確認。原文は Android 17 / targetSdkVersion 37+ で opt-out unavailable と述べるが、AOSP 適用ゲートは未確認。
- targetSdkVersion 37 以上: 公式文書上は該当。AOSP 適用ゲートは未確認。
- その他の必須条件: 大画面、画面向き / リサイズ可否 / アスペクト比制約、Android 16 opt-out 利用。詳細ページは smallest width が 600dp より大きい display と説明している。
- Compat Change ID: 未確認
- Compat のデフォルト状態: 未確認

## 早見マトリクス

| シナリオ | 影響 |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 未確認。Android 16 / SDK 36 opt-out が維持されるか AOSP 未確認。 |
| Android 17 / targetSdkVersion 37 | 公式文書上、SDK 36 で使えた opt-out が利用不可。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | 大画面で画面向き / リサイズ可否 / アスペクト比制約が無視される可能性。 |

## 要約

Android 17 では、targetSdkVersion 37 以上のアプリで、Android 16 / SDK 36 では可能だった大画面制約の無視に対する opt-out が利用できなくなる、と公式文書は説明している。

## 顧客影響

- 要確認

## 影響対象

- 対象アプリ: 大画面で固定向き、固定アスペクト比、non-resizable を前提にしているアプリ。
- 対象機能: tablet / foldable / desktop windowing / multi-window 上の Activity 表示。
- 対象条件: `sw >= 600dp`、targetSdkVersion 37 以上、Android 16 opt-out 依存、画面向き / リサイズ可否 / アスペクト比制約の指定。

## 対応要否

- 必須対応: Android 16 opt-out 利用状況と manifest の画面向き / リサイズ可否 / アスペクト比制約を棚卸しする。
- 推奨対応: 大画面で adaptive layout、構成変更、multi-window resize、fold / unfold を検証する。`setRequestedOrientation()` / `getRequestedOrientation()` 依存、games 例外、ユーザーのアスペクト比設定による opt-in、`sw600dp` 未満の画面の例外も確認する。
- 不要: 大画面で利用されず、固定向き・固定比率・非リサイズ制約に依存しないアプリでは直接影響は限定的。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 36 | 公式文書上、大画面制約の無視は導入済みだが opt-out 可能。 |
| Android 17 | 36 | 未確認。SDK 36 opt-out が維持されるか AOSP 未確認。 |
| Android 17 | 37 | opt-out は利用不可。大画面上で画面向き / リサイズ可否 / アスペクト比制限が無視されると公式文書は説明。 |

## 顧客向け説明

Android 16 では、targetSdkVersion 36 以上のアプリについて、`sw >= 600dp` の大画面で画面向き、リサイズ可否、アスペクト比制約を platform が無視する変更が導入されました。SDK 36 では opt-out が可能でしたが、Android 17 / targetSdkVersion 37 以上ではその opt-out が利用できなくなります。

詳細ページでは、`screenOrientation`、`resizableActivity`、`minAspectRatio`、`maxAspectRatio`、`setRequestedOrientation()`、`getRequestedOrientation()` が大画面の full-screen / multi-window modes で無視されると説明されています。`UNIVERSAL_RESIZABLE_BY_DEFAULT` compat flag でテストできる点も確認対象です。

固定 portrait、non-resizable、固定アスペクト比を前提にした UI は、tablet、foldable、desktop windowing で表示崩れや想定外のリサイズが起きる可能性があります。現時点ではローカル AOSP checkout に Android 17 タグがないため、targetSdkVersion 適用ゲート、opt-out removal の実装、compat flag の有無は未確認です。

## 根拠

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-17
- 検証対象の原文: Android 16 で API level 36+ 向けに大画面 (`sw >= 600dp`) で画面向き / アスペクト比 / リサイズ可否制限を無視する変更が導入され、SDK 36 では opt-out 可能だったが、Android 17 / API level 37+ では opt-out 不可。
- AOSP ファイル: 未確認。ローカルの `frameworks-base` に `android-17*` タグがない。
- AOSP ソース文脈: 未確認。タグ間差分を実行できない。
- 差分解釈: 未分類。公式文書上は opt-out removal / 変更された条件と読めるが、AOSP 差分による確認は Android 17 タグ待ち。
- 適用ゲートの結論: 未確認。公式文書は targetSdkVersion 37+ と大画面条件を示すが、AOSP 適用ゲート根拠は未取得。

## 人間の判断欄

最終優先度（Final Priority）:
- Human decision required

判断（Decision）:
- 追加調査が必要

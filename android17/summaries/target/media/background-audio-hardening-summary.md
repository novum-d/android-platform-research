# バックグラウンド音声の制限強化 - 1ページ要約

> 役割メモ:
> この要約は、バックグラウンド音声の制限強化の targetSdkVersion 37 追加条件を中心に扱う。
> Android 17 上の全アプリに関係する共通制限は [all/media/background-audio-hardening-summary.md](../../all/media/background-audio-hardening-summary.md) を参照する。

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
- OS アップデート / 全アプリ: 共通制限は [all/media/background-audio-hardening-summary.md](../../all/media/background-audio-hardening-summary.md) 側で扱う。
- targetSdkVersion 37 以上: 公式文書上は、より厳格な制限が該当。AOSP gate は未確認。
- その他の必須条件: background audio interaction、foreground service running、WIU capabilities、exact alarm permission、`USAGE_ALARM` audio stream。
- Compat Change ID: 未確認
- Compat default state: 未確認

## 早見マトリクス

| シナリオ | 影響 |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 未確認。一部 all apps 制限があると公式文書は述べるが、詳細未確認。 |
| Android 17 / targetSdkVersion 37 | background audio interaction には running foreground service が必要と公式文書は説明。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | FGS が WIU capabilities を持つ、または exact alarm permission + `USAGE_ALARM` 条件を満たす必要がある。 |

## 要約

Android 17 では、background からの audio playback、audio focus request、volume change APIs が hardening され、targetSdkVersion 37 以上では foreground service と追加条件が必要になる、と公式文書は説明している。

## 顧客影響

- 要確認

## 影響対象

- 対象アプリ: background で audio playback、audio focus request、volume change APIs を使うアプリ。
- 対象機能: 音楽、ポッドキャスト、アラーム、通話、ナビゲーション、録音、音声通知。
- 対象条件: targetSdkVersion 37 以上、background state、FGS なし、WIU capability なし、exact alarm + `USAGE_ALARM` 条件を満たさない audio interaction。

## 対応要否

- 必須対応: background audio API 呼び出し箇所を棚卸しし、foreground service / WIU / alarm 条件を満たすか確認する。
- 推奨対応: background audio 操作を user-initiated flow へ寄せ、alarm use case は exact alarm permission と `USAGE_ALARM` を明確にする。
- 不要: background audio interaction を行わないアプリでは直接影響は限定的。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 36 | Android 16 baseline。具体挙動は Android 17 タグ比較待ち。 |
| Android 17 | 36 | 未確認。一部 all apps 制限があると公式文書は述べるが、範囲未確認。 |
| Android 17 | 37 | background audio interaction には running FGS と WIU または exact alarm + `USAGE_ALARM` 条件が必要と公式文書は説明。 |

## 顧客向け説明

Android 17 では、background からの audio playback、audio focus request、volume change APIs に対する制限が強化されます。targetSdkVersion 37 以上のアプリが background で audio と interaction するには、foreground service が running であるだけでなく、WIU capabilities を持つか、exact alarm permission を持ち `USAGE_ALARM` audio stream を扱う必要があります。

現時点ではローカル AOSP checkout に Android 17 タグがないため、all apps 制限の範囲、targetSdkVersion gate、API ごとの failure mode、compat flag の有無は未確認です。Android 17 タグ公開後に AOSP evidence で再確認が必要です。

## 根拠

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-17
- 検証対象の原文: Android 17 では audio framework が background audio interactions を制限する。一部制限は all apps、targetSdkVersion 37 以上ではより厳格で、running FGS と WIU capability または exact alarm + `USAGE_ALARM` 条件が必要。
- AOSP ファイル: 未確認。ローカル `frameworks-base` に `android-17*` タグがない。
- AOSP ソース文脈: 未確認。タグ間 diff が実行できない。
- 差分解釈: 未分類。公式文書上は added behavior / changed condition と読めるが、AOSP diff による確認は Android 17 タグ待ち。
- 適用ゲートの結論: 未確認。公式文書は all apps 制限と targetSdkVersion 37+ 条件を示すが、AOSP gate evidence は未取得。

## 人間の判断欄

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 追加調査が必要

# バックグラウンド音声の制限強化 - 1ページ要約

> 役割メモ:
> この要約は、バックグラウンド音声の制限強化の targetSdkVersion 37 追加条件を中心に扱う。
> Android 17 上の全アプリに関係する共通制限は [all/media/background-audio-hardening-要約.md](../../all/media/background-audio-hardening-summary.md) を参照する。

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
- OS アップデート / 全アプリ: 共通制限は [all/media/background-audio-hardening-要約.md](../../all/media/background-audio-hardening-summary.md) 側で扱う。
- targetSdkVersion 37 以上: 公式文書上は、より厳格な制限が該当。AOSP 適用ゲートは未確認。
- その他の必須条件: バックグラウンドでの音声操作、フォアグラウンドサービス running、WIU capabilities、正確なアラーム権限、`USAGE_ALARM` 音声ストリーム。
- Compat Change ID: 未確認
- Compat のデフォルト状態: 未確認

## 早見マトリクス

| シナリオ | 影響 |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 未確認。一部全アプリ制限があると公式文書は述べるが、詳細未確認。 |
| Android 17 / targetSdkVersion 37 | バックグラウンドでの音声操作には running フォアグラウンドサービスが必要と公式文書は説明。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | FGS が WIU capabilities を持つ、または正確なアラーム権限 + `USAGE_ALARM` 条件を満たす必要がある。 |

## 要約

Android 17 では、バックグラウンドからの音声再生、オーディオフォーカス要求、音量変更 API が hardening され、targetSdkVersion 37 以上ではフォアグラウンドサービスと追加条件が必要になる、と公式文書は説明している。

## 顧客影響

- 要確認

## 影響対象

- 対象アプリ: バックグラウンドで音声再生、オーディオフォーカス要求、音量変更 API を使うアプリ。
- 対象機能: 音楽、ポッドキャスト、アラーム、通話、ナビゲーション、録音、音声通知。
- 対象条件: targetSdkVersion 37 以上、バックグラウンド状態、FGS なし、WIU capability なし、正確なアラーム + `USAGE_ALARM` 条件を満たさない音声操作。

## 対応要否

- 必須対応: バックグラウンド音声 API 呼び出し箇所を棚卸しし、フォアグラウンドサービス / WIU / alarm 条件を満たすか確認する。
- 推奨対応: バックグラウンド音声操作をユーザー起点のフローへ寄せ、alarm ユースケースは正確なアラーム権限と `USAGE_ALARM` を明確にする。
- 不要: バックグラウンドでの音声操作を行わないアプリでは直接影響は限定的。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 36 | Android 16 基準挙動。具体挙動は Android 17 タグ比較待ち。 |
| Android 17 | 36 | 未確認。一部全アプリ制限があると公式文書は述べるが、範囲未確認。 |
| Android 17 | 37 | バックグラウンドでの音声操作には実行中の FGS と WIU capability または正確なアラーム + `USAGE_ALARM` 条件が必要と公式文書は説明。 |

## 顧客向け説明

Android 17 では、バックグラウンドからの音声再生、オーディオフォーカス要求、音量変更 API に対する制限が強化されます。targetSdkVersion 37 以上のアプリがバックグラウンドで音声とやり取りするには、フォアグラウンドサービスが実行中であるだけでなく、WIU capabilities を持つか、正確なアラーム権限を持ち `USAGE_ALARM` 音声ストリームを扱う必要があります。

現時点ではローカル AOSP checkout に Android 17 タグがないため、全アプリ制限の範囲、targetSdkVersion 適用ゲート、API ごとの失敗時の挙動、compat flag の有無は未確認です。Android 17 タグ公開後に AOSP 根拠で再確認が必要です。

## 根拠

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-17
- 検証対象の原文: Android 17 では音声フレームワークがバックグラウンドでの音声操作を制限する。一部制限は全アプリ、targetSdkVersion 37 以上ではより厳格で、実行中の FGS と WIU capability または正確なアラーム + `USAGE_ALARM` 条件が必要。
- AOSP ファイル: 未確認。ローカルの `frameworks-base` に `android-17*` タグがない。
- AOSP ソース文脈: 未確認。タグ間差分を実行できない。
- 差分解釈: 未分類。公式文書上は追加された挙動 / 変更された条件と読めるが、AOSP 差分による確認は Android 17 タグ待ち。
- 適用ゲートの結論: 未確認。公式文書は全アプリ制限と targetSdkVersion 37+ 条件を示すが、AOSP 適用ゲート根拠は未取得。

## 人間の判断欄

最終優先度（Final Priority）:
- Human decision required

判断（Decision）:
- 追加調査が必要

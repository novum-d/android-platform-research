# Bluetooth ペアリング情報消失時の自律的な再ペアリング - 1ページ要約

## 対象（Target）

Android 17 挙動変更

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP タグ

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

## 適用条件（Applicability）

- 主分類（Primary classification）: UNKNOWN_NEEDS_MORE_EVIDENCE
- OS アップデート / 全アプリ: 公式文書上は該当候補。Android 17 の全アプリ向けページに掲載され、targetSdkVersion 条件は示されていない。
- targetSdkVersion 37 以上: 公式文書上は不要。AOSP 適用ゲートは未確認。
- その他の必須条件: Bluetooth 周辺機器のペアリング情報が失われ、システムが自律的な再ペアリングを試行すること。コンパニオンアプリがペアリング関連または `ACTION_KEY_MISSING` ブロードキャストを扱う場合は特に確認が必要。
- Compat Change ID: 未確認
- Compat default state: 未確認

## 早見マトリクス

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | ペアリング情報の消失後、システムが自律的な再ペアリングを試行する可能性。AOSP 適用ゲートは未確認。 |
| Android 17 / targetSdkVersion 37 | targetSdkVersion 36 と同様の可能性。公式文書に targetSdkVersion 条件なし。 |
| Android 17 / コンパニオンアプリがペアリング関連ブロードキャストを監視 | `ACTION_PAIRING_REQUEST` の文脈と `ACTION_KEY_MISSING` のタイミングを確認する必要がある。 |

## 要約

Android 17 では、Bluetooth のペアリング情報が失われた後に、システムが自律的な再ペアリングを試行できる。従来のように、ユーザーが OS の設定アプリで手動のペアリング解除と再ペアリングを行う必要が減る可能性がある。

## 顧客影響

- 要確認

## 影響対象

- 対象アプリ: Bluetooth コンパニオンアプリ、周辺機器メーカーのアプリ、wearable / audio / IoT / health 端末アプリ。
- 対象機能: ペアリング UX、ペアリング情報消失時の復旧、手動でのペアリング解除と再ペアリングのガイダンス、`ACTION_PAIRING_REQUEST` / `ACTION_KEY_MISSING` の handling。
- 対象条件: Bluetooth のペアリング情報の消失が発生し、システム管理の自律的な再ペアリングが試行される場合。

## 対応要否

- 必須対応: ペアリング情報消失時の復旧フローと、ペアリング関連 / `ACTION_KEY_MISSING` ブロードキャストの handling を棚卸しする。
- 推奨対応: `ACTION_PAIRING_REQUEST` の `EXTRA_PAIRING_CONTEXT` を確認し、通常のペアリングと自律的な再ペアリング試行を区別する。
- 注意: `ACTION_KEY_MISSING` は自律的な再ペアリング失敗時だけブロードキャストされるため、復旧成功時にも届く前提のエラーハンドリングは見直す。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 36 | 基準挙動。ペアリング情報の消失後の手動復旧フローを確認。 |
| Android 17 | 36 | システムが自律的な再ペアリングを試行する可能性。 |
| Android 17 | 37 | targetSdkVersion 36 と同じ期待。targetSdkVersion 条件は公式文書に記載なし。 |

## 顧客向け説明

Android 17 では、Bluetooth 周辺機器のペアリング情報が失われた場合、システムが自律的な再ペアリングによってバックグラウンドでペアリング情報の再確立を試行できます。

多くのアプリではコード変更は不要ですが、コンパニオンアプリや周辺機器メーカーのアプリは、`EXTRA_PAIRING_CONTEXT`、`ACTION_KEY_MISSING` のタイミング、システム管理の通知 / ダイアログとアプリ側の復旧 UI の整合を確認してください。

## 根拠

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-all
- 検証対象の原文: Android 17 は Bluetooth のペアリング情報の消失を自動的に解決する自律的な再ペアリングを導入する。`ACTION_PAIRING_REQUEST` に `EXTRA_PAIRING_CONTEXT` が追加され、`ACTION_KEY_MISSING` は自律的な再ペアリング失敗時だけブロードキャストされる。
- AOSP ファイル: 未確認。ローカルの `frameworks-base` に `android-17*` タグがない。
- AOSP ソース文脈: 未確認。タグ間差分が実行できない。Bluetooth stack は `packages/modules/Bluetooth` など `frameworks-base` 外も確認対象になる可能性が高い。
- 差分解釈: 未分類。公式文書上は、追加された挙動 / 変更されたブロードキャストタイミング / API surface addition と読めるが、AOSP 差分による確認は Android 17 タグ待ち。
- 適用ゲートの結論: 未確認。公式文書上は Android 17 全アプリ + Bluetooth のペアリング情報消失条件。targetSdkVersion 適用ゲート / Compat framework の根拠は未取得。

## 人間の判断欄

最終優先度（Final Priority）:
- Human decision required

判断（Decision）:
- Android 17 AOSP タグが利用可能になった後に追加調査が必要

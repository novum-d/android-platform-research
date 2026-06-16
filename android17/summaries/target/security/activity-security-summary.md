# Activity Security - 1ページ要約

## 対象（Target）

Android 17 Behavior Change

比較元:
- android-16.0.0_r4

比較先:
- TBD: Android 17 AOSP tag

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

## 適用条件（Applicability）

- 主分類（Primary classification）: UNKNOWN_NEEDS_MORE_EVIDENCE
- OS アップデート / 全アプリ（OS update / all apps）: 未確認。この section は targetSdkVersion 37 以上向けページにあるが、AOSP gate 未確認。
- targetSdkVersion 37 以上: 公式ページ種別上は該当と推定。AOSP gate 未確認。
- その他の必須条件（Other required conditions）: background activity launch、IntentSender / PendingIntent 経由の Activity 起動、ActivityOptions BAL mode、calling app visibility。
- Compat Change ID: 未確認
- Compat default state: 未確認

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 未確認。この section は targetSdkVersion 37 以上向けだが、AOSP gate 未確認。 |
| Android 17 / targetSdkVersion 37 | 公式文書上は、IntentSender へ BAL protections が拡張され、legacy BAL opt-in から granular controls への移行が必要。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` 依存を避け、visible state などに限定する `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` への移行が推奨される。 |

## 要約（Summary）

Android 17 では、Activity 起動まわりの security hardening として BAL restrictions が IntentSender にも拡張される、と公式文書は説明している。

## 顧客影響（Customer Impact）

- 要確認

## 影響対象（Who Is Affected）

- 対象アプリ: background から Activity を起動するアプリ、IntentSender / PendingIntent 経由で画面起動を委譲するアプリ。
- 対象機能: 通知、アラーム、認証、決済、デバイス連携、外部アプリ連携などの画面起動。
- 対象条件: targetSdkVersion 37 以上、BAL opt-in、legacy `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` 利用、calling app visibility に依存する起動。

## 対応要否（Required Action）

- 必須対応: `MODE_BACKGROUND_ACTIVITY_START_ALLOWED`、IntentSender / PendingIntent 経由の Activity 起動箇所を棚卸しする。
- 推奨対応: `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` などの granular controls へ移行し、strict mode / lint checks で legacy pattern を検出する。
- 不要: background activity launch や IntentSender 経由の画面起動を行わないアプリでは直接影響は限定的。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 16 | 36 | Android 16 baseline。具体挙動は Android 17 tag 比較待ち。 |
| Android 17 | 36 | 未確認。この section は targetSdkVersion 37 以上向けだが、AOSP gate 未確認。 |
| Android 17 | 37 | IntentSender へ BAL protections が拡張され、legacy broad opt-in から granular controls への移行が必要と公式文書は説明。 |

## 顧客向け説明（Explanation for Customers）

Android 17 では、background から Activity を起動する経路の安全性が強化され、IntentSender 経由の起動も BAL restrictions の対象として扱われる方向です。従来の `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` のような広い許可ではなく、呼び出し元が visible な場合だけ許可する `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` など、より限定的な opt-in へ移行する必要があります。

現時点では local AOSP checkout に Android 17 tag がないため、targetSdkVersion gate、実装上の適用範囲、compat flag の有無は未確認です。Android 17 tag 公開後に AOSP evidence で再確認が必要です。

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-17
- 検証対象の原文: Android 17 は secure-by-default architecture へ移行し、BAL restrictions を IntentSender に拡張する。開発者は legacy `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` から `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` などの granular controls へ移行する必要がある。
- AOSP ファイル: 未確認。local `frameworks-base` に `android-17*` tag がない。
- AOSP ソース文脈: 未確認。tag 間 diff が実行できない。
- 差分解釈: 未分類。added behavior / changed condition / changed default の判定は Android 17 tag 待ち。
- Gate conclusion: 未確認。公式ページ種別は targetSdkVersion 37 以上を示すが、AOSP gate evidence は未取得。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 追加調査が必要

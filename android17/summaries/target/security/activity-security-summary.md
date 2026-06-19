# Activity Security - 1ページ要約

## 対象（Target）

Android 17 Behavior Change

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

## 適用条件（Applicability）

- 主分類（Primary classification）: TARGET_SDK_37_CONDITIONAL
- OS アップデート / 全アプリ（OS update / all apps）: 主条件ではない。`ASM_RESTRICTIONS` は targetSdkVersion 37 以上で enabled。
- targetSdkVersion 37 以上: 該当。
- その他の必須条件（Other required conditions）: PendingIntent / IntentSender 経由の background activity start、ActivityOptions BAL mode、caller / real caller の visible state。
- Compat Change ID: `230590090L`
- Compat default state: `@EnabledAfter(targetSdkVersion = BAKLAVA)`。Android 17 / targetSdkVersion 37 以上で enabled。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | compat default では `ASM_RESTRICTIONS` disabled。 |
| Android 17 / targetSdkVersion 37 + `ALLOW_IF_VISIBLE` | caller / real caller が visible / foreground の場合に限定して BAL を許可。 |
| Android 17 / targetSdkVersion 37 + `ALLOW_ALWAYS` | BAL permission、SYSTEM_ALERT_WINDOW、allowlist など広い exemption を評価。特殊用途向け。 |

## 要約（Summary）

Android 17 では、PendingIntent / IntentSender 経由の Background Activity Launch がより厳格になり、legacy `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` から `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` または `MODE_BACKGROUND_ACTIVITY_START_ALLOW_ALWAYS` への移行が必要になる。

AOSP では `BackgroundActivityStartController.ASM_RESTRICTIONS = 230590090L` が `@EnabledAfter(BAKLAVA)` として定義され、targetSdkVersion 37 以上で Activity Security rules が enabled になることを確認した。

## 顧客影響（Customer Impact）

- 通知、アラーム、認証、決済、デバイス連携、外部アプリ連携などで background から画面を起動する設計に影響する。
- 通常用途では `ALLOW_IF_VISIBLE` を使い、visible でない状態からの起動は通知など user-mediated path に寄せる必要がある。
- 常時起動が必要な特殊用途だけ `ALLOW_ALWAYS` を検討する。

## 対応要否（Required Action）

- 必須対応候補: `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` と PendingIntent / IntentSender 経由の Activity 起動箇所を棚卸しする。
- 推奨対応: `ALLOW_IF_VISIBLE` へ移行し、background 状態では通知や foreground service 経由にする。
- テスト: targetSdkVersion 36 / 37、caller visible / background、`ALLOW_IF_VISIBLE` / `ALLOW_ALWAYS` を分けて検証する。

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-17
- AOSP: `core/java/android/app/ActivityOptions.java` の `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` は deprecated。
- AOSP: `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` は visible window がある場合だけ BAL privileges を付与。
- AOSP: `MODE_BACKGROUND_ACTIVITY_START_ALLOW_ALWAYS` は広い BAL privileges を付与する特殊用途向け mode。
- AOSP: `services/core/java/com/android/server/wm/BackgroundActivityStartController.java` の `ASM_RESTRICTIONS = 230590090L`
- AOSP: `ASM_RESTRICTIONS` は `@EnabledAfter(targetSdkVersion = BAKLAVA)` かつ `@Overridable`。
- AOSP: `ALLOW_IF_VISIBLE` の場合、caller / real caller visible / foreground 系 check に限定される。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断

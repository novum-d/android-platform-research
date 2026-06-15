# Background audio hardening - 1ページ要約（One Page Summary）

## 対象（Target）

Android 17 Behavior Change

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP tag

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

## 適用条件（Applicability）

- 主分類（Primary classification）: UNKNOWN_NEEDS_MORE_EVIDENCE
- OS アップデート / 全アプリ（OS update / all apps）: Conditional / Unknown。一部制限は all apps と公式文書は述べるが、範囲と AOSP gate 未確認。
- targetSdkVersion 37 以上: 公式文書上は、より厳格な制限が該当。AOSP gate 未確認。
- その他の必須条件（Other required conditions）: background audio interaction、foreground service running、WIU capabilities、exact alarm permission、`USAGE_ALARM` audio stream。
- Compat Change ID: Unknown
- Compat default state: Unknown

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | Unknown。一部 all apps 制限があると公式文書は述べるが、詳細未確認。 |
| Android 17 / targetSdkVersion 37 | background audio interaction には running foreground service が必要と公式文書は説明。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | FGS が WIU capabilities を持つ、または exact alarm permission + `USAGE_ALARM` 条件を満たす必要がある。 |

## 要約（Summary）

Android 17 では、background からの audio playback、audio focus request、volume change APIs が hardening され、targetSdkVersion 37 以上では foreground service と追加条件が必要になる、と公式文書は説明している。

## 顧客影響（Customer Impact）

- 要確認

## 影響対象（Who Is Affected）

- 対象アプリ: background で audio playback、audio focus request、volume change APIs を使うアプリ。
- 対象機能: 音楽、ポッドキャスト、アラーム、通話、ナビゲーション、録音、音声通知。
- 対象条件: targetSdkVersion 37 以上、background state、FGS なし、WIU capability なし、exact alarm + `USAGE_ALARM` 条件を満たさない audio interaction。

## 対応要否（Required Action）

- 必須対応: background audio API 呼び出し箇所を棚卸しし、foreground service / WIU / alarm 条件を満たすか確認する。
- 推奨対応: background audio 操作を user-initiated flow へ寄せ、alarm use case は exact alarm permission と `USAGE_ALARM` を明確にする。
- 不要: background audio interaction を行わないアプリでは直接影響は限定的。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 16 | 36 | Android 16 baseline。具体挙動は Android 17 tag 比較待ち。 |
| Android 17 | 36 | Unknown。一部 all apps 制限があると公式文書は述べるが、範囲未確認。 |
| Android 17 | 37 | background audio interaction には running FGS と WIU または exact alarm + `USAGE_ALARM` 条件が必要と公式文書は説明。 |

## 顧客向け説明（Explanation for Customers）

Android 17 では、background からの audio playback、audio focus request、volume change APIs に対する制限が強化されます。targetSdkVersion 37 以上のアプリが background で audio と interaction するには、foreground service が running であるだけでなく、WIU capabilities を持つか、exact alarm permission を持ち `USAGE_ALARM` audio stream を扱う必要があります。

現時点では local AOSP checkout に Android 17 tag がないため、all apps 制限の範囲、targetSdkVersion gate、API ごとの failure mode、compat flag の有無は未確認です。Android 17 tag 公開後に AOSP evidence で再確認が必要です。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-17
- Original statement: Android 17 では audio framework が background audio interactions を制限する。一部制限は all apps、targetSdkVersion 37 以上ではより厳格で、running FGS と WIU capability または exact alarm + `USAGE_ALARM` 条件が必要。
- AOSP files: 未確認。local `frameworks-base` に `android-17*` tag がない。
- AOSP source context: 未確認。tag 間 diff が実行できない。
- Diff interpretation: 未分類。公式文書上は added behavior / changed condition と読めるが、AOSP diff による確認は Android 17 tag 待ち。
- Gate conclusion: Unknown。公式文書は all apps 制限と targetSdkVersion 37+ 条件を示すが、AOSP gate evidence は未取得。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Human decision required

判断（Decision）:
- Further investigation required

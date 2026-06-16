# static final フィールドが変更不可に - 1ページ要約

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
- OS アップデート / 全アプリ: 未確認。公式文書は Android 17+ と targetSdkVersion 37+ の両方を条件としている。
- targetSdkVersion 37 以上: 公式文書上は該当。ただし AOSP 適用ゲートは未確認。
- その他の必須条件: static final フィールドを reflection または JNI で変更しようとする場合。
- Compat Change ID: 未確認
- Compat default state: 未確認

## 早見マトリクス

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 未確認。公式文書上は targetSdkVersion 37 以上向けだが、AOSP 適用ゲートは未確認。 |
| Android 17 / targetSdkVersion 37 | static final フィールド変更が拒否されると公式文書は説明。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | reflection では `IllegalAccessException`、JNI ではアプリクラッシュの可能性がある。 |

## 要約

Android 17 では、Android 17 以上で動作し targetSdkVersion 37 以上のアプリが static final フィールドを実行時に変更できなくなる、と公式文書は説明している。影響は reflection または JNI で static final フィールドを書き換えるコードに集中する。

## 顧客影響

- 要確認

## 影響対象

- 対象アプリ: targetSdkVersion 37 への更新を予定している Android アプリ。
- 対象機能: 機能フラグ override、SDK 内部値の変更、hot patch、mocking、hooking、diagnostics、ネイティブ instrumentation。
- 対象条件: 自社コードまたは SDK が reflection / JNI で static final フィールドを変更している場合。

## 対応要否

- 必須対応: static final フィールドの実行時 write を棚卸しする。
- 推奨対応: mutable 設定、dependency injection、server-side 設定など、static final フィールド書き換えに依存しない設計へ移行する。
- 不要: static final フィールドを読み取るだけで変更せず、関連 SDK も実行時 write していないことを確認できる場合は、互換性対応は限定的。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 36 | Android 16 基準挙動。具体挙動は Android 17 タグ比較待ち。 |
| Android 17 | 36 | 未確認。公式文書上は旧挙動維持が期待されるが、AOSP 適用ゲートは未確認。 |
| Android 17 | 37 | 公式文書上は static final フィールド変更が拒否される。 |

## 顧客向け説明

Android 17 では、targetSdkVersion 37 以上のアプリに対して static final フィールドの実行時変更が禁止される予定です。reflection で変更しようとした場合は `IllegalAccessException`、JNI API で変更しようとした場合はアプリクラッシュになると公式文書は説明しています。自社コードだけでなく、組み込み SDK やネイティブ library が static final フィールドを書き換えていないか確認する必要があります。

ただし、現時点ではローカル AOSP checkout に Android 17 タグがないため、targetSdkVersion 適用ゲートや compat flag の有無は未確認です。最終的な適用分類は Android 17 AOSP タグ公開後に再確認が必要です。

## 根拠

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-17
- 検証対象の原文: Android 17+ で動作し targetSdkVersion 37+ のアプリは static final フィールドを変更できない。reflection では `IllegalAccessException`、JNI ではクラッシュ。
- AOSP ファイル: 未確認。ローカルの `frameworks-base` に `android-17*` タグがない。
- AOSP ソース文脈: 未確認。タグ間差分が実行できない。
- 差分解釈: 未分類。added behavior / changed condition / changed default の判定は Android 17 タグ待ち。
- 適用ゲートの結論: 未確認。公式文書は Android 17+ / targetSdkVersion 37+ / static final フィールド write を条件として示すが、AOSP 適用ゲート根拠は未取得。

## 人間の判断欄

最終優先度（Final Priority）:
- Human decision required

判断（Decision）:
- 追加調査が必要

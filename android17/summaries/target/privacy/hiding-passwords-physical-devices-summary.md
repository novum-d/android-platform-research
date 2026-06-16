# 物理デバイス入力時のパスワード非表示 - 1ページ要約

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
- OS アップデート / 全アプリ（OS update / all apps）: 未確認。公式ページは targetSdkVersion 37 以上向け。
- targetSdkVersion 37 以上: 公式文書上は該当。AOSP gate 未確認。
- その他の必須条件（Other required conditions）: password field、physical input device、touchscreen input の setting 分岐。
- Compat Change ID: 未確認
- Compat default state: 未確認

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 未確認。公式文書上は targetSdkVersion 37 以上向けだが、AOSP gate 未確認。 |
| Android 17 / targetSdkVersion 37 | physical input device 使用時に `show_passwords_physical` が適用されると公式文書は説明。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | password field への external keyboard 等の入力で、default では全 password characters が hidden。 |

## 要約（Summary）

Android 17 では、targetSdkVersion 37 以上のアプリで physical input device を使って password field に入力する場合、`show_passwords_physical` setting により既定で全 password characters が非表示になる、と公式文書は説明している。

## 顧客影響（Customer Impact）

- 要確認

## 影響対象（Who Is Affected）

- 対象アプリ: targetSdkVersion 37 へ更新し、password field を持つアプリ。
- 対象機能: login、sign-up、password confirmation、custom password field、password visibility toggle。
- 対象条件: external keyboard など physical input device で password を入力する場合。touchscreen input は `show_passwords_touch` が適用される。

## 対応要否（Required Action）

- 必須対応: password field と custom password UI を棚卸しし、physical keyboard / touchscreen の両方で Android 17 テストを行う。
- 推奨対応: UI test、support 文言、custom transformation が last-character reveal を前提としていないか確認する。
- 不要: password field を持たないアプリでは直接影響は限定的。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 16 | 36 | Android 16 baseline。具体挙動は Android 17 tag 比較待ち。 |
| Android 17 | 36 | 未確認。公式文書上は targetSdkVersion 37 以上向けだが、AOSP gate 未確認。 |
| Android 17 | 37 | physical input device 使用時、default では全 password characters が hidden。 |

## 顧客向け説明（Explanation for Customers）

Android 17 では、targetSdkVersion 37 以上のアプリで外部キーボードなどの physical input device を使って password を入力する場合、最後に入力した文字も含めて password characters が既定で隠されます。大きな画面や外部キーボード環境では覗き見リスクが高いため、従来の入力確認用の一時表示とは別の policy が適用されます。

現時点では local AOSP checkout に Android 17 tag がないため、targetSdkVersion gate、setting default、input device 判定、compat flag の有無は未確認です。最終的な適用分類は Android 17 AOSP tag 公開後に再確認が必要です。

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-17
- 検証対象の原文: targetSdkVersion 37 以上のアプリで physical input device 使用中は `show_passwords_physical` が password field の全 characters に適用され、default では全 characters が hidden。touchscreen では `show_passwords_touch` が適用される。
- AOSP ファイル: 未確認。local `frameworks-base` に `android-17*` tag がない。
- AOSP ソース文脈: 未確認。tag 間 diff が実行できない。
- 差分解釈: 未分類。added behavior / changed condition / changed default の判定は Android 17 tag 待ち。
- Gate conclusion: 未確認。公式文書は targetSdkVersion 37 以上と physical input device / password field 条件を示すが、AOSP gate evidence は未取得。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 追加調査が必要

# 物理入力デバイスでのパスワード非表示 - 1ページ要約

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
- OS アップデート / 全アプリ: 未確認。公式ページは targetSdkVersion 37+ 向け。
- targetSdkVersion 37 以上: 公式文書上は該当。AOSP 適用ゲートは未確認。
- その他の必須条件: パスワードフィールド、物理入力デバイス、touchscreen input の setting 分岐。
- Compat Change ID: 未確認
- Compat のデフォルト状態: 未確認

## 早見マトリクス

| シナリオ | 影響 |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 未確認。公式文書上は targetSdkVersion 37+ 向けだが、AOSP 適用ゲートは未確認。 |
| Android 17 / targetSdkVersion 37 | 物理入力デバイス使用時に `show_passwords_physical` が適用されると公式文書は説明。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | パスワードフィールドへの external キーボード等の入力で、デフォルトでは全パスワード characters が hidden。 |

## 要約

Android 17 では、targetSdkVersion 37 以上のアプリで物理入力デバイスを使ってパスワードフィールドに入力する場合、`show_passwords_physical` setting により既定で全パスワード characters が非表示になる、と公式文書は説明している。

## 顧客影響

- 要確認

## 影響対象

- 対象アプリ: targetSdkVersion 37 へ更新し、パスワードフィールドを持つアプリ。
- 対象機能: login、sign-up、パスワード confirmation、custom パスワードフィールド、パスワード visibility toggle。
- 対象条件: external キーボードなど物理入力デバイスでパスワードを入力する場合。touchscreen input では `show_passwords_touch` が適用される。

## 対応要否

- 必須対応: パスワードフィールドと custom パスワード UI を棚卸しし、物理キーボード / touchscreen の両方で Android 17 テストを行う。
- 推奨対応: UI テスト、support 文言、custom transformation が last-character reveal を前提としていないか確認する。
- 不要: パスワードフィールドを持たないアプリでは直接影響は限定的。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 36 | Android 16 基準挙動。具体挙動は Android 17 タグ比較待ち。 |
| Android 17 | 36 | 未確認。公式文書上は targetSdkVersion 37+ 向けだが、AOSP 適用ゲートは未確認。 |
| Android 17 | 37 | 物理入力デバイス使用時、デフォルトでは全パスワード characters が hidden。 |

## 顧客向け説明

Android 17 では、targetSdkVersion 37 以上のアプリで外部キーボードなどの物理入力デバイスを使ってパスワードを入力する場合、最後に入力した文字も含めてパスワード characters が既定で隠されます。大きな画面や外部キーボード環境では覗き見リスクが高いため、従来の入力確認用の一時表示とは別のポリシーが適用されます。

現時点ではローカル AOSP checkout に Android 17 タグがないため、targetSdkVersion 適用ゲート、setting デフォルト、入力デバイス判定、compat flag の有無は未確認です。最終的な適用分類は Android 17 AOSP タグ公開後に再確認が必要です。

## 根拠

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-17
- 検証対象の原文: targetSdkVersion 37+ のアプリで物理入力デバイス使用中は `show_passwords_physical` がパスワードフィールドの全 characters に適用され、デフォルトでは全 characters が hidden。touchscreen では `show_passwords_touch` が適用される。
- AOSP ファイル: 未確認。ローカルの `frameworks-base` に `android-17*` タグがない。
- AOSP ソース文脈: 未確認。タグ間差分を実行できない。
- 差分解釈: 未分類。追加された挙動 / 変更された条件 / 変更されたデフォルトの判定は Android 17 タグ待ち。
- 適用ゲートの結論: 未確認。公式文書は targetSdkVersion 37+ と物理入力デバイス / パスワードフィールド条件を示すが、AOSP 適用ゲート根拠は未取得。

## 人間の判断欄

最終優先度（Final Priority）:
- Human decision required

判断（Decision）:
- 追加調査が必要

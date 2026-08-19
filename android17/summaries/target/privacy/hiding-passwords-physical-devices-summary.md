# 物理デバイス入力時のパスワード非表示 - 1ページ要約

## 対象

Android 17 Behavior Change

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

## 適用条件

- 主分類（Primary classification）: TARGET_SDK_37_CONDITIONAL
- OS アップデート / 全アプリ（OS update / all apps）: No。AOSP の Change ID は targetSdkVersion 37 以上で デフォルト有効。
- targetSdkVersion 37 以上: Yes。`@EnabledSince(targetSdkVersion = Build.VERSION_CODES.CINNAMON_BUN)` で確認。
- その他の必須条件（Other required conditions）: password field、physical input device、touchscreen input の setting 分岐。
- Compat Change ID: `417951523` / `SPLIT_SHOW_PASSWORDS_TO_TOUCH_AND_PHYSICAL`
- Compat default state: targetSdkVersion 36 では デフォルト無効、targetSdkVersion 37 以上で デフォルト有効

## 早見マトリクス

| シナリオ | 影響 |
| --- | --- |
| Android 17 / targetSdkVersion 36 | default では旧 `TEXT_SHOW_PASSWORD` 相当の挙動が維持される。 |
| Android 17 / targetSdkVersion 37 | physical input device 使用時に `show_passwords_physical` が適用されると公式文書は説明。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | password field への external keyboard 等の入力で、default では全 password characters が hidden。 |

## 要約

Android 17 では、targetSdkVersion 37 以上のアプリで physical input device を使って password field に入力する場合、`show_passwords_physical` setting により既定で全 password characters が非表示になる、と公式文書は説明している。

## 顧客影響

- 要確認

## 影響対象（Who Is Affected）

- 対象アプリ: targetSdkVersion 37 へ更新し、password field を持つアプリ。
- 対象機能: login、sign-up、password confirmation、custom password field、password visibility toggle。
- 対象条件: external keyboard など physical input device で password を入力する場合。touchscreen input は `show_passwords_touch` が適用される。

## 対応要否

- 必須対応: password field と custom password UI を棚卸しし、physical keyboard / touchscreen の両方で Android 17 テストを行う。
- 推奨対応: UI test、support 文言、custom transformation が last-character reveal を前提としていないか確認する。
- 不要: password field を持たないアプリでは直接影響は限定的。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 36 | 単一の`TEXT_SHOW_PASSWORD` / `TextKeyListener.SHOW_PASSWORD`設定を使い、有効時は最後に入力した1文字を一時表示する従来path。 |
| Android 17 | 36 | `SPLIT_SHOW_PASSWORDS_TO_TOUCH_AND_PHYSICAL` は デフォルト無効。旧 path が維持される。 |
| Android 17 | 37 | physical input device 使用時、default では全 password characters が hidden。 |

## 顧客向け説明

Android 17 では、targetSdkVersion 37 以上のアプリで外部キーボードなどの physical input device を使って password を入力する場合、最後に入力した文字も含めて password characters が既定で隠されます。大きな画面や外部キーボード環境では覗き見リスクが高いため、従来の入力確認用の一時表示とは別の policy が適用されます。

Android 17 AOSP tag `android-17.0.0_r1` では、`SPLIT_SHOW_PASSWORDS_TO_TOUCH_AND_PHYSICAL = 417951523` が `@EnabledSince(CINNAMON_BUN)` として定義されています。`PasswordTransformationMethod` は `PhysicalInputSpan` で physical input を判定し、physical input では default `HIDE` の `show_password_physical`、touch input では default `SHOW` の `show_password_touch` を参照します。

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-17
- 検証対象の原文: targetSdkVersion 37 以上のアプリで physical input device 使用中は `show_passwords_physical` が password field の全 characters に適用され、default では全 characters が hidden。touchscreen では `show_passwords_touch` が適用される。
- AOSP ファイル: `core/java/android/text/ShowSecretsSetting.java`, `core/java/android/text/method/PasswordTransformationMethod.java`, `core/java/android/text/method/BaseKeyListener.java`, `core/java/android/provider/Settings.java`, `packages/SettingsProvider/src/com/android/providers/settings/SettingsProvider.java`
- AOSP ソース文脈: Change ID、`@EnabledSince(CINNAMON_BUN)`、physical input span、touch / physical setting default を確認。
- 差分解釈: added behavior / changed condition / changed default。split setting 追加、targetSdkVersion 37 gate、physical input default hide。
- ゲート結論: Android 17 上で targetSdkVersion 37 以上、かつ password field への入力時に適用。physical input device では default で全文字非表示。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 人間による判断が必要

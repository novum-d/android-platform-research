# 物理デバイス入力時のパスワード非表示

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

### Behavior Change 文書（Behavior Change Source）

文書:
https://developer.android.com/about/versions/17/behavior-changes-17

セクション:
Hiding passwords from physical devices

ページ種別:
- Android 17 以上をターゲットにするアプリ

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- TARGET_SDK_37_CONDITIONAL

公式文書からの初期適用条件判断:
- 公式文書は、targetSdkVersion 37 以上のアプリで、ユーザーが physical input device を使っている場合に `show_passwords_physical` setting が password field の全文字へ適用されると説明している。
- 追加条件として、password field、physical input device、touchscreen input の場合の `show_passwords_touch` 分岐がある。
- AOSP では `SPLIT_SHOW_PASSWORDS_TO_TOUCH_AND_PHYSICAL = 417951523` が `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.CINNAMON_BUN)` として定義され、targetSdkVersion 37 以上で split setting が有効になる。

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | No | `SPLIT_SHOW_PASSWORDS_TO_TOUCH_AND_PHYSICAL` は `@EnabledSince(CINNAMON_BUN)` の compat change。 |
| targetSdkVersion 37 以上が必要か | Yes | AOSP の Change ID が targetSdkVersion 37 以上で default enabled。 |
| 追加の実行時条件があるか | Yes | password field 入力、physical input device / touchscreen input の判定、split settings が関係する。 |
| Compat Change ID が関係するか | Yes | `SPLIT_SHOW_PASSWORDS_TO_TOUCH_AND_PHYSICAL = 417951523`。 |

### 調査日（Investigation Date）

2026-06-18

### 信頼度（Confidence）

- High

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] targetSdkVersion に関係なく Android 17 の全アプリへ適用
- [ ] Android 17 以上かつ targetSdkVersion 37 以上で適用
- [x] targetSdkVersion 37 以上かつ追加の実行時条件を満たす場合に適用
- [ ] Mainline / Google Play system update に依存
- [ ] API 追加のみであり、挙動変更ではない
- [ ] 未確認 / 追加 evidence が必要

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 以上。
- targetSdkVersion: 37 以上。AOSP の `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.CINNAMON_BUN)` で確認。
- Device/form factor: physical input device、例として external keyboard。large display を伴う device で shoulder surfing risk が高いと説明されている。
- Permission/API/component condition: password field、password visibility setting、input method / input device 判定。
- App state/process condition: password field への文字入力時。

Compat framework:
- Change ID: `417951523`
- 変更名: `SPLIT_SHOW_PASSWORDS_TO_TOUCH_AND_PHYSICAL`
- 既定状態: targetSdkVersion 37 以上で default enabled。targetSdkVersion 36 では default disabled。
- テスト時に切り替え可能か: compat change として切り替え可能。

分類信頼度（Classification confidence）:
- High

分類根拠（Classification evidence）:
- 公式ドキュメントページ: `behavior-changes-17`
- 検証対象の適用条件文: targetSdkVersion 37 以上、physical input device 使用中、password field。
- AOSP targetSdk gate: `core/java/android/text/ShowSecretsSetting.java` の `SPLIT_SHOW_PASSWORDS_TO_TOUCH_AND_PHYSICAL` が `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.CINNAMON_BUN)`。
- Compat framework entry: `SPLIT_SHOW_PASSWORDS_TO_TOUCH_AND_PHYSICAL = 417951523`。

---

# エグゼクティブサマリー（Executive Summary）

Android 17 では、targetSdkVersion 37 以上のアプリでユーザーが external keyboard などの physical input device を使って password field に入力する場合、新しい `show_passwords_physical` setting が適用され、既定では password characters がすべて非表示になる、と公式文書は説明している。

従来の「最後に入力した password character を一時表示する」挙動は、物理キーボードと大きな画面では必要性が低く、覗き見リスクが高いという理由で見直される。touchscreen 入力では別の `show_passwords_touch` setting が適用される。

AOSP では `ShowSecretsSetting` が追加され、`show_password_touch` は既定で表示、`show_password_physical` は既定で非表示として読み取られる。`PasswordTransformationMethod` は `PhysicalInputSpan` で physical keyboard 入力を判定し、`SPLIT_SHOW_PASSWORDS_TO_TOUCH_AND_PHYSICAL` が有効な場合に touch / physical の setting を分けて参照する。

---

# 公式ドキュメント確認

## 原文（Statement）

ページタイトル:
- Behavior changes: Apps targeting Android 17 or higher

ページ URL:
- https://developer.android.com/about/versions/17/behavior-changes-17

ページ種別:
- Android 17 をターゲットにするアプリ

セクションタイトル:
- Hiding passwords from physical devices

検証対象の原文:

> applies the new show_passwords_physical setting

公式文書は、Android 17 / API level 37 以上をターゲットにするアプリでユーザーが physical input device を使っている場合、Android が password field の全 characters に `show_passwords_physical` を適用すると説明している。また、既定ではすべての password characters を非表示にし、touchscreen input では `show_passwords_touch` を使うことも説明している。

## 解釈（Interpretation）

この変更は、password field の文字表示ポリシーを input device ごとに分ける privacy / security behavior change である。physical input device の場合、最後の1文字を表示する利便性より、外部キーボードや大きな画面で入力文字が見られるリスクを重視し、既定で全 password characters を隠す。

アプリ側が標準の password field / platform text input behavior に依存している場合、targetSdkVersion 37 更新後に physical keyboard 入力時の visual feedback が変わる可能性がある。独自 password field や custom transformation を持つアプリは、platform setting と整合しているか確認が必要である。

---

# 変更内容（What Changed）

公式文書上の変更点:
- targetSdkVersion 37 以上のアプリで、ユーザーが physical input device を使う場合、password field の全 characters に `show_passwords_physical` setting が適用される。
- `show_passwords_physical` の default は password characters をすべて隠す。
- これまでの最後に入力した password character を表示する挙動は、external keyboard / larger display では必要性が低く、覗き見リスクが高いと説明されている。
- touchscreen を使う場合は `show_passwords_touch` setting が適用される。

AOSP で確認した点:
- `core/java/android/text/ShowSecretsSetting.java` が追加され、touch / physical input ごとの show password setting を扱う。
- `SPLIT_SHOW_PASSWORDS_TO_TOUCH_AND_PHYSICAL = 417951523` は `@ChangeId` かつ `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.CINNAMON_BUN)`。
- `ShowSecretsSetting.shouldShowTouchInput()` は `Settings.Secure.TEXT_SHOW_PASSWORD_TOUCH` を既定 `SHOW` で読む。
- `ShowSecretsSetting.shouldShowPhysicalInput()` は `Settings.Secure.TEXT_SHOW_PASSWORD_PHYSICAL` を既定 `HIDE` で読む。
- `PasswordTransformationMethod.onTextChanged()` は compat change が有効な場合、`BaseKeyListener.PhysicalInputSpan` で physical input を判定し、physical / touch の setting を分岐する。
- `Settings.Secure.TEXT_SHOW_PASSWORD_TOUCH` と `TEXT_SHOW_PASSWORD_PHYSICAL` が追加され、SettingsProvider に backup / validator / migration path が追加された。

## 適用条件（Applicability）

公式文書と AOSP evidence から、Android 17 以上、targetSdkVersion 37 以上、password field への入力時に適用される条件付き変更と分類する。physical input device では `show_password_physical`、touchscreen 入力では `show_password_touch` が参照される。

### OS アップデート時の挙動（OS Update Behavior）

- Android 17 にアップデートしただけで適用されるか: No。targetSdkVersion 36 では compat change が default enabled ではない。
- targetSdkVersion に依存しない根拠: なし。AOSP は `@EnabledSince(CINNAMON_BUN)` を使う。
- Android 16 以前での挙動: 従来の `TEXT_SHOW_PASSWORD` / `TextKeyListener.SHOW_PASSWORD` による単一 setting を参照する。

### targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- targetSdkVersion 37 以上で適用されるか: Yes。`SPLIT_SHOW_PASSWORDS_TO_TOUCH_AND_PHYSICAL` が `@EnabledSince(CINNAMON_BUN)` で default enabled。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: Android 17 platform の `frameworks-base` 実装に依存する。Android 16 platform には本調査対象の split setting 実装はない。
- opt-out / temporary override の有無: compat change としてテスト時に切り替え可能。ユーザー設定として `show_password_touch` / `show_password_physical` が分離される。

### その他の条件（Other Conditions）

- device/form factor: physical input device、external keyboard。large display を伴う可能性。
- permission: 公式抜粋では条件なし。
- API usage: password field / text input / transformation method / input device source。
- manifest attribute: なし。
- component boundary: app password UI、platform text input、system setting、input device classification にまたがる。

---

# AOSP 調査（AOSP Investigation）

## checkout 状態（Checkout Status）

Commands checked before evidence use:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list 'android-17*'
```

Result:
- `frameworks-base` working tree: clean at the time of investigation.
- From tag: `android-16.0.0_r4` exists.
- To tag: `android-17.0.0_r1` exists.

根拠上の制約（Evidence limitation）:
- source evidence は `android-16.0.0_r4` と `android-17.0.0_r1` の明示的な tag 比較、および `android-17.0.0_r1` 上の symbol 確認に限定した。
- `frameworks-base` working tree は clean のため、local working tree changes を platform evidence として誤採用するリスクは確認されていない。

## 関連ファイル（Related Files）

- `core/java/android/text/ShowSecretsSetting.java`
- `core/java/android/text/method/PasswordTransformationMethod.java`
- `core/java/android/text/method/BaseKeyListener.java`
- `core/java/android/text/method/TextKeyListener.java`
- `core/java/android/provider/Settings.java`
- `packages/SettingsProvider/src/com/android/providers/settings/SettingsProvider.java`
- `packages/SettingsProvider/src/android/provider/settings/backup/SecureSettings.java`
- `packages/SettingsProvider/src/android/provider/settings/validators/SecureSettingsValidators.java`

## 確認したソース文脈（Source Context Reviewed）

| File / symbol | Android 16 baseline | Android 17 behavior | 関連性 |
| --- | --- | --- | --- |
| `ShowSecretsSetting.SPLIT_SHOW_PASSWORDS_TO_TOUCH_AND_PHYSICAL` | split setting API / compat change は存在しない。 | `@ChangeId` `417951523` が追加され、`@EnabledSince(targetSdkVersion = Build.VERSION_CODES.CINNAMON_BUN)` で targetSdkVersion 37 以上 default enabled。 | 公式文書の targetSdkVersion 37 条件を直接裏付ける gate。 |
| `ShowSecretsSetting.shouldShowTouchInput()` | 単一の show password setting を利用。 | `TEXT_SHOW_PASSWORD_TOUCH` を既定 `SHOW` で読む。 | touchscreen input の表示 policy を分離する実装。 |
| `ShowSecretsSetting.shouldShowPhysicalInput()` | 単一の show password setting を利用。 | `TEXT_SHOW_PASSWORD_PHYSICAL` を既定 `HIDE` で読む。 | physical input device では既定で全文字を隠すという公式文書の説明と一致する。 |
| `PasswordTransformationMethod.onTextChanged()` | `TextKeyListener.SHOW_PASSWORD` が有効なら最後の1文字を一時表示する。 | compat change が有効な場合、`PhysicalInputSpan` により physical input を判定し、touch / physical の setting を分岐する。 | password field 入力時に behavior change が実際に適用される entry point。 |
| `BaseKeyListener.PhysicalInputSpan` | なし。 | physical keyboard 由来の入力範囲に span を付ける。 | physical input device 判定の source context。 |
| `Settings.Secure.TEXT_SHOW_PASSWORD_TOUCH` / `TEXT_SHOW_PASSWORD_PHYSICAL` | なし。 | `show_password_touch` / `show_password_physical` が追加される。 | setting definition と default / migration path の根拠。 |

必要な context:
- Entry point / caller: password field への text input -> `BaseKeyListener` -> `PasswordTransformationMethod.onTextChanged()`。
- 関連 class / service の責務: `PasswordTransformationMethod` は password field の表示文字を mask / reveal する。`ShowSecretsSetting` は touch / physical input ごとの show password policy を読む。
- app API / system event から変更箇所までの runtime path: physical keyboard event または touch input -> text mutation -> `PhysicalInputSpan` 付与 -> `PasswordTransformationMethod` が split setting を参照 -> last-character reveal の有無を決定。
- 関係しない code path を除外した理由: Settings backup / migration は setting 保持の補助 path であり、password field 表示変更の primary runtime path ではないため補助根拠として扱う。

## 差分解釈（Diff Interpretation）

| 観測した diff | 解釈 | Behavior Change との関連 | 信頼度 |
| --- | --- | --- | --- |
| `ShowSecretsSetting.java` が追加され、Change ID `417951523` が `@EnabledSince(CINNAMON_BUN)` で定義される。 | added behavior / changed condition | targetSdkVersion 37 以上で split setting を使う gate。 | High |
| `PasswordTransformationMethod` が `CompatChanges.isChangeEnabled(SPLIT_SHOW_PASSWORDS_TO_TOUCH_AND_PHYSICAL)` を確認し、touch / physical setting を分岐する。 | changed condition / gate | password field の実際の表示挙動が targetSdkVersion 37 と input source に依存する根拠。 | High |
| `shouldShowPhysicalInput()` の default が `HIDE`、`shouldShowTouchInput()` の default が `SHOW`。 | changed default | physical input device では既定で password characters を隠すという公式説明を裏付ける。 | High |
| `Settings.Secure` に `show_password_touch` / `show_password_physical` が追加される。 | added setting surface | 公式文書の new setting 名と一致する。 | High |

必要な解釈:
- Added behavior: touch / physical input ごとの show password setting と Change ID。
- Removed behavior: public API の削除は確認していない。
- Changed condition / gate: targetSdkVersion 37 以上かつ compat change enabled、さらに input source によって表示 policy が分岐。
- Changed default: physical input は default hide、touch input は default show。
- No behavior change found: 該当しない。

## 事実（Evidence）

事実:
- 公式 Behavior Change 文書は、targetSdkVersion 37 以上のアプリで physical input device 使用中に `show_passwords_physical` setting が password field の全 characters に適用されると述べている。
- 公式文書は、`show_passwords_physical` の default がすべての password characters を隠すことだと述べている。
- 公式文書は、last-typed password character の表示は入力ミス確認を助けるが、external keyboard と large display では必要性が低く、覗き見リスクが高いと説明している。
- 公式文書は、touchscreen 使用時には `show_passwords_touch` setting が適用されると述べている。
- local `frameworks-base` には `android-16.0.0_r4` tag がある。
- local `frameworks-base` には `android-17.0.0_r1` tag がある。
- 調査時点で `frameworks-base` working tree は clean。
- AOSP では `SPLIT_SHOW_PASSWORDS_TO_TOUCH_AND_PHYSICAL = 417951523` が `@EnabledSince(CINNAMON_BUN)` として定義される。
- AOSP では physical input setting の default は `HIDE`、touch input setting の default は `SHOW`。

観察:
- 公式ページ種別は targetSdkVersion 37 以上向けである。
- この項目は targetSdkVersion 37 条件に加えて、physical input device / touchscreen の runtime condition を含む。
- standard password field を使うアプリでは platform behavior change として現れる可能性がある。
- custom password UI は platform setting と一致しない表示をしてしまう可能性がある。
- AOSP gate は targetSdkVersion 37 以上で default enabled であり、公式文書と一致する。
- input source 判定は `PhysicalInputSpan` によって password transformation path に伝達される。

仮説:
- Android 17 / targetSdkVersion 37 以上では、external keyboard など physical input device から password field へ入力した場合、最後の1文字表示が抑制される可能性が高い。
- touchscreen 入力では `show_passwords_touch` により、default では最後の1文字表示に近い policy が維持される。
- targetSdkVersion 36 のアプリでは compat change が default disabled のため、旧 `show_passwords` 相当の挙動が維持される。

結論:
- 公式文書と AOSP evidence が一致するため、primary classification は `TARGET_SDK_37_CONDITIONAL` とする。
- Android 17 / targetSdkVersion 37 以上で、password field に physical input device から入力する場合、default では最後の1文字も含めて非表示になる。

## 適用ゲート根拠（Applicability Gate Evidence）

- targetSdkVersion gate: `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.CINNAMON_BUN)`。targetSdkVersion 37 以上で default enabled。
- CompatChanges.isChangeEnabled / ChangeId: `CompatChanges.isChangeEnabled(ShowSecretsSetting.SPLIT_SHOW_PASSWORDS_TO_TOUCH_AND_PHYSICAL)`、Change ID `417951523`。
- @EnabledAfter / @EnabledSince / default state: `@EnabledSince(CINNAMON_BUN)`。targetSdkVersion 36 では default disabled、37 以上では default enabled。
- Build.VERSION / SDK_INT gate: Android 17 platform implementation として扱う。明示的な SDK_INT runtime gate は主根拠ではない。
- DeviceConfig / resources config: `Flags.splitShowPasswordsToTouchAndPhysical()` の flag guard があるが、Behavior Change の適用条件分類は compat change の default state に基づく。
- Permission/AppOps gate: 公式文書上は permission 条件なし。
- Manifest/property gate: なし。
- No gate found: 該当しない。
- Gate conclusion: Android 17 上で targetSdkVersion 37 以上、かつ password field 入力時に split setting が適用される。physical input device では default hide。
- Reasoning from source context: `BaseKeyListener` が physical input span を付け、`PasswordTransformationMethod` が compat change と setting を確認する。

検索済み:
- `frameworks-base` checkout status。
- `android-16.0.0_r4` tag の存在。
- `android-17.0.0_r1` tag の存在。
- Change ID、targetSdkVersion gate、setting definition、physical input 判定、default values。

未検索:
- OEM / product config で `Flags.splitShowPasswordsToTouchAndPhysical()` がどう設定されるか。
- custom password field が platform setting を読むかどうか。

---

# 影響分析（Impact Analysis）

## 影響を受けるアプリ（Affected Apps）

影響を受ける可能性があるアプリ:
- targetSdkVersion 37 以上への更新を予定しているアプリ。
- password field を持つアプリ。
- external keyboard、Chromebook、tablet keyboard、desktop mode、large display で password input が行われるアプリ。
- custom password field、custom transformation、独自の show / hide password UI を持つアプリ。
- 入力直後の最後の1文字表示を前提とした UI test / screenshot test / accessibility test を持つアプリ。

## 影響を受けないアプリ（Non-Affected Apps）

影響が限定的と考えられるケース:
- password field を持たないアプリ。
- physical input device での password input を想定しないアプリ。ただし foldable / tablet / Chromebook / desktop mode では想定外に該当する可能性がある。
- touchscreen 入力のみの場合。`show_passwords_touch` の default は `SHOW`。
- targetSdkVersion 37 へ上げないアプリ。AOSP gate 上は targetSdkVersion 36 では default disabled。

---

# 顧客影響（Customer Impact）

## 影響度

- 人間による判断が必要

※ 最終 severity / priority は人間が判断する。このレポートでは確定しない。

## ビジネス影響（Business Impact）

- ユーザー影響: physical keyboard 入力時に最後の password character が表示されなくなり、入力確認の UX が変わる可能性がある。一方で、large display / external keyboard 環境での覗き見リスクは低下する。
- 運用影響: password 入力の UI test、manual QA、サポート手順で「最後の1文字が表示される」前提がある場合、期待結果の更新が必要。
- 開発影響: custom password field は platform setting と整合しているか確認し、physical keyboard / touchscreen の両方でテストする必要がある。

---

# サービス影響例（Service Impact Examples）

このセクションは、公式文書と AOSP evidence から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: 外部キーボード利用が多いログイン画面

- 対象サービス例: tablet / Chromebook 向け業務アプリ、教育アプリ、金融・認証画面。
- 影響を受ける実装パターン: password field で最後に入力した文字の一時表示をユーザー確認として期待している UI。
- 発生条件: Android 17 / targetSdkVersion 37 で physical input device 使用中に `show_passwords_physical` が適用される場合。
- ユーザーに見える症状: 外部キーボード入力時に password character が一切表示されず、入力ミス確認の体感が変わる可能性。
- 開発・運用への影響: support 文言、ログイン失敗率、keyboard 利用 QA の確認が必要になる可能性。
- 推奨対応候補: password visibility toggle、error feedback、physical keyboard / touchscreen 別テストを整備する。
- 根拠: 公式 statement、`ShowSecretsSetting` の Change ID、`PasswordTransformationMethod` の physical input 判定、physical setting default。
- 信頼度: Medium
- 注意: 実サービスで発生確認した事実ではない。ユーザー影響は入力環境と password UI に依存する。

## 例2（Example 2）: Custom password field を持つアプリ

- 対象サービス例: password manager、認証 SDK、独自 design system を持つアプリ。
- 影響を受ける実装パターン: platform password field ではなく custom masking / reveal behavior を実装している UI。
- 発生条件: platform setting と custom field の表示方針がずれる場合。
- ユーザーに見える症状: 標準 password field と custom field で表示挙動が違い、ユーザーが混乱する可能性。
- 開発・運用への影響: design system component の見直し、security review、UI test 更新が必要になる可能性。
- 推奨対応候補: platform setting に合わせる、または custom reveal の security rationale を明確にする。
- 根拠: 公式 statement、AOSP の split show-password settings、platform password transformation path。
- 信頼度: Medium
- 注意: custom field が platform setting を読むかどうかはアプリ実装ごとの確認が必要。

---

# 対応候補（Required Actions）

## 必須対応（Must）

- password field を持つ画面を棚卸しする。
- targetSdkVersion 37 更新前に Android 17 上で physical keyboard と touchscreen の password input をテストする。
- custom password field / custom transformation / 独自 show password UI がある場合、`show_passwords_physical` / `show_passwords_touch` の方針と衝突しないか確認する。

## 推奨対応（Recommended）

- tablet、Chromebook、external keyboard、large display での password input QA を追加する。
- UI test / screenshot test が last-typed character reveal を前提としていないか確認する。
- ユーザー向けヘルプやサポート文言が「最後に入力した文字が表示される」ことを前提としていないか確認する。
- アプリ独自の password visibility toggle がある場合、system default とユーザー選択の関係を整理する。

## 任意対応（Optional）

- accessibility service や password manager との組み合わせで visual feedback が期待どおりか確認する。

---

# 検証方法（Verification Method）

## 検証マトリクス（Matrix）

| 端末 OS | targetSdkVersion | Compat flag | 期待される挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | default | Android 16 baseline。last-typed password character reveal の挙動は Android 17 tag 比較待ち。 |
| Android 17 | 36 | default | `SPLIT_SHOW_PASSWORDS_TO_TOUCH_AND_PHYSICAL` は default disabled。旧 `TEXT_SHOW_PASSWORD` 相当の挙動が維持される。 |
| Android 17 | 37 | default | 公式文書上は physical input device 使用時に `show_passwords_physical` が適用され、default では全 password characters が hidden。 |
| Android 17 | 36 | force-enabled | `SPLIT_SHOW_PASSWORDS_TO_TOUCH_AND_PHYSICAL` を有効化すると split setting path を検証できる。 |
| Android 17 | 37 | force-disabled | `SPLIT_SHOW_PASSWORDS_TO_TOUCH_AND_PHYSICAL` を無効化すると旧 path との切り分けができる。 |

## 手順（Steps）

- targetSdk変更: test app を targetSdkVersion 36 と 37 で build し、Android 17 上で同じ password field を比較する。
- compat framework command: `adb am compat enable|disable SPLIT_SHOW_PASSWORDS_TO_TOUCH_AND_PHYSICAL <package>`、または Change ID `417951523` を使って切り替える。
- テスト方法: standard password `TextView` / `EditText`、custom password field、physical keyboard、touchscreen を組み合わせる。
- 再現手順: physical keyboard と touchscreen で password を入力し、入力直後の last character reveal、全 character masking、system setting の反映を比較する。
- 期待結果: targetSdkVersion 37 で physical input device を使う場合、default では最後の1文字も含めて password characters が非表示になる。touchscreen の結果は `show_password_touch` の policy に従う。targetSdkVersion 36 では default で旧 path が維持される。

---

# 結論（Conclusion）

公式文書は、Android 17 で targetSdkVersion 37 以上のアプリに対し、physical input device 使用時の password display policy として `show_passwords_physical` を適用し、default では全 password characters を隠すと説明している。主な影響は、password field、external keyboard、large display、custom password UI の組み合わせで発生する。

AOSP では `SPLIT_SHOW_PASSWORDS_TO_TOUCH_AND_PHYSICAL = 417951523` が `@EnabledSince(CINNAMON_BUN)` として定義され、`PasswordTransformationMethod` が `PhysicalInputSpan` と split settings を参照することを確認した。primary classification は `TARGET_SDK_37_CONDITIONAL`、confidence は High とする。

Human decision placeholder:
- 最終優先度: 人間による判断が必要
- 最終 severity: 人間による判断が必要
- リリース可否: 人間による判断が必要
- 顧客連絡の優先度: 人間による判断が必要
- 次に必要な人間の判断: password field / custom password UI の確認を targetSdkVersion 37 対応のどの優先度で顧客へ案内するかを判断する。

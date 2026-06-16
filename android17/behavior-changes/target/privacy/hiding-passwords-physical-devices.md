# Hiding passwords from physical devices

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP tag

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

### Behavior Change 文書（Behavior Change Source）

Document:
https://developer.android.com/about/versions/17/behavior-changes-17

Section:
Hiding passwords from physical devices

Page type:
- Apps targeting Android 17 or higher

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- 公式文書は、targetSdkVersion 37 以上のアプリで、ユーザーが physical input device を使っている場合に `show_passwords_physical` setting が password field の全文字へ適用されると説明している。
- 追加条件として、password field、physical input device、touchscreen input の場合の `show_passwords_touch` 分岐がある。
- ただし、local `frameworks-base` に Android 17 AOSP tag がないため、AOSP gate、setting implementation、input device 判定、Compat Change ID、default state は未検証である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | Unknown | 公式文書は targetSdkVersion 37+ を条件としているが、AOSP gate 未確認。 |
| targetSdkVersion 37 以上が必要か | Likely, but unverified | 原文は apps targeting Android 17 / API level 37 or higher と述べている。 |
| 追加の実行時条件があるか | Yes | physical input device 使用中、password field、または touchscreen input による setting 分岐。 |
| Compat Change ID が関係するか | Unknown | Android 17 tag と compat framework evidence が未確認。 |

### 調査日（Investigation Date）

2026-06-10

### 信頼度（Confidence）

- Low

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] OS update / all apps on Android 17 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 37 on Android 17+
- [ ] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [x] Unknown / needs more evidence

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 以上が前提と考えられるが、AOSP tag 未取得。
- targetSdkVersion: 公式文書上は 37 以上。
- Device/form factor: physical input device、例として external keyboard。large display を伴う device で shoulder surfing risk が高いと説明されている。
- Permission/API/component condition: password field、password visibility setting、input method / input device 判定。
- App state/process condition: password field への文字入力時。

Compat framework:
- Change ID: Unknown
- Change name: Unknown
- Default state: Unknown
- Toggleable for testing: Unknown

分類信頼度（Classification confidence）:
- Low

分類根拠（Classification evidence）:
- Official documentation page: `behavior-changes-17`
- Original applicability statement: targetSdkVersion 37 以上、physical input device 使用中、password field。
- AOSP targetSdk gate: 未確認。local `frameworks-base` に `android-17*` tag がない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# エグゼクティブサマリー（Executive Summary）

Android 17 では、targetSdkVersion 37 以上のアプリでユーザーが external keyboard などの physical input device を使って password field に入力する場合、新しい `show_passwords_physical` setting が適用され、既定では password characters がすべて非表示になる、と公式文書は説明している。

従来の「最後に入力した password character を一時表示する」挙動は、物理キーボードと大きな画面では必要性が低く、覗き見リスクが高いという理由で見直される。touchscreen 入力では別の `show_passwords_touch` setting が適用される。

ただし、現時点の local `frameworks-base` には Android 17 AOSP tag がないため、実装差分、targetSdkVersion gate、input device 判定、setting default、Compat Change ID は未確認である。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statement）

Page title:
- Behavior changes: Apps targeting Android 17 or higher

Page URL:
- https://developer.android.com/about/versions/17/behavior-changes-17

Page type:
- apps targeting Android 17

Section title:
- Hiding passwords from physical devices

Original statement being verified:

> applies the new show_passwords_physical setting

The supplied official text states that if an app targets Android 17 / API level 37 or higher and the user is using a physical input device, Android applies `show_passwords_physical` to all characters in the password field. It also states that the default hides all password characters, and that touchscreen input uses `show_passwords_touch`.

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

AOSP で未確認の点:
- Android 16 baseline の password character reveal behavior。
- Android 17 で追加された `show_passwords_physical` / `show_passwords_touch` setting の定義。
- physical input device と touchscreen input の判定箇所。
- password field への適用 path。
- targetSdkVersion 37 gate の実装箇所。
- Compat Change ID と default state。

## 適用条件（Applicability）

公式文書の一次判断では、Android 17 以上、targetSdkVersion 37 以上、password field、physical input device 使用中に適用される。touchscreen 入力では `show_passwords_touch` が適用される。AOSP tag が未取得のため、確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

### OS アップデート時の挙動（OS Update Behavior）

- Android 17 にアップデートしただけで適用されるか: Unknown
- targetSdkVersion に依存しない根拠: なし。公式文書は targetSdkVersion 37 以上を明示している。
- Android 16 以前での挙動: AOSP tag 比較未実施。Android 16 baseline source は Android 17 tag との比較ができないため、この調査では platform evidence として採用していない。

### targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- targetSdkVersion 37 以上で適用されるか: 公式文書上は Yes と読めるが、AOSP gate 未確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: Unknown。公式文書は Android 17 Behavior Changes として説明しているため、Android 17 platform behavior として扱う。
- opt-out / temporary override の有無: Unknown。settings UI / user setting / compat framework の関係は AOSP 未確認。

### その他の条件（Other Conditions）

- device/form factor: physical input device、external keyboard。large display を伴う可能性。
- permission: 公式抜粋では条件なし。
- API usage: password field / text input / transformation method / input device source。
- manifest attribute: Unknown。
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
- To tag: no local `android-17*` tag found.

根拠上の制約（Evidence limitation）:
- Android 17 AOSP tag が local `frameworks-base` に存在しないため、`git -C frameworks-base diff android-16.0.0_r4 <android-17-tag> -- ...` による明示的な tag 比較を実行できない。
- Repository rule に従い、Android 17 working tree や推測による source evidence は採用しない。
- この制約により、AOSP-backed conclusion は High confidence にできない。

## 関連ファイル（Related Files）

未確認。Android 17 AOSP tag 取得後に、少なくとも以下の候補を tag 比較で確認する必要がある。

- `core/java/android/text/method/PasswordTransformationMethod.java`
- `core/java/android/widget/TextView.java`
- `core/java/android/provider/Settings.java`
- `core/java/android/view/InputDevice.java`
- `core/java/android/view/inputmethod/InputMethodManager.java`
- `core/res/res/values/config.xml` または settings default 関連 resource
- compat framework 定義ファイル内の password reveal / physical input device / targetSdkVersion 37 関連 Change ID

## 確認したソース文脈（Source Context Reviewed）

Android 17 AOSP tag がないため、source context は未レビュー。

| File / symbol | Android 16 baseline | Android 17 behavior | Why this code path matters |
| --- | --- | --- | --- |
| Not reviewed | Not reviewed | Not reviewed | Android 17 tag がないため、公式文書の記述を AOSP diff で検証できない。 |

Required context:
- Entry point / caller: 未確認。想定される entry point は password field への key input、TextView / PasswordTransformationMethod の表示更新、Settings の show password policy 読み取りだが、AOSP evidence としては未採用。
- Relevant class or service responsibility: 未確認。
- Runtime path from app API / system event to changed code: 未確認。
- Why unrelated code paths were excluded: Android 17 tag 不在のため、source path の採否判断自体を保留。

## 差分解釈（Diff Interpretation）

| Observed diff | Interpretation | Behavior Change relevance | Confidence |
| --- | --- | --- | --- |
| No Android 17 tag diff available | Source diff type cannot be classified yet | 公式文書の `show_passwords_physical` / `show_passwords_touch` setting と physical input gate を source diff で裏取りできていない | Low |

Required interpretation:
- Added behavior: 未確認。
- Removed behavior: 未確認。
- Changed condition / gate: 未確認。
- Changed default: 未確認。
- No behavior change found: 未確認。tag 不在のため「no behavior change」とは判断しない。

## 事実（Evidence）

Facts:
- 公式 Behavior Change 文書は、targetSdkVersion 37 以上のアプリで physical input device 使用中に `show_passwords_physical` setting が password field の全 characters に適用されると述べている。
- 公式文書は、`show_passwords_physical` の default がすべての password characters を隠すことだと述べている。
- 公式文書は、last-typed password character の表示は入力ミス確認を助けるが、external keyboard と large display では必要性が低く、覗き見リスクが高いと説明している。
- 公式文書は、touchscreen 使用時には `show_passwords_touch` setting が適用されると述べている。
- local `frameworks-base` には `android-16.0.0_r4` tag がある。
- local `frameworks-base` には `android-17*` tag がない。
- 調査時点で `frameworks-base` working tree は clean。

Observations:
- 公式ページ種別は targetSdkVersion 37 以上向けである。
- この項目は targetSdkVersion 37 条件に加えて、physical input device / touchscreen の runtime condition を含む。
- standard password field を使うアプリでは platform behavior change として現れる可能性がある。
- custom password UI は platform setting と一致しない表示をしてしまう可能性がある。
- AOSP tag がないため、実装が本当に targetSdkVersion 37 gate で制御されているかは未確認。
- Compat framework entry の有無も未確認。

Hypotheses:
- Android 17 / targetSdkVersion 37 以上では、external keyboard など physical input device から password field へ入力した場合、最後の1文字表示が抑制される可能性が高い。
- touchscreen 入力では `show_passwords_touch` により従来に近い別 policy が適用される可能性があるが、default と user setting の詳細は未確認。
- targetSdkVersion 36 のアプリでは旧 `show_passwords` 相当の挙動が維持される可能性があるが、AOSP gate 未確認のため断定しない。

結論:
- 現時点で顧客向けに確定できるのは、「公式文書上は Android 17 / targetSdkVersion 37 以上で physical input device 使用時の password character 表示が `show_passwords_physical` に分離され、default では全文字非表示になる」という範囲まで。
- AOSP gate、setting definition、input device 判定、compat framework default state が未確認のため、primary classification は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

## 適用ゲート根拠（Applicability Gate Evidence）

- targetSdkVersion gate: 未確認。Android 17 AOSP tag がないため、`targetSdkVersion` / `ApplicationInfo.targetSdkVersion` 検索は実施していない。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。Android 17 AOSP tag がないため、`CompatChanges.isChangeEnabled` / `@ChangeId` / `@EnabledAfter` / `@EnabledSince` 検索は実施していない。
- @EnabledAfter / @EnabledSince / default state: 未確認。
- Build.VERSION / SDK_INT gate: 未確認。
- DeviceConfig / resources config: 未確認。
- Permission/AppOps gate: 公式文書上は permission 条件なし。
- Manifest/property gate: 未確認。
- No gate found: 未判断。検索不能のため「gate なし」とは扱わない。
- Gate conclusion: Unknown。公式文書上の Android 17 / targetSdkVersion 37 / physical input device / password field 条件はあるが、AOSP evidence が不足している。
- Reasoning from source context: source context 未取得のため不可。

Searched:
- `frameworks-base` checkout status。
- `android-16.0.0_r4` tag の存在。
- `android-17*` tag の存在。

Not searched yet:
- Android 17 implementation files。
- Android 17 compat framework definitions。
- Android 17 settings default / resource files。
- password transformation / TextView input handling implementation。

理由（Reason）:
- Android 17 target tag が local checkout に存在しないため、tag 間 diff による platform evidence が作れない。

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
- touchscreen 入力のみの場合。ただし `show_passwords_touch` の詳細は AOSP 未確認。
- targetSdkVersion 37 へ上げないアプリ。ただし、これは公式文書からの一次判断であり、AOSP gate 未確認。

---

# 顧客影響（Customer Impact）

## 影響度（Impact Level）

- Human decision required

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
- 根拠: 公式 statement と report の missing AOSP evidence。
- Confidence（信頼度）: Low
- 注意: default setting と input device 判定は AOSP tag 待ち。

## 例2（Example 2）: Custom password field を持つアプリ

- 対象サービス例: password manager、認証 SDK、独自 design system を持つアプリ。
- 影響を受ける実装パターン: platform password field ではなく custom masking / reveal behavior を実装している UI。
- 発生条件: platform setting と custom field の表示方針がずれる場合。
- ユーザーに見える症状: 標準 password field と custom field で表示挙動が違い、ユーザーが混乱する可能性。
- 開発・運用への影響: design system component の見直し、security review、UI test 更新が必要になる可能性。
- 推奨対応候補: platform setting に合わせる、または custom reveal の security rationale を明確にする。
- 根拠: 公式 statement と report の interpretation。
- Confidence（信頼度）: Low
- 注意: 実装適用範囲は未確認。

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

- Android 17 AOSP tag 公開後、setting definition、default value、TextView / PasswordTransformationMethod diff、compat Change ID を再調査する。
- accessibility service や password manager との組み合わせで visual feedback が期待どおりか確認する。

---

# 検証方法（Verification Method）

## 検証マトリクス（Matrix）

| Device OS | targetSdkVersion | Compat flag | Expected behavior |
| --- | --- | --- | --- |
| Android 16 | 36 | default | Android 16 baseline。last-typed password character reveal の挙動は Android 17 tag 比較待ち。 |
| Android 17 | 36 | default | Unknown。公式文書上は targetSdkVersion 37 以上向けだが、AOSP gate 未確認。 |
| Android 17 | 37 | default | 公式文書上は physical input device 使用時に `show_passwords_physical` が適用され、default では全 password characters が hidden。 |
| Android 17 | 36 | force-enabled if available | Unknown。Compat Change ID 未確認。 |
| Android 17 | 37 | force-disabled if available | Unknown。Compat Change ID 未確認。 |

## 手順（Steps）

- targetSdk変更: test app を targetSdkVersion 36 と 37 で build し、Android 17 上で同じ password field を比較する。
- compat framework command: Change ID 未確認のため未定。Android 17 tag / compat page 確認後に追加する。
- テスト方法: standard password `TextView` / `EditText`、custom password field、physical keyboard、touchscreen を組み合わせる。
- 再現手順: physical keyboard と touchscreen で password を入力し、入力直後の last character reveal、全 character masking、system setting の反映を比較する。
- 期待結果: targetSdkVersion 37 で physical input device を使う場合、default では最後の1文字も含めて password characters が非表示になる。touchscreen の結果は `show_passwords_touch` の policy に従う。targetSdkVersion 36 の結果は AOSP gate 確認待ち。

---

# 結論（Conclusion）

公式文書は、Android 17 で targetSdkVersion 37 以上のアプリに対し、physical input device 使用時の password display policy として `show_passwords_physical` を適用し、default では全 password characters を隠すと説明している。主な影響は、password field、external keyboard、large display、custom password UI の組み合わせで発生する。

一方で、local `frameworks-base` に Android 17 AOSP tag がないため、実装差分、targetSdkVersion gate、setting definition、input device 判定、Compat Change ID、default state を検証できていない。現時点の primary classification は `UNKNOWN_NEEDS_MORE_EVIDENCE`、confidence は Low とする。

Human decision placeholder:
- Final priority: Human decision required
- Final severity: Human decision required
- Release readiness: Human decision required
- Customer communication priority: Human decision required
- Next required human decision: Android 17 AOSP tag 公開後に再調査するか、公式 documentation ベースの暫定 security / UX guidance として扱うかを判断する。

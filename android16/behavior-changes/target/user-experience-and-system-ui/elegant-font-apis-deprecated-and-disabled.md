# Elegant font APIs deprecated and disabled 調査レポート

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:
- `frameworks-base` checkout は clean。指定 tag `android-15.0.0_r36` / `android-16.0.0_r4` はどちらも存在する。

### Behavior Change 文書（Behavior Change Source）

Document:
- https://developer.android.com/about/versions/16/behavior-changes-16#elegant-text-height

Section:
- Elegant font APIs deprecated and disabled

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `TARGET_SDK_36_CONDITIONAL`

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 16 に OS アップデートしただけで適用されるか | No | 公式文書は apps targeting Android 16 / API level 36 の Behavior Change として掲載。AOSP では `DEPRECATE_UI_FONT_ENFORCE` が targetSdkVersion 36 以上で default enabled |
| targetSdkVersion 36 以上が必要か | Yes | `Paint.DEPRECATE_UI_FONT_ENFORCE` / 349519475 が `@EnabledSince(targetSdkVersion = 36)` |
| 追加の実行時条件があるか | Yes | `elegantTextHeight=false` の指定、`TextView#setElegantTextHeight(false)` / `Paint#setElegantTextHeight(false)` の呼び出し、または対象言語の行高・クリッピングに依存する UI で実質影響が出る |
| Compat Change ID が関係するか | Yes | AOSP: `DEPRECATE_UI_FONT` / 279646685、`DEPRECATE_UI_FONT_ENFORCE` / 349519475。公開 compat framework changes ページでは該当 ID / name は検索で見つからなかった |

### 調査日（Investigation Date）

2026-06-30

### 信頼度（Confidence）

- Medium

理由:
- 公式文書、AOSP の `@ChangeId` / `@EnabledSince`、`Paint#setElegantTextHeight(false)` の no-op 化、`TextView` の attribute 適用経路は一致している。
- 一方で、指定 tag 間の `Paint` core gate には実質的な挙動差分がほぼなく、Android 15 tag 側にも targetSdkVersion 36 enforce 用の compat change が存在する。Android 15 端末上で targetSdkVersion 36 アプリを動かす実運用可能性は SDK / Play / device image 条件にも依存するため、Android 15 / targetSdkVersion 36 の期待挙動は「技術的には同じ gate が存在するが、公式 Behavior Change としての適用対象は Android 16」として扱う。

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] OS update / all apps on Android 16 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 36 on Android 16+
- [x] targetSdkVersion >= 36, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [ ] Unknown / needs more evidence

必要な実行時条件（Required runtime conditions）:
- Android version: 公式 Behavior Change としては Android 16 以上。指定 Android 15 tag にも同じ core gate が存在するため、Android 15 / targetSdkVersion 36 の評価は実機・SDK 条件つきで要確認。
- targetSdkVersion: 36 以上で `elegantTextHeight=false` の override が無効化される。
- Device/form factor: 特定 form factor 条件なし。
- Permission/API/component condition: `android:elegantTextHeight="false"`、`TextView#setElegantTextHeight(false)`、`Paint#setElegantTextHeight(false)`、`TextAppearanceSpan` 等で elegant text height を false にする経路。
- App state/process condition: TextView / Paint によるテキスト描画・測定時。対象言語や固定高さ layout で影響が顕在化しやすい。

Compat framework:
- Change ID: 279646685
- Change name: `DEPRECATE_UI_FONT`
- Default state: `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.VANILLA_ICE_CREAM)`。targetSdkVersion 35 以上で default enabled。
- Toggleable for testing: AOSP compat ChangeId として存在するため compat override 対象になり得る。

Compat framework:
- Change ID: 349519475
- Change name: `DEPRECATE_UI_FONT_ENFORCE`
- Default state: `@EnabledSince(targetSdkVersion = 36)`。targetSdkVersion 36 以上で default enabled。
- Toggleable for testing: AOSP compat ChangeId として存在するため compat override 対象になり得る。ただし Android Developers の公開 compat framework changes ページでは該当 entry は見つからなかった。

分類信頼度（Classification confidence）:
- Medium

分類根拠（Classification evidence）:
- Official documentation page: `behavior-changes-16` の `User experience and system UI` セクション。
- Original applicability statement: apps targeting Android 16 / API level 36 では `elegantTextHeight` attribute が deprecated になり、target すると ignored。
- AOSP targetSdk gate: `Paint.DEPRECATE_UI_FONT_ENFORCE` が `@EnabledSince(targetSdkVersion = 36)`。
- Compat framework entry: AOSP annotation あり。公開 compat page は `279646685`、`349519475`、`DEPRECATE_UI_FONT`、`DEPRECATE_UI_FONT_ENFORCE`、`elegant` で検索したが該当 entry は見つからなかった。

---

# エグゼクティブサマリー（Executive Summary）

Android 16 では、targetSdkVersion 36 以上のアプリで `elegantTextHeight=false` による compact font / compact metrics への opt-out が無効化される。
Android 16 へ OS アップデートしただけで、targetSdkVersion 35 以下のアプリにこの override 無効化が適用される根拠は確認していない。
影響があるのは、`elegantTextHeight=false` や `setElegantTextHeight(false)` に依存し、Arabic、Lao、Myanmar、Tamil、Gujarati、Kannada、Malayalam、Odia、Telugu、Thai などの行高・クリッピング・固定高さ表示を厳密に調整しているアプリである。
対応候補は、compact metrics 前提の固定高さ layout を見直し、対象言語で行高、baseline、複数行、固定高さ container 内表示を再検証することである。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statement）

検証対象 statement:

```text
Apps targeting Android 15 (API level 35) have the elegantTextHeight TextView attribute set to true by default
```

```text
You could override this by setting the elegantTextHeight attribute to false.
```

```text
Android 16 deprecates the elegantTextHeight attribute, and the attribute will be ignored once your app targets Android 16.
```

```text
The "UI fonts" controlled by these APIs are being discontinued
```

```text
you should adapt any layouts to ensure consistent and future proof text rendering in Arabic, Lao, Myanmar, Tamil, Gujarati, Kannada, Malayalam, Odia, Telugu or Thai.
```

図の caption では、compact 側の挙動は Android 14 以下を target するアプリ、または Android 15 target で default を `false` override したアプリの挙動として説明されている。elegant 側の挙動は Android 16 target、または Android 15 target で `false` override していないアプリの挙動として説明されている。

## 解釈（Interpretation）

公式文書は、Android 15 / targetSdkVersion 35 で `TextView` の `elegantTextHeight` default が true になったこと、Android 16 / targetSdkVersion 36 で false override が無視されることを分けて説明している。
したがって、本件の互換性リスクは「Android 16 へ OS アップデートしただけ」ではなく、「targetSdkVersion 36 化により `false` 指定が効かなくなる」点である。
実質影響はすべてのアプリではなく、対象 API / attribute の利用、または対象言語の表示レイアウトへの依存がある場合に顕在化する。

---

# 変更内容（What Changed）

- targetSdkVersion 35 以上では、`Paint` の `DEPRECATE_UI_FONT` compat change により elegant text height の default が true 相当になる。
- targetSdkVersion 36 以上では、`Paint` の `DEPRECATE_UI_FONT_ENFORCE` compat change により `setElegantTextHeight(false)` が warning を出して return し、native paint へ disabled state を設定しない。
- `TextView` は XML / style / TextAppearance の `elegantTextHeight` を読み取り、`TextView#setElegantTextHeight()` 経由で `TextPaint#setElegantTextHeight()` に渡す。したがって attribute false 指定も最終的には `Paint#setElegantTextHeight(false)` の enforce gate に到達する。
- `TextAppearanceSpan` も `elegantTextHeight` を読み取り、`TextPaint#setElegantTextHeight()` を呼ぶため同じ gate の影響を受ける。
- API surface では `Paint#isElegantTextHeight()` と `Paint#setElegantTextHeight(boolean)` が `@Deprecated` かつ `@FlaggedApi("com.android.text.flags.deprecate_elegant_text_height_api")` として公開されている。`TextView#setElegantTextHeight(boolean)` は public API として残るが、内部の `Paint` gate により false 指定は targetSdkVersion 36 以上で効かない。

## 適用条件（Applicability）

### OS アップデート時の挙動（OS Update Behavior）

- Android 16 にアップデートしただけで適用されるか: 原則 No。
- targetSdkVersion に依存しない根拠: なし。AOSP の false override 無効化は `@EnabledSince(targetSdkVersion = 36)` の compat change で制御される。
- Android 15 以前での挙動: targetSdkVersion 35 以上では default true。targetSdkVersion 35 のアプリは `elegantTextHeight=false` により override 可能。

### targetSdkVersion 36 以上での挙動（targetSdkVersion 36 Behavior）

- targetSdkVersion 36 以上で適用されるか: Yes。
- Android 16 以外で targetSdkVersion 36 にした場合の挙動: 指定 Android 15 tag にも `DEPRECATE_UI_FONT_ENFORCE` / `@EnabledSince(targetSdkVersion = 36)` は存在するため、技術的には同じ gate が見える。ただし Android 15 端末で targetSdkVersion 36 アプリを実際に評価するには、SDK / package install / compat framework の実機条件を別途確認する必要がある。
- opt-out / temporary override の有無: 公式文書上、`elegantTextHeight=false` による opt-out は Android 16 target で無視される。AOSP compat override によるテスト上の切り替えは可能な可能性があるが、公開 compat page には該当 entry は見つからなかったため、顧客向けの正式な回避策としては扱わない。

### その他の条件（Other Conditions）

- device/form factor: 条件なし。
- permission: 条件なし。
- API usage: `android:elegantTextHeight`、`TextView#setElegantTextHeight`、`Paint#setElegantTextHeight`、`TextAppearanceSpan` など。
- manifest attribute: 条件なし。
- component boundary: Android View / TextView / Paint のテキスト描画経路。Compose-only UI は Android View の `TextView` attribute には直接依存しないが、platform text rendering / font metrics を使う箇所があれば対象言語で確認が必要。

---

# AOSP 調査（AOSP Investigation）

## 関連ファイル（Related Files）

- `graphics/java/android/graphics/Paint.java`
- `libs/hwui/jni/Paint.cpp`
- `core/java/android/widget/TextView.java`
- `core/java/android/text/style/TextAppearanceSpan.java`
- `core/java/android/text/TextLine.java`
- `core/java/android/text/PrecomputedText.java`
- `core/res/res/values/attrs.xml`
- `core/api/current.txt`
- `core/java/android/text/flags/flags.aconfig`
- `core/java/android/os/Build.java`

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル（File / symbol） | Android 15 の基準挙動（baseline） | Android 16 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `Paint.DEPRECATE_UI_FONT` / 279646685 | `@EnabledSince(targetSdkVersion = VANILLA_ICE_CREAM)`。targetSdkVersion 35 以上で default true 相当 | 同じ。Android 16 tag では `@NoLogging` 追加のみ | Android 15 target で default true になる公式 statement の gate |
| `Paint.DEPRECATE_UI_FONT_ENFORCE` / 349519475 | `@EnabledSince(targetSdkVersion = 36)` が存在 | 同じ | Android 16 target で false override が ignored になる gate |
| `Paint#setElegantTextHeight(boolean)` | `Flags.deprecateElegantTextHeightApi()` かつ `!elegant` かつ `CompatChanges.isChangeEnabled(DEPRECATE_UI_FONT_ENFORCE)` の場合 return | 同じ | `setElegantTextHeight(false)` が native paint に反映されなくなる直接根拠 |
| `Paint#resetElegantTextHeight()` | `DEPRECATE_UI_FONT` enabled なら native state を `ELEGANT_TEXT_HEIGHT_UNSET`、それ以外は disabled にする | 同じ | default true / compact default の分岐を決める初期化経路 |
| `TextView#readTextAppearance()` / `applyTextAppearance()` | `elegantTextHeight` を読み取り `setElegantTextHeight(attributes.mElegant)` を呼ぶ | 同じ | XML / style / TextAppearance attribute が `Paint` gate に到達する経路 |
| `TextView#setElegantTextHeight(boolean)` | `mTextPaint.setElegantTextHeight(elegant)` 後、layout を破棄して再測定・再描画 | 同じ | View API 利用時の runtime path |
| `TextAppearanceSpan#updateMeasureState()` | span に `elegantTextHeight` があれば `TextPaint#setElegantTextHeight()` を呼ぶ | 同じ | span 経由の text rendering も同じ gate に入る |
| `Paint.cpp` JNI | Java state を minikin `FamilyVariant::ELEGANT` / `DEFAULT` / unset に変換 | 同じ周辺実装 | `elegantTextHeight` が font family variant selection に影響する根拠 |
| `TextLine` / `PrecomputedText` | `isElegantTextHeight()` が measurement / cache equality / hash に入る | 同じ | 行測定・precomputed text cache に関係する根拠 |

必須記入項目（Required context）:
- Entry point / caller: XML/style inflation -> `TextView.readTextAppearance()` -> `TextView.applyTextAppearance()` -> `TextView#setElegantTextHeight()` -> `TextPaint/Paint#setElegantTextHeight()` -> JNI `Paint.cpp#setElegantTextHeight()` -> minikin family variant selection。
- Relevant class or service responsibility: `TextView` は app UI の文字 attribute を読み取り、`Paint` は text drawing / measuring の font metrics と font family variant を保持する。
- Runtime path from app API / system event to changed code: app が `android:elegantTextHeight="false"` または `setElegantTextHeight(false)` を指定すると、最終的に `Paint#setElegantTextHeight(false)` に到達し、targetSdkVersion 36 以上では `DEPRECATE_UI_FONT_ENFORCE` により return する。
- Why unrelated code paths were excluded: `Window` / edge-to-edge、input method、font update service、test-only assets は本件の target gate や `elegantTextHeight` false override の有効性を決めないため除外した。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
| 指定 tag 間の `Paint#setElegantTextHeight()` / `DEPRECATE_UI_FONT_ENFORCE` に実質差分なし | No behavior change found between selected tags for core gate | 変更は Android 16 tag に初めて現れた差分というより、compat gate と公式 targetSdkVersion 36 policy の組み合わせとして説明される | Medium |
| `DEPRECATE_UI_FONT` は `@EnabledSince(VANILLA_ICE_CREAM)` | Changed default | Android 15 target で default true になる根拠 | High |
| `DEPRECATE_UI_FONT_ENFORCE` は `@EnabledSince(targetSdkVersion = 36)` | Changed condition / gate | targetSdkVersion 36 以上で false override を無効化する根拠 | High |
| `Paint#setElegantTextHeight(false)` は enforce change enabled 時に warning を出して return | Removed behavior | compact font / compact metrics への opt-out が効かなくなる | High |
| `core/api/current.txt` で `Paint` API が `@Deprecated` | API surface change | 公式文書の deprecated statement と一致 | High |

必須分類（Required interpretation）:
- Added behavior: targetSdkVersion 35 以上で elegant text height default true、targetSdkVersion 36 以上で false override enforced no-op になる compat behavior が存在する。
- Removed behavior: targetSdkVersion 36 以上では `elegantTextHeight=false` / `setElegantTextHeight(false)` による compact UI font 選択ができなくなる。
- Changed condition / gate: `DEPRECATE_UI_FONT` は targetSdkVersion 35、`DEPRECATE_UI_FONT_ENFORCE` は targetSdkVersion 36。
- Changed default: targetSdkVersion 35 以上では default が false/compact から true/elegant 相当に変わる。
- No behavior change found: 指定 tag 間では core `Paint` gate 自体の差分は `@NoLogging` 追加程度で、Android 16 r4 で初めて追加された実装差分としては確認できなかった。

## 事実（Facts）

- 公式文書は、この項目を apps targeting Android 16 / API level 36 の Behavior Change として掲載している。
- 公式文書は、Android 15 target では `elegantTextHeight` の default が true で、false に override できたと説明している。
- AOSP の `Paint.DEPRECATE_UI_FONT` は Change ID 279646685 で、targetSdkVersion 35 以上で default enabled。
- AOSP の `Paint.DEPRECATE_UI_FONT_ENFORCE` は Change ID 349519475 で、targetSdkVersion 36 以上で default enabled。
- `Paint#setElegantTextHeight(false)` は `DEPRECATE_UI_FONT_ENFORCE` が enabled の場合、warning を出して native state を更新せず return する。
- `Paint.cpp` は elegant text height state を minikin の `FamilyVariant::ELEGANT` / `DEFAULT` / unset に変換する。
- `TextView` と `TextAppearanceSpan` は attribute / span 指定を `TextPaint#setElegantTextHeight()` に流す。
- Android 16 の `Build.VERSION_CODES.BAKLAVA` は 36。Android 15 tag では `BAKLAVA` は `CUR_DEVELOPMENT` として存在する。
- 公開 compat framework changes ページでは、`279646685` / `349519475` / `DEPRECATE_UI_FONT` / `DEPRECATE_UI_FONT_ENFORCE` / `elegant` の該当 entry は見つからなかった。

## 観察（Observations）

- 本件の primary gate は OS version literal ではなく compat framework の targetSdkVersion gate である。
- 実質影響は `false` override がある場合に最も明確である。未指定アプリは targetSdkVersion 35 以上で既に default true のため、targetSdkVersion 36 化による差分は小さい。
- `TextView#setElegantTextHeight(false)` は public API として残るが、内部 `Paint` の gate により targetSdkVersion 36 以上では false の効果が反映されない。
- `TextLine` / `PrecomputedText` が `isElegantTextHeight()` を比較・hash に使うため、行測定・precomputed text cache にも font metrics state が関係する。

## 仮説（Hypotheses）

- Android 15 端末上で targetSdkVersion 36 アプリを動かす場合も、同じ compat gate が有効になる可能性がある。ただし Android 15 安定端末における targetSdkVersion 36 アプリの実行可否・compat default は、実機 image と package manager / SDK 条件で確認する必要がある。
- Compose-only UI は `TextView` attribute の直接影響は受けにくいが、platform text rendering の font metrics に依存する箇所では対象言語の visual regression が必要になる可能性がある。

## 結論（Conclusions）

- 主分類は `TARGET_SDK_36_CONDITIONAL`。
- Android 16 / targetSdkVersion 35 では、`elegantTextHeight=false` override は引き続き有効と判断する。
- Android 16 / targetSdkVersion 36 では、`elegantTextHeight=false` override は無視され、elegant text height が常に有効になる。
- 顧客向けには「Android 16 へ OS アップデートしただけの影響」と「targetSdkVersion 36 化により false override が効かなくなる影響」を分けて説明する必要がある。

## 適用ゲート根拠（Applicability Gate Evidence）

- targetSdkVersion gate: `DEPRECATE_UI_FONT` は targetSdkVersion 35 以上、`DEPRECATE_UI_FONT_ENFORCE` は targetSdkVersion 36 以上。
- CompatChanges.isChangeEnabled / ChangeId: `CompatChanges.isChangeEnabled(DEPRECATE_UI_FONT)`、`CompatChanges.isChangeEnabled(DEPRECATE_UI_FONT_ENFORCE)`。
- @EnabledAfter / @EnabledSince / default state: `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.VANILLA_ICE_CREAM)`、`@EnabledSince(targetSdkVersion = 36)`。
- Build.VERSION / SDK_INT gate: `Paint` の該当実装に明示的な runtime `SDK_INT` gate は確認していない。
- DeviceConfig / resources config: 該当なし。
- Permission/AppOps gate: 該当なし。
- Manifest/property gate: 該当なし。
- No gate found: OS update only / all apps を示す gate は確認していない。
- Gate conclusion: 公式 Behavior Change としては Android 16 以上かつ targetSdkVersion 36 以上。実質影響は `false` override または対象言語の font metrics 依存がある場合。
- Reasoning from source context: XML / API 指定は `TextView` / `TextPaint` 経由で `Paint#setElegantTextHeight(false)` に到達し、compat change enabled 時は native state 更新前に return するため、attribute / API 指定が ignored になる。

---

# 影響分析（Impact Analysis）

## 影響を受けるアプリ（Affected Apps）

- `android:elegantTextHeight="false"` を指定している Android View / TextView ベースのアプリ。
- `TextView#setElegantTextHeight(false)` または `Paint#setElegantTextHeight(false)` を呼んでいるアプリ。
- `TextAppearanceSpan` などで `elegantTextHeight=false` を指定しているテキスト表示。
- Arabic、Lao、Myanmar、Tamil、Gujarati、Kannada、Malayalam、Odia、Telugu、Thai の表示で、固定高さ、baseline、line spacing、複数行 clipping を厳密に調整している UI。

## 影響を受けない、または影響が小さいアプリ（Non-Affected Apps）

- `elegantTextHeight` を未指定で、targetSdkVersion 35 以降の default true を受け入れているアプリ。
- 対象言語を表示しない、または text container に十分な余白があるアプリ。
- Android View / TextView を使わず、Compose の text layout のみで実装しているアプリ。ただし platform font metrics 依存がある箇所は確認対象に残る。

## アプリ種別別の影響

| アプリ種別 | 影響 |
| --- | --- |
| elegantTextHeight 未指定 | targetSdkVersion 35 以上では既に default true。targetSdkVersion 36 化による差分は通常小さい |
| `android:elegantTextHeight="false"` 指定 | Android 16 / targetSdkVersion 36 で false 指定が効かず、行高や clipping が変わる可能性がある |
| `TextView#setElegantTextHeight(false)` 呼び出し | Android 16 / targetSdkVersion 36 で call が no-op になり、warning のみになる |
| 対象言語の固定高さ UI | line height 増加・baseline 差・text clipping 解消または layout overflow の可能性がある |
| Compose-only | `TextView` attribute 直接影響は小さいが、対象言語の visual regression は推奨 |

---

# 顧客影響（Customer Impact）

## 影響度（Impact Level）

- 要確認。

理由:
- 影響は API / attribute 使用と対象言語 UI 依存に限定される。
- ただし該当する場合、固定高さのボタン、リスト行、入力欄、ラベル、複数行テキストで表示崩れや baseline 差が出る可能性がある。

## OS アップデートだけの影響

Android 16 へ OS アップデートしただけで、targetSdkVersion 35 以下のアプリに `elegantTextHeight=false` 無効化が適用されるとは判断しない。
targetSdkVersion 35 のアプリでは、Android 15 で導入された default true はあるが、false override は維持される想定である。

## targetSdkVersion 36 化の影響

targetSdkVersion 36 以上に上げると、Android 16 端末上では `elegantTextHeight=false` による compact font / compact metrics への opt-out が無視される。
その結果、対象言語の文字がより大きい vertical metrics で測定・描画され、固定高さ layout で高さ、baseline、折り返し、クリッピングの見え方が変わる可能性がある。

---

# 期待挙動マトリクス（Expected Behavior Matrix）

| 端末 OS | targetSdkVersion | `elegantTextHeight` 未指定 | `elegantTextHeight=false` / API false | 判定 |
| --- | --- | --- | --- | --- |
| Android 15 | 35 | default true | override 可能 | Android 15 の default true 変更は受けるが、false opt-out は可能 |
| Android 16 | 35 | default true | override 可能 | OS update だけでは false override 無効化は適用されない想定 |
| Android 16 | 36 | true / always enabled | ignored / no-op | 本 Behavior Change の主対象 |
| Android 15 | 36 | 技術的には `DEPRECATE_UI_FONT_ENFORCE` gate が Android 15 tag にも存在 | 技術的には no-op になる可能性 | 実機・SDK 条件つきで要確認。公式 Behavior Change としては Android 16 target の項目 |

---

# 推奨対応候補（Recommended Action Candidates）

- `android:elegantTextHeight="false"`、`setElegantTextHeight(false)`、`Paint#setElegantTextHeight(false)` の利用箇所を棚卸しする。
- false 指定を layout 調整目的で使っている場合、固定高さ container、line spacing、padding、baseline alignment を見直す。
- Arabic、Lao、Myanmar、Tamil、Gujarati、Kannada、Malayalam、Odia、Telugu、Thai で visual regression を実施する。
- `TextView` / `EditText` / custom view / span / precomputed text を分けて確認する。
- 一時的な compat override はテスト用途に限定し、顧客向けの恒久回避策として案内しない。

---

# テスト観点（Test Considerations）

| 端末 OS（Device OS） | targetSdkVersion | 条件 | 期待挙動 |
| --- | --- | --- | --- |
| Android 15 | 35 | `elegantTextHeight=false` | compact 側に override 可能 |
| Android 16 | 35 | `elegantTextHeight=false` | compact 側に override 可能な想定 |
| Android 16 | 36 | `elegantTextHeight=false` | false 指定が ignored。elegant text height が有効 |
| Android 16 | 36 | false 指定なし | default true / elegant 側 |
| Android 16 | 36 | 対象言語 | 行高、baseline、クリッピング、複数行、固定高さ container 内表示を確認 |

確認対象:
- `android:elegantTextHeight="false"` 指定あり / なし。
- `TextView#setElegantTextHeight(false)` 呼び出しあり / なし。
- 対象言語ごとの単一行・複数行・EditText 空文字・固定高さボタン・RecyclerView 行。
- Android 15 端末上の targetSdkVersion 36 は、実行可能な検証環境がある場合に Android 16 端末との差を確認する。

---

# Traceability Checklist

- Investigated Android versions: `android-15.0.0_r36` -> `android-16.0.0_r4`
- Related Behavior Change document: https://developer.android.com/about/versions/16/behavior-changes-16#elegant-text-height
- Original statement being verified: 上記「公式ドキュメント確認」に記載。
- Evidence from AOSP source: `Paint.java`、`TextView.java`、`Paint.cpp`、`attrs.xml`、`current.txt`、`flags.aconfig`。
- AOSP source context reviewed: XML/style -> TextView -> TextPaint/Paint -> JNI/minikin の経路。
- Diff interpretation: changed default、changed condition / gate、removed behavior、no behavior change found between specified tags for core gate。
- Applicability classification: `TARGET_SDK_36_CONDITIONAL`
- Confidence level: Medium

---

# 人間の判断欄（Human Decision Placeholder）

最終優先度（Final Priority）:
- 未判断

判断（Decision）:
- 未判断

Owner notes:
- 最終優先度、severity、release readiness、顧客 communication priority は repository owner が判断する。

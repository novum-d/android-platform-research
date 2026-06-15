# Accessibility support of complex IME physical keyboard typing

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

Related documents:
- https://developer.android.com/reference/android/view/accessibility/AccessibilityEvent
- https://developer.android.com/reference/android/view/inputmethod/TextAttribute

Section:
Accessibility support of complex IME physical keyboard typing

Page type:
- Apps targeting Android 17 or higher

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- 公式文書は Android 17 / targetSdkVersion 37 以上向けページに掲載されている。
- `TextView` を使う targetSdkVersion 37 以上のアプリでは、IME から candidate selection data を取得し、アクセシビリティイベントの text change type を設定する挙動が既定で有効になると説明されている。
- ただし、local `frameworks-base` に Android 17 AOSP tag がないため、AOSP gate、API surface、Compat Change ID、default state は未検証である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | Unknown | 公式ページは targetSdkVersion 37+ 向けだが、IME / AccessibilityService / custom InputConnection の API 利用条件も含む。AOSP gate 未確認。 |
| targetSdkVersion 37 以上が必要か | Conditional, unverified | 公式文書は standard `TextView` について apps targeting Android 17 で既定有効と述べる。AOSP evidence は未取得。 |
| 追加の実行時条件があるか | Yes | CJKV IME、edit field、custom `InputConnection`、`TYPE_VIEW_TEXT_CHANGED` を処理する AccessibilityService などの API 利用条件がある。 |
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
- targetSdkVersion: standard `TextView` の既定有効化については、公式文書上 targetSdkVersion 37 以上。
- Device/form factor: physical keyboard typing と IME composition が関係するが、端末 form factor 条件は公式抜粋では明示されていない。
- Permission/API/component condition: CJKV IME、edit field、custom `InputConnection`、`AccessibilityEvent`、`TextAttribute`、AccessibilityService の `TYPE_VIEW_TEXT_CHANGED` 処理。
- App state/process condition: text composition / candidate selection / commit を伴う入力中。

Compat framework:
- Change ID: Unknown
- Change name: Unknown
- Default state: Unknown
- Toggleable for testing: Unknown

分類信頼度（Classification confidence）:
- Low

分類根拠（Classification evidence）:
- Official documentation page: `behavior-changes-17`
- Original applicability statement: standard `TextView` を使う targetSdkVersion 37 以上のアプリでは既定有効。
- AOSP targetSdk gate: 未確認。local `frameworks-base` に `android-17*` tag がない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# エグゼクティブサマリー（Executive Summary）

Android 17 では、CJKV 言語の IME 入力中に、変換候補の選択や composition / commit の違いをアクセシビリティサービスへ伝えるための `AccessibilityEvent` と `TextAttribute` API が追加される、と公式文書は説明している。目的は、スクリーンリーダーが複雑な IME 物理キーボード入力に対して、より正確な読み上げフィードバックを行えるようにすること。

通常の `TextView` を使う targetSdkVersion 37 以上のアプリでは、この機能が既定で有効になるとされている。一方、custom `InputConnection` を持つ edit field や IME、AccessibilityService は、必要に応じて新 API の利用・処理を実装する必要がある。

ただし、現時点の local `frameworks-base` には Android 17 AOSP tag がないため、実装差分、targetSdkVersion gate、Compat Change ID、default state は未確認である。

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
- Accessibility support of complex IME physical keyboard typing

Original statement being verified:

> new AccessibilityEvent and TextAttribute APIs

The supplied official text states that these APIs enhance screen reader feedback for CJKV language input. It also states that CJKV IMEs can signal candidate selection, apps with edit fields can specify text change types, and targetSdkVersion 37 apps using standard `TextView` have this behavior enabled by default.

## 解釈（Interpretation）

この変更は、CJKV 入力の composition 中に「変換候補が選択されたか」「変更が composition 中か commit か」といった意味情報を、IME、edit field、AccessibilityService の間で受け渡すための変更である。

互換性リスクというより、アクセシビリティ品質向上のための behavior / API adoption 項目である。ただし、standard `TextView` を使う targetSdkVersion 37 以上のアプリでは既定でイベント内容が変わるため、スクリーンリーダー連携や独自アクセシビリティイベント送信を持つアプリでは確認が必要になる。

---

# 変更内容（What Changed）

公式文書上の変更点:
- CJKV language input のスクリーンリーダー読み上げを改善するため、`AccessibilityEvent` と `TextAttribute` の API が追加される。
- IME は `TextAttribute.Builder.setTextSuggestionSelected()` で、composition 中に特定の変換候補が選択されたかを示せる。
- custom `InputConnection` を持つ edit field は `TextAttribute.isTextSuggestionSelected()` で候補選択情報を取得できる。
- edit field を持つアプリは `TYPE_VIEW_TEXT_CHANGED` dispatch 時に `AccessibilityEvent.setTextChangeTypes()` を呼び、text composition 中の変更か commit 由来の変更かを示せる。
- AccessibilityService は `AccessibilityEvent.getTextChangeTypes()` で変更種別を読み取り、読み上げ戦略を調整できる。
- targetSdkVersion 37 以上で standard `TextView` を使うアプリでは、TextView が IME からの data retrieval と accessibility event の text change type 設定を既定で処理すると説明されている。

AOSP で未確認の点:
- Android 16 baseline にこれらの API / event field / TextView default handling が存在しなかったこと。
- Android 17 で追加された API surface と implementation diff。
- `TextView` の targetSdkVersion 37 gate の実装箇所。
- custom `InputConnection`、IME、AccessibilityService に対する targetSdkVersion 条件の有無。
- Compat Change ID と default state。

## 適用条件（Applicability）

公式文書の一次判断では、standard `TextView` の既定処理は Android 17 / targetSdkVersion 37 以上 / TextView 使用時に適用される。IME、custom edit field、AccessibilityService については、新 API を利用するかどうかが追加条件になる。AOSP tag が未取得のため、確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

### OS アップデート時の挙動（OS Update Behavior）

- Android 17 にアップデートしただけで適用されるか: Unknown
- targetSdkVersion に依存しない根拠: なし。公式文書は targetSdkVersion 37 以上向けページで、standard `TextView` の既定有効化も targetSdkVersion 37 以上と述べる。
- Android 16 以前での挙動: AOSP tag 比較未実施。Android 16 baseline source は Android 17 tag との比較ができないため、この調査では platform evidence として採用していない。

### targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- targetSdkVersion 37 以上で適用されるか: standard `TextView` については公式文書上 Yes と読めるが、AOSP gate 未確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: Unknown。公式文書は Android 17 Behavior Changes として説明しているため、Android 17 platform behavior として扱う。
- opt-out / temporary override の有無: Unknown。compat framework evidence 未確認。

### その他の条件（Other Conditions）

- device/form factor: physical keyboard typing と関係するが、特定 form factor は公式抜粋では明示なし。
- permission: 公式抜粋では条件なし。
- API usage: `TextAttribute.Builder.setTextSuggestionSelected()`、`TextAttribute.isTextSuggestionSelected()`、`AccessibilityEvent.setTextChangeTypes()`、`AccessibilityEvent.getTextChangeTypes()`、`TYPE_VIEW_TEXT_CHANGED`。
- manifest attribute: Unknown。
- component boundary: IME app、edit field を持つ app、AccessibilityService の三者にまたがる。

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

- `core/java/android/view/accessibility/AccessibilityEvent.java`
- `core/java/android/view/inputmethod/TextAttribute.java`
- `core/java/android/widget/TextView.java`
- `core/java/android/view/inputmethod/InputConnection.java`
- `core/java/android/view/inputmethod/BaseInputConnection.java`
- compat framework 定義ファイル内の `TextView` / `AccessibilityEvent` / `TextAttribute` / text change type 関連 Change ID

## 確認したソース文脈（Source Context Reviewed）

Android 17 AOSP tag がないため、source context は未レビュー。

| File / symbol | Android 16 baseline | Android 17 behavior | Why this code path matters |
| --- | --- | --- | --- |
| Not reviewed | Not reviewed | Not reviewed | Android 17 tag がないため、公式文書の記述を AOSP diff で検証できない。 |

Required context:
- Entry point / caller: 未確認。想定される entry point は IME から edit field への composing text 設定、`TextView` の accessibility event dispatch、AccessibilityService の `TYPE_VIEW_TEXT_CHANGED` processing だが、AOSP evidence としては未採用。
- Relevant class or service responsibility: 未確認。
- Runtime path from app API / system event to changed code: 未確認。
- Why unrelated code paths were excluded: Android 17 tag 不在のため、source path の採否判断自体を保留。

## 差分解釈（Diff Interpretation）

| Observed diff | Interpretation | Behavior Change relevance | Confidence |
| --- | --- | --- | --- |
| No Android 17 tag diff available | Source diff type cannot be classified yet | 公式文書の API 追加と TextView default handling を source diff で裏取りできていない | Low |

Required interpretation:
- Added behavior: 未確認。
- Removed behavior: 未確認。
- Changed condition / gate: 未確認。
- Changed default: 未確認。
- No behavior change found: 未確認。tag 不在のため「no behavior change」とは判断しない。

## 事実（Evidence）

Facts:
- 公式文書は、CJKV language input の screen reader spoken feedback を改善するため、`AccessibilityEvent` と `TextAttribute` API を導入すると述べている。
- 公式文書は、CJKV IME が `TextAttribute.Builder.setTextSuggestionSelected()` で conversion candidate の選択状態を示せると述べている。
- 公式文書は、custom `InputConnection` を持つ edit field が `TextAttribute.isTextSuggestionSelected()` で candidate selection data を取得できると述べている。
- 公式文書は、apps with edit fields が `AccessibilityEvent.setTextChangeTypes()` を使って `TYPE_VIEW_TEXT_CHANGED` の text change type を指定できると述べている。
- 公式文書は、targetSdkVersion 37 以上かつ standard `TextView` を使うアプリではこの機能が既定で有効になると述べている。
- local `frameworks-base` には `android-16.0.0_r4` tag がある。
- local `frameworks-base` には `android-17*` tag がない。
- 調査時点で `frameworks-base` working tree は clean。

Observations:
- 公式ページ種別は targetSdkVersion 37 以上向けである。
- この項目は API 追加と framework default behavior の両方を含む。
- standard `TextView` の既定有効化は targetSdkVersion 37 条件があると読める。
- IME、custom edit field、AccessibilityService は、新 API を採用するかどうかが影響条件になる。
- AOSP tag がないため、実装が本当に targetSdkVersion 37 gate で制御されているかは未確認。
- Compat framework entry の有無も未確認。

Hypotheses:
- Android 17 / targetSdkVersion 37 の standard `TextView` では、IME から渡された `TextAttribute` を読み取り、`TYPE_VIEW_TEXT_CHANGED` に適切な text change type を設定する可能性が高い。
- targetSdkVersion 36 の standard `TextView` では旧イベント形式が維持される可能性があるが、AOSP gate 未確認のため断定しない。
- custom `InputConnection` を持つアプリでは、targetSdkVersion に関係なく API を明示的に利用しない限り、新しい feedback 改善が得られない可能性がある。

結論:
- 現時点で顧客向けに確定できるのは、「公式文書上は Android 17 / targetSdkVersion 37 以上の standard `TextView` で CJKV IME 入力のアクセシビリティイベントが改善される」という範囲まで。
- AOSP gate、API surface diff、compat framework default state が未確認のため、primary classification は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

## 適用ゲート根拠（Applicability Gate Evidence）

- targetSdkVersion gate: 未確認。Android 17 AOSP tag がないため、`targetSdkVersion` / `ApplicationInfo.targetSdkVersion` 検索は実施していない。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。Android 17 AOSP tag がないため、`CompatChanges.isChangeEnabled` / `@ChangeId` / `@EnabledAfter` / `@EnabledSince` 検索は実施していない。
- @EnabledAfter / @EnabledSince / default state: 未確認。
- Build.VERSION / SDK_INT gate: 未確認。
- DeviceConfig / resources config: 未確認。
- Permission/AppOps gate: 未確認。
- Manifest/property gate: 未確認。
- No gate found: 未判断。検索不能のため「gate なし」とは扱わない。
- Gate conclusion: Unknown。公式文書上の targetSdkVersion 37 条件と API usage 条件はあるが、AOSP evidence が不足している。
- Reasoning from source context: source context 未取得のため不可。

Searched:
- `frameworks-base` checkout status。
- `android-16.0.0_r4` tag の存在。
- `android-17*` tag の存在。

Not searched yet:
- Android 17 implementation files。
- Android 17 compat framework definitions。
- Android 17 API surface files。

理由（Reason）:
- Android 17 target tag が local checkout に存在しないため、tag 間 diff による platform evidence が作れない。

---

# 影響分析（Impact Analysis）

## 影響を受けるアプリ（Affected Apps）

影響または対応機会があるアプリ:
- CJKV language input を扱う IME アプリ。
- custom `InputConnection` を持つ edit field を実装しているアプリ。
- `TextView` ではなく独自 edit field / custom text editor を持つアプリ。
- `TYPE_VIEW_TEXT_CHANGED` を明示的に dispatch しているアプリ。
- `TYPE_VIEW_TEXT_CHANGED` を処理して読み上げや入力フィードバックを調整する AccessibilityService。
- targetSdkVersion 37 以上で standard `TextView` を使うアプリ。

## 影響を受けないアプリ（Non-Affected Apps）

影響が限定的と考えられるケース:
- CJKV IME composition / physical keyboard typing と関係しない入力フローのみを持つアプリ。
- standard `TextView` の既定処理に任せており、独自アクセシビリティイベントや custom `InputConnection` を持たないアプリ。
- AccessibilityService でも IME でもなく、text changed accessibility event を直接扱わないアプリ。
- targetSdkVersion 37 へ上げないアプリ。ただし、これは公式文書からの一次判断であり、AOSP gate 未確認。

---

# 顧客影響（Customer Impact）

## 影響度（Impact Level）

- Human decision required

※ 最終 severity / priority は人間が判断する。このレポートでは確定しない。

## ビジネス影響（Business Impact）

- ユーザー影響: CJKV 入力中のスクリーンリーダー読み上げがより正確になり、候補選択、composition、commit の違いが伝わりやすくなる可能性がある。
- 運用影響: IME、custom editor、AccessibilityService を提供している場合、Android 17 対応として API adoption と読み上げ挙動の検証が必要になる。
- 開発影響: standard `TextView` では既定対応される可能性がある一方、custom `InputConnection` / custom accessibility event dispatch では明示的な実装が必要。

---

# サービス影響例（Service Impact Examples）

このセクションは、公式文書と AOSP evidence から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: 物理キーボードを使う業務入力アプリ

- 対象サービス例: POS、倉庫管理、医療・金融の業務入力、Chromebook / tablet keyboard 利用アプリ。
- 影響を受ける実装パターン: complex IME composition と physical keyboard input を前提にした text field / shortcut handling。
- 発生条件: Android 17 / targetSdkVersion 37 で accessibility support と IME physical keyboard typing の挙動が変わる場合。
- ユーザーに見える症状: 日本語入力、変換、候補選択、アクセシビリティ読み上げとの組み合わせで入力体験が変わる可能性。
- 開発・運用への影響: 外部キーボード、IME、accessibility service を組み合わせた QA が必要になる可能性。
- 推奨対応候補: key event を直接消費しすぎない、standard text input を利用する、IME composition test を追加する。
- 根拠: 公式 Behavior Change statement と report の AOSP evidence limitation。
- Confidence（信頼度）: Low
- 注意: 具体的な IME / accessibility service 別の挙動は未検証。

## 例2（Example 2）: アクセシビリティ利用者向けの入力支援機能

- 対象サービス例: メモ、チャット、文書編集、教育アプリ。
- 影響を受ける実装パターン: accessibility focus、screen reader、hardware keyboard shortcut、IME composing text が同時に動く UI。
- 発生条件: physical keyboard typing と accessibility support の platform behavior が Android 17 で変わる場合。
- ユーザーに見える症状: 入力中の読み上げ、候補操作、カーソル移動の体感が変わる可能性。
- 開発・運用への影響: TalkBack / physical keyboard / major IME の組み合わせ検証が必要になる可能性。
- 推奨対応候補: accessibility node / text selection state を標準 API と整合させ、custom key handling を限定する。
- 根拠: 公式 statement と report の source evidence 未確認事項。
- Confidence（信頼度）: Low
- 注意: 実利用者への影響度は human decision と実機評価が必要。

---

# 対応候補（Required Actions）

## 必須対応（Must）

- custom `InputConnection` を持つ edit field があるか確認する。
- 独自に `TYPE_VIEW_TEXT_CHANGED` を dispatch している箇所があるか確認する。
- CJKV IME、custom editor、AccessibilityService を提供している場合、Android 17 / targetSdkVersion 37 の入力・読み上げテストを計画する。

## 推奨対応（Recommended）

- IME アプリは、composing text 設定時に `TextAttribute.Builder.setTextSuggestionSelected()` を使えるか検討する。
- custom edit field は `TextAttribute.isTextSuggestionSelected()` を読み取り、`AccessibilityEvent.setTextChangeTypes()` で text change type を設定する設計を検討する。
- AccessibilityService は `AccessibilityEvent.getTextChangeTypes()` を読み取り、composition / commit / candidate selection に応じた feedback strategy を検討する。
- standard `TextView` を使うアプリでも、targetSdkVersion 37 更新時に CJKV 入力とスクリーンリーダーの回帰テストを行う。

## 任意対応（Optional）

- Android 17 AOSP tag 公開後、`TextView` default handling、API surface、compat Change ID を再調査する。
- CJKV 以外の IME や software keyboard 入力で副作用がないか smoke test を行う。

---

# 検証方法（Verification Method）

## 検証マトリクス（Matrix）

| Device OS | targetSdkVersion | Compat flag | Expected behavior |
| --- | --- | --- | --- |
| Android 16 | 36 | default | Android 16 baseline。新 API / TextView default handling の有無は Android 17 tag 比較待ち。 |
| Android 17 | 36 | default | Unknown。standard `TextView` の既定有効化は targetSdkVersion 37 条件と読めるが、AOSP gate 未確認。 |
| Android 17 | 37 | default | 公式文書上は standard `TextView` が IME data retrieval と text change type 設定を既定で処理する。 |
| Android 17 | 36 | force-enabled if available | Unknown。Compat Change ID 未確認。 |
| Android 17 | 37 | force-disabled if available | Unknown。Compat Change ID 未確認。 |

## 手順（Steps）

- targetSdk変更: test app を targetSdkVersion 36 と 37 で build し、Android 17 上の standard `TextView` と custom edit field の差を確認する。
- compat framework command: Change ID 未確認のため未定。Android 17 tag / compat page 確認後に追加する。
- テスト方法: CJKV IME、物理キーボード、standard `TextView`、custom `InputConnection`、AccessibilityService を組み合わせる。
- 再現手順: composition 中の candidate selection と commit を行い、`TYPE_VIEW_TEXT_CHANGED` の text change type とスクリーンリーダー読み上げを記録する。
- 期待結果: targetSdkVersion 37 の standard `TextView` では、公式文書どおり text change type が設定され、AccessibilityService が変更種別を識別できる。targetSdkVersion 36 の結果は AOSP gate 確認待ち。

---

# 結論（Conclusion）

公式文書は、Android 17 で CJKV IME の複雑な物理キーボード入力に対するアクセシビリティフィードバックを改善するため、`AccessibilityEvent` と `TextAttribute` の API と standard `TextView` の既定処理を導入すると説明している。影響範囲は、IME、custom edit field、AccessibilityService、targetSdkVersion 37 以上の standard `TextView` 利用アプリに分かれる。

一方で、local `frameworks-base` に Android 17 AOSP tag がないため、実装差分、targetSdkVersion gate、API surface diff、Compat Change ID、default state を検証できていない。現時点の primary classification は `UNKNOWN_NEEDS_MORE_EVIDENCE`、confidence は Low とする。

Human decision placeholder:
- Final priority: Human decision required
- Final severity: Human decision required
- Release readiness: Human decision required
- Customer communication priority: Human decision required
- Next required human decision: Android 17 AOSP tag 公開後に再調査するか、公式 documentation ベースの暫定 adoption guidance として扱うかを判断する。

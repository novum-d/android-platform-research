# 複雑な IME 物理キーボード入力のアクセシビリティ対応

## 基本情報

### 調査対象 Android バージョン

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

### Behavior Change 文書

文書:
- https://developer.android.com/about/versions/17/behavior-changes-17

関連文書:
- https://developer.android.com/reference/android/view/accessibility/AccessibilityEvent
- https://developer.android.com/reference/android/view/inputmethod/TextAttribute
- https://developer.android.com/reference/android/view/inputmethod/EditorInfo

セクション:
- Accessibility support of complex IME physical keyboard typing

ページ種別:
- Apps targeting Android 17 or higher

### 分類スナップショット

主分類（Primary classification）:
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- 公式ドキュメントでは、Android 17 および `targetSdkVersion 37` 以上を対象としたページで説明されている。
- 標準 `TextView` を使用する `targetSdkVersion 37` 以上のアプリでは、IME から candidate selection data を取得し、アクセシビリティイベントの text change type を設定する動作がデフォルトで有効になると説明されている。
- AOSP では `AccessibilityEvent` / `TextAttribute` / `TextView` / `EditableInputConnection` の実装差分を確認できた。
- ただし、確認した `frameworks-base` の該当実装には `Build.VERSION_CODES.CINNAMON_BUN`、`targetSdkVersion 37`、`CompatChanges.isChangeEnabled()` による明示的な target gate が見つからなかった。公式文書の target 37 条件と AOSP gate の対応が閉じていないため、確定分類は保留する。

早見表:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 未確定 | `TextView` 実装は `a11yTextChangeTypesApi()` flag で動作し、targetSdkVersion ゲートは見つからない。flag default / rollout の確認が必要。 |
| `targetSdkVersion 37` 以上が必要か | 公式文書上は Yes / AOSP gate は未検出 | target 37 ページに掲載されているが、該当コードに targetSdkVersion 37 分岐を確認できない。 |
| 追加の実行時条件があるか | ある | CJKV IME、`TextAttribute`、標準 `TextView` / `EditableInputConnection`、`TYPE_VIEW_TEXT_CHANGED`、AccessibilityService が関係する。 |
| Compat Change ID が関係するか | 確認できず | `@ChangeId` / `@EnabledSince(CINNAMON_BUN)` / `CompatChanges.isChangeEnabled()` は該当実装で確認できない。 |

### 調査日

2026-06-18

### 信頼度

- Medium

### 適用条件分類

適用される条件:

- [ ] Android 17 上の全アプリ（targetSdkVersion に依存しない）
- [ ] Android 17 以上で targetSdkVersion >= 37
- [ ] targetSdkVersion 37 以上かつ追加の実行時条件を満たす場合に適用
- [ ] Mainline / Google Play system update に依存
- [ ] API 追加のみであり、挙動変更ではない
- [x] 未確認 / 追加根拠が必要

必要な実行時条件:

- Android version: Android 17 (`android-17.0.0_r1`)。
- targetSdkVersion: 公式文書上は 37 以上。ただし AOSP の該当 Java 実装では targetSdkVersion 37 gate は未検出。
- Device/form factor: 物理キーボード入力や CJKV IME composition が関係するが、特定 form factor の gate は確認していない。
- Permission/API/component condition: CJKV IME、標準 `TextView` / `EditableInputConnection`、独自 `InputConnection`、`TextAttribute`、`AccessibilityEvent.TYPE_VIEW_TEXT_CHANGED`、AccessibilityService。
- App state/process condition: IME composition、候補選択、commit を伴うテキスト入力中。

Compat framework:

- Change ID: 確認できず
- 変更名: 確認できず
- 既定状態: `android.view.accessibility.a11y_text_change_types_api` flag に依存
- テスト時の切り替え可否: aconfig flag 側の切り替えが必要。Compat ChangeId は未検出。

分類信頼度:

- Medium

分類根拠:

- `core/java/android/view/accessibility/AccessibilityEvent.java`
- `core/java/android/view/inputmethod/TextAttribute.java`
- `core/java/android/view/inputmethod/EditorInfo.java`
- `core/java/android/widget/TextView.java`
- `core/java/com/android/internal/inputmethod/EditableInputConnection.java`
- `core/java/android/view/accessibility/flags/accessibility_flags.aconfig`

---

# エグゼクティブサマリー

Android 17 では、CJKV IME の入力中に、変換候補の選択、composition 中の変更、commit による確定入力を AccessibilityService が識別できるようにする API と `TextView` のイベント設定処理が追加されている。

AOSP では、`AccessibilityEvent` に `TEXT_CHANGE_TYPE_IN_COMPOSITION`、`TEXT_CHANGE_TYPE_COMMITTED_BY_IME`、`TEXT_CHANGE_TYPE_CONVERSION_SUGGESTION_SELECTED_BY_IME` と `setTextChangeTypes()` / `getTextChangeTypes()` が追加されている。`TextAttribute` には `setTextSuggestionSelected()` / `isTextSuggestionSelected()` が追加され、`EditableInputConnection` が IME から受け取った `TextAttribute` を `TextView` の候補選択状態へ反映する。`TextView` は `TYPE_VIEW_TEXT_CHANGED` を送る時に composition / commit / suggestion selected の種別を設定する。

一方で、確認できた実装は `a11yTextChangeTypesApi()` flag によって制御されており、targetSdkVersion 37 の直接 gate は見つからない。公式文書の target 37 条件と AOSP 実装の対応が未解決のため、分類は `UNKNOWN_NEEDS_MORE_EVIDENCE`、信頼度は Medium とする。

---

# 公式ドキュメント確認

## 原文（Statement）

Page title:
- Behavior changes: Apps targeting Android 17 or higher

Page URL:
- https://developer.android.com/about/versions/17/behavior-changes-17

ページ種別:
- Apps targeting Android 17

Section title:
- Accessibility support of complex IME physical keyboard typing

検証対象の原文:
- CJKV language input の screen reader feedback を改善するため、新しい `AccessibilityEvent` と `TextAttribute` API が導入される。
- CJKV IME は候補選択状態を通知できる。
- 編集フィールドを持つアプリは `TYPE_VIEW_TEXT_CHANGED` event の text change type を指定できる。
- AccessibilityService は text change type を読み、composition / commit / candidate selection を区別できる。
- 標準 `TextView` を使用する targetSdkVersion 37 以上のアプリでは既定で処理されると説明されている。

## 解釈

この変更は、IME、編集フィールド、AccessibilityService の三者にまたがるアクセシビリティ品質改善である。互換性リスクは、独自 `InputConnection` や独自 `TYPE_VIEW_TEXT_CHANGED` event を実装している場合、Android 17 の新 API と整合しない可能性がある点にある。

---

# 変更内容

AOSP で確認した変更点:
- `AccessibilityEvent` に text change type constants と `setTextChangeTypes()` / `getTextChangeTypes()` が追加された。
- `TextAttribute` に `mTextSuggestionSelected`、`isTextSuggestionSelected()`、`Builder.setTextSuggestionSelected()` が追加された。
- `EditorInfo` の input type bit に `TYPE_TEXT_FLAG_ENABLE_TEXT_SUGGESTION_SELECTED` が追加された。
- `TextView.onCreateInputConnection()` は `a11yTextChangeTypesApi()` が true の場合に `EditorInfo.TYPE_TEXT_FLAG_ENABLE_TEXT_SUGGESTION_SELECTED` を `inputType` に追加する。
- `EditableInputConnection.setComposingText(..., TextAttribute)` は `TextAttribute.isTextSuggestionSelected()` を `TextView.setSuggestionSelection()` に反映する。
- `EditableInputConnection.commitText(..., TextAttribute)` は commit 中フラグを `TextView.beginCommitText()` / `endCommitText()` で管理し、commit 後に suggestion selection を reset する。
- `TextView.sendAccessibilityEventTypeViewTextChanged()` は `a11yTextChangeTypesApi()` が true の場合、`setTextChangeTypes(event)` により composition / commit / suggestion selected を event に設定する。

## 適用条件

### OS アップデート時の挙動

- Android 17 にアップデートしただけで適用されるか: 未確定。
- targetSdkVersion に依存しない根拠: 確認した `TextView` / `EditableInputConnection` 実装には targetSdkVersion ゲートが見つからず、`a11yTextChangeTypesApi()` flag で制御される。
- Android 16 以前での挙動: `AccessibilityEvent` の text change type API、`TextAttribute` の suggestion selected field、`TextView` の text change type 設定処理は Android 17 tag で追加されている。

### targetSdkVersion 37 以上での挙動

- `targetSdkVersion 37` 以上で適用されるか: 公式文書上は Yes。ただし AOSP の該当 Java path に targetSdkVersion 37 gate は未検出。
- Android 17 / targetSdkVersion 36 と Android 17 / targetSdkVersion 37 の差分: AOSP 根拠 だけでは差分を確定できない。
- opt-out / temporary override の有無: Compat ChangeId は未検出。feature flag `a11y_text_change_types_api` の状態に依存する。

### その他の条件

- API usage: IME が `TextAttribute.Builder.setTextSuggestionSelected()` を使う、または app / framework が `AccessibilityEvent.setTextChangeTypes()` を使う。
- 標準 `TextView`: flag enabled 時、IME へ suggestion selected support を伝え、`TYPE_VIEW_TEXT_CHANGED` に text change type を設定する。
- Custom editor: 独自 `InputConnection` は `TextAttribute` を明示的に処理しない限り、標準 `TextView` と同等の情報を event に載せられない可能性がある。
- AccessibilityService: `AccessibilityEvent.getTextChangeTypes()` を読むことで、composition / commit / suggestion selected を区別できる。

---

# AOSP 調査

## checkout 状態

根拠を採用する前に確認したコマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list android-17.0.0_r1
```

結果:
- `frameworks-base` の working tree は調査時点で clean。
- `android-16.0.0_r4` tag は存在する。
- `android-17.0.0_r1` tag は存在する。

## 関連ファイル

- `core/java/android/view/accessibility/AccessibilityEvent.java`
- `core/java/android/view/inputmethod/TextAttribute.java`
- `core/java/android/view/inputmethod/EditorInfo.java`
- `core/java/android/widget/TextView.java`
- `core/java/android/widget/Editor.java`
- `core/java/com/android/internal/inputmethod/EditableInputConnection.java`
- `core/java/android/view/accessibility/flags/accessibility_flags.aconfig`
- `core/api/current.txt`

## 確認したソース文脈

| ファイル / シンボル | Android 16 基準挙動 | Android 17 挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `AccessibilityEvent.TEXT_CHANGE_TYPE_*` | text change type constants は存在しない | composition / committed by IME / conversion suggestion selected constants が追加 | AccessibilityService が変更種別を読むための API surface |
| `AccessibilityEvent.setTextChangeTypes()` / `getTextChangeTypes()` | 存在しない | `TYPE_VIEW_TEXT_CHANGED` event に text change type bitmask を設定・取得できる | 公式文書の AccessibilityEvent API 追加に対応 |
| `TextAttribute.Builder.setTextSuggestionSelected()` / `isTextSuggestionSelected()` | 存在しない | IME が候補選択中であることを editor へ伝えられる | 公式文書の candidate selection data に対応 |
| `EditorInfo.TYPE_TEXT_FLAG_ENABLE_TEXT_SUGGESTION_SELECTED` | input type bit に存在しない | IME に suggestion selected support を伝える bit として追加 | `TextView` が IME から候補選択情報を受ける前提 |
| `EditableInputConnection.setComposingText(..., TextAttribute)` | suggestion selected state を `TextView` へ反映しない | `textAttribute.isTextSuggestionSelected()` を `TextView.setSuggestionSelection()` に反映 | IME から editor への runtime path |
| `EditableInputConnection.commitText(..., TextAttribute)` | commit 中状態を accessibility event 用に保持しない | `beginCommitText()` / `endCommitText()` で commit state を管理し、suggestion selection を reset | commit と composition を区別する根拠 |
| `TextView.setTextChangeTypes()` | 存在しない | composing span、suggestion selected、commit state を見て event bitmask を設定 | 標準 `TextView` の既定処理の根拠 |
| `accessibility_flags.aconfig` | `a11y_text_change_types_api` flag なし | flag が追加され、説明は text change types を AccessibilityEvent に送る機能 | 実装 gate の根拠 |

必須記入項目:

- Entry point / caller: IME -> `InputConnection.setComposingText(..., TextAttribute)` / `commitText(..., TextAttribute)` -> `EditableInputConnection` -> `TextView` state -> `sendAccessibilityEventTypeViewTextChanged()` -> `AccessibilityEvent.setTextChangeTypes()` -> AccessibilityService。
- Relevant class or service responsibility: `TextAttribute` は IME から editor へ候補選択情報を渡し、`TextView` は text change type を event に設定し、`AccessibilityEvent` は service が読む bitmask を保持する。
- Runtime path from app API / system event to changed code: CJKV IME が composition / suggestion selection / commit を行う -> `TextAttribute` 付き InputConnection call -> `TextView` が internal state を更新 -> text changed accessibility event に change type を付与する。
- 除外した無関係なコードパス: accessibility cache、window info、keyboard layout resource、controller glyph map、generic accessibility service changes は、この Behavior Change の API / TextView event path を直接説明しないため除外した。

## 差分解釈

| 確認した差分 | 解釈 | 挙動変更との関係 | 信頼度 |
| --- | --- | --- | --- |
| `AccessibilityEvent` text change type API 追加 | API addition | AccessibilityService が composition / commit / suggestion selected を区別可能になる | High |
| `TextAttribute` suggestion selected field 追加 | API addition / data propagation | IME から editor へ候補選択状態を伝える | High |
| `EditableInputConnection` が `TextAttribute` を `TextView` 状態へ反映 | added behavior | 標準 TextView が IME data retrieval を行う根拠 | High |
| `TextView` が `TYPE_VIEW_TEXT_CHANGED` に text change type を設定 | changed default behavior when flag enabled | 標準 TextView の accessibility event 内容が変わる | High |
| `a11y_text_change_types_api` flag | feature gate | targetSdk gate ではなく flag gate として確認 | Medium |
| targetSdkVersion 37 gate 未検出 | unresolved gate mismatch | 公式 target 37 条件と AOSP 実装の対応が未解決 | Medium |

---

# 事実 / 観察 / 仮説 / 結論

## 事実

- Android 17 tag の `AccessibilityEvent` に text change type API が追加されている。
- Android 17 tag の `TextAttribute` に suggestion selected API が追加されている。
- Android 17 tag の `TextView` は `a11yTextChangeTypesApi()` が true の時、`TYPE_VIEW_TEXT_CHANGED` event に text change type を設定する。
- Android 17 tag の `EditableInputConnection` は `TextAttribute.isTextSuggestionSelected()` を `TextView` へ反映する。
- 該当ファイルの検索では、CINNAMON_BUN / targetSdkVersion 37 / compat ChangeId による gate は確認できない。

## 観察

- AOSP 実装は公式文書の API / TextView behavior を裏付ける。
- 一方で、公式文書が述べる targetSdkVersion 37 条件は、少なくとも確認した Java path では直接表現されていない。
- flag が disabled の場合、`TextAttribute` の suggestion selected field の parcel read/write や `TextView` event 設定は動作しない。

## 仮説

- targetSdkVersion 37 条件は API surface / SDK availability と公式 documentation policy に由来し、runtime implementation は feature flag によって制御されている可能性がある。
- または、flag default / build configuration / module boundary 側で target 37 相当の rollout が管理されている可能性がある。

## 結論

- AOSP 根拠 は十分に更新できたが、targetSdkVersion 37 gate は確認できない。
- そのため、顧客向けの確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` のままとする。
- 実装上の影響説明としては、「Android 17 の flag-enabled TextView / InputConnection / AccessibilityEvent path で CJKV IME 入力の text change type が AccessibilityService に伝わる」と説明できる。

## 適用ゲート根拠

- targetSdkVersion 適用ゲート: 未検出。`TextView`、`TextAttribute`、`AccessibilityEvent`、`EditableInputConnection` の該当 path では `Build.VERSION_CODES.CINNAMON_BUN` や targetSdkVersion 37 check を確認できない。
- CompatChanges.isChangeEnabled / Change ID: 未検出。
- @EnabledAfter / @EnabledSince / default state: 該当実装では未検出。
- Build.VERSION / SDK_INT 適用ゲート: Android 17 platform API / flag として追加。
- DeviceConfig / resources config: 未確認。
- Permission/AppOps 適用ゲート: なし。
- Manifest/property 適用ゲート: なし。
- 適用ゲートの結論: `a11y_text_change_types_api` feature flag は確認。targetSdkVersion 37 gate は未確認。

---

# 影響分析

## 影響を受けるアプリ

- CJKV 言語入力を扱う IME アプリ。
- 独自の `InputConnection` を実装した編集フィールドを持つアプリ。
- 標準 `TextView` ではなく、独自の編集フィールドやカスタムテキストエディタを実装しているアプリ。
- `TYPE_VIEW_TEXT_CHANGED` イベントを明示的に送出しているアプリ。
- `TYPE_VIEW_TEXT_CHANGED` を処理し、読み上げや入力フィードバックを調整する AccessibilityService。
- targetSdkVersion 37 以上で標準 `TextView` を利用するアプリ。

## 影響を受けにくいアプリ

- CJKV IME の変換処理や物理キーボード入力と関係しない入力フローのみを持つアプリ。
- AccessibilityService や IME ではなく、text changed 系のアクセシビリティイベントを直接扱わないアプリ。
- 標準 `TextView` に任せ、読み上げ内容の厳密な差分を検証対象にしていないアプリ。

---

# 顧客影響

## 影響度

- 人間による判断が必要

## ビジネス影響

- ユーザー影響: CJKV 言語入力時のスクリーンリーダー読み上げ精度が向上し、変換候補の選択状態、composition 中の変更、確定入力による変更の違いがより適切に伝わる可能性がある。
- 運用影響: IME、独自エディタ、AccessibilityService を提供している場合は、Android 17 対応の一環として新 API の採用可否や読み上げ挙動の検証が必要になる。
- 開発影響: 標準 `TextView` を利用している場合は framework 側で対応されるが、独自 `InputConnection` や独自 accessibility event dispatch を持つ場合は明示的な対応が必要になる可能性がある。

---

# サービス影響例

このセクションは、公式文書と AOSP 根拠から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: Google Docs / Microsoft Word / Notion のような文書編集アプリ

- 具体サービス例: Google Docs、Microsoft Word、Notion、Evernote。
- 影響を受ける実装パターン: 標準 `TextView` ではなく独自 editor / custom `InputConnection` で CJKV 変換入力を扱う実装。
- 発生条件: Android 17 の TextView / InputConnection / AccessibilityEvent path で CJKV IME の text change type が伝わる一方、独自 editor が同等の event 情報を出さない場合。
- ユーザーに見える症状: TalkBack などの読み上げで、変換中・候補選択・確定入力の違いが伝わりにくい可能性。
- 技術的に起きていること: framework は `TextAttribute` / `AccessibilityEvent` の追加情報を扱うが、custom editor は明示的に対応しない限り新しい分類を伝えない。
- 推奨対応シーン: 日本語・中国語・韓国語・ベトナム語入力を独自 editor で扱う文書編集機能。
- 検証観点: TalkBack 有効時の CJKV composition、candidate selection、commit の読み上げ差分。
- 根拠: `TextAttribute`、`EditableInputConnection`、`TextView`、`AccessibilityEvent` の AOSP source context。
- Confidence（信頼度）: Medium。targetSdkVersion gate は未確認のため分類は未確定。
- 注意: 上記サービスで発生確認した事実ではない。実際の影響は custom editor 実装と accessibility event dispatch に依存する。

## 例2（Example 2）: Gboard / Simeji / ATOK と TalkBack の組み合わせ

- 具体サービス例: Gboard、Simeji、ATOK、Google TalkBack。
- 影響を受ける実装パターン: IME または AccessibilityService が CJKV 変換中の text change type を使って feedback を最適化する実装。
- 発生条件: Android 17 の新 API / flag-enabled path が有効で、IME / AccessibilityService が追加情報を送受信する場合。
- ユーザーに見える症状: 変換候補の選択、composition 中の変更、確定入力の読み上げがより区別される可能性。未対応の組み合わせでは期待どおり改善しない可能性。
- 技術的に起きていること: `TextAttribute` の suggestion selected field などが AccessibilityEvent に反映され、サービス側がそれを解釈できる。
- 推奨対応シーン: IME、screen reader、入力支援 SDK の Android 17 対応確認。
- 検証観点: 物理キーボード / ソフトキーボード、CJKV 各言語、標準 TextView / custom editor の組み合わせ。
- 根拠: 公式 Behavior Change statement と AOSP の TextView / InputConnection / AccessibilityEvent path。
- Confidence（信頼度）: Medium。
- 注意: 上記サービスで発生確認した事実ではない。IME と AccessibilityService のバージョン差分を個別に確認する必要がある。

---

# 対応候補

## 必須対応（Must）

- 独自の `InputConnection` を実装した編集フィールドが存在するか確認する。
- 独自に `TYPE_VIEW_TEXT_CHANGED` を送出している箇所が存在するか確認する。
- CJKV IME、独自エディタ、AccessibilityService を提供している場合は、Android 17 環境での入力・読み上げテストを計画する。

## 推奨対応（Recommended）

- IME アプリは、composing text 設定時に `TextAttribute.Builder.setTextSuggestionSelected()` を利用できるか検討する。
- 独自の編集フィールドは、`TextAttribute.isTextSuggestionSelected()` の利用、および `AccessibilityEvent.setTextChangeTypes()` による text change type 設定を検討する。
- AccessibilityService は、`AccessibilityEvent.getTextChangeTypes()` を利用し、composition・commit・候補選択状態に応じたフィードバック戦略を検討する。
- 標準 `TextView` を利用しているアプリでも、targetSdkVersion 37 移行時には CJKV 入力とスクリーンリーダーを組み合わせた回帰テストを実施する。

---

# 検証方法

## 検証マトリクス

| 端末 OS | targetSdkVersion | flag / gate | 期待される挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | default | text change type API / TextView default handling は存在しない。 |
| Android 17 | 36 | `a11y_text_change_types_api` enabled | AOSP 実装上は TextView が text change type を設定する可能性。target gate 未確認。 |
| Android 17 | 37 | `a11y_text_change_types_api` enabled | 公式文書上の対象。標準 `TextView` では text change type が設定される。 |
| Android 17 | 37 | flag disabled | `TextAttribute` suggestion selected field と `TextView` event 設定は無効化される可能性。 |

## 手順

- targetSdkVersion 36 / 37 のテストアプリを用意し、標準 `TextView` と独自 `InputConnection` を比較する。
- CJKV IME と物理キーボードで、composition、candidate selection、commit を行う。
- AccessibilityService または instrumentation で `TYPE_VIEW_TEXT_CHANGED` の `getTextChangeTypes()` を記録する。
- `TextAttribute.Builder.setTextSuggestionSelected(true)` を送る IME / テスト IME で `TEXT_CHANGE_TYPE_CONVERSION_SUGGESTION_SELECTED_BY_IME` が設定されるか確認する。

---

# One Page Summary

- [summary](../../../summaries/target/accessibility/accessibility-ime-physical-keyboard-summary.md)

# 人間の判断欄

最終優先度（Final Priority）:
- 人間による判断が必要

最終影響度:
- 人間による判断が必要

リリース判断:
- 人間による判断が必要

顧客通知優先度:
- 人間による判断が必要

次に必要な人間の判断:
- 公式 targetSdkVersion 37 条件と AOSP の flag-only implementation の差分を、追加ソースまたは実機検証でどう扱うか。

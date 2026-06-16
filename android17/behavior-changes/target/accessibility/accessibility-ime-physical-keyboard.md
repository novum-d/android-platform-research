# 複雑な IME 物理キーボード入力のアクセシビリティ対応

## 基本情報（Metadata）

### 調査対象 Android バージョン

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP タグ

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

### Behavior Change 文書

Document:
https://developer.android.com/about/versions/17/behavior-changes-17

Related documents:
- https://developer.android.com/reference/android/view/accessibility/AccessibilityEvent
- https://developer.android.com/reference/android/view/inputmethod/TextAttribute

Section:
複雑な IME 物理キーボード入力のアクセシビリティ対応

Page type:
- Apps targeting Android 17 or higher

### 分類スナップショット

主分類（Primary classification）:
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- 公式文書は Android 17 / targetSdkVersion 37 以上向けページに掲載されている。
- `TextView` を使う targetSdkVersion 37 以上のアプリでは、IME から candidate selection data を取得し、アクセシビリティイベントの text 変更 type を設定する挙動が既定で有効になると説明されている。
- ただし、ローカルの `frameworks-base` に Android 17 AOSP タグがないため、AOSP 適用ゲート、API surface、Compat Change ID、default state は未検証である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

早見表:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 未確認 | 公式ページは targetSdkVersion 37+ 向けだが、IME / AccessibilityService / custom InputConnection の API 利用条件も含む。AOSP 適用ゲートは未確認。 |
| targetSdkVersion 37 以上が必要か | 条件付きの可能性があるが未検証 | 公式文書は、standard `TextView` について Android 17 を対象とするアプリで既定有効と述べる。AOSP 根拠は未取得。 |
| 追加の実行時条件があるか | あり | CJKV IME、edit フィールド、custom `InputConnection`、`TYPE_VIEW_TEXT_CHANGED` を処理する AccessibilityService などの API 利用条件がある。 |
| Compat Change ID が関係するか | 未確認 | Android 17 タグと Compat framework の根拠が未確認。 |

### 調査日（Investigation Date）

2026-06-10

### 信頼度

- 低

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] Android 17 上の全アプリ（targetSdkVersion に依存しない）
- [ ] Android 17 以上で targetSdkVersion >= 37
- [ ] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [x] 未確認 / 追加根拠が必要

必要な実行時条件:
- Android バージョン: Android 17 以上が前提と考えられるが、AOSP タグは未取得。
- targetSdkVersion: standard `TextView` の既定有効化については、公式文書上 targetSdkVersion 37 以上。
- 端末/フォームファクター: 物理キーボード入力と IME 変換中テキストが関係するが、端末形態条件は公式抜粋では明示されていない。
- 権限/API/コンポーネント条件: CJKV IME、edit フィールド、custom `InputConnection`、`AccessibilityEvent`、`TextAttribute`、AccessibilityService の `TYPE_VIEW_TEXT_CHANGED` 処理。
- アプリ状態/プロセス条件: 変換中テキスト / candidate selection / commit を伴う入力中。

Compat framework:
- Change ID: 未確認
- 変更名: 未確認
- default state: 未確認
- テスト時の切り替え可否: 未確認

分類信頼度:
- 低

分類根拠:
- Official documentation page: `behavior-changes-17`
- 検証対象の適用条件文: standard `TextView` を使う targetSdkVersion 37 以上のアプリでは既定有効。
- AOSP targetSdk 適用ゲート: 未確認。ローカルの `frameworks-base` に `android-17*` タグがない。
- Compat framework エントリ: 未確認。Android 17 Compat framework の根拠が未取得。

---

# エグゼクティブサマリー

Android 17 では、CJKV 言語の IME 入力中に、変換候補の選択や変換中テキスト / commit の違いをアクセシビリティサービスへ伝えるための `AccessibilityEvent` と `TextAttribute` API が追加される、と公式文書は説明している。目的は、スクリーンリーダーが複雑な IME 物理キーボード入力に対して、より正確な読み上げフィードバックを行えるようにすることである。

通常の `TextView` を使う targetSdkVersion 37 以上のアプリでは、この機能が既定で有効になるとされている。一方、custom `InputConnection` を持つ edit フィールドや IME、AccessibilityService は、必要に応じて新 API の利用・処理を実装する必要がある。

ただし、現時点のローカルの `frameworks-base` には Android 17 AOSP タグがないため、実装差分、targetSdkVersion 適用ゲート、Compat Change ID、default state は未確認である。

---

# 公式ドキュメント確認

## 原文（Statement）

Page title:
- Behavior changes: Apps targeting Android 17 or higher

Page URL:
- https://developer.android.com/about/versions/17/behavior-changes-17

Page type:
- Android 17 を対象とするアプリ

Section title:
- 複雑な IME 物理キーボード入力のアクセシビリティ対応

検証対象の原文:

> 新しい `AccessibilityEvent` API と `TextAttribute` API

提供された公式文書の抜粋は、これらの API が CJKV 言語入力に対するスクリーンリーダーのフィードバックを改善すると説明している。また、CJKV IME は候補選択を通知でき、編集フィールドを持つアプリはテキスト変更の種類を指定でき、標準の `TextView` を使う targetSdkVersion 37 アプリではこの挙動がデフォルトで有効になると説明している。

## 解釈

この変更は、CJKV 入力の変換中テキスト中に「変換候補が選択されたか」「変更が変換中テキスト中か commit か」といった意味情報を、IME、edit フィールド、AccessibilityService の間で受け渡すための変更である。

互換性リスクというより、アクセシビリティ品質向上のための挙動 / API adoption 項目である。ただし、standard `TextView` を使う targetSdkVersion 37 以上のアプリでは既定でイベント内容が変わるため、スクリーンリーダー連携や独自アクセシビリティイベント送信を持つアプリでは確認が必要になる。

---

# 変更内容

公式文書上の変更点:
- CJKV language input のスクリーンリーダー読み上げを改善するため、`AccessibilityEvent` と `TextAttribute` の API が追加される。
- IME は `TextAttribute.Builder.setTextSuggestionSelected()` で、変換中テキスト中に特定の変換候補が選択されたかを示せる。
- custom `InputConnection` を持つ edit フィールドは `TextAttribute.isTextSuggestionSelected()` で候補選択情報を取得できる。
- edit フィールドを持つアプリは `TYPE_VIEW_TEXT_CHANGED` dispatch 時に `AccessibilityEvent.setTextChangeTypes()` を呼び、変換中テキスト中の変更か commit 由来の変更かを示せる。
- AccessibilityService は `AccessibilityEvent.getTextChangeTypes()` で変更種別を読み取り、読み上げ戦略を調整できる。
- targetSdkVersion 37 以上で standard `TextView` を使うアプリでは、TextView が IME からの data retrieval と accessibility event の text 変更 type 設定を既定で処理すると説明されている。

AOSP で未確認の点:
- Android 16 基準挙動にこれらの API / event フィールド / TextView default handling が存在しなかったこと。
- Android 17 で追加された API surface と implementation diff。
- `TextView` の targetSdkVersion 37 適用ゲートの実装箇所。
- custom `InputConnection`、IME、AccessibilityService に対する targetSdkVersion 条件の有無。
- Compat Change ID と default state。

## 適用条件（Applicability）

公式文書の一次判断では、standard `TextView` の既定処理は Android 17 / targetSdkVersion 37 以上 / TextView 使用時に適用される。IME、custom edit フィールド、AccessibilityService については、新 API を利用するかどうかが追加条件になる。AOSP タグが未取得のため、確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

### OS アップデート時の挙動

- Android 17 にアップデートしただけで適用されるか: 未確認
- targetSdkVersion に依存しない根拠: なし。公式文書は targetSdkVersion 37 以上向けページで、standard `TextView` の既定有効化も targetSdkVersion 37 以上と述べる。
- Android 16 以前での挙動: AOSP タグ比較は未実施。Android 16 基準挙動 source は Android 17 タグとの比較ができないため、この調査では platform 根拠として採用していない。

### targetSdkVersion 37 以上での挙動

- targetSdkVersion 37 以上で適用されるか: standard `TextView` については公式文書上 Yes と読めるが、AOSP 適用ゲートは未確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: 未確認。公式文書は Android 17 挙動変更として説明しているため、Android 17 platform の挙動として扱う。
- opt-out / temporary override の有無: 未確認。Compat framework の根拠は未確認。

### その他の条件

- 端末/フォームファクター: 物理キーボード入力と関係するが、特定フォームファクターは公式抜粋では明示なし。
- 権限: 公式抜粋では条件なし。
- API 使用: `TextAttribute.Builder.setTextSuggestionSelected()`、`TextAttribute.isTextSuggestionSelected()`、`AccessibilityEvent.setTextChangeTypes()`、`AccessibilityEvent.getTextChangeTypes()`、`TYPE_VIEW_TEXT_CHANGED`。
- manifest attribute: 未確認。
- コンポーネント境界: IME アプリ、edit フィールドを持つアプリ、AccessibilityService の三者にまたがる。

---

# AOSP 調査

## checkout 状態

根拠利用前に確認したコマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list 'android-17*'
```

結果:
- `frameworks-base` 作業ツリー: 調査時点で clean。
- From タグ: `android-16.0.0_r4` は存在する。
- To タグ: ローカルに `android-17*` タグは存在しない。

根拠上の制約:
- Android 17 AOSP タグがローカルの `frameworks-base` に存在しないため、`git -C frameworks-base diff android-16.0.0_r4 <android-17-tag> -- ...` による明示的なタグ比較を実行できない。
- Repository rule に従い、Android 17 作業ツリーや推測によるソース根拠は採用しない。
- この制約により、AOSP に基づく結論は高信頼度にできない。

## 関連ファイル

未確認。Android 17 AOSP タグ取得後に、少なくとも以下の候補をタグ比較で確認する必要がある。

- `core/java/android/view/accessibility/AccessibilityEvent.java`
- `core/java/android/view/inputmethod/TextAttribute.java`
- `core/java/android/widget/TextView.java`
- `core/java/android/view/inputmethod/InputConnection.java`
- `core/java/android/view/inputmethod/BaseInputConnection.java`
- Compat framework 定義ファイル内の `TextView` / `AccessibilityEvent` / `TextAttribute` / text 変更 type 関連 Change ID

## 確認したソース文脈

Android 17 AOSP タグがないため、ソース文脈は未レビュー。

| ファイル / シンボル | Android 16 基準挙動 | Android 17 挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| 未レビュー | 未レビュー | 未レビュー | Android 17 タグがないため、公式文書の記述を AOSP 差分で検証できない。 |

必須記入項目:
- 入口 / 呼び出し元: 未確認。想定される入口は、IME から edit フィールドへの composing text 設定、`TextView` の accessibility event dispatch、AccessibilityService の `TYPE_VIEW_TEXT_CHANGED` processing だが、AOSP 根拠としては未採用。
- Relevant class or service responsibility: 未確認。
- アプリ API またはシステムイベントから変更箇所までの実行時パス: 未確認。
- 除外した無関係なコードパス: Android 17 タグ不在のため、ソースパスの採否判断自体を保留。

## 差分解釈

| 確認した差分 | 解釈 | 挙動変更との関係 | 信頼度 |
| --- | --- | --- | --- |
| Android 17 タグ間差分は利用不可 | ソース差分の種別はまだ分類できない | 公式文書の API 追加と TextView default handling をソース差分で裏取りできていない | 低 |

必須分類:
- Added behavior: 未確認。
- Removed behavior: 未確認。
- Changed condition / gate: 未確認。
- Changed default: 未確認。
- No behavior change found: 未確認。タグ不在のため「no behavior change」とは判断しない。

## 事実

事実:
- 公式文書は、CJKV language input の screen reader spoken feedback を改善するため、`AccessibilityEvent` と `TextAttribute` API を導入すると述べている。
- 公式文書は、CJKV IME が `TextAttribute.Builder.setTextSuggestionSelected()` で conversion candidate の選択状態を示せると述べている。
- 公式文書は、custom `InputConnection` を持つ edit フィールドが `TextAttribute.isTextSuggestionSelected()` で candidate selection data を取得できると述べている。
- 公式文書は、アプリで edit フィールドが `AccessibilityEvent.setTextChangeTypes()` を使って `TYPE_VIEW_TEXT_CHANGED` の text 変更 type を指定できると述べている。
- 公式文書は、targetSdkVersion 37 以上かつ standard `TextView` を使うアプリではこの機能が既定で有効になると述べている。
- ローカルの `frameworks-base` には `android-16.0.0_r4` タグがある。
- ローカルの `frameworks-base` には `android-17*` タグがない。
- 調査時点で `frameworks-base` 作業ツリーは clean。

観察:
- 公式ページ種別は targetSdkVersion 37 以上向けである。
- この項目は API 追加と framework default 挙動の両方を含む。
- standard `TextView` の既定有効化は targetSdkVersion 37 条件があると読める。
- IME、custom edit フィールド、AccessibilityService は、新 API を採用するかどうかが影響条件になる。
- AOSP タグがないため、実装が本当に targetSdkVersion 37 適用ゲートで制御されているかは未確認。
- Compat framework エントリの有無も未確認。

仮説:
- Android 17 / targetSdkVersion 37 の standard `TextView` では、IME から渡された `TextAttribute` を読み取り、`TYPE_VIEW_TEXT_CHANGED` に適切な text 変更 type を設定する可能性が高い。
- targetSdkVersion 36 の standard `TextView` では旧イベント形式が維持される可能性があるが、AOSP 適用ゲートが未確認のため断定しない。
- custom `InputConnection` を持つアプリでは、targetSdkVersion に関係なく API を明示的に利用しない限り、新しい feedback 改善が得られない可能性がある。

結論:
- 現時点で顧客向けに確定できるのは、「公式文書上は Android 17 / targetSdkVersion 37 以上の standard `TextView` で CJKV IME 入力のアクセシビリティイベントが改善される」という範囲まで。
- AOSP 適用ゲート、API surface diff、Compat framework default state が未確認のため、主分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

## 適用ゲート根拠

- targetSdkVersion 適用ゲート: 未確認。Android 17 AOSP タグがないため、`targetSdkVersion` / `ApplicationInfo.targetSdkVersion` 検索は実施していない。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。Android 17 AOSP タグがないため、`CompatChanges.isChangeEnabled` / `@ChangeId` / `@EnabledAfter` / `@EnabledSince` 検索は実施していない。
- @EnabledAfter / @EnabledSince / default state: 未確認。
- Build.VERSION / SDK_INT 適用ゲート: 未確認。
- DeviceConfig / resources 設定: 未確認。
- 権限/AppOps 適用ゲート: 未確認。
- Manifest/property 適用ゲート: 未確認。
- 適用ゲート未検出: 未判断。検索不能のため「適用ゲートなし」とは扱わない。
- 適用ゲートの結論: 未確認。公式文書上の targetSdkVersion 37 条件と API 使用条件はあるが、AOSP 根拠が不足している。
- ソース文脈からの推論: ソース文脈未取得のため不可。

確認済み:
- `frameworks-base` checkout 状態。
- `android-16.0.0_r4` タグの存在。
- `android-17*` タグの存在。

未確認:
- Android 17 implementation files。
- Android 17 Compat framework definitions。
- Android 17 API surface files。

理由:
- Android 17 target タグがローカル checkout に存在しないため、タグ間差分による platform 根拠が作れない。

---

# 影響分析

## 影響を受けるアプリ

影響または対応機会があるアプリ:
- CJKV language input を扱う IME アプリ。
- custom `InputConnection` を持つ edit フィールドを実装しているアプリ。
- `TextView` ではなく独自 edit フィールド / custom text エディタを持つアプリ。
- `TYPE_VIEW_TEXT_CHANGED` を明示的に dispatch しているアプリ。
- `TYPE_VIEW_TEXT_CHANGED` を処理して読み上げや入力フィードバックを調整する AccessibilityService。
- targetSdkVersion 37 以上で standard `TextView` を使うアプリ。

## 影響を受けにくいアプリ

影響が限定的と考えられるケース:
- CJKV IME 変換中テキスト / 物理キーボード入力と関係しない入力フローのみを持つアプリ。
- standard `TextView` の既定処理に任せており、独自アクセシビリティイベントや custom `InputConnection` を持たないアプリ。
- AccessibilityService でも IME でもなく、text 変更された accessibility event を直接扱わないアプリ。
- targetSdkVersion 37 へ上げないアプリ。ただし、これは公式文書からの一次判断であり、AOSP 適用ゲートは未確認。

---

# 顧客影響

## 影響度

- Human decision required

※ 最終 severity / priority は人間が判断する。このレポートでは確定しない。

## ビジネス影響

- ユーザー影響: CJKV 入力中のスクリーンリーダー読み上げがより正確になり、候補選択、変換中テキスト、commit の違いが伝わりやすくなる可能性がある。
- 運用影響: IME、custom エディタ、AccessibilityService を提供している場合、Android 17 対応として API adoption と読み上げ挙動の検証が必要になる。
- 開発影響: standard `TextView` では既定対応される可能性がある一方、custom `InputConnection` / custom accessibility event dispatch では明示的な実装が必要。

---

# サービス影響例

このセクションは、公式文書と AOSP 根拠 から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: 物理キーボードを使う業務入力アプリ

- 対象サービス例: POS、倉庫管理、医療・金融の業務入力、Chromebook / tablet キーボード利用アプリ。
- 影響を受ける実装パターン: complex IME 変換中テキストと物理キーボード input を前提にした text フィールド / shortcut handling。
- 発生条件: Android 17 / targetSdkVersion 37 で accessibility support と IME 物理キーボード入力の挙動が変わる場合。
- ユーザーに見える症状: 日本語入力、変換、候補選択、アクセシビリティ読み上げとの組み合わせで入力体験が変わる可能性。
- 開発・運用への影響: 外部キーボード、IME、accessibility service を組み合わせた QA が必要になる可能性。
- 推奨対応候補: key event を直接消費しすぎない、standard text input を利用する、IME 変換中テキストのテストを追加する。
- 根拠: 公式 Behavior Change 文書の記述と、レポートの AOSP 根拠上の制約。
- 信頼度: 低
- 注意: 具体的な IME / accessibility service 別の挙動は未検証。

## 例2（Example 2）: アクセシビリティ利用者向けの入力支援機能

- 対象サービス例: メモ、チャット、文書編集、教育アプリ。
- 影響を受ける実装パターン: accessibility focus、screen reader、hardware キーボード shortcut、IME composing text が同時に動く UI。
- 発生条件: 物理キーボード入力と accessibility support の platform 挙動が Android 17 で変わる場合。
- ユーザーに見える症状: 入力中の読み上げ、候補操作、カーソル移動の体感が変わる可能性。
- 開発・運用への影響: TalkBack / 物理キーボード / major IME の組み合わせ検証が必要になる可能性。
- 推奨対応候補: accessibility node / text selection 状態を標準 API と整合させ、custom key handling を限定する。
- 根拠: 公式文書の記述とレポートのソース根拠未確認事項。
- 信頼度: 低
- 注意: 実利用者への影響度は human decision と実機評価が必要。

---

# 対応候補

## 必須対応（Must）

- custom `InputConnection` を持つ edit フィールドがあるか確認する。
- 独自に `TYPE_VIEW_TEXT_CHANGED` を dispatch している箇所があるか確認する。
- CJKV IME、custom エディタ、AccessibilityService を提供している場合、Android 17 / targetSdkVersion 37 の入力・読み上げテストを計画する。

## 推奨対応（Recommended）

- IME アプリは、composing text 設定時に `TextAttribute.Builder.setTextSuggestionSelected()` を使えるか検討する。
- custom edit フィールドは `TextAttribute.isTextSuggestionSelected()` を読み取り、`AccessibilityEvent.setTextChangeTypes()` で text 変更 type を設定する設計を検討する。
- AccessibilityService は `AccessibilityEvent.getTextChangeTypes()` を読み取り、変換中テキスト / commit / candidate selection に応じた feedback strategy を検討する。
- standard `TextView` を使うアプリでも、targetSdkVersion 37 更新時に CJKV 入力とスクリーンリーダーの回帰テストを行う。

## 任意対応（Optional）

- Android 17 AOSP タグ公開後、`TextView` default handling、API surface、Compat Change ID を再調査する。
- CJKV 以外の IME や software キーボード入力で副作用がないか smoke test を行う。

---

# 検証方法

## 検証マトリクス

| 端末 OS | targetSdkVersion | Compat flag | 期待される挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | デフォルト | Android 16 基準挙動。新 API / TextView default handling の有無は Android 17 タグ比較待ち。 |
| Android 17 | 36 | デフォルト | 未確認。standard `TextView` の既定有効化は targetSdkVersion 37 条件と読めるが、AOSP 適用ゲートは未確認。 |
| Android 17 | 37 | デフォルト | 公式文書上は standard `TextView` が IME data retrieval と text 変更 type 設定を既定で処理する。 |
| Android 17 | 36 | force-有効 if 利用可能 | 未確認。Compat Change ID は未確認。 |
| Android 17 | 37 | force-無効 if 利用可能 | 未確認。Compat Change ID は未確認。 |

## 手順

- targetSdk 変更: テストアプリを targetSdkVersion 36 と 37 で build し、Android 17 上の standard `TextView` と custom edit フィールドの差を確認する。
- Compat framework コマンド: Change ID 未確認のため未定。Android 17 タグ / compat page 確認後に追加する。
- テスト方法: CJKV IME、物理キーボード、standard `TextView`、custom `InputConnection`、AccessibilityService を組み合わせる。
- 再現手順: 変換中テキスト中の candidate selection と commit を行い、`TYPE_VIEW_TEXT_CHANGED` の text 変更 type とスクリーンリーダー読み上げを記録する。
- 期待結果: targetSdkVersion 37 の standard `TextView` では、公式文書どおり text 変更 type が設定され、AccessibilityService が変更種別を識別できる。targetSdkVersion 36 の結果は AOSP 適用ゲート確認待ち。

---

# 結論

公式文書は、Android 17 で CJKV IME の複雑な物理キーボード入力に対するアクセシビリティフィードバックを改善するため、`AccessibilityEvent` と `TextAttribute` の API と standard `TextView` の既定処理を導入すると説明している。影響範囲は、IME、custom edit フィールド、AccessibilityService、targetSdkVersion 37 以上の standard `TextView` 利用アプリに分かれる。

一方で、ローカルの `frameworks-base` に Android 17 AOSP タグがないため、実装差分、targetSdkVersion 適用ゲート、API surface diff、Compat Change ID、default state を検証できていない。現時点の主分類は `UNKNOWN_NEEDS_MORE_EVIDENCE`、信頼度は低とする。

人間の判断欄:
- Final priority: Human decision required
- Final severity: Human decision required
- Release readiness: Human decision required
- Customer communication priority: Human decision required
- Next required human decision: Android 17 AOSP タグ公開後に再調査するか、公式 documentation ベースの暫定 adoption ガイダンスとして扱うかを判断する。

# 複雑な IME 物理キーボード入力のアクセシビリティ対応

## 基本情報

### 調査対象 Android バージョン

比較元:
- android-16.0.0_r4

比較先:
- TBD: Android 17 AOSP タグ

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

### Behavior Change 文書

文書:
https://developer.android.com/about/versions/17/behavior-changes-17

関連文書:
- https://developer.android.com/reference/android/view/accessibility/AccessibilityEvent
- https://developer.android.com/reference/android/view/inputmethod/TextAttribute

セクション:
Accessibility support of complex IME physical keyboard typing

ページ種別:
- Apps targeting Android 17 or higher

### 分類スナップショット

主分類（Primary classification）:
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- 公式ドキュメントでは、Android 17 および `targetSdkVersion 37` 以上を対象としたページで説明されている。
- `TextView` を使用する `targetSdkVersion 37` 以上のアプリでは、IME から candidate selection data を取得し、アクセシビリティイベントの text change type を設定する動作がデフォルトで有効になると記載されている。
- ただし、手元の `frameworks-base` には Android 17 の AOSP タグが存在しないため、AOSP 上での実装有無、API surface、Compat Change ID、およびデフォルト状態は未確認である。そのため、現時点での分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

早見表:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 未確認 | 公式ドキュメントでは `targetSdkVersion 37` 以上を対象としているが、IME・AccessibilityService・独自実装の `InputConnection` などの利用条件も関係するため、現時点では断定できない。AOSP 上での適用条件は未確認。 |
| `targetSdkVersion 37` 以上が必要か | 条件付きと考えられるが未確認 | 公式ドキュメントでは、標準の `TextView` について Android 17 をターゲットとするアプリで既定有効になると説明されている。ただし、AOSP 上の実装根拠は未確認である。 |
| 追加の実行時条件があるか | ある | CJKV 系 IME、編集可能なテキストフィールド、独自の `InputConnection` 実装、`TYPE_VIEW_TEXT_CHANGED` を処理する AccessibilityService など、関連 API や実装条件が存在する。 |
| Compat Change ID が関係するか | 未確認 | Android 17 の AOSP タグおよび Compat Framework 上の根拠を確認できていないため、現時点では不明である。 |

### 調査日

2026-06-10

### 信頼度

- 低

### 適用条件分類

適用される条件:

- [ ] Android 17 上の全アプリ（targetSdkVersion に依存しない）
- [ ] Android 17 以上で targetSdkVersion >= 37
- [ ] targetSdkVersion 37 以上かつ追加の実行時条件を満たす場合に適用
- [ ] Mainline / Google Play system update に依存
- [ ] API 追加のみであり、挙動変更ではない
- [x] 未確認 / 追加根拠が必要

必要な実行時条件:

- Android version: Android 17 以上が前提と考えられるが、AOSP タグ未取得のため未確認。
- targetSdkVersion: 標準 `TextView` の既定有効化については、公式ドキュメント上 `targetSdkVersion 37` 以上が対象とされている。
- Device/form factor: 物理キーボード入力や IME の変換処理が関係するが、端末種別やフォームファクタに関する条件は公式抜粋では明示されていない。
- Permission/API/component condition: CJKV IME、編集可能なテキストフィールド、独自実装の `InputConnection`、`AccessibilityEvent`、`TextAttribute`、および `TYPE_VIEW_TEXT_CHANGED` を処理する AccessibilityService が関係する。
- App state/process condition: テキスト入力中であり、文字変換・候補選択・確定入力を伴う状態。

Compat framework:

- Change ID: 未確認
- 変更名: 未確認
- 既定状態: 未確認
- テスト時の切り替え可否: 未確認

分類信頼度:

- 低

分類根拠:

- 公式ドキュメントページ: `behavior-changes-17`
- 検証対象の適用条件文: 標準 `TextView` を使用する `targetSdkVersion 37` 以上のアプリでは既定で有効になると記載されている。
- AOSP targetSdk gate: 未確認。手元の `frameworks-base` に `android-17*` タグが存在しない。
- Compat framework entry: 未確認。Android 17 の Compat Framework に関する根拠は取得できていない。

---

# エグゼクティブサマリー

Android 17 では、CJKV 言語向け IME の入力中に、変換候補の選択や composition と commit の違いをアクセシビリティサービスへ伝えるための `AccessibilityEvent` および `TextAttribute` API が追加されると、公式ドキュメントで説明されている。これにより、スクリーンリーダーは IME を利用した複雑な物理キーボード入力に対して、より正確な読み上げフィードバックを提供できるようになる。

標準の `TextView` を使用する `targetSdkVersion 37` 以上のアプリでは、この機能が既定で有効になるとされている。一方で、独自の `InputConnection` を実装した編集フィールド、IME、AccessibilityService については、必要に応じて新しい API の利用や対応実装が求められる。

ただし、現時点では手元の `frameworks-base` に Android 17 の AOSP タグが存在しないため、実際の実装差分、`targetSdkVersion` による適用条件、Compat Change ID、およびデフォルト状態については確認できていない。

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

> new AccessibilityEvent and TextAttribute APIs

提供された公式文書の抜粋は、これらの API により CJKV 言語入力時のスクリーンリーダーのフィードバックが改善されると説明している。また、CJKV IME は候補選択状態を通知でき、編集フィールドを持つアプリは text change type を指定でき、標準 `TextView` を使用する targetSdkVersion 37 以上のアプリではこの挙動が既定で有効になると説明している。

## 解釈

この変更は、CJKV 入力の composition 中に「変換候補が選択されたか」「変更が composition 中か commit か」といった意味情報を、IME、edit field、AccessibilityService の間で受け渡すための変更である。

互換性リスクというより、アクセシビリティ品質向上のための behavior / API adoption 項目である。ただし、標準 `TextView` を使う targetSdkVersion 37 以上のアプリでは既定でイベント内容が変わるため、スクリーンリーダー連携や独自アクセシビリティイベント送信を持つアプリでは確認が必要になる。

---

# 変更内容

公式ドキュメント上の変更点:

- CJKV 言語入力時のスクリーンリーダーによる読み上げ精度を向上させるため、`AccessibilityEvent` および `TextAttribute` に関連する API が追加される。
- IME は `TextAttribute.Builder.setTextSuggestionSelected()` を利用して、変換中に特定の候補が選択されていることを示せる。
- 独自の `InputConnection` を実装した編集フィールドは、`TextAttribute.isTextSuggestionSelected()` を利用して候補選択情報を取得できる。
- 編集フィールドを持つアプリは、`TYPE_VIEW_TEXT_CHANGED` を送出する際に `AccessibilityEvent.setTextChangeTypes()` を呼び出し、その変更が変換中の更新なのか、確定入力による変更なのかを示せる。
- AccessibilityService は `AccessibilityEvent.getTextChangeTypes()` を利用して変更種別を取得し、読み上げ方法を調整できる。
- `targetSdkVersion 37` 以上で標準の `TextView` を利用するアプリでは、IME からのデータ取得およびアクセシビリティイベントへの text change type 設定を `TextView` が既定で処理すると説明されている。

AOSP で未確認の点:

- Android 16 時点で、これらの API・イベントフィールド・`TextView` の既定処理が存在していなかったこと。
- Android 17 で追加された API surface および実装差分。
- `TextView` における `targetSdkVersion 37` 条件の実装箇所。
- 独自の `InputConnection` 実装、IME、AccessibilityService に対して `targetSdkVersion` 条件が存在するかどうか。
- Compat Change ID およびデフォルト状態。

## 適用条件（Applicability）

公式ドキュメントの記載からは、標準 `TextView` による既定処理は Android 17・`targetSdkVersion 37` 以上・`TextView` 利用時に適用されると考えられる。一方で、IME、独自実装の編集フィールド、AccessibilityService については、新しい API を利用するかどうかが追加条件となる。

ただし、Android 17 の AOSP タグを確認できていないため、現時点での確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

### OS アップデート時の挙動

- Android 17 にアップデートしただけで適用されるか: 未確認
- targetSdkVersion に依存しない根拠: なし。公式ドキュメントは `targetSdkVersion 37` 以上を対象としたページであり、標準 `TextView` の既定有効化についても `targetSdkVersion 37` 以上が条件と記載されている。
- Android 16 以前での挙動: AOSP タグ間の比較を実施できていない。Android 16 のソースのみでは Android 17 との差分を確認できないため、本調査ではプラットフォーム根拠として採用していない。

### targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- `targetSdkVersion 37` 以上で適用されるか: 標準 `TextView` については、公式ドキュメントの記載から Yes と解釈できるが、AOSP 上の適用条件は未確認。
- Android 17 以外で `targetSdkVersion 37` を指定した場合の挙動: 未確認。公式ドキュメントでは Android 17 の Behavior Changes として説明されているため、Android 17 のプラットフォーム変更として扱う。
- opt-out / temporary override の有無: 未確認。Compat Framework に関する根拠を確認できていない。

### その他の条件

- Device/form factor: 物理キーボード入力との関連はあるが、特定のフォームファクタに限定されるという記載はない。
- Permission: 公式ドキュメントの抜粋では特別な権限要件は示されていない。
- API usage:
  - `TextAttribute.Builder.setTextSuggestionSelected()`
  - `TextAttribute.isTextSuggestionSelected()`
  - `AccessibilityEvent.setTextChangeTypes()`
  - `AccessibilityEvent.getTextChangeTypes()`
  - `TYPE_VIEW_TEXT_CHANGED`
- Manifest attribute: 未確認
- Component boundary: IME アプリ、編集フィールドを持つアプリ、AccessibilityService の三者にまたがる変更である。

---

# AOSP 調査

## checkout 状態

根拠を採用する前に確認したコマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list 'android-17*'
```

結果:

- `frameworks-base` のワーキングツリーは、調査時点でクリーンな状態だった。

- 比較元タグとして `android-16.0.0_r4` の存在を確認した。

- ローカル環境には `android-17*` に一致するタグが存在しなかった。


根拠上の制約:

- Android 17 の AOSP タグがローカルの `frameworks-base` に存在しないため、`git -C frameworks-base diff android-16.0.0_r4 <android-17-tag> -- ...` のような明示的なタグ比較を実施できない。

- リポジトリ調査ルールに従い、Android 17 のワーキングツリーや推測に基づくソースコード根拠は採用しない。

- この制約により、AOSP に基づく結論の信頼度を High とすることはできない。


## 関連ファイル

未確認。Android 17 の AOSP タグ取得後、少なくとも以下のファイルについてタグ間比較を実施する必要がある。

- `core/java/android/view/accessibility/AccessibilityEvent.java`
- `core/java/android/view/inputmethod/TextAttribute.java`
- `core/java/android/widget/TextView.java`
- `core/java/android/view/inputmethod/InputConnection.java`
- `core/java/android/view/inputmethod/BaseInputConnection.java`
- Compat Framework 定義ファイル内の TextView、AccessibilityEvent、TextAttribute、text change type 関連の Change ID 定義

## 確認したソース文脈

Android 17 の AOSP タグが存在しないため、ソースコード上の文脈確認は未実施。

| ファイル / シンボル | Android 16 基準挙動 | Android 17 挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| 未レビュー | 未レビュー | 未レビュー | Android 17 のタグが存在しないため、公式ドキュメントの記載内容を AOSP の差分で検証できていない。 |

必須記入項目:

- Entry point / caller: 未確認。想定されるエントリポイントとしては、IME から編集フィールドへの composing text 設定、`TextView` によるアクセシビリティイベント送出、および AccessibilityService における `TYPE_VIEW_TEXT_CHANGED` の処理が考えられるが、AOSP による裏付けは取得できていない。
- Relevant class or service responsibility: 未確認。
- Runtime path from app API / system event to changed code: 未確認。
- 除外した無関係なコードパス: Android 17 のタグが存在しないため、どのソースパスを採用・除外すべきかの判断自体を保留している。

## 差分解釈

| 確認した差分 | 解釈 | 挙動変更との関係 | 信頼度 |
| --- | --- | --- | --- |
| Android 17 のタグ差分を取得できていない | ソースコード差分の種類を現時点では分類できない | 公式ドキュメントで説明されている API 追加および `TextView` の既定処理をソースコード差分で裏付けできていない | 低 |

必須分類:

- Added behavior: 未確認。
- Removed behavior: 未確認。
- Changed condition / gate: 未確認。
- Changed default: 未確認。
- No behavior change found: 未確認。Android 17 のタグが存在しないため、「Behavior Change ではない」と結論付けることはできない。

## 事実

事実:

- 公式ドキュメントでは、CJKV 言語入力時のスクリーンリーダーによる読み上げ品質を向上させるため、`AccessibilityEvent` および `TextAttribute` に関する API が導入されると説明されている。
- 公式ドキュメントでは、CJKV IME が `TextAttribute.Builder.setTextSuggestionSelected()` を利用して、変換候補の選択状態を示せると説明されている。
- 公式ドキュメントでは、独自の `InputConnection` を持つ編集フィールドが `TextAttribute.isTextSuggestionSelected()` を利用して候補選択情報を取得できると説明されている。
- 公式ドキュメントでは、編集フィールドを持つアプリが `AccessibilityEvent.setTextChangeTypes()` を利用して、`TYPE_VIEW_TEXT_CHANGED` イベントの text change type を指定できると説明されている。
- 公式ドキュメントでは、`targetSdkVersion 37` 以上かつ標準 `TextView` を利用するアプリでは、この機能が既定で有効になると説明されている。
- ローカルの `frameworks-base` には `android-16.0.0_r4` タグが存在する。
- ローカルの `frameworks-base` には `android-17*` タグが存在しない。
- 調査時点で `frameworks-base` のワーキングツリーはクリーンな状態だった。

観察:

- 対象の公式ページは `targetSdkVersion 37` 以上のアプリ向け Behavior Changes ページである。
- この変更は API の追加とフレームワーク側の既定動作変更の両方を含んでいる。
- 標準 `TextView` の既定有効化には `targetSdkVersion 37` が条件として存在すると解釈できる。
- IME、独自実装の編集フィールド、AccessibilityService については、新 API を採用するかどうかが適用条件となる。
- Android 17 の AOSP タグが存在しないため、実際に `targetSdkVersion 37` による制御が行われているかは確認できていない。
- Compat Framework による制御が存在するかどうかも未確認である。

仮説:

- Android 17 かつ `targetSdkVersion 37` の標準 `TextView` では、IME から渡された `TextAttribute` を解釈し、`TYPE_VIEW_TEXT_CHANGED` イベントへ適切な text change type を設定する可能性が高い。
- `targetSdkVersion 36` 以下の標準 `TextView` では従来のイベント形式が維持される可能性があるが、AOSP 上の適用条件を確認できていないため断定はできない。
- 独自の `InputConnection` を実装しているアプリでは、`targetSdkVersion` に関係なく新 API を明示的に利用しない限り、このアクセシビリティ改善の恩恵を受けられない可能性がある。

## 結論

結論:

- 現時点で顧客向けに確定して説明できるのは、「公式ドキュメント上では、Android 17 かつ `targetSdkVersion 37` 以上の標準 `TextView` において、CJKV IME 入力時のアクセシビリティイベント処理が改善される」とされている点までである。
- AOSP 上での適用条件、API surface の差分、Compat Framework におけるデフォルト状態を確認できていないため、最終的な分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

## 適用ゲート根拠

- targetSdkVersion 適用ゲート: 未確認。Android 17 の AOSP タグが存在しないため、`targetSdkVersion` や `ApplicationInfo.targetSdkVersion` に関する検索は実施していない。
- CompatChanges.isChangeEnabled / Change ID: 未確認。Android 17 の AOSP タグが存在しないため、`CompatChanges.isChangeEnabled`、`@ChangeId`、`@EnabledAfter`、`@EnabledSince` に関する検索は実施していない。
- @EnabledAfter / @EnabledSince / default state: 未確認。
- Build.VERSION / SDK_INT 適用ゲート: 未確認。
- DeviceConfig / resources config: 未確認。
- Permission/AppOps 適用ゲート: 未確認。
- Manifest/property 適用ゲート: 未確認。
- 適用ゲート未検出: 未判断。必要な検索を実施できていないため、「ゲートが存在しない」とは判断しない。
- 適用ゲートの結論: 未確認。公式ドキュメント上は `targetSdkVersion 37` 条件および API 利用条件が示されているが、AOSP による裏付けは取得できていない。
- ソース文脈からの推論: ソースコード上の文脈を確認できていないため評価不可。

確認済み:

- `frameworks-base` の checkout 状態
- `android-16.0.0_r4` タグの存在
- `android-17*` タグの存在

未確認:

- Android 17 の実装ファイル
- Android 17 の Compat Framework 定義
- Android 17 の API surface 定義ファイル

理由:

- ローカル環境に Android 17 のターゲットタグが存在しないため、タグ間差分によるプラットフォーム根拠を取得できない。

---

# 影響分析

## 影響を受けるアプリ

影響または対応機会があるアプリ:

- CJKV 言語入力を扱う IME アプリ。
- 独自の `InputConnection` を実装した編集フィールドを持つアプリ。
- 標準 `TextView` ではなく、独自の編集フィールドやカスタムテキストエディタを実装しているアプリ。
- `TYPE_VIEW_TEXT_CHANGED` イベントを明示的に送出しているアプリ。
- `TYPE_VIEW_TEXT_CHANGED` を処理し、読み上げや入力フィードバックを調整する AccessibilityService。
- `targetSdkVersion 37` 以上で標準 `TextView` を利用するアプリ。

## 影響を受けにくいアプリ

影響が限定的と考えられるケース:

- CJKV IME の変換処理や物理キーボード入力と関係しない入力フローのみを持つアプリ。
- 標準 `TextView` の既定動作に任せており、独自のアクセシビリティイベント処理や独自実装の `InputConnection` を持たないアプリ。
- AccessibilityService や IME ではなく、text changed 系のアクセシビリティイベントを直接扱わないアプリ。
- `targetSdkVersion 37` へ移行しないアプリ。ただし、これは公式ドキュメントに基づく一次判断であり、AOSP 上の適用条件は未確認である。

---

# 顧客影響

## 影響度

- 人間による判断が必要

※ 最終的な Severity や Priority は人間による判断が必要であり、本レポートでは確定しない。


## ビジネス影響

- ユーザー影響: CJKV 言語入力時のスクリーンリーダーによる読み上げ精度が向上し、変換候補の選択状態、composition 中の変更、確定入力による変更の違いがより適切に伝わる可能性がある。
- 運用影響: IME、独自エディタ、AccessibilityService を提供している場合は、Android 17 対応の一環として新 API の採用可否や読み上げ挙動の検証が必要になる可能性がある。
- 開発影響: 標準 `TextView` を利用している場合はフレームワーク側で対応される可能性がある一方、独自実装の `InputConnection` やアクセシビリティイベント送出処理を持つ場合は、明示的な対応実装が必要になる可能性がある。

---

# サービス影響例

このセクションは、公式ドキュメントおよび確認できた根拠から推測される影響例を示すものであり、特定サービスで実際に発生した事象を示すものではない。

## 例1: 物理キーボードを利用する業務入力アプリ

- 対象サービス例: POS システム、倉庫管理システム、医療・金融系業務システム、Chromebook やタブレット用キーボードを利用するアプリ。
- 影響を受ける実装パターン: IME による複雑な文字変換処理や物理キーボード入力を前提としたテキスト入力機能、ショートカットキー制御など。
- 発生条件: Android 17 かつ `targetSdkVersion 37` 環境で、IME の物理キーボード入力に対するアクセシビリティサポートの挙動が変更された場合。
- ユーザーに見える症状: 日本語入力中の変換候補選択や入力確定時に、スクリーンリーダーの読み上げ内容やタイミングが変化する可能性がある。
- 開発・運用への影響: 外部キーボード、IME、AccessibilityService を組み合わせた検証や回帰テストが必要になる可能性がある。
- 推奨対応候補:
  - キーイベントを過度に独自処理しない。
  - 可能な限り標準のテキスト入力コンポーネントを利用する。
  - IME の変換処理を含む入力テストケースを追加する。
- 根拠: 公式 Behavior Change の記載および、本レポートで整理した AOSP 調査上の制約事項。
- 信頼度: 低
- 注意: IME や AccessibilityService ごとの具体的な挙動差異については未検証である。

## 例2: アクセシビリティ利用者向けの入力支援機能

- 対象サービス例: メモアプリ、チャットアプリ、文書編集アプリ、教育系アプリ。
- 影響を受ける実装パターン: Accessibility Focus、スクリーンリーダー、ハードウェアキーボードショートカット、IME の composing text が同時に動作する UI。
- 発生条件: 物理キーボード入力とアクセシビリティサポートに関するプラットフォーム挙動が Android 17 で変更された場合。
- ユーザーに見える症状: 入力中の読み上げ内容、変換候補の操作、カーソル移動時のフィードバックなどの体感が変化する可能性がある。
- 開発・運用への影響: TalkBack、物理キーボード、主要 IME の組み合わせによる検証が必要になる可能性がある。
- 推奨対応候補:
  - Accessibility Node やテキスト選択状態を標準 API と整合させる。
  - 独自のキー入力処理は必要最小限に留める。
- 根拠: 公式ドキュメントの記載および、本レポートで整理した未確認事項。
- 信頼度: 低
- 注意: 実際の利用者への影響度は、個別の評価と実機検証による確認が必要である。

---

# 対応候補

## 必須対応（Must）

- 独自の `InputConnection` を実装した編集フィールドが存在するか確認する。
- 独自に `TYPE_VIEW_TEXT_CHANGED` を送出している箇所が存在するか確認する。
- CJKV IME、独自エディタ、AccessibilityService を提供している場合は、Android 17 および `targetSdkVersion 37` 環境での入力・読み上げテストを計画する。

## 推奨対応（Recommended）

- IME アプリは、composing text 設定時に `TextAttribute.Builder.setTextSuggestionSelected()` を利用できるか検討する。
- 独自の編集フィールドを実装している場合は、`TextAttribute.isTextSuggestionSelected()` の利用、および `AccessibilityEvent.setTextChangeTypes()` による text change type 設定を検討する。
- AccessibilityService は、`AccessibilityEvent.getTextChangeTypes()` を利用し、composition・commit・候補選択状態に応じたフィードバック戦略を検討する。
- 標準 `TextView` を利用しているアプリであっても、`targetSdkVersion 37` への移行時には CJKV 入力とスクリーンリーダーを組み合わせた回帰テストを実施する。

## 任意対応（Optional）

- Android 17 の AOSP タグ公開後に、`TextView` の既定処理、API surface の差分、および Compat Change ID を再調査する。
- CJKV 以外の IME やソフトウェアキーボード入力に対して、副作用が発生しないか簡易的なスモークテストを実施する。

---

# 検証方法

## 検証マトリクス

| 端末 OS | targetSdkVersion | Compat flag | 期待される挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | default | Android 16 のベースライン挙動。新 API や `TextView` の既定処理の有無は Android 17 とのタグ比較待ち。 |
| Android 17 | 36 | default | 未確認。標準 `TextView` の既定有効化は `targetSdkVersion 37` 条件と解釈できるが、AOSP 上の適用条件は未確認。 |
| Android 17 | 37 | default | 公式ドキュメント上では、標準 `TextView` が IME からのデータ取得および text change type の設定を既定で処理する。 |
| Android 17 | 36 | force-enabled（利用可能な場合） | 未確認。Compat Change ID が未確認。 |
| Android 17 | 37 | force-disabled（利用可能な場合） | 未確認。Compat Change ID が未確認。 |

## 手順

- targetSdk の変更:
  - テストアプリを `targetSdkVersion 36` と `targetSdkVersion 37` の両方でビルドする。
  - Android 17 上で標準 `TextView` と独自実装の編集フィールドの挙動差を確認する。

- Compat Framework コマンド:
  - Change ID が未確認のため現時点では未定。
  - Android 17 の AOSP タグまたは Compat Framework 情報を確認後に追加する。

- テスト方法:
  - CJKV IME
  - 物理キーボード
  - 標準 `TextView`
  - 独自実装の `InputConnection`
  - AccessibilityService

  上記の組み合わせで検証を実施する。

- 再現手順:
  - 文字入力中に変換候補を選択する。
  - composition 中の状態変化を発生させる。
  - 入力を確定（commit）する。
  - `TYPE_VIEW_TEXT_CHANGED` の text change type とスクリーンリーダーの読み上げ内容を記録する。

- 期待結果:
  - `targetSdkVersion 37` の標準 `TextView` では、公式ドキュメントどおり text change type が設定され、AccessibilityService が変更種別を識別できる。
  - `targetSdkVersion 36` の挙動については、AOSP 上の適用条件確認後に評価する。

---

# 結論

公式ドキュメントでは、Android 17 において CJKV IME の複雑な物理キーボード入力に対するアクセシビリティフィードバックを改善するため、`AccessibilityEvent` および `TextAttribute` に関する API と、標準 `TextView` の既定処理が導入されると説明されている。

影響範囲は大きく以下のカテゴリに分かれる。

- IME アプリ
- 独自実装の編集フィールド（custom edit field）
- AccessibilityService
- `targetSdkVersion 37` 以上で標準 `TextView` を利用するアプリ

一方で、ローカルの `frameworks-base` には Android 17 の AOSP タグが存在しないため、以下の項目をソースコードレベルで検証できていない。

- 実装差分
- `targetSdkVersion` による適用条件
- API surface の差分
- Compat Change ID
- デフォルト状態（default state）

そのため、本調査時点での分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とし、信頼度は低とする。

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
- Android 17 の AOSP タグ公開後に再調査を行うか。
- 公式ドキュメントを根拠とした暫定的な導入ガイダンスとして扱うかを判断する。

# 物理入力デバイスでのパスワード非表示

## 基本情報

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

Section:
物理入力デバイスでのパスワード非表示

Page type:
- Apps targeting Android 17 or higher

### 分類スナップショット

主分類（Primary classification）:
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- 公式文書は、targetSdkVersion 37 以上のアプリで、ユーザーが物理入力デバイスを使っている場合に `show_passwords_physical` setting がパスワードフィールドの全文字へ適用されると説明している。
- 追加条件として、パスワードフィールド、物理入力デバイス、touchscreen input の場合の `show_passwords_touch` 分岐がある。
- ただし、ローカルの `frameworks-base` に Android 17 AOSP タグがないため、AOSP 適用ゲート、setting implementation、入力デバイス判定、Compat Change ID、デフォルト状態は未検証である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

早見表:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 未確認 | 公式文書は targetSdkVersion 37+ を条件としているが、AOSP 適用ゲートは未確認。 |
| targetSdkVersion 37 以上が必要か | 可能性は高いが未確認 | 原文は Android 17 を対象とするアプリ / API level 37 or higher と述べている。 |
| 追加の実行時条件があるか | Yes | 物理入力デバイス使用中、パスワードフィールド、または touchscreen input による setting 分岐。 |
| Compat Change ID が関係するか | 未確認 | Android 17 タグと Compat framework 根拠が未確認。 |

### 調査日

2026-06-10

### 信頼度

- 低

### 適用条件分類

適用される条件（Applies when）:
- [ ] Android 17 上の全アプリ（targetSdkVersion に依存しない）
- [ ] Android 17 以上で targetSdkVersion >= 37
- [ ] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play システムアップデート dependent
- [ ] API addition only, not a behavior change
- [x] 未確認 / 追加根拠が必要

必要な実行時条件（必要な実行時条件）:
- Android バージョン: Android 17 以上が前提と考えられるが、AOSP タグは未取得。
- targetSdkVersion: 公式文書上は 37 以上。
- 端末/フォームファクター: 物理入力デバイス、例として external キーボード。大きな画面を伴う端末で shoulder surfing risk が高いと説明されている。
- 権限/API/コンポーネント条件: パスワードフィールド、パスワード visibility setting、input method / 入力デバイス判定。
- アプリ状態/プロセス条件: パスワードフィールドへの文字入力時。

Compat framework:
- 変更 ID: 未確認
- 変更 name: 未確認
- デフォルト状態: 未確認
- テスト時の切り替え可否: 未確認

分類信頼度:
- 低

分類根拠:
- Official documentation page: `behavior-changes-17`
- 検証対象の適用条件文: targetSdkVersion 37 以上、物理入力デバイス使用中、パスワードフィールド。
- AOSP targetSdk 適用ゲート: 未確認。ローカルの `frameworks-base` に `android-17*` タグがない。
- Compat framework エントリ: 未確認。Android 17 Compat framework 根拠が未取得。

---

# エグゼクティブサマリー

Android 17 では、targetSdkVersion 37 以上のアプリでユーザーが external キーボードなどの物理入力デバイスを使ってパスワードフィールドに入力する場合、新しい `show_passwords_physical` setting が適用され、既定ではパスワード characters がすべて非表示になる、と公式文書は説明している。

従来の「最後に入力したパスワード character を一時表示する」挙動は、物理キーボードと大きな画面では必要性が低く、覗き見リスクが高いという理由で見直される。touchscreen 入力では別の `show_passwords_touch` setting が適用される。

ただし、現時点のローカルの `frameworks-base` には Android 17 AOSP タグがないため、実装差分、targetSdkVersion 適用ゲート、入力デバイス判定、setting デフォルト、Compat Change ID は未確認である。

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
- 物理入力デバイスでのパスワード非表示

検証対象の原文:

> applies 新しい show_passwords_physical setting

提供された公式文書の抜粋は、アプリが Android 17 / API level 37 以上を対象とし、ユーザーが物理入力デバイスを使っている場合、Android がパスワードフィールド内の全文字に `show_passwords_physical` を適用すると説明している。また、デフォルトではすべてのパスワード文字を非表示にし、タッチスクリーン入力では `show_passwords_touch` を使うと説明している。

## 解釈

この変更は、パスワードフィールドの文字表示ポリシーを入力デバイスごとに分けるプライバシー / セキュリティ挙動変更である。物理入力デバイスの場合、最後の 1 文字を表示する利便性より、外部キーボードや大きな画面で入力文字が見られるリスクを重視し、既定で全パスワード文字を隠す。

アプリ側が標準のパスワードフィールド / プラットフォームのテキスト入力挙動に依存している場合、targetSdkVersion 37 更新後に物理キーボード入力時の視覚的フィードバックが変わる可能性がある。独自パスワードフィールドやカスタム変換を持つアプリは、プラットフォーム設定と整合しているか確認が必要である。

---

# 変更内容

公式文書上の変更点:
- targetSdkVersion 37 以上のアプリで、ユーザーが物理入力デバイスを使う場合、パスワードフィールドの全 characters に `show_passwords_physical` setting が適用される。
- `show_passwords_physical` のデフォルトはパスワード characters をすべて隠す。
- これまでの最後に入力したパスワード character を表示する挙動は、external キーボード / larger display では必要性が低く、覗き見リスクが高いと説明されている。
- touchscreen を使う場合は `show_passwords_touch` setting が適用される。

AOSP で未確認の点:
- Android 16 基準挙動のパスワード character reveal 挙動。
- Android 17 で追加された `show_passwords_physical` / `show_passwords_touch` setting の定義。
- 物理入力デバイスと touchscreen input の判定箇所。
- パスワードフィールドへの適用パス。
- targetSdkVersion 37 適用ゲートの実装箇所。
- Compat Change ID とデフォルト状態。

## 適用条件（Applicability）

公式文書の一次判断では、Android 17 以上、targetSdkVersion 37 以上、パスワードフィールド、物理入力デバイス使用中に適用される。touchscreen 入力では `show_passwords_touch` が適用される。AOSP タグが未取得のため、確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

### OS アップデート時の挙動

- Android 17 にアップデートしただけで適用されるか: 未確認
- targetSdkVersion に依存しない根拠: なし。公式文書は targetSdkVersion 37 以上を明示している。
- Android 16 以前での挙動: AOSP タグ比較未実施。Android 16 基準挙動 source は Android 17 タグとの比較ができないため、この調査では platform 根拠として採用していない。

### targetSdkVersion 37 以上での挙動

- targetSdkVersion 37 以上で適用されるか: 公式文書上は Yes と読めるが、AOSP 適用ゲートは未確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: 未確認。公式文書は Android 17 挙動変更として説明しているため、Android 17 platform 挙動として扱う。
- opt-out / temporary override の有無: 未確認。設定 UI / ユーザー setting / Compat framework の関係は AOSP 未確認。

### その他の条件

- 端末/フォームファクター: 物理入力デバイス、external キーボード。大きな画面を伴う可能性。
- 権限: 公式抜粋では条件なし。
- API 使用: パスワードフィールド / text input / transformation method / 入力デバイス source。
- manifest attribute: 未確認。
- コンポーネント境界: アプリのパスワード UI、platform text input、システム setting、入力デバイス classification にまたがる。

---

# AOSP 調査

## checkout 状態

根拠利用前に確認したコマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list 'android-17*'
```

Result:
- `frameworks-base` 作業ツリー: 調査時点で clean。
- From タグ: `android-16.0.0_r4` exists.
- To タグ: ローカルに `android-17*` タグなし。

根拠上の制約:
- Android 17 AOSP タグがローカルの `frameworks-base` に存在しないため、`git -C frameworks-base diff android-16.0.0_r4 <android-17-tag> -- ...` による明示的なタグ比較を実行できない。
- Repository rule に従い、Android 17 作業ツリーや推測によるソース根拠は採用しない。
- この制約により、AOSP-backed 結論は高信頼度にできない。

## 関連ファイル

未確認。Android 17 AOSP タグ取得後に、少なくとも以下の候補をタグ比較で確認する必要がある。

- `core/java/android/text/method/PasswordTransformationMethod.java`
- `core/java/android/widget/TextView.java`
- `core/java/android/provider/Settings.java`
- `core/java/android/view/InputDevice.java`
- `core/java/android/view/inputmethod/InputMethodManager.java`
- `core/res/res/values/config.xml` または設定デフォルト関連 resource
- Compat framework 定義ファイル内のパスワード reveal / 物理入力デバイス / targetSdkVersion 37 関連 Change ID

## 確認したソース文脈

Android 17 AOSP タグがないため、ソース文脈は未レビュー。

| ファイル / シンボル | Android 16 基準挙動 | Android 17 挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| 未レビュー | 未レビュー | 未レビュー | Android 17 タグがないため、公式文書の記述を AOSP 差分で検証できない。 |

必須記入項目:
- 入口 / 呼び出し元: 未確認。想定される入口はパスワードフィールドへのキー入力、TextView / PasswordTransformationMethod の表示更新、設定の show パスワードポリシー読み取りだが、AOSP 根拠としては未採用。
- Relevant class or service responsibility: 未確認。
- アプリ API またはシステムイベントから変更箇所までの実行時パス: 未確認。
- 除外した無関係なコードパス: Android 17 タグ不在のため、ソースパスの採否判断自体を保留。

## 差分解釈

| 確認した差分 | 解釈 | 挙動変更 との関係 | 信頼度 |
| --- | --- | --- | --- |
| Android 17 タグ間差分は利用不可 | ソース差分の種別はまだ分類できない | 公式文書の `show_passwords_physical` / `show_passwords_touch` setting と物理入力適用ゲートをソース差分で裏取りできていない | 低 |

必須分類:
- Added behavior: 未確認。
- Removed behavior: 未確認。
- Changed condition / gate: 未確認。
- Changed default: 未確認。
- No behavior change found: 未確認。タグ不在のため「no behavior change」とは判断しない。

## 事実

事実:
- 公式 Behavior Change 文書は、targetSdkVersion 37 以上のアプリで物理入力デバイス使用中に `show_passwords_physical` setting がパスワードフィールドの全 characters に適用されると述べている。
- 公式文書は、`show_passwords_physical` のデフォルトがすべてのパスワード characters を隠すことだと述べている。
- 公式文書は、last-typed パスワード character の表示は入力ミス確認を助けるが、external キーボードと大きな画面では必要性が低く、覗き見リスクが高いと説明している。
- 公式文書は、touchscreen 使用時には `show_passwords_touch` setting が適用されると述べている。
- ローカルの `frameworks-base` には `android-16.0.0_r4` タグがある。
- ローカルの `frameworks-base` には `android-17*` タグがない。
- 調査時点で `frameworks-base` 作業ツリーは clean。

観察:
- 公式ページ種別は targetSdkVersion 37 以上向けである。
- この項目は targetSdkVersion 37 条件に加えて、物理入力デバイス / touchscreen の実行時条件を含む。
- standard パスワードフィールドを使うアプリでは platform 挙動変更として現れる可能性がある。
- custom パスワード UI は platform setting と一致しない表示をしてしまう可能性がある。
- AOSP タグがないため、実装が本当に targetSdkVersion 37 適用ゲートで制御されているかは未確認。
- Compat framework エントリの有無も未確認。

仮説:
- Android 17 / targetSdkVersion 37 以上では、external キーボードなど物理入力デバイスからパスワードフィールドへ入力した場合、最後の1文字表示が抑制される可能性が高い。
- touchscreen 入力では `show_passwords_touch` により従来に近い別ポリシーが適用される可能性があるが、デフォルトとユーザー setting の詳細は未確認。
- targetSdkVersion 36 のアプリでは旧 `show_passwords` 相当の挙動が維持される可能性があるが、AOSP 適用ゲート未確認のため断定しない。

結論:
- 現時点で顧客向けに確定できるのは、「公式文書上は Android 17 / targetSdkVersion 37 以上で物理入力デバイス使用時のパスワード character 表示が `show_passwords_physical` に分離され、デフォルトでは全文字非表示になる」という範囲まで。
- AOSP 適用ゲート、setting definition、入力デバイス判定、Compat framework デフォルト状態が未確認のため、主分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

## 適用ゲート根拠

- targetSdkVersion 適用ゲート: 未確認。Android 17 AOSP タグがないため、`targetSdkVersion` / `ApplicationInfo.targetSdkVersion` 検索は実施していない。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。Android 17 AOSP タグがないため、`CompatChanges.isChangeEnabled` / `@ChangeId` / `@EnabledAfter` / `@EnabledSince` 検索は実施していない。
- @EnabledAfter / @EnabledSince / デフォルト状態: 未確認。
- Build.VERSION / SDK_INT 適用ゲート: 未確認。
- DeviceConfig / resources 設定: 未確認。
- 権限/AppOps 適用ゲート: 公式文書上は権限条件なし。
- Manifest/property 適用ゲート: 未確認。
- 適用ゲート未検出: 未判断。検索不能のため「適用ゲートなし」とは扱わない。
- 適用ゲートの結論: 未確認。公式文書上の Android 17 / targetSdkVersion 37 / 物理入力デバイス / パスワードフィールド条件はあるが、AOSP 根拠が不足している。
- ソース文脈からの推論: ソース文脈未取得のため不可。

Searched:
- `frameworks-base` checkout 状態。
- `android-16.0.0_r4` タグの存在。
- `android-17*` タグの存在。

Not searched yet:
- Android 17 implementation files.
- Android 17 Compat framework definitions.
- Android 17 設定デフォルト / resource files.
- パスワード transformation / TextView input handling implementation.

理由:
- Android 17 target タグがローカル checkout に存在しないため、タグ間差分による platform 根拠が作れない。

---

# 影響分析

## 影響を受けるアプリ

影響を受ける可能性があるアプリ:
- targetSdkVersion 37 以上への更新を予定しているアプリ。
- パスワードフィールドを持つアプリ。
- external キーボード、Chromebook、tablet キーボード、desktop mode、大きな画面でパスワード input が行われるアプリ。
- custom パスワードフィールド、custom transformation、独自の show / hide パスワード UI を持つアプリ。
- 入力直後の最後の1文字表示を前提とした UI テスト / screenshot テスト / accessibility テストを持つアプリ。

## 影響を受けにくいアプリ

影響が限定的と考えられるケース:
- パスワードフィールドを持たないアプリ。
- 物理入力デバイスでのパスワード input を想定しないアプリ。ただし foldable / tablet / Chromebook / desktop mode では想定外に該当する可能性がある。
- touchscreen 入力のみの場合。ただし `show_passwords_touch` の詳細は AOSP 未確認。
- targetSdkVersion 37 へ上げないアプリ。ただし、これは公式文書からの一次判断であり、AOSP 適用ゲートは未確認。

---

# 顧客影響

## 影響度

- Human decision required

※ 最終 severity / priority は人間が判断する。このレポートでは確定しない。

## ビジネス影響

- ユーザー影響: 物理キーボード入力時に最後のパスワード character が表示されなくなり、入力確認の UX が変わる可能性がある。一方で、大きな画面 / external キーボード環境での覗き見リスクは低下する。
- 運用影響: パスワード 入力の UI テスト、手動 QA、サポート手順で「最後の1文字が表示される」前提がある場合、期待結果の更新が必要。
- 開発影響: custom パスワードフィールドは platform setting と整合しているか確認し、物理キーボード / touchscreen の両方でテストする必要がある。

---

# サービス影響例

このセクションは、公式文書と AOSP 根拠から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1: 外部キーボード利用が多いログイン画面

- 対象サービス例: tablet / Chromebook 向け業務アプリ、教育アプリ、金融・認証画面。
- 影響を受ける実装パターン: パスワードフィールドで最後に入力した文字の一時表示をユーザー確認として期待している UI。
- 発生条件: Android 17 / targetSdkVersion 37 で物理入力デバイス使用中に `show_passwords_physical` が適用される場合。
- ユーザーに見える症状: 外部キーボード入力時にパスワード character が一切表示されず、入力ミス確認の体感が変わる可能性。
- 開発・運用への影響: support 文言、ログイン失敗率、キーボード利用 QA の確認が必要になる可能性。
- 推奨対応候補: パスワード visibility toggle、error feedback、物理キーボード / touchscreen 別テストを整備する。
- 根拠: 公式文書の記述とレポートの未確認の AOSP 根拠。
- 信頼度: 低
- 注意: デフォルト setting と入力デバイス判定は AOSP タグ待ち。

## 例2: Custom パスワードフィールドを持つアプリ

- 対象サービス例: パスワード manager、認証 SDK、独自 design システム を持つアプリ。
- 影響を受ける実装パターン: platform パスワードフィールドではなく custom masking / reveal 挙動を実装している UI。
- 発生条件: platform setting と custom フィールドの表示方針がずれる場合。
- ユーザーに見える症状: 標準パスワードフィールドと custom フィールドで表示挙動が違い、ユーザーが混乱する可能性。
- 開発・運用への影響: design システムコンポーネントの見直し、security review、UI テスト更新が必要になる可能性。
- 推奨対応候補: platform setting に合わせる、または custom reveal の security rationale を明確にする。
- 根拠: 公式文書の記述とレポートの解釈。
- 信頼度: 低
- 注意: 実装適用範囲は未確認。

---

# 対応候補

## 必須対応（Must）

- パスワードフィールドを持つ画面を棚卸しする。
- targetSdkVersion 37 更新前に Android 17 上で物理キーボードと touchscreen のパスワード input をテストする。
- custom パスワードフィールド / custom transformation / 独自 show パスワード UI がある場合、`show_passwords_physical` / `show_passwords_touch` の方針と衝突しないか確認する。

## 推奨対応（Recommended）

- tablet、Chromebook、external キーボード、大きな画面でのパスワード input QA を追加する。
- UI テスト / screenshot テストが last-typed character reveal を前提としていないか確認する。
- ユーザー向けヘルプやサポート文言が「最後に入力した文字が表示される」ことを前提としていないか確認する。
- アプリ独自のパスワード visibility toggle がある場合、システムデフォルトとユーザー選択の関係を整理する。

## 任意対応（Optional）

- Android 17 AOSP タグ公開後、setting definition、デフォルト value、TextView / PasswordTransformationMethod diff、Compat Change ID を再調査する。
- accessibility service やパスワード manager との組み合わせで visual feedback が期待どおりか確認する。

---

# 検証方法

## 検証マトリクス

| 端末 OS | targetSdkVersion | Compat flag | 期待される挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | デフォルト | Android 16 基準挙動。last-typed パスワード character reveal の挙動は Android 17 タグ比較待ち。 |
| Android 17 | 36 | デフォルト | 未確認。公式文書上は targetSdkVersion 37 以上向けだが、AOSP 適用ゲートは未確認。 |
| Android 17 | 37 | デフォルト | 公式文書上は物理入力デバイス使用時に `show_passwords_physical` が適用され、デフォルトでは全パスワード characters が hidden。 |
| Android 17 | 36 | force-enabled（利用可能な場合） | 未確認。Compat Change ID 未確認。 |
| Android 17 | 37 | force-disabled（利用可能な場合） | 未確認。Compat Change ID 未確認。 |

## 手順

- targetSdkVersion 変更: テストアプリを targetSdkVersion 36 と 37 で build し、Android 17 上で同じパスワードフィールドを比較する。
- Compat framework コマンド: Change ID 未確認のため未定。Android 17 タグ / compat page 確認後に追加する。
- テスト方法: standard パスワード `TextView` / `EditText`、custom パスワードフィールド、物理キーボード、touchscreen を組み合わせる。
- 再現手順: 物理キーボードと touchscreen でパスワードを入力し、入力直後の last character reveal、全 character masking、システム setting の反映を比較する。
- 期待結果: targetSdkVersion 37 で物理入力デバイスを使う場合、デフォルトでは最後の1文字も含めてパスワード characters が非表示になる。touchscreen の結果は `show_passwords_touch` のポリシーに従う。targetSdkVersion 36 の結果は AOSP 適用ゲート確認待ち。

---

# 結論

公式文書は、Android 17 で targetSdkVersion 37 以上のアプリに対し、物理入力デバイス使用時のパスワード display ポリシーとして `show_passwords_physical` を適用し、デフォルトでは全パスワード characters を隠すと説明している。主な影響は、パスワードフィールド、external キーボード、大きな画面、custom パスワード UI の組み合わせで発生する。

一方で、ローカルの `frameworks-base` に Android 17 AOSP タグがないため、実装差分、targetSdkVersion 適用ゲート、setting definition、入力デバイス判定、Compat Change ID、デフォルト状態を検証できていない。現時点の主分類は `UNKNOWN_NEEDS_MORE_EVIDENCE`、信頼度は低とする。

# 人間の判断欄

最終優先度（Final Priority）:
- Human decision required

最終影響度（Final Severity）:
- Human decision required

リリース判断（Release Readiness）:
- Human decision required

顧客通知優先度（Customer Communication Priority）:
- Human decision required

次に必要な人間の判断:
- Android 17 AOSP タグ公開後に再調査するか、公式 documentation ベースの暫定 security / UX ガイダンスとして扱うかを判断する。

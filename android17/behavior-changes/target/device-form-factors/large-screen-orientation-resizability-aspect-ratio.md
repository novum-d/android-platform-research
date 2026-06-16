# 大画面で画面向き・リサイズ可否・アスペクト比制約を無視するプラットフォーム API の変更 (sw>=600dp)

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
- https://developer.android.com/about/versions/16/behavior-changes-16#ignore-orientation
- https://developer.android.com/about/versions/17/changes/ff-restrictions-ignored

Section:
大画面で画面向き・リサイズ可否・アスペクト比制約を無視するプラットフォーム API の変更 (sw>=600dp)

Page type:
- Apps targeting Android 17 or higher

### 分類スナップショット

主分類（Primary classification）:
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- 公式文書は、Android 16 で targetSdkVersion 36 以上のアプリに対し、大画面 (`sw >= 600dp`) で画面向き、アスペクト比、リサイズ可否の制限を無視するプラットフォーム API changes が導入されたと説明している。
- Android 16 / SDK 36 では開発者が opt out できたが、Android 17 / API level 37 以上を target するアプリでは、この opt-out が利用できなくなると説明している。
- 追加条件として、大画面 (`sw >= 600dp`)、画面向き / リサイズ可否 / アスペクト比 制約、Android 16 の opt-out mechanism、Android 17 targetSdkVersion 37 が関係する。
- ただし、ローカルの `frameworks-base` に Android 17 AOSP タグがないため、opt-out removal、targetSdkVersion 37 適用ゲート、大画面判定、ActivityInfo / WindowManager / ActivityTaskManager の適用パス、Compat Change ID、default state は未検証である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

早見表:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 未確認 | Android 16 で targetSdkVersion 36+ 向けに導入済みだが、Android 17 の opt-out removal 適用ゲートは AOSP では未確認。 |
| targetSdkVersion 37 以上が必要か | その可能性が高いが未検証 | 原文は、Android 17 / API level 37 以上を対象とするアプリでは opt-out が利用不可と述べている。 |
| 追加の実行時条件があるか | あり | 大画面 (`sw >= 600dp`) と画面向き / リサイズ可否 / アスペクト比制約が関係する。 |
| Compat Change ID が関係するか | 未確認 | Android 17 タグと Compat framework の根拠が未確認。 |

### 調査日（Investigation Date）

2026-06-11

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
- targetSdkVersion: 公式文書上は 37 以上で opt-out unavailable。Android 16 では 36 以上で opt-out 可能だったと説明されている。
- 端末/フォームファクター: 大画面 / `sw >= 600dp`。
- Permission/API/コンポーネント条件: 画面向き request、リサイズ可否 restriction、アスペクト比制約、Android 16 opt-out mechanism。
- アプリ状態/プロセス条件: Activity launch / configuration / windowing mode / display サイズ evaluation 時点。

Compat framework:
- Change ID: 未確認
- 変更名: 未確認
- default state: 未確認
- テスト時の切り替え可否: 未確認

分類信頼度:
- 低

分類根拠:
- Official documentation page: `behavior-changes-17`
- 検証対象の適用条件文: Android 16 では API 36 以上を対象とするアプリについて、大画面で画面向き / アスペクト比 / リサイズ可否の制限を無視する変更が導入され、開発者は opt-out できた。Android 17 / API 37 以上ではその opt-out が利用できなくなる。
- AOSP targetSdk 適用ゲート: 未確認。ローカルの `frameworks-base` に `android-17*` タグがない。
- Compat framework エントリ: 未確認。Android 17 Compat framework の根拠が未取得。

---

# エグゼクティブサマリー

Android 16 では、targetSdkVersion 36 以上のアプリについて、大画面 (`sw >= 600dp`) で画面向き、アスペクト比、リサイズ可否の制約をプラットフォームが無視する変更が導入された、と公式文書は説明している。Android 16 では opt-out が可能だったが、Android 17 / targetSdkVersion 37 以上ではその opt-out が利用できなくなる。

この変更により、タブレット、折りたたみ端末、デスクトップサイズのウィンドウなどで、アプリが縦向き固定、リサイズ不可、固定アスペクト比を指定していても、プラットフォームがより大きな画面に適した表示・リサイズを優先する可能性がある。既存 UI が固定向き・固定比率を前提としている場合は、大画面対応の確認が必要である。

ただし、現時点のローカルの `frameworks-base` には Android 17 AOSP タグがないため、opt-out 削除の実装差分、targetSdkVersion 適用ゲート、大画面判定、Compat 変更 ID は未確認である。

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
- 大画面で画面向き・リサイズ可否・アスペクト比制約を無視するプラットフォーム API の変更 (sw>=600dp)

検証対象の原文:

> Android 16 では、API level 36 以上を対象とするアプリについて、大画面 (`sw >= 600dp`) で画面向き、アスペクト比、リサイズ可否の制限を無視するプラットフォーム API の変更が導入された。

提供された公式文書の抜粋は、SDK 36 では開発者がこれらの変更から opt-out できたが、Android 17 / API level 37 以上を対象とするアプリではこの opt-out が利用できなくなると説明している。

## 解釈

この変更は、大画面でアプリの画面向き / リサイズ可否 / アスペクト比制約よりもプラットフォームの画面適応を優先する大画面互換性の挙動変更である。Android 17 では、Android 16 で許されていた SDK 36 向け opt-out が targetSdkVersion 37 以上では使えなくなる点が中心である。

アプリ開発者にとって重要なのは、targetSdkVersion 37 へ更新すると、大画面上で portrait 固定、resize 不可、最大 / 最小アスペクト比などの制約に依存したレイアウト保護が効かなくなる可能性がある点である。UI は `sw >= 600dp` を含む大画面 / multi-window / foldable / desktop windowing を前提に検証する必要がある。

---

# 変更内容

公式文書上の変更点:
- Android 16 で、大画面 (`sw >= 600dp`) において画面向き、アスペクト比、リサイズ可否の制限を無視するプラットフォーム API changes が導入された。
- Android 16 の対象は API level 36 以上を target するアプリ。
- SDK 36 では開発者が opt out できた。
- Android 17 / API level 37 以上を target するアプリでは、この opt-out が利用できなくなる。
- 詳細は Android 16 の挙動変更と Android 17 の `Restrictions on orientation and resizability are ignored` 関連ページに誘導されている。
- 詳細ページでは、targetSdkVersion 37 以上のアプリについて、smallest width が 600dp より大きい display では画面向き、リサイズ可否、アスペクト比制限が適用されず、アプリはアスペクト比やユーザー preferred 画面向きに関係なく display window 全体を fill し、pillarboxing は使われないと説明されている。
- 詳細ページでは、`screenOrientation`、`resizableActivity`、`minAspectRatio`、`maxAspectRatio`、`setRequestedOrientation()`、`getRequestedOrientation()` が大画面端末の full-screen / multi-window modes で無視されると説明されている。
- 詳細ページでは、games、端末のアスペクト比設定でユーザーがアプリ default 挙動に明示 opt-in した場合、smallest width が `sw600dp` より小さい screens は例外と説明されている。
- 詳細ページでは、`UNIVERSAL_RESIZABLE_BY_DEFAULT` compat flag でテストできると説明されている。

AOSP で未確認の点:
- Android 16 基準挙動で画面向き / アスペクト比 / リサイズ可否制限を無視する実装と opt-out mechanism。
- Android 17 で targetSdkVersion 37 以上の opt-out を無効化する実装箇所。
- `sw > 600dp` / `sw >= 600dp` の exact 条件。詳細ページは "smallest width is greater than 600dp" と説明している一方、関連文書や Android 16 文脈では `sw >= 600dp` と表現されることがある。
- Activity requested 画面向き、`resizeableActivity`、最小 / 最大アスペクト比、letterbox / compatibility mode、multi-window mode の扱い。
- Android 16 opt-out property / manifest / Compat framework と Android 17 removal の関係。
- Compat Change ID と default state。

## 適用条件（Applicability）

公式文書の一次判断では、Android 17 以上、targetSdkVersion 37 以上、大画面 (`sw >= 600dp`) で画面向き / リサイズ可否 / アスペクト比制約を指定しているアプリに適用される。Android 16 / targetSdkVersion 36 で存在した opt-out が Android 17 / targetSdkVersion 37 では使えないという変更である。AOSP タグが未取得のため、確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

### OS アップデート時の挙動

- Android 17 にアップデートしただけで適用されるか: 未確認
- targetSdkVersion に依存しない根拠: なし。原文は Android 17 / API level 37 以上を target するアプリで opt-out unavailable と述べている。
- Android 16 以前での挙動: 公式文書は Android 16 / API level 36+ で制約無視が導入され、SDK 36 では opt-out 可能だったと述べている。AOSP タグ比較は未実施。

### targetSdkVersion 37 以上での挙動

- targetSdkVersion 37 以上で適用されるか: 公式文書上は Yes と読めるが、AOSP 適用ゲートは未確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: 未確認。公式文書は Android 17 挙動変更として説明しているため、Android 17 platform の挙動として扱う。
- opt-out / temporary override の有無: 公式文書上、SDK 36 の opt-out は Android 17 / targetSdkVersion 37 以上では利用不可。AOSP による具体的 opt-out 名、manifest property、compat toggle は未確認。

### その他の条件

- 端末/フォームファクター: 大画面。詳細ページは smallest width が 600dp より大きい display と説明している。tablet、foldable inner display、desktop / freeform windowing、大画面 emulator などが関係する可能性。
- 権限: 公式抜粋では条件なし。
- API 使用: requested 画面向き、リサイズ可否、アスペクト比制約、Activity manifest attributes、WindowManager / ActivityTaskManager 挙動。
- manifest attribute / 実行時 API: `screenOrientation`、`resizeableActivity`、`minAspectRatio` / `maxAspectRatio`、`setRequestedOrientation()`、`getRequestedOrientation()`、Android 16 opt-out property が関係する可能性。
- 例外: games based on `android:appCategory`、端末アスペクト比設定でユーザーがアプリ default 挙動に明示 opt-in した場合、smallest width が `sw600dp` より小さい screens。
- コンポーネント境界: Activity launch、task / windowing mode、display metrics、構成変更、letterbox / compatibility handling にまたがる。

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

- `core/java/android/content/pm/ActivityInfo.java`
- `core/java/android/R.styleable` / manifest attribute definitions
- `services/core/java/com/android/server/wm/ActivityRecord.java`
- `services/core/java/com/android/server/wm/ActivityTaskManagerService.java`
- `services/core/java/com/android/server/wm/DisplayContent.java`
- `services/core/java/com/android/server/wm/LetterboxUiController.java`
- `services/core/java/com/android/server/wm/SizeCompatPolicy.java`
- `services/core/java/com/android/server/wm/AspectRatioPolicy.java`
- Compat framework 定義ファイル内の画面向き / リサイズ可否 / アスペクト比 / 大画面 / targetSdkVersion 37 関連 Change ID
- `UNIVERSAL_RESIZABLE_BY_DEFAULT` compat flag definition / default state

## 確認したソース文脈

Android 17 AOSP タグがないため、ソース文脈は未レビュー。

| ファイル / シンボル | Android 16 基準挙動 | Android 17 挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| 未レビュー | 未レビュー | 未レビュー | Android 17 タグがないため、公式文書の記述を AOSP 差分で検証できない。 |

必須記入項目:
- 入口 / 呼び出し元: 未確認。想定される入口は Activity launch、manifest parsing、requested 画面向き evaluation、resizeability / アスペクト比ポリシー、大画面 display metrics 判定だが、AOSP 根拠としては未採用。
- Relevant class or service responsibility: 未確認。
- アプリ API またはシステムイベントから変更箇所までの実行時パス: 未確認。
- 除外した無関係なコードパス: Android 17 タグ不在のため、ソースパスの採否判断自体を保留。

## 差分解釈

| 確認した差分 | 解釈 | 挙動変更との関係 | 信頼度 |
| --- | --- | --- | --- |
| Android 17 タグ間差分は利用不可 | ソース差分の種別はまだ分類できない | 公式文書の Android 16 挙動、SDK 36 opt-out、Android 17 / targetSdkVersion 37 opt-out removal、大画面条件をソース差分で裏取りできていない | 低 |

必須分類:
- Added behavior: 未確認。
- Removed behavior: 未確認。公式文書上は Android 16 の opt-out が Android 17 / targetSdkVersion 37 以上では removed / unavailable になる可能性がある。
- Changed condition / gate: 未確認。targetSdkVersion 37 と `sw >= 600dp` 適用ゲートがある可能性は高いが、AOSP では未確認。
- Changed default: 未確認。
- No behavior change found: 未確認。タグ不在のため「no behavior change」とは判断しない。

## 事実

事実:
- 公式 Behavior Change 文書は、Android 16 で API level 36 以上を target するアプリに対し、大画面 (`sw >= 600dp`) で画面向き、アスペクト比、リサイズ可否制限を無視するプラットフォーム API changes が導入されたと述べている。
- 公式文書は、SDK 36 では開発者が opt out できたと述べている。
- 公式文書は、Android 17 / API level 37 以上を target するアプリでは、この opt-out が no longer available と述べている。
- ローカルの `frameworks-base` には `android-16.0.0_r4` タグがある。
- ローカルの `frameworks-base` には `android-17*` タグがない。
- 調査時点で `frameworks-base` 作業ツリーは clean。

観察:
- 公式ページ種別は targetSdkVersion 37 以上向けである。
- この項目は targetSdkVersion 37 条件に加えて、大画面 (`sw >= 600dp`) という端末/フォームファクター条件を含む。
- Android 16 ですでに制約無視が導入されており、Android 17 の主な変更は SDK 36 で使えた opt-out の終了である。
- fixed 画面向き / fixed アスペクト比 / non-resizable 前提の UI は、targetSdkVersion 37 で大画面上の表示崩れや予期しない構成変更に遭遇する可能性がある。
- AOSP タグがないため、実装が本当に targetSdkVersion 37 適用ゲートで制御されているかは未確認。
- Compat framework エントリの有無も未確認。

仮説:
- Android 17 / targetSdkVersion 37 以上では、Android 16 の opt-out manifest property または compat override を指定しても、大画面上で画面向き / リサイズ可否 / アスペクト比制限が無視される可能性が高い。
- Android 17 / targetSdkVersion 36 のアプリでは Android 16 と同様に opt-out が有効な可能性があるが、AOSP 適用ゲートが未確認のため断定しない。
- `sw >= 600dp` の判定は display / window metrics / smallest width configuration に依存する可能性があるが、exact 条件は未確認である。

結論:
- 現時点で顧客向けに確定できるのは、「公式文書上は Android 17 / targetSdkVersion 37 以上のアプリでは、大画面で画面向き / リサイズ可否 / アスペクト比制限を無視する Android 16 変更への opt-out が利用できなくなる」という範囲まで。
- AOSP 適用ゲート、大画面判定、opt-out mechanism、Compat framework default state が未確認のため、主分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

## 適用ゲート根拠

- targetSdkVersion 適用ゲート: 未確認。公式文書は targetSdkVersion 37 以上を示すが、AOSP 適用ゲート根拠はない。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。Android 17 タグがないため検索未実施。
- @EnabledAfter / @EnabledSince / default state: 未確認。Android 17 タグがないため検索未実施。
- Build.VERSION / SDK_INT 適用ゲート: 未確認。
- DeviceConfig / resources 設定: 未確認。`sw >= 600dp` 条件は公式文書上の端末条件だが、AOSP 判定箇所は未確認。
- 権限/AppOps 適用ゲート: 公式抜粋では条件なし。
- Manifest/property 適用ゲート: 未確認。Android 16 opt-out mechanism と Android 17 removal の具体的 manifest / property 名は AOSP では未確認。
- 適用ゲート未検出: 未確認。Android 17 タグがないため「適用ゲートがない」とは判断しない。
- 適用ゲートの結論: 未確認。公式文書の wording から targetSdkVersion 37 + 大画面条件と推定されるが、AOSP で検証できていない。
- ソース文脈からの推論: ソース文脈未レビューのため未確定。

---

# 影響分析

## 影響を受けるアプリ

影響を受ける可能性があるアプリ:
- targetSdkVersion 37 へ更新し、大画面 (`sw >= 600dp`) で動作するアプリ。
- `screenOrientation` で portrait / landscape 固定を前提にしているアプリ。
- `resizeableActivity=false` または固定 window サイズ / non-resizable 前提の設計を持つアプリ。
- `minAspectRatio` / `maxAspectRatio` や固定 アスペクト比 に依存するアプリ。
- Android 16 / SDK 36 で opt-out を利用して大画面制約無視を回避していたアプリ。
- tablet、foldable、desktop windowing、ChromeOS など大画面展開があるアプリ。

## 影響を受けにくいアプリ

影響が限定的または対象外と考えられるケース:
- 大画面 (`sw >= 600dp`) で利用されないアプリ。
- すでに画面向き / リサイズ可否 / アスペクト比制約に依存せず adaptive UI を実装しているアプリ。
- Android 16 / targetSdkVersion 36 で opt-out を使っておらず、大画面で検証済みのアプリ。
- Android 17 AOSP タグ取得後に対象外適用ゲートや exemption が確認されたケース。

---

# 顧客影響

顧客説明用。

## 影響度

- Human decision required

※ 仮評価。最終判断は人間が行う。

## ビジネス影響

- ユーザー影響: 大画面上で固定向き / 固定比率前提の UI が広がる、回転する、リサイズされる、letterbox されないなどにより、表示崩れや操作不能が起きる可能性がある。
- 運用影響: tablet / foldable / desktop windowing の QA matrix、Android 16 opt-out 利用状況、targetSdkVersion 37 移行計画を確認する必要がある可能性がある。
- 開発影響: adaptive layout、multi-window、構成変更、responsive resource、Jetpack WindowManager / Compose adaptive UI などの対応が必要になる可能性がある。

---

# サービス影響例

このセクションは、公式文書と AOSP 根拠 から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: Portrait 固定のスマートフォン前提 UI

- 対象サービス例: 決済、本人確認、縦長 feed、camera / scanner UI。
- 影響を受ける実装パターン: `screenOrientation="portrait"`、固定アスペクト比、non-resizable 前提の Activity。
- 発生条件: Android 17 / targetSdkVersion 37、`sw >= 600dp` 大画面で Android 16 opt-out が使えない場合。
- ユーザーに見える症状: tablet / foldable で横向きや大きな window に広がり、UI が崩れる可能性。
- 開発・運用への影響: 大画面 QA、adaptive layout、構成変更 handling の見直しが必要になる可能性。
- 推奨対応候補: fixed 画面向き前提を減らし、responsive layout と状態 restoration を整備する。
- 根拠: 公式文書の記述とレポートの 期待される挙動。
- 信頼度: 低
- 注意: exact opt-out mechanism と大画面判定は AOSP タグ待ち。

## 例2（Example 2）: Tablet / foldable で non-resizable を指定する業務アプリ

- 対象サービス例: POS、医療業務、教育、店舗管理、在庫管理。
- 影響を受ける実装パターン: `resizeableActivity=false` や固定 window サイズ前提で画面密度・サイズを決め打ちする UI。
- 発生条件: targetSdkVersion 37 で大画面制約無視が opt-out できない場合。
- ユーザーに見える症状: split-screen / freeform resize でボタン重なり、入力欄切れ、操作不能が起きる可能性。
- 開発・運用への影響: multi-window、fold / unfold、external display のテスト matrix 更新が必要になる可能性。
- 推奨対応候補: window サイズに応じた layout 分岐、scrollable content、minimum touch target を整備する。
- 根拠: 公式文書の記述とレポートの対応候補。
- 信頼度: 低
- 注意: 実サービスでの発生確認ではない。

---

# 対応候補

## 必須対応（Must）

- Android 16 の opt-out mechanism を利用しているか確認する。
- `screenOrientation`、`resizeableActivity`、`minAspectRatio`、`maxAspectRatio` など、大画面制約に関わる manifest / API の使用箇所を棚卸しする。
- `setRequestedOrientation()` / `getRequestedOrientation()` に依存している実行時ロジックを棚卸しする。
- `android:appCategory="game"` の対象可否、端末のアスペクト比設定でユーザーが opt-in した場合の扱い、`sw600dp` 未満の画面の例外をテスト計画に含める。
- `sw >= 600dp` 相当の tablet / foldable / desktop windowing 環境で、targetSdkVersion 37 のビルドを検証する。
- 画面向き変更、multi-window resize、split-screen、fold / unfold、freeform resize で UI が崩れないか確認する。
- Android 17 AOSP タグ入手後に、targetSdkVersion 適用ゲート、opt-out removal、Compat Change ID を再確認する。

## 推奨対応（Recommended）

- 画面向き固定 / アスペクト比固定の前提を減らし、layout を adaptive / responsive にする。
- 状態 restoration と構成変更 handling を確認し、回転やリサイズで入力中データが失われないようにする。
- 大画面用 resource、navigation layout、two-pane / supporting pane、window size class 相当の layout 分岐を整備する。
- Android 16 の関連挙動変更と Android 17 の opt-out removal を分けて、既存 opt-out 依存のリスクを管理する。

## 任意対応（Optional）

- foldable posture、external display、ChromeOS / desktop mode など、`sw >= 600dp` 以外の大画面利用条件もテストする。
- UI screenshot / automated layout テストを追加し、targetSdkVersion 37 移行時の表示崩れを検出する。

---

# 検証方法

## 検証マトリクス

| 端末 OS | targetSdkVersion | Compat flag | 期待される挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | デフォルト / opt-out 設定あり | 公式文書上、大画面制約の無視は導入済みだが、SDK 36 では opt-out 可能。 |
| Android 17 | 36 | デフォルト / opt-out 利用可能な場合 | 未確認。SDK 36 opt-out が維持されるかは AOSP 適用ゲート未確認。 |
| Android 17 | 37 | デフォルト | 公式文書上、SDK 36 で利用できた opt-out は利用不可。大画面で画面向き / アスペクト比 / リサイズ可否の制限が無視される。 |
| Android 17 | 36 | force-enabled（利用可能な場合） | 未確認。Compat Change ID 未確認。 |
| Android 17 | 37 | force-disabled（利用可能な場合） | 未確認。Compat Change ID 未確認。 |

## 手順

- targetSdkVersion 変更: targetSdkVersion 36 と 37 のテストビルドを用意する。
- Compat framework コマンド: 公式詳細ページは `UNIVERSAL_RESIZABLE_BY_DEFAULT` compat flag を有効化してテストできると説明している。具体的なコマンド / package scope は Android 17 タグまたは Compat framework page で再確認する。
- テスト方法: `sw >= 600dp` の emulator / tablet / foldable で、画面向き固定 / `resizeableActivity=false` / アスペクト比固定の Activity を起動し、Android 16 opt-out あり / なし、targetSdkVersion 36 / 37 を比較する。
- 再現手順: Android 17 端末 / emulator で対象アプリをインストールし、portrait / landscape、split-screen、freeform resize、fold / unfold を実施する。requested 画面向き、actual 画面向き、window bounds、構成変更、layout breakage を記録する。
- 期待結果: targetSdkVersion 37 のアプリでは、Android 16 で使えた opt-out が効かず、大画面上で画面向き / アスペクト比 / リサイズ可否の制限が platform により無視される。具体的な opt-out 失敗時の挙動は AOSP タグと実機検証待ち。

---

# 結論

公式文書上、Android 17 / targetSdkVersion 37 以上のアプリでは、Android 16 で導入された大画面上の画面向き / リサイズ可否 / アスペクト比制約の無視に対する SDK 36 opt-out が利用できなくなる。大画面で固定向き・固定比率・非リサイズ前提の UI を持つアプリは、targetSdkVersion 37 移行前に adaptive UI と構成変更対応を確認する必要がある。

ただし、Android 17 AOSP タグがローカル checkout にないため、実装上の適用ゲート、opt-out removal、大画面判定、Compat framework の確認は未完了である。最終的な適用分類と顧客向け確定説明は、Android 17 AOSP タグ入手後に再調査が必要である。

---

# 人間の判断欄

最終優先度（Final Priority）:
- Human decision required

最終影響度（Final Severity）:
- Human decision required

リリース判断（Release Readiness）:
- Human decision required

顧客通知優先度（Customer Communication Priority）:
- Human decision required

判断（Decision）:
- 追加調査が必要

判断メモ:
- Android 17 AOSP タグ入手後に、AOSP 根拠と Compat framework 根拠を確認してから最終判断する。

---

# 参照（References）

## ドキュメント

- https://developer.android.com/about/versions/17/behavior-changes-17
- https://developer.android.com/about/versions/16/behavior-changes-16#ignore-orientation
- https://developer.android.com/about/versions/17/changes/ff-restrictions-ignored

## AOSP

- ローカルの `frameworks-base` では Android 17 は利用不可。
- From タグ checked: `android-16.0.0_r4`
- To タグ checked: ローカルに `android-17*` タグなし。

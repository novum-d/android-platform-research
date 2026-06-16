# 大画面で画面向き・リサイズ可否・アスペクト比制約を無視するプラットフォーム API の変更（sw >= 600dp）

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
- https://developer.android.com/about/versions/16/behavior-changes-16#ignore-orientation
- https://developer.android.com/about/versions/17/changes/ff-restrictions-ignored

セクション:
Platform API changes to ignore orientation, resizability and aspect ratio constraints on large screens (sw>=600dp)

ページ種別:
- Apps targeting Android 17 or higher

### 分類スナップショット

主分類（Primary classification）:
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- 公式文書は、Android 16 で targetSdkVersion 36 以上のアプリに対し、大画面 (`sw >= 600dp`) で画面向き、アスペクト比、リサイズ可否の制約を無視する Platform API changes が導入されたと説明している。
- Android 16 / SDK 36 では開発者が opt out できたが、Android 17 / API level 37 以上を target するアプリでは、この opt-out が利用できなくなると説明している。
- 追加条件として、大画面 (`sw >= 600dp`)、画面向き / リサイズ可否 / アスペクト比制約、Android 16 の opt-out mechanism、Android 17 targetSdkVersion 37 が関係する。
- ただし、ローカル `frameworks-base` に Android 17 AOSP タグがないため、opt-out removal、targetSdkVersion 37 gate、大画面判定、ActivityInfo / WindowManager / ActivityTaskManager の enforcement path、Compat Change ID、default state は未検証である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

早見表:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 未確認 | Android 16 で targetSdkVersion 36+ 向けに導入済みだが、Android 17 の opt-out removal gate は AOSP 未確認。 |
| targetSdkVersion 37 以上が必要か | 可能性は高いが未確認 | 原文は opt-out が apps that target Android 17 / API level 37 or higher では利用不可と述べている。 |
| 追加の実行時条件があるか | ある | 大画面 (`sw >= 600dp`) と画面向き / リサイズ可否 / アスペクト比制約が関係する。 |
| Compat Change ID が関係するか | 未確認 | Android 17 タグと compat framework evidence が未確認。 |

### 調査日

2026-06-11

### 信頼度

- 低

### 適用条件分類

適用される条件:
- [ ] Android 17 上の全アプリ（targetSdkVersion に依存しない）
- [ ] Android 17 以上で targetSdkVersion >= 37
- [ ] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [x] 未確認 / 追加根拠が必要

必要な実行時条件:
- Android version: Android 17 以上が前提と考えられるが、AOSP タグ未取得。
- targetSdkVersion: 公式文書上は 37 以上で opt-out unavailable。Android 16 では 36 以上で opt-out 可能だったと説明されている。
- Device/form factor: 大画面 / `sw >= 600dp`。
- Permission/API/component condition: orientation request、resizability restriction、aspect ratio constraint、Android 16 opt-out mechanism。
- App state/process condition: Activity launch / configuration / windowing mode / display size evaluation 時点。

Compat framework:
- Change ID: 未確認
- 変更名: 未確認
- 既定状態: 未確認
- テスト時の切り替え可否: 未確認

分類信頼度:
- 低

分類根拠:
- 公式ドキュメントページ: `behavior-changes-17`
- 検証対象の適用条件文: Android 16 introduced ignoring orientation / aspect ratio / resizability restrictions on large screens for API 36+ with opt-out; Android 17 / API 37+ removes that opt-out.
- AOSP targetSdk gate: 未確認。ローカル `frameworks-base` に `android-17*` タグがない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# エグゼクティブサマリー

Android 16 では、targetSdkVersion 36 以上のアプリについて、large screens (`sw >= 600dp`) で orientation、aspect ratio、resizability の制約を platform が無視する変更が導入された、と公式文書は説明している。Android 16 では opt-out が可能だったが、Android 17 / targetSdkVersion 37 以上ではその opt-out が利用できなくなる。

この変更により、タブレット、折りたたみ端末、デスクトップサイズのウィンドウなどで、アプリが portrait 固定、non-resizable、固定 aspect ratio を指定していても、platform がより大きな画面に適した表示・リサイズを優先する可能性がある。既存 UI が固定向き・固定比率を前提としている場合は、large screen 対応の確認が必要である。

ただし、現時点のローカル `frameworks-base` には Android 17 AOSP タグがないため、opt-out removal の実装差分、targetSdkVersion gate、大画面判定、Compat Change ID は未確認である。

---

# 公式ドキュメント確認

## 原文（Statement）

Page title:
- Behavior changes: Apps targeting Android 17 or higher

Page URL:
- https://developer.android.com/about/versions/17/behavior-changes-17

ページ種別:
- apps targeting Android 17

Section title:
- Platform API changes to ignore orientation, resizability and aspect ratio constraints on large screens (sw>=600dp)

検証対象の原文:

> We introduced Platform API changes in Android 16 to ignore orientation, aspect ratio, and resizability restrictions on large screens (sw >= 600dp) for apps targeting API level 36 or higher.

提供された公式文書の抜粋は、SDK 36 では開発者がこれらの変更から opt out できたが、Android 17 / API level 37 以上を target するアプリではこの opt-out が利用できなくなるとも説明している。

## 解釈

この変更は、large screen でアプリの orientation / resizability / aspect ratio 制約よりも platform の画面適応を優先する large-screen compatibility behavior change である。Android 17 では、Android 16 で許されていた SDK 36 向け opt-out が targetSdkVersion 37 以上では使えなくなる点が中心である。

アプリ開発者にとって重要なのは、targetSdkVersion 37 へ更新すると、large screen 上で portrait 固定、resize 不可、最大 / 最小 aspect ratio などの制約に依存したレイアウト保護が効かなくなる可能性がある点である。UI は `sw >= 600dp` を含む large screen / multi-window / foldable / desktop windowing を前提に検証する必要がある。

---

# 変更内容

公式文書上の変更点:
- Android 16 で、large screens (`sw >= 600dp`) において orientation、aspect ratio、resizability restrictions を無視する Platform API changes が導入された。
- Android 16 の対象は API level 36 以上を target するアプリ。
- SDK 36 では developers が opt out できた。
- Android 17 / API level 37 以上を target するアプリでは、この opt-out が利用できなくなる。
- 詳細は Android 16 の behavior change と Android 17 の `Restrictions on orientation and resizability are ignored` 関連ページに誘導されている。
- 詳細ページでは、targetSdkVersion 37 以上の app について、smallest width が 600dp より大きい display では orientation、resizability、aspect ratio restrictions が適用されず、apps は aspect ratio や user preferred orientation に関係なく display window 全体を fill し、pillarboxing は使われないと説明されている。
- 詳細ページでは、`screenOrientation`、`resizableActivity`、`minAspectRatio`、`maxAspectRatio`、`setRequestedOrientation()`、`getRequestedOrientation()` が large screen devices の full-screen / multi-window modes で ignored と説明されている。
- 詳細ページでは、games、device の aspect ratio settings で users が app default behavior に明示 opt-in した場合、smallest width が `sw600dp` より小さい screens は例外と説明されている。
- 詳細ページでは、`UNIVERSAL_RESIZABLE_BY_DEFAULT` compat flag で test できると説明されている。

AOSP で未確認の点:
- Android 16 baseline で orientation / aspect ratio / resizability restrictions を無視する実装と opt-out mechanism。
- Android 17 で targetSdkVersion 37 以上の opt-out を無効化する実装箇所。
- `sw > 600dp` / `sw >= 600dp` の exact condition。詳細ページは "smallest width is greater than 600dp" と説明している一方、関連文書や Android 16 文脈では `sw >= 600dp` と表現されることがある。
- Activity requested orientation、`resizeableActivity`、min / max aspect ratio、letterbox / compatibility mode、multi-window mode の扱い。
- Android 16 opt-out property / manifest / compat framework と Android 17 removal の関係。
- Compat Change ID と default state。

## 適用条件（Applicability）

公式文書の一次判断では、Android 17 以上、targetSdkVersion 37 以上、large screens (`sw >= 600dp`) で orientation / resizability / aspect ratio constraints を指定しているアプリに適用される。Android 16 / targetSdkVersion 36 で存在した opt-out が Android 17 / targetSdkVersion 37 では使えないという変更である。AOSP tag が未取得のため、確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

### OS アップデート時の挙動

- Android 17 にアップデートしただけで適用されるか: 未確認
- targetSdkVersion に依存しない根拠: なし。原文は Android 17 / API level 37 以上を target するアプリで opt-out unavailable と述べている。
- Android 16 以前での挙動: 公式文書は Android 16 / API level 36+ で制約無視が導入され、SDK 36 では opt-out 可能だったと述べている。AOSP タグ比較は未実施。

### targetSdkVersion 37 以上での挙動

- targetSdkVersion 37 以上で適用されるか: 公式文書上は Yes と読めるが、AOSP gate は未確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: 未確認。公式文書は Android 17 Behavior Changes として説明しているため、Android 17 platform behavior として扱う。
- opt-out / temporary override の有無: 公式文書上、SDK 36 の opt-out は Android 17 / targetSdkVersion 37 以上では利用不可。AOSP による具体的 opt-out 名、manifest property、compat toggle は未確認。

### その他の条件

- device/form factor: large screens。詳細ページは smallest width が 600dp より大きい display と説明している。tablet、foldable inner display、desktop / freeform windowing、large screen emulator などが関係する可能性。
- permission: 公式抜粋では条件なし。
- API usage: requested orientation、resizability、aspect ratio constraints、Activity manifest attributes、WindowManager / ActivityTaskManager behavior。
- manifest attribute / runtime API: `screenOrientation`、`resizeableActivity`、`minAspectRatio` / `maxAspectRatio`、`setRequestedOrientation()`、`getRequestedOrientation()`、Android 16 opt-out property が関係する可能性。
- exceptions: games based on `android:appCategory`、device aspect ratio settings で user が app default behavior に明示 opt-in した場合、smallest width が `sw600dp` より小さい screens。
- component boundary: Activity launch、task / windowing mode、display metrics、configuration changes、letterbox / compatibility handling にまたがる。

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
- `frameworks-base` working tree: 調査時点で clean。
- From tag: `android-16.0.0_r4` exists.
- To tag: ローカルに `android-17*` タグなし。

根拠上の制約:
- Android 17 AOSP タグがローカル `frameworks-base` に存在しないため、`git -C frameworks-base diff android-16.0.0_r4 <android-17-tag> -- ...` による明示的なタグ比較を実行できない。
- Repository rule に従い、Android 17 working tree や推測による source evidence は採用しない。
- この制約により、AOSP-backed conclusion は高信頼度にできない。

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
- compat framework 定義ファイル内の orientation / resizability / aspect ratio / large screen / targetSdkVersion 37 関連 Change ID
- `UNIVERSAL_RESIZABLE_BY_DEFAULT` compat flag definition / default state

## 確認したソース文脈

Android 17 AOSP タグがないため、source context は未レビュー。

| ファイル / シンボル | Android 16 基準挙動 | Android 17 挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| 未レビュー | 未レビュー | 未レビュー | Android 17 タグがないため、公式文書の記述を AOSP diff で検証できない。 |

必須記入項目:
- Entry point / caller: 未確認。想定される entry point は Activity launch、manifest parsing、requested orientation evaluation、resizeability / aspect ratio policy、large screen display metrics 判定だが、AOSP evidence としては未採用。
- Relevant class or service responsibility: 未確認。
- Runtime path from app API / system event to changed code: 未確認。
- 除外した無関係なコードパス: Android 17 タグ不在のため、source path の採否判断自体を保留。

## 差分解釈

| 確認した差分 | 解釈 | 挙動変更との関係 | 信頼度 |
| --- | --- | --- | --- |
| Android 17 タグ間差分は利用不可 | ソース差分の種別はまだ分類できない | 公式文書の Android 16 behavior、SDK 36 opt-out、Android 17 / targetSdkVersion 37 opt-out removal、large screen condition を source diff で裏取りできていない | 低 |

必須分類:
- Added behavior: 未確認。
- Removed behavior: 未確認。公式文書上は Android 16 の opt-out が Android 17 / targetSdkVersion 37 以上では removed / unavailable になる可能性がある。
- Changed condition / gate: 未確認。targetSdkVersion 37 と `sw >= 600dp` gate がある可能性は高いが、AOSP 未確認。
- Changed default: 未確認。
- No behavior change found: 未確認。タグ不在のため「no behavior change」とは判断しない。

## 事実

事実:
- 公式 Behavior Change 文書は、Android 16 で API level 36 以上を target するアプリに対し、large screens (`sw >= 600dp`) で orientation、aspect ratio、resizability restrictions を無視する Platform API changes が導入されたと述べている。
- 公式文書は、SDK 36 では developers が opt out できたと述べている。
- 公式文書は、Android 17 / API level 37 以上を target するアプリでは、この opt-out が no longer available と述べている。
- ローカル `frameworks-base` には `android-16.0.0_r4` タグがある。
- ローカル `frameworks-base` には `android-17*` タグがない。
- 調査時点で `frameworks-base` working tree は clean。

観察:
- 公式ページ種別は targetSdkVersion 37 以上向けである。
- この項目は targetSdkVersion 37 条件に加えて、large screen (`sw >= 600dp`) という device/form factor condition を含む。
- Android 16 ですでに制約無視が導入されており、Android 17 の主な変更は SDK 36 で使えた opt-out の終了である。
- fixed orientation / fixed aspect ratio / non-resizable 前提の UI は、targetSdkVersion 37 で large screen 上の表示崩れや予期しない configuration change に遭遇する可能性がある。
- AOSP タグがないため、実装が本当に targetSdkVersion 37 gate で制御されているかは未確認。
- Compat framework entry の有無も未確認。

仮説:
- Android 17 / targetSdkVersion 37 以上では、Android 16 の opt-out manifest property または compat override を指定しても large screen 上で orientation / resizability / aspect ratio restrictions が無視される可能性が高い。
- Android 17 / targetSdkVersion 36 のアプリでは Android 16 と同様に opt-out が有効な可能性があるが、AOSP gate 未確認のため断定しない。
- `sw >= 600dp` の判定は display / window metrics / smallest width configuration に依存する可能性があるが、exact condition は未確認である。

結論:
- 現時点で顧客向けに確定できるのは、「公式文書上は Android 17 / targetSdkVersion 37 以上のアプリでは、large screen で orientation / resizability / aspect ratio restrictions を無視する Android 16 変更への opt-out が利用できなくなる」という範囲まで。
- AOSP gate、大画面判定、opt-out mechanism、compat framework default state が未確認のため、主分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

## 適用ゲート根拠

- targetSdkVersion 適用ゲート: 未確認。公式文書は targetSdkVersion 37 以上を示すが、AOSP gate evidence はない。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。Android 17 タグがないため検索未実施。
- @EnabledAfter / @EnabledSince / default state: 未確認。Android 17 タグがないため検索未実施。
- Build.VERSION / SDK_INT 適用ゲート: 未確認。
- DeviceConfig / resources config: 未確認。`sw >= 600dp` condition は公式文書上の device condition だが、AOSP 判定箇所は未確認。
- Permission/AppOps 適用ゲート: 公式抜粋では条件なし。
- Manifest/property 適用ゲート: 未確認。Android 16 opt-out mechanism と Android 17 removal の具体的 manifest / property 名は AOSP 未確認。
- 適用ゲート未検出: 未確認。Android 17 タグがないため「gate がない」とは判断しない。
- 適用ゲートの結論: 未確認。公式文書の wording から targetSdkVersion 37 + large screen condition と推定されるが、AOSP で検証できていない。
- ソース文脈からの推論: source context 未レビューのため未確定。

---

# 影響分析

## 影響を受けるアプリ

影響を受ける可能性があるアプリ:
- targetSdkVersion 37 へ更新し、large screens (`sw >= 600dp`) で動作するアプリ。
- `screenOrientation` で portrait / landscape 固定を前提にしているアプリ。
- `resizeableActivity=false` または固定 window size / non-resizable 前提の設計を持つアプリ。
- `minAspectRatio` / `maxAspectRatio` や固定 aspect ratio に依存するアプリ。
- Android 16 / SDK 36 で opt-out を利用して large screen 制約無視を回避していたアプリ。
- tablet、foldable、desktop windowing、ChromeOS など large screen 展開があるアプリ。

## 影響を受けにくいアプリ

影響が限定的または対象外と考えられるケース:
- large screen (`sw >= 600dp`) で利用されないアプリ。
- すでに orientation / resizability / aspect ratio constraints に依存せず adaptive UI を実装しているアプリ。
- Android 16 / targetSdkVersion 36 で opt-out を使っておらず、large screen で検証済みのアプリ。
- Android 17 AOSP タグ取得後に対象外 gate や exemption が確認されたケース。

---

# 顧客影響

## 影響度

- 人間による判断が必要

※ 最終 severity / priority は人間が判断する。このレポートでは確定しない。

## ビジネス影響

- ユーザー影響: large screen 上で固定向き / 固定比率前提の UI が広がる、回転する、リサイズされる、letterbox されないなどにより、表示崩れや操作不能が起きる可能性がある。
- 運用影響: tablet / foldable / desktop windowing の QA matrix、Android 16 opt-out 利用状況、targetSdkVersion 37 移行計画を確認する必要がある可能性がある。
- 開発影響: adaptive layout、multi-window、configuration change、responsive resource、Jetpack WindowManager / Compose adaptive UI などの対応が必要になる可能性がある。

---

# サービス影響例

このセクションは、公式文書と AOSP evidence から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1: Portrait 固定のスマートフォン前提 UI

- 対象サービス例: 決済、本人確認、縦長 feed、camera / scanner UI。
- 影響を受ける実装パターン: `screenOrientation="portrait"`、固定 aspect ratio、non-resizable 前提の Activity。
- 発生条件: Android 17 / targetSdkVersion 37、`sw >= 600dp` large screen で Android 16 opt-out が使えない場合。
- ユーザーに見える症状: tablet / foldable で横向きや大きな window に広がり、UI が崩れる可能性。
- 開発・運用への影響: large screen QA、adaptive layout、configuration change handling の見直しが必要になる可能性。
- 推奨対応候補: fixed orientation 前提を減らし、responsive layout と state restoration を整備する。
- 根拠: 公式 statement と report の expected behavior。
- 信頼度: 低
- 注意: exact opt-out mechanism と large screen 判定は AOSP タグ待ち。

## 例2: Tablet / foldable で non-resizable を指定する業務アプリ

- 対象サービス例: POS、医療業務、教育、店舗管理、在庫管理。
- 影響を受ける実装パターン: `resizeableActivity=false` や固定 window size 前提で画面密度・サイズを決め打ちする UI。
- 発生条件: targetSdkVersion 37 で large screen 制約無視が opt-out できない場合。
- ユーザーに見える症状: split-screen / freeform resize でボタン重なり、入力欄切れ、操作不能が起きる可能性。
- 開発・運用への影響: multi-window、fold / unfold、external display の test matrix 更新が必要になる可能性。
- 推奨対応候補: window size に応じた layout 分岐、scrollable content、minimum touch target を整備する。
- 根拠: 公式 statement と report の action candidates。
- 信頼度: 低
- 注意: 実サービスでの発生確認ではない。

---

# 対応候補

## 必須対応（Must）

- Android 16 の opt-out mechanism を利用しているか確認する。
- `screenOrientation`、`resizeableActivity`、`minAspectRatio`、`maxAspectRatio` など large screen 制約に関わる manifest / API usage を棚卸しする。
- `setRequestedOrientation()` / `getRequestedOrientation()` に依存している runtime logic を棚卸しする。
- `android:appCategory="game"` の対象可否、device aspect ratio settings で user opt-in された場合の扱い、`sw600dp` 未満 screen の例外を test plan に含める。
- `sw >= 600dp` 相当の tablet / foldable / desktop windowing 環境で、targetSdkVersion 37 build を検証する。
- orientation change、multi-window resize、split-screen、fold / unfold、freeform resize で UI が崩れないか確認する。
- Android 17 AOSP タグ入手後に、targetSdkVersion gate、opt-out removal、compat Change ID を再確認する。

## 推奨対応（Recommended）

- fixed orientation / fixed aspect ratio 前提を減らし、layout を adaptive / responsive にする。
- state restoration と configuration change handling を確認し、回転やリサイズで入力中データが失われないようにする。
- large screen 用 resource、navigation layout、two-pane / supporting pane、window size class 相当の layout 分岐を整備する。
- Android 16 の関連 behavior change と Android 17 の opt-out removal を分けて、既存 opt-out 依存のリスクを管理する。

## 任意対応（Optional）

- foldable posture、external display、ChromeOS / desktop mode など、`sw >= 600dp` 以外の large screen 実利用条件もテストする。
- UI screenshot / automated layout test を追加し、targetSdkVersion 37 移行時の表示崩れを検出する。

---

# 検証方法

## 検証マトリクス

| 端末 OS | targetSdkVersion | Compat flag | 期待される挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | default / opt-out if configured | 公式文書上、large screen 制約無視は導入済みだが SDK 36 では opt-out 可能。 |
| Android 17 | 36 | default / opt-out if available | 未確認。SDK 36 opt-out が維持されるかは AOSP gate 未確認。 |
| Android 17 | 37 | default | 公式文書上、SDK 36 で利用できた opt-out は利用不可。large screen で orientation / aspect ratio / resizability restrictions が無視される。 |
| Android 17 | 36 | force-enabled（利用可能な場合） | 未確認。Compat Change ID 未確認。 |
| Android 17 | 37 | force-disabled（利用可能な場合） | 未確認。Compat Change ID 未確認。 |

## 手順

- targetSdk変更: targetSdkVersion 36 と 37 の test build を用意する。
- Compat framework コマンド: 公式詳細ページは `UNIVERSAL_RESIZABLE_BY_DEFAULT` compat flag を enable して test できると説明している。具体的な command / package scope は Android 17 タグまたは compat framework page で再確認する。
- テスト方法: `sw >= 600dp` の emulator / tablet / foldable で、orientation fixed / resizable false / fixed aspect ratio の Activity を起動し、Android 16 opt-out あり / なし、targetSdkVersion 36 / 37 を比較する。
- 再現手順: Android 17 device / emulator で対象アプリを install し、portrait / landscape、split-screen、freeform resize、fold / unfold を実施する。requested orientation、actual orientation、window bounds、configuration changes、layout breakage を記録する。
- 期待結果: targetSdkVersion 37 のアプリでは、Android 16 で使えた opt-out が効かず、large screen 上で orientation / aspect ratio / resizability restrictions が platform により無視される。具体的な opt-out failure mode は AOSP タグと実機検証待ち。

---

# 結論

公式文書上、Android 17 / targetSdkVersion 37 以上のアプリでは、Android 16 で導入された large screen 上の orientation / resizability / aspect ratio constraints 無視に対する SDK 36 opt-out が利用できなくなる。large screen で固定向き・固定比率・非リサイズ前提の UI を持つアプリは、targetSdkVersion 37 移行前に adaptive UI と configuration change 対応を確認する必要がある。

ただし、Android 17 AOSP タグがローカル checkout にないため、実装 gate、opt-out removal、large screen 判定、compat framework の確認は未完了である。最終的な適用分類と顧客向け確定説明は、Android 17 AOSP タグ入手後に再調査が必要である。

---

# 人間の判断欄

最終優先度（Final Priority）:
- 人間による判断が必要

最終影響度:
- 人間による判断が必要

リリース判断:
- 人間による判断が必要

顧客通知優先度:
- 人間による判断が必要

判断（Decision）:
- 追加調査が必要

判断メモ:
- Android 17 AOSP タグ入手後に、AOSP evidence と compat framework evidence を確認してから最終判断する。

---

# 参照（References）

## ドキュメント

- https://developer.android.com/about/versions/17/behavior-changes-17
- https://developer.android.com/about/versions/16/behavior-changes-16#ignore-orientation
- https://developer.android.com/about/versions/17/changes/ff-restrictions-ignored

## AOSP

- ローカル `frameworks-base` では Android 17 は利用不可。
- From tag checked: `android-16.0.0_r4`
- To tag checked: ローカルに `android-17*` タグなし。

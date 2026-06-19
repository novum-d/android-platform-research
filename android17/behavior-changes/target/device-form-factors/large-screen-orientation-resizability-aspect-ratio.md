# 大画面で画面向き・リサイズ可否・アスペクト比制約を無視するプラットフォーム API の変更（sw >= 600dp）

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

関連文書:
- https://developer.android.com/about/versions/16/behavior-changes-16#ignore-orientation
- https://developer.android.com/about/versions/17/changes/ff-restrictions-ignored

セクション:
- Platform API changes to ignore orientation, resizability and aspect ratio constraints on large screens (sw>=600dp)

ページ種別:
- Android 17 以上をターゲットにするアプリ

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- TARGET_SDK_37_CONDITIONAL

公式文書からの適用条件判断:
- Android 16 では targetSdkVersion 36 以上のアプリに対し、大画面で orientation / aspect ratio / resizability restrictions を無視する変更が導入され、SDK 36 では opt-out が可能だった。
- Android 17 / targetSdkVersion 37 以上では、この opt-out が利用できなくなる。
- AOSP では Android 16 側の gate として `ActivityInfo.UNIVERSAL_RESIZABLE_BY_DEFAULT = 357141415L` が `@EnabledAfter(VANILLA_ICE_CREAM)`、Android 17 側の opt-out 無効化 gate として `AppCompatResizeOverrides.DISABLE_OPT_OUT_UNIVERSAL_RESIZABLE_BY_DEFAULT = 447301631L` が `@EnabledAfter(BAKLAVA)` として定義されている。

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 主条件ではない | opt-out 無効化は `@EnabledAfter(targetSdkVersion = BAKLAVA)`。 |
| targetSdkVersion 37 以上が必要か | Yes | `DISABLE_OPT_OUT_UNIVERSAL_RESIZABLE_BY_DEFAULT` が Android 17 target 相当で enabled。 |
| 追加の実行時条件があるか | ある | 大画面 `sw >= 600dp`、game 例外、orientation / aspect ratio / resizability restriction、opt-out property の有無。 |
| Compat Change ID が関係するか | Yes | `UNIVERSAL_RESIZABLE_BY_DEFAULT = 357141415L`、`DISABLE_OPT_OUT_UNIVERSAL_RESIZABLE_BY_DEFAULT = 447301631L`。 |

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
- targetSdkVersion: 37 以上。
- Display condition: `smallestScreenWidthDp >= WindowManager.LARGE_SCREEN_SMALLEST_SCREEN_WIDTH_DP`、つまり `sw >= 600dp`。
- App condition: game category ではないこと。AOSP `canBeUniversalResizeable` は `ApplicationInfo.CATEGORY_GAME` を除外する。
- Manifest / API condition: `screenOrientation`、`resizeableActivity`、`minAspectRatio` / `maxAspectRatio`、`setRequestedOrientation()` などの制約に依存していること。
- Opt-out condition: Android 16 では `android.window.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` による opt-out があり得るが、Android 17 target では `DISABLE_OPT_OUT_UNIVERSAL_RESIZABLE_BY_DEFAULT` により無効化される。

Compat framework:
- Change ID: `357141415L`
- 変更名: `UNIVERSAL_RESIZABLE_BY_DEFAULT`
- 既定状態: `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.VANILLA_ICE_CREAM)`。targetSdkVersion 36 以上で enabled。
- Change ID: `447301631L`
- 変更名: `DISABLE_OPT_OUT_UNIVERSAL_RESIZABLE_BY_DEFAULT`
- 既定状態: `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)`。targetSdkVersion 37 以上で enabled。
- テスト時に切り替え可能か: compat change として切り替え可能。

分類信頼度（Classification confidence）:
- High

分類根拠（Classification evidence）:
- 公式文書は Android 17 target で Android 16 opt-out が利用不可になると説明している。
- AOSP `ActivityInfo.UNIVERSAL_RESIZABLE_BY_DEFAULT` は fixed orientation / aspect ratio / resizability restrictions を無視し、app が available area を fill する change と説明している。
- AOSP `AppCompatResizeOverrides.DISABLE_OPT_OUT_UNIVERSAL_RESIZABLE_BY_DEFAULT` は opt-out property が Android 17 / API 37 から効かなくなると comment している。
- AOSP `DisplayContent.isLargeScreen` は `smallestScreenWidthDp >= WindowManager.LARGE_SCREEN_SMALLEST_SCREEN_WIDTH_DP` を大画面条件に使う。
- AOSP `ActivityRecord.canBeUniversalResizeable` は large screen かつ `UNIVERSAL_RESIZABLE_BY_DEFAULT` enabled の場合に universal resizable の候補にする。

---

# エグゼクティブサマリー（Executive Summary）

Android 17 では、targetSdkVersion 37 以上のアプリについて、Android 16 で許されていた大画面制約無視への opt-out が利用できなくなる。対象は `sw >= 600dp` の大画面で、orientation、resizability、aspect ratio の制約を platform が無視し、アプリを available area に合わせて表示する変更である。

AOSP では、Android 16 で導入された制約無視の gate `UNIVERSAL_RESIZABLE_BY_DEFAULT = 357141415L` と、Android 17 で opt-out property を無効化する gate `DISABLE_OPT_OUT_UNIVERSAL_RESIZABLE_BY_DEFAULT = 447301631L` を確認した。後者の comment は、`android.window.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` が Android 17 / API level 37 から効かなくなると明記している。

固定 portrait、non-resizable、固定 aspect ratio を前提にした UI は、tablet、foldable、desktop windowing、multi-window で表示崩れや想定外の resize が起きる可能性がある。

---

# 公式ドキュメント確認

## 原文（Statement）

ページタイトル:
- Behavior changes: Apps targeting Android 17 or higher

ページ URL:
- https://developer.android.com/about/versions/17/behavior-changes-17

セクションタイトル:
- Platform API changes to ignore orientation, resizability and aspect ratio constraints on large screens (sw>=600dp)

検証対象の原文:
- Android 16 では API level 36 以上を target するアプリについて、大画面で orientation / aspect ratio / resizability restrictions を無視する Platform API changes が導入された。
- SDK 36 では opt out できたが、Android 17 / API level 37 以上を target するアプリでは opt-out が利用できない。

## 解釈（Interpretation）

この変更は、large screen で app manifest / runtime API の固定表示制約よりも platform の resize / full area 表示を優先する large-screen compatibility change である。Android 17 target では、Android 16 で許されていた restricted resizability opt-out に依存できなくなる。

---

# 変更内容（What Changed）

公式文書上の変更点:
- Android 16 で targetSdkVersion 36 以上に `UNIVERSAL_RESIZABLE_BY_DEFAULT` 相当の制約無視が導入された。
- Android 16 / SDK 36 では opt-out が可能だった。
- Android 17 / targetSdkVersion 37 以上では opt-out が利用不可。
- `screenOrientation`、`resizeableActivity`、`minAspectRatio` / `maxAspectRatio`、`setRequestedOrientation()` / `getRequestedOrientation()` が大画面で無視され得る。
- game や user aspect ratio setting などの例外がある。

AOSP で確認した変更点:
- `ActivityInfo.UNIVERSAL_RESIZABLE_BY_DEFAULT` は fixed orientation / aspect ratio / resizability restrictions を無視し、available area を fill する change として定義される。
- `UNIVERSAL_RESIZABLE_BY_DEFAULT` は `@EnabledAfter(VANILLA_ICE_CREAM)` で、Android 16 target 以上に対応する。
- `AppCompatResizeOverrides.DISABLE_OPT_OUT_UNIVERSAL_RESIZABLE_BY_DEFAULT` は opt-out property を Android 17 / API 37 から無効化する。
- `DisplayContent.isLargeScreen` は `smallestScreenWidthDp >= 600dp` を大画面判定として使う。
- `DisplayContent.getIgnoreOrientationRequest` は大画面で orientation request を default ignored とする。
- `ActivityRecord.canBeUniversalResizeable` は game を除外し、大画面かつ `UNIVERSAL_RESIZABLE_BY_DEFAULT` enabled の場合に universal resizeable 候補にする。

---

# AOSP 調査（AOSP Investigation）

## checkout 状態（Checkout Status）

Commands checked before evidence use:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list android-17.0.0_r1
```

Result:
- `frameworks-base` working tree: clean at the time of investigation.
- From tag: `android-16.0.0_r4` exists.
- To tag: `android-17.0.0_r1` exists.

## 関連ファイル（Related Files）

- `core/java/android/content/pm/ActivityInfo.java`
- `services/core/java/com/android/server/wm/AppCompatResizeOverrides.java`
- `services/core/java/com/android/server/wm/ActivityRecord.java`
- `services/core/java/com/android/server/wm/DisplayContent.java`
- `services/core/java/com/android/server/wm/ActivityTaskManagerService.java`

## 確認したソース文脈（Source Context Reviewed）

| File / symbol | Android 16 baseline | Android 17 behavior | 関連性 |
| --- | --- | --- | --- |
| `ActivityInfo.UNIVERSAL_RESIZABLE_BY_DEFAULT` | targetSdkVersion 36 以上で enabled。opt-out 可能 | 引き続き制約無視の中核 gate | 大画面で orientation / aspect ratio / resizability restrictions を無視する change。 |
| `AppCompatResizeOverrides.DISABLE_OPT_OUT_UNIVERSAL_RESIZABLE_BY_DEFAULT` | targetSdkVersion 36 では disabled | targetSdkVersion 37 以上で enabled。opt-out property を無効化 | Android 17 target で opt-out 不可になる中核 evidence。 |
| `AppCompatResizeOverrides.allowRestrictedResizability` | opt-out property を読める | change enabled 時は property を読まず false を返す | Android 16 opt-out の無効化 path。 |
| `DisplayContent.isLargeScreen` | `sw >= 600dp` 判定 | 同じ | 大画面条件の implementation。 |
| `DisplayContent.getIgnoreOrientationRequest` | large screen で orientation request ignored | 同じ | 大画面で requested orientation を無視する WM path。 |
| `ActivityRecord.canBeUniversalResizeable` | game 以外、大画面かつ change enabled で候補 | 同じ | app category 例外と universal resizeable 判定。 |

Source context の補足:
- Entry point / caller: Activity launch / configuration resolution / display policy / resize policy。
- 関連性: WM policy が display の smallest width、app category、compat change、opt-out property を見て orientation / resize / aspect ratio 制約を尊重するか決める。
- Baseline Android behavior: Android 16 target では universal resizable は有効だが opt-out property が有効。
- Target Android behavior: Android 17 target では opt-out property が `DISABLE_OPT_OUT_UNIVERSAL_RESIZABLE_BY_DEFAULT` により無効化される。
- Source diff type: changed condition / gate、changed default。
- Excluded code paths: wallpaper / camera output aspect ratio / notification image aspect ratio など、app Activity の大画面表示制約と無関係な aspect ratio code は除外した。

## 差分解釈（Diff Interpretation）

| 観測した diff | 解釈 | Behavior Change との関連 | 信頼度 |
| --- | --- | --- | --- |
| `UNIVERSAL_RESIZABLE_BY_DEFAULT @EnabledAfter(VANILLA_ICE_CREAM)` | changed default | Android 16 target 以上で制約無視を有効化 | High |
| `DISABLE_OPT_OUT_UNIVERSAL_RESIZABLE_BY_DEFAULT @EnabledAfter(BAKLAVA)` | changed condition / gate | Android 17 target 以上で opt-out property を無効化 | High |
| `allowRestrictedResizability` が change enabled 時に false | removed opt-out behavior | Android 17 target で restricted resizability opt-out が効かない | High |
| `DisplayContent.isLargeScreen` / `getIgnoreOrientationRequest` | runtime condition | `sw >= 600dp` で orientation request を default ignored | High |

---

# 事実・観察・仮説・結論

## 事実（Facts）

- `frameworks-base` の `android-16.0.0_r4` と `android-17.0.0_r1` tag は存在し、調査時点の working tree は clean。
- `ActivityInfo.UNIVERSAL_RESIZABLE_BY_DEFAULT = 357141415L` は fixed orientation / aspect ratio / resizability restrictions を無視する change。
- `UNIVERSAL_RESIZABLE_BY_DEFAULT` は `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.VANILLA_ICE_CREAM)`。
- `AppCompatResizeOverrides.DISABLE_OPT_OUT_UNIVERSAL_RESIZABLE_BY_DEFAULT = 447301631L` は Android 17 / API 37 から `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` が効かなくなると comment している。
- `DISABLE_OPT_OUT_UNIVERSAL_RESIZABLE_BY_DEFAULT` は `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)`。
- `DisplayContent.isLargeScreen` は `smallestScreenWidthDp >= WindowManager.LARGE_SCREEN_SMALLEST_SCREEN_WIDTH_DP` を使う。

## 観察（Observations）

- 公式文書の Android 16 導入 / Android 17 opt-out removal は、AOSP の 2 段階の compat change と一致する。
- Android 17 で新しく「制約無視」が始まるのではなく、Android 16 target で始まった制約無視に対する opt-out が targetSdkVersion 37 で閉じられる。
- game category は universal resizable の対象外として扱われる。

## 仮説（Hypotheses）

- device user aspect ratio settings で app default behavior を選んだ場合の例外は、`PackageManager` の user aspect ratio override と `OVERRIDE_ANY_ORIENTATION_TO_USER` 周辺 policy によって実装されている。

## 結論（Conclusions）

- この Behavior Change は `TARGET_SDK_37_CONDITIONAL` と分類する。
- targetSdkVersion 37 以上では、大画面で orientation / resizability / aspect ratio 制約を維持するための Android 16 opt-out に依存できない。
- large screen / foldable / desktop windowing / multi-window で adaptive UI を検証する必要がある。
- 信頼度は High。AOSP gate、opt-out 無効化、large screen 判定、WM policy evidence が確認できた。

---

# 開発者影響（Developer Impact）

影響を受ける可能性が高いアプリ:
- portrait / landscape 固定を前提にしたアプリ
- `resizeableActivity=false` に依存するアプリ
- `minAspectRatio` / `maxAspectRatio` に依存するアプリ
- tablet / foldable / desktop windowing / multi-window で表示されるアプリ

対応候補:
- Android 16 opt-out property の利用を棚卸しする。
- `screenOrientation`、`resizeableActivity`、`minAspectRatio` / `maxAspectRatio`、`setRequestedOrientation()` 依存を確認する。
- `sw >= 600dp`、fold / unfold、multi-window resize、desktop windowing でレイアウトを検証する。
- game category や user aspect ratio setting 例外に依存する場合は端末別に確認する。

---

# テスト観点（Test Matrix）

| 端末 OS | targetSdkVersion | Display | Opt-out property | 期待挙動 |
| --- | --- | --- | --- | --- |
| Android 16 | 36 | `sw >= 600dp` | enabled | 制約無視から opt out できる想定。 |
| Android 17 | 36 | `sw >= 600dp` | enabled | Android 16 互換として opt-out が効く想定。 |
| Android 17 | 37 | `sw >= 600dp` | enabled | opt-out property は無効。orientation / resizability / aspect ratio restrictions は無視される想定。 |
| Android 17 | 37 | `sw < 600dp` | enabled/disabled | large screen 条件外。小画面用 policy として別扱い。 |

---

# 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断

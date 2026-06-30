# Edge to edge opt-out going away 調査レポート

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:
- `android16/AGENTS.md` の既定 scope は `android-16.0.0_r1` だが、この調査では依頼に従い、確認時点で利用可能な Android 16 最新 tag として `android-16.0.0_r4` を使った。

### Behavior Change 文書（Behavior Change Source）

Document:
- https://developer.android.com/about/versions/16/behavior-changes-16#edge-to-edge

Section:
- Edge to edge opt-out going away

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `TARGET_SDK_36_CONDITIONAL`

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 16 に OS アップデートしただけで適用されるか | No | 公式文書は apps targeting Android 16 / API level 36 の変更として掲載。AOSP でも `DISABLE_OPT_OUT_EDGE_TO_EDGE` が `@EnabledSince(targetSdkVersion = BAKLAVA)` |
| targetSdkVersion 36 以上が必要か | Yes | `PhoneWindow.DISABLE_OPT_OUT_EDGE_TO_EDGE` Change ID 377864165 が `BAKLAVA` 以上で default enabled |
| 追加の実行時条件があるか | Yes | Android 16 端末上で実行され、アプリが `R.attr.windowOptOutEdgeToEdgeEnforcement=true` に依存している場合に実質影響が出る |
| Compat Change ID が関係するか | Yes | AOSP: `DISABLE_OPT_OUT_EDGE_TO_EDGE` / 377864165。公開 compat framework changes ページでは該当 ID / name は検索で見つからなかった |

### 調査日（Investigation Date）

2026-06-30

### 信頼度（Confidence）

- High

理由:
- 公式 Behavior Change 原文、AOSP の `@ChangeId` / `@EnabledSince(BAKLAVA)`、`PhoneWindow` の opt-out 判定、属性コメントの Android 16 差分が一致している。
- 公開 compat framework changes ページに Change ID は掲載されていないが、AOSP annotation で default state と targetSdkVersion gate を確認できる。

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] OS update / all apps on Android 16 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 36 on Android 16+
- [x] targetSdkVersion >= 36, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [ ] Unknown / needs more evidence

必要な実行時条件（Required runtime conditions）:
- Android version: Android 16 以上。公式文書は Android 15 端末上では opt-out が引き続き機能すると明記している。
- targetSdkVersion: 36 以上。
- Device/form factor: 特定 form factor 条件は確認していない。edge-to-edge 表示そのものは system bars / display cutout / insets を含む window 表示に関係する。
- Permission/API/component condition: Activity / Window theme で `android:windowOptOutEdgeToEdgeEnforcement="true"` を使っていた場合に実質影響が出る。
- App state/process condition: Activity window 生成時、または application window 以外の window を追加する時の style 判定。

Compat framework:
- Change ID: 377864165
- Change name: `DISABLE_OPT_OUT_EDGE_TO_EDGE`
- Default state: `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)`。targetSdkVersion 36 以上で default enabled。
- Toggleable for testing: AOSP の compat ChangeId として存在するため compat override 対象になり得る。ただし Android Developers の公開 compat framework changes ページでは該当 entry は見つからなかった。

分類信頼度（Classification confidence）:
- High

分類根拠（Classification evidence）:
- Official documentation page: `behavior-changes-16` の `User experience and system UI` セクション。
- Original applicability statement: apps targeting Android 16 / API level 36 では opt-out 属性が deprecated and disabled。
- AOSP targetSdk gate: `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)` on Change ID 377864165。
- Compat framework entry: AOSP annotation あり。公開 compat page は `377864165` / `DISABLE_OPT_OUT_EDGE_TO_EDGE` / `ENFORCE_EDGE_TO_EDGE` で検索したが該当なし。

---

# エグゼクティブサマリー（Executive Summary）

Android 16 では、targetSdkVersion 36 以上のアプリで `R.attr.windowOptOutEdgeToEdgeEnforcement` による edge-to-edge 強制の回避が無効になる。
Android 16 へ OS アップデートしただけで targetSdkVersion 35 以下のアプリにこの変更が適用される根拠は確認していない。
影響があるのは、Android 15 の edge-to-edge 強制に対して opt-out 属性で対応していたアプリが、targetSdkVersion 36 に上げて Android 16 端末上で動く場合である。
対応候補は、opt-out 属性への依存をやめ、Compose / Views の insets 対応を実装・検証することである。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statement）

検証対象 statement:

```text
For apps targeting Android 16 (API level 36), R.attr#windowOptOutEdgeToEdgeEnforcement is deprecated and disabled, and your app can't opt-out of going edge-to-edge.
```

適用条件として、公式文書は次も述べている。

```text
Android 15 device: R.attr#windowOptOutEdgeToEdgeEnforcement continues to work.
Android 16 device: R.attr#windowOptOutEdgeToEdgeEnforcement is disabled.
```

## 解釈（Interpretation）

この変更は Android 16 の `behavior-changes-16` に掲載されているため、初期分類は targetSdkVersion 36 以上向けである。
ただし targetSdkVersion 36 だけでは実質影響は発生せず、Android 16 端末上で実行され、かつアプリが `windowOptOutEdgeToEdgeEnforcement=true` に依存している場合に表示挙動が変わる。
Android 15 端末上では、targetSdkVersion 36 にしても opt-out は引き続き機能するという例外が公式文書で明示されている。

---

# 変更内容（What Changed）

- Android 15 では、targetSdkVersion 35 以上のアプリに edge-to-edge が強制される一方、`windowOptOutEdgeToEdgeEnforcement=true` による opt-out が残っていた。
- Android 16 では、targetSdkVersion 36 以上のアプリに対して、その opt-out が無効化される。
- AOSP では `DISABLE_OPT_OUT_EDGE_TO_EDGE` Change ID が追加され、targetSdkVersion 36 以上で default enabled になる。
- `attrs.xml` の属性説明も、Android 15 の「将来 SDK で deprecated and disabled」から、Android 16 の「BAKLAVA 以上を target する app では ignored」に更新されている。

## 適用条件（Applicability）

### OS アップデート時の挙動（OS Update Behavior）

- Android 16 にアップデートしただけで適用されるか: 原則 No。
- targetSdkVersion に依存しない根拠: なし。AOSP の opt-out 無効化は `@EnabledSince(targetSdkVersion = BAKLAVA)` の compat change で制御される。
- Android 15 以前での挙動: Android 15 端末では、targetSdkVersion 36 のアプリでも `windowOptOutEdgeToEdgeEnforcement` は引き続き機能すると公式文書が明記している。

### targetSdkVersion 36 以上での挙動（targetSdkVersion 36 Behavior）

- targetSdkVersion 36 以上で適用されるか: Yes。ただし Android 16 端末上での実行が必要。
- Android 16 以外で targetSdkVersion 36 にした場合の挙動: 公式文書上、Android 15 端末では opt-out は機能し続ける。
- opt-out / temporary override の有無: `R.attr.windowOptOutEdgeToEdgeEnforcement` による opt-out は Android 16 / targetSdkVersion 36 では無効。AOSP compat override でテスト上の切り替えは可能な可能性があるが、公開 compat page には該当 entry は見つからなかった。

### その他の条件（Other Conditions）

- device/form factor: 特定の screen size / form factor gate は確認していない。
- permission: 権限条件なし。
- API usage: Window / Activity theme で `windowOptOutEdgeToEdgeEnforcement` を使っていた場合。
- manifest attribute: theme attribute `android:windowOptOutEdgeToEdgeEnforcement="true"`。
- component boundary: Activity window と、`WindowManagerGlobal.addView()` 経由の application window 以外の window private flag 付与で関連する。

---

# AOSP 調査（AOSP Investigation）

## 関連ファイル（Related Files）

- `core/java/com/android/internal/policy/PhoneWindow.java`
- `core/res/res/values/attrs.xml`
- `core/java/android/view/WindowManagerGlobal.java`
- `services/core/java/com/android/server/wm/ActivityRecord.java`
- `core/api/current.txt`

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル（File / symbol） | Android 15 の基準挙動（baseline） | Android 16 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `PhoneWindow.DISABLE_OPT_OUT_EDGE_TO_EDGE` | Change ID 377864165 は存在しない | `@ChangeId` + `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)` で追加 | 公式文書の「targetSdkVersion 36 以上で opt-out disabled」を直接制御する gate |
| `PhoneWindow.isEdgeToEdgeEnforced()` | style の `windowOptOutEdgeToEdgeEnforcement` が true なら edge-to-edge 強制を回避する | `isOptingOutEdgeToEdgeEnforcement()` 経由になり、opt-out enabled 判定が compat change に依存する | edge-to-edge を実際に強制するかどうかを判定する中心ロジック |
| `PhoneWindow.isOptOutEdgeToEdgeEnabled()` | なし | `DISABLE_OPT_OUT_EDGE_TO_EDGE` が enabled なら opt-out を false にする | targetSdkVersion 36 以上で style opt-out を無効化する直接根拠 |
| `attrs.xml` / `windowOptOutEdgeToEdgeEnforcement` | true の場合は enforcement が適用されないが、将来 SDK で disabled 予定 | BAKLAVA 以上を target する app では属性が ignored と明記 | public attr の開発者向け説明が公式 Behavior Change と一致する |
| `ActivityRecord.mOptOutEdgeToEdge` | style から opt-out を読む | style opt-out に加えて `PhoneWindow.isOptOutEdgeToEdgeEnabled()` を確認する | WindowManager 側の Activity 記録にも同じ opt-out 無効化 gate が反映されている |

必須記入項目（Required context）:
- Entry point / caller: Activity window の theme 読み込み、`PhoneWindow.generateLayout()`、`WindowManagerGlobal.addView()`、`ActivityRecord` の theme attribute cache。
- Relevant class or service responsibility: `PhoneWindow` は app window の decor / system bars / edge-to-edge enforcement を設定する。`ActivityRecord` は WindowManager 側で Activity の window style 情報を保持する。
- Runtime path from app API / system event to changed code: app theme の `windowOptOutEdgeToEdgeEnforcement` -> `PhoneWindow.isEdgeToEdgeEnforced()` / `isOptingOutEdgeToEdgeEnforcement()` -> `PRIVATE_FLAG_EDGE_TO_EDGE_ENFORCED` と decor fitting / bar color の設定。
- Why unrelated code paths were excluded: SystemUI / PrintSpooler / tests の theme 利用は platform 内部アプリまたはテスト資産であり、顧客アプリ向け Behavior Change の適用 gate 判定には使わない。`OVERRIDE_LAYOUT_IN_DISPLAY_CUTOUT_MODE` は edge-to-edge enforcement に隣接する別 Change ID であり、本件の primary gate ではない。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
| `DISABLE_OPT_OUT_EDGE_TO_EDGE = 377864165` と `@EnabledSince(BAKLAVA)` の追加 | Added behavior / changed condition | targetSdkVersion 36 以上で opt-out を無効化する条件が追加された | High |
| `isEdgeToEdgeEnforced()` が raw style boolean ではなく `isOptingOutEdgeToEdgeEnforcement()` を使うよう変更 | Changed condition / gate | style opt-out が compat change によって無視されるようになった | High |
| `attrs.xml` の説明が BAKLAVA 以上では ignored に変更 | API documentation behavior clarification | 公式 Behavior Change の開発者向け説明と一致する | High |
| `ActivityRecord` が `PhoneWindow.isOptOutEdgeToEdgeEnabled()` を考慮 | Added behavior / changed condition | WindowManager 側の Activity state にも同じ gate が伝播する | High |

必須分類（Required interpretation）:
- Added behavior: `DISABLE_OPT_OUT_EDGE_TO_EDGE` Change ID が Android 16 で追加された。
- Removed behavior: targetSdkVersion 36 以上かつ Android 16 上では、従来の style opt-out の効果が取り除かれる。
- Changed condition / gate: opt-out 判定が `windowStyle.getBoolean(...)` のみから、`isOptOutEdgeToEdgeEnabled()` との AND 条件に変わった。
- Changed default: targetSdkVersion 36 以上では `DISABLE_OPT_OUT_EDGE_TO_EDGE` が default enabled になり、opt-out enabled が false になる。
- No behavior change found: `R.attr.windowOptOutEdgeToEdgeEnforcement` の API surface 自体は残っている。既存属性の存在ではなく、実行時の解釈が変わっている。

## 事実（Evidence）

- 公式文書は、この項目を apps targeting Android 16 / API level 36 の Behavior Change として掲載している。
- Android 16 AOSP の `PhoneWindow.java` には Change ID 377864165 `DISABLE_OPT_OUT_EDGE_TO_EDGE` が追加され、`@EnabledSince(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)` が付いている。
- `Build.VERSION_CODES.BAKLAVA` は API level 36 である。
- Android 16 AOSP の `PhoneWindow.isOptOutEdgeToEdgeEnabled()` は、`DISABLE_OPT_OUT_EDGE_TO_EDGE` が enabled の場合に opt-out を許可しない。
- Android 16 AOSP の `attrs.xml` は、BAKLAVA 以上を target する app では `windowOptOutEdgeToEdgeEnforcement` が ignored と説明している。
- 公開 compat framework changes ページを `377864165`、`DISABLE_OPT_OUT_EDGE_TO_EDGE`、`309578419`、`ENFORCE_EDGE_TO_EDGE` で検索したが、該当 entry は見つからなかった。

## 観察（Observations）

- Android 15 の `PhoneWindow.isEdgeToEdgeEnforced()` は style の opt-out boolean を直接見ていた。
- Android 16 では style boolean が true でも、compat change `DISABLE_OPT_OUT_EDGE_TO_EDGE` が enabled なら opt-out として扱われない。
- `WindowManagerGlobal.addView()` と `ActivityRecord` も `PhoneWindow` の helper を使うため、client side と server side の両方で opt-out enabled 判定がそろっている。

## 仮説（Hypotheses）

- 実機または CTS では、compat override により `DISABLE_OPT_OUT_EDGE_TO_EDGE` を force-disabled にすると旧 opt-out 挙動を再現できる可能性がある。ただし公開 compat ページに掲載されていないため、顧客向けには rollback 手段として案内しない。

## 結論（Conclusions）

- 主分類は `TARGET_SDK_36_CONDITIONAL`。
- Android 16 / targetSdkVersion 35 では、本変更だけを理由に opt-out が無効になるとは判断しない。
- Android 16 / targetSdkVersion 36 では、`windowOptOutEdgeToEdgeEnforcement=true` に依存していた Activity / Window は opt-out できず、edge-to-edge 前提の insets 対応が必要になる。

## 適用ゲート根拠（Applicability Gate Evidence）

- targetSdkVersion gate: `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)` on `DISABLE_OPT_OUT_EDGE_TO_EDGE`。
- CompatChanges.isChangeEnabled / ChangeId: `CompatChanges.isChangeEnabled(DISABLE_OPT_OUT_EDGE_TO_EDGE)` / `info.isChangeEnabled(DISABLE_OPT_OUT_EDGE_TO_EDGE)`。
- @EnabledAfter / @EnabledSince / default state: `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)`。targetSdkVersion 36 以上で default enabled。
- Build.VERSION / SDK_INT gate: `Build.VERSION_CODES.BAKLAVA = 36`。
- DeviceConfig / resources config: 該当なし。
- Permission/AppOps gate: 該当なし。
- Manifest/property gate: theme attribute `windowOptOutEdgeToEdgeEnforcement=true` を使っている場合に影響が顕在化する。
- No gate found: 公開 compat framework changes ページには該当 entry が見つからなかった。
- Gate conclusion: Android 16 以上かつ targetSdkVersion 36 以上で `DISABLE_OPT_OUT_EDGE_TO_EDGE` が有効になり、style opt-out が無効化される。実質影響は opt-out 属性に依存していたアプリに限定される。
- Reasoning from source context: `PhoneWindow.isEdgeToEdgeEnforced()` が edge-to-edge enforcement の実行判定であり、その前段の opt-out 判定が targetSdkVersion 36 以上で無効化されるため。

---

# 影響分析（Impact Analysis）

## 影響を受けるアプリ（Affected Apps）

- Android 15 の edge-to-edge 強制に対して、`android:windowOptOutEdgeToEdgeEnforcement="true"` で一時回避していたアプリ。
- targetSdkVersion 36 へ更新し、Android 16 端末上で動作するアプリ。
- system bars / display cutout / IME / gesture navigation 周辺の insets 対応が不十分で、edge-to-edge 表示時にコンテンツがステータスバー・ナビゲーションバー・カットアウト領域と干渉するアプリ。

## 影響を受けないアプリ（Non-Affected Apps）

- targetSdkVersion 35 以下のまま Android 16 端末上で動作するアプリ。
- Android 15 端末上で動作する targetSdkVersion 36 アプリ。公式文書上、opt-out は引き続き機能する。
- すでに edge-to-edge / window insets 対応済みで、opt-out 属性に依存していないアプリ。
- `windowOptOutEdgeToEdgeEnforcement` を使っていないアプリ。

---

# 顧客影響（Customer Impact）

## 影響度（Impact Level）

- Medium

※ 仮評価。最終判断は人間が行う。

## ビジネス影響（Business Impact）

- ユーザー影響: edge-to-edge 未対応画面では、コンテンツ、ボタン、リスト末尾、入力欄が system bars や cutout と重なる可能性がある。
- 運用影響: targetSdkVersion 36 対応時の UI 回帰テスト対象が増える。
- 開発影響: opt-out 属性の削除と、Compose / Views それぞれの insets 対応が必要になる可能性がある。

---

# 対応候補（Required Actions）

## 必須対応（Must）

- targetSdkVersion 36 対応前に、`windowOptOutEdgeToEdgeEnforcement` の利用箇所を棚卸しする。
- Android 16 端末または emulator で、該当画面の system bars / cutout / IME overlap を確認する。
- opt-out 前提の画面では、WindowInsets / Compose insets / Views edge-to-edge guidance に従って余白・スクロール領域・タップ領域を調整する。

## 推奨対応（Recommended）

- Android 15 / targetSdkVersion 36 と Android 16 / targetSdkVersion 36 を別シナリオとして比較し、公式文書にある OS 差分を確認する。
- UI screenshot / visual regression test に、gesture navigation、3-button navigation、landscape、display cutout、IME 表示を含める。
- `windowOptOutEdgeToEdgeEnforcement` は移行完了後に削除する。

## 任意対応（Optional）

- compat override による isolated test が可能か、社内検証環境でのみ確認する。公開 compat page に掲載がないため、顧客向け rollback 手段としては扱わない。

---

# 検証方法（Verification Method）

## 検証マトリクス（Matrix）

| 端末 OS（Device OS） | targetSdkVersion | Compat flag | 期待挙動（Expected behavior） |
| --- | --- | --- | --- |
| Android 15 | 35 | default | edge-to-edge enforcement は Android 15 の targetSdkVersion 35 変更として有効。ただし `windowOptOutEdgeToEdgeEnforcement=true` による opt-out は機能する |
| Android 15 | 36 | default | 公式文書上、`windowOptOutEdgeToEdgeEnforcement` は引き続き機能する |
| Android 16 | 35 | default | 本変更の opt-out 無効化は適用されない。OS アップデートだけでは targetSdkVersion 36 向け挙動にならない |
| Android 16 | 36 | default | `DISABLE_OPT_OUT_EDGE_TO_EDGE` が default enabled。`windowOptOutEdgeToEdgeEnforcement` は無効で edge-to-edge を opt-out できない |
| Android 16 | 35 | force-enabled if available | `DISABLE_OPT_OUT_EDGE_TO_EDGE` を強制有効化できる場合、targetSdkVersion 35 でも opt-out 無効化単体の影響を検証できる可能性がある |
| Android 16 | 36 | force-disabled if available | `DISABLE_OPT_OUT_EDGE_TO_EDGE` を強制無効化できる場合、旧 opt-out 挙動へ戻るかを検証できる可能性がある |

## 手順（Steps）

- targetSdk変更: 同一 app で targetSdkVersion 35 と 36 の build variant を用意する。
- compat framework command: `adb shell am compat enable|disable 377864165 <package>` が利用可能か確認する。ただし公開 compat page に掲載がないため、利用可否は端末 build 依存として扱う。
- テスト方法: `windowOptOutEdgeToEdgeEnforcement=true` の Activity を用意し、status bar / navigation bar / IME / cutout と content の重なり、`decorFitsSystemWindows` 相当の挙動を確認する。
- 再現手順: Android 15 と Android 16 で同じ Activity を起動し、targetSdkVersion と compat override の組み合わせを切り替える。
- 期待結果: Android 16 / targetSdkVersion 36 / default では opt-out が効かず、edge-to-edge 前提の描画になる。

---

# 結論（Conclusion）

この変更は、Android 16 端末上で targetSdkVersion 36 以上にしたアプリに対し、`windowOptOutEdgeToEdgeEnforcement` による edge-to-edge 回避を無効化する。
OS アップデートだけで targetSdkVersion 35 以下のアプリへ同じ変更が適用されるとは説明しない。
顧客向けには、targetSdkVersion 36 対応時に opt-out 属性への依存をなくし、edge-to-edge / insets 対応を完了する必要がある、と説明する。

---

# 参照（References）

## ドキュメント（Documentation）

- https://developer.android.com/about/versions/16/behavior-changes-16#edge-to-edge
- https://developer.android.com/about/versions/15/behavior-changes-15#edge-to-edge
- https://developer.android.com/reference/android/R.attr#windowOptOutEdgeToEdgeEnforcement
- https://developer.android.com/develop/ui/compose/layouts/insets
- https://developer.android.com/develop/ui/views/layout/edge-to-edge
- https://developer.android.com/about/versions/16/reference/compat-framework-changes

## AOSP

- `core/java/com/android/internal/policy/PhoneWindow.java`
- `core/res/res/values/attrs.xml`
- `core/java/android/view/WindowManagerGlobal.java`
- `services/core/java/com/android/server/wm/ActivityRecord.java`
- `core/api/current.txt`

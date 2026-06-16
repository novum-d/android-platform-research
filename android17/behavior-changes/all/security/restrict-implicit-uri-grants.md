# Implicit URI grants の制限

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

比較元:
- android-16.0.0_r4

比較先:
- TBD: Android 17 AOSP tag

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

### Behavior Change 文書（Behavior Change Source）

文書:
- https://developer.android.com/about/versions/17/behavior-changes-all

関連文書:
- https://developer.android.com/reference/android/content/Intent#ACTION_SEND
- https://developer.android.com/reference/android/content/Intent#ACTION_SEND_MULTIPLE
- https://developer.android.com/reference/android/provider/MediaStore#ACTION_IMAGE_CAPTURE
- https://developer.android.com/reference/android/content/Intent#FLAG_GRANT_READ_URI_PERMISSION
- https://developer.android.com/reference/android/content/Intent#FLAG_GRANT_WRITE_URI_PERMISSION
- https://developer.android.com/reference/android/os/StrictMode.VmPolicy.Builder#detectImplicitUriPermissionGrant()

セクション:
- Restrict implicit URI grants

ページ種別:
- Behavior changes: all apps

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- 公式文書は Android 17 の `Behavior changes: all apps` ページにこの項目を掲載している。
- ただし、本文は "Starting in Android 18" で system が implicit URI permission grants を自動付与しなくなると説明しており、Android 17 で即時に自動付与が停止するとは述べていない。
- Android 17 文書上の主な開発者対応は、`ACTION_SEND`、`ACTION_SEND_MULTIPLE`、`ACTION_IMAGE_CAPTURE` で URI を渡すときに、明示的に `FLAG_GRANT_READ_URI_PERMISSION` / `FLAG_GRANT_WRITE_URI_PERMISSION` を付けることである。
- Android 17 では、`StrictMode.VmPolicy.Builder.detectImplicitUriPermissionGrant()` と logcat message によって、implicit grant に依存している箇所を検出できると説明されている。
- local `frameworks-base` に Android 17 AOSP tag がないため、StrictMode detection API、log emission、implicit grant path、Android 18 gate、compat framework entry は未確認である。

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 即時 enforcement はない可能性が高いが未検証 | 公式文書は enforcement を Android 18 starting と説明。Android 17 では検出・移行 guidance と読める。 |
| targetSdkVersion 37 以上が必要か | この guidance では不要と考えられるが未検証 | All apps ページ掲載。本文に targetSdkVersion 37 gate は示されていない。 |
| 追加の実行時条件があるか | 関連条件としてある | URI を含む `ACTION_SEND` / `ACTION_SEND_MULTIPLE` / `ACTION_IMAGE_CAPTURE` intent を起動し、implicit grant に依存している場合。 |
| Compat Change ID が関係するか | 未確認 | Android 17 tag と compat framework evidence が未確認。 |

### 調査日（Investigation Date）

2026-06-15

### 信頼度（Confidence）

- Low

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] OS update / all apps on Android 17 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 37 on Android 17+
- [ ] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [x] Unknown / 追加根拠が必要

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 文書上の guidance。自動 grant 停止は Android 18 starting と説明されており、Android 17 での enforcement gate は未確認。
- targetSdkVersion: 公式文書上、この項目に targetSdkVersion 37 条件は示されていない。AOSP targetSdkVersion gate 未確認。
- Device/form factor: 公式文書からは条件なし。
- Permission/API/component condition: URI を含む `ACTION_SEND`、`ACTION_SEND_MULTIPLE`、`ACTION_IMAGE_CAPTURE` intent、`FLAG_GRANT_READ_URI_PERMISSION`、`FLAG_GRANT_WRITE_URI_PERMISSION`、`StrictMode.VmPolicy.Builder.detectImplicitUriPermissionGrant()`。
- App state/process condition: app が target app に URI を渡し、system の implicit URI permission grant に依存している場合。

Compat framework:
- Change ID: 未確認
- 変更名: 未確認
- 既定状態: 未確認
- テスト時の切り替え可否: 未確認

分類信頼度（Classification confidence）:
- Low

分類根拠（Classification evidence）:
- 公式ドキュメントページ: `behavior-changes-all`
- 検証対象の適用条件文: all apps page に掲載されているが、本文は Android 18 から自動 grant を停止すると説明しており、Android 17 では explicit grant への移行と StrictMode / logcat による検出を案内している。
- AOSP targetSdk gate: 未確認。local `frameworks-base` に `android-17*` tag がない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# エグゼクティブサマリー（Executive Summary）

Android 17 の all apps ページは、URI を含む `ACTION_SEND`、`ACTION_SEND_MULTIPLE`、`ACTION_IMAGE_CAPTURE` intent に対する implicit URI permission grants の制限計画を示している。公式文書上、system が read / write URI permissions を自動付与しなくなるのは Android 18 starting と説明されており、Android 17 で即時に自動 grant が停止するとは読み取れない。

Android 17 では、`StrictMode.VmPolicy.Builder.detectImplicitUriPermissionGrant()` や logcat message を使って、implicit grant に依存している箇所を検出し、`FLAG_GRANT_READ_URI_PERMISSION` / `FLAG_GRANT_WRITE_URI_PERMISSION` を明示的に付ける移行準備を進める項目として扱う。

現時点では local `frameworks-base` に Android 17 AOSP tag がないため、StrictMode detection path、log emission、URI grant implementation、compat framework entry は未確認である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とし、Android 17 AOSP tag 公開後に再調査する。

---

# 公式ドキュメント確認

## 原文（Statement）

Page title:
- Behavior changes: all apps

Page URL:
- https://developer.android.com/about/versions/17/behavior-changes-all

ページ種別:
- all apps

Section title:
- Restrict implicit URI grants

検証対象の原文:
- Currently, if an app launches an intent with a URI and action `ACTION_SEND`, `ACTION_SEND_MULTIPLE`, or `ACTION_IMAGE_CAPTURE`, the system automatically grants read and write URI permissions to the target app.
- Starting in Android 18, the system will no longer automatically grant these permissions.
- Apps should explicitly grant the relevant URI permissions instead of relying on system implicit grants.
- Apps can use `StrictMode.VmPolicy.Builder.detectImplicitUriPermissionGrant()` to detect usage.
- Apps can monitor logcat for the message `Please set the grant explicitly in the app`.
- For `ACTION_SEND` and `ACTION_SEND_MULTIPLE`, apps should add `FLAG_GRANT_READ_URI_PERMISSION`.
- For `ACTION_IMAGE_CAPTURE`, apps should add both `FLAG_GRANT_READ_URI_PERMISSION` and `FLAG_GRANT_WRITE_URI_PERMISSION`.

## 解釈（Interpretation）

この項目は、Android 17 で即時に URI permission grant の挙動を変えるというより、Android 18 で予定されている自動 grant 停止に備える migration guidance と読むのが自然である。公式文書は "Starting in Android 18" と説明しており、Android 17 で `ACTION_SEND` などの implicit grant が直ちに停止するとは明記していない。

開発者にとっての実務上の意味は、system が暗黙に URI permission を付けてくれる前提をやめ、intent を送る側が必要な read / write permission flag を明示的に付けることである。Android 17 では StrictMode と logcat により、移行対象を検出する段階として扱う。

---

# 変更内容（What Changed）

公式文書上の変更点:
- 現在は URI を含む `ACTION_SEND`、`ACTION_SEND_MULTIPLE`、`ACTION_IMAGE_CAPTURE` intent を起動すると、system が target app に read / write URI permissions を自動付与する。
- Android 18 starting では、この自動付与が行われなくなる。
- Android 17 文書では、Android 18 に備えて relevant URI permissions を明示的に grant することが推奨されている。
- `StrictMode.VmPolicy.Builder.detectImplicitUriPermissionGrant()` により implicit grant usage を violation として検出できる。
- system が implicit grant を設定したとき、logcat に `Please set the grant explicitly in the app` を含む exception message が出ると説明されている。
- `ACTION_SEND` / `ACTION_SEND_MULTIPLE` では `FLAG_GRANT_READ_URI_PERMISSION` を明示的に追加する。
- `ACTION_IMAGE_CAPTURE` では `FLAG_GRANT_READ_URI_PERMISSION` と `FLAG_GRANT_WRITE_URI_PERMISSION` の両方を明示的に追加する。

AOSP で未確認の点:
- Android 17 で `detectImplicitUriPermissionGrant()` が新規追加 / 有効化されたか。
- Android 17 で implicit grant 時の log emission が追加されたか。
- Android 18 enforcement gate がどこにあるか。
- `ACTION_SEND` / `ACTION_SEND_MULTIPLE` / `ACTION_IMAGE_CAPTURE` に対する current implicit grant path。
- `FLAG_GRANT_READ_URI_PERMISSION` / `FLAG_GRANT_WRITE_URI_PERMISSION` の明示 grant と implicit grant の precedence。
- targetSdkVersion gate、OS version gate、compat framework Change ID の有無。

## 適用条件（Applicability）

この変更がいつ適用されるかを OS 条件と targetSdkVersion 条件に分けて説明する。

### OS アップデート時の挙動（OS Update Behavior）

- Android 17 に OS アップデートしただけで適用されるか: 公式文書上、Android 17 で即時に implicit URI grant が停止するとは確認できない。Android 18 starting の変更に向けた検出 / migration guidance と読む。
- targetSdkVersion に依存しない根拠: All apps ページに掲載されているが、本文には targetSdkVersion 37 条件はない。AOSP gate 未確認。
- Android 16 以前での挙動: 公式文書は current behavior として、対象 intent では system が read / write URI permissions を target app に自動付与すると説明している。AOSP baseline diff は未確認。

### targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- targetSdkVersion 37 以上で適用されるか: 公式文書上、この項目に targetSdkVersion 37 条件は示されていない。AOSP gate 未確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: 未確認。公式文書は Android 17 all apps page 上の guidance として説明している。
- opt-out / temporary override の有無: 未確認。公式文書は opt-out ではなく explicit grant への移行を示している。

### その他の条件（Other Conditions）

- device/form factor: 公式文書からは条件なし。
- permission: URI permission grants が関係する。対象 URI の provider permission / grantUriPermissions / FileProvider 設定も実装上関係する可能性があるが AOSP 未確認。
- API usage: `Intent.ACTION_SEND`、`Intent.ACTION_SEND_MULTIPLE`、`MediaStore.ACTION_IMAGE_CAPTURE`、`FLAG_GRANT_READ_URI_PERMISSION`、`FLAG_GRANT_WRITE_URI_PERMISSION`、`StrictMode.VmPolicy.Builder.detectImplicitUriPermissionGrant()`。
- manifest attribute: provider 側の `grantUriPermissions` や `FileProvider` 設定が関係する可能性がある。
- component boundary: intent launch、URI permission grant manager、activity start、content provider URI permission enforcement にまたがる可能性。

---

# AOSP 調査（AOSP Investigation）

## checkout 状態（Checkout Status）

確認コマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list 'android-17*'
```

結果:
- `frameworks-base` の `status --short` は空で、dirty working tree は確認されなかった。
- `android-16.0.0_r4` tag は存在する。
- `android-17*` tag は local checkout に存在しない。

根拠上の制約:
- Android 17 AOSP tag が local `frameworks-base` にないため、`android-16.0.0_r4` と Android 17 tag の明示的な source diff は実行できない。
- そのため、local working tree や未確定 branch を platform evidence として扱わない。
- 本レポートの AOSP-backed conclusion は Low confidence に留める。

## 関連ファイル（Related Files）

Android 17 AOSP tag 未取得のため、tag diff に基づく related files は未確定。

Android 17 tag 公開後に確認すべき候補:
- `core/java/android/content/Intent.java`
- `core/java/android/os/StrictMode.java`
- `services/core/java/com/android/server/uri/` 以下の URI grant management path
- `services/core/java/com/android/server/wm/` または activity start / intent dispatch path
- `core/java/android/provider/MediaStore.java`
- `core/java/androidx/core/content/FileProvider` 相当は platform 外の可能性があるため、platform evidence と分けて扱う
- compat framework 定義ファイル内の implicit URI grant / Android 18 enforcement 関連 Change ID

## 確認したソース文脈（Source Context Reviewed）

AOSP tag diff は未実行。以下は公式文書から見た確認予定の source context であり、AOSP evidence ではない。

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| Intent launch / activity start URI grant path | 対象 intent で system が implicit read / write grant を付与すると公式文書が説明 | Android 17 では検出 / migration guidance、Android 18 で自動 grant 停止予定と説明 | implicit URI grant の実行時挙動を決める中心 path |
| `StrictMode.VmPolicy.Builder.detectImplicitUriPermissionGrant()` | 未確認 | implicit grant usage を violation として検出できると公式文書が説明 | Android 17 で移行対象を検出する developer-facing API |
| log emission path | 未確認 | `Please set the grant explicitly in the app` message を監視できると公式文書が説明 | 既存 app が implicit grant に依存している箇所を運用検出できる |
| `Intent.FLAG_GRANT_READ_URI_PERMISSION` / `FLAG_GRANT_WRITE_URI_PERMISSION` | explicit grant flag として既存 | Android 18 に備え明示指定が推奨される | mitigation の正当性を確認する public API |

必須記入項目:
- Entry point / caller: 未確認。想定される entry point は app の `startActivity()` / `sendIntent` -> activity start / intent dispatch -> URI grant manager -> target app の content URI access。
- Relevant class or service responsibility: intent action 判定、URI permission grant、StrictMode violation、log emission。
- Runtime path from app API / system event to changed code: app が URI 付き `ACTION_SEND` / `ACTION_SEND_MULTIPLE` / `ACTION_IMAGE_CAPTURE` intent を起動 -> system が implicit grant を付与するか判定 -> Android 17 では検出 / log、Android 18 では自動付与停止、という path が想定される。AOSP evidence としては未確認。
- Why unrelated code paths were excluded: tag diff 未実行のため、除外判断は未完了。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
| Android 17 tag 未取得のため source diff 未確認 | 公式文書上は Android 17 immediate enforcement ではなく Android 18 migration guidance / detection と読める | implicit URI grant の将来制限、StrictMode detection、explicit grant migration が説明されている | Low |

必須分類:
- Added behavior: 未確認。公式文書上、Android 17 で `detectImplicitUriPermissionGrant()` / log detection が利用できると説明されているが、AOSP diff 未確認。
- Removed behavior: 未確認。公式文書上、自動 grant の停止は Android 18 starting と説明されており、Android 17 で削除されたとは説明されていない。
- Changed condition / gate: 未確認。Android 18 enforcement gate、targetSdkVersion gate、compat gate は AOSP tag 待ち。
- Changed default: 未確認。Android 17 で implicit grant default が変わったとは公式文書上確認できない。
- No behavior change found: 未確認。AOSP tag 不在のため断定しない。ただし公式文書上は Android 18 advance warning / migration guidance の可能性が高い。

## 事実（Evidence）

事実:
- 公式文書は `Restrict implicit URI grants` を Android 17 `Behavior changes: all apps` ページに掲載している。
- 公式文書は、現在は URI を含む `ACTION_SEND`、`ACTION_SEND_MULTIPLE`、`ACTION_IMAGE_CAPTURE` intent で system が target app に read / write URI permissions を自動付与すると説明している。
- 公式文書は、Android 18 starting で system がこれらの permissions を自動付与しなくなると説明している。
- 公式文書は、system implicit grant に頼らず、relevant URI permissions を明示的に付与することを推奨している。
- 公式文書は、`StrictMode.VmPolicy.Builder.detectImplicitUriPermissionGrant()` を使って usage を検出できると説明している。
- 公式文書は、`Please set the grant explicitly in the app` を含む logcat message を監視できると説明している。
- 公式文書は、`ACTION_SEND` / `ACTION_SEND_MULTIPLE` には `FLAG_GRANT_READ_URI_PERMISSION` を追加するよう説明している。
- 公式文書は、`ACTION_IMAGE_CAPTURE` には `FLAG_GRANT_READ_URI_PERMISSION` と `FLAG_GRANT_WRITE_URI_PERMISSION` の両方を追加するよう説明している。

観察:
- All apps ページ掲載だが、本文は Android 17 で自動 grant を止めるとは述べていない。
- Android 17 では、StrictMode / logcat による検出と explicit grant への移行を進める準備期間として扱うのが自然である。
- `ACTION_IMAGE_CAPTURE` は書き込み先 URI を camera app に渡す用途が多いため、read だけでなく write grant が必要になる可能性が高い。

仮説:
- Android 17 には implicit grant が発生した際の StrictMode violation / log warning が追加され、Android 18 で enforcement が有効になる可能性がある。
- Android 18 enforcement は OS version gate または compat framework gate で制御される可能性がある。
- targetSdkVersion ではなく platform version による all-apps change として導入される可能性があるが、AOSP evidence がないため未確定。

結論:
- 現時点の確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE`。公式文書上は Android 17 で即時 enforcement される変更ではなく、Android 18 に向けた advance warning / migration guidance と見る。
- 顧客向けには、Android 17 で今すぐ URI sharing / camera capture が壊れる変更としてではなく、Android 18 に備えて explicit grant flag を追加する準備項目として説明する。

## 適用ゲート根拠（Applicability Gate Evidence）

- targetSdkVersion gate: 未確認。公式文書上、この項目に targetSdkVersion 37 条件はない。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。
- @EnabledAfter / @EnabledSince / default state: 未確認。
- Build.VERSION / SDK_INT gate: 未確認。公式文書は enforcement を Android 18 starting と説明している。
- DeviceConfig / resources config: 未確認。
- Permission/AppOps gate: URI permission grant が関係するが、AOSP 未確認。
- Manifest/property gate: provider 側 `grantUriPermissions` / exported / authority / FileProvider 設定が関係する可能性があるが、AOSP 未確認。
- No gate found: 未確認。AOSP tag 未取得のため gate search 未実行。
- Gate conclusion: 公式文書上は Android 18 enforcement + Android 17 migration guidance。Android 17 runtime gate は未確認。AOSP evidence 未取得のため `UNKNOWN_NEEDS_MORE_EVIDENCE`。
- Reasoning from source context: source context は未確認。公式文書の page type と statement のみから一次判断している。

---

# 影響分析（Impact Analysis）

## 影響を受けるアプリ（Affected Apps）

- URI を含む `ACTION_SEND` / `ACTION_SEND_MULTIPLE` intent で他アプリへ content URI を共有するアプリ。
- `ACTION_IMAGE_CAPTURE` で camera app に出力先 URI を渡すアプリ。
- system の implicit read / write URI grant に依存し、intent flags を明示していないアプリ。
- Android 18 以降も同じ共有 / 撮影 flow を維持する必要があるアプリ。
- Android 17 で StrictMode detection を有効にしたときに violation / log message が出るアプリ。

## 影響を受けないアプリ（Non-Affected Apps）

- content URI を他アプリへ渡さないアプリ。
- 対象 intent action を使わないアプリ。
- `FLAG_GRANT_READ_URI_PERMISSION` / `FLAG_GRANT_WRITE_URI_PERMISSION` を適切に明示しているアプリ。
- file sharing を official FileProvider / grant flags の組み合わせで実装しているアプリ。
- Android 17 時点では、公式文書上 immediate enforcement は未確認。ただし Android 18 での影響は再確認が必要。

---

# 顧客影響（Customer Impact）

## 影響度（Impact Level）

- 要確認

※ 最終 severity / priority は人間が判断する。このレポートでは確定しない。

## ビジネス影響（Business Impact）

- ユーザー影響: Android 17 時点で即時に share / camera capture が失敗する変更とは公式文書上確認できない。Android 18 以降、未移行のアプリでは shared URI を target app が読めない、camera app が output URI に書き込めない、といった失敗が起きる可能性がある。
- セキュリティ影響: system の暗黙 grant に頼らず、intent sender が必要な permission を明示することで、URI permission の意図が明確になる。
- 開発影響: URI 付き intent の棚卸し、grant flag の追加、StrictMode / logcat による検出、共有先 / camera app との相互運用確認が必要になる。
- 運用影響: share flow、画像添付、camera capture、document export などのユーザー導線で Android 18 への移行リスクを監視する必要がある。

---

# サービス影響例（Service Impact Examples）

このセクションは、公式文書と未確認の AOSP 調査観点から導いた「起こりうる影響例」を記録する。
特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: 画像共有アプリ

- 対象サービス例: social sharing、chat attachment、document export。
- 影響を受ける実装パターン: `ACTION_SEND` に content URI を入れて共有するが、`FLAG_GRANT_READ_URI_PERMISSION` を付けていない。
- 発生条件: Android 18 enforcement 後、target app が implicit grant を受けられなくなる場合。
- ユーザーに見える症状: 共有先アプリで添付画像 / document を開けない。
- 開発・運用への影響: share intent 生成箇所に read grant flag を追加し、主要共有先アプリで検証する必要がある。
- 推奨対応候補: `ACTION_SEND` / `ACTION_SEND_MULTIPLE` の全 call site に `FLAG_GRANT_READ_URI_PERMISSION` を明示する。
- 根拠: 公式文書は `ACTION_SEND` / `ACTION_SEND_MULTIPLE` に read grant flag を追加するよう説明している。
- Confidence（信頼度）: Low。Android 18 enforcement details は未確認。
- 注意: 実サービスで発生確認した事実ではない。

## 例2（Example 2）: カメラ撮影フロー

- 対象サービス例: profile photo capture、receipt scanner、identity verification。
- 影響を受ける実装パターン: `ACTION_IMAGE_CAPTURE` に output URI を渡すが、read / write grant flags を明示していない。
- 発生条件: Android 18 enforcement 後、camera app が output URI に書き込む permission を受けられなくなる場合。
- ユーザーに見える症状: 撮影後に画像が保存されない、camera result が失敗する。
- 開発・運用への影響: camera intent 生成箇所に read / write grant flags を追加し、複数 camera app / device で検証する必要がある。
- 推奨対応候補: `ACTION_IMAGE_CAPTURE` には `FLAG_GRANT_READ_URI_PERMISSION | FLAG_GRANT_WRITE_URI_PERMISSION` を明示する。
- 根拠: 公式文書は `ACTION_IMAGE_CAPTURE` に read / write grant flags の両方を含めるよう説明している。
- Confidence（信頼度）: Low。Android 18 enforcement details は未確認。
- 注意: 実サービスで発生確認した事実ではない。

---

# 対応候補（Required Actions）

## 必須対応（Must）

- URI を含む `ACTION_SEND`、`ACTION_SEND_MULTIPLE`、`ACTION_IMAGE_CAPTURE` の call site を棚卸しする。
- `ACTION_SEND` / `ACTION_SEND_MULTIPLE` には `FLAG_GRANT_READ_URI_PERMISSION` を明示する。
- `ACTION_IMAGE_CAPTURE` には `FLAG_GRANT_READ_URI_PERMISSION` と `FLAG_GRANT_WRITE_URI_PERMISSION` を明示する。
- Android 17 で `StrictMode.VmPolicy.Builder.detectImplicitUriPermissionGrant()` を有効にし、implicit grant 依存箇所を検出する。
- logcat の `Please set the grant explicitly in the app` message を確認する。

## 推奨対応（Recommended）

- URI grant flags を intent helper / share helper に集約し、call site ごとの抜け漏れを減らす。
- `ACTION_SEND_MULTIPLE` で複数 URI を渡す場合も grant flag が intent 全体に付いているか確認する。
- provider 側の `grantUriPermissions`、FileProvider paths、authority、exported state を確認する。
- Android 17 では warning / StrictMode 検出、Android 18 では enforcement という前提で QA matrix を作る。
- 主要 share target / camera app / document consumer で相互運用を確認する。

## 任意対応（Optional）

- URI 共有箇所を静的解析や lint rule で検出する。
- Android 18 preview / beta が利用可能になった時点で、implicit grant なしの挙動を実機確認する。
- Android 17 AOSP tag 公開後に、StrictMode API と log emission の実装を確認する。

---

# 検証方法（Verification Method）

変更を確認する方法。

## 検証マトリクス（Matrix）

| 端末 OS（Device OS） | targetSdkVersion | Compat flag / test control | 期待挙動（Expected behavior） |
| --- | --- | --- | --- |
| Android 16 | 36 | default | baseline。対象 intent で implicit grant により target app が URI を読めるか確認する。 |
| Android 17 | 36 | default + StrictMode | 公式文書上、immediate enforcement は未確認。StrictMode / logcat で implicit grant usage を検出できるか確認する。 |
| Android 17 | 37 | default + StrictMode | targetSdkVersion 37 による差分がないか確認する。公式文書上は targetSdkVersion gate なし。 |
| Android 17 | 36 | force-enabled if available | Compat flag 未確認。存在する場合は implicit grant restriction 単体の影響を確認する。 |
| Android 17 | 37 | force-disabled if available | Compat flag 未確認。存在する場合は rollback / opt-out 可能性を確認する。 |

## 手順（Steps）

- targetSdk変更: targetSdkVersion 36 / 37 の両方で検証し、targetSdkVersion 差分があるか確認する。
- compat framework command: 未確認。Android 17 tag 公開後に Change ID が存在する場合のみ force-enable / force-disable を検証する。
- テスト方法:
  - `ACTION_SEND` + URI + grant flag なし。
  - `ACTION_SEND` + URI + `FLAG_GRANT_READ_URI_PERMISSION`。
  - `ACTION_SEND_MULTIPLE` + 複数 URI + grant flag なし / あり。
  - `ACTION_IMAGE_CAPTURE` + output URI + grant flag なし。
  - `ACTION_IMAGE_CAPTURE` + output URI + read / write grant flags。
  - `StrictMode.VmPolicy.Builder.detectImplicitUriPermissionGrant()` 有効 / 無効。
- 再現手順:
  - content URI を提供する test provider / FileProvider を用意する。
  - 対象 intent を grant flag なしで起動する。
  - target app が URI を読めるか、Android 17 で StrictMode violation / logcat message が出るか確認する。
  - grant flag を明示して同じ flow を実行し、target app が URI を読めるか確認する。
- 期待結果:
  - Android 17 では implicit grant usage が検出できる可能性がある。
  - Android 18 enforcement 後は、grant flag なし flow が失敗し、explicit grant flag あり flow が成功することが期待される。

---

# 結論（Conclusion）

`Restrict implicit URI grants` は Android 17 all apps ページに掲載されているが、公式文書の主張は「Android 17 で即時に implicit URI grants を停止する」ではなく、「Android 18 starting で自動 grant を停止するため、Android 17 時点で検出し explicit grant へ移行する」という guidance である。

ただし、Android 17 AOSP tag が local `frameworks-base` に存在しないため、StrictMode detection API、log emission、URI grant path、compat framework entry は未確認である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

Android app developer は、URI を含む share / capture intent を棚卸しし、必要な `FLAG_GRANT_READ_URI_PERMISSION` / `FLAG_GRANT_WRITE_URI_PERMISSION` を明示的に追加する準備を進める必要がある。

---

# 人間の判断欄

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- Android 17 AOSP tag 公開後に追加調査が必要

判断理由候補:
- 公式文書上は Android 18 enforcement の advance warning であり、Android 17 即時の runtime behavior change とは断定できない。
- 顧客影響は URI 付き intent の利用、grant flag の明示有無、provider 設定、Android 18 enforcement details に依存する。

---

# 参照（References）

## ドキュメント（Documentation）

- https://developer.android.com/about/versions/17/behavior-changes-all
- https://developer.android.com/reference/android/content/Intent#ACTION_SEND
- https://developer.android.com/reference/android/content/Intent#ACTION_SEND_MULTIPLE
- https://developer.android.com/reference/android/provider/MediaStore#ACTION_IMAGE_CAPTURE
- https://developer.android.com/reference/android/content/Intent#FLAG_GRANT_READ_URI_PERMISSION
- https://developer.android.com/reference/android/content/Intent#FLAG_GRANT_WRITE_URI_PERMISSION
- https://developer.android.com/reference/android/os/StrictMode.VmPolicy.Builder#detectImplicitUriPermissionGrant()

## AOSP

- 未確認。local `frameworks-base` に Android 17 AOSP tag がないため、tag diff による source evidence は未取得。

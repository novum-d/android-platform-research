# Implicit URI grants の制限

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
- TARGET_SDK_37_CONDITIONAL

公式文書からの初期適用条件判断:
- 公式文書は Android 17 の `Behavior changes: all apps` ページにこの項目を掲載している。
- ただし、本文は "Starting in Android 18" で system が implicit URI permission grants を自動付与しなくなると説明しており、Android 17 で即時に自動付与が停止するとは述べていない。
- Android 17 AOSP 根拠 では `StrictMode.VmPolicy.Builder.detectImplicitUriPermissionGrant()` が追加され、`StrictMode.detectAll()` では feature flag と compat change が有効な場合に自動検出へ含まれる。
- compat ChangeId `DETECT_IMPLICIT_URI_PERMISSION_GRANT` は `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)` であり、Android 17 / targetSdkVersion 37 以上の StrictMode 検出に関係する。

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 自動 grant 停止は No。明示 StrictMode 利用時は検出可能 | `Intent` は Android 18 以降の廃止予定 message を出しつつ、restriction flag が無効なら grant flag を追加し続ける。 |
| targetSdkVersion 37 以上が必要か | StrictMode detectAll の自動検出では Yes | `DETECT_IMPLICIT_URI_PERMISSION_GRANT` は `@EnabledAfter(targetSdkVersion = BAKLAVA)`。 |
| 追加の実行時条件があるか | ある | URI 付き `ACTION_SEND` / `ACTION_SEND_MULTIPLE` / `ACTION_IMAGE_CAPTURE` で explicit grant flags が欠けていること。StrictMode VM policy または detectAll が有効であること。 |
| Compat Change ID が関係するか | Yes | `DETECT_IMPLICIT_URI_PERMISSION_GRANT`。ID は source snippet 外だが ChangeId と target gate は確認済み。 |

### 調査日（Investigation Date）

2026-06-18

### 信頼度（Confidence）

- Medium

理由:
- Android 17 AOSP tag で StrictMode API、targetSdk gate、Intent 側の detection/log path を確認できた。
- Android 18 enforcement は future behavior として文書化されており、Android 17 tag では feature flags により restriction path が guarded される。
- restriction flags の release default と Android 18 側の最終 gate はこの調査範囲では未確認のため High confidence にはしない。

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] OS update / all apps on Android 17 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 37 on Android 17+
- [x] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [ ] Unknown / 追加根拠が必要

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 では検出 / warning / migration support。自動 grant 停止は公式文書上 Android 18 starting。
- targetSdkVersion: StrictMode `detectAll()` による自動検出は targetSdkVersion 37 以上。
- Device/form factor: 公式文書からは条件なし。
- Permission/API/component condition: URI を含む `ACTION_SEND`、`ACTION_SEND_MULTIPLE`、`ACTION_IMAGE_CAPTURE` intent、`FLAG_GRANT_READ_URI_PERMISSION`、`FLAG_GRANT_WRITE_URI_PERMISSION`、`StrictMode.VmPolicy.Builder.detectImplicitUriPermissionGrant()`。
- App state/process condition: app が target app に URI を渡し、system の implicit URI permission grant に依存している場合。

Compat framework:
- Change ID: `DETECT_IMPLICIT_URI_PERMISSION_GRANT`
- 変更名: implicit URI permission grant StrictMode detection
- 既定状態: `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)`
- テスト時の切り替え可否: compat change と feature flag `strict_mode_violation_for_implicit_uri_grants_enabled` により制御される。

分類信頼度（Classification confidence）:
- Medium

---

# エグゼクティブサマリー

Android 17 の all apps ページは、URI を含む `ACTION_SEND`、`ACTION_SEND_MULTIPLE`、`ACTION_IMAGE_CAPTURE` intent に対する implicit URI permission grants の制限計画を示している。公式文書上、system が read / write URI permissions を自動付与しなくなるのは Android 18 starting であり、Android 17 で即時に自動 grant が停止する変更ではない。

Android 17 AOSP では移行支援が実装されている。`StrictMode.VmPolicy.Builder.detectImplicitUriPermissionGrant()` / `permitImplicitUriPermissionGrant()` が追加され、`Intent` は missing grant flag を検出すると、Android 18 以降に implicit URI grant が廃止される旨の message を生成する。StrictMode VM policy が有効なら `ImplicitUriPermissionGrantViolation` が発火する。

また、`ACTION_SEND`、`ACTION_SEND_MULTIPLE`、`ACTION_IMAGE_CAPTURE` には restriction feature flags が存在する。flag が有効な場合は implicit grant を skip する path があるが、Android 17 文書は enforcement を Android 18 starting と説明しているため、Android 17 では検出・移行準備の項目として扱う。

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

この項目は、Android 17 で即時に URI permission grant の挙動を止めるというより、Android 18 で予定されている自動 grant 停止に備える migration guidance と読む。Android 17 では StrictMode と logcat により、移行対象を検出する段階として扱う。

---

# AOSP 調査（AOSP Investigation）

## チェックアウト状態

確認コマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list android-17.0.0_r1
```

結果:
- `frameworks-base` の `status --short` は空で、未コミット変更 は確認されなかった。
- `android-16.0.0_r4` tag は存在する。
- `android-17.0.0_r1` tag は存在する。

## 関連ファイル（Related Files）

確認した主なファイル:
- `core/java/android/os/StrictMode.java`
- `core/java/android/os/strictmode/ImplicitUriPermissionGrantViolation.java`
- `core/java/android/content/Intent.java`
- `core/api/current.txt`
- `core/java/android/security/responsible_apis_flags.aconfig`

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `StrictMode.VmPolicy.Builder.detectImplicitUriPermissionGrant()` | なし | flagged API として追加 | 公式文書が案内する検出 API そのもの |
| `StrictMode.DETECT_IMPLICIT_URI_PERMISSION_GRANT` | なし | `@ChangeId @EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)` の VM detection として追加 | targetSdkVersion 37 gate の evidence |
| `StrictMode.detectAll()` | implicit URI grant 検出を含まない | feature flag と compat change が有効なら `detectImplicitUriPermissionGrant()` を含める | Android 17 target アプリで StrictMode detectAll を使う場合の自動検出 path |
| `StrictMode.onImplicitUriPermissionGrant()` | なし | `ImplicitUriPermissionGrantViolation` を VM policy violation として通知 | violation 発火 path |
| `Intent.migrateExtraStreamToClipData()` の `ACTION_SEND` path | missing read grant flag でも implicit grant を追加する legacy path | missing read grant flag で message / StrictMode violation / stats を出し、restriction flag が off なら read grant を追加し続ける | `ACTION_SEND` の移行警告と Android 18 enforcement 準備 |
| `Intent.migrateExtraStreamToClipData()` の `ACTION_SEND_MULTIPLE` path | missing read grant flag でも implicit grant を追加する legacy path | missing read grant flag で message / StrictMode violation / stats を出し、restriction flag が off なら read grant を追加し続ける | `ACTION_SEND_MULTIPLE` の移行警告 |
| `Intent` の image capture path | missing read/write grant flag でも implicit grant を追加する legacy path | missing read/write grant flag で message / StrictMode violation / stats を出し、restriction flag が off なら read/write grant を追加し続ける | `ACTION_IMAGE_CAPTURE` の移行警告 |
| `responsible_apis_flags.aconfig` | restriction / strict mode flags なし | `implicit_uri_grants_restricted_for_send_action`、`implicit_uri_grants_restricted_for_sendmultiple_imagecapture_actions`、`strict_mode_violation_for_implicit_uri_grants_enabled` が追加 | Android 17 では detection と enforcement-prep が flag guarded であることを示す |

## 実装 path（Runtime Path）

1. app が URI 付き `ACTION_SEND`、`ACTION_SEND_MULTIPLE`、または `ACTION_IMAGE_CAPTURE` intent を作る。
2. `FLAG_GRANT_READ_URI_PERMISSION` / `FLAG_GRANT_WRITE_URI_PERMISSION` が欠けている場合、`Intent` の migration path が implicit grant 依存を検出する。
3. `strict_mode_violation_for_implicit_uri_grants_enabled` と StrictMode VM policy が有効なら、`StrictMode.onImplicitUriPermissionGrant()` が `ImplicitUriPermissionGrantViolation` を発火する。
4. logcat には `Please set the grant explicitly in the app` を含む message が出る。
5. Android 17 では restriction flag が無効なら legacy 互換のため grant flag が追加され続ける。
6. restriction flag が有効な場合は implicit grant を skip する path がある。公式文書は、この enforcement が Android 18 starting であると説明している。

## 差分確認（Diff Review）

確認コマンド:

```bash
git -C frameworks-base diff android-16.0.0_r4 android-17.0.0_r1 -- \
  core/java/android/os/StrictMode.java \
  core/java/android/content/Intent.java \
  core/api/current.txt \
  core/java/android/security/responsible_apis_flags.aconfig
```

確認結果:
- `StrictMode.VmPolicy.Builder.detectImplicitUriPermissionGrant()` と `permitImplicitUriPermissionGrant()` が API surface に追加された。
- `StrictMode` に `DETECT_IMPLICIT_URI_PERMISSION_GRANT`、`vmImplicitUriPermissionGrantEnabled()`、`onImplicitUriPermissionGrant()` が追加された。
- `Intent` の `ACTION_SEND`、`ACTION_SEND_MULTIPLE`、image capture path に missing grant flag の warning / StrictMode / restriction flag branch が追加された。
- implicit grant restriction 用 feature flags と StrictMode violation flag が追加された。

差分解釈:
- Source diff type: added detection behavior / added API surface / guarded future restriction path。
- Behavior Change を支える evidence: Android 17 で StrictMode / logcat による検出が可能になり、Android 18 enforcement の warning text と guarded skip path が実装されている。
- 分類を支える evidence: StrictMode `detectAll()` 側の compat change は `@EnabledAfter(BAKLAVA)` で、targetSdkVersion 37 以上に関係する。

## 関連しない / 除外した path

- `UriGrantsManagerService` の通常 grant enforcement は URI permission の一般処理であり、本項目の Android 17 warning / migration path とは分けて扱う。
- `AppFunctionUriGrant` など App Functions 関連の URI grant API は別機能であり、本項目の `ACTION_SEND` / `ACTION_IMAGE_CAPTURE` implicit grant とは別。

---

# 適用条件（Applicability）

## OS アップデート時の挙動（OS Update Behavior）

- Android 17 に OS アップデートしただけで適用されるか: 自動 grant 停止は No。Android 17 では detection / warning が中心。
- targetSdkVersion に依存しない根拠: app が明示的に `detectImplicitUriPermissionGrant()` を有効化すれば targetSdkVersion に関係なく検出できる可能性がある。ただし `detectAll()` への自動追加は targetSdkVersion 37 gate。
- Android 16 以前での挙動: 対象 intent では system が implicit URI permission grant を追加していた。

## targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- targetSdkVersion 37 以上で適用されるか: StrictMode `detectAll()` の自動検出では Yes。
- Android 17 / targetSdkVersion 36: explicit StrictMode API を使わない限り、detectAll による自動検出は有効にならない想定。
- Android 17 / targetSdkVersion 37: feature flag と compat change が有効で、StrictMode detectAll を使うと implicit URI grant を VM violation として検出する。
- opt-out / temporary override の有無: `permitImplicitUriPermissionGrant()` で StrictMode detection を無効化できるが、移行回避ではなく検出抑止である。

## その他の条件（Other Conditions）

- device/form factor: 公式文書からは条件なし。
- permission: URI permission grants が関係する。provider 側の `grantUriPermissions` や `FileProvider` 設定も実装上関係する。
- API usage: `Intent.ACTION_SEND`、`Intent.ACTION_SEND_MULTIPLE`、`MediaStore.ACTION_IMAGE_CAPTURE`、`FLAG_GRANT_READ_URI_PERMISSION`、`FLAG_GRANT_WRITE_URI_PERMISSION`、`StrictMode.VmPolicy.Builder.detectImplicitUriPermissionGrant()`。
- app behavior: content URI を他アプリへ渡し、必要な grant flag を明示していない場合。

---

# 開発者影響

影響を受ける可能性がある app:
- content URI を他アプリへ共有するアプリ。
- camera app に output URI を渡すアプリ。
- share sheet、画像 / document 共有、camera capture、添付ファイル送信で grant flag を明示していないアプリ。

影響が限定的な app:
- URI を他アプリへ渡さないアプリ。
- すでに `FLAG_GRANT_READ_URI_PERMISSION` / `FLAG_GRANT_WRITE_URI_PERMISSION` を明示しているアプリ。
- StrictMode を本番で有効にしていないアプリは Android 17 ではユーザー影響が限定的だが、Android 18 enforcement に備えた修正は必要。

ユーザー影響:
- Android 17 では主に開発時 / テスト時の StrictMode violation や logcat warning として見える。
- Android 18 以降では、明示 grant がない share / capture flow で target app が URI を読めない、または書き込めない可能性がある。

---

# サービス影響例

このセクションは、公式文書と AOSP 根拠から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: Google Photos / LINE / Slack への画像共有

- 具体サービス例: Google Photos、LINE、Slack、Gmail へ画像・PDF・添付ファイルを共有するアプリ。
- 影響を受ける実装パターン: `ACTION_SEND` / `ACTION_SEND_MULTIPLE` で content URI を渡すが、`FLAG_GRANT_READ_URI_PERMISSION` を明示していない実装。
- 発生条件: Android 17 では StrictMode / logcat detection、有効化設定によって violation として検出される。将来 enforcement では target app が URI を読めない可能性がある。
- ユーザーに見える症状: Android 17 では通常は開発時 warning。将来 release では共有先で添付ファイルが開けない、送信に失敗する可能性。
- 技術的に起きていること: system による暗黙 URI grant に依存しており、明示 grant flag が欠落している。
- 推奨対応シーン: share sheet、chat attachment、email attachment、document export。
- 検証観点: StrictMode `detectImplicitUriPermissionGrant()`、`detectAll()`、read grant flag、複数 URI、FileProvider 設定。
- 根拠: 公式文書、`StrictMode.VmPolicy.Builder.detectImplicitUriPermissionGrant()`、`Intent.ACTION_SEND` / `ACTION_SEND_MULTIPLE` warning path。
- Confidence（信頼度）: Medium。Android 17 は detection / migration period が中心。
- 注意: 上記サービスで発生確認した事実ではない。共有元アプリの intent flags と provider 設定に依存する。

## 例2（Example 2）: カメラアプリ連携でプロフィール画像や本人確認画像を撮影する flow

- 具体サービス例: メルカリ、PayPay、銀行アプリ、保険アプリなどのプロフィール画像・本人確認書類撮影 flow。
- 影響を受ける実装パターン: `MediaStore.ACTION_IMAGE_CAPTURE` に output URI を渡すが、read / write grant flag を明示しない実装。
- 発生条件: Android 17 で StrictMode detection を有効化したテスト、または将来 release の implicit grant restriction が有効な場合。
- ユーザーに見える症状: 将来 enforcement では camera app が output URI に書き込めない、撮影後の画像取得に失敗する可能性。
- 技術的に起きていること: camera app へ必要な URI permission が明示されず、従来の implicit grant に依存している。
- 推奨対応シーン: identity verification、receipt capture、expense report、profile image capture。
- 検証観点: `FLAG_GRANT_READ_URI_PERMISSION` と `FLAG_GRANT_WRITE_URI_PERMISSION`、camera app 差分、Android 17 StrictMode。
- 根拠: 公式文書と AOSP の image capture path warning / StrictMode API。
- Confidence（信頼度）: Medium。
- 注意: 上記サービスで発生確認した事実ではない。Android 17 時点の主要目的は Android 18 enforcement への移行準備である。

---

# 推奨対応候補（Recommended Action Candidates）

開発者向け対応候補:
- URI 付き `ACTION_SEND`、`ACTION_SEND_MULTIPLE`、`ACTION_IMAGE_CAPTURE` の call site を棚卸しする。
- `ACTION_SEND` / `ACTION_SEND_MULTIPLE` には `FLAG_GRANT_READ_URI_PERMISSION` を明示する。
- `ACTION_IMAGE_CAPTURE` には `FLAG_GRANT_READ_URI_PERMISSION` と `FLAG_GRANT_WRITE_URI_PERMISSION` を明示する。
- StrictMode の `detectImplicitUriPermissionGrant()` または `detectAll()` をテストで有効にし、logcat の `Please set the grant explicitly in the app` を確認する。
- Android 18 enforcement に備えて、Android 17 のうちに explicit grant へ移行する。

---

# テスト観点（Test Matrix）

| 端末 OS | targetSdkVersion | 条件 | 期待挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | URI 付き send / capture intent、grant flag なし | baseline。implicit grant により target app が URI を読める可能性。 |
| Android 17 | 36 | StrictMode 明示検出なし、grant flag なし | legacy grant が維持され、logcat warning が出る可能性。 |
| Android 17 | 37 | StrictMode detectAll、grant flag なし | `ImplicitUriPermissionGrantViolation` と warning を検出する想定。 |
| Android 17 | 37 | explicit read/write grant flags あり | StrictMode violation なしで target app が URI にアクセスできる想定。 |

---

# 顧客向け説明（Customer-facing Explanation）

Android 17 の文書では、URI を含む `ACTION_SEND`、`ACTION_SEND_MULTIPLE`、`ACTION_IMAGE_CAPTURE` intent に対して system が暗黙に read / write URI permissions を付与する挙動が、Android 18 から廃止される予定だと説明されています。Android 17 では、StrictMode と logcat により依存箇所を検出し、明示的な grant flag へ移行する準備ができます。

`ACTION_SEND` と `ACTION_SEND_MULTIPLE` では `FLAG_GRANT_READ_URI_PERMISSION` を付けます。`ACTION_IMAGE_CAPTURE` では camera app が output URI に書き込めるよう、`FLAG_GRANT_READ_URI_PERMISSION` と `FLAG_GRANT_WRITE_URI_PERMISSION` の両方を付けます。

---

# 未解決事項（Open Questions）

- `implicit_uri_grants_restricted_for_send_action` と `implicit_uri_grants_restricted_for_sendmultiple_imagecapture_actions` の Android 17 / Android 18 release default。
- Android 18 enforcement の最終 gate と targetSdkVersion 条件。
- 公式文書が all apps ページに掲載していることと、StrictMode detectAll の targetSdkVersion 37 gate の関係。

---

# 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断

---

## 再検証記録（2026-08-22）

### 調査日（Investigation Date）

- 2026-08-22

### 公式ドキュメント再確認（Original Documentation Recheck）

- Android 17 の all-apps / target Behavior Change ページを再取得し、このレポートが参照する公式 section の掲載と適用範囲を再確認した。
- 公式ページの最終更新表示: all-apps / target: 2026-08-14 UTC。
- Android 17 compat framework 一覧は 2026-08-22 時点でも HTTP 404 のため、公式 Behavior Change 文書と AOSP annotation / gate を正とした。
- 既存の引用は短い要約として扱い、適用条件は公式ページ種別と AOSP gate の両方で再評価した。

### AOSP 証拠ワークスペース（AOSP Evidence Workspaces）

| AOSP project | Official remote URL | Checkout path | Working tree | From tag / resolved commit | To tag / resolved commit | Comparison command | Dirty risk / limitations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `platform/frameworks/base` | `https://android.googlesource.com/platform/frameworks/base` | `frameworks-base/` | Clean | `android-16.0.0_r4` / `45034f0663f960d9ee5fb0a101a4732b71f6e2f4` | `android-17.0.0_r1` / `94b4c163b7dfe5ce3607f7bb8456f9573f7de57d` | `git -C frameworks-base diff --no-renames --name-only android-16.0.0_r4 android-17.0.0_r1` | なし。明示タグ比較のため working tree の内容は根拠に含めない。 |

### ソース文脈・差分解釈の再確認（Source Context Reviewed / Diff Interpretation）

- 各 official remote で Android 16 / 17 の最新通常リリースタグが `android-16.0.0_r4` / `android-17.0.0_r1` のままであることを確認した。
- 上表の project-level `--name-only` 比較を再実行し、既存本文の path / symbol 別 source context、gate、追加・削除・条件変更・既定値変更・差分なしの解釈を再確認した。
- タグと解決済み commit が既存調査の比較対象から変わっていないため、本文の evidence record を別タグへ機械的に置換していない。
- 実機 Observed は新規実施していない。既存の「未実施」「未確認」および不足根拠はそのまま維持した。

### 事実（Facts）

- `android-16.0.0_r4` と `android-17.0.0_r1` は 2026-08-22 時点の最新通常リリースタグである。
- 上表に再検証時の working tree 状態を記録し、official remote、両タグ、解決済み commit を確認した。展開中または dirty の working tree は根拠に使用していない。
- 公式 section と AOSP evidence の比較 pair は一致している。

### 観察（Observations）

- 最新タグが変わっていないため、今回の再検証で既存の source diff 解釈を変更する新しい AOSP tag evidence は生じなかった。
- report 内に残る Medium / Low confidence、OEM / Mainline / QPR 条件、未確認の module enforcement は解消したものとして扱わない。

### 仮説（Hypotheses）

- 新しい仮説は追加しない。既存本文で仮説または可能性として記載した事項は、実機・製品 build・未確認 module の evidence が得られるまで事実へ昇格しない。

### 結論（Conclusions）

- 既存本文の主分類、confidence、対応候補を維持する。既存の不足根拠がある場合はその制約も維持する。
- 全件再検証の横断記録は [`android17/analysis/REVALIDATION_2026-08-22.md`](../../../analysis/REVALIDATION_2026-08-22.md) を参照する。

### Human Decision

- この再検証では最終 priority、severity、release readiness、顧客説明優先度を変更していない。
- 人間の判断は [Android 17 Decision Log](../../../decisions/DECISION_LOG.md) を正とする。

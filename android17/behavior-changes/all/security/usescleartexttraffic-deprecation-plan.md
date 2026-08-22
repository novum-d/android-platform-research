# usesCleartextTraffic の deprecation plan

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
- https://developer.android.com/guide/topics/manifest/application-element#usesCleartextTraffic
- https://developer.android.com/privacy-and-security/security-config
- https://developer.android.com/training/articles/security-config#CleartextTrafficPermitted

セクション:
- usesCleartextTraffic deprecation plan

ページ種別:
- Behavior changes: all apps

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- TARGET_SDK_37_CONDITIONAL

公式文書からの初期適用条件判断:
- 公式文書は Android 17 の `Behavior changes: all apps` ページにこの項目を掲載している。
- ただし本文は "In a future release" と説明しており、Android 17 で全アプリに即時 runtime behavior change があるとは述べていない。
- Android 17 AOSP tag では `usesCleartextTraffic` attribute が `@Deprecated` / flagged API になり、Network Security Config 側に `DEPRECATE_USES_CLEARTEXT_TRAFFIC = 415007211L` が追加されている。
- 実装上は feature flag `deprecate_uses_cleartext_traffic2` と compat change が両方有効な場合、`android:usesCleartextTraffic` 由来の default config が false に上書きされる。
- aconfig の説明は「targetSdk version C+ で `usesCleartextTraffic` を無視する」としているが、`ManifestConfigSource` の ChangeId は `@Disabled` で、default-enabled evidence はこの checkout だけでは完了していない。

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | No / 少なくとも無条件適用ではない | 実装は feature flag + compat change の内側。公式文書も future deprecation plan と説明。 |
| targetSdkVersion 37 以上が必要か | 意図としては Yes / 条件付き | aconfig description は targetSdk C+ で無視すると説明。ただし ChangeId annotation は `@Disabled` で default state の追加確認が必要。 |
| 追加の実行時条件があるか | ある | Network Security Config を指定していない、`usesCleartextTraffic` に依存している、feature flag と compat change が有効、cleartext HTTP が必要。 |
| Compat Change ID が関係するか | Yes | `ManifestConfigSource.DEPRECATE_USES_CLEARTEXT_TRAFFIC = 415007211L`。 |

### 調査日（Investigation Date）

2026-06-18

### 信頼度（Confidence）

- Medium

理由:
- Android 17 AOSP tag で ChangeId、feature flag、Network Security Config 側の実装、テストを確認できた。
- ただし ChangeId は `@Disabled` で、targetSdkVersion 37 以上に対する default enable 状態は annotation だけでは確認できない。
- 公式文書も Android 17 即時 enforcement ではなく future deprecation plan として説明しているため、High confidence にはしない。

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] OS update / all apps on Android 17 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 37 on Android 17+
- [x] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [ ] Unknown / 追加根拠が必要

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 以上の実装で確認。
- targetSdkVersion: aconfig description 上は C / Android 17 以上。ただし compat default state は追加確認が必要。
- Device/form factor: 公式文書からは条件なし。
- Permission/API/component condition: unencrypted HTTP connection、`android:usesCleartextTraffic`、Network Security Configuration、`cleartextTrafficPermitted`。
- App state/process condition: Network Security Config を指定せず、manifest の `usesCleartextTraffic` だけで cleartext を許可している場合に影響する可能性がある。

Compat framework:
- Change ID: `415007211`
- 変更名: `DEPRECATE_USES_CLEARTEXT_TRAFFIC`
- 既定状態: source annotation は `@Disabled`。targetSdk C+ default enable はこの checkout だけでは未確認。
- テスト時の切り替え可否: `UsesCleartextTrafficDeprecationTest` が `@EnableCompatChanges` / `@DisableCompatChanges` と `@EnableFlags` / `@DisableFlags` の組み合わせを検証している。

分類信頼度（Classification confidence）:
- Medium

---

# エグゼクティブサマリー

Android 17 の all apps ページは、将来 release で `usesCleartextTraffic` element を deprecate する計画を示している。Android 17 で全アプリに対して即時かつ無条件に HTTP cleartext 接続を壊す変更とは読めない。

一方、Android 17 AOSP tag には実装準備が入っている。`usesCleartextTraffic` attribute は `@Deprecated` / flagged API となり、`ManifestConfigSource` には `DEPRECATE_USES_CLEARTEXT_TRAFFIC = 415007211L` が追加された。feature flag `deprecate_uses_cleartext_traffic2` と compat change が両方有効な場合、manifest の `FLAG_USES_CLEARTEXT_TRAFFIC` は Network Security Config の default source で false に上書きされる。

顧客向けには、`usesCleartextTraffic` だけに依存せず、必要な domain を Network Security Configuration の `cleartextTrafficPermitted` で明示する移行タスクとして扱う。`minSdkVersion < 24` のアプリでは API 24 未満向けに `usesCleartextTraffic="true"` を残しつつ、API 24 以上向けに Network Security Configuration を追加する必要がある。

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
- usesCleartextTraffic deprecation plan

検証対象の原文:
- In a future release, Android plans to deprecate the `usesCleartextTraffic` element.
- Apps that need unencrypted HTTP connections should migrate to a Network Security Configuration file.
- Network Security Configuration lets apps specify which domains need cleartext connections.
- Network Security Configuration files are supported only on API level 24 and higher.
- If an app has `minSdkVersion` lower than 24, it should set `usesCleartextTraffic` to `true` and use a Network Security Configuration file.
- If an app has `minSdkVersion` 24 or higher, it can use a Network Security Configuration file and does not need `usesCleartextTraffic`.

## 解釈（Interpretation）

この項目は、Android 17 で即時に `usesCleartextTraffic` の挙動を全アプリへ変えるというより、将来の deprecation に備えた migration guidance と読むのが自然である。ただし AOSP 実装には feature flag / compat change 付きの挙動変更が入っており、targetSdkVersion 37 以上を想定した段階的移行の可能性がある。

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
- `core/java/android/security/flags.aconfig`
- `core/res/res/values/attrs_manifest.xml`
- `core/api/current.txt`
- `core/java/com/android/internal/pm/parsing/pkg/PackageImpl.java`
- `packages/NetworkSecurityConfig/platform/src/android/security/net/config/ManifestConfigSource.java`
- `packages/NetworkSecurityConfig/tests/src/android/security/net/config/UsesCleartextTrafficDeprecationTest.java`

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `attrs_manifest.xml` / `usesCleartextTraffic` | attribute は通常 API として存在 | `@Deprecated` と `@FlaggedApi(android.security.Flags.FLAG_DEPRECATE_USES_CLEARTEXT_TRAFFIC2)` が追加され、Network Security Config 併用を推奨 | 公式文書の deprecation plan と一致する API surface evidence |
| `core/api/current.txt` / `R.attr.usesCleartextTraffic` | deprecated ではない | `@Deprecated @FlaggedApi("android.security.deprecate_uses_cleartext_traffic2")` | public API surface 上も deprecation が反映される |
| `flags.aconfig` / `deprecate_uses_cleartext_traffic2` | `deprecate_uses_cleartext_traffic` が fixed read-only flag として存在 | `deprecate_uses_cleartext_traffic2` が exported flag として追加され、targetSdk C+ で XML application flag を無視すると説明 | 実装 gate の feature flag |
| `ManifestConfigSource.DEPRECATE_USES_CLEARTEXT_TRAFFIC` | なし | `@ChangeId @Disabled static final long 415007211L` が追加 | app compatibility gate |
| `ManifestConfigSource.getConfigSource()` | Network Security Config がない場合、`ApplicationInfo.FLAG_USES_CLEARTEXT_TRAFFIC` から default cleartext policy を作る | compat change と feature flag が有効な場合、`usesCleartextTraffic = false` に上書き | 実際に `usesCleartextTraffic` を無効化する behavior path |
| `UsesCleartextTrafficDeprecationTest` | なし | flag と compat change の両方が enabled のときだけ `isCleartextTrafficPermitted()` が false になることを検証 | gate の組み合わせと期待挙動を示すテスト evidence |

## 実装 path（Runtime Path）

1. アプリが Network Security Config を指定していない。
2. `ManifestConfigSource.getConfigSource()` が manifest 由来の `ApplicationInfo.FLAG_USES_CLEARTEXT_TRAFFIC` から `DefaultConfigSource` を作ろうとする。
3. `CompatChanges.isChangeEnabled(DEPRECATE_USES_CLEARTEXT_TRAFFIC)` と `deprecateUsesCleartextTraffic2()` が両方 true の場合、`usesCleartextTraffic` は false に上書きされる。
4. 結果として manifest の `android:usesCleartextTraffic="true"` だけでは cleartext traffic permitted default にならない。
5. cleartext を許可したい場合は Network Security Configuration の `cleartextTrafficPermitted` で明示する必要がある。

## 差分確認（Diff Review）

確認コマンド:

```bash
git -C frameworks-base diff android-16.0.0_r4 android-17.0.0_r1 -- \
  core/java/android/security/flags.aconfig \
  core/res/res/values/attrs_manifest.xml \
  core/api/current.txt \
  packages/NetworkSecurityConfig/platform/src/android/security/net/config/ManifestConfigSource.java \
  packages/NetworkSecurityConfig/tests/src/android/security/net/config/UsesCleartextTrafficDeprecationTest.java
```

確認結果:
- `usesCleartextTraffic` attribute に deprecated / flagged API annotation が追加された。
- `deprecate_uses_cleartext_traffic2` flag が追加された。
- `ManifestConfigSource` に compat ChangeId `415007211L` と `usesCleartextTraffic = false` への上書き処理が追加された。
- `UsesCleartextTrafficDeprecationTest` が追加され、flag と compat change が両方 enabled のときのみ cleartext が false になることを検証している。

差分解釈:
- Source diff type: changed condition / changed default / API deprecation。
- Behavior Change を支える evidence: manifest attribute の deprecation annotation と Network Security Config 側の gate が追加されている。
- 分類を支える evidence: OS update all-apps の無条件変更ではなく、feature flag + compat change + targetSdk C+ 意図 + Network Security Config 未指定という条件付きの変更。

## 関連しない / 除外した path

- Network Security Config XML を明示しているアプリでは、`XmlConfigSource` が使われるため、この manifest fallback path の影響は限定される。
- 既に HTTPS 化済みで cleartext traffic を使わないアプリは、runtime 影響を受けにくい。
- `minSdkVersion < 24` の互換性説明は、API 24 未満で Network Security Config が使えないための migration guidance であり、Android 17 の runtime gate そのものではない。

---

# 適用条件（Applicability）

## OS アップデート時の挙動（OS Update Behavior）

- Android 17 に OS アップデートしただけで適用されるか: 無条件には適用されない。公式文書は future release の deprecation plan と説明し、AOSP 実装も feature flag + compat change の内側にある。
- targetSdkVersion に依存しない根拠: なし。むしろ aconfig description は targetSdk C+ を示す。
- Android 16 以前での挙動: Network Security Config がない場合、manifest の `usesCleartextTraffic` flag が default cleartext policy に反映される。

## targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- targetSdkVersion 37 以上で適用されるか: 意図としては Yes / 条件付き。feature flag description は targetSdk C+ で無視すると説明する。
- Android 17 / targetSdkVersion 36: compat change が無効なら従来通り `usesCleartextTraffic` が default cleartext policy に反映される想定。
- Android 17 / targetSdkVersion 37: feature flag と compat change が有効で、Network Security Config がない場合、`usesCleartextTraffic` は false 扱いになる可能性がある。
- opt-out / temporary override の有無: compat change と feature flag による制御はテストで確認できるが、一般 app 向け opt-out は公式文書に記載されていない。対応は Network Security Configuration への移行。

## その他の条件（Other Conditions）

- device/form factor: 公式文書からは条件なし。
- permission: 公式文書からは permission 条件なし。
- API usage: unencrypted HTTP connection、Network Security Configuration、`cleartextTrafficPermitted`。
- manifest attribute: `android:usesCleartextTraffic`。
- app config: Network Security Config を明示していない場合に manifest fallback path が関係する。

---

# 開発者影響

影響を受ける可能性がある app:
- HTTP cleartext connection が必要で、Network Security Configuration を使っていないアプリ。
- `android:usesCleartextTraffic="true"` だけで cleartext を許可しているアプリ。
- legacy HTTP API、閉域網 endpoint、IoT / gateway / partner integration を使うアプリ。

影響が限定的な app:
- HTTPS 化済みのアプリ。
- Network Security Configuration で必要 domain の `cleartextTrafficPermitted` を明示しているアプリ。
- cleartext traffic を使わないアプリ。

ユーザー影響:
- cleartext HTTP が必要な通信で接続失敗が発生する可能性がある。
- 認証、同期、決済、デバイス連携などが legacy HTTP endpoint に依存している場合、機能停止として見える可能性がある。

---

# サービス影響例

このセクションは、公式文書と AOSP 根拠から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: Google Home / TP-Link Tapo / Canon PRINT のような local HTTP device setup

- 具体サービス例: Google Home、TP-Link Tapo、Canon PRINT、Epson Smart Panel、Nature Remo。
- 影響を受ける実装パターン: 初期設定中の device AP / LAN endpoint へ `http://192.168.x.x` や `http://device.local` で接続し、`usesCleartextTraffic="true"` だけで許可している実装。
- 発生条件: Android 17 / targetSdkVersion 37 以上、feature flag + compat change が有効、Network Security Config を明示していない場合。
- ユーザーに見える症状: IoT 機器、プリンター、カメラの初期設定や LAN 操作で HTTP 接続が失敗する可能性。
- 技術的に起きていること: manifest の `usesCleartextTraffic` fallback が Network Security Config の default policy に反映されず、cleartext が許可されない。
- 推奨対応シーン: local device onboarding、LAN device control、printer / camera / hub 連携。
- 検証観点: Network Security Config の domain / base-config、private IP / `.local`、targetSdkVersion 36 / 37、minSdkVersion < 24 互換。
- 根拠: 公式文書、`DEPRECATE_USES_CLEARTEXT_TRAFFIC` compat change、`ManifestConfigSource` evidence。
- Confidence（信頼度）: Medium。release flag default は未解決。
- 注意: 上記サービスで発生確認した事実ではない。Network Security Config を明示済みなら影響は限定的。

## 例2（Example 2）: 社内 API / legacy partner API を使う業務アプリ

- 具体サービス例: Salesforce Field Service 連携、SAP Fiori Client 連携、社内 warehouse / POS / logistics アプリ。
- 影響を受ける実装パターン: 閉域網や legacy partner endpoint への HTTP cleartext を、manifest の `usesCleartextTraffic` だけで許可している実装。
- 発生条件: Android 17 target 37 移行時に manifest fallback が無視され、Network Security Config がない場合。
- ユーザーに見える症状: 社内 API への同期、在庫照会、POS 連携、配送端末連携が接続失敗になる可能性。
- 技術的に起きていること: app-wide manifest flag ではなく、Network Security Config による明示 domain policy が必要になる。
- 推奨対応シーン: enterprise / B2B / warehouse / retail / closed-network integration。
- 検証観点: HTTPS 化可否、domain-specific cleartext allow、API 24 未満 fallback、debug / staging config。
- 根拠: 公式文書の deprecation plan と AOSP の feature flag + compat gated behavior。
- Confidence（信頼度）: Medium。
- 注意: 上記サービスで発生確認した事実ではない。将来 release plan のため、Android 17 では flag / compat default を確認する必要がある。

---

# 推奨対応候補（Recommended Action Candidates）

開発者向け対応候補:
- `usesCleartextTraffic` と HTTP endpoint を棚卸しする。
- Network Security Configuration を導入し、必要 domain のみ `cleartextTrafficPermitted="true"` にする。
- `minSdkVersion < 24` の場合は API 24 未満向けに `usesCleartextTraffic="true"` を残しつつ、API 24 以上向けに Network Security Configuration も追加する。
- `minSdkVersion >= 24` の場合は Network Security Configuration への移行を優先し、`usesCleartextTraffic` への依存をなくす。
- Android 17 / targetSdkVersion 36 と 37 の両方で、Network Security Config あり / なしの cleartext 接続を確認する。

---

# テスト観点（Test Matrix）

| 端末 OS | targetSdkVersion | 条件 | 期待挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | Network Security Config なし / `usesCleartextTraffic=true` | baseline。manifest flag が default cleartext policy に反映される。 |
| Android 17 | 36 | Network Security Config なし / `usesCleartextTraffic=true` | compat change が無効なら従来挙動の想定。 |
| Android 17 | 37 | Network Security Config なし / `usesCleartextTraffic=true` / flag + compat enabled | manifest flag が無視され、cleartext が許可されない可能性。 |
| Android 17 | 37 | Network Security Config あり / domain cleartext permitted | 必要 domain で cleartext が許可される想定。 |

---

# 顧客向け説明（Customer-facing Explanation）

Android 17 の文書では、将来 release で `usesCleartextTraffic` element を deprecate する計画が示されています。Android 17 AOSP には、その準備として `usesCleartextTraffic` を `@Deprecated` 化し、feature flag と compat change が有効な場合に manifest の `usesCleartextTraffic` を Network Security Config の デフォルト ポリシー へ反映しない実装が追加されています。

HTTP cleartext が必要なアプリは、`usesCleartextTraffic` だけに依存せず、Network Security Configuration で必要な domain を明示してください。`minSdkVersion` が 24 未満の場合は API 24 未満向けに `usesCleartextTraffic="true"` を残しつつ、API 24 以上向けに Network Security Configuration も追加する必要があります。

---

# 未解決事項（Open Questions）

- `DEPRECATE_USES_CLEARTEXT_TRAFFIC` compat change が Android 17 release build で targetSdkVersion 37 以上に default-enabled される evidence。
- `deprecate_uses_cleartext_traffic2` feature flag の release default。
- 公式文書の future release plan と Android 17 実装 gate の対応関係。

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

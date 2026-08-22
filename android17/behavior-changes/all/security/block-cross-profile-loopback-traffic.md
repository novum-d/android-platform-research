# Block cross profile loopback traffic

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
- https://developer.android.com/work/managed-profiles
- https://developer.android.com/work/dpc/build-dpc
- https://developer.android.com/reference/android/app/admin/DevicePolicyManager

セクション:
- Block cross profile loopback traffic

ページ種別:
- Behavior changes: all apps

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- OS_UPDATE_ALL_APPS

公式文書からの初期適用条件判断:
- 公式文書は Android 17 の `Behavior changes: all apps` ページにこの項目を掲載している。
- 原文は、Android 17 から cross-profile loopback traffic が default で許可されなくなると説明している。
- 原文は、この変更が Android 17 以上で動作するすべてのアプリに target API level に関係なく適用されると明記している。
- Android 17 AOSP 根拠 では、loopback interface traffic を permission で guard するための `USE_LOOPBACK_INTERFACE` と `FORCE_USE_LOOPBACK_INTERFACE` が追加されている。

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | Yes / 条件付き | 公式文書は Android 17 以上の全アプリに target API level に関係なく適用と説明。 |
| targetSdkVersion 37 以上が必要か | No | 原文は regardless of target API level と明記。確認済み framework evidence に targetSdk gate はない。 |
| 追加の実行時条件があるか | ある | multiple profiles があり、loopback traffic が profile boundary を跨ぐ場合。same-profile loopback は対象外。 |
| Compat Change ID が関係するか | 確認できず | 確認済み evidence は permission / feature flag / BPF permission allowlist。 |

### 調査日（Investigation Date）

2026-06-18

### 信頼度（Confidence）

- Medium

理由:
- 公式文書は targetSdkVersion 非依存の all-apps change と明記している。
- Android 17 `frameworks-base` で loopback interface 用 permission と BPF permission allowlist への追加を確認できた。
- ただし packet-level blocking / cross-profile 判定の実装本体は Connectivity / netd / BPF 側にある可能性が高く、この checkout だけでは完全には確認できない。

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [x] OS update / all apps on Android 17 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 37 on Android 17+
- [ ] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [ ] Unknown / 追加根拠が必要

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 以上。
- targetSdkVersion: 条件なし。公式文書は target API level に関係なく適用と説明。
- Device/form factor: personal profile / work profile など複数 profile が存在する device / user state。
- Permission/API/component condition: loopback traffic、localhost / `127.0.0.1` / `::1`、cross-profile communication、managed profile / work profile、network policy / firewall / BPF / netd。
- App state/process condition: app または component が profile boundary を跨いで loopback address 経由で通信しようとする場合。

Compat framework:
- Change ID: 確認できず
- 変更名: なし
- 既定状態: 未確認
- テスト時の切り替え可否: feature flags `use_loopback_interface_permission_enabled` / `full_loopback_protections_enabled` が関連する可能性がある。

分類信頼度（Classification confidence）:
- Medium

---

# エグゼクティブサマリー

Android 17 では、profile boundary を跨ぐ loopback traffic が default で許可されなくなる、と公式文書は説明している。対象は personal profile と work profile などの別 profile 間で localhost / loopback を使う通信であり、同じ profile 内の loopback traffic は影響を受けない。

Android 17 AOSP では、loopback interface traffic を permission で guard するための `android.permission.USE_LOOPBACK_INTERFACE` と system/role 向け `android.permission.FORCE_USE_LOOPBACK_INTERFACE` が追加されている。`PermissionService` の BPF permission allowlist にもこれらの permission が追加されており、network/BPF enforcement と連携する設計が見える。

ただし、実際の packet-level blocking、cross-profile 判定、same-profile 例外は `frameworks-base` のみでは確認できない。Connectivity / netd / BPF policy 側の追加 evidence が必要なため、confidence は Medium とする。

---

# 公式ドキュメント確認

## 原文（Statement）

ページタイトル:
- Behavior changes: all apps

ページ URL:
- https://developer.android.com/about/versions/17/behavior-changes-all

ページ種別:
- all apps

セクションタイトル:
- Block cross profile loopback traffic

検証対象の原文:
- Beginning with Android 17, cross-profile loopback traffic is no longer permitted by default.
- Loopback traffic within the same profile is not affected.
- This change applies to all apps running on Android 17 or higher, regardless of what API level the app targets.

## 解釈（Interpretation）

この変更は、localhost / loopback address を使った profile boundary 越え通信を default で遮断する security / isolation behavior change である。work profile と personal profile のように異なる profile に属する app / component が、loopback を共有された通信路として使う設計は Android 17 で動作しなくなる可能性がある。

同じ profile 内で app が local HTTP server や local socket を使う flow は、公式文書上は影響対象外である。

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
- `core/res/AndroidManifest.xml`
- `core/api/current.txt`
- `core/api/system-current.txt`
- `core/java/android/permission/flags.aconfig`
- `services/permission/java/com/android/server/permission/access/permission/PermissionService.kt`
- `packages/services/Proxy/AndroidManifest.xml`

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `AndroidManifest.xml` / `USE_LOOPBACK_INTERFACE` | なし | normal permission として追加。説明は loopback interface 上の IP packets による他 app との interaction に必要 | loopback traffic を permission で guard する framework surface |
| `AndroidManifest.xml` / `FORCE_USE_LOOPBACK_INTERFACE` | なし | `signature|role` permission として追加。他 app の permission を要求せず loopback interface で interaction するための system/role 向け permission | system / role exception path の surface |
| `permission/flags.aconfig` / `use_loopback_interface_permission_enabled` | なし | `USE_LOOPBACK_INTERFACE` install permission を有効化し、loopback interface の IP traffic を guard すると説明 | feature flag evidence |
| `permission/flags.aconfig` / `full_loopback_protections_enabled` | なし | loopback interface traffic に `USE_LOOPBACK_INTERFACE` permission を要求すると説明 | protection 有効化 flag |
| `PermissionService.kt` / `ALLOWED_BPF_PERMISSIONS` | loopback permission なし | `USE_LOOPBACK_INTERFACE` と `FORCE_USE_LOOPBACK_INTERFACE` が BPF permission allowlist に追加 | packet / BPF enforcement と permission model が接続される evidence |
| `packages/services/Proxy/AndroidManifest.xml` | なし | `FORCE_USE_LOOPBACK_INTERFACE` を要求 | system component が loopback exception permission を使う evidence |

## 実装 path（Runtime Path）

公式文書と framework evidence から推定できる path:
1. app が loopback interface 経由で別 app / 別 profile と通信しようとする。
2. Android 17 では loopback interface traffic が permission `USE_LOOPBACK_INTERFACE` / `FORCE_USE_LOOPBACK_INTERFACE` によって guard される。
3. BPF permission allowlist にこれらの permission が追加されているため、network policy / BPF layer が permission state を参照する可能性がある。
4. cross-profile traffic は default block、same-profile traffic は unaffected と公式文書は説明している。

上記 1-3 の framework permission surface は確認済み。4 の exact packet filtering / cross-profile 判定は Connectivity / netd / BPF 側の追加調査が必要。

## 差分確認（Diff Review）

確認コマンド:

```bash
git -C frameworks-base diff android-16.0.0_r4 android-17.0.0_r1 -- \
  core/res/AndroidManifest.xml \
  core/api/current.txt \
  core/api/system-current.txt \
  core/java/android/permission/flags.aconfig \
  services/permission/java/com/android/server/permission/access/permission/PermissionService.kt
```

確認結果:
- `USE_LOOPBACK_INTERFACE` public permission が追加された。
- `FORCE_USE_LOOPBACK_INTERFACE` system permission が追加された。
- `use_loopback_interface_permission_enabled` と `full_loopback_protections_enabled` flags が追加された。
- `ALLOWED_BPF_PERMISSIONS` に loopback permissions が追加された。

差分解釈:
- Source diff type: added permission / changed condition / guarded enforcement surface。
- Behavior Change を支える evidence: loopback interface traffic を permission で guard する framework API / permission surface が Android 17 tag に存在する。
- 分類を支える evidence: 公式文書は all apps / target API level independent と明記し、確認済み framework evidence に targetSdkVersion ゲートはない。

## 関連しない / 除外した path

- `INTERACT_ACROSS_PROFILES` は cross-profile app interaction の一般 permission であり、本項目の loopback interface packet protection とは別。
- media projection の loopback は screen/audio projection 文脈であり、本項目の network loopback traffic とは別。
- same-profile localhost / loopback は公式文書上影響対象外。

---

# 適用条件（Applicability）

## OS アップデート時の挙動（OS Update Behavior）

- Android 17 に OS アップデートしただけで適用されるか: Yes / Conditional。
- targetSdkVersion に依存しない根拠: 公式文書は Android 17 以上の全アプリに target API level に関係なく適用と説明している。
- Android 16 以前での挙動: cross-profile loopback traffic が default permitted だったと公式文書は説明している。Android 17 では default block される。

## targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- targetSdkVersion 37 以上で適用されるか: targetSdkVersion 37 は必要条件ではない。
- Android 17 / targetSdkVersion 36: 条件を満たす場合、cross-profile loopback traffic は default block。
- Android 17 / targetSdkVersion 37: targetSdkVersion 36 と同じ期待。
- opt-out / temporary override の有無: 一般 app 向け opt-out は確認できない。system / role 向けには `FORCE_USE_LOOPBACK_INTERFACE` が存在する。

## その他の条件（Other Conditions）

- device/form factor: 複数 profile が存在する device / user state。single profile device では cross-profile traffic 自体が発生しない。
- permission: `USE_LOOPBACK_INTERFACE` / `FORCE_USE_LOOPBACK_INTERFACE` が関係する。
- API usage: loopback network traffic、localhost / `127.0.0.1` / `::1`、local server / socket、cross-profile communication。
- component boundary: permission service、network stack、BPF / netd、managed profile、DevicePolicy / enterprise policy。

---

# 開発者影響

影響を受ける可能性がある app:
- work profile / personal profile など複数 profile 間で localhost / loopback communication を使うアプリ。
- enterprise companion、DPC support、profile 間 helper、testing / diagnostic bridge。

影響が限定的な app:
- single profile device のみで動作するアプリ。
- same-profile loopback のみを使うアプリ。
- loopback を使わないアプリ。

ユーザー影響:
- 別 profile から localhost service に接続する設計の機能が失敗する可能性がある。
- enterprise / work profile 連携や diagnostic tooling で接続不可として見える可能性がある。

---

# サービス影響例

このセクションは、公式文書と AOSP 根拠から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: Microsoft Intune / Android Enterprise の work profile 連携アプリ

- 具体サービス例: Microsoft Intune Company Portal、Google Android Enterprise 管理下の work profile アプリ、VMware Workspace ONE。
- 影響を受ける実装パターン: personal profile 側または work profile 側の companion / helper が `localhost` を profile 間通信路として使う設計。
- 発生条件: Android 17 で cross-profile loopback traffic が default block され、同一 profile 内通信ではない場合。
- ユーザーに見える症状: work profile 側の診断、認証補助、local helper 連携が接続失敗として見える可能性。
- 技術的に起きていること: `127.0.0.1` / `::1` 宛てでも profile boundary を跨ぐ traffic は same-profile loopback と扱われず block 対象になる。
- 推奨対応シーン: enterprise / DPC / managed profile 機能で localhost を使う箇所の棚卸し。
- 検証観点: personal -> work、work -> personal、same-profile loopback を分けて Android 17 実機で確認する。
- 根拠: 公式文書の cross-profile loopback block、report の permission / policy evidence。
- Confidence（信頼度）: Medium。packet-level enforcement は追加 evidence が必要。
- 注意: 上記サービスで発生確認した事実ではない。実際の影響は profile 構成と通信設計に依存する。

## 例2（Example 2）: Postman / Termux / 開発者向け local server 診断

- 具体サービス例: Postman、Termux、HTTP Toolkit、社内 debug companion app。
- 影響を受ける実装パターン: 片方の profile で起動した local HTTP server / proxy / debug endpoint に、別 profile の app から `localhost` で接続する実装。
- 発生条件: Android 17 で cross-profile boundary を跨ぐ loopback 接続になる場合。
- ユーザーに見える症状: local debug server が起動しているのに接続できない、proxy 設定や診断結果が失敗になる可能性。
- 技術的に起きていること: loopback address は device-wide の共有通信路として使えず、profile 境界を跨ぐ access が制限される。
- 推奨対応シーン: QA / enterprise debug / companion app の local server 利用手順。
- 検証観点: 同一 profile では成功し、cross-profile では失敗するかを分離して確認する。
- 根拠: 公式文書の same-profile exception と cross-profile block の説明。
- Confidence（信頼度）: Medium。
- 注意: 上記サービスで発生確認した事実ではない。debug tool の profile 配置とネットワーク経路に依存する。

---

# 推奨対応候補（Recommended Action Candidates）

開発者向け対応候補:
- localhost / loopback 利用箇所を棚卸しし、same-profile か cross-profile かを確認する。
- cross-profile communication は managed profile / enterprise 向けの公式 mechanism へ移行する。
- work profile / personal profile の両方で Android 17 実機テストを行う。
- system / role app の場合は `USE_LOOPBACK_INTERFACE` / `FORCE_USE_LOOPBACK_INTERFACE` の適用可否を platform owner と確認する。

---

# テスト観点（Test Matrix）

| 端末 OS | targetSdkVersion | 条件 | 期待挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | personal -> work profile loopback | baseline。cross-profile loopback の現行挙動を確認。 |
| Android 17 | 36 | personal -> work profile loopback | default block の想定。 |
| Android 17 | 37 | personal -> work profile loopback | targetSdkVersion 36 と同じ想定。 |
| Android 17 | 37 | same-profile loopback | 公式文書上、影響なし。 |

---

# 顧客向け説明（Customer-facing Explanation）

Android 17 では、work profile と personal profile など、profile boundary を跨ぐ loopback traffic が default で許可されなくなります。これは `localhost` / `127.0.0.1` / `::1` を profile 間通信路として使う設計に影響する可能性があります。

同じ profile 内の loopback traffic は公式文書上影響を受けません。したがって、同一 profile 内で local server を使うだけの機能と、別 profile から localhost へ接続する機能を分けて確認してください。

---

# 未解決事項（Open Questions）

- Connectivity / netd / BPF 側の packet-level enforcement 実装。
- cross-profile 判定の exact unit。
- `USE_LOOPBACK_INTERFACE` / `FORCE_USE_LOOPBACK_INTERFACE` の release flag default。
- DPC / enterprise policy による例外設定の有無。

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

# Block cross profile loopback traffic

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP tag

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

### Behavior Change 文書（Behavior Change Source）

Document:
- https://developer.android.com/about/versions/17/behavior-changes-all

Related documents:
- https://developer.android.com/work/managed-profiles
- https://developer.android.com/work/dpc/build-dpc
- https://developer.android.com/reference/android/app/admin/DevicePolicyManager

Section:
- Block cross profile loopback traffic

Page type:
- Behavior changes: all apps

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- 公式文書は Android 17 の `Behavior changes: all apps` ページにこの項目を掲載している。
- 原文は、Android 17 から cross-profile loopback traffic が default で許可されなくなると説明している。
- 原文は、same-profile loopback traffic は影響を受けないと説明している。
- 原文は、この変更が Android 17 以上で動作するすべてのアプリに target API level に関係なく適用されると明記している。
- ただし、local `frameworks-base` に Android 17 AOSP tag がないため、network stack / netd / firewall / profile boundary policy / DevicePolicy exception / compat framework entry は未確認である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | Likely Yes / Conditional, but unverified | 公式文書は Android 17 以上の全アプリに target API level に関係なく適用と説明。AOSP gate 未確認。 |
| targetSdkVersion 37 以上が必要か | Likely No, but unverified | 原文は regardless of target API level と明記。AOSP targetSdkVersion gate 未確認。 |
| 追加の実行時条件があるか | Yes | multiple profiles があり、loopback traffic が profile boundary を跨ぐ場合。same-profile loopback は対象外。 |
| Compat Change ID が関係するか | Unknown | Android 17 tag と compat framework evidence が未確認。 |

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
- [x] Unknown / needs more evidence

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 以上。AOSP tag 未取得のため実装上の OS gate は未確認。
- targetSdkVersion: 公式文書上は target API level に依存しない。AOSP targetSdkVersion gate 未確認。
- Device/form factor: personal profile / work profile など複数 profile が存在する device / user state。
- Permission/API/component condition: loopback traffic、localhost / `127.0.0.1` / `::1`、cross-profile communication、managed profile / work profile、network policy / firewall / netd。
- App state/process condition: app または component が profile boundary を跨いで loopback address 経由で通信しようとする場合。

Compat framework:
- Change ID: Unknown
- Change name: Unknown
- Default state: Unknown
- Toggleable for testing: Unknown

分類信頼度（Classification confidence）:
- Low

分類根拠（Classification evidence）:
- Official documentation page: `behavior-changes-all`
- Original applicability statement: Android 17 から cross-profile loopback traffic は default で許可されず、same-profile loopback は影響なし。Android 17 以上の全アプリに target API level に関係なく適用。
- AOSP targetSdk gate: 未確認。local `frameworks-base` に `android-17*` tag がない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# エグゼクティブサマリー（Executive Summary）

Android 17 では、profile boundary を跨ぐ loopback traffic が default で許可されなくなる、と公式文書は説明している。対象は personal profile と work profile などの別 profile 間で localhost / loopback を使う通信であり、同じ profile 内の loopback traffic は影響を受けない。

この変更は Android 17 以上で動作するすべてのアプリに target API level に関係なく適用されると明記されている。そのため、targetSdkVersion 37 への更新有無ではなく、Android 17 OS update と multi-profile / cross-profile loopback usage の条件で影響を評価する。

現時点では local `frameworks-base` に Android 17 AOSP tag がないため、block が network stack、user/profile boundary、socket routing、firewall、netd、DevicePolicy のどこで実装されるかは未確認である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とし、Android 17 AOSP tag 公開後に再調査する。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statement）

Page title:
- Behavior changes: all apps

Page URL:
- https://developer.android.com/about/versions/17/behavior-changes-all

Page type:
- all apps

Section title:
- Block cross profile loopback traffic

Original statement being verified:
- Beginning with Android 17, cross-profile loopback traffic is no longer permitted by default.
- Loopback traffic within the same profile is not affected.
- This change applies to all apps running on Android 17 or higher, regardless of what API level the app targets.

## 解釈（Interpretation）

この変更は、localhost / loopback address を使った profile boundary 越え通信を default で遮断する security / isolation behavior change である。work profile と personal profile のように異なる profile に属する app / component が、loopback を共有された通信路として使う設計は Android 17 で動作しなくなる可能性がある。

一方、同じ profile 内で app が local HTTP server や local socket を使う flow は、公式文書上は影響対象外である。顧客向けには「localhost 全般が禁止される」ではなく、「cross-profile の loopback traffic が default block される」と分けて説明する必要がある。

---

# 変更内容（What Changed）

公式文書上の変更点:
- Android 17 から cross-profile loopback traffic は default で許可されない。
- same-profile loopback traffic は影響を受けない。
- Android 17 以上で動作するすべてのアプリに適用される。
- target API level に関係なく適用される。

AOSP で未確認の点:
- block が network stack / netd / firewall / routing / SELinux / user profile boundary のどこで実装されるか。
- loopback address の対象が `127.0.0.1`、`localhost`、`::1`、abstract / local socket まで含むか。
- personal profile / work profile / private space / clone profile など profile 種別ごとの差分。
- enterprise / device policy / profile owner / DPC による例外や許可 path の有無。
- same-profile traffic 判定の単位。
- compat framework Change ID と default state。

## 適用条件（Applicability）

この変更がいつ適用されるかを OS 条件と targetSdkVersion 条件に分けて説明する。

### OS アップデート時の挙動（OS Update Behavior）

- Android 17 に OS アップデートしただけで適用されるか: 公式文書上は Yes / Conditional。Android 17 以上の全アプリに target API level に関係なく適用と明記されている。ただし AOSP gate 未確認。
- targetSdkVersion に依存しない根拠: 原文は regardless of what API level the app targets と説明している。
- Android 16 以前での挙動: 公式文書は Android 17 から default で許可されないと説明している。Android 16 baseline の cross-profile loopback behavior は AOSP diff 未確認。

### targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- targetSdkVersion 37 以上で適用されるか: 公式文書上、targetSdkVersion 37 は必要条件ではない。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: Unknown。公式文書は Android 17 platform behavior として説明している。
- opt-out / temporary override の有無: 未確認。公式文書には opt-out や exception policy は記載されていない。DevicePolicy / enterprise exception の有無は AOSP tag 待ち。

### その他の条件（Other Conditions）

- device/form factor: 複数 profile が存在する device / user state。single profile device では cross-profile traffic 自体が発生しない。
- permission: 公式文書からは特定 permission 条件なし。
- API usage: loopback network traffic、localhost / `127.0.0.1` / `::1`、local server / socket、cross-profile communication。
- manifest attribute: 公式文書からは条件なし。
- component boundary: network stack、profile / user boundary、managed profile、DevicePolicy / enterprise policy、firewall / routing layer にまたがる可能性。

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

Evidence limitation:
- Android 17 AOSP tag が local `frameworks-base` にないため、`android-16.0.0_r4` と Android 17 tag の明示的な source diff は実行できない。
- そのため、local working tree や未確定 branch を platform evidence として扱わない。
- 本レポートの AOSP-backed conclusion は Low confidence に留める。

## 関連ファイル（Related Files）

Android 17 AOSP tag 未取得のため、tag diff に基づく related files は未確定。

Android 17 tag 公開後に確認すべき候補:
- `services/core/java/com/android/server/net/` 以下の network policy / firewall path
- `services/core/java/com/android/server/connectivity/` または connectivity service path
- `services/core/java/com/android/server/pm/` の user / profile relation 判定 path
- `services/core/java/com/android/server/devicepolicy/` の DevicePolicy / profile owner exception path
- `netd` / firewall / routing policy に関係する AOSP project
- compat framework 定義ファイル内の cross-profile loopback / network isolation 関連 Change ID

Note:
- 実際の enforcement は `frameworks-base` 以外の `packages/modules/Connectivity`、`system/netd`、kernel / firewall policy 側にある可能性がある。Android 17 tag 入手後は該当 project も evidence 対象として確認する必要がある。

## 確認したソース文脈（Source Context Reviewed）

AOSP tag diff は未実行。以下は公式文書から見た確認予定の source context であり、AOSP evidence ではない。

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| cross-profile network policy / firewall path | 未確認 | cross-profile loopback traffic が default block と公式文書が説明 | 実際に traffic を許可 / 拒否する enforcement point |
| user / profile boundary check | 未確認 | same-profile traffic は影響なし、cross-profile traffic は default block と公式文書が説明 | profile 境界の判定が適用条件そのものになるため |
| loopback address routing / socket path | 未確認 | loopback traffic のうち cross-profile のみ制限されると公式文書が説明 | localhost / `127.0.0.1` / `::1` の扱いを確認するため |
| DevicePolicy / enterprise exception path | 未確認 | 公式文書には exception 記載なし | DPC / managed profile 環境で例外や policy override があるか確認するため |

必須記入項目（Required context）:
- Entry point / caller: 未確認。想定される entry point は app socket connect / bind -> network stack / netd / firewall -> user/profile boundary policy -> allow / block。
- Relevant class or service responsibility: loopback routing、profile boundary isolation、network policy / firewall enforcement、DevicePolicy exception。
- Runtime path from app API / system event to changed code: app が localhost / loopback へ connect -> system が source profile と destination profile を判定 -> same-profile なら許可、cross-profile なら default block、という path が想定される。AOSP evidence としては未確認。
- Why unrelated code paths were excluded: tag diff 未実行のため、除外判断は未完了。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
| Android 17 tag 未取得のため source diff 未確認 | 公式文書上は changed default / changed condition と読める | cross-profile loopback traffic が default block になり、same-profile loopback は維持されると説明されている | Low |

必須分類（Required interpretation）:
- Added behavior: 未確認。cross-profile loopback block enforcement が追加された可能性がある。
- Removed behavior: 未確認。
- Changed condition / gate: 公式文書上、same-profile は許可、cross-profile は default block という条件差分がある。AOSP gate 未確認。
- Changed default: 公式文書上、cross-profile loopback traffic は no longer permitted by default。AOSP default 未確認。
- No behavior change found: 未確認。tag 不在のため「no behavior change」とは判断しない。

## 事実（Evidence）

事実:
- 公式文書は `Block cross profile loopback traffic` を Android 17 `Behavior changes: all apps` ページに掲載している。
- 公式文書は、Android 17 から cross-profile loopback traffic が default で許可されなくなると説明している。
- 公式文書は、same-profile loopback traffic は影響を受けないと説明している。
- 公式文書は、この変更が Android 17 以上で動作するすべてのアプリに target API level に関係なく適用されると説明している。

観察:
- All apps ページ掲載かつ regardless of target API level の明記があるため、一次分類は `OS_UPDATE_ALL_APPS` 候補である。
- 実際の影響は、複数 profile が存在し、profile boundary を跨ぐ loopback communication を使っている場合に限られる。
- same-profile loopback は対象外であり、local development server、in-app localhost server、same-profile IPC まで一律に禁止される変更ではない。

仮説:
- enforcement は network policy / firewall / netd / connectivity module 側で profile boundary を見て適用される可能性がある。
- enterprise / work profile 環境では DevicePolicyManager または DPC による例外設定が存在する可能性があるが、公式抜粋からは確認できない。
- `localhost` / `127.0.0.1` / `::1` のすべてが対象になる可能性があるが、AOSP evidence がないため範囲は未確定。

結論:
- 現時点の確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE`。公式文書上は `OS_UPDATE_ALL_APPS` 候補だが、AOSP tag 未取得のため High confidence にできない。
- 顧客向けには、Android 17 上では targetSdkVersion 36 のままでも cross-profile loopback communication が default block される可能性がある、と条件付きで説明する。

## 適用ゲート根拠（Applicability Gate Evidence）

- targetSdkVersion gate: 未確認。公式文書上は target API level に関係なく適用。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。
- @EnabledAfter / @EnabledSince / default state: 未確認。
- Build.VERSION / SDK_INT gate: 未確認。公式文書上は Android 17 introduced。
- DeviceConfig / resources config: 未確認。
- Permission/AppOps gate: 公式文書からは確認できない。
- Manifest/property gate: 公式文書からは確認できない。
- No gate found: 未確認。AOSP tag 未取得のため gate search 未実行。
- Gate conclusion: 公式文書上は Android 17 all apps + cross-profile loopback condition。AOSP evidence 未取得のため `UNKNOWN_NEEDS_MORE_EVIDENCE`。
- Reasoning from source context: source context は未確認。公式文書の page type と statement のみから一次判断している。

---

# 影響分析（Impact Analysis）

## 影響を受けるアプリ（Affected Apps）

- personal profile / work profile など複数 profile がある device 上で動作するアプリ。
- one profile で local HTTP server / local socket server を起動し、別 profile の app / component から loopback 経由で接続する設計。
- enterprise / companion / testing tools で profile boundary を跨ぐ localhost communication に依存しているアプリ。
- managed cross-profile API ではなく localhost / loopback を cross-profile IPC として使っているアプリ。

## 影響を受けないアプリ（Non-Affected Apps）

- single profile device でのみ動作する場合。
- same-profile loopback traffic のみを使う場合。
- localhost / loopback を使わないアプリ。
- managed cross-profile APIs や公式の enterprise / profile communication mechanism を使う場合。
- ただし、AOSP tag 未取得のため正確な non-affected condition は未確定。

---

# 顧客影響（Customer Impact）

顧客説明用。

## 影響度（Impact Level）

- 要確認

※ 仮評価。最終判断は人間が行う。

## ビジネス影響（Business Impact）

- ユーザー影響: work profile / personal profile 間で localhost 連携している機能が接続失敗、同期失敗、companion integration failure として見える可能性がある。
- セキュリティ影響: profile isolation を強化し、loopback を使った profile boundary bypass を防ぐ意図がある。
- 開発影響: cross-profile communication を localhost に依存している箇所を棚卸しし、managed cross-profile API や enterprise policy に沿った設計へ移行する必要がある。
- 運用影響: enterprise / work profile 環境での接続失敗率、local server connection failure、DPC policy compatibility を監視する必要がある。

---

# サービス影響例（Service Impact Examples）

このセクションは、公式文書と未確認の AOSP 調査観点から導いた「起こりうる影響例」を記録する。
特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: work profile と personal profile の companion 連携

- 対象サービス例: enterprise companion app、DPC support app、社内認証 helper。
- 影響を受ける実装パターン: personal profile 側の app が local HTTP server を起動し、work profile 側 app が `127.0.0.1` へ接続する。
- 発生条件: Android 17、複数 profile、profile boundary を跨ぐ loopback traffic。
- ユーザーに見える症状: profile 間連携、認証、同期、device setup helper が失敗する。
- 開発・運用への影響: localhost 依存をやめ、DevicePolicyManager / managed profile API / approved cross-profile communication path へ移行する必要がある。
- 推奨対応候補: cross-profile localhost connection を検出し、same-profile に閉じるか official cross-profile mechanism へ置き換える。
- 根拠: 公式文書は cross-profile loopback traffic が default で許可されなくなると説明している。
- Confidence（信頼度）: Low。AOSP enforcement condition 未確認。
- 注意: 実サービスで発生確認した事実ではない。

## 例2（Example 2）: QA / testing tool の localhost bridge

- 対象サービス例: enterprise QA agent、debug bridge、test automation helper。
- 影響を受ける実装パターン: 片方の profile で debug server を起動し、もう片方の profile から localhost で接続する。
- 発生条件: Android 17、cross-profile loopback traffic。
- ユーザーに見える症状: test setup、automation、diagnostic collection が失敗する。
- 開発・運用への影響: test infrastructure を profile-aware にし、profile ごとに server を起動する、または supported communication mechanism に変更する必要がある。
- 推奨対応候補: same-profile loopback と cross-profile loopback を分けた test matrix を作る。
- 根拠: 公式文書は same-profile loopback は影響なし、cross-profile loopback は default block と説明している。
- Confidence（信頼度）: Low。AOSP enforcement condition 未確認。
- 注意: 実サービスで発生確認した事実ではない。

---

# 対応候補（Required Actions）

## 必須対応（Must）

- localhost / `127.0.0.1` / `::1` / local socket を使う機能を棚卸しする。
- その通信が same-profile に閉じているか、profile boundary を跨いでいるか確認する。
- work profile / managed profile 環境で cross-profile loopback に依存している機能を特定する。
- Android 17 で personal profile / work profile を用意し、same-profile と cross-profile の loopback behavior を分けて検証する。

## 推奨対応（Recommended）

- cross-profile communication には managed profile / enterprise 向けの公式 mechanism を使う。
- local server を profile ごとに起動するなど、same-profile に閉じる設計へ変更する。
- DPC / profile owner / DevicePolicyManager による許可 path や例外の有無を Android 17 AOSP tag 公開後に確認する。
- enterprise 顧客向け QA matrix に personal profile / work profile / managed device を追加する。

## 任意対応（Optional）

- loopback connection failure を telemetry / logs で検出できるようにする。
- cross-profile localhost usage を static analysis / code search で検出する。
- Android 17 AOSP tag 公開後に network policy / netd / firewall / DevicePolicy path を再確認する。

---

# 検証方法（Verification Method）

変更を確認する方法。

## 検証マトリクス（Matrix）

| 端末 OS（Device OS） | targetSdkVersion | Compat flag / test control | 期待挙動（Expected behavior） |
| --- | --- | --- | --- |
| Android 16 | 36 | default | baseline。same-profile / cross-profile loopback がどう動くか確認する。 |
| Android 17 | 36 | default | 公式文書上、cross-profile loopback は default block、same-profile loopback は unaffected。 |
| Android 17 | 37 | default | targetSdkVersion 36 と同様に、target API level に関係なく適用されると公式文書は説明。 |
| Android 17 | 36 | force-enabled if available | Compat flag 未確認。存在する場合は block 単体の影響を確認する。 |
| Android 17 | 37 | force-disabled if available | Compat flag 未確認。存在する場合は rollback / opt-out 可能性を確認する。 |

## 手順（Steps）

- targetSdk変更: targetSdkVersion 36 / 37 の両方で検証し、targetSdkVersion 差分ではなく profile boundary 差分として観測されるか確認する。
- compat framework command: 未確認。Android 17 tag 公開後に Change ID が存在する場合のみ force-enable / force-disable を検証する。
- テスト方法:
  - personal profile 内 server -> personal profile client。
  - work profile 内 server -> work profile client。
  - personal profile server -> work profile client。
  - work profile server -> personal profile client。
  - `localhost`、`127.0.0.1`、`::1` を分ける。
  - managed profile / DPC policy の有無を分ける。
- 再現手順:
  - Android 17 device / emulator に work profile を作成する。
  - profile A で local HTTP server または local socket server を起動する。
  - 同じ profile と別 profile の client から loopback address へ接続する。
  - 接続成功 / timeout / connection refused / permission denial / firewall log を記録する。
- 期待結果:
  - same-profile loopback は接続できる。
  - cross-profile loopback は default で接続できない。
  - targetSdkVersion 36 / 37 の差分はない。

---

# 結論（Conclusion）

`Block cross profile loopback traffic` は Android 17 all apps ページに掲載されており、target API level に関係なく Android 17 以上の全アプリに適用されると公式文書は説明している。主な適用条件は、複数 profile が存在し、loopback traffic が profile boundary を跨ぐことである。same-profile loopback は影響を受けない。

ただし、Android 17 AOSP tag が local `frameworks-base` に存在しないため、network stack / netd / firewall / profile boundary / DevicePolicy exception の実装根拠は未確認である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

Android app developer は、localhost / loopback を cross-profile communication として使っていないか確認し、必要に応じて managed profile / enterprise 向けの公式 communication path へ移行する必要がある。

---

# 人間の判断欄（Human Decision Placeholder）

最終優先度（Final Priority）:
- Human decision required

判断（Decision）:
- Further investigation required after Android 17 AOSP tag is available

判断理由候補:
- 公式文書上は all apps / regardless of target API level と明確だが、AOSP gate、DevicePolicy exception、enforcement layer が未確認である。
- 顧客影響は work profile / managed profile の利用有無と、cross-profile loopback 依存の有無に依存する。

---

# 参照（References）

## ドキュメント（Documentation）

- https://developer.android.com/about/versions/17/behavior-changes-all
- https://developer.android.com/work/managed-profiles
- https://developer.android.com/work/dpc/build-dpc
- https://developer.android.com/reference/android/app/admin/DevicePolicyManager

## AOSP

- 未確認。local `frameworks-base` に Android 17 AOSP tag がないため、tag diff による source evidence は未取得。

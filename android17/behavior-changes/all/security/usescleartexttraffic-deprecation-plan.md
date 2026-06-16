# usesClearTraffic deprecation plan

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
- https://developer.android.com/guide/topics/manifest/application-element#usesCleartextTraffic
- https://developer.android.com/privacy-and-security/security-config
- https://developer.android.com/training/articles/security-config#CleartextTrafficPermitted

Section:
- usesClearTraffic deprecation plan

Page type:
- Behavior changes: all apps

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- 公式文書は Android 17 の `Behavior changes: all apps` ページにこの項目を掲載している。
- ただし、原文は "In a future release, we plan to deprecate the `usesCleartextTraffic` element" と説明しており、Android 17 で `usesCleartextTraffic` の実行時挙動が即時に変わるとは述べていない。
- 公式文書上の主な開発者対応は、unencrypted HTTP connection が必要なアプリに対して Network Security Configuration へ移行することである。
- `minSdkVersion < 24` のアプリは、API 24 未満で Network Security Configuration が使えないため、`usesCleartextTraffic="true"` と Network Security Configuration の両方を使うよう説明されている。
- `minSdkVersion >= 24` のアプリは Network Security Configuration を使えばよく、`usesCleartextTraffic` は不要と説明されている。
- local `frameworks-base` に Android 17 AOSP tag がないため、Android 17 での manifest parsing、cleartext traffic policy default、targetSdkVersion gate、compat framework entry、actual deprecation state は未確認である。

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | Likely No immediate runtime behavior, but unverified | 公式文書は future release の deprecation plan として説明。Android 17 で即時 enforcement すると明記していない。 |
| targetSdkVersion 37 以上が必要か | Likely No for this guidance, but unverified | All apps ページ掲載。ただし主内容は migration guidance。AOSP gate 未確認。 |
| 追加の実行時条件があるか | Yes, for relevance | unencrypted HTTP connection が必要なアプリ、`usesCleartextTraffic` を使っているアプリ、`minSdkVersion` が 24 未満か以上か。 |
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
- Android version: Android 17 文書上の guidance。実行時挙動変更は future release と説明されており、Android 17 での OS gate は未確認。
- targetSdkVersion: 公式文書上、この migration guidance に targetSdkVersion 37 条件は示されていない。AOSP targetSdkVersion gate 未確認。
- Device/form factor: 公式文書からは条件なし。
- Permission/API/component condition: unencrypted HTTP connection、`android:usesCleartextTraffic`、Network Security Configuration、`cleartextTrafficPermitted`。
- App state/process condition: network connection 時の cleartext traffic policy evaluation が関係する可能性があるが、Android 17 実装差分は未確認。

Compat framework:
- Change ID: Unknown
- Change name: Unknown
- Default state: Unknown
- Toggleable for testing: Unknown

分類信頼度（Classification confidence）:
- Low

分類根拠（Classification evidence）:
- Official documentation page: `behavior-changes-all`
- Original applicability statement: all apps page に掲載されているが、本文は future release で `usesCleartextTraffic` element を deprecate する計画と説明している。
- AOSP targetSdk gate: 未確認。local `frameworks-base` に `android-17*` tag がない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# エグゼクティブサマリー（Executive Summary）

Android 17 の all apps ページは、将来の release で `usesCleartextTraffic` element を deprecate する計画を示している。Android 17 で cleartext traffic の実行時挙動が直ちに変わる、または `usesCleartextTraffic` が直ちに無効になる、とは公式文書上は読み取れない。

HTTP 接続が必要なアプリは、domain 単位で cleartext traffic を許可できる Network Security Configuration へ移行することが推奨される。`minSdkVersion < 24` の場合は、API 24 未満との互換性のため `usesCleartextTraffic="true"` も併用する必要がある。

現時点では local `frameworks-base` に Android 17 AOSP tag がないため、manifest parsing、cleartext policy evaluation、targetSdkVersion gate、compat framework entry は未確認である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とし、Android 17 AOSP tag 公開後に再調査する。

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
- usesClearTraffic deprecation plan

Original statement being verified:
- In a future release, Android plans to deprecate the `usesCleartextTraffic` element.
- Apps that need unencrypted HTTP connections should migrate to a Network Security Configuration file.
- Network Security Configuration lets apps specify which domains need cleartext connections.
- Network Security Configuration files are supported only on API level 24 and higher.
- If an app has `minSdkVersion` lower than 24, it should set `usesCleartextTraffic` to `true` and use a Network Security Configuration file.
- If an app has `minSdkVersion` 24 or higher, it can use a Network Security Configuration file and does not need `usesCleartextTraffic`.

## 解釈（Interpretation）

この項目は、Android 17 で即時に `usesCleartextTraffic` の挙動を変えるというより、将来の deprecation に備えた migration guidance と読むのが自然である。公式文書は "future release" と書いており、Android 17 で HTTP cleartext connection が新たに拒否される、または `usesCleartextTraffic` が無視される、とは明記していない。

開発者にとっての実務上の意味は、アプリ全体で cleartext を許可する manifest attribute から、domain 単位で明示できる Network Security Configuration へ移行することにある。特に `minSdkVersion < 24` のアプリでは、API 24 未満で Network Security Configuration がサポートされないため、当面は `usesCleartextTraffic="true"` を残しつつ、API 24 以上向けに Network Security Configuration も導入する必要がある。

---

# 変更内容（What Changed）

公式文書上の変更点:
- 将来の release で `usesCleartextTraffic` element を deprecate する計画が示された。
- unencrypted HTTP connection が必要なアプリは Network Security Configuration へ移行することが推奨される。
- Network Security Configuration により、cleartext connection が必要な domain を指定できる。
- Network Security Configuration は API level 24 以上でのみサポートされる。
- `minSdkVersion < 24` のアプリは、`usesCleartextTraffic="true"` と Network Security Configuration の両方を使う必要がある。
- `minSdkVersion >= 24` のアプリは、Network Security Configuration を使えば `usesCleartextTraffic` は不要と説明されている。

AOSP で未確認の点:
- Android 17 で `android:usesCleartextTraffic` の parsing / policy evaluation が変更されたか。
- Android 17 で cleartext traffic default や enforcement が変更されたか。
- Android 17 で deprecation warning、lint、manifest validation、compat framework entry が追加されたか。
- `minSdkVersion` / `targetSdkVersion` / API level による branch があるか。
- Network Security Configuration と `usesCleartextTraffic` の precedence が Android 17 で変わったか。

## 適用条件（Applicability）

この変更がいつ適用されるかを OS 条件と targetSdkVersion 条件に分けて説明する。

### OS アップデート時の挙動（OS Update Behavior）

- Android 17 に OS アップデートしただけで適用されるか: 公式文書上、即時の runtime behavior change は確認できない。将来 release の deprecation plan と migration guidance と読む。
- targetSdkVersion に依存しない根拠: All apps ページに掲載されているが、本文は targetSdkVersion gate ではなく `minSdkVersion` と Network Security Configuration support を説明している。
- Android 16 以前での挙動: 未確認。Android 17 tag との明示的な比較ができないため、Android 16 source だけから platform evidence として断定しない。

### targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- targetSdkVersion 37 以上で適用されるか: 公式文書上、この項目に targetSdkVersion 37 条件は示されていない。AOSP gate 未確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: Unknown。公式文書は Android 17 page 上の guidance として説明している。
- opt-out / temporary override の有無: 未確認。公式文書は opt-out ではなく migration path として Network Security Configuration を示している。

### その他の条件（Other Conditions）

- device/form factor: 公式文書からは条件なし。
- permission: 公式文書からは permission 条件なし。
- API usage: unencrypted HTTP connection、Network Security Configuration、`cleartextTrafficPermitted`。
- manifest attribute: `android:usesCleartextTraffic`。
- component boundary: manifest parser、network security policy、Network Security Configuration parser、HTTP stack / library にまたがる可能性。

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
- `core/java/android/content/pm/ApplicationInfo.java`
- `core/java/android/security/NetworkSecurityPolicy.java`
- `core/java/android/security/net/config/` 以下の Network Security Configuration parser / policy path
- manifest parsing / `android:usesCleartextTraffic` attribute handling path
- API surface files / `current.txt` における deprecation annotation の有無
- compat framework 定義ファイル内の cleartext traffic / network security 関連 Change ID
- lint / build tooling 側に移行 warning がある場合、その該当 project

## 確認したソース文脈（Source Context Reviewed）

AOSP tag diff は未実行。以下は公式文書から見た確認予定の source context であり、AOSP evidence ではない。

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| Manifest parsing / `android:usesCleartextTraffic` | 未確認 | future release で deprecate 予定と公式文書が説明 | manifest attribute が引き続き認識されるか、deprecation annotation / warning があるか確認するため |
| `NetworkSecurityPolicy` / cleartext policy evaluation | 未確認 | Network Security Configuration への移行が推奨される | 実際に HTTP cleartext connection の許可判定へ影響する app-facing policy path |
| Network Security Configuration parser / `cleartextTrafficPermitted` | 未確認 | domain 単位の cleartext connection 指定が推奨される | `usesCleartextTraffic` から移行する設定先の挙動を確認するため |
| API surface / docs annotations | 未確認 | `usesCleartextTraffic` deprecation plan が文書化 | Android 17 で actual deprecation annotation が追加されたか確認するため |

必須記入項目（Required context）:
- Entry point / caller: 未確認。想定される entry point は app manifest parsing -> ApplicationInfo cleartext policy -> Network Security Configuration -> network stack の cleartext permission check。
- Relevant class or service responsibility: manifest attribute parsing、Network Security Configuration parsing、cleartext traffic policy evaluation。
- Runtime path from app API / system event to changed code: app が HTTP cleartext connection を開始 -> network stack / policy が cleartext permitted state を参照 -> manifest attribute または Network Security Configuration の設定で許可可否を決める、という path が想定される。AOSP evidence としては未確認。
- Why unrelated code paths were excluded: tag diff 未実行のため、除外判断は未完了。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
| Android 17 tag 未取得のため source diff 未確認 | 公式文書上は immediate behavior change ではなく deprecation plan / migration guidance と読める | `usesCleartextTraffic` の future deprecation と Network Security Configuration への移行が説明されている | Low |

必須分類（Required interpretation）:
- Added behavior: 未確認。公式文書上、Android 17 で新しい runtime behavior が追加されたとは明記されていない。
- Removed behavior: 未確認。公式文書上、Android 17 で `usesCleartextTraffic` が削除されたとは説明されていない。
- Changed condition / gate: 未確認。`minSdkVersion < 24` と `minSdkVersion >= 24` の guidance はあるが、Android 17 runtime gate かは未確認。
- Changed default: 未確認。cleartext traffic default が Android 17 で変更されたとは公式文書上確認できない。
- No behavior change found: 未確認。AOSP tag 不在のため断定しない。ただし公式文書上は future deprecation plan の可能性が高い。

## 事実（Evidence）

事実:
- 公式文書は `usesClearTraffic deprecation plan` を Android 17 `Behavior changes: all apps` ページに掲載している。
- 公式文書は、future release で `usesCleartextTraffic` element を deprecate する計画があると説明している。
- 公式文書は、unencrypted HTTP connection が必要なアプリに Network Security Configuration file への移行を推奨している。
- 公式文書は、Network Security Configuration により cleartext connection が必要な domain を指定できると説明している。
- 公式文書は、Network Security Configuration files が API level 24 以上でのみサポートされると説明している。
- 公式文書は、`minSdkVersion < 24` のアプリでは `usesCleartextTraffic="true"` と Network Security Configuration の両方を使うべきと説明している。
- 公式文書は、`minSdkVersion >= 24` のアプリでは Network Security Configuration を使えば `usesCleartextTraffic` は不要と説明している。

観察:
- All apps ページ掲載だが、本文は Android 17 runtime enforcement ではなく将来の deprecation plan を示している。
- `targetSdkVersion` ではなく `minSdkVersion` が migration path の分岐として示されている。
- この項目は「互換性破壊が Android 17 で即時発生する」というより、cleartext traffic 設定を domain-scoped configuration へ移す準備項目として扱うのが適切である。

仮説:
- Android 17 時点では `usesCleartextTraffic` はまだ機能し、将来 release で deprecation / removal / warning 強化が行われる可能性がある。
- Android 17 AOSP または tooling には、deprecation annotation、lint warning、documentation-only update のいずれかが存在する可能性がある。
- 実際の runtime enforcement 変更は future release 側で発生する可能性が高い。

結論:
- 現時点の確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE`。公式文書上は Android 17 で即時の runtime behavior change があるとは読めず、future deprecation plan / migration guidance と見る。
- 顧客向けには、Android 17 で今すぐ HTTP 接続が壊れる変更としてではなく、将来 deprecation に備えて Network Security Configuration へ移行する準備項目として説明する。

## 適用ゲート根拠（Applicability Gate Evidence）

- targetSdkVersion gate: 未確認。公式文書上、この項目に targetSdkVersion 37 条件はない。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。
- @EnabledAfter / @EnabledSince / default state: 未確認。
- Build.VERSION / SDK_INT gate: 未確認。公式文書は future release と説明している。
- DeviceConfig / resources config: 未確認。
- Permission/AppOps gate: 公式文書からは確認できない。
- Manifest/property gate: `android:usesCleartextTraffic` と Network Security Configuration / `cleartextTrafficPermitted` が関係する。
- No gate found: 未確認。AOSP tag 未取得のため gate search 未実行。
- Gate conclusion: 公式文書上は future deprecation plan + migration guidance。Android 17 runtime gate は未確認。AOSP evidence 未取得のため `UNKNOWN_NEEDS_MORE_EVIDENCE`。
- Reasoning from source context: source context は未確認。公式文書の page type と statement のみから一次判断している。

---

# 影響分析（Impact Analysis）

## 影響を受けるアプリ（Affected Apps）

- unencrypted HTTP connection が必要なアプリ。
- `android:usesCleartextTraffic` によって cleartext traffic を許可しているアプリ。
- domain 単位の Network Security Configuration をまだ導入していないアプリ。
- `minSdkVersion >= 24` で、`usesCleartextTraffic` を残したまま Network Security Configuration に移行していないアプリ。
- `minSdkVersion < 24` で、API 24 未満互換性と API 24 以上の Network Security Configuration を両立する必要があるアプリ。

## 影響を受けないアプリ（Non-Affected Apps）

- HTTP cleartext connection を使わないアプリ。
- すべて HTTPS に移行済みのアプリ。
- Network Security Configuration で必要 domain のみ cleartext を許可しているアプリ。
- ただし、future release での deprecation details は未確認であり、将来影響の有無は再確認が必要。

---

# 顧客影響（Customer Impact）

顧客説明用。

## 影響度（Impact Level）

- 要確認

※ 仮評価。最終判断は人間が行う。

## ビジネス影響（Business Impact）

- ユーザー影響: Android 17 時点で即時に HTTP 接続が失敗する変更とは公式文書上確認できない。将来 release で deprecation が進むと、未移行アプリの HTTP 接続や legacy endpoint 連携に影響する可能性がある。
- セキュリティ影響: app-wide cleartext 許可から domain-scoped allowlist へ移行することで、不要な HTTP 通信許可を減らせる。
- 開発影響: manifest attribute 依存を棚卸しし、Network Security Configuration の導入、domain allowlist、`minSdkVersion` 別の互換性確認が必要になる。
- 運用影響: HTTP endpoint が残っている backend / partner integration を特定し、HTTPS 化または domain-scoped cleartext policy の管理が必要になる。

---

# サービス影響例（Service Impact Examples）

このセクションは、公式文書と未確認の AOSP 調査観点から導いた「起こりうる影響例」を記録する。
特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: Legacy HTTP endpoint を持つアプリ

- 対象サービス例: 社内端末向けアプリ、古い IoT / gateway 連携、閉域網 API。
- 影響を受ける実装パターン: `usesCleartextTraffic="true"` で app-wide に HTTP を許可している。
- 発生条件: future release で `usesCleartextTraffic` deprecation が進み、Network Security Configuration へ未移行の場合。
- ユーザーに見える症状: 将来 release で HTTP endpoint への接続が失敗する可能性。
- 開発・運用への影響: HTTP endpoint の棚卸し、HTTPS 化、Network Security Configuration の domain allowlist 作成が必要。
- 推奨対応候補: `res/xml/network_security_config.xml` を導入し、必要 domain のみ `cleartextTrafficPermitted="true"` にする。
- 根拠: 公式文書は Network Security Configuration への移行を推奨している。
- Confidence（信頼度）: Low。future release の enforcement details は未確認。
- 注意: 実サービスで発生確認した事実ではない。

## 例2（Example 2）: minSdkVersion 23 以下を維持するアプリ

- 対象サービス例: 古い Android device をサポートする consumer / enterprise app。
- 影響を受ける実装パターン: API 23 以下もサポートしつつ、API 24 以上では Network Security Configuration を使いたい。
- 発生条件: `minSdkVersion < 24` で Network Security Configuration だけに移行し、API 23 以下の behavior を考慮しない場合。
- ユーザーに見える症状: 古い OS で HTTP 接続許可の意図が反映されない可能性。
- 開発・運用への影響: `usesCleartextTraffic="true"` と Network Security Configuration を併用し、OS version ごとの挙動を確認する必要がある。
- 推奨対応候補: `minSdkVersion` を確認し、API 24 未満向けには manifest attribute、API 24 以上向けには Network Security Configuration を使う。
- 根拠: 公式文書は `minSdkVersion < 24` では両方を使うよう説明している。
- Confidence（信頼度）: Medium for documentation guidance, Low for Android 17 implementation. AOSP tag 未確認。
- 注意: 実サービスで発生確認した事実ではない。

---

# 対応候補（Required Actions）

## 必須対応（Must）

- `android:usesCleartextTraffic` を使っている manifest を棚卸しする。
- HTTP cleartext endpoint を使っている通信経路を洗い出す。
- `minSdkVersion` が 24 未満か 24 以上かを確認し、移行方法を分ける。
- Android 17 で即時 runtime break があると決めつけず、将来 deprecation に備えた migration item として管理する。

## 推奨対応（Recommended）

- `minSdkVersion >= 24` のアプリは Network Security Configuration へ移行し、`usesCleartextTraffic` への依存をなくす。
- `minSdkVersion < 24` のアプリは `usesCleartextTraffic="true"` を残しつつ、API 24 以上向けに Network Security Configuration を導入する。
- Network Security Configuration では、app-wide ではなく必要 domain のみ `cleartextTrafficPermitted="true"` にする。
- HTTP endpoint は可能な限り HTTPS 化する。
- CI / lint / manifest review で `usesCleartextTraffic` の利用を検出し、移行 backlog に入れる。

## 任意対応（Optional）

- backend / partner API の HTTP endpoint を棚卸しし、HTTPS 化ロードマップを作る。
- future Android release での deprecation enforcement に備え、Android 17 以降の release notes / compat framework を継続監視する。
- Android 17 AOSP tag 公開後に、actual deprecation annotation / warning / runtime policy change の有無を再確認する。

---

# 検証方法（Verification Method）

変更を確認する方法。

## 検証マトリクス（Matrix）

| 端末 OS（Device OS） | targetSdkVersion | Compat flag / test control | 期待挙動（Expected behavior） |
| --- | --- | --- | --- |
| Android 16 | 36 | default | baseline。`usesCleartextTraffic` と Network Security Configuration の現行挙動を確認する。 |
| Android 17 | 36 | default | 公式文書上、即時 runtime behavior change は未確認。HTTP cleartext policy が Android 16 と同じか確認する。 |
| Android 17 | 37 | default | targetSdkVersion 37 による差分がないか確認する。公式文書上は targetSdkVersion gate なし。 |
| Android 17 | 36 | force-enabled if available | Compat flag 未確認。存在する場合は cleartext policy 変更単体の影響を確認する。 |
| Android 17 | 37 | force-disabled if available | Compat flag 未確認。存在する場合は rollback / opt-out 可能性を確認する。 |

## 手順（Steps）

- targetSdk変更: targetSdkVersion 36 / 37 の両方で検証し、targetSdkVersion 差分があるか確認する。
- compat framework command: 未確認。Android 17 tag 公開後に Change ID が存在する場合のみ force-enable / force-disable を検証する。
- テスト方法:
  - `usesCleartextTraffic="true"` のみ。
  - Network Security Configuration のみ。
  - `usesCleartextTraffic="true"` + Network Security Configuration 併用。
  - `minSdkVersion < 24` と `minSdkVersion >= 24` の build variant。
  - allowed domain / non-allowed domain への HTTP connection。
- 再現手順:
  - HTTP endpoint を用意する。
  - test app に manifest attribute と Network Security Configuration の組み合わせを設定する。
  - Android 16 / Android 17、targetSdkVersion 36 / 37 で HTTP connection の成否を比較する。
  - logcat、exception、NetworkSecurityPolicy の結果を確認する。
- 期待結果:
  - 公式文書どおり future deprecation plan のみであれば、Android 17 時点では `usesCleartextTraffic` の runtime behavior は大きく変わらない可能性がある。
  - Network Security Configuration では、許可した domain のみ cleartext connection が許可されることを確認する。

---

# 結論（Conclusion）

`usesClearTraffic deprecation plan` は Android 17 all apps ページに掲載されているが、公式文書の主張は「Android 17 で即時に cleartext traffic 挙動が変わる」ではなく、「将来 release で `usesCleartextTraffic` element を deprecate する計画があるため Network Security Configuration へ移行する」という guidance である。

ただし、Android 17 AOSP tag が local `frameworks-base` に存在しないため、actual deprecation annotation、manifest parsing、runtime policy、compat framework entry は未確認である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

Android app developer は、HTTP cleartext endpoint と `usesCleartextTraffic` 依存を棚卸しし、`minSdkVersion` に応じて Network Security Configuration へ移行する準備を進める必要がある。

---

# 人間の判断欄（Human Decision Placeholder）

最終優先度（Final Priority）:
- Human decision required

判断（Decision）:
- Further investigation required after Android 17 AOSP tag is available

判断理由候補:
- 公式文書上は future deprecation plan であり、Android 17 即時の runtime behavior change とは断定できない。
- 顧客影響は HTTP cleartext endpoint の有無、`usesCleartextTraffic` 利用、`minSdkVersion`、Network Security Configuration 移行状況に依存する。

---

# 参照（References）

## ドキュメント（Documentation）

- https://developer.android.com/about/versions/17/behavior-changes-all
- https://developer.android.com/guide/topics/manifest/application-element#usesCleartextTraffic
- https://developer.android.com/privacy-and-security/security-config
- https://developer.android.com/training/articles/security-config#CleartextTrafficPermitted

## AOSP

- 未確認。local `frameworks-base` に Android 17 AOSP tag がないため、tag diff による source evidence は未取得。

# ECH (Encrypted Client Hello) の有効化

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
- https://developer.android.com/privacy-and-security/security-config#domainEncryption
- https://developer.android.com/privacy-and-security/security-config#EncryptedClientHelloSummary
- https://www.rfc-editor.org/rfc/rfc9849.html#name-grease-ech

セクション:
ECH (Encrypted Client Hello) enabled

ページ種別:
- Android 17 以上をターゲットにするアプリ

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- TARGET_SDK_37_CONDITIONAL

公式文書からの初期適用条件判断:
- 公式 Behavior Change 文書は、targetSdkVersion 37 以上のアプリでは TLS connection に ECH が使われると説明している。
- ただし ECH が実際に有効になるには、アプリが使う networking library が ECH を統合していること、remote server が ECH protocol をサポートしていることが必要。
- Network Security Configuration の `<domainEncryption>` により、global または per-domain で ECH mode を `"enabled"` / `"disabled"` に設定できる。
- AOSP では `ENABLE_DEFAULT_ENCRYPTED_CLIENT_HELLO = 419020719L` が `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)` として定義され、targetSdkVersion 37 以上で default domain encryption mode が有効側になる。

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | No | `ENABLE_DEFAULT_ENCRYPTED_CLIENT_HELLO` は `@EnabledAfter(BAKLAVA)` の compat change。 |
| targetSdkVersion 37 以上が必要か | Yes | AOSP Change ID が targetSdkVersion 37 以上で デフォルト有効。 |
| 追加の実行時条件があるか | ある | networking library の ECH support、remote server の ECH support、TLS connection、`<domainEncryption>` mode が条件。 |
| Compat Change ID が関係するか | Yes | `ENABLE_DEFAULT_ENCRYPTED_CLIENT_HELLO = 419020719L`。 |

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
- targetSdkVersion: 37 以上。AOSP の `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)` で確認。
- Device/form factor: 公式抜粋では条件なし。
- Permission/API/component condition: TLS connection、ECH 対応 networking library、ECH 対応 server、Network Security Configuration の `<domainEncryption>` mode。
- App state/process condition: remote endpoint への TLS handshake 実行時。

Compat framework:
- Change ID: `419020719`
- 変更名: `ENABLE_DEFAULT_ENCRYPTED_CLIENT_HELLO`
- 既定状態: targetSdkVersion 36 では デフォルト無効、targetSdkVersion 37 以上で デフォルト有効。
- テスト時に切り替え可能か: compat change として切り替え可能。

分類信頼度（Classification confidence）:
- High

分類根拠（Classification evidence）:
- 公式ドキュメントページ: `behavior-changes-17`
- 検証対象の適用条件文: targetSdkVersion 37 以上のアプリでは TLS connection に ECH が使われる。
- AOSP targetSdk gate: `packages/NetworkSecurityConfig/platform/src/android/security/net/config/NetworkSecurityConfig.java` の `ENABLE_DEFAULT_ENCRYPTED_CLIENT_HELLO` が `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)`。
- Compat framework entry: `ENABLE_DEFAULT_ENCRYPTED_CLIENT_HELLO = 419020719L`。

---

# エグゼクティブサマリー

Android 17 では、targetSdkVersion 37 以上のアプリに対して Encrypted Client Hello (ECH) の platform support が導入される、と公式文書は説明している。ECH は TLS handshake の Server Name Indication (SNI) を暗号化し、ネットワーク観測者が接続先ドメインを特定しにくくするための privacy 機能である。

実際に ECH が使われるには、アプリが使う networking library が ECH に対応し、接続先 server も ECH をサポートしている必要がある。ECH を negotiated できない場合は ECH GREASE が送信される。また、Android 17 では Network Security Configuration に `<domainEncryption>` が追加され、global または per-domain で ECH を enabled / disabled にできる。

AOSP では `NetworkSecurityConfig.defaultDomainEncryptionMode()` が `CompatChanges.isChangeEnabled(ENABLE_DEFAULT_ENCRYPTED_CLIENT_HELLO)` と `encryptedClientHelloConfiguration()` を確認し、条件を満たす場合に `DOMAIN_ENCRYPTION_MODE_OPPORTUNISTIC` を返す。`XmlConfigSource` は `<domainEncryption>` を parse し、`disabled` / `enabled` / `opportunistic` を Network Security Config に反映する。

---

# 公式ドキュメント確認

## 原文（Statement）

ページタイトル:
- Behavior changes: Apps targeting Android 17 or higher

ページ URL:
- https://developer.android.com/about/versions/17/behavior-changes-17

ページ種別:
- Android 17 をターゲットにするアプリ

セクションタイトル:
- ECH (Encrypted Client Hello) enabled

検証対象の原文:

> ECH is used for TLS connections

公式文書は、Android 17 / API level 37 以上をターゲットにするアプリでは TLS connection に ECH が使われると説明している。また、ECH が有効になるにはアプリの networking library と remote server の両方が ECH をサポートする必要があること、negotiation に失敗した場合は ECH GREASE になること、`<domainEncryption>` により global または domain 単位で挙動を調整できることも説明している。

## 解釈（Interpretation）

この変更は、targetSdkVersion 37 以上のアプリにおける TLS 接続の privacy behavior を変更する。従来の TLS handshake では SNI により接続先ドメインが観測され得るが、ECH は SNI を含む ClientHello の機微情報を暗号化し、接続先ドメインの露出を減らす。

ただし、アプリ単体の targetSdkVersion だけで必ず ECH が negotiated されるわけではない。networking library、server support、DNS / ECH configuration、Network Security Configuration の `<domainEncryption>` mode が実際の挙動を左右する。

---

# 変更内容（What Changed）

公式文書上の変更点:
- Android 17 は ECH の platform support を導入する。
- targetSdkVersion 37 以上のアプリでは TLS connection に ECH が使われる。
- ECH は networking library が ECH support を統合し、remote server も ECH protocol をサポートしている場合に active になる。
- ECH を negotiated できない場合、client は randomized contents を持つ ECH extension、つまり ECH GREASE を送る。
- Android 17 は Network Security Configuration に `<domainEncryption>` element を追加する。
- `<domainEncryption>` は `<base-config>` または `<domain-config>` 内で使え、global または per-domain に ECH mode を `"enabled"` / `"disabled"` へ設定できる。
- Network Security Configuration docs は、`<domainEncryption>` の default mode が targetSdkVersion 37 以上では `"enabled"`、それ以外では `"disabled"` と説明している。

AOSP で確認した点:
- `ENABLE_DEFAULT_ENCRYPTED_CLIENT_HELLO = 419020719L` は `@ChangeId` かつ `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)`。
- `defaultDomainEncryptionMode()` は compat change と `encryptedClientHelloConfiguration()` が true の場合に `DOMAIN_ENCRYPTION_MODE_OPPORTUNISTIC`、それ以外では `DOMAIN_ENCRYPTION_MODE_DISABLED` を返す。
- `NetworkSecurityConfig.Builder` の `mDomainEncryptionMode` default は `defaultDomainEncryptionMode()`。
- `XmlConfigSource` は `<domainEncryption mode="disabled|enabled|opportunistic">` を parse して builder に反映する。
- `NetworkSecurityPolicy` に `DOMAIN_ENCRYPTION_MODE_*` 定数と `getDomainEncryptionMode(String)` API surface が追加されている。

## 適用条件

公式文書と AOSP 根拠 から、Android 17 以上、targetSdkVersion 37 以上、TLS connection、ECH 対応 networking library、ECH 対応 server、`<domainEncryption>` mode が条件となる変更として分類する。

### OS アップデート時の挙動（OS Update Behavior）

- Android 17 にアップデートしただけで適用されるか: No。targetSdkVersion 36 では compat change が デフォルト有効 ではない。
- targetSdkVersion に依存しない根拠: なし。AOSP は `@EnabledAfter(BAKLAVA)` を使う。
- Android 16 以前での挙動: Network Security Configuration docs は Android 16 以下では ECH は available ではないと説明している。AOSP でも Android 17 tag で default domain encryption mode と parser が追加されている。

### targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- targetSdkVersion 37 以上で適用されるか: Yes。`ENABLE_DEFAULT_ENCRYPTED_CLIENT_HELLO` が `@EnabledAfter(BAKLAVA)` で デフォルト有効。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: Android 17 platform の `frameworks-base` 実装に依存する。Android 16 platform には本調査対象の `<domainEncryption>` 実装はない。
- opt-out / temporary override の有無: `<domainEncryption mode="disabled"/>` による opt-out が可能。compat change としてテスト時に切り替え可能。

### その他の条件（Other Conditions）

- device/form factor: 公式抜粋では条件なし。
- permission: 公式抜粋では条件なし。
- API usage: TLS connection を行う networking library。例として HttpEngine、WebView、OkHttp が挙げられている。
- manifest attribute: Network Security Configuration file の指定が関係する可能性がある。
- component boundary: platform Network Security Configuration、networking library、remote server の三者にまたがる。

---

# AOSP 調査（AOSP Investigation）

## チェックアウト状態

根拠利用前に確認したコマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list 'android-17*'
```

結果:
- `frameworks-base` working tree: clean at the time of investigation.
- From tag: `android-16.0.0_r4` exists.
- To tag: `android-17.0.0_r1` exists.

根拠上の制約（Evidence limitation）:
- ソース根拠 は `android-16.0.0_r4` と `android-17.0.0_r1` の明示的な tag 比較、および `android-17.0.0_r1` 上の symbol 確認に限定した。
- `frameworks-base` working tree は clean のため、ローカル作業ツリーの変更 を platform 根拠 として誤採用するリスクは確認されていない。

## 関連ファイル（Related Files）

- `packages/NetworkSecurityConfig/platform/src/android/security/net/config/NetworkSecurityConfig.java`
- `packages/NetworkSecurityConfig/platform/src/android/security/net/config/XmlConfigSource.java`
- `packages/NetworkSecurityConfig/platform/src/android/security/net/config/ApplicationConfig.java`
- `packages/NetworkSecurityConfig/platform/src/android/security/net/config/ConfigNetworkSecurityPolicy.java`
- `packages/NetworkSecurityConfig/platform/src/android/security/NetworkSecurityPolicy.java`
- `packages/NetworkSecurityConfig/api/current.txt`

注記:
- `android-17.0.0_r1`の`frameworks-base`ではNetwork Security Configとpolicy APIまで確認済みである。実際のECH handshake implementationを担うnetworking library / TLS stack側projectは本調査の検索範囲外であり、追加evidence対象として残る。

## 確認したソース文脈（Source Context Reviewed）

| File / symbol | Android 16 baseline | Android 17 behavior | 関連性 |
| --- | --- | --- | --- |
| `NetworkSecurityConfig.ENABLE_DEFAULT_ENCRYPTED_CLIENT_HELLO` | ECH default の compat gate は存在しない。 | Change ID `419020719L` が追加され、`@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)` で targetSdkVersion 37 以上 デフォルト有効。 | 公式文書の targetSdkVersion 37 条件を直接裏付ける gate。 |
| `NetworkSecurityConfig.defaultDomainEncryptionMode()` | default domain encryption mode は存在しない。 | compat change と `encryptedClientHelloConfiguration()` が true の場合に `DOMAIN_ENCRYPTION_MODE_OPPORTUNISTIC`、それ以外で disabled。 | targetSdkVersion 37 default behavior を決める実装。 |
| `XmlConfigSource` / `domainEncryption` | `<domainEncryption>` parser は存在しない。 | `<base-config>` / `<domain-config>` 内の `domainEncryption` を parse し、builder に mode を反映する。 | 公式文書の global / per-domain mode 設定を裏付ける。 |
| `NetworkSecurityPolicy.getDomainEncryptionMode(String)` | API surface なし。 | domain encryption mode を取得する API surface が追加される。 | Network Security Config policy が library / TLS stack から参照可能になる根拠。 |

必要な context:
- Entry point / caller: app の TLS connection -> networking library / TLS stack -> `NetworkSecurityPolicy.getDomainEncryptionMode(hostname)`。
- 関連 class / service の責務: `NetworkSecurityConfig` は domain ごとの security policy を保持し、`XmlConfigSource` は app の Network Security Config XML を parse する。
- app API / system event から変更箇所までの runtime path: app TLS handshake -> hostname の Network Security Config lookup -> domain encryption mode -> ECH / GREASE の有効化判断。
- 関係しない code path を除外した理由: CT default enable は同じ `NetworkSecurityConfig` 内の別 Change ID であり、ECH の gate とは別変更として除外した。

## 差分解釈（Diff Interpretation）

| 観測した diff | 解釈 | Behavior Change との関連 | 信頼度 |
| --- | --- | --- | --- |
| `ENABLE_DEFAULT_ENCRYPTED_CLIENT_HELLO = 419020719L` が `@EnabledAfter(BAKLAVA)` で定義される。 | changed condition / gate | targetSdkVersion 37 以上で default domain encryption mode が有効側になる直接根拠。 | High |
| `defaultDomainEncryptionMode()` が compat change を確認し、default を opportunistic / disabled に分岐する。 | changed default | Android 17 / targetSdkVersion 37 の default behavior を決める実装。 | High |
| `XmlConfigSource` が `<domainEncryption>` を parse する。 | added behavior / explicit override path | 公式文書の global / per-domain enabled / disabled 設定を裏付ける。 | High |
| `NetworkSecurityPolicy` に domain encryption mode API surface が追加される。 | API surface addition supporting behavior | TLS stack / networking library が policy を参照できる接点。 | Medium |

必要な解釈:
- 追加された挙動: `<domainEncryption>` parser と domain encryption mode policy。
- 削除された挙動: public API の削除は確認していない。
- 変更された条件 / gate: targetSdkVersion 37 以上で default domain encryption mode が opportunistic。
- 変更された default: targetSdkVersion 37 以上では デフォルト無効 ではなく opportunistic。
- 挙動変更なし: 該当しない。

## 事実（Evidence）

事実:
- 公式 Behavior Change 文書は、Android 17 が ECH platform support を導入すると述べている。
- 公式文書は、targetSdkVersion 37 以上のアプリでは TLS connection に ECH が使われると述べている。
- 公式文書は、ECH が active になるには networking library と remote server の ECH support が必要と述べている。
- 公式文書は、ECH を negotiated できない場合に ECH GREASE が送信されると述べている。
- 公式文書は、Network Security Configuration に `<domainEncryption>` が追加され、`<base-config>` / `<domain-config>` 内で ECH mode を指定できると述べている。
- Network Security Configuration docs は、`<domainEncryption>` の default mode が API level 37 以上で `"enabled"`、それ以外で `"disabled"` と説明している。
- RFC 9849 は、ECH を実装する client が実 ECH extension または GREASE ECH extension を送る client behavior を定義している。
- local `frameworks-base` には `android-16.0.0_r4` tag がある。
- local `frameworks-base` には `android-17.0.0_r1` tag がある。
- 調査時点で `frameworks-base` working tree は clean。
- AOSP では `ENABLE_DEFAULT_ENCRYPTED_CLIENT_HELLO = 419020719L` が `@EnabledAfter(BAKLAVA)` として定義される。
- AOSP では default domain encryption mode が compat change と ECH config flag の両方を満たす場合に `OPPORTUNISTIC` になる。

観察:
- 公式ページ種別は targetSdkVersion 37 以上向けである。
- この項目は privacy behavior change と Network Security Configuration の新要素追加の両方を含む。
- 実際の ECH negotiated behavior は、app targetSdkVersion だけでなく networking library と server support に依存する。
- `<domainEncryption mode="disabled"/>` により opt-out できる。
- AOSP gate は targetSdkVersion 37 以上で デフォルト有効 であり、公式文書と一致する。
- `encryptedClientHelloConfiguration()` の platform flag が false の環境では default opportunistic path が抑止されるため、実端末では platform flag / module state も確認対象になる。

仮説:
- Android 17 / targetSdkVersion 37 以上では、Network Security Configuration の default domain encryption mode が enabled になり、ECH 対応 library が TLS handshake 時に ECH または ECH GREASE を送る可能性が高い。
- targetSdkVersion 36 のアプリでは compat change が デフォルト無効 のため、default mode は disabled。
- 一部の enterprise network、TLS inspection、domain-based filtering、allowlist / blocklist 運用では、SNI visibility 低下または GREASE extension により観測・制御の前提が変わる可能性がある。

結論:
- 公式文書と AOSP 根拠 が一致するため、primary classification は `TARGET_SDK_37_CONDITIONAL` とする。
- Android 17 / targetSdkVersion 37 以上で、ECH 対応 networking library / server を使い、`<domainEncryption>` が disabled でない場合に ECH / GREASE behavior が適用される。

## 適用ゲート根拠（Applicability Gate Evidence）

- targetSdkVersion ゲート: `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)`。targetSdkVersion 37 以上で デフォルト有効。
- CompatChanges.isChangeEnabled / ChangeId: `CompatChanges.isChangeEnabled(ENABLE_DEFAULT_ENCRYPTED_CLIENT_HELLO)`、Change ID `419020719L`。
- @EnabledAfter / @EnabledSince / default state: `@EnabledAfter(BAKLAVA)`。targetSdkVersion 36 では デフォルト無効、37 以上では デフォルト有効。
- Build.VERSION / SDK_INT gate: Android 17 platform implementation として扱う。明示的な SDK_INT runtime gate は主根拠ではない。
- DeviceConfig / resources config: `encryptedClientHelloConfiguration()` の platform flag が default opportunistic path の追加条件。
- Permission/AppOps gate: 公式文書上は permission 条件なし。確認した AOSP の Network Security Config gate でも permission / AppOps 条件は主条件ではない。
- Manifest/property gate: Network Security Configuration の `<domainEncryption>` mode により domain 単位で `disabled` / `enabled` / `opportunistic` を指定できる。
- No gate found: 該当しない。
- ゲート結論: Android 17 上で targetSdkVersion 37 以上、かつ TLS connection / ECH 対応 library / ECH 対応 server / config 条件を満たす場合に ECH が使われる。
- Reasoning from source context: `NetworkSecurityConfig` が domain encryption mode を保持し、`NetworkSecurityPolicy.getDomainEncryptionMode(hostname)` 経由で library / TLS stack が参照できる。

検索済み:
- `frameworks-base` checkout status。
- `android-16.0.0_r4` tag の存在。
- `android-17.0.0_r1` tag の存在。
- Change ID、targetSdkVersion ゲート、domain encryption mode default、`<domainEncryption>` parser、API surface。

未検索:
- networking library / TLS stack integration points。
- `encryptedClientHelloConfiguration()` の product / module default。

---

# 影響分析

## 影響を受けるアプリ（Affected Apps）

影響を受ける可能性があるアプリ:
- targetSdkVersion 37 以上への更新を予定しているアプリ。
- HTTPS / TLS connection を行い、ECH 対応 networking library を使うアプリ。
- HttpEngine、WebView、OkHttp などの ECH 対応版を使うアプリ。
- 接続先 server が ECH をサポートしているアプリ。
- Network Security Configuration を使い、domain ごとに通信ポリシーを制御しているアプリ。
- enterprise network、TLS inspection、SNI ベースの allowlist / blocklist、通信監視環境で動作するアプリ。

## 影響を受けないアプリ（Non-Affected Apps）

影響が限定的と考えられるケース:
- TLS connection を行わないアプリ。
- ECH 非対応 networking library のみを使うアプリ。
- 接続先 server が ECH をサポートせず、かつ ECH GREASE も disabled にしている構成。
- `<domainEncryption mode="disabled"/>` で対象 domain の ECH / ECH GREASE を無効化している構成。
- targetSdkVersion 37 へ上げないアプリ。AOSP gate 上は targetSdkVersion 36 では デフォルト無効。

---

# 顧客影響

## 影響度

- 人間による判断が必要

※ 最終 severity / priority は人間が判断する。このレポートでは確定しない。

## ビジネス影響

- ユーザー影響: SNI が暗号化されることで、ユーザーの接続先ドメインがネットワーク観測者に見えにくくなり privacy が向上する可能性がある。
- 運用影響: SNI を前提とする enterprise proxy、TLS inspection、domain filtering、traffic monitoring では、接続判定や可観測性の前提が変わる可能性がある。
- 開発影響: targetSdkVersion 37 更新前に、利用 networking library の ECH 対応状況、server support、Network Security Configuration の `<domainEncryption>` policy を確認する必要がある。

---

# サービス影響例

このセクションは、公式文書と AOSP 根拠 から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: Microsoft 365 / Salesforce / Slack を使う企業ネットワーク環境

- 具体サービス例: Microsoft 365、Salesforce、Slack などの SaaS を、MDM 管理端末や社内 proxy / TLS inspection 環境から利用する業務アプリ。
- 影響を受ける実装パターン: ClientHello / SNI を network appliance が観測する前提の TLS inspection / routing / policy enforcement。
- 発生条件: Android 17 で ECH が有効になり、network appliance が期待する hostname visibility が変わる場合。
- ユーザーに見える症状: 社内ネットワークで接続失敗、proxy policy mismatch、特定 endpoint だけ接続できない可能性。
- 技術的に起きていること: ECH により ClientHello の一部が暗号化され、SNI ベースの routing / allowlist / inspection が従来どおりに機能しない可能性がある。
- 開発・運用への影響: network team と ECH 対応、DNS / HTTPS RR、proxy policy の確認が必要になる可能性。
- 推奨対応候補: ECH 詳細ページと network policy を照合し、検証環境で endpoint 別接続テストを行う。
- 根拠: 公式 Behavior Change statement、AOSP の domain encryption default gate、`<domainEncryption>` parser。
- 信頼度: Medium
- 注意: 上記 SaaS で発生確認した事実ではない。ECH availability は DNS / server / network condition に依存する。

## 例2（Example 2）: Cloudflare WARP / Zscaler / Netskope のようなネットワーク保護・診断連携

- 具体サービス例: Cloudflare WARP、Zscaler Client Connector、Netskope Client、社内 network diagnostics tool。
- 影響を受ける実装パターン: TLS handshake metadata や SNI を前提に接続先分類・診断を行う実装。
- 発生条件: platform networking が ECH を使い、外部から見える handshake 情報が変わる場合。
- ユーザーに見える症状: 診断結果が不正確になる、接続先分類が失敗する、policy 表示が変わる可能性。
- 技術的に起きていること: app / network agent が観測できる TLS metadata が減り、SNI ベース分類の精度や説明可能性が変わる。
- 開発・運用への影響: ECH 対応の telemetry / logging / support documentation 更新が必要になる可能性。
- 推奨対応候補: public hostname 依存を減らし、app-layer / explicit config による診断へ寄せる。
- 根拠: 公式 statement、AOSP の domain encryption mode API surface、Network Security Config policy。
- 信頼度: Medium
- 注意: 上記サービスで発生確認した事実ではない。実際の可観測性は library / TLS stack / network path に依存する。

---

# 対応候補（Required Actions）

## 必須対応（Must）

- アプリが使う networking library が ECH をサポートしているか確認する。
- 接続先 server / CDN / hosting provider が ECH をサポートしているか確認する。
- enterprise network、TLS inspection、SNI ベース制御が関係する顧客環境があるか確認する。
- targetSdkVersion 37 更新前に Android 17 上で主要 endpoint への TLS 接続テストを行う。

## 推奨対応（Recommended）

- Network Security Configuration に `<domainEncryption>` を追加する必要がある domain がないか確認する。
- ECH を許可したい domain と、互換性理由で一時的に disable したい domain を分ける。
- failure 時の telemetry を用意し、ECH negotiation failure、ECH GREASE、TLS handshake failure、HTTP layer failure を区別できるようにする。
- WebView / OkHttp / HttpEngine などの library version と Android 17 support note を確認する。

## 任意対応（Optional）

- packet capture / TLS handshake logging が可能な検証環境で、ECH enabled / disabled の差分を観測する。

---

# 検証方法（Verification Method）

## 検証マトリクス（Matrix）

| 端末 OS | targetSdkVersion | Compat flag | 期待される挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | default | Android 16 baseline。公式 docs では ECH は available ではない。 |
| Android 17 | 36 | default | `ENABLE_DEFAULT_ENCRYPTED_CLIENT_HELLO` は デフォルト無効。domain encryption default は disabled。 |
| Android 17 | 37 | default | 公式文書上は ECH が TLS connection に使われる。library / server support がある場合に active。未 negotiated 時は ECH GREASE。 |
| Android 17 | 36 | force-enabled | `ENABLE_DEFAULT_ENCRYPTED_CLIENT_HELLO` を有効化すると default opportunistic path を検証できる。`<domainEncryption mode="enabled"/>` による config 明示は別途検証対象。 |
| Android 17 | 37 | force-disabled | `ENABLE_DEFAULT_ENCRYPTED_CLIENT_HELLO` を無効化すると デフォルト無効 path との切り分けができる。`<domainEncryption mode="disabled"/>` による opt-out は公式 docs 上あり。 |

## 手順（Steps）

- targetSdk変更: test app を targetSdkVersion 36 と 37 で build し、Android 17 上で同じ endpoint へ TLS connection を行う。
- compat framework command: `adb am compat enable|disable ENABLE_DEFAULT_ENCRYPTED_CLIENT_HELLO <package>`、または Change ID `419020719` を使って切り替える。
- テスト方法: ECH 対応 server と非対応 server、ECH 対応 networking library と非対応 library、`<domainEncryption mode="enabled"/>` / `"disabled"` を組み合わせる。
- 再現手順: TLS handshake、connection success / failure、server support、network observer 上の SNI visibility、GREASE extension の有無を比較する。
- 期待結果: targetSdkVersion 37 かつ ECH 対応 library / server では ECH が active になる。ECH negotiated 不可の場合は ECH GREASE が送信される。targetSdkVersion 36 では デフォルト無効。

---

# 結論（Conclusion）

公式文書は、Android 17 で targetSdkVersion 37 以上のアプリに ECH support が導入され、TLS connection の SNI 露出を減らすと説明している。実際の効果は、networking library、server support、Network Security Configuration の `<domainEncryption>` mode に依存する。

AOSP では `ENABLE_DEFAULT_ENCRYPTED_CLIENT_HELLO = 419020719L` が `@EnabledAfter(BAKLAVA)` として定義され、`defaultDomainEncryptionMode()` と `<domainEncryption>` parser が追加されていることを確認した。primary classification は `TARGET_SDK_37_CONDITIONAL`、confidence は High とする。

Human decision placeholder:
- 最終優先度: 人間による判断が必要
- 最終 severity: 人間による判断が必要
- リリース可否: 人間による判断が必要
- 顧客連絡の優先度: 人間による判断が必要
- 次に必要な人間の判断: ECH による enterprise network / TLS inspection 影響をどの優先度で顧客へ案内するかを判断する。

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

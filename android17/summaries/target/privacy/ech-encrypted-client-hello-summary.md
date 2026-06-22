# ECH (Encrypted Client Hello) の有効化 - 1ページ要約

## 対象

Android 17 Behavior Change

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

## 適用条件

- 主分類（Primary classification）: TARGET_SDK_37_CONDITIONAL
- OS アップデート / 全アプリ（OS update / all apps）: No。AOSP の compat change は targetSdkVersion 37 以上で デフォルト有効。
- targetSdkVersion 37 以上: Yes。`@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)` により確認。
- その他の必須条件（Other required conditions）: TLS connection、ECH 対応 networking library、ECH 対応 server、`<domainEncryption>` mode、platform ECH configuration。
- Compat Change ID: `419020719` (`ENABLE_DEFAULT_ENCRYPTED_CLIENT_HELLO`)
- Compat default state: targetSdkVersion 36 では デフォルト無効、targetSdkVersion 37 以上で デフォルト有効。

## 早見マトリクス

| シナリオ | 影響 |
| --- | --- |
| Android 17 / targetSdkVersion 36 | AOSP gate 上は デフォルト無効。OS アップデートだけでは default ECH は有効にならない。 |
| Android 17 / targetSdkVersion 37 | default domain encryption mode が opportunistic になる。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | networking library と server が ECH 対応なら ECH が active。negotiated 不可なら ECH GREASE。 |

## 要約

Android 17 では、targetSdkVersion 37 以上のアプリに ECH support が導入され、TLS handshake の SNI を暗号化して接続先ドメインの露出を減らす、と公式文書は説明している。AOSP では `ENABLE_DEFAULT_ENCRYPTED_CLIENT_HELLO` が targetSdkVersion 37 以上で デフォルト有効 になり、`NetworkSecurityConfig.defaultDomainEncryptionMode()` が条件を満たす場合に `DOMAIN_ENCRYPTION_MODE_OPPORTUNISTIC` を返す。

## 顧客影響

- targetSdkVersion 37 更新時に、ECH 対応 networking library / server / enterprise network policy の組み合わせで TLS 接続挙動が変わる可能性がある。
- SNI を前提にした TLS inspection、domain filtering、traffic monitoring では、観測・制御の前提が変わる可能性がある。

## 影響対象（Who Is Affected）

- 対象アプリ: targetSdkVersion 37 へ更新する、HTTPS / TLS connection を行うアプリ。
- 対象機能: HttpEngine、WebView、OkHttp などの networking library、Network Security Configuration、enterprise network / TLS inspection / SNI-based filtering。
- 対象条件: networking library と remote server が ECH をサポートし、`<domainEncryption>` が disabled ではない場合。

## 対応要否

- 必須対応: 利用 networking library と接続先 server / CDN の ECH support を確認する。
- 推奨対応: `<domainEncryption>` で global / per-domain の enabled / disabled 方針を決め、Android 17 / targetSdkVersion 37 で TLS 接続テストを行う。
- 不要: TLS connection を行わない、または ECH 非対応 library のみを使うアプリでは直接影響は限定的。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 36 | 本調査対象の `<domainEncryption>` / default ECH gate は存在しない。 |
| Android 17 | 36 | compat change が デフォルト無効 のため、default domain encryption mode は disabled。 |
| Android 17 | 37 | default domain encryption mode が opportunistic になり、条件を満たす TLS connection で ECH / GREASE が使われ得る。 |

## 顧客向け説明

Android 17 では、targetSdkVersion 37 以上のアプリで TLS 接続時に ECH が使われる可能性があります。ECH は SNI を暗号化し、ネットワーク上の観測者がアプリの接続先ドメインを特定しにくくする privacy 機能です。ただし、実際に ECH が有効になるには、アプリの networking library と接続先 server の両方が ECH をサポートしている必要があります。

互換性上の懸念がある場合、Android 17 の Network Security Configuration で `<domainEncryption mode="disabled"/>` を global または per-domain に設定できます。AOSP では `defaultDomainEncryptionMode()` が compat change と platform ECH configuration を確認し、条件を満たす場合に opportunistic mode を返します。

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-17
- Network Security Configuration: https://developer.android.com/privacy-and-security/security-config#domainEncryption
- Encrypted Client Hello summary: https://developer.android.com/privacy-and-security/security-config#EncryptedClientHelloSummary
- RFC 9849 GREASE ECH: https://www.rfc-editor.org/rfc/rfc9849.html#name-grease-ech
- 検証対象の原文: targetSdkVersion 37 以上のアプリでは TLS connection に ECH が使われ、library / server support が必要。未 negotiated 時は ECH GREASE。`<domainEncryption>` で mode を制御可能。
- AOSP ファイル: `NetworkSecurityConfig.java`, `XmlConfigSource.java`, `ApplicationConfig.java`, `ConfigNetworkSecurityPolicy.java`, `NetworkSecurityPolicy.java`, `packages/NetworkSecurityConfig/api/current.txt`
- AOSP ソース文脈: app の TLS connection -> networking library / TLS stack -> `NetworkSecurityPolicy.getDomainEncryptionMode(hostname)` -> domain encryption mode lookup。
- 差分解釈: `ENABLE_DEFAULT_ENCRYPTED_CLIENT_HELLO` の追加は changed condition / gate、`defaultDomainEncryptionMode()` は changed default、`XmlConfigSource` の `<domainEncryption>` parser は added behavior、`NetworkSecurityPolicy` API は supporting API surface addition。
- ゲート結論: Android 17 上で targetSdkVersion 37 以上、かつ TLS connection / ECH 対応 library / ECH 対応 server / config 条件を満たす場合に ECH または ECH GREASE が使われ得る。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 人間による判断が必要

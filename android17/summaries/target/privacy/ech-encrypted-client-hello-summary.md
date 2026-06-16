# ECH (Encrypted Client Hello) の有効化 - 1ページ要約

## 対象（Target）

Android 17 Behavior Change

比較元:
- android-16.0.0_r4

比較先:
- TBD: Android 17 AOSP tag

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

## 適用条件（Applicability）

- 主分類（Primary classification）: UNKNOWN_NEEDS_MORE_EVIDENCE
- OS アップデート / 全アプリ（OS update / all apps）: 未確認。公式ページは targetSdkVersion 37 以上向け。
- targetSdkVersion 37 以上: 公式文書上は該当。AOSP gate 未確認。
- その他の必須条件（Other required conditions）: TLS connection、ECH 対応 networking library、ECH 対応 server、`<domainEncryption>` mode。
- Compat Change ID: 未確認
- Compat default state: 未確認

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 未確認。Network Security Configuration docs は API 37 未満で default disabled と示すが、AOSP gate 未確認。 |
| Android 17 / targetSdkVersion 37 | 公式文書上は TLS connection に ECH が使われる。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | networking library と server が ECH 対応なら ECH が active。negotiated 不可なら ECH GREASE。 |

## 要約（Summary）

Android 17 では、targetSdkVersion 37 以上のアプリに ECH support が導入され、TLS handshake の SNI を暗号化して接続先ドメインの露出を減らす、と公式文書は説明している。

## 顧客影響（Customer Impact）

- 要確認

## 影響対象（Who Is Affected）

- 対象アプリ: targetSdkVersion 37 へ更新する、HTTPS / TLS connection を行うアプリ。
- 対象機能: HttpEngine、WebView、OkHttp などの networking library、Network Security Configuration、enterprise network / TLS inspection / SNI-based filtering。
- 対象条件: networking library と remote server が ECH をサポートし、`<domainEncryption>` が disabled ではない場合。

## 対応要否（Required Action）

- 必須対応: 利用 networking library と接続先 server / CDN の ECH support を確認する。
- 推奨対応: `<domainEncryption>` で global / per-domain の enabled / disabled 方針を決め、Android 17 / targetSdkVersion 37 で TLS 接続テストを行う。
- 不要: TLS connection を行わない、または ECH 非対応 library のみを使うアプリでは直接影響は限定的。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 16 | 36 | 公式 docs では ECH は available ではない。AOSP baseline diff は未確認。 |
| Android 17 | 36 | 未確認。default disabled と読めるが AOSP gate 未確認。 |
| Android 17 | 37 | 公式文書上は TLS connection に ECH が使われ、条件未充足時は ECH GREASE が送信される。 |

## 顧客向け説明（Explanation for Customers）

Android 17 では、targetSdkVersion 37 以上のアプリで TLS 接続時に ECH が使われるようになります。ECH は SNI を暗号化し、ネットワーク上の観測者がアプリの接続先ドメインを特定しにくくする privacy 機能です。ただし、実際に ECH が有効になるには、アプリの networking library と接続先 server の両方が ECH をサポートしている必要があります。

互換性上の懸念がある場合、Android 17 の Network Security Configuration で `<domainEncryption mode="disabled"/>` を global または per-domain に設定できます。現時点では local AOSP checkout に Android 17 tag がないため、targetSdkVersion gate、parser diff、compat flag の有無は未確認です。

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-17
- Network Security Configuration: https://developer.android.com/privacy-and-security/security-config#domainEncryption
- Encrypted Client Hello summary: https://developer.android.com/privacy-and-security/security-config#EncryptedClientHelloSummary
- RFC 9849 GREASE ECH: https://www.rfc-editor.org/rfc/rfc9849.html#name-grease-ech
- 検証対象の原文: targetSdkVersion 37 以上のアプリでは TLS connection に ECH が使われ、library / server support が必要。未 negotiated 時は ECH GREASE。`<domainEncryption>` で mode を制御可能。
- AOSP ファイル: 未確認。local `frameworks-base` に `android-17*` tag がない。
- AOSP ソース文脈: 未確認。tag 間 diff が実行できない。
- 差分解釈: 未分類。added behavior / changed condition / changed default の判定は Android 17 tag 待ち。
- Gate conclusion: 未確認。公式文書は targetSdkVersion 37 以上と runtime / config 条件を示すが、AOSP gate evidence は未取得。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 追加調査が必要

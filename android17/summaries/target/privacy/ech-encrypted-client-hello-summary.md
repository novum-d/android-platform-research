# ECH (Encrypted Client Hello) 有効 - 1ページ要約

## 対象

Android 17 挙動変更

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP タグ

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

## 適用条件

- 主分類（Primary classification）: UNKNOWN_NEEDS_MORE_EVIDENCE
- OS アップデート / 全アプリ: 未確認。公式ページは targetSdkVersion 37+ 向け。
- targetSdkVersion 37 以上: 公式文書上は該当。AOSP 適用ゲートは未確認。
- その他の必須条件: TLS 接続、ECH 対応 networking library、ECH 対応 server、`<domainEncryption>` mode。
- Compat Change ID: 未確認
- Compat のデフォルト状態: 未確認

## 早見マトリクス

| シナリオ | 影響 |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 未確認。ネットワークセキュリティ設定 docs は API 37 未満でデフォルト無効と示すが、AOSP 適用ゲートは未確認。 |
| Android 17 / targetSdkVersion 37 | 公式文書上は TLS 接続に ECH が使われる。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | networking library と server が ECH 対応なら ECH が active。negotiated 不可なら ECH GREASE。 |

## 要約

Android 17 では、targetSdkVersion 37 以上のアプリに ECH support が導入され、TLS handshake の SNI を暗号化して接続先ドメインの露出を減らす、と公式文書は説明している。

## 顧客影響

- 要確認

## 影響対象

- 対象アプリ: targetSdkVersion 37 へ更新する、HTTPS / TLS 接続を行うアプリ。
- 対象機能: HttpEngine、WebView、OkHttp などの networking library、ネットワークセキュリティ設定、enterprise network / TLS inspection / SNI-based filtering。
- 対象条件: networking library と remote server が ECH をサポートし、`<domainEncryption>` が無効ではない場合。

## 対応要否

- 必須対応: 利用 networking library と接続先 server / CDN の ECH support を確認する。
- 推奨対応: `<domainEncryption>` で global / per-domain の有効 / 無効方針を決め、Android 17 / targetSdkVersion 37 で TLS 接続テストを行う。
- 不要: TLS 接続を行わない、または ECH 非対応 library のみを使うアプリでは直接影響は限定的。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 36 | 公式 docs では ECH は利用可能ではない。AOSP 基準挙動 diff は未確認。 |
| Android 17 | 36 | 未確認。デフォルト無効と読めるが、AOSP 適用ゲートは未確認。 |
| Android 17 | 37 | 公式文書上は TLS 接続に ECH が使われ、条件未充足時は ECH GREASE が送信される。 |

## 顧客向け説明

Android 17 では、targetSdkVersion 37 以上のアプリで TLS 接続時に ECH が使われるようになります。ECH は SNI を暗号化し、ネットワーク上の観測者がアプリの接続先ドメインを特定しにくくする privacy 機能です。ただし、実際に ECH が有効になるには、アプリの networking library と接続先 server の両方が ECH をサポートしている必要があります。

互換性上の懸念がある場合、Android 17 のネットワークセキュリティ設定で `<domainEncryption mode="disabled"/>` を global または per-domain に設定できます。現時点ではローカル AOSP checkout に Android 17 タグがないため、targetSdkVersion 適用ゲート、parser diff、compat flag の有無は未確認です。

## 根拠

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-17
- ネットワークセキュリティ設定: https://developer.android.com/privacy-and-security/security-config#domainEncryption
- Encrypted Client Hello 要約: https://developer.android.com/privacy-and-security/security-config#EncryptedClientHelloSummary
- RFC 9849 GREASE ECH: https://www.rfc-エディタ.org/rfc/rfc9849.html#name-grease-ech
- 検証対象の原文: targetSdkVersion 37+ のアプリでは TLS 接続に ECH が使われ、library / server support が必要。未 negotiated 時は ECH GREASE。`<domainEncryption>` で mode を制御可能。
- AOSP ファイル: 未確認。ローカルの `frameworks-base` に `android-17*` タグがない。
- AOSP ソース文脈: 未確認。タグ間差分を実行できない。
- 差分解釈: 未分類。追加された挙動 / 変更された条件 / 変更されたデフォルトの判定は Android 17 タグ待ち。
- 適用ゲートの結論: 未確認。公式文書は targetSdkVersion 37+ と実行時 / 設定条件を示すが、AOSP 適用ゲート根拠は未取得。

## 人間の判断欄

最終優先度（Final Priority）:
- Human decision required

判断（Decision）:
- 追加調査が必要

# BC-005: ECH enabled

## 基本情報（Basic Information）

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/17/behavior-changes-17
- Section: ECH enabled

Original statement:
> targetSdkVersion 37 以上のアプリでは TLS connection に ECH が使われる可能性がある、という趣旨の公式説明。

調査対象 Android バージョン:
- From: android-16.0.0_r4
- To: android-17.0.0_r1

## 対象アプリとの関係（Relevance to Target App）

関連するアプリ機能:
- HTTPS / TLS 通信。
- CDN / API / WebView。
- 企業ネットワークや TLS inspection 環境での利用。

関連する API / permission / component:
- Network Security Config `<domainEncryption>`。
- platform networking library。
- ECH 対応 server / CDN。

アプリが該当する可能性:
- Conditional。HTTPS 通信と ECH 対応 library / server 条件がある。

## 適用条件分類（Applicability Classification）

主分類（Primary classification）:
- TARGET_SDK_37_CONDITIONAL

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | No | compat change は targetSdkVersion 37 以上で default enabled。 |
| targetSdkVersion 37 以上が必要か | Yes | `ENABLE_DEFAULT_ENCRYPTED_CLIENT_HELLO`。 |
| 追加の実行時条件があるか | Yes | TLS、ECH 対応 library / server、domain encryption mode。 |
| Compat Change ID が関係するか | Yes | `419020719`。 |

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17。
- targetSdkVersion: 37 以上。
- Permission/API/component condition: TLS connection。
- Manifest/property condition: `<domainEncryption>` が disabled でないこと。
- Mainline/module condition: platform ECH configuration。

Compat framework:
- Change ID: `419020719`
- Change name: `ENABLE_DEFAULT_ENCRYPTED_CLIENT_HELLO`
- Default state: targetSdkVersion 37 以上で default enabled。
- Toggleable for testing: compat change として確認候補。

## AOSP 調査（AOSP Investigation）

関連ファイル:
- `NetworkSecurityConfig.java`
- `XmlConfigSource.java`
- `ApplicationConfig.java`
- `ConfigNetworkSecurityPolicy.java`
- `NetworkSecurityPolicy.java`

確認したソース文脈（Source Context Reviewed）:

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `NetworkSecurityConfig.defaultDomainEncryptionMode()` | default ECH gate なし | 条件を満たす場合に opportunistic mode | TLS 接続の domain encryption policy に直接関係する。 |
| `XmlConfigSource` / `<domainEncryption>` | 設定なし | domain encryption parser 追加 | app 側で ECH 方針を制御できる。 |

差分解釈（Diff Interpretation）:
- Added behavior: `<domainEncryption>` parser / API surface。
- Changed default: targetSdkVersion 37 以上で opportunistic mode。
- Changed condition / gate: Change ID `419020719`。

適用ゲート根拠（Applicability Gate Evidence）:
- targetSdkVersion gate: targetSdkVersion 37 以上。
- CompatChanges.isChangeEnabled / ChangeId: `419020719`。
- Gate conclusion: Android 17 / targetSdkVersion 37 / TLS / ECH 対応条件で適用。

## 事実・観察・仮説・結論（Facts / Observations / Hypotheses / Conclusion）

事実（Facts）:
- Android 17 / targetSdkVersion 37 で default domain encryption mode が opportunistic になり得る。

観察（Observations）:
- ECH は privacy improvement であり、一般ユーザー環境では問題になりにくい可能性がある。

仮説（Hypotheses）:
- 企業ネットワーク、SNI-based filtering、TLS inspection を前提にした環境では接続観測・制御の前提が変わる可能性。

結論（Conclusion）:
- 通信先と利用 library を確認し、必要なら Network Security Config の domain encryption 方針を決める。

## アプリ影響（App Impact）

想定される影響:
- 一部ネットワーク環境で通信観測・制御・トラブルシュートが変わる可能性。

ユーザー影響:
- 通常は軽微。ただし企業ネットワーク等で接続問題が出る可能性。

開発者影響:
- `<domainEncryption>` の global / per-domain 方針を検討する。

推奨対応候補:
- ECH 対応 library / server / CDN を確認する。
- Android 17 / targetSdkVersion 37 で主要 endpoint へ接続する。

## Confidence

Confidence:
- High

Confidence の根拠:
- AOSP Change ID、Network Security Config API、domain encryption path を確認済み。

不足している根拠:
- 対象アプリの networking library / endpoint。

---

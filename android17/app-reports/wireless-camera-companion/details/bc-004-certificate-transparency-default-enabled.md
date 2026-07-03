# BC-004: Enable CT by default

## 基本情報（Basic Information）

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/17/behavior-changes-17
- Section: Enable CT by default

Original statement:
> targetSdkVersion 37 以上のアプリでは certificate transparency が default enabled になる、という趣旨の公式説明。

調査対象 Android バージョン:
- From: android-16.0.0_r4
- To: android-17.0.0_r1

## 対象アプリとの関係（Relevance to Target App）

関連するアプリ機能:
- HTTPS API。
- アカウント連携。
- ファームウェア情報取得。
- クラウド同期。
- 利用規約 / お知らせ / ヘルプ表示。
- staging / test endpoint。

関連する API / permission / component:
- platform TLS / HTTPS。
- Network Security Config。
- certificate pinning。

アプリが該当する可能性:
- Conditional。HTTPS 通信がある場合は該当。

判断理由:
- カメラ連携アプリでもクラウド API、サポート情報、利用規約、ファームウェア情報など HTTPS 通信を行う可能性が高い。

## 適用条件分類（Applicability Classification）

主分類（Primary classification）:
- TARGET_SDK_37_CONDITIONAL

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | No | Change ID は targetSdkVersion 37 以上で default enabled。 |
| targetSdkVersion 37 以上が必要か | Yes | `DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY`。 |
| 追加の実行時条件があるか | Yes | TLS / HTTPS、CT policy、証明書チェーン、Network Security Config。 |
| Compat Change ID が関係するか | Yes | `407952621`。 |

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17。
- targetSdkVersion: 37 以上。
- Permission/API/component condition: platform TLS / HTTPS certificate validation。
- Manifest/property condition: Network Security Config の CT 設定。

Compat framework:
- Change ID: `407952621`
- Change name: `DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY`
- Default state: targetSdkVersion 37 以上で default enabled。
- Toggleable for testing: compat change として確認候補。

## AOSP 調査（AOSP Investigation）

関連ファイル:
- `packages/NetworkSecurityConfig/platform/src/android/security/net/config/NetworkSecurityConfig.java`
- `NetworkSecurityTrustManager.java`
- `RootTrustManager.java`
- `XmlConfigSource.java`

確認したソース文脈（Source Context Reviewed）:

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `NetworkSecurityConfig` / CT default policy | CT は app opt-in が必要 | targetSdkVersion 37 以上で default enabled | platform TLS validation の default policy に直接関係する。 |

差分解釈（Diff Interpretation）:
- Changed default: CT default policy が targetSdkVersion 37 以上で有効。
- Changed condition / gate: Change ID `407952621`。

適用ゲート根拠（Applicability Gate Evidence）:
- targetSdkVersion gate: targetSdkVersion 37 以上。
- CompatChanges.isChangeEnabled / ChangeId: `407952621`。
- Gate conclusion: Android 17 / targetSdkVersion 37 / platform TLS / HTTPS 接続に適用。

## 事実・観察・仮説・結論（Facts / Observations / Hypotheses / Conclusion）

事実（Facts）:
- Android 17 / targetSdkVersion 37 では CT default enabled。

観察（Observations）:
- production endpoint は問題ない可能性が高いが、staging、private PKI、device-local HTTPS、pinning では要確認。

仮説（Hypotheses）:
- 対象アプリが private CA、自己署名、local HTTPS endpoint、古い証明書チェーンを利用している場合、targetSdkVersion 37 更新時に接続影響が出る可能性。

結論（Conclusion）:
- 通信先棚卸しと Android 17 / targetSdkVersion 37 接続テストが必要。

## アプリ影響（App Impact）

想定される影響:
- HTTPS 接続失敗。
- ログイン、クラウド同期、サポート表示、ファームウェア情報取得の失敗。

ユーザー影響:
- 一部ネットワーク機能が利用できない可能性。

開発者影響:
- 証明書チェーン、pinning、Network Security Config、staging endpoint の見直し。

推奨対応候補:
- 全 endpoint の証明書チェーンを確認する。
- Android 17 / targetSdkVersion 37 で接続テストする。

## Confidence

Confidence:
- High

Confidence の根拠:
- AOSP Change ID と Network Security Config path を確認済み。

不足している根拠:
- 対象アプリの endpoint / certificate policy。

---

# CT のデフォルト有効化 - 1ページ要約

## 対象（Target）

Android 17 Behavior Change

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

## 適用条件（Applicability）

- 主分類（Primary classification）: TARGET_SDK_37_CONDITIONAL
- OS アップデート / 全アプリ（OS update / all apps）: No。AOSP の Change ID は targetSdkVersion 37 以上で default enabled。
- targetSdkVersion 37 以上: Yes。`@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)` で確認。
- その他の必須条件（Other required conditions）: TLS / HTTPS 通信、certificate transparency policy、Network Security Config、証明書チェーン。
- Compat Change ID: `407952621` / `DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY`
- Compat default state: targetSdkVersion 36 では default disabled、targetSdkVersion 37 以上で default enabled

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | default では CT は明示 opt-in が必要。 |
| Android 17 / targetSdkVersion 37 | 公式文書上は CT が default enabled。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | CT 要件を満たさない証明書チェーンを使う HTTPS 接続で失敗する可能性。 |

## 要約（Summary）

Android 17 では、targetSdkVersion 37 以上のアプリで certificate transparency (CT) が default enabled になる、と公式文書は説明している。

## 顧客影響（Customer Impact）

- 要確認

## 影響対象（Who Is Affected）

- 対象アプリ: targetSdkVersion 37 へ更新し、platform TLS / HTTPS 通信を行うアプリ。
- 対象機能: API 通信、ログイン、決済、コンテンツ取得、staging / internal endpoint への接続。
- 対象条件: CT 要件を満たさない証明書チェーン、Network Security Config の CT 設定、証明書 pinning / private PKI との組み合わせ。

## 対応要否（Required Action）

- 必須対応: HTTPS 接続先の証明書チェーンが CT 要件を満たすか棚卸しする。
- 推奨対応: Android 16 の opt-in または Android 17 / targetSdkVersion 37 環境で CT 有効時の接続テストを行う。
- 不要: ネットワーク通信を行わないアプリ、または全接続先が CT 要件を満たすことを確認済みのアプリでは直接影響は限定的。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 16 | 36 | 公式文書上、CT は available だが app opt-in が必要。 |
| Android 17 | 36 | `DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY` は default disabled。CT は明示 opt-in が必要。 |
| Android 17 | 37 | CT が default enabled。CT 要件を満たさない証明書チェーンでは接続影響の可能性。 |

## 顧客向け説明（Explanation for Customers）

Android 17 では、targetSdkVersion 37 以上のアプリで certificate transparency が既定で有効になります。Android 16 ではアプリが明示的に opt in した場合だけ CT が使われていましたが、Android 17 / targetSdkVersion 37 では opt in していない接続にも CT policy が適用される可能性があります。

そのため、公開 HTTPS endpoint、staging endpoint、private PKI、証明書 pinning を利用する通信について、証明書チェーンが CT 要件を満たしているか確認してください。Android 17 AOSP tag `android-17.0.0_r1` では、`DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY = 407952621L` が `@EnabledAfter(BAKLAVA)` として定義され、`NetworkSecurityConfig` の default policy に反映されます。

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-17
- 検証対象の原文: targetSdkVersion 37 以上のアプリでは certificate transparency が default enabled。Android 16 では CT は available だが opt in が必要。
- AOSP ファイル: `packages/NetworkSecurityConfig/platform/src/android/security/net/config/NetworkSecurityConfig.java`, `NetworkSecurityTrustManager.java`, `RootTrustManager.java`, `XmlConfigSource.java`
- AOSP ソース文脈: Change ID、`@EnabledAfter(BAKLAVA)`、`certificateTransparencyVerificationRequiredDefault()`、Conscrypt policy path を確認。
- 差分解釈: changed condition / changed default / added behavior。targetSdkVersion 37 default enable gate と TrustManager policy path。
- Gate conclusion: Android 17 上で targetSdkVersion 37 以上、かつ platform TLS / HTTPS certificate validation を使う通信に CT default policy が適用される。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 人間による判断が必要

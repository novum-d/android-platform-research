# CT のデフォルト有効化 - 1ページ要約

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
- OS アップデート / 全アプリ: いいえ。AOSP の Change ID は targetSdkVersion 37 以上でデフォルト有効。
- targetSdkVersion 37 以上: はい。`@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)` で確認。
- その他の必須条件: TLS / HTTPS 通信、certificate transparency policy、Network Security Config、証明書チェーン。
- Compat Change ID: `407952621` / `DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY`
- Compat default state: targetSdkVersion 36 ではデフォルト無効、targetSdkVersion 37 以上でデフォルト有効

## 早見マトリクス

| シナリオ | 影響 |
| --- | --- |
| Android 17 / targetSdkVersion 36 | デフォルトでは CT は明示 opt-in が必要。 |
| Android 17 / targetSdkVersion 37 | 公式文書上は CT がデフォルト有効。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | CT 要件を満たさない証明書チェーンを使う HTTPS 接続で失敗する可能性。 |

## 要約

Android 17 では、targetSdkVersion 37 以上のアプリで certificate transparency (CT) がデフォルト有効になる、と公式文書は説明している。

## 顧客影響

- 要確認

## 影響対象

- 対象アプリ: targetSdkVersion 37 へ更新し、platform TLS / HTTPS 通信を行うアプリ。
- 対象機能: API 通信、ログイン、決済、コンテンツ取得、staging / internal endpoint への接続。
- 対象条件: CT 要件を満たさない証明書チェーン、Network Security Config の CT 設定、証明書 pinning / private PKI との組み合わせ。

## 対応要否

- 必須対応: HTTPS 接続先の証明書チェーンが CT 要件を満たすか棚卸しする。
- 推奨対応: Android 16 の opt-in または Android 17 / targetSdkVersion 37 環境で CT 有効時の接続テストを行う。
- 不要: ネットワーク通信を行わないアプリ、または全接続先が CT 要件を満たすことを確認済みのアプリでは直接影響は限定的。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 36 | 公式文書上、CT は利用可能だがアプリの opt-in が必要。 |
| Android 17 | 36 | `DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY` はデフォルト無効。CT は明示 opt-in が必要。 |
| Android 17 | 37 | CT がデフォルト有効。CT 要件を満たさない証明書チェーンでは接続影響の可能性。 |

## 顧客向け説明

Android 17 では、targetSdkVersion 37 以上のアプリで certificate transparency が既定で有効になります。Android 16 ではアプリが明示的に opt-in した場合だけ CT が使われていましたが、Android 17 / targetSdkVersion 37 では opt-in していない接続にも CT policy が適用される可能性があります。

そのため、公開 HTTPS endpoint、staging endpoint、private PKI、証明書 pinning を利用する通信について、証明書チェーンが CT 要件を満たしているか確認してください。Android 17 AOSP タグ `android-17.0.0_r1` では、`DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY = 407952621L` が `@EnabledAfter(BAKLAVA)` として定義され、`NetworkSecurityConfig` のデフォルト ポリシーに反映されます。

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-17
- 検証対象の原文: targetSdkVersion 37 以上のアプリでは certificate transparency がデフォルト有効。Android 16 では CT は利用可能だが opt-in が必要。
- AOSP ファイル: `packages/NetworkSecurityConfig/platform/src/android/security/net/config/NetworkSecurityConfig.java`, `NetworkSecurityTrustManager.java`, `RootTrustManager.java`, `XmlConfigSource.java`
- AOSP ソース文脈: Change ID、`@EnabledAfter(BAKLAVA)`、`certificateTransparencyVerificationRequiredDefault()`、Conscrypt policy path を確認。
- 差分解釈: changed condition / changed default / added behavior。targetSdkVersion 37 のデフォルト有効化ゲートと TrustManager policy path。
- ゲート結論: Android 17 上で targetSdkVersion 37 以上、かつ platform TLS / HTTPS certificate validation を使う通信に CT デフォルト ポリシーが適用される。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 人間による判断が必要

## 再検証記録（2026-08-22）

- Android 17 の公式 Behavior Change 一覧と最新通常AOSPタグを再確認した。
- 対応する[主レポート](../../../behavior-changes/target/security/enable-ct-by-default.md)で official section、AOSP project / remote / checkout、解決済み commit、比較 command、dirty risk を再検証した。
- 主レポートの分類、confidence、未確認事項を維持し、実機未実施の項目を Observed 済みへ変更していない。
- 全件の結果は[再検証台帳](../../../analysis/REVALIDATION_2026-08-22.md)を参照する。

# CT のデフォルト有効化

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
- https://developer.android.com/privacy-and-security/security-config#CertificateTransparencySummary
- https://developer.android.com/privacy-and-security/security-config#certificateTransparency

セクション:
Enable CT by default

ページ種別:
- Android 17 以上をターゲットにするアプリ

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- TARGET_SDK_37_CONDITIONAL

公式文書からの初期適用条件判断:
- 公式文書は、targetSdkVersion 37 以上のアプリでは certificate transparency (CT) がデフォルトで有効になると説明している。
- Android 16 では CT は利用可能だったが、アプリが opt-in する必要があったと説明している。
- 追加条件として、TLS / HTTPS 接続、証明書チェーン、CT log 証明、Network Security Config による opt-in / opt-out などが関係する可能性がある。
- AOSP では `DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY = 407952621L` が `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)` として定義され、targetSdkVersion 37 以上で CT のデフォルト有効化が適用される。

早見表（影響の早見）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | いいえ | `DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY` は `@EnabledAfter(BAKLAVA)` の compat change。 |
| targetSdkVersion 37 以上が必要か | はい | AOSP Change ID が targetSdkVersion 37 以上でデフォルト有効になる。 |
| 追加の実行時条件があるか | はい | platform TLS / HTTPS 証明書検証、CT policy、Network Security Config、証明書チェーンが関係する。 |
| Compat Change ID が関係するか | はい | `DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY = 407952621L`。 |

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
- [ ] 未確認 / 追加根拠が必要

必要な実行時条件（Required runtime conditions）:
- Android バージョン: Android 17 以上。
- targetSdkVersion: 37 以上。AOSP の `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)` で確認。
- 端末 / フォーム ファクタ: 公式抜粋では条件なし。
- 権限 / API / コンポーネント条件: TLS / HTTPS 通信、platform trust manager / Network Security Config、certificate transparency policy。
- アプリ状態 / プロセス条件: アプリがサーバー証明書を検証するネットワーク接続を行う時点。

Compat framework:
- Change ID: `407952621`
- 変更名: `DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY`
- 既定状態: targetSdkVersion 36 ではデフォルト無効、targetSdkVersion 37 以上でデフォルト有効。
- テスト時に切り替え可能か: compat change として切り替え可能。

分類信頼度（Classification confidence）:
- High

分類根拠（Classification evidence）:
- 公式ドキュメントページ: `behavior-changes-17`
- 検証対象の適用条件文: Android 17 / API level 37 以上を target にするアプリでは CT がデフォルト有効になり、Android 16 では opt-in が必要だった。
- AOSP targetSdk ゲート: `packages/NetworkSecurityConfig/platform/src/android/security/net/config/NetworkSecurityConfig.java` の `DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY` が `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)`。
- Compat framework entry: `DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY = 407952621L`。

---

# エグゼクティブサマリー

Android 17 では、targetSdkVersion 37 以上のアプリで certificate transparency (CT) がデフォルトで有効になる、と公式文書は説明している。Android 16 では CT は利用可能だったが、Network Security Config などでアプリが opt-in する必要があった。

この変更により、公開 TLS 証明書を使う HTTPS 接続で CT 要件を満たさない証明書チェーンがある場合、targetSdkVersion 37 更新後に接続失敗などの互換性影響が発生する可能性がある。特に独自 CA、private PKI、検証環境、証明書発行運用が CT に対応していない場合は確認が必要である。

AOSP では `NetworkSecurityConfig.certificateTransparencyVerificationRequiredDefault()` が `certificateTransparencyDefaultEnabled()` と `CompatChanges.isChangeEnabled(DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY)` を確認して CT のデフォルト状態を決める。`RootTrustManager` / `NetworkSecurityTrustManager` は Conscrypt へ `ConscryptNetworkSecurityPolicy` を渡すコードパスを持つため、platform TLS 証明書検証に接続される。

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
- Enable CT by default

検証対象の原文:

> If an app targets Android 17 (API level 37) or higher, certificate transparency (CT) is enabled by default. (On Android 16, CT is available but apps had to opt in.)

## 解釈（Interpretation）

この変更は、Network Security Config / platform TLS validation における certificate transparency のデフォルト ポリシーを、targetSdkVersion 37 以上のアプリで opt-in からデフォルト有効に変える security behavior change である。

アプリ開発者にとって重要なのは、targetSdkVersion 37 へ更新しただけで、従来 CT に opt-in していなかった TLS 接続にも CT 検証が適用される可能性がある点である。証明書やサーバー運用が CT 要件を満たしていない場合、通信失敗として現れる可能性がある。

---

# 変更内容（What Changed）

公式文書上の変更点:
- Android 17 / targetSdkVersion 37 以上のアプリでは certificate transparency (CT) がデフォルトで有効になる。
- Android 16 では CT は利用可能だったが、アプリが opt-in する必要があった。
- Network Security Config の CT 関連ドキュメントが参照されているため、アプリの network security policy と TLS 証明書検証に関係する変更と考えられる。

AOSP で確認した点:
- `DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY = 407952621L` は `@ChangeId` かつ `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)`。
- `certificateTransparencyVerificationRequiredDefault()` は `certificateTransparencyDefaultEnabled()` と `CompatChanges.isChangeEnabled(DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY)` が true の場合にデフォルト true を返す。
- `NetworkSecurityConfig.Builder` の `mCertificateTransparencyVerificationRequired` はデフォルト値として `certificateTransparencyVerificationRequiredDefault()` を使う。
- `RootTrustManager.getNetworkSecurityPolicy()` と `NetworkSecurityConfig.setNetworkSecurityPolicy()` は Conscrypt へ `ConscryptNetworkSecurityPolicy` を渡す。
- `XmlConfigSource` は `certificateTransparency` 要素により Network Security Config 側の明示設定を builder に反映する。

## 適用条件

公式文書と AOSP 根拠から、Android 17 以上、targetSdkVersion 37 以上、platform の TLS / HTTPS 証明書検証を使う通信に適用される条件付き変更と分類する。

### OS アップデート時の挙動（OS Update Behavior）

- Android 17 にアップデートしただけで適用されるか: いいえ。targetSdkVersion 36 では compat change がデフォルト有効ではない。
- targetSdkVersion に依存しない根拠: なし。AOSP は `@EnabledAfter(BAKLAVA)` を使う。
- Android 16 以前での挙動: 公式文書上、CT は利用可能だがアプリ側の opt-in が必要。AOSP でも Android 17 タグでデフォルト有効化ゲートが追加されている。

### targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- targetSdkVersion 37 以上で適用されるか: はい。`DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY` が `@EnabledAfter(BAKLAVA)` でデフォルト有効。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: Android 17 platform の `frameworks-base` 実装に依存する。Android 16 platform では公式文書上 opt-in。
- opt-out / 一時 override の有無: compat change としてテスト時に切り替え可能。Network Security Config の CT 設定により明示的な設定が可能。

### その他の条件（Other Conditions）

- 端末 / フォーム ファクタ: 公式抜粋では条件なし。
- 権限: 公式抜粋では条件なし。通常のネットワーク通信では `INTERNET` permission が関係するが、CT policy 自体のゲートかは未確認。
- API 利用: platform trust manager、Network Security Config、HTTPS / TLS、証明書チェーン検証。
- manifest 属性: `android:networkSecurityConfig` が関係する可能性がある。
- コンポーネント境界: アプリ プロセス、Network Security Config parser、TrustManager / Conscrypt、certificate transparency verification、server certificate chain にまたがる。

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
- `frameworks-base` working tree: 調査時点で clean。
- 比較元タグ: `android-16.0.0_r4` が存在する。
- 比較先タグ: `android-17.0.0_r1` が存在する。

根拠上の制約（Evidence limitation）:
- ソース根拠は `android-16.0.0_r4` と `android-17.0.0_r1` の明示的なタグ比較、および `android-17.0.0_r1` 上のシンボル確認に限定した。
- `frameworks-base` working tree は clean のため、ローカル作業ツリーの変更を platform 根拠として誤採用するリスクは確認されていない。

## 関連ファイル（Related Files）

- `packages/NetworkSecurityConfig/platform/src/android/security/net/config/NetworkSecurityConfig.java`
- `packages/NetworkSecurityConfig/platform/src/android/security/net/config/NetworkSecurityTrustManager.java`
- `packages/NetworkSecurityConfig/platform/src/android/security/net/config/RootTrustManager.java`
- `packages/NetworkSecurityConfig/platform/src/android/security/net/config/XmlConfigSource.java`
- `packages/NetworkSecurityConfig/platform/src/android/security/net/config/CertificatesEntryRef.java`
- `packages/NetworkSecurityConfig/platform/src/android/security/net/config/SystemCertificateSource.java`

注記:
- `android-17.0.0_r1`の`frameworks-base`ではNetwork Security Config、API surface、compat framework定義まで確認済みである。実際のCT verification implementationを担うConscryptなど別projectの内部は本調査の検索範囲外であり、追加evidence対象として残る。

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル | Android 16 の基準挙動 | Android 17 の挙動 | 関連性 |
| --- | --- | --- | --- |
| `NetworkSecurityConfig.DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY` | CT デフォルト有効化の targetSdkVersion 37 ゲートは存在しない。 | Change ID `407952621L` が追加され、`@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)` で targetSdkVersion 37 以上はデフォルト有効。 | 公式文書の targetSdkVersion 37 条件を直接裏付けるゲート。 |
| `NetworkSecurityConfig.certificateTransparencyVerificationRequiredDefault()` | CT は明示設定に依存する。 | `certificateTransparencyDefaultEnabled()` と `CompatChanges.isChangeEnabled(DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY)` によりデフォルト状態を決める。 | Android 17 / targetSdkVersion 37 で opt-in からデフォルト有効へ変わる実装。 |
| `NetworkSecurityConfig.Builder.mCertificateTransparencyVerificationRequired` | デフォルトは CT opt-in ではない。 | builder のデフォルト値に `certificateTransparencyVerificationRequiredDefault()` を使う。 | Network Security Config のデフォルト ポリシーに CT ゲートが反映される箇所。 |
| `RootTrustManager.getNetworkSecurityPolicy()` / `NetworkSecurityTrustManager.setNetworkSecurityPolicy()` | Conscrypt へ CT policy を渡すデフォルト コードパスは限定的。 | `ConscryptNetworkSecurityPolicy` を TrustManager に渡すコードパスが追加される。 | platform TLS certificate validation へ Network Security Config policy が接続される根拠。 |
| `XmlConfigSource.parseCertificateTransparency()` | app opt-in の CT 設定を parse する。 | CT 要素の明示設定は引き続き builder に反映され、デフォルト有効化への opt-out / override path になる。 | デフォルト有効化だけでなく Network Security Config による明示制御が可能であることの根拠。 |

必要な context:
- Entry point / caller: アプリの platform TLS / HTTPS 接続 -> `RootTrustManager` / `NetworkSecurityTrustManager` -> Conscrypt certificate validation。
- 関連 class / service の責務: `NetworkSecurityConfig` はアプリ / domain ごとの network security policy を保持し、`RootTrustManager` は hostname に応じた設定を選ぶ。
- app API / system event から変更箇所までの runtime path: アプリ TLS handshake -> hostname-aware trust manager -> `NetworkSecurityConfig` -> `ConscryptNetworkSecurityPolicy` -> CT verification policy。
- 関係しないコードパスを除外した理由: `ManifestConfigSource.DEPRECATE_USES_CLEARTEXT_TRAFFIC` は同じ Network Security Config 周辺の別 Change ID であり、CT デフォルト有効化とは別変更として除外した。

## 差分解釈（Diff Interpretation）

| 観測した差分 | 解釈 | Behavior Change との関連 | 信頼度 |
| --- | --- | --- | --- |
| `DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY = 407952621L` が `@EnabledAfter(BAKLAVA)` で定義される。 | 条件変更 / ゲート | targetSdkVersion 37 以上で CT がデフォルト有効になる直接根拠。 | High |
| `certificateTransparencyVerificationRequiredDefault()` が compat change を確認する。 | デフォルト変更 | Android 16 opt-in から Android 17 / targetSdkVersion 37 デフォルト有効へ変わる実装。 | High |
| `ConscryptNetworkSecurityPolicy` を TrustManager に渡すコードパスが追加される。 | 挙動追加 | CT policy が platform TLS certificate validation に接続される根拠。 | High |
| `XmlConfigSource` が CT 設定を builder に反映する。 | 明示 override 経路 | Network Security Config による明示設定がデフォルト ポリシーを調整できることを示す。 | Medium |

必要な解釈:
- Added behavior: CT デフォルト ポリシーを Conscrypt policy に接続するコードパス。
- Removed behavior: public API の削除は確認していない。
- Changed condition / gate: targetSdkVersion 37 以上で CT がデフォルト有効。
- Changed default: targetSdkVersion 37 以上では CT が opt-in ではなくデフォルト有効。
- No behavior change found: 該当しない。

## 事実（Evidence）

事実:
- 公式 Behavior Change 文書は、targetSdkVersion 37 以上のアプリで certificate transparency (CT) が default で enabled になると述べている。
- 公式文書は、Android 16 では CT は利用可能だが、アプリが opt-in する必要があったと述べている。
- 公式文書は、Network Security Config の CT summary と CT 設定に関する documentation を参照している。
- local `frameworks-base` には `android-16.0.0_r4` タグがある。
- local `frameworks-base` には `android-17.0.0_r1` タグがある。
- 調査時点で `frameworks-base` working tree は clean。
- AOSP では `DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY = 407952621L` が `@EnabledAfter(BAKLAVA)` として定義される。
- AOSP では CT のデフォルト有効化が compat change と Conscrypt flag の両方を満たす場合に有効になる。

観察:
- 公式ページ種別は targetSdkVersion 37 以上向けである。
- 原文は `If an app targets Android 17 (API level 37) or higher` と明示しており、targetSdkVersion 37 ゲートがある可能性が高い。
- この項目は targetSdkVersion 37 条件に加えて、TLS / HTTPS 証明書検証、CT 対応証明書、Network Security Config の設定という実行時 / 配備条件を含む。
- Android 16 で opt-in だったものが Android 17 / targetSdkVersion 37 でデフォルト有効になるため、source diff type は changed default と判断できる。
- AOSP ゲートは targetSdkVersion 37 以上でデフォルト有効であり、公式文書と一致する。
- `certificateTransparencyDefaultEnabled()` の platform flag が false の環境ではデフォルト有効化コードパスが抑止されるため、実端末では platform flag / module state も確認対象になる。

仮説:
- Android 17 / targetSdkVersion 37 以上では、Network Security Config で明示 opt-in していないアプリでも、platform TLS validation に CT policy が適用される可能性が高い。
- Android 17 / targetSdkVersion 36 のアプリでは compat change がデフォルト無効のため、Android 16 と同様に opt-in が必要。
- CT に対応していない公開証明書チェーン、検証環境、独自 CA / private PKI を使う通信では、接続失敗または証明書検証エラーが起きる可能性がある。

結論:
- 公式文書と AOSP 根拠が一致するため、primary classification は `TARGET_SDK_37_CONDITIONAL` とする。
- Android 17 / targetSdkVersion 37 以上で platform TLS / HTTPS 証明書検証を使う場合、CT がデフォルト有効になる。

## 適用ゲート根拠（Applicability Gate Evidence）

- targetSdkVersion ゲート: `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)`。targetSdkVersion 37 以上でデフォルト有効。
- CompatChanges.isChangeEnabled / ChangeId: `CompatChanges.isChangeEnabled(DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY)`、Change ID `407952621L`。
- @EnabledAfter / @EnabledSince / デフォルト状態: `@EnabledAfter(BAKLAVA)`。targetSdkVersion 36 ではデフォルト無効、37 以上ではデフォルト有効。
- Build.VERSION / SDK_INT ゲート: Android 17 platform 実装として扱う。明示的な SDK_INT 実行時ゲートは主根拠ではない。
- DeviceConfig / resources config: `certificateTransparencyDefaultEnabled()` の platform flag が CT デフォルト有効化コードパスの追加条件。
- Permission/AppOps ゲート: なし。
- Manifest/property ゲート: Network Security Config の certificate transparency 設定により明示 opt-in / opt-out できる。
- No gate found: 該当しない。
- ゲート結論: Android 17 上で targetSdkVersion 37 以上、かつ platform TLS / HTTPS certificate validation を使う通信に CT デフォルト ポリシーが適用される。
- ソース文脈からの推論: TrustManager が hostname に応じた `NetworkSecurityConfig` を取得し、Conscrypt policy として CT 設定を渡す。

---

# 影響分析

## 影響を受けるアプリ（Affected Apps）

影響を受ける可能性があるアプリ:
- targetSdkVersion 37 へ更新し、platform TLS / HTTPS 通信を行うアプリ。
- CT に対応していない証明書チェーンを使う backend に接続するアプリ。
- 検証環境、社内環境、private PKI、独自 CA、証明書 pinning と CT policy の組み合わせを持つアプリ。
- Network Security Config で CT に明示 opt-in していなかったが、Android 17 でデフォルト有効化の対象になるアプリ。

## 影響を受けないアプリ（Non-Affected Apps）

影響が限定的または対象外と考えられるケース:
- ネットワーク通信を行わないアプリ。
- platform TLS / HTTPS 証明書検証を使わない通信だけを行うアプリ。ただし独自 TLS stack の扱いは別途確認が必要。
- すべての接続先証明書チェーンが CT 要件を満たしているアプリ。
- Android 16 ですでに CT に opt in しており、接続先が検証済みのアプリ。
- Network Security Config で対象外または opt-out として明示設定されているケース。

---

# 顧客影響

## 影響度

- 人間による判断が必要

※ 最終 severity / priority は人間が判断する。このレポートでは確定しない。

## ビジネス影響

- ユーザー影響: CT 要件を満たさない証明書を使う endpoint への接続が失敗すると、ログイン、API 通信、決済、コンテンツ取得などが利用できなくなる可能性がある。
- 運用影響: backend 証明書の発行元、CT log inclusion、検証環境 / staging 環境の証明書運用を確認する必要がある可能性がある。
- 開発影響: Network Security Config、証明書 pinning、debug / staging 設定、targetSdkVersion 37 テストを見直す必要がある可能性がある。

---

# サービス影響例

このセクションは、公式文書と AOSP 根拠から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: Stripe / PayPal / Firebase Auth と並行して使う自社 HTTPS API

- 具体サービス例: Stripe / PayPal 決済、Firebase Auth ログイン、Cloudflare / Fastly 配下の自社 API を同じアプリから呼び出す構成。
- 影響を受ける実装パターン: CT 要件を満たさない公開証明書チェーンを使う endpoint に platform TLS で接続する実装。
- 発生条件: Android 17 / targetSdkVersion 37 で CT がデフォルト有効になり、証明書チェーンが CT policy を満たさない場合。
- ユーザーに見える症状: API 通信失敗、ログイン不能、決済失敗、コンテンツ取得失敗の可能性。
- 技術的に起きていること: platform TLS の certificate transparency policy が default enabled になり、対象 host の公開証明書チェーンが CT 要件を満たさないと handshake が失敗する。
- 開発・運用への影響: 証明書発行、CT log inclusion、証明書更新手順の確認が必要になる可能性。
- 推奨対応候補: 接続先証明書の CT 対応を棚卸しし、Android 16 opt-in または Android 17 環境で事前検証する。
- 根拠: 公式 statement とレポートの期待挙動。
- 信頼度: Medium
- 注意: Stripe / PayPal / Firebase Auth で発生確認した事実ではない。実際のリスクは、アプリが接続する各 host の証明書と Network Security Config に依存する。

## 例2（Example 2）: Okta / Microsoft Entra ID 連携アプリの staging / private PKI 環境

- 具体サービス例: Okta / Microsoft Entra ID で認証し、その後に private CA の staging API や社内 API へ接続する業務アプリ。
- 影響を受ける実装パターン: public CT log に載らない証明書や private trust anchor を使う接続。
- 発生条件: Android 17 / targetSdkVersion 37 で CT デフォルト ポリシーが staging endpoint にも適用される場合。
- ユーザーに見える症状: 社内検証や beta build でだけ通信失敗する可能性。
- 技術的に起きていること: production IdP への接続は成功しても、アプリ固有の staging / private endpoint で CT policy または Network Security Config の扱いが異なり接続に失敗する。
- 開発・運用への影響: Network Security Config、debug overrides、private PKI 例外条件の確認が必要になる可能性。
- 推奨対応候補: staging証明書運用を見直し、公式CT policyと必要に応じたConscrypt側evidenceから対象外条件を確認する。
- 根拠: 公式 statement、AOSP の CT デフォルト ゲート、Network Security Config の CT policy path。
- 信頼度: Medium
- 注意: Okta / Microsoft Entra ID で発生確認した事実ではない。private CA / user-added CA / debug override の扱いは Network Security Config と証明書設定ごとの確認が必要。

---

# 対応候補（Required Actions）

## 必須対応（Must）

- アプリの HTTPS / TLS 接続先を棚卸しし、公開証明書チェーンが CT 要件を満たしているか確認する。
- Android 16 で CT に opt-in していないアプリは、Android 17 / targetSdkVersion 37 でデフォルト有効になった場合の接続テストを行う。
- Network Security Config の CT 関連設定、debug-overrides、domain-config、certificate pinning の組み合わせを確認する。
- targetSdkVersion 37 更新前に、デフォルト CT policy と Network Security Config の明示設定を組み合わせて接続テストを行う。

## 推奨対応（Recommended）

- staging / QA / internal API endpoint も含め、証明書発行と CT log inclusion の運用を backend / infra owner と確認する。
- CT 検証失敗時のエラーログ、メトリクス、ユーザー向け fallback を整備する。
- Android 16 の opt-in 設定で事前に CT を有効化し、接続先の互換性を早期検証する。

## 任意対応（Optional）

- 証明書 pinning を利用している場合、pin 更新手順と CT policy の関係を security review で確認する。
- 独自 TrustManager / TLS stack を使う箇所があれば、platform CT policy の適用有無を別途整理する。

---

# 検証方法（Verification Method）

## 検証マトリクス（Matrix）

| 端末 OS | targetSdkVersion | Compat flag | 期待される挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | default | 公式文書上、CT は利用可能だがアプリの opt-in が必要。 |
| Android 17 | 36 | default | `DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY` はデフォルト無効。CT は明示 opt-in が必要。 |
| Android 17 | 37 | default | 公式文書上、CT がデフォルト有効。CT 要件を満たさない証明書チェーンでは接続影響の可能性。 |
| Android 17 | 36 | force-enabled | `DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY` を有効化すると CT デフォルト有効化コードパスを検証できる。 |
| Android 17 | 37 | force-disabled | `DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY` を無効化すると CT デフォルト有効化コードパスとの切り分けができる。 |

## 手順（Steps）

- targetSdk 変更: targetSdkVersion 36 と 37 の test build を用意する。
- compat framework command: `adb am compat enable|disable DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY <package>`、または Change ID `407952621` を使って切り替える。
- テスト方法: CT 対応証明書、CT 非対応証明書、staging / private PKI endpoint、Network Security Config の CT 設定あり / なしを分けて HTTPS 接続を確認する。
- 再現手順: Android 17 device / emulator で対象アプリを install し、targetSdkVersion 36 / 37 の両方で同一 endpoint へ接続する。必要に応じて Android 16 opt-in 設定でも比較する。
- 期待結果: targetSdkVersion 37 のアプリでは CT がデフォルト有効になり、CT policy を満たさない証明書チェーンで TLS validation failure が起きる可能性がある。targetSdkVersion 36 ではデフォルトで旧 opt-in path が維持される。

---

# 結論（Conclusion）

AOSP では `DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY = 407952621L` が `@EnabledAfter(BAKLAVA)` として定義され、`certificateTransparencyVerificationRequiredDefault()` がこの compat change を見て CT のデフォルト状態を決めることを確認した。HTTPS 接続先の証明書が CT 要件を満たしていない場合、targetSdkVersion 37 更新後に通信互換性リスクがある。

primary classification は `TARGET_SDK_37_CONDITIONAL`、confidence は High とする。

---

# 人間の判断欄

最終優先度（Final Priority）:
- 人間による判断が必要

最終影響度:
- 人間による判断が必要

リリース判断:
- 人間による判断が必要

顧客連絡の優先度:
- 人間による判断が必要

判断（Decision）:
- 人間による判断が必要

判断メモ:
- targetSdkVersion 37 対応時に、証明書 / CT 対応確認をどの優先度で顧客へ案内するかを判断する。

---

# 参照（References）

## ドキュメント（Documentation）

- https://developer.android.com/about/versions/17/behavior-changes-17
- https://developer.android.com/privacy-and-security/security-config#CertificateTransparencySummary
- https://developer.android.com/privacy-and-security/security-config#certificateTransparency

## AOSP

- 確認済みの比較元 tag: `android-16.0.0_r4`
- 確認済みの比較先 tag: `android-17.0.0_r1`

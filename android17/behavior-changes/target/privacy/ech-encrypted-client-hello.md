# ECH (Encrypted Client Hello) 有効

## 基本情報

### 調査対象 Android バージョン

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP タグ

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

### Behavior Change 文書

Document:
https://developer.android.com/about/versions/17/behavior-changes-17

Related documents:
- https://developer.android.com/privacy-and-security/security-config#domainEncryption
- https://developer.android.com/privacy-and-security/security-config#EncryptedClientHelloSummary
- https://www.rfc-エディタ.org/rfc/rfc9849.html#name-grease-ech

Section:
ECH (Encrypted Client Hello) enabled

Page type:
- Apps targeting Android 17 or higher

### 分類スナップショット

主分類（Primary classification）:
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- 公式 Behavior Change 文書は、targetSdkVersion 37 以上のアプリでは TLS 接続に ECH が使われると説明している。
- ただし ECH が実際に有効になるには、アプリが使う networking library が ECH を統合していること、remote server が ECH protocol をサポートしていることが必要。
- ネットワークセキュリティ設定の `<domainEncryption>` により、global または per-domain で ECH mode を `"enabled"` / `"disabled"` に設定できる。
- ローカルの `frameworks-base` に Android 17 AOSP タグがないため、AOSP 適用ゲート、ネットワークセキュリティ設定 parser diff、Compat Change ID、デフォルト状態は未検証である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

早見表:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 未確認 | 公式ページは targetSdkVersion 37+ 向け。AOSP 適用ゲートは未確認。 |
| targetSdkVersion 37 以上が必要か | 可能性は高いが未確認 | 公式文書とネットワークセキュリティ設定 docs は API 37+ のデフォルトで有効を示す。AOSP 根拠は未取得。 |
| 追加の実行時条件があるか | Yes | networking library ECH support、remote server ECH support、TLS 接続、`<domainEncryption>` mode が条件。 |
| Compat Change ID が関係するか | 未確認 | Android 17 タグと Compat framework 根拠が未確認。 |

### 調査日

2026-06-10

### 信頼度

- 低

### 適用条件分類

適用される条件（Applies when）:
- [ ] Android 17 上の全アプリ（targetSdkVersion に依存しない）
- [ ] Android 17 以上で targetSdkVersion >= 37
- [ ] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play システムアップデート dependent
- [ ] API addition only, not a behavior change
- [x] 未確認 / 追加根拠が必要

必要な実行時条件（必要な実行時条件）:
- Android バージョン: Android 17 以上が前提と考えられるが、AOSP タグは未取得。
- targetSdkVersion: 公式文書上は 37 以上。
- 端末/フォームファクター: 公式抜粋では条件なし。
- 権限/API/コンポーネント条件: TLS 接続、ECH 対応 networking library、ECH 対応 server、ネットワークセキュリティ設定の `<domainEncryption>` mode。
- アプリ状態/プロセス条件: remote endpoint への TLS handshake 実行時。

Compat framework:
- 変更 ID: 未確認
- 変更 name: 未確認
- デフォルト状態: 未確認
- テスト時の切り替え可否: 未確認

分類信頼度:
- 低

分類根拠:
- Official documentation page: `behavior-changes-17`
- 検証対象の適用条件文: targetSdkVersion 37 以上のアプリでは TLS 接続に ECH が使われる。
- AOSP targetSdk 適用ゲート: 未確認。ローカルの `frameworks-base` に `android-17*` タグがない。
- Compat framework エントリ: 未確認。Android 17 Compat framework 根拠が未取得。

---

# エグゼクティブサマリー

Android 17 では、targetSdkVersion 37 以上のアプリに対して Encrypted Client Hello (ECH) の platform support が導入される、と公式文書は説明している。ECH は TLS handshake の Server Name Indication (SNI) を暗号化し、ネットワーク観測者が接続先ドメインを特定しにくくするための privacy 機能である。

実際に ECH が使われるには、アプリが使う networking library が ECH に対応し、接続先 server も ECH をサポートしている必要がある。ECH を negotiated できない場合は ECH GREASE が送信される。また、Android 17 ではネットワークセキュリティ設定に `<domainEncryption>` が追加され、global または per-domain で ECH を有効 / 無効にできる。

ただし、現時点のローカルの `frameworks-base` には Android 17 AOSP タグがないため、実装差分、targetSdkVersion 適用ゲート、Compat Change ID、デフォルト状態は未確認である。

---

# 公式ドキュメント確認

## 原文（Statement）

Page title:
- Behavior changes: Apps targeting Android 17 or higher

Page URL:
- https://developer.android.com/about/versions/17/behavior-changes-17

Page type:
- Android 17 を対象とするアプリ

Section title:
- ECH (Encrypted Client Hello) enabled

検証対象の原文:

> TLS 接続で ECH が使われる

提供された公式文書の抜粋は、Android 17 / API level 37 以上を対象とするアプリでは TLS 接続に ECH が使われると説明している。また、ECH はアプリのネットワークライブラリとリモートサーバーの両方が ECH をサポートする場合にのみ有効になり、ネゴシエーションに失敗した場合は ECH GREASE になり、`<domainEncryption>` によって全体またはドメイン単位で挙動を調整できると説明している。

## 解釈

この変更は、targetSdkVersion 37 以上のアプリにおける TLS 接続の privacy 挙動を変更する。従来の TLS handshake では SNI により接続先ドメインが観測され得るが、ECH は SNI を含む ClientHello の機微情報を暗号化し、接続先ドメインの露出を減らす。

ただし、アプリ単体の targetSdkVersion だけで必ず ECH が negotiated されるわけではない。networking library、server support、DNS / ECH configuration、ネットワークセキュリティ設定の `<domainEncryption>` mode が実際の挙動を左右する。

---

# 変更内容

公式文書上の変更点:
- Android 17 は ECH の platform support を導入する。
- targetSdkVersion 37 以上のアプリでは TLS 接続に ECH が使われる。
- ECH は networking library が ECH support を統合し、remote server も ECH protocol をサポートしている場合に active になる。
- ECH を negotiated できない場合、client は randomized contents を持つ ECH extension、つまり ECH GREASE を送る。
- Android 17 はネットワークセキュリティ設定に `<domainEncryption>` element を追加する。
- `<domainEncryption>` は `<base-config>` または `<domain-config>` 内で使え、global または per-domain に ECH mode を `"enabled"` / `"disabled"` へ設定できる。
- ネットワークセキュリティ設定 docs は、`<domainEncryption>` のデフォルト mode が targetSdkVersion 37 以上では `"enabled"`、それ以外では `"disabled"` と説明している。

AOSP で未確認の点:
- Android 16 基準挙動で ECH / `<domainEncryption>` が存在しなかったこと。
- Android 17 で追加されたネットワークセキュリティ設定 parser / ポリシーの diff。
- targetSdkVersion 37 適用ゲートの実装箇所。
- ECH mode デフォルト `"enabled"` / `"disabled"` の実装。
- HttpEngine、WebView、OkHttp など library integration との接続点。
- Compat Change ID とデフォルト状態。

## 適用条件（Applicability）

公式文書の一次判断では、Android 17 以上、targetSdkVersion 37 以上、TLS 接続、ECH 対応 networking library、ECH 対応 server、`<domainEncryption>` mode が条件となる。AOSP タグが未取得のため、確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

### OS アップデート時の挙動

- Android 17 にアップデートしただけで適用されるか: 未確認
- targetSdkVersion に依存しない根拠: なし。公式文書は targetSdkVersion 37 以上を明示している。
- Android 16 以前での挙動: ネットワークセキュリティ設定 docs は Android 16 以下では ECH は利用可能ではないと説明しているが、AOSP タグ比較は未実施。

### targetSdkVersion 37 以上での挙動

- targetSdkVersion 37 以上で適用されるか: 公式文書上は Yes と読めるが、AOSP 適用ゲートは未確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: 未確認。公式文書とネットワークセキュリティ設定 docs は Android 17 / API level 37 以上の機能として説明している。
- opt-out / temporary override の有無: `<domainEncryption mode="disabled"/>` による opt-out が公式 docs で説明されている。Compat framework による force enable / disable は未確認。

### その他の条件

- 端末/フォームファクター: 公式抜粋では条件なし。
- 権限: 公式抜粋では条件なし。
- API 使用: TLS 接続を行う networking library。例として HttpEngine、WebView、OkHttp が挙げられている。
- manifest attribute: ネットワークセキュリティ設定 file の指定が関係する可能性がある。
- コンポーネント境界: platform ネットワークセキュリティ設定、networking library、remote server の三者にまたがる。

---

# AOSP 調査

## checkout 状態

根拠利用前に確認したコマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list 'android-17*'
```

Result:
- `frameworks-base` 作業ツリー: 調査時点で clean。
- From タグ: `android-16.0.0_r4` exists.
- To タグ: ローカルに `android-17*` タグなし。

根拠上の制約:
- Android 17 AOSP タグがローカルの `frameworks-base` に存在しないため、`git -C frameworks-base diff android-16.0.0_r4 <android-17-tag> -- ...` による明示的なタグ比較を実行できない。
- Repository rule に従い、Android 17 作業ツリーや推測によるソース根拠は採用しない。
- この制約により、AOSP-backed 結論は高信頼度にできない。

## 関連ファイル

未確認。Android 17 AOSP タグ取得後に、少なくとも以下の候補をタグ比較で確認する必要がある。

- `core/java/android/security/net/config/NetworkSecurityConfig.java`
- `core/java/android/security/net/config/XmlConfigSource.java`
- `core/java/android/security/net/config/ConfigSource.java`
- `core/java/android/security/net/config/ApplicationConfig.java`
- `core/java/android/security/NetworkSecurityPolicy.java`
- API surface files for ネットワークセキュリティ設定 / policy exposure, 該当する場合
- Compat framework 定義ファイル内の ECH / domain encryption / ネットワークセキュリティ設定関連 Change ID

Note:
- 実際の ECH handshake implementation は networking library や TLS stack 側にある可能性がある。今回の mission は `frameworks-base` 根拠に限定されているため、library / TLS stack 側は Android 17 タグ公開後の追加調査対象として扱う。

## 確認したソース文脈

Android 17 AOSP タグがないため、ソース文脈は未レビュー。

| ファイル / シンボル | Android 16 基準挙動 | Android 17 挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| 未レビュー | 未レビュー | 未レビュー | Android 17 タグがないため、公式文書の記述を AOSP 差分で検証できない。 |

必須記入項目:
- 入口 / 呼び出し元: 未確認。想定される入口はアプリ TLS 接続、ネットワークセキュリティ設定 parsing、networking library の TLS handshake setup だが、AOSP 根拠としては未採用。
- Relevant class or service responsibility: 未確認。
- アプリ API またはシステムイベントから変更箇所までの実行時パス: 未確認。
- 除外した無関係なコードパス: Android 17 タグ不在のため、ソースパスの採否判断自体を保留。

## 差分解釈

| 確認した差分 | 解釈 | 挙動変更 との関係 | 信頼度 |
| --- | --- | --- | --- |
| Android 17 タグ間差分は利用不可 | ソース差分の種別はまだ分類できない | 公式文書の ECH デフォルト挙動と `<domainEncryption>` 追加をソース差分で裏取りできていない | 低 |

必須分類:
- Added behavior: 未確認。
- Removed behavior: 未確認。
- Changed condition / gate: 未確認。
- Changed default: 未確認。
- No behavior change found: 未確認。タグ不在のため「no behavior change」とは判断しない。

## 事実

事実:
- 公式 Behavior Change 文書は、Android 17 が ECH platform support を導入すると述べている。
- 公式文書は、targetSdkVersion 37 以上のアプリでは TLS 接続に ECH が使われると述べている。
- 公式文書は、ECH が active になるには networking library と remote server の ECH support が必要と述べている。
- 公式文書は、ECH を negotiated できない場合に ECH GREASE が送信されると述べている。
- 公式文書は、ネットワークセキュリティ設定に `<domainEncryption>` が追加され、`<base-config>` / `<domain-config>` 内で ECH mode を指定できると述べている。
- ネットワークセキュリティ設定 docs は、`<domainEncryption>` のデフォルト mode が API level 37 以上で `"enabled"`、それ以外で `"disabled"` と説明している。
- RFC 9849 は、ECH を実装する client が実 ECH extension または GREASE ECH extension を送る client behavior を定義している。
- ローカルの `frameworks-base` には `android-16.0.0_r4` タグがある。
- ローカルの `frameworks-base` には `android-17*` タグがない。
- 調査時点で `frameworks-base` 作業ツリーは clean。

観察:
- 公式ページ種別は targetSdkVersion 37 以上向けである。
- この項目は privacy 挙動変更とネットワークセキュリティ設定の新要素追加の両方を含む。
- 実際の ECH negotiated 挙動は、アプリ targetSdkVersion だけでなく networking library と server support に依存する。
- `<domainEncryption mode="disabled"/>` により opt-out できる。
- AOSP タグがないため、実装が本当に targetSdkVersion 37 適用ゲートで制御されているかは未確認。
- Compat framework エントリの有無も未確認。

仮説:
- Android 17 / targetSdkVersion 37 以上では、ネットワークセキュリティ設定のデフォルト domain encryption mode が有効になり、ECH 対応 library が TLS handshake 時に ECH または ECH GREASE を送る可能性が高い。
- targetSdkVersion 36 のアプリではデフォルト mode が無効の可能性が高いが、AOSP 適用ゲート未確認のため断定しない。
- 一部の enterprise network、TLS inspection、domain-based filtering、allowlist / blocklist 運用では、SNI visibility 低下または GREASE extension により観測・制御の前提が変わる可能性がある。

結論:
- 現時点で顧客向けに確定できるのは、「公式文書上は Android 17 / targetSdkVersion 37 以上で ECH がデフォルトで有効になり、library / server support と `<domainEncryption>` 設定に依存する」という範囲まで。
- AOSP 適用ゲート、ネットワークセキュリティ設定 parser diff、Compat framework デフォルト状態が未確認のため、主分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

## 適用ゲート根拠

- targetSdkVersion 適用ゲート: 未確認。Android 17 AOSP タグがないため、`targetSdkVersion` / `ApplicationInfo.targetSdkVersion` 検索は実施していない。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。Android 17 AOSP タグがないため、`CompatChanges.isChangeEnabled` / `@ChangeId` / `@EnabledAfter` / `@EnabledSince` 検索は実施していない。
- @EnabledAfter / @EnabledSince / デフォルト状態: 未確認。
- Build.VERSION / SDK_INT 適用ゲート: 未確認。
- DeviceConfig / resources 設定: 未確認。
- 権限/AppOps 適用ゲート: 公式文書上は権限条件なし。AOSP 未確認。
- Manifest/property 適用ゲート: ネットワークセキュリティ設定の `<domainEncryption>` mode が関係する。manifest で network security 設定 file を指定する構成は未確認。
- 適用ゲート未検出: 未判断。検索不能のため「適用ゲートなし」とは扱わない。
- 適用ゲートの結論: 未確認。公式文書上の Android 17 / targetSdkVersion 37 / library support / server support / 設定条件はあるが、AOSP 根拠が不足している。
- ソース文脈からの推論: ソース文脈未取得のため不可。

Searched:
- `frameworks-base` checkout 状態。
- `android-16.0.0_r4` タグの存在。
- `android-17*` タグの存在。

Not searched yet:
- Android 17 implementation files.
- Android 17 Compat framework definitions.
- Android 17 API surface files.
- networking library / TLS stack integration points.

理由:
- Android 17 target タグがローカル checkout に存在しないため、タグ間差分による platform 根拠が作れない。

---

# 影響分析

## 影響を受けるアプリ

影響を受ける可能性があるアプリ:
- targetSdkVersion 37 以上への更新を予定しているアプリ。
- HTTPS / TLS 接続を行い、ECH 対応 networking library を使うアプリ。
- HttpEngine、WebView、OkHttp などの ECH 対応版を使うアプリ。
- 接続先 server が ECH をサポートしているアプリ。
- ネットワークセキュリティ設定を使い、domain ごとに通信ポリシーを制御しているアプリ。
- enterprise network、TLS inspection、SNI ベースの allowlist / blocklist、通信監視環境で動作するアプリ。

## 影響を受けにくいアプリ

影響が限定的と考えられるケース:
- TLS 接続を行わないアプリ。
- ECH 非対応 networking library のみを使うアプリ。
- 接続先 server が ECH をサポートせず、かつ ECH GREASE も無効にしている構成。
- `<domainEncryption mode="disabled"/>` で対象 domain の ECH / ECH GREASE を無効化している構成。
- targetSdkVersion 37 へ上げないアプリ。ただし、これは公式文書からの一次判断であり、AOSP 適用ゲートは未確認。

---

# 顧客影響

## 影響度

- Human decision required

※ 最終 severity / priority は人間が判断する。このレポートでは確定しない。

## ビジネス影響

- ユーザー影響: SNI が暗号化されることで、ユーザーの接続先ドメインがネットワーク観測者に見えにくくなり privacy が向上する可能性がある。
- 運用影響: SNI を前提とする enterprise proxy、TLS inspection、domain filtering、traffic 監視では、接続判定や可観測性の前提が変わる可能性がある。
- 開発影響: targetSdkVersion 37 更新前に、利用 networking library の ECH 対応状況、server support、ネットワークセキュリティ設定の `<domainEncryption>` ポリシーを確認する必要がある。

---

# サービス影響例

このセクションは、公式文書と AOSP 根拠から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1: 企業ネットワーク / TLS inspection 環境の業務アプリ

- 対象サービス例: 社内 SaaS、MDM 管理端末、社内 proxy 経由の業務アプリ。
- 影響を受ける実装パターン: ClientHello / SNI を network appliance が観測する前提の TLS inspection / routing / ポリシー適用。
- 発生条件: Android 17 で ECH が有効になり、network appliance が期待する hostname visibility が変わる場合。
- ユーザーに見える症状: 社内ネットワークで接続失敗、proxy ポリシー mismatch、特定 endpoint だけ接続できない可能性。
- 開発・運用への影響: network team と ECH 対応、DNS / HTTPS RR、proxy ポリシーの確認が必要になる可能性。
- 推奨対応候補: ECH 詳細ページと network ポリシーを照合し、検証環境で endpoint 別接続テストを行う。
- 根拠: 公式 Behavior Change 文書の記述と、レポートに記録した未確認の AOSP 根拠。
- 信頼度: 低
- 注意: 実ネットワークでの発生確認ではない。ECH availability は DNS / server / network 条件に依存する可能性がある。

## 例2: 独自ネットワーク診断 / SNI ベース制御を持つアプリ

- 対象サービス例: VPN アプリ、network monitor、security アプリ、開発者 diagnostics tool。
- 影響を受ける実装パターン: TLS handshake metadata や SNI を前提に接続先分類・診断を行う実装。
- 発生条件: platform networking が ECH を使い、外部から見える handshake 情報が変わる場合。
- ユーザーに見える症状: 診断結果が不正確になる、接続先分類が失敗する、ポリシー表示が変わる可能性。
- 開発・運用への影響: ECH 対応のテレメトリ / logging / support documentation 更新が必要になる可能性。
- 推奨対応候補: public hostname 依存を減らし、アプリ layer / explicit 設定による診断へ寄せる。
- 根拠: 公式文書の記述とレポートの targetSdkVersion / 適用ゲート未確認事項。
- 信頼度: 低
- 注意: Android 17 AOSP タグと実通信条件の確認が必要。

---

# 対応候補

## 必須対応（Must）

- アプリが使う networking library が ECH をサポートしているか確認する。
- 接続先 server / CDN / hosting プロバイダー が ECH をサポートしているか確認する。
- enterprise network、TLS inspection、SNI ベース制御が関係する顧客環境があるか確認する。
- targetSdkVersion 37 更新前に Android 17 上で主要 endpoint への TLS 接続テストを行う。

## 推奨対応（Recommended）

- ネットワークセキュリティ設定に `<domainEncryption>` を追加する必要がある domain がないか確認する。
- ECH を許可したい domain と、互換性理由で一時的に disable したい domain を分ける。
- 失敗時のテレメトリを用意し、ECH negotiation 失敗、ECH GREASE、TLS handshake 失敗、HTTP layer 失敗を区別できるようにする。
- WebView / OkHttp / HttpEngine などの library version と Android 17 support note を確認する。

## 任意対応（Optional）

- Android 17 AOSP タグ公開後、`<domainEncryption>` parser / ポリシー diff と Compat Change ID を再調査する。
- packet capture / TLS handshake logging が可能な検証環境で、ECH 有効 / 無効の差分を観測する。

---

# 検証方法

## 検証マトリクス

| 端末 OS | targetSdkVersion | Compat flag | 期待される挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | デフォルト | Android 16 基準挙動。公式 docs では ECH は利用可能ではない。AOSP 基準挙動 diff は未確認。 |
| Android 17 | 36 | デフォルト | 未確認。ネットワークセキュリティ設定 docs は API 37 未満でデフォルト無効と示すが、AOSP 適用ゲートは未確認。 |
| Android 17 | 37 | デフォルト | 公式文書上は ECH が TLS 接続に使われる。library / server support がある場合に active。未 negotiated 時は ECH GREASE。 |
| Android 17 | 36 | force-enabled（利用可能な場合） | 未確認。Compat Change ID 未確認。`<domainEncryption mode="enabled"/>` による設定明示は別途検証対象。 |
| Android 17 | 37 | force-disabled（利用可能な場合） | 未確認。Compat Change ID 未確認。`<domainEncryption mode="disabled"/>` による opt-out は公式 docs 上あり。 |

## 手順

- targetSdkVersion 変更: テストアプリを targetSdkVersion 36 と 37 で build し、Android 17 上で同じ endpoint へ TLS 接続を行う。
- Compat framework コマンド: Change ID 未確認のため未定。Android 17 タグ / compat page 確認後に追加する。
- テスト方法: ECH 対応 server と非対応 server、ECH 対応 networking library と非対応 library、`<domainEncryption mode="enabled"/>` / `"disabled"` を組み合わせる。
- 再現手順: TLS handshake、接続 success / 失敗、server support、network observer 上の SNI visibility、GREASE extension の有無を比較する。
- 期待結果: targetSdkVersion 37 かつ ECH 対応 library / server では ECH が active になる。ECH negotiated 不可の場合は ECH GREASE が送信される。targetSdkVersion 36 の結果は AOSP 適用ゲート確認待ち。

---

# 結論

公式文書は、Android 17 で targetSdkVersion 37 以上のアプリに ECH support が導入され、TLS 接続の SNI 露出を減らすと説明している。実際の効果は、networking library、server support、ネットワークセキュリティ設定の `<domainEncryption>` mode に依存する。

一方で、ローカルの `frameworks-base` に Android 17 AOSP タグがないため、実装差分、targetSdkVersion 適用ゲート、ネットワークセキュリティ設定 parser diff、Compat Change ID、デフォルト状態を検証できていない。現時点の主分類は `UNKNOWN_NEEDS_MORE_EVIDENCE`、信頼度は低とする。

# 人間の判断欄

最終優先度（Final Priority）:
- Human decision required

最終影響度（Final Severity）:
- Human decision required

リリース判断（Release Readiness）:
- Human decision required

顧客通知優先度（Customer Communication Priority）:
- Human decision required

次に必要な人間の判断:
- Android 17 AOSP タグ公開後に再調査するか、公式 documentation ベースの暫定 privacy / networking ガイダンスとして扱うかを判断する。

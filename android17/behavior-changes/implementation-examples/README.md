# Android 17 対応例一覧

このディレクトリは、Android 17 Behavior Changesを実装・設定・テストへ落とすための
companion examplesである。

[Android 17対応例テンプレート](../../templates/implementation-examples-template.md)を使用する。
根拠、適用条件、confidenceは[Behavior Changes一覧](../README.md)と各主レポートを正とする。

## 分冊

| 分冊 | 主な例 |
| --- | --- |
| [Core functionality](core-functionality.md) | memory exit診断、MessageQueue private依存除去、static final mutation移行 |
| [Connectivity and security](connectivity-and-security.md) | autonomous re-pair、RFCOMM EOF、URI grant、BAL、Keystore、native DCL、CP2 |
| [Privacy and media](privacy-and-media.md) | SMS OTP、Local Network Permission、ECH、physical password、background audio |
| [UI, input and device form factors](ui-input-and-device-form-factors.md) | IME再表示、pointer capture、CJKV accessibility、adaptive large screen |

4分冊で、主レポートが存在する23個の親テーマを扱う。
同じ親テーマにall-apps版とtarget 37版があるSMS OTPとbackground audioは、
1つの対応例内でOS update条件とtargetSdkVersion条件を分離する。

## 共通の使い方

1. 各例の`rg`で既存コードを検出する。
2. [Android 16→17挙動比較](../version-comparisons/README.md)で発火条件を確認する。
3. 最小の対象screen / component / endpointへ対応を入れる。
4. Android 16 / target 36、Android 17 / target 36、Android 17 / target 37を分離して試験する。
5. temporary opt-outやcompat overrideを使った場合は削除条件を残す。

## 制約

- サンプルはアプリ固有のerror model、DI、threading、permission UXを省略している。
- API 37のsymbolを参照する例はcompileSdk 37を前提とする。
- AOSP gateが未解決の項目は確定コードではなく検証方針のみ記載する。
- 実機Observedは未実施。
- 主レポート未作成の公式追加項目は、[追加調査待ち一覧](../version-comparisons/latest-documentation-gaps.md)
  で管理し、根拠確認前の対応例は作らない。

## Human Decision

このファイル群では最終priority、severity、release readinessを決定しない。

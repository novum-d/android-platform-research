# Android 17 最新公式一覧 - 追加調査待ち項目

## 位置づけ

2026-07-28時点の
[Android 17 features and changes list](https://developer.android.com/about/versions/17/summary)
とローカルの主レポート一覧を比較し、まだ独立したtraceability reportがない項目を記録する。

このファイルはBehavior Change findingではない。AOSP source context、gate、classification、
summary、Human Decisionが揃うまでは、顧客向け確定結論に使用しない。

## 公式文書上の暫定差分

| 公式項目 | Android 16 baseline | Android 17公式記述 | 暫定確認 | 不足根拠 |
| --- | --- | --- | --- | --- |
| New NPU feature flag | NPU利用に`android.hardware.npu`宣言を必須とするAndroid 17 ruleなし | target 37 appはNPU accessにfeature宣言が必要 | manifest / NPU利用を棚卸し | AOSP gate、failure mode、report / summary |
| Memory restrictions for notification custom views | Android 17のstrict custom-view memory checksなし | target 37でcustom notification viewのmemory checkを強化 | large bitmap / RemoteViewsを検出 | limit値、exception / rejection path、AOSP gate |
| User-agent reduction for WebView |従来のdefault WebView UA | target 37でdefault UAを短縮 | UA parsing / server branchingを検出 | exact format、WebView module / target gate |
| New global keyboard navigation shortcuts | app-specific shortcutがMeta+Back系と競合し得る | Q3からMeta+Back(F1)等をglobal shortcutとして予約 | hardware keyboard shortcutを棚卸し | QPR / build条件、input dispatch AOSP evidence |
| App memory runtime limits | Android 17 MemoryLimiterなし | limit超過時のenforcement / crashを強化 |既存App memory limits reportへ統合候補 | 独立項目かsubsectionか、source / gate差分 |
| Restricted message access | E2EE messageへの一般的なAndroid 17制限なし |多くのappがend-to-end encrypted messageへaccess不可 | SMS OTP reportとの境界を確認 |対象provider / role / exemption / AOSP path |

## 調査順

1. 公式detail pageとoriginal statementを保存する。
2. `android-16.0.0_r4` / `android-17.0.0_r1`でsource contextを比較する。
3. OS updateとtargetSdkVersion 37 gateを分離する。
4. Compat Change ID、feature flag、module / QPR条件を確認する。
5. customer reportとone-page summaryを作成する。
6. 該当分冊へAndroid 16→17比較を追加する。

## Observed / Human Decision

- Observed: 未実施
- Confidence: 未評価
- Human Decision: 未決定

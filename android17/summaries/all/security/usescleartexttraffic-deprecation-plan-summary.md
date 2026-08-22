# usesCleartextTraffic の deprecation plan - 1ページ要約

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
- OS アップデート / 全アプリ（OS update / all apps）: 無条件の即時 runtime change ではない。公式文書は future release の deprecation plan と説明。
- targetSdkVersion 37 以上: 意図としては該当候補。AOSP の feature flag description は targetSdk C+ で `usesCleartextTraffic` を無視すると説明する。
- その他の必須条件（Other required conditions）: feature flag と compat change が有効、Network Security Config 未指定、`usesCleartextTraffic` に依存、cleartext HTTP が必要。
- Compat Change ID: `415007211` (`DEPRECATE_USES_CLEARTEXT_TRAFFIC`)
- Compat default state: source annotation は `@Disabled`。targetSdk 37 default-enabled evidence は追加確認が必要。
- Confidence: Medium

## 早見マトリクス

| シナリオ | 影響 |
| --- | --- |
| Android 17 / targetSdkVersion 36 | compat change が無効なら従来通り `usesCleartextTraffic` が default cleartext policy に反映される想定。 |
| Android 17 / targetSdkVersion 37 | flag + compat change が有効で Network Security Config がない場合、`usesCleartextTraffic` が false 扱いになる可能性。 |
| Android 17 / targetSdkVersion 37 + Network Security Config | 必要 domain の `cleartextTrafficPermitted` を明示することで cleartext を許可する想定。 |

## 要約

Android 17 の文書は、将来 release で `usesCleartextTraffic` element を deprecate する計画を示している。Android 17 AOSP では `usesCleartextTraffic` attribute が `@Deprecated` / flagged API になり、Network Security Config 側に compat ChangeId `415007211` が追加された。

実装上は `deprecate_uses_cleartext_traffic2` feature flag と compat change が両方有効な場合、Network Security Config 未指定アプリの manifest `usesCleartextTraffic` は false に上書きされる。`usesCleartextTraffic` だけに依存せず、Network Security Configuration へ移行する必要がある。

## 顧客影響

- legacy HTTP endpoint への接続が、targetSdkVersion 37 以上で失敗する可能性がある。
- 閉域網、IoT、gateway、partner integration など HTTPS 化が完了していない通信で影響が出る可能性がある。
- Network Security Configuration に必要 domain を明示していれば影響を避けられる想定。

## 影響対象（Who Is Affected）

- 対象アプリ: HTTP cleartext connection が必要なアプリ、`usesCleartextTraffic` に依存しているアプリ。
- 対象機能: legacy HTTP API、閉域網 endpoint、IoT / gateway / partner integration。
- 対象条件: Network Security Configuration 未導入、または domain-scoped cleartext policy が未整理。

## 対応要否

- 必須対応: `usesCleartextTraffic` と HTTP endpoint を棚卸しし、`minSdkVersion` を確認する。
- 推奨対応: Network Security Configuration を導入し、必要 domain のみ `cleartextTrafficPermitted="true"` にする。
- 不要: HTTP cleartext connection を使わないアプリ、HTTPS 化済みのアプリでは直接影響は限定的。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 36 | baseline。`usesCleartextTraffic` と Network Security Configuration の現行挙動を確認。 |
| Android 17 | 36 | compat change が無効なら従来挙動の想定。 |
| Android 17 | 37 | flag + compat enabled では、Network Security Config なしの `usesCleartextTraffic` が無視される可能性。 |

## 顧客向け説明

Android 17 の文書では、将来 release で `usesCleartextTraffic` element を deprecate する計画が示されています。AOSP 実装上も、feature flag と compat change が有効な場合に manifest の `usesCleartextTraffic` を Network Security Config の デフォルト ポリシー へ反映しない path が追加されています。

HTTP が必要なアプリは Network Security Configuration へ移行し、必要な domain だけ `cleartextTrafficPermitted="true"` を明示してください。

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-all
- 検証対象の原文: future release で `usesCleartextTraffic` element を deprecate する計画があり、unencrypted HTTP connection が必要なアプリは Network Security Configuration file へ移行すべき。
- AOSP ファイル: `core/java/android/security/flags.aconfig`, `core/res/res/values/attrs_manifest.xml`, `core/api/current.txt`, `packages/NetworkSecurityConfig/platform/src/android/security/net/config/ManifestConfigSource.java`, `packages/NetworkSecurityConfig/tests/src/android/security/net/config/UsesCleartextTrafficDeprecationTest.java`
- AOSP ソース文脈: `ManifestConfigSource.getConfigSource()` が feature flag + compat change 有効時に `usesCleartextTraffic = false` に上書きする。
- 差分解釈: changed condition / changed default / API deprecation。
- ゲート結論: `DEPRECATE_USES_CLEARTEXT_TRAFFIC = 415007211L` と `deprecate_uses_cleartext_traffic2` が gate。targetSdk 37 default-enabled evidence は追加確認が必要。

## 人間の判断欄

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断

## 再検証記録（2026-08-22）

- Android 17 の公式 Behavior Change 一覧と最新通常AOSPタグを再確認した。
- 対応する[主レポート](../../../behavior-changes/all/security/usescleartexttraffic-deprecation-plan.md)で official section、AOSP project / remote / checkout、解決済み commit、比較 command、dirty risk を再検証した。
- 主レポートの分類、confidence、未確認事項を維持し、実機未実施の項目を Observed 済みへ変更していない。
- 全件の結果は[再検証台帳](../../../analysis/REVALIDATION_2026-08-22.md)を参照する。

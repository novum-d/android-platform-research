# 翻訳用語集

このファイルは、Android Behavior Change 調査レポートを日本語化するときの標準訳を定義する。
分類 ID、API 名、コマンド、ファイルパスは原則として翻訳しない。

## 標準訳

| 英語 | 標準訳 | 備考 |
| --- | --- | --- |
| applicability | 適用条件 | 見出しでは「適用条件分類」も使う。 |
| applicability classification | 適用条件分類 | `APPLICABILITY_CLASSIFICATION.md` ではこの訳を使う。 |
| evidence | 根拠 | AOSP evidence は「AOSP 根拠」でもよい。 |
| finding | 調査項目 | 文脈上「finding」を残す必要がある場合を除く。 |
| gate | gate / 適用 gate | 技術的な gate は無理に訳さない。説明文では「適用条件」も可。 |
| confidence | confidence | `High confidence` などの分類語は英語を残す。 |
| missing evidence | 不足している根拠 | |
| original statement | 検証対象の原文 | Summary / report の根拠欄で使用。 |
| original applicability statement | 検証対象の適用条件文 | |
| official documentation | 公式ドキュメント | |
| official documentation page | 公式ドキュメントページ | |
| AOSP files | AOSP ファイル | |
| AOSP source context | AOSP ソース文脈 | |
| diff interpretation | 差分解釈 | |
| gate conclusion | 適用 gate の結論 | |
| required context | 必須記入項目 | report template 由来の項目。 |
| required interpretation | 必須分類 | |
| evidence limitation | 根拠上の制約 | |
| current status | 現在の状況 | |
| from | 比較元 | AOSP tag の比較元。 |
| to | 比較先 | AOSP tag の比較先。 |
| previous targetSdkVersion | 以前の targetSdkVersion | |
| target targetSdkVersion | 対象 targetSdkVersion | |
| document | 文書 | metadata 欄で使用。 |
| related documents | 関連文書 | |
| section | セクション | |
| page type | ページ種別 | |
| final priority | 最終優先度 | |
| final severity | 最終影響度 | |
| release readiness | リリース判断 | |
| customer communication required | 顧客通知要否 | |
| human decision required | 人間による判断が必要 | |
| further investigation required | 追加調査が必要 | |
| unknown | 未確認 | 調査上未確認の場合。 |
| likely | 可能性が高い | 単独では使わず「可能性が高いが未検証」などにする。 |
| unverified | 未検証 | |
| TBD | 未定 | |
| local checkout | ローカル checkout | 手元にある checkout を指す。 |
| local working tree | ローカル working tree | 手元の git working tree を指す。 |
| local `frameworks-base` checkout | ローカルの `frameworks-base` checkout | 手元にある `frameworks-base` ディレクトリ / checkout を指す。 |
| default state | 既定状態 | compat framework 欄。 |
| change name | 変更名 | compat framework 欄。 |
| toggleable for testing | テスト時の切り替え可否 | |

## 残す用語

以下は原則として英語または識別子のまま残す。

- `targetSdkVersion`
- `minSdkVersion`
- `Compat Change ID`
- `Change ID`
- `AOSP`
- `Behavior Change`
- `Mainline`
- `Google Play system update`
- `API surface`
- `current.txt`
- `frameworks-base`
- `foreground service`
- `while-in-use`
- `local network`
- `local network permission`
- `IntentSender`
- `PendingIntent`
- `Network Security Configuration`
- `FileProvider`
- `WebOTP`
- `SMS Retriever`
- `SMS User Consent API`
- `UNKNOWN_NEEDS_MORE_EVIDENCE`
- `OS_UPDATE_ALL_APPS`
- `TARGET_SDK_37`
- `TARGET_SDK_37_CONDITIONAL`
- `MAINLINE_OR_PLAY_SYSTEM_UPDATE`
- `API_ADDITION_ONLY`

## `local` の扱い

`local` は文脈で訳し分ける。

| 文脈 | 扱い | 例 |
| --- | --- | --- |
| 手元の checkout / working tree / repository を指す場合 | 「ローカルの」「手元の」と訳す | `local frameworks-base checkout` → `ローカルの frameworks-base checkout` |
| Android 機能名やネットワーク概念の一部の場合 | 原則として `local` を残す | `local network permission`, `local network access` |
| AOSP / git の状態説明の場合 | 「ローカル」を使ってよい | `local checkout has no tag` → `ローカル checkout にタグが存在しない` |

## 判定表の標準表現

| 英語表現 | 標準訳 |
| --- | --- |
| Likely Yes / Conditional, but unverified | 可能性は高いが条件付き、かつ未検証 |
| Likely No, but unverified | 不要と考えられるが未検証 |
| Likely No for this guidance, but unverified | この guidance では不要と考えられるが未検証 |
| Likely No immediate enforcement, but unverified | 即時 enforcement はない可能性が高いが未検証 |
| Likely No immediate runtime behavior, but unverified | 即時の runtime behavior はない可能性が高いが未検証 |
| Yes | ある |
| Yes, for relevance | 関連条件としてある |
| Partially | 一部で必要 |
| Unknown | 未確認 |

## 判断欄の標準表現

| 英語表現 | 標準訳 |
| --- | --- |
| Human decision required | 人間による判断が必要 |
| Further investigation required after Android 17 AOSP tag is available | Android 17 AOSP タグ公開後に追加調査が必要 |
| Final Priority | 最終優先度 |
| Final Severity | 最終影響度 |
| Release Readiness | リリース判断 |
| Customer Communication Required | 顧客通知要否 |

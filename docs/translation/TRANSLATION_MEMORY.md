# 翻訳メモリ

このファイルは、過去の Android 17 調査レポート翻訳で採用した表現を記録する。
今後の翻訳では、ここを参照して表現の一貫性を保つ。

## Metadata

```text
From:
```

採用訳:

```text
比較元:
```

```text
To:
```

採用訳:

```text
比較先:
```

```text
Previous targetSdkVersion:
```

採用訳:

```text
以前の targetSdkVersion:
```

```text
Target targetSdkVersion:
```

採用訳:

```text
対象 targetSdkVersion:
```

```text
Document:
Related documents:
Section:
Page type:
```

採用訳:

```text
文書:
関連文書:
セクション:
ページ種別:
```

## 判定表

```text
| Question | Answer | Evidence |
```

採用訳:

```text
| 確認項目 | 回答 | 根拠 |
```

```text
Likely Yes / Conditional, but unverified
```

採用訳:

```text
可能性は高いが条件付き、かつ未検証
```

```text
Likely No, but unverified
```

採用訳:

```text
不要と考えられるが未検証
```

```text
Yes, for relevance
```

採用訳:

```text
関連条件としてある
```

## Compat framework

```text
Change ID: Unknown
Change name: Unknown
Default state: Unknown
Toggleable for testing: Unknown
```

採用訳:

```text
Change ID: 未確認
変更名: 未確認
既定状態: 未確認
テスト時の切り替え可否: 未確認
```

## 根拠欄

```text
Official documentation:
Original statement:
AOSP files:
AOSP source context:
Diff interpretation:
Gate conclusion:
```

採用訳:

```text
公式ドキュメント:
検証対象の原文:
AOSP ファイル:
AOSP ソース文脈:
差分解釈:
適用 gate の結論:
```

```text
Official documentation page:
Original applicability statement:
```

採用訳:

```text
公式ドキュメントページ:
検証対象の適用条件文:
```

## 判断欄

```text
Human Decision Placeholder
```

採用訳:

```text
人間の判断欄
```

```text
Final Priority:
Final Severity:
Release Readiness:
Customer Communication Required:
```

採用訳:

```text
最終優先度:
最終影響度:
リリース判断:
顧客通知要否:
```

```text
Human decision required
Further investigation required after Android 17 AOSP tag is available
```

採用訳:

```text
人間による判断が必要
Android 17 AOSP タグ公開後に追加調査が必要
```

## README / 手順書

```text
Current status:
Generated from:
Using:
Rule:
How To Use:
```

採用訳:

```text
現在の状況:
生成元:
使用するコマンド:
取り扱いルール:
使い方:
```

```text
Android 17 AOSP tag is not currently available in the local frameworks-base checkout.
```

採用訳:

```text
現時点では、ローカルの `frameworks-base` checkout に Android 17 AOSP タグは存在しません。
```

補足:
- ここでの `local` は Android の機能名ではなく、手元にある checkout / ディレクトリを指す。
- `local network permission` の `local` は機能名の一部なので、この訳し方を流用しない。

```text
Do not create High confidence AOSP-backed conclusions until the target Android 17 tag is available.
```

採用訳:

```text
対象となる Android 17 タグを利用できるようになるまでは、AOSP 根拠に基づく High confidence の結論は作成しないでください。
```

## 調査上の定型表現

```text
Android 17 AOSP tag is not available locally.
```

採用訳:

```text
ローカルの `frameworks-base` には Android 17 AOSP タグが存在しない。
```

```text
Do not assign High confidence.
```

採用訳:

```text
High confidence を付けない。
```

```text
Customer-facing wording does not mix OS update impact with targetSdkVersion impact.
```

採用訳:

```text
顧客向け表現で、OS アップデートによる影響と targetSdkVersion 変更による影響を混同していない。
```

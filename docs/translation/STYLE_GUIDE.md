# 翻訳スタイルガイド

このファイルは、Android Behavior Change 調査レポートを日本語化するときの文体と判断基準を定義する。

## 基本方針

- 人間向けの説明、レポート、Summary は日本語で書く。
- 分類 ID、API 名、コマンド、URL、ファイルパス、コードブロックは原則として翻訳しない。
- 公式文書の意味、調査上の不確実性、AOSP 根拠の有無を変えない。
- 文脈を確認せずに文字列の一括置換をしない。
- ファイル単位で読み、訳す箇所と残す箇所を判断する。

## 文体

- 調査レポート本文は「である」調を基本にする。
- README や手順書は、既存文体に合わせる。必要に応じて「です・ます」調を使ってよい。
- 顧客向け説明は自然で読みやすい表現を優先する。
- 不確実な内容は断定しない。

例:

```text
悪い例:
Android 17 で必ず失敗する。

良い例:
公式文書上は影響する可能性がある。ただし、関連AOSP projectの実装pathを未確認のためgateは未検証である。
```

## 技術用語の扱い

- `gate` は技術的な意味が強い場合は「gate」のまま残す。
- 説明文では「適用条件」「分岐条件」と言い換えてよい。
- `local` は文脈で訳し分ける。手元の checkout / working tree を指す場合は「ローカルの」または「手元の」と訳す。`local network` のように Android 機能名やネットワーク概念の一部である場合は `local` を残す。
- `default state` は compat framework 欄では「既定状態」と訳す。
- `High confidence` は分類語として英語を残す。
- `Behavior Change` は文書カテゴリとして英語を残す。
- `Summary` はファイル名やディレクトリ名と対応させる場合は英語を残してよい。本文では「要約」も使える。

## 不確実性の表現

- `Unknown` は「未確認」とする。
- `Unverified` は「未検証」とする。
- `Likely` は単独で断定せず、「可能性が高いが未検証」のように根拠不足を明示する。
- target tagまたは関連project checkoutがない場合は、対象versionとprojectを明記して「`<project>`の`<target-tag>`を未取得のため未確認」と書く。tagが公開済みか、ローカルcheckoutにないだけかを混同しない。
- 最終 priority / severity / release readiness は agent が確定しない。

## 翻訳しない箇所

以下は原則としてそのまま残す。

- コードブロック
- シェルコマンド
- URL
- ファイルパス
- Java / Kotlin / XML / manifest の識別子
- Android API 名
- AOSP tag 名
- 分類 ID
- 公式原文の短い引用

## Report と Summary の整合

- Report で「未確認」とした内容は Summary でも「未確認」とする。
- Reportで「関連AOSP project / implementation pathの追加調査が必要」とした場合、Summaryの判断欄も同じ不足証拠を示す。
- `AOSP ファイル`、`AOSP ソース文脈`、`差分解釈`、`適用 gate の結論` の順序をできるだけ揃える。
- `Final Priority` などの判断欄は、人間判断であることを明記する。

## 禁止事項

- 文書全体に対する機械的一括置換。
- コード、URL、コマンド、分類 ID を巻き込む翻訳。
- AOSP 根拠がない状態で High confidence と書くこと。
- `targetSdkVersion` 条件と OS update 条件を混同すること。
- 公式文書が future release と書いている内容を Android 17 即時 enforcement と断定すること。

## 推奨手順

1. 対象ファイルを読む。
2. 公式文書の意味と AOSP 根拠の有無を確認する。
3. 見出し、metadata、判定表、根拠欄、判断欄を文脈ごとに整える。
4. Summary がある場合は同じ判断表現に揃える。
5. `git diff --check` と残存テンプレート語の検索で確認する。

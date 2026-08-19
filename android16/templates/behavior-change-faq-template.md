# [Behavior Change Title] - FAQ

## 位置づけ（Scope）

このファイルは、Behavior Change の primary report を読む際に生じる用語・前提・処理経路・影響判定の疑問を補足する FAQ companion である。

根拠、適用条件、classification、confidence、Human Decision は primary report / one-page summary を正とする。この FAQ 自体で新しい Behavior Change や独立した適用分類を定義しない。

Primary report:
- `<relative path>`

One-page summary:
- `<relative path>`

Related app report / PM overview, if applicable:
- `<relative path>`

## 調査メタデータ（Metadata）

- Android version: Android 16
- From tag: `android-15.0.0_r36`
- To tag: `android-16.0.0_r4`
- Parent section: `<Behavior Change section>`
- FAQ scope: `<terms / architecture / runtime flow / testing / common misunderstanding>`
- Inherited applicability classification: `<label from primary report>`
- Inherited confidence: `<confidence from primary report>`

## FAQ作成ルール（Authoring Rules）

- FAQはprimary reportと別ファイルにする。
- primary reportには、FAQの要点を重複掲載せず、短い位置づけとFAQへのリンクを置く。
- 一つの質問を一つの見出しにする。
- 質問は読者が実際に迷う表現で書く。
- 回答は「短い回答」「説明」「本件との関係」「確認方法」の順を基本とする。
- Facts、Observations、Hypothesesを混ぜない。
- OS update impact と targetSdkVersion impact を混ぜない。
- FAQだけを読んで独立したBehavior Changeや別classificationがあるように見せない。
- app固有の影響予測を書く場合は、事実と未確認の予測を分け、該当app reportにも反映する。

## FAQ

### Q1. [Reader question]

短い回答:

`<one or two sentences>`

説明:

`<background and mechanics>`

本件との関係:

`<why the answer matters for this Behavior Change>`

確認方法:

`<source review / code search / device test / log signal>`

### Q2. [Reader question]

短い回答:

`<one or two sentences>`

説明:

`<background and mechanics>`

本件との関係:

`<why the answer matters for this Behavior Change>`

確認方法:

`<source review / code search / device test / log signal>`

## 用語早見表（Glossary）

| 用語 | 説明 | Behavior Changeとの関係 |
| --- | --- | --- |
| `<term>` | `<plain-language definition>` | `<relevance>` |

## 適用条件の再確認（Applicability Reminder）

- OS update impact: `<inherits from primary report>`
- targetSdkVersion impact: `<inherits from primary report>`
- Additional conditions: `<device / API / permission / state>`
- FAQで未解決の条件: `<unknowns>`

この節ではprimary reportのclassificationを再判定せず、FAQ回答に必要な条件だけを短く再掲する。

## Facts / Observations / Hypotheses

### Facts

- `<official documentation or source-backed fact>`

### Observations

- `<project or device observation>`

### Hypotheses

- `<unverified interpretation and how to verify it>`

## Verification

- Source review: `<files / symbols / official references>`
- Code search: `<commands / patterns>`
- Device matrix: `<OS / targetSdkVersion / device / app state>`
- Expected log / signal: `<log or observable behavior>`
- Pass / fail criteria: `<what counts as confirmed>`

## References

- `<Official Behavior Change URL>`
- `<API / kernel / AOSP reference>`
- `<Primary report>`
- `<One-page summary>`

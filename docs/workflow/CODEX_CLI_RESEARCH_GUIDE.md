# Codex CLI 調査依頼ガイド（Codex CLI Research Guide）

この手順書は、Codex CLI に Android Behavior Change 調査を依頼する時の URL-only workflow、プロンプト生成規則、実行規則を定義します。

調査作成・更新、実装例、判断ログ、再レビューなど目的別の入力例は [PROMPT_USE_CASES.md](PROMPT_USE_CASES.md) を参照してください。

通常の依頼では、調査対象の公式 Behavior Change セクション URL だけを入力します。Codex は公式セクションと repository の version-specific instructions から必要項目を補完し、中間プロンプトファイルを生成して、その内容を同じセッション内で実行します。長い固定指示や公式文書抜粋を人間が毎回貼る必要はありません。

```text
項目 URL
-> 公式セクションの解析
-> バージョン・カテゴリ・出力先等を補完
-> 中間プロンプトファイル生成
-> Codex で実行
```

## URL-only workflow

### 人間が入力するもの

原則として、Android Developers の Behavior Change セクション URL 1件だけを入力します。URL fragment がある場合は、その fragment が指すセクションを調査単位とします。

```text
https://developer.android.com/about/versions/<version>/behavior-changes-<page>#<section>
```

URL とともに追加の調査観点が指定された場合は、それも中間プロンプトへ保存します。URLから取得できる値を人間へ再入力させてはいけません。

### Step 1: 公式セクションの解析

必ず公式ページを読み、対象セクションから以下を抽出します。

- page title と canonical page URL
- page type: all apps / apps targeting Android `<version>` / compat framework changes
- official category
- parent section、section title、subsections
- original statements to verify
- OS version、targetSdkVersion、permission、API、device、app state などの適用条件
- 追加条件、例外、opt-in、opt-out、移行方法
- セクション内の公式関連リンク

fragment を含まないページ URL など、1つの Behavior Change セクションを一意に特定できない場合は、推測で複数項目をまとめず、対象セクションの確認を求めます。ページ取得に失敗した場合も、公式本文を推測で補完しません。

### Step 2: repository metadata の補完

公式ページと repository から以下を補完します。

| 項目 | Source of truth |
| --- | --- |
| Android version | 公式 URL と page title |
| Version directory | `android<version>/` |
| From / To tag | `<version-dir>/AGENTS.md`、次に `<version-dir>/README.md` |
| Previous / Target targetSdkVersion | `<version-dir>/AGENTS.md` と適用条件分類 |
| Page type | 公式 URL、ページ見出し、公式 statement |
| Official category | 公式ページ上の対象セクションの親カテゴリ |
| Output paths | このガイドの path rule と既存の category / slug convention |
| Applicability labels | `<version-dir>/behavior-changes/APPLICABILITY_CLASSIFICATION.md` |
| Report / summary templates | `<version-dir>/templates/` |

prompt template の placeholder と version-specific instructions が矛盾する場合は、version-specific instructions を優先します。既存ファイルとの衝突を確認し、同じ項目の既存調査なら更新候補として扱います。別項目と衝突する場合は勝手に上書きしません。

出力 path は次の形式で決定します。

```text
<version-dir>/behavior-changes/<all-or-target>/<official-category-slug>/<topic-slug>.md
<version-dir>/summaries/<all-or-target>/<official-category-slug>/<topic-slug>-summary.md
```

### Step 3: 中間プロンプトファイル生成

補完した内容を、このガイドの詳細入力フォーマットに従って次へ保存します。

```text
tmp/research-prompts/android<version>/<all-or-target>/<topic-slug>.md
```

中間ファイルには placeholder を残さず、最低限以下を含めます。

- source URL
- 補完済みの research target と output paths
- 公式セクションから抽出した original statements
- applicability details、exceptions、related links
- 公式本文と repository metadata を分けた extraction notes
- 調査時に確認すべき AOSP gate / compat framework の検索観点
- report、summary、必要な companion file の作成指示

不明な値をもっともらしく埋めてはいけません。調査を継続できる不明点は `Unknown - verify during investigation` として明示し、分類や出力先を変える不明点だけを人間へ確認します。

中間プロンプトは生成物であり、調査レポートの evidence や正式な成果物ではありません。Git の追跡対象にも含めません。

### Step 4: 生成プロンプトの実行

中間ファイルを書いた後に必ず読み返し、placeholder、URL、version、tag、targetSdkVersion、page type、category、output path の整合性を確認します。問題があれば中間ファイルを修正します。

整合性確認後、そのファイルを現在の Codex セッションにおける authoritative task specification として扱い、同じターンで `Required investigation steps` へ進みます。人間へ再貼付を求めず、別の `codex exec` を再帰的に起動しません。

中間ファイルを生成しただけでは調査完了ではありません。report と summary の作成、review checklist による確認まで終えた時点で完了です。

## 事前準備

調査を始める前に、対象バージョンの以下が存在することを確認します。

```text
<version-dir>/README.md
<version-dir>/AGENTS.md
<version-dir>/behavior-changes/APPLICABILITY_CLASSIFICATION.md
<version-dir>/templates/customer-report-template.md
<version-dir>/templates/one-page-summary-template.md
```

`frameworks-base` に比較対象 tag が存在することも確認します。

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list '<from-tag>'
git -C frameworks-base tag --list '<to-tag>'
```

`frameworks-base` が dirty な場合は、ローカル working tree の変更を platform evidence として扱わないでください。必ず `<from-tag>` と `<to-tag>` の明示的な tag 比較を使います。

AOSP checkout の扱いは以下も確認します。

```text
docs/workflow/AOSP_CHECKOUT.md
```

## 展開済みプロンプトの項目

以下は Codex が URL と repository から補完して中間プロンプトへ記録する項目です。URL-only workflow では人間が手入力する必要はありません。

| 入力項目 | 内容 |
| --- | --- |
| Android version | 調査対象の Android バージョン名 |
| Version directory | 調査成果物を置くディレクトリ |
| From tag | 比較元 AOSP tag |
| To tag | 比較先 AOSP tag。未公開なら `TBD: Android <version> AOSP tag` |
| Previous targetSdkVersion | OS update impact を比較するための直前 targetSdkVersion |
| Target targetSdkVersion | 調査対象の targetSdkVersion / API level |
| Behavior Change section title | 調査する Behavior Change セクション名 |
| Official documentation URL | 公式 Behavior Change 文書の URL |
| Official documentation category | 公式 Behavior Change 文書上のカテゴリ。例: Core functionality / Accessibility / Privacy / Security / Media |
| Report output file | 作成する調査レポートの path |
| Summary output file | 作成する 1ページ要約の path |
| Official documentation excerpt | 公式文書の該当セクション原文 |

`Official documentation excerpt` には、最低限以下を含めます。

- セクションタイトル
- 原文 statement
- 適用条件が書かれている段落
- 追加条件、例外、opt-out が書かれている段落
- 関連リンクがあれば URL

詳細な調査依頼を作る場合は、以下の項目名を使って構造化します。既存の最小入力フォーマットと意味は同じですが、Codex が original statement、applicability、関連リンク、追加調査観点を取り違えないように分離します。

| 詳細入力項目 | 内容 |
| --- | --- |
| 調査対象 | version / tag / targetSdkVersion / section title / URL / category / output paths |
| 公式ドキュメント抜粋 | page title / page URL / page type / page category / parent section title / section title / subsections |
| Original statements to verify | 公式文書の検証対象 statement。複数ある場合は bullet list |
| Applicability details | OS 条件、targetSdkVersion 条件、permission / API / device / app state などの適用条件 |
| Related links | 公式関連ページ、API reference、compat framework、blog、migration guide など |
| Additional notes | 初期分類仮説、AOSP で必ず確認する項目、必須 matrix、影響対象アプリ種別、テスト観点、Facts / Observations / Hypotheses / Conclusions の要求、Human decision placeholder 要求 |

詳細入力では、`Parent section title` と `Subsections` は該当する場合だけ入れます。サブセクション単体を調査する場合は、親セクションの base behavior と当該サブセクションの論点を分けて書きます。

## 手動入力用の最小フォーマット（fallback）

公式 URL だけでは対象セクションを特定できない場合、または URL を利用できない環境でのみ、以下をコピーし、値を埋めて Codex CLI に貼り付けます。

```text
docs/workflow/CODEX_CLI_RESEARCH_GUIDE.md の固定調査指示に従って、以下の Behavior Change 1件を調査してください。

Research target:
- Android version: <android-version>
- Version directory: <version-dir>
- From tag: <from-tag>
- To tag: <to-tag>
- Previous targetSdkVersion: <previous-target-api>
- Target targetSdkVersion: <target-api>
- Behavior Change section title: <section-title>
- Official documentation URL: <behavior-change-url>
- Official documentation category: <official-category>
- Report output file: <report-file>
- Summary output file: <summary-file>

Official documentation excerpt:
Page title: <page-title>
Page URL: <behavior-change-url>
Page type: all apps / apps targeting Android <version> / compat framework changes
Page category: <official-category>
Section title: <section-title>

Original text:
<official statement and section text>

Additional notes:
<related links, exceptions, opt-out, migration notes, or "none">
```

## 詳細入力フォーマット

詳細な調査依頼を作る場合は、以下のフォーマットを使います。最小入力フォーマットより長くなりますが、複雑な Behavior Change、サブセクション、例外、opt-in / opt-out、将来 release plan を扱う調査ではこちらを優先します。

```text
以下の内容で調査してください。

調査対象

Android version: <android-version>

Version directory: <version-dir>

From tag: <from-tag>

To tag: <to-tag>

Previous targetSdkVersion: <previous-target-api>

Target targetSdkVersion: <target-api>

Behavior Change section title: <section-title>

Official documentation URL: <behavior-change-url>

Official documentation category: <official-category>

Report output file: <report-file>

Summary output file: <summary-file>


公式ドキュメント抜粋

Page title: <page-title>

Page URL: <page-url>

Page type: all apps / apps targeting Android <version> / compat framework changes

Page category: <official-category>

Parent section title: <parent-section-title, if applicable>

Section title: <section-title>

Subsections:
- <subsection, if applicable>


Original statements to verify:

"<official statement 1>"

"<official statement 2>"


Applicability details:

Applies to <OS / targetSdkVersion / permission / API / device / app state conditions>.

Potentially affects apps that:
- <affected app/API/pattern 1>
- <affected app/API/pattern 2>

The investigation must separate:
- <scenario 1>
- <scenario 2>
- <scenario 3>


Related links:

<official doc URL>

<API reference URL>

<compat framework URL>


Additional notes:

初期分類仮説は <classification hypothesis>。

ただし、利用可能な分類ラベルは <version-dir>/behavior-changes/APPLICABILITY_CLASSIFICATION.md に従うこと。

調査開始時に Official documentation URL の該当セクションを再確認し、Original statements / Applicability details が最新の公式本文と一致しているか確認する。差分があれば report に記録する。

AOSP では少なくとも以下を確認する:
- <required AOSP evidence 1>
- <required AOSP evidence 2>
- <required AOSP evidence 3>

Android <version> / targetSdkVersion <previous-target-api>、Android <version> / targetSdkVersion <target-api>、baseline OS / targetSdkVersion <target-api> の期待挙動マトリクスを必ず作る。

さらに以下のマトリクスを必ず作る:
- <detailed matrix row 1>
- <detailed matrix row 2>

顧客向け説明では「OS アップデートしただけの影響」と「targetSdkVersion を上げた時の影響」を混ぜない。

影響対象は以下のアプリ種別に分けて書く:
- <app type 1>
- <app type 2>

テスト観点として以下を明示する:
- <test focus 1>
- <test focus 2>

調査結果では Facts / Observations / Hypotheses / Conclusions を分ける。

Report と Summary は日本語で作成する。

One page summary には Human decision placeholder を必ず残す。
```

## Android 17 用の調査依頼テンプレート

Android 17 調査では、ルートの `android17-prompt-template.md` を使います。単純な項目では最小入力として使い、複雑な項目では詳細入力フォーマットとして使います。

```text
android17-prompt-template.md
```

## 固定調査指示

Codex は最小入力フォーマットを受け取ったら、このセクションを固定指示として扱います。依頼プロンプト側に再掲する必要はありません。

### Mission

- Behavior Change section 1件だけを end-to-end で調査する。
- 必ず公式 Behavior Change 文書から開始する。
- AOSP source は公式文書の statement を検証・説明するためだけに使う。
- 顧客向け report、summary、説明、判断材料は日本語で書く。

### Repository rules

- 作業前に `README.md`、`AGENTS.md`、`<version-dir>/AGENTS.md` があればそれ、`docs/GETTING_STARTED.md`、`docs/workflow/INVESTIGATION_PLAYBOOK.md`、`docs/workflow/REVIEW_CHECKLIST.md`、`docs/workflow/CONFIDENCE.md`、`docs/workflow/AOSP_CHECKOUT.md`、`<version-dir>/behavior-changes/APPLICABILITY_CLASSIFICATION.md` を読む。
- report は `<version-dir>/templates/customer-report-template.md` を使う。
- summary は `<version-dir>/templates/one-page-summary-template.md` を使う。
- version-specific output は `<version-dir>/` 配下に置く。
- Android 17 の report / summary は、公式文書のページ種別とカテゴリに合わせて `<version-dir>/behavior-changes/<all-or-target>/<official-category-slug>/<topic-slug>.md` と `<version-dir>/summaries/<all-or-target>/<official-category-slug>/<topic-slug>-summary.md` に置く。ファイル名の先頭に連番は付けない。
- unrelated file を上書きしない。
- `docs/notes/PERSONAL_NOTES.md` は編集しない。
- final priority、final severity、release readiness、customer communication priority は決めない。人間の判断欄として残す。
- AOSP evidence を使う前に `git -C frameworks-base status --short` を確認する。dirty な working tree は platform evidence として扱わず、明示的な tag 比較を使う。

### Required investigation steps

1. 検証対象の公式 statement を抜き出す。
2. documentation page type と initial applicability assumption を特定する。
3. `<from-tag>` と `<to-tag>` の AOSP tag 比較で evidence を確認する。`<to-tag>` が未入手なら、その制約を記録し High confidence にしない。
4. AOSP evidence がある場合は file / symbol / entry point / caller を特定する。
5. その code path が Behavior Change の根拠になる理由を書く。
6. baseline behavior と target Android behavior を分ける。
7. diff type を added behavior / removed behavior / changed condition / changed default / no behavior change のいずれかで説明する。
8. targetSdkVersion gate と compat framework evidence を確認する。
9. gate / compat evidence が見つからない場合は、検索した file / symbol / query と見つからない理由を記録する。
10. OS update impact と targetSdkVersion impact を分ける。
11. previous targetSdkVersion / target targetSdkVersion / compat force-enabled / compat force-disabled の期待挙動を分ける。
12. facts、observations、hypotheses、conclusions を分ける。
13. `<version-dir>/behavior-changes/APPLICABILITY_CLASSIFICATION.md` の分類ラベルから primary classification を1つだけ選ぶ。
14. confidence level と不足根拠を説明する。
15. Android app developer 向けの対応候補を書く。
16. report file と summary file を作成または更新する。
17. `docs/workflow/REVIEW_CHECKLIST.md` で report / summary をレビューし、不足を修正する。

### Final checks

- `shared/templates` や `docs/templates` など旧 template path を導入していないか repository search で確認する。
- root `git status --short` と `git -C frameworks-base status --short` を確認する。
- 完了内容と、人間が判断すべき残事項を final response にまとめる。

## 実行後に人間が確認すること

Codex の出力後、人間が以下を確認します。

- 公式文書の原文が正しく扱われているか
- AOSP evidence が Behavior Change の説明と対応しているか
- OS update impact と targetSdkVersion impact が混ざっていないか
- compat framework evidence の有無が明記されているか
- `High confidence` の根拠が十分か
- 顧客向けの説明になっているか
- final priority / severity を人間が判断できる材料になっているか

人間の最終判断は、対象バージョンの `decisions/` に記録します。

## 追加確認用プロンプト

Codex の出力が弱い場合だけ、以下を追加で貼ります。

```text
作成した report と summary を docs/workflow/REVIEW_CHECKLIST.md に照らして再レビューしてください。
不足している項目を修正してください。
特に original statement、AOSP source context、diff interpretation、applicability classification、OS update impact、targetSdkVersion impact、compat framework evidence、confidence level を確認してください。
```

compat framework の確認が弱い場合:

```text
compat framework evidence を再確認してください。
@ChangeId、@EnabledAfter、@EnabledSince、@Disabled、CompatChanges.isChangeEnabled を検索し、
該当 Change ID、default state、targetSdkVersion との関係を明記してください。
見つからない場合は、検索した file / symbol / query を記録してください。
```

AOSP 根拠がファイル名だけになっている場合:

```text
AOSP source context が不足しています。
file / symbol / entry point / caller、baseline behavior、target Android behavior、
diff type、なぜそのコードパスが Behavior Change の根拠になるかを追記してください。
無関係または除外したコードパスがあれば、それも書いてください。
```

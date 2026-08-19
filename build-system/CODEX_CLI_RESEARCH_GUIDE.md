# Build System Codex CLI 調査依頼ガイド

この手順書は、公式 Build System entry-point URL を起点に、必要な情報を補完し、中間プロンプトを生成して同じ Codex セッションで調査を実行する規則を定義する。

AGP差分の作成・更新、project向けchecklist、検証結果反映、preview watchなど目的別の入力例は [../docs/workflow/PROMPT_USE_CASES.md](../docs/workflow/PROMPT_USE_CASES.md) を参照する。

現在、完全な URL-only workflow の対象は AGP Release Notes である。

```text
AGP Release Notes URL
-> 公式 Release Notes の解析
-> From / To version・release channel・出力先等を補完
-> 中間プロンプトファイル生成
-> Codex で AGP 差分調査を実行
```

## 人間が入力するもの

原則として、対象 version または release line を一意に識別できる公式 AGP Release Notes URL 1件だけを入力する。

```text
https://developer.android.com/build/releases/agp-<version>-release-notes
```

From version、対象 project、追加観点が同時に指定された場合は、その値を優先して中間プロンプトへ保存する。URLやrepositoryから取得できる情報を人間へ再入力させない。

## Step 1: 公式 Release Notes の解析

公式ページを読み、最低限以下を抽出する。

- page title、canonical URL、対象 AGP version / release line
- stable / beta / alpha / rc などの release channel
- release date と patch releases
- compatibility table と minimum / default versions
- new features、behavior changes、breaking changes、deprecations
- DSL、Variant API、task、lint、R8、resource processing、performance、CI、NDK への変更
- fixed issues と issue tracker links
- migration guide、API reference、compatibility documentation などの公式リンク

Release Notes に含まれる変更を最初に inventory 化し、その後で deep dive 対象と対象外を分類する。先に一部の目立つ変更だけを選んではいけない。

対象 version を一意に特定できない generic URL、複数 release line をまとめた URL、取得できないページについては推測で進めず確認する。

Release Notes の page title が `AGP X.Y.0` でも、それだけで stable と判定しない。固定 issue の release heading、公式 AGP API Reference の `Current Release` / `Preview Releases`、対応する Android Studio release 情報を照合し、channel を確定する。公式情報が食い違う場合は preview として扱い、不一致を中間プロンプトへ保存する。

## Step 2: From / To version の補完

To version は公式 Release Notes の page title、version heading、release tableから決定する。

From version は次の優先順位で決定する。

1. 同じ依頼でユーザーが明示した From version
2. requested target を To version とする既存の詳細調査に記録された From version
3. requested target より低い、完了済み stable AGP 詳細調査のうち、version ordering 上もっとも新しい To version

補完時は `build-system/agp/research-scope.json` を機械可読な正本とし、`build-system/agp/README.md` の Current Research、`build-system/agp/versions/` の Metadata / Research Complete Criteria が一致することを確認する。

次は比較元として使わない。

- local machine に偶然インストールされている version
- `demos/` の version
- 未完了調査の暫定 version
- preview watch の version
- requested target 以上の version

同じ優先順位で候補が複数残る、version ordering を判断できない、または完了済み baseline が存在しない場合だけ From version を確認する。

既存成果物の identity は target URL だけでなく、`(target version / release line, release channel, purpose)` で判定する。同じ identity の単一 version inventory は目的と path を再利用し、差分調査へ無理に変換しない。同じ stable version diff identity は既存の From / To と path を再利用する。preview watch と stable version diff は URL が同じでも別 identity とし、stable 調査で preview watch を上書きしない。

## Step 3: 調査 metadata と出力先の補完

既存成果物の version、channel、purpose、path、Research / Decision status は `build-system/agp/research-scope.json` から補完する。成果物を作成・更新した場合は registry と人間向け index を同時に更新する。

stable version diff の標準 path は次のとおりとする。versionはfilename-safeな形式へ正規化し、既存pathがある場合は既存表記を優先する。

```text
Detail: build-system/agp/versions/agp-<from>-to-<to>.md
Summary: build-system/agp/summaries/agp-<from>-to-<to>-summary.md
Checklist: build-system/agp/checklists/agp-<from>-to-<to>-migration-checklist.md
Intermediate prompt: tmp/research-prompts/build-system/agp/agp-<from>-to-<to>.md
```

この Checklist path は、version pair 共通の再利用可能な手順を置く場所である。対象 project 固有の affected modules、実行結果、実変更、Human Decision は対象 project 側の PR / issue / 実行用 checklist に記録し、repository-wide checklist へ実績として混在させない。

preview releaseはstable migration targetと分離し、次のconventionを使う。

```text
Detail: build-system/agp/versions/agp-<major>.<minor>-preview-watch.md
Intermediate prompt: tmp/research-prompts/build-system/agp/agp-<major>.<minor>-preview-watch.md
```

preview watchではstableへの移行チェックリストを作らない。previewをproductionのRecommended versionとして扱わない。

出力先が同じ channel / purpose の既存成果物なら更新対象として扱う。別の version pair、release channel、または purpose の成果物と衝突する場合は上書きせず確認する。

対象application projectが指定されていないことはblockerにしない。その場合は次のように明記する。

- Affected Modules: 対象project未指定のため一般的な候補と検出方法を記載
- Project Verification: 未実施
- Verification Commands: 実行候補として記載し、実行済みとしない
- Current project versions: 未確認

## Step 4: 中間プロンプトファイル生成

補完した内容を次へ保存する。

```text
tmp/research-prompts/build-system/agp/<derived-name>.md
```

中間プロンプトにはplaceholderを残さず、最低限以下を含める。

### Research target

- Area: AGP
- Entry Point URL
- Page title
- Release channel
- From versionとderivation source
- To versionとofficial evidence
- Detail / Summary / Checklist output paths
- 対象projectの有無

### Extracted official entry-point facts

- compatibility table
- change inventory
- breaking changes / deprecations / defaults
- linked official references and issues
- official pageで確認できない事項

### Investigation instructions

- `.codex/prompts/investigation.md`、`build-system/AGENTS.md`、`build-system/README.md`、`build-system/agp/README.md`を読む
- Release NotesをEntry Pointとして記録し、Referencesと分ける
- inventory全件にcategory、Deep Dive Yes / No、理由を付ける
- compatibility、migration、API、issue trackerを必要な項目だけdeep diveする
- tools/base sourceは文書だけでは判断できない場合に限る
- Fact / Evidence / Confidenceを対応付ける
- MinimumとRecommendedを分ける
- Change Isolation、Affected Modules、Detection Method、Verification Commands、Test Scope、Rollback Plan、PR Strategyを記載する
- Facts / Observations / Hypotheses / Conclusionsを分ける
- 詳細調査、1ページサマリ、必要なmigration checklistを日本語で作成する
- Human Decision placeholderを残す

生成時は次の見出し構成を使い、`<...>`を補完済みの値へ置換する。該当情報を公式ページから確認できない場合はplaceholderを残さず、`Unknown - verify during investigation`と理由を記録する。

```text
# AGP <from> -> <to> research request

## Research target
- Area: AGP
- Entry Point URL: <official-release-notes-url>
- Page title: <official-page-title>
- Release channel: <stable-or-preview-channel>
- From version: <from-version>
- From version derivation: <user-input-or-existing-research>
- To version: <to-version>
- To version evidence: <official-heading-or-table>
- Target project: <path-or-not-provided>

## Output files
- Detail: <detail-path>
- Summary: <summary-path-or-not-required>
- Migration checklist: <checklist-path-or-not-required>

## Extracted official entry-point facts

### Compatibility requirements
<officially-extracted-compatibility-facts>

### Change inventory
<all-release-note-changes-with-source-context>

### Breaking changes, deprecations, and defaults
<officially-extracted-items-or-none-found>

### Official related links
<official-links-and-issue-links>

### Information not established by the entry point
<unknown-items-to-verify>

## Repository-derived metadata
<baseline-derivation-output-conventions-and-existing-artifact-status>

## Required investigation
<completed-investigation-instructions-from-this-guide>

## Project-specific validation state
<provided-project-context-or-explicit-not-provided-and-not-executed-state>
```

公式ページから抽出したFactとrepositoryから補完したmetadataを分けて記録する。確認できない値を推測で埋めず、調査中に確認できるものは `Unknown - verify during investigation` とする。From versionや出力先を変える不明点だけ人間へ確認する。

中間プロンプトは生成物であり、正式なEvidenceや成果物ではない。Gitの追跡対象に含めない。

## Step 5: 生成プロンプトの検証と実行

生成後に中間ファイルを必ず読み返し、次を検証する。

- Entry Point URLとpage titleが一致する
- To versionとrelease channelが公式ページと一致する
- release channel を page title だけで判定していない
- From versionにderivation sourceがある
- From versionがTo versionより低い
- stableとpreviewが混在していない
- output pathsが同じversion pairを指す
- placeholderが残っていない
- target project未指定の値を実測済みとしていない

問題があれば中間ファイルを修正する。整合性確認後、そのファイルを現在のCodexセッションにおけるauthoritative task specificationとして扱い、同じターンで調査を実行する。

人間へ中間ファイルの再貼付を求めず、別の `codex exec` を再帰的に起動しない。中間ファイル生成だけでは完了ではなく、必要な成果物作成とcompletion criteria確認まで継続する。

## 完了条件

stable AGP version diffは、次をすべて満たした場合に **Research Complete** とする。repository owner が Human Decision を記録した後にのみ **Decision Complete** となる。

- 詳細調査を`build-system/templates/version-diff-template.md`に沿って作成または更新した
- 1ページサマリを`build-system/templates/one-page-summary-template.md`に沿って作成または更新した
- migration checklistを`build-system/templates/migration-checklist-template.md`に沿って作成または更新した
- Entry PointとReferencesを分けた
- Change Inventoryの全項目についてDeep Dive要否と理由を記録した
- compatibility matrix、Minimum / Recommended、breaking changesを記録した
- project未指定または未検証の事項を実測結果と区別した
- rollback plan、test scope、follow-up tasks、PR strategyを記録した
- Human Decision placeholderを残した
- `build-system/AGENTS.md`のCompletion Criteriaを確認した

preview watchはmigration checklistを必須にせず、stableとの差、production判断に使えない不確実性、次回確認条件を記録する。

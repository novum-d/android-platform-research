# Codex プロンプト・ユースケース一覧

この文書は、Android Platform / Build System 調査で Codex に何を依頼できるか、最小入力、作成・更新される成果物、判断上の制約をまとめる。

詳細な調査ルールは次を正とする。

- Android Behavior Change: [CODEX_CLI_RESEARCH_GUIDE.md](CODEX_CLI_RESEARCH_GUIDE.md)
- AGP / Build System: [../../build-system/CODEX_CLI_RESEARCH_GUIDE.md](../../build-system/CODEX_CLI_RESEARCH_GUIDE.md)
- 共通調査手順: [../../.codex/prompts/investigation.md](../../.codex/prompts/investigation.md)

## 早見表

| ID | ユースケース | 最小入力 | 主な成果物 |
| --- | --- | --- | --- |
| UC-01 | Android OS差分調査の項目を作成・更新 | 公式Behavior ChangeセクションURL | 主レポート、1ページ要約、必要な補足資料 |
| UC-02 | AGP差分調査の項目を作成・更新 | 公式AGP Release Notes URL | 詳細調査、1ページサマリ、移行チェックリスト |
| UC-03 | Behavior Changeの実装例を作成・更新 | 主レポートpath | Kotlin / Java / Manifest / XML / native / testの補足資料 |
| UC-04 | 人間の判断をDecision Logへ記録 | 判断、理由、影響、関連ファイル | version固有Decision Log |
| UC-05 | 調査レポートと要約を再レビュー | 主レポートpath | 不足項目を修正したレポートと要約 |
| UC-06 | Android OS間の実行時挙動を比較 | 主レポートpath、比較したいtrigger | OS version behavior comparison |
| UC-07 | 特定アプリへの影響を横断整理 | アプリpathまたは機能・API情報 | app investigation report |
| UC-08 | AOSP gate / compat evidenceを再調査 | 主レポートpath、未解決論点 | evidenceとconfidenceを更新したレポート・要約 |
| UC-09 | 実機・CI・project検証結果を反映 | 成果物path、実行条件、結果 | Expected / Observed、Validation、confidenceの更新 |
| UC-10 | AGP移行チェックリストを実project向けに具体化 | AGP詳細調査path、対象project path | 対象project側の実行用checklistまたはPR / issue記録 |
| UC-11 | AGP preview watchを更新 | 公式preview Release Notes URL | preview watch、stableとの差、次回確認条件 |
| UC-12 | Behavior Changeの概念FAQを作成・更新 | 主レポートpath、読者の質問 | version固有FAQ companion |
| UC-13 | 複数API・実装方式のruntime挙動を比較 | 主レポートpath、比較対象 | runtime behavior comparison |
| UC-14 | このrepositoryの構成をレビュー | review scope、必要なら改善実装の可否 | evidence付き構成レビュー、明示依頼時のみ修正 |
| UC-15 | Pixel Tablet実機でAndroidアプリの回転・window resize影響を検証 | Android project、package、target 35 / 36 build、画面到達手順 | screenshot、logcat、UI hierarchy、system state、code impact |

## 共通ルール

- 既存成果物と同じ調査対象なら、新規ファイルを重複作成せず既存ファイルを更新する。
- URLまたはrepositoryから補完できるversion、tag、category、output path、公式本文を人間へ再入力させない。
- URL-only workflowでは、中間プロンプトを`tmp/research-prompts/`へ生成し、同じCodexセッションで実行する。人間へ再貼付を求めない。
- 公式情報、repositoryから導出したmetadata、観察、仮説、結論を分ける。
- 実行していないtestや実機確認をObservedまたはPassとして記録しない。
- 最終priority、severity、release readiness、customer communication priorityはCodexが決めない。
- Decision Logへ記録する判断は、人間が明示した内容に限る。
- 調査成果物、説明、要約、Decision Logは日本語で作成する。

構成レビューで改善実装も依頼された場合は、`review -> improve -> tests / validator -> re-review`を繰り返す。新しい指摘がなく、未解決事項が外部状態またはHuman Decisionだけになるまで継続し、各周回で見つけた問題を次の検証基準へ反映する。

## UC-01: Android OS差分調査の項目を作成・更新

### 使う場面

公式Behavior Changeの1セクションについて、新しい調査を開始する、または公式文書・AOSP tag更新後に既存調査を更新する。

### 最小プロンプト

```text
https://developer.android.com/about/versions/<version>/behavior-changes-<page>#<section>
```

更新目的を明示する場合:

```text
https://developer.android.com/about/versions/<version>/behavior-changes-<page>#<section>

既存調査があれば、最新の公式本文とAOSP evidenceで更新してください。
```

### Codexの処理

1. 公式セクションを解析する。
2. Android version、AOSP tag、targetSdkVersion、category、output pathを補完する。
3. `tmp/research-prompts/android<version>/...`へ中間プロンプトを生成する。
4. 同一項目の既存成果物を検索し、作成または更新を判断する。
5. 主レポート、1ページ要約、必要な補足資料を作成・更新する。
6. applicability、OS update impact、targetSdkVersion impact、compat evidence、confidenceをレビューする。

### 主な成果物

```text
android<version>/behavior-changes/<all-or-target>/<category>/<topic>.md
android<version>/summaries/<all-or-target>/<category>/<topic>-summary.md
```

## UC-02: AGP差分調査の項目を作成・更新

### 使う場面

公式AGP Release Notesを起点に、stable version diffを作成する、既存差分調査を更新する、または特定のrelease-note項目を既存inventoryへ反映する。

### 最小プロンプト

```text
https://developer.android.com/build/releases/agp-<version>-release-notes
```

特定項目を優先する場合:

```text
https://developer.android.com/build/releases/agp-<version>-release-notes#<section>

この項目を優先して、既存のAGP差分調査を更新してください。
```

### Codexの処理

1. Release Notes全体のchange inventoryを抽出する。
2. To version、release channel、compatibility requirementsを抽出する。page title だけで stable と判定せず、公式 API Reference の Current / Preview 表示などを照合する。
3. 既存調査からFrom versionを一意に補完する。一意に決まらない場合だけ確認する。
4. `tmp/research-prompts/build-system/agp/`へ中間プロンプトを生成する。
5. Release NotesをEntry Pointとして、必要な項目だけCompatibility Matrix、Migration Guide、API Reference、Issue Trackerを深掘りする。
6. stable なら詳細調査、1ページサマリ、移行チェックリストを作成・更新する。preview なら UC-11 の preview watch に routing し、stable 成果物を上書きしない。

### 主な成果物

```text
build-system/agp/versions/agp-<from>-to-<to>.md
build-system/agp/summaries/agp-<from>-to-<to>-summary.md
build-system/agp/checklists/agp-<from>-to-<to>-migration-checklist.md
```

## UC-03: Behavior Changeの実装例を作成・更新

### 使う場面

調査済みBehavior Changeについて、アプリ開発者が対応方法を検討できるよう、移行前後のコード、設定、失敗処理、test例を具体化する。

### プロンプト例

```text
android17/behavior-changes/target/privacy/local-network-permission.md

この主レポートを正として、Kotlin、Manifest、permission denial時の処理、
Android 16 / 17とtargetSdkVersion 36 / 37を分けたtest例を作成または更新してください。
コードは完成品ではなく、対象アプリの既存architectureへ調整して組み込む移行例として記載してください。
```

対象projectがある場合:

```text
android17/behavior-changes/<report>.md を正として、<project-path>の実装方式に合わせた対応例を作成してください。
既存コードは変更せず、検出方法とBefore / After例を補足資料へまとめてください。
コードは完成品ではなく、既存architectureへ調整して組み込む移行例として明記してください。
```

### 制約

- 主レポートのclassification、confidence、AOSP evidenceを再判定しない。
- gate未解決の項目を確定コードとして書かず、検証用pseudocodeと明記する。
- 各コード例は完成品ではなく、対象アプリの既存architectureへ調整して組み込む移行例であると明記する。
- state management、navigation、dependency injection、error policy、lifecycle、threading、test strategyのうち、対象例に関係する調整点を示す。
- 実装例から主レポートと要約へリンクを戻す。

### 主な成果物

- version固有の`implementation-examples-template.md`を使用する。
- Android versionにかかわらず、実装例は`behavior-changes/implementation-examples/`へ置く。`case-guides/`はケース選択、カテゴリ別対応手順、挙動ガイドに限定する。

## UC-04: 人間の判断をDecision Logへ記録

### 使う場面

調査結果を読んだrepository ownerが、着手、保留、分割、追加調査などを判断した後、その判断を追跡可能な形で残す。

### プロンプト例

```text
Android 17のDecision Logに次の人間判断を記録してください。

- 判断: Local Network Permission対応をtargetSdkVersion 37更新PRとは別PRに分ける
- 理由: permission UXと既存LAN discovery機能の回帰試験を独立して実施するため
- 影響: targetSdkVersion更新前に検出と設計を行い、実装時期は別途決定する
- 関連ファイル: android17/behavior-changes/target/privacy/local-network-permission.md
- 判断者: <name>
- 判断日: YYYY-MM-DD
```

### 制約

- Codexは判断内容を補完、変更、強化しない。
- 調査上の推奨候補を、人間が決定した事実として記録しない。
- 判断者、日付、理由など必須情報が不足し、意味が変わる場合は確認する。
- Androidの判断は`android<version>/decisions/`、Build Systemの判断は対象調査またはchecklistのDecision Logへ記録する。

## UC-05: 調査レポートと要約を再レビュー

### 使う場面

既存成果物がcompletion criteriaを満たすか確認し、根拠不足、report / summary不整合、リンク切れ、未解決事項の表現を修正する。

### プロンプト例

```text
android17/behavior-changes/<report>.md と対応するsummaryを再レビューしてください。
REVIEW_CHECKLIST、applicability、AOSP source context、compat evidence、
Expected / Observed、Human Decision placeholderの不足を修正してください。
```

AGPの場合:

```text
build-system/agp/versions/<report>.md とsummary、migration checklistを再レビューしてください。
Change Inventory、Compatibility Matrix、Minimum / Recommended、Rollback Plan、PR Strategyの整合性を修正してください。
```

## UC-06: Android OS間の実行時挙動を比較

### 使う場面

同じapp build、初期状態、triggerについて、baseline OSとtarget OSのstate transitionやapp-visible signalを並べて説明する必要がある。

### プロンプト例

```text
android17/behavior-changes/<report>.md を正として、
「<initial-state>で<trigger>を実行した時」のAndroid 16 / 17挙動比較を作成してください。
同一app buildを使い、OS差とtargetSdkVersion差、system behaviorとcallback / broadcast / UIを分けてください。
```

### 成果物

- [android-os-version-behavior-comparison-template.md](../templates/android-os-version-behavior-comparison-template.md)を使う。
- 未実施の観察は`未検証`とし、ExpectedとObservedを分ける。
- 主レポートと1ページ要約へ相互リンクする。

## UC-07: 特定アプリへの影響を横断整理

### 使う場面

複数のBehavior Changeを、特定アプリの機能、API、permission、manifest、background処理、device条件に照らして絞り込む。

### プロンプト例

```text
<project-path>を対象にAndroid 17 Behavior Changesの影響を横断調査してください。
OS updateだけの影響とtargetSdkVersion 37更新の影響を分け、
関連する既存主レポートを正としてapp investigation reportを作成してください。
```

projectを渡せない場合:

```text
次のアプリ特性を対象にAndroid 17の影響を整理してください。
- Bluetooth RFCOMMを使用
- background audioを使用
- targetSdkVersion 36
- large screen対応あり
```

### 制約

- 個別Behavior Changeのclassificationとconfidenceは主レポートを正とする。
- project未提供ならコード確認済みと記録しない。
- 最終priorityやrelease readinessは決めない。

## UC-08: AOSP gate / compat evidenceを再調査

### 使う場面

公式文書は確認済みだが、targetSdkVersion gate、Change ID、default state、caller、module境界などが未解決でconfidenceを上げられない。

### プロンプト例

```text
android17/behavior-changes/<report>.md の未解決evidenceを再調査してください。
特に@ChangeId、@EnabledAfter、@EnabledSince、CompatChanges.isChangeEnabled、
entry point / callerを確認し、見つからない場合は検索pathとqueryを記録してください。
reportとsummaryのconfidenceを根拠に合わせて更新してください。
```

### 制約

- 公式Behavior Change statementから調査を再開し、source diffだけから新しいBehavior Changeを作らない。
- 見つからないevidenceを「存在しない」と断定せず、検索範囲を記録する。

## UC-09: 実機・CI・project検証結果を反映

### 使う場面

調査時にExpectedのみだった項目へ、実機、emulator、sample project、production project、CIの実行結果を追加する。

### プロンプト例

```text
android17/behavior-changes/<report>.md に次の検証結果を反映してください。

- Device / image: <value>
- App build / targetSdkVersion: <value>
- Initial state: <value>
- Trigger: <value>
- Expected: <value>
- Observed: <value>
- Logs / artifact: <path-or-link>

Facts、Observed、Conclusionsを分け、summaryも必要な範囲だけ更新してください。
```

AGP / CIの場合:

```text
build-system/agp/versions/<report>.md と汎用checklistを根拠として、<project-path>側の実行用checklistまたはPR / issue記録に
<commands>の結果を反映してください。汎用checklistへproject固有の実績を混ぜず、未実行commandは未実行のまま残してください。
```

## UC-10: AGP移行チェックリストを実project向けに具体化

### 使う場面

repository-wideなAGP差分調査を、実際のproject module、Gradle設定、JDK、CI、native build、release buildへ適用する。

### プロンプト例

```text
build-system/agp/versions/agp-<from>-to-<to>.md と
build-system/agp/checklists/agp-<from>-to-<to>-migration-checklist.md を正として、
<project-path>側に実行用migration checklistを作成または更新してください。
現在version、affected modules、検出command、変更候補、verification、rollbackをprojectから確認してください。
このrepositoryの汎用checklistにはproject固有の実行結果を混ぜず、実装変更は行わないでください。
```

### 制約

- AGP、Gradle、Kotlin、compileSdk、targetSdkVersion、NDK、依存更新を必要なく同じPRへ混ぜない。
- commandを実行していない場合は候補と実績を分ける。
- project固有のcommand result、対象module、実変更、Human Decisionは対象project側へ記録する。
- このrepositoryの汎用checklistは、複数projectに再利用できる手順が変わる場合だけ更新する。
- upgrade実装まで依頼された場合だけproject filesを変更する。

## UC-11: AGP preview watchを更新

### 使う場面

新しいalpha、beta、rc公開後に、stable migration targetと分離したまま先行変更と不確実性を更新する。

### 最小プロンプト

```text
https://developer.android.com/build/releases/agp-<preview-version>-release-notes
```

### 制約

- previewをproductionのRecommended versionにしない。
- stable baselineとの差、変更されたcompatibility条件、削除・追加された項目、stable昇格後の再確認条件を記録する。
- preview watchではstable用migration checklistを作らない。

## UC-12: Behavior Changeの概念FAQを作成・更新

### 使う場面

用語、前提、処理経路、適用条件、よくある誤解を複数の質問と回答に分けた方が、主レポートより理解しやすい場合に使う。

### プロンプト例

```text
android16/behavior-changes/<report>.md を正として、次の読者質問を整理したFAQを作成または更新してください。

- <question-1>
- <question-2>
- <question-3>

主レポートのclassification、confidence、evidence、Human Decisionを再判定せず、各回答から根拠箇所へリンクしてください。
```

### 制約

- version固有のFAQ templateが存在する場合だけ独立したFAQ companionを作成する。
- 主レポート内へ複数質問の長いFAQを埋め込まない。
- FAQを主レポートの代替にせず、classification、confidence、evidence、Human Decisionは主レポートを正とする。
- 回答できない質問は推測せず、未確認事項と次の確認方法を記載する。

## UC-13: 複数API・実装方式のruntime挙動を比較

### 使う場面

複数APIまたは実装方式について、実行時刻、callback選択順、fallback、遅延実行、lifecycle復帰後の差をside-by-sideで説明する必要がある。

### プロンプト例

```text
android16/behavior-changes/<report>.md を正として、<API-or-pattern-A>と<API-or-pattern-B>のruntime挙動比較を作成してください。
共通初期状態、trigger、timeline、callback順、fallback、process / lifecycle条件、Expected / Observedを分けてください。
```

### 制約

- version固有の`runtime-behavior-comparison-template.md`がある場合に使用する。
- OS version間の差が主題ならUC-06を使い、API・実装方式の差と混ぜない。
- primary reportのapplicabilityやevidenceを比較資料側で再判定しない。
- 未実施結果をObservedとして記録しない。

## UC-14: このrepositoryの構成をレビュー

### 使う場面

調査を追加する前後やversion追加時に、repositoryの入口、instruction hierarchy、directory配置、source of truth、templateと成果物の対応、索引、内部リンク、生成物の扱いが一貫しているか確認する。

通常はread-onlyのレビューとして実行する。レビュー依頼だけではファイル修正、成果物移動、削除、commit、pushを行わない。「レビューして改善まで実施」と明示された場合だけ、指摘内容に沿った変更を行う。

### 最小プロンプト

```text
このrepositoryの構成をレビューしてください。
ファイルは変更せず、構成上の問題、根拠、影響、改善候補を日本語で報告してください。
```

Android PlatformとBuild Systemの境界を重点確認する場合:

```text
このrepositoryの構成をレビューしてください。
特にAndroid version固有情報とBuild System調査の分離、AGENTS.mdのinstruction hierarchy、
source of truthの重複、Codex URL-only workflow、templateと成果物pathの整合性を確認してください。
変更は行わないでください。
```

レビュー後の改善まで依頼する場合:

```text
このrepositoryの構成をレビューし、根拠が明確な構成・導線・リンク・instruction不整合を改善してください。
既存の調査内容とdocs/notes/PERSONAL_NOTES.mdは変更せず、mainへcommit・pushしてください。
判断が必要な再編、成果物移動、削除は実行せず、候補として報告してください。
```

### 必須確認項目

| 観点 | 確認内容 |
| --- | --- |
| Entry points | root README、docs、version directory、Build Systemから目的の手順・成果物へ到達できるか |
| Instruction hierarchy | root / version / Build SystemのAGENTS.mdに重複、矛盾、scope漏れがないか |
| Source of truth | version、AOSP tag、targetSdkVersion、classification、workflow、template pathが複数箇所で食い違っていないか |
| Directory ownership | version固有成果物、共通workflow、Build System、demo、temporary evidenceの配置が方針どおりか |
| Templates and outputs | 必須成果物にtemplateがあり、既存成果物と保存先conventionが対応しているか |
| Index coverage | 作成済みreport、summary、comparison、example、checklistがREADMEやindexから参照されているか |
| Prompt workflows | Android / AGP URL-only workflow、中間プロンプト、ユースケース一覧が入口から発見できるか |
| Links | repository内Markdown link、相互link、古いpath参照に問題がないか |
| Generated files | `frameworks-base/`、`tmp/`、中間プロンプトなどが正式成果物やGit追跡対象と混ざっていないか |
| Naming and placeholders | filename、category slug、version表記、古いTBDやplaceholderが現行scopeと矛盾していないか |
| Duplication and maintenance | 同じ規則やmetadataの重複が将来の更新漏れを起こしやすくしていないか |
| Protected content | `docs/notes/PERSONAL_NOTES.md`を編集対象または正式なsource of truthとして扱っていないか |

### レビュー手順

1. branchとworking treeを確認し、既存の未commit変更をユーザーの変更として保護する。
2. root、対象scope、下位directoryのAGENTS.mdを確認する。
3. `README.md`、`GETTING_STARTED.md`、workflow guide、template、indexの導線をたどる。
4. `rg --files`と`rg`を使い、未索引成果物、古いpath、重複metadata、placeholder候補を確認する。
5. findingごとにFact、Evidence、Impact、Recommendationを分ける。
6. 問題が見つからない観点も、確認範囲とともに記録する。
7. read-only依頼なら報告して終了する。改善依頼なら、安全でscope内の変更だけを実施・検証する。

### 出力フォーマット

```text
## Review scope
- 確認したdirectory / entry point
- 確認対象外

## Findings
| Finding | Evidence | Impact | Recommendation |

## Confirmed consistent areas
- 問題が見つからなかった観点と確認範囲

## Proposed changes requiring human decision
- 成果物移動、削除、大規模再編、source of truth変更など

## Validation
- 実行したread-only check
- 変更を行った場合だけ、変更後checkとGit状態
```

### 制約

- 構成レビューをBehavior ChangeやAGPの内容再調査へ広げない。内容の正確性は、構成矛盾の確認に必要な範囲だけ扱う。
- final priority、final severity、release readinessを決めず、影響と改善候補を提示する。
- review findingに実ファイルpath、見出し、検索結果などの根拠を付ける。
- protected noteの内容をレビュー材料として読み込んだり、編集したりしない。
- unrelatedな既存変更を修正、整形、commitしない。
- ファイル移動、削除、大規模なdirectory再編は、改善依頼に含まれていても人間の明示判断なしに実行しない。

## UC-15: Pixel Tablet実機でAndroidアプリの回転・window resize影響を検証

### 使う場面

Android 16 Adaptive layoutsの影響を受けるAndroidアプリについて、Pixel Tablet実機でtargetSdkVersion 35 / 36、全画面、分割画面、回転を比較し、画面到達と属性依存branchの実行を再確認可能な証跡として保存する。業務領域や機能種別に依存しない汎用プロンプトとして使用する。

これはUC-09の前段にあたる。UC-15は実機操作とevidence bundleの収集を担当し、UC-09は確認済みObservedを主レポートやapp reportへ反映する。

### 実行用プロンプト

[Pixel Tabletアプリ回転・window resize検証プロンプト](../../.codex/prompts/verify-app-rotation-on-pixel-tablet.md)を使う。

最小入力:

```text
- Android project: <android-project-path>
- Package name: <package-name>
- targetSdkVersion 35 build command or APK: <value>
- targetSdkVersion 36 build command or APK: <value>
- Known affected screens and entry steps: <value>
- Evidence output root: <path>

.codex/prompts/verify-app-rotation-on-pixel-tablet.md に従って、
Pixel Tablet実機 / Android 16で画面回転とmulti-window影響を検証してください。
```

### 必須確認項目

- 接続端末が物理実機のPixel Tablet、Android 16 / API 36であること。
- target 35 / 36 APKが同じsource baselineから作られ、targetSdkVersionを端末上でも確認できること。
- manifest、runtime orientation API、Configuration、WindowMetrics、multi-window、resource qualifier、window size breakpointの利用箇所。
- 取得・設定した属性を使うbranchと、その下流のlayout、resource選択、navigation、rendering、入力受付、state restorationへの影響。
- target 35 / 36 defaultと、compat change force-enable / force-disableによるBehavior Change単体の分離。
- full-screen、split-screen wide / narrow、split中のrotation / resize、full-screen復帰。
- destination側marker、top / resumed state、UI hierarchy、視認済みscreenshotの一致。
- secure / protected surface、UI hierarchy取得不能、ADB logical rotationと物理回転の差。
- rotation、compat override、window stateのcleanup。

### 主な成果物

```text
<evidence-output-root>/<run-id>/
├── INDEX.md
├── code-impact.md
├── visual-comparison.md
├── SHA256SUMS
├── cleanup.md
└── <case-id>/
    ├── metadata.txt
    ├── commands.txt
    ├── logcat.txt
    ├── activity.txt
    ├── window.txt
    ├── display.txt
    ├── layout.json
    ├── screenshot.png
    └── visual-review.md
```

### 制約

- emulatorをPixel Tablet実機のObservedとして代用しない。
- `wm size`によるdisplay overrideをmulti-windowの代用にしない。
- rotation command成功だけでportrait / landscapeを判定しない。
- single-Activity appでActivity名だけを画面到達証拠にしない。
- appログだけでPassにせず、system state、UI hierarchy、screenshotと照合する。
- production / release behaviorへ検証ログを追加しない。
- secure表示を回避しない。capture不能はBlockedとして代替候補を示す。
- target projectまたは調査レポートへObservedを反映するのは、証跡確認後に明示依頼された場合だけとする。

## ユースケース選択の目安

```text
公式URLから新しい調査を始める
  -> AndroidならUC-01、AGPならUC-02またはUC-11

調査済み項目を開発作業へ落とす
  -> Android実装例ならUC-03、AGP project適用ならUC-10

読者向けの補足資料を作る
  -> 概念整理はUC-12、複数API / callback比較はUC-13

根拠または品質を補強する
  -> 全体レビューはUC-05、AOSP / compat再調査はUC-08、実機証跡収集はUC-15、実測反映はUC-09

複数条件や対象を横断して説明する
  -> OS間比較はUC-06、特定アプリ影響はUC-07

人間の最終判断を保存する
  -> UC-04

repository全体の運用・配置・導線を確認する
  -> UC-14
```

## 一覧へ追加する基準

新しいユースケースは、次のいずれかを満たす場合に追加する。

- 独立した成果物templateまたは保存先がある。
- 通常調査と異なる入力条件、evidence、completion criteriaがある。
- Human Decision、Observed、previewなど、誤って事実化すると危険な境界がある。
- 複数回利用する定型依頼である。

単発の言い換えや、既存ユースケースの追加観点だけなら新しいIDを作らず、該当ユースケースのプロンプト例へ追加する。

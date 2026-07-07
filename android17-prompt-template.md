# Android 17 Behavior Change 調査依頼テンプレート

`docs/workflow/CODEX_CLI_RESEARCH_GUIDE.md` の固定調査指示に従って、この Behavior Change 1件を end-to-end で調査してください。

複雑な項目、サブセクション、例外、opt-in / opt-out、将来 release plan を扱う場合は、下の詳細入力項目を埋めてください。単純な項目では、空欄を削って最小入力として使って構いません。

## 調査対象

Android version: Android 17

Version directory: android17

From tag: android-16.0.0_r4

To tag: TBD: Android 17 AOSP tag

Previous targetSdkVersion: 36

Target targetSdkVersion: 37

Behavior Change section title: <公式ドキュメント上のセクション名>

Official documentation URL: <公式ドキュメントURL>

Official documentation category: <Core functionality / Accessibility / Privacy / Security / Media / ...>

Report output file: android17/behavior-changes/<all-or-target>/<official-category-slug>/<topic-slug>.md

Summary output file: android17/summaries/<all-or-target>/<official-category-slug>/<topic-slug>-summary.md

## 公式ドキュメント抜粋

Page title: <ページタイトル>

Page URL: <公式ドキュメントURL>

Page type: all apps / apps targeting Android 17 / compat framework changes

Page category: <公式ドキュメント上のカテゴリ名>

Parent section title: <親セクション名。なければ削除>

Section title: <セクション名>

Subsections:
- <サブセクション名。なければ削除>

Original statements to verify:

"<検証対象の公式 statement 1>"

"<検証対象の公式 statement 2>"


Applicability details:

Applies to <OS / targetSdkVersion / permission / API / device / app state conditions>.

Potentially affects apps that:
- <影響対象アプリ/API/pattern 1>
- <影響対象アプリ/API/pattern 2>

The investigation must separate:
- Android 17 OS behavior for targetSdkVersion 36 apps
- Android 17 OS behavior for targetSdkVersion 37 apps
- Android 16 OS behavior for targetSdkVersion 37 apps, if relevant and technically possible
- <追加で分けるべき scenario>


Related links:

<公式文書URL>

<API reference URL>

<compat framework URL>


Additional notes:

初期分類仮説は <classification hypothesis>。

ただし、利用可能な分類ラベルは android17/behavior-changes/APPLICABILITY_CLASSIFICATION.md に従うこと。

調査開始時に Official documentation URL の該当セクションを再確認し、Original statements / Applicability details が最新の公式本文と一致しているか確認する。差分があれば report に記録する。

AOSP では少なくとも以下を確認する:
- <required AOSP evidence 1>
- <required AOSP evidence 2>
- <required AOSP evidence 3>

Android 17 / targetSdkVersion 36、Android 17 / targetSdkVersion 37、Android 16 / targetSdkVersion 37 の期待挙動マトリクスを必ず作る。

さらに以下のマトリクスを必ず作る:
- <detailed matrix row 1>
- <detailed matrix row 2>

顧客向け説明では「Android 17 へ OS アップデートしただけの影響」と「targetSdkVersion 37 化した時の影響」を混ぜない。

影響対象は以下のアプリ種別に分けて書く:
- <app type 1>
- <app type 2>

テスト観点として以下を明示する:
- <test focus 1>
- <test focus 2>

調査結果では Facts / Observations / Hypotheses / Conclusions を分ける。

Report と Summary は日本語で作成する。

One page summary には Human decision placeholder を必ず残す。

## 最小入力にする場合

Original text:

```text
<ここに公式ドキュメントの該当セクション本文を貼る>
```

Additional notes:

```text
<追加条件、例外、opt-out、移行方法、関連リンクがあれば貼る。なければ「なし」。>
```

## 任意メモ

- <調査時に特に確認してほしい観点があれば書く>

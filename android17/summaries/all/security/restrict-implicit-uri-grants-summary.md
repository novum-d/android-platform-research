# Restrict implicit URI grants - 1ページ要約（One Page Summary）

## 対象（Target）

Android 17 Behavior Change

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP tag

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

## 適用条件（Applicability）

- 主分類（Primary classification）: UNKNOWN_NEEDS_MORE_EVIDENCE
- OS アップデート / 全アプリ（OS update / all apps）: All apps ページに掲載。ただし本文の enforcement は Android 18 starting と説明されており、Android 17 では検出 / migration guidance と読める。
- targetSdkVersion 37 以上: 公式文書上、この項目に targetSdkVersion 37 条件はない。AOSP gate 未確認。
- その他の必須条件（Other required conditions）: URI を含む `ACTION_SEND`、`ACTION_SEND_MULTIPLE`、`ACTION_IMAGE_CAPTURE` intent を使い、system の implicit URI grant に依存していること。
- Compat Change ID: Unknown
- Compat default state: Unknown

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 公式文書上、即時 enforcement は未確認。StrictMode / logcat で implicit grant 依存を検出する段階。 |
| Android 17 / targetSdkVersion 37 | targetSdkVersion 36 と同様。targetSdkVersion 37 gate は公式文書上確認できない。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | URI 付き share / capture intent では explicit grant flags を追加すべき。Android 18 enforcement に備える。 |

## 要約（Summary）

Android 17 の all apps ページは、URI 付き `ACTION_SEND`、`ACTION_SEND_MULTIPLE`、`ACTION_IMAGE_CAPTURE` に対する implicit URI permission grants の将来制限を案内している。自動 grant 停止は Android 18 starting と説明されており、Android 17 では StrictMode / logcat で検出し、explicit grant flag へ移行する準備項目として扱う。

## 顧客影響（Customer Impact）

- 要確認

## 影響対象（Who Is Affected）

- 対象アプリ: content URI を他アプリへ共有するアプリ、camera app に output URI を渡すアプリ。
- 対象機能: share sheet、画像 / document 共有、camera capture、添付ファイル送信。
- 対象条件: URI 付き intent に `FLAG_GRANT_READ_URI_PERMISSION` / `FLAG_GRANT_WRITE_URI_PERMISSION` を明示していない場合。

## 対応要否（Required Action）

- 必須対応: URI 付き `ACTION_SEND`、`ACTION_SEND_MULTIPLE`、`ACTION_IMAGE_CAPTURE` の call site を棚卸しする。
- 推奨対応: `ACTION_SEND` / `ACTION_SEND_MULTIPLE` には read grant、`ACTION_IMAGE_CAPTURE` には read / write grant を明示する。
- 不要: URI を他アプリへ渡さないアプリ、または grant flags をすでに明示している flow では直接影響は限定的。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 16 | 36 | baseline。implicit grant により target app が URI を読めるか確認。 |
| Android 17 | 36 | 即時 enforcement は未確認。StrictMode / logcat で検出できるか確認。 |
| Android 17 | 37 | targetSdkVersion 37 による差分がないか確認。公式文書上は targetSdkVersion gate なし。 |

## 顧客向け説明（Explanation for Customers）

Android 17 の文書では、URI を含む `ACTION_SEND`、`ACTION_SEND_MULTIPLE`、`ACTION_IMAGE_CAPTURE` intent に対して system が暗黙に read / write URI permissions を付与する挙動が、Android 18 から廃止される予定だと説明されています。Android 17 で直ちに share / camera flow が壊れる変更とは公式文書上確認できませんが、Android 17 のうちに StrictMode や logcat で依存箇所を検出し、明示的な grant flag を追加することが推奨されます。

`ACTION_SEND` と `ACTION_SEND_MULTIPLE` では `FLAG_GRANT_READ_URI_PERMISSION` を付けます。`ACTION_IMAGE_CAPTURE` では camera app が output URI に書き込めるよう、`FLAG_GRANT_READ_URI_PERMISSION` と `FLAG_GRANT_WRITE_URI_PERMISSION` の両方を付けます。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-all
- Original statement: Android 18 starting で system は URI 付き `ACTION_SEND` / `ACTION_SEND_MULTIPLE` / `ACTION_IMAGE_CAPTURE` に対する read / write URI permissions を自動 grant しなくなる。Android 17 では StrictMode / logcat による検出と explicit grant flag への移行が案内されている。
- AOSP files: 未確認。local `frameworks-base` に `android-17*` tag がない。
- AOSP source context: 未確認。tag 間 diff が実行できない。
- Diff interpretation: 未分類。公式文書上は Android 17 immediate enforcement ではなく Android 18 advance warning / migration guidance と読めるが、AOSP diff による確認は Android 17 tag 待ち。
- Gate conclusion: Unknown。公式文書上は targetSdkVersion 37 gate なし、Android 18 enforcement + Android 17 detection guidance。runtime gate / compat framework evidence は未取得。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Human decision required

判断（Decision）:
- Further investigation required after Android 17 AOSP tag is available

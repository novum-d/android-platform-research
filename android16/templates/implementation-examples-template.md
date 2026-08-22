# [Behavior Change Title] - 実装例（Implementation Examples）

## 位置づけ（Scope）

このファイルは、Behavior Change 調査レポートの対応候補を補足する実装例である。
根拠、適用条件、classification、confidence、Human Decision は primary report / one-page summary を正とする。

Primary report:
- `<relative path>`

One-page summary:
- `<relative path>`

Runtime behavior comparison, if applicable:
- `<relative path>`

## 対象（Target）

Android 16 Behavior Change:
- Document: `<URL>`
- Section: `<Section Name>`

適用条件の要点:
- OS アップデート / 全アプリ:
- targetSdkVersion 36 以上:
- その他の必須条件:

## 使い方（How to Use）

- primary report の「対応候補」には、代表的な短いコード例とこのファイルへのリンクだけを置く。
- フレームワーク別、画面別、テスト補助用など複数パターンの実装例はこのファイルに集約する。
- 掲載するコードはそのまま貼り付けて使う完成品ではなく、対象アプリの既存architectureへ調整して組み込む移行例として扱う。
- state management、navigation、dependency injection、error policy、lifecycle、threading、test strategyのうち、各例に関係する調整点を明記する。
- 各例は「既存実装で探す箇所」「移行前」「移行後」「移行手順」「確認観点」をセットで書く。
- opt-out 例を載せる場合は、一時対応であること、適用範囲、削除条件、リスクを明記する。

## 対応方針（Implementation Strategy）

推奨方針:
- `<supported API / recommended pattern>`

一時対応:
- `<temporary opt-out / compatibility workaround>`

避けるべき方針:
- `<legacy API / risky workaround>`

## 移行対象の見つけ方（Finding Existing Code）

探すコード:
- `<legacy API / manifest / config / behavior pattern>`

```bash
# Example search command
```

分類:

| 既存実装（Existing pattern） | 移行先（Migration target） | 優先度 | Notes |
| --- | --- | --- | --- |
| `<legacy pattern>` | `<recommended API / pattern>` | Must / Recommended / Optional | `<why>` |

## 移行マップ（Migration Map）

| Before | After | 目的 |
| --- | --- | --- |
| `<existing implementation>` | `<new implementation>` | `<what changes>` |
| `<temporary workaround>` | `<planned final state>` | `<when to remove>` |

## 例 1: [Scenario]

目的:
- `<what this example demonstrates>`

既存実装で探す箇所:
- `<what to search in current code>`

移行前:

```kotlin
// Before
```

移行後:

```kotlin
// After
```

移行手順:
1. `<step>`
2. `<step>`
3. `<step>`

既存architectureへの調整点:
- `<state management / navigation / dependency injection / error policy / lifecycle / threading / test strategy>`

確認観点:
- `<how to verify this migration>`

注意点:
- `<caveat>`

## 例 2: [Scenario]

目的:
- `<what this example demonstrates>`

既存実装で探す箇所:
- `<what to search in current code>`

移行前:

```xml
<!-- Before -->
```

移行後:

```xml
<!-- After -->
```

移行手順:
1. `<step>`
2. `<step>`
3. `<step>`

既存architectureへの調整点:
- `<state management / navigation / dependency injection / error policy / lifecycle / threading / test strategy>`

確認観点:
- `<how to verify this migration>`

注意点:
- `<caveat>`

## テスト観点（Verification）

- Android 16 / targetSdkVersion 35
- Android 16 / targetSdkVersion 36
- Android 16 / targetSdkVersion 36 + implementation change
- Android 16 / targetSdkVersion 36 + temporary opt-out, if applicable

## References

- `<Official documentation URL>`
- `<API reference URL>`

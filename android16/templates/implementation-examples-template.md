# [Behavior Change Title] - 実装例（Implementation Examples）

## 位置づけ（Scope）

このファイルは、Behavior Change 調査レポートの対応候補を補足する実装例である。
根拠、適用条件、classification、confidence、Human Decision は primary report / one-page summary を正とする。

Primary report:
- `<relative path>`

One-page summary:
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
- 実装例はそのまま貼り付ける完成コードではなく、移行方針を具体化するためのサンプルとして扱う。
- opt-out 例を載せる場合は、一時対応であること、適用範囲、削除条件、リスクを明記する。

## 対応方針（Implementation Strategy）

推奨方針:
- `<supported API / recommended pattern>`

一時対応:
- `<temporary opt-out / compatibility workaround>`

避けるべき方針:
- `<legacy API / risky workaround>`

## 例 1: [Scenario]

目的:
- `<what this example demonstrates>`

```kotlin
// Example code
```

注意点:
- `<caveat>`

## 例 2: [Scenario]

目的:
- `<what this example demonstrates>`

```xml
<!-- Example manifest or resources -->
```

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

# 情報源（Sources）

Android Platform調査とBuild System調査では、entry pointと証拠の役割が異なる。
具体的な優先順位の正本はルート[`AGENTS.md`](../../AGENTS.md#evidence-hierarchy)とし、
このページでは読み分けだけを示す。

## Android Platform Behavior Changes

公式Behavior Change文書から調査項目を特定し、AOSP source codeとAPI surfaceで
statementを検証する。Android公式文書・release notes・外部記事は、実装根拠の
文脈説明と補助に使う。

```text
Behavior Change Documentation（調査入口）
-> AOSP source / API surface（実装検証）
-> 顧客向け結論
```

公式文書とAOSP gateがずれる場合は差分を明記し、High confidenceにしない。

## Build System

Release Notesをentry pointとしてchange inventoryを作成し、影響候補だけを公式文書、
Compatibility Matrix、API Reference / Migration Guide、Issue Tracker、実機・
実プロジェクト検証へ深掘りする。Release Notesの要約だけを最終根拠にしない。

詳細は[`build-system/AGENTS.md`](../../build-system/AGENTS.md#evidence-hierarchy)を参照する。

## External Context

Android Developers Blog、公式conference session、AOSP commentは補助根拠として使える。
Vendor blog、community article、forum post、social mediaは参考情報に留め、これらだけで
Behavior ChangeまたはBuild System互換性の結論を出さない。

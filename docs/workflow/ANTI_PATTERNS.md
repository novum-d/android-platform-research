# Anti Patterns

このファイルは、Android Behavior Change 調査で避けるべき進め方と、その理由を記録するためのものです。

## AP-001: Source code first

AOSP差分から調査を開始する。

Reason:
Behavior Changes の文脈から外れやすい。

## AP-002: Release note only

公式ドキュメントだけで結論を出す。

Reason:
実装差分で裏取りできていない。

## AP-003: Internal refactor deep dive

アプリ開発者への影響がない内部リファクタリングを深追いする。

Reason:
顧客説明向けの価値が低い。

## AP-004: AI final severity decision

Codexに最終重要度を決めさせる。

Reason:
最終判断は人間が行う。

## AP-005: Mixing OS update and targetSdk impact

OSアップデートで自動適用される変更と、targetSdkVersion 更新で有効になる変更を同じ影響として説明する。

Reason:
顧客の対応判断が誤る。OS update / all apps と targetSdkVersion update は必ず分けて説明する。

## AP-006: High confidence without applicability gate

AOSP の targetSdkVersion gate、compat framework default state、または gate が存在しないことを確認せずに High confidence とする。

Reason:
公式ドキュメントの分類と実装上の適用条件がずれる可能性がある。

## AP-007: Ignoring conditional applicability

large screen、permission、API usage、manifest property、process lifecycle などの追加条件を確認せず、全アプリまたは targetSdkVersion 更新全体の影響として説明する。

Reason:
実際には一部の端末・機能・利用パターンだけに影響する変更を過大評価する。

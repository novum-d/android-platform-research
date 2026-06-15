# 避けるべき進め方（Anti Patterns）

このファイルは、Android Behavior Change 調査で避けるべき進め方と、その理由を記録するためのものです。

## AP-001: Source code first（ソースコードから始める）

AOSP差分から調査を開始する。

理由:
Behavior Changes の文脈から外れやすい。

## AP-002: Release note only（リリースノートだけで結論を出す）

公式ドキュメントだけで結論を出す。

理由:
実装差分で裏取りできていない。

## AP-003: Internal refactor deep dive（内部リファクタリングを深追いする）

アプリ開発者への影響がない内部リファクタリングを深追いする。

理由:
顧客説明向けの価値が低い。

## AP-004: AI final severity decision（AI が最終重要度を決める）

Codexに最終重要度を決めさせる。

理由:
最終判断は人間が行う。

## AP-005: Mixing OS update and targetSdk impact（OS update 影響と targetSdkVersion 影響を混ぜる）

OSアップデートで自動適用される変更と、targetSdkVersion 更新で有効になる変更を同じ影響として説明する。

理由:
顧客の対応判断が誤る。OS update / all apps と targetSdkVersion update は必ず分けて説明する。

例:
- Android 17 にアップデートしただけで発生する影響と、targetSdkVersion 37 化で初めて発生する影響を同じ表現で説明する。

## AP-006: High confidence without applicability gate（適用ゲート未確認で High confidence にする）

AOSP の targetSdkVersion gate、compat framework default state、または gate が存在しないことを確認せずに High confidence とする。

理由:
公式ドキュメントの分類と実装上の適用条件がずれる可能性がある。

例:
- Android 17 AOSP tag がなく targetSdkVersion gate を確認できないのに、High confidence とする。

## AP-007: Ignoring conditional applicability（追加条件を無視する）

large screen、permission、API usage、manifest property、process lifecycle などの追加条件を確認せず、全アプリまたは targetSdkVersion 更新全体の影響として説明する。

理由:
実際には一部の端末・機能・利用パターンだけに影響する変更を過大評価する。

例:
- large screen のみの変更を、すべての smartphone app に影響するように説明する。
- 特定 API を呼ぶ場合だけの変更を、アプリ全体の互換性リスクとして説明する。

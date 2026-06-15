# 情報源（Sources）

このファイルは、調査で参照する情報源の優先順位と、根拠として扱う際の信頼度を整理するためのものです。

## Tier 1: 最優先根拠（Source of Truth）

- AOSP source code
- API surface files such as `current.txt`
- Android official documentation
- Android release notes

## Tier 2: 補助根拠

- Android Developers Blog
- Google I/O sessions
- Android source comments

## Tier 3: 参考情報

- External blogs
- Reddit
- Medium
- Personal notes

## ルール（Rule）

Tier 1 と矛盾する場合は Tier 1 を優先する。

利用例:
- AOSP source と外部 blog が矛盾する場合は、AOSP source を採用する。
- 公式ドキュメントと AOSP gate がずれる場合は、差分を明記し、High confidence にしない。

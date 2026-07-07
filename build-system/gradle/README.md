# Gradle 調査

Gradle wrapper、Gradle runtime、configuration cache、plugin resolution、dependency resolution、build cache、CI 実行環境への影響を調査する。

## Scope

- Gradle version update
- Gradle と AGP / JDK / Kotlin の互換性
- Gradle wrapper 更新
- configuration cache / build cache 影響
- dependency resolution 変更
- CI image / cache / daemon 設定への影響

## Out of Scope

- AGP 更新そのもの
- Kotlin 更新そのもの
- 任意の依存ライブラリ更新

互換性上同時更新が必要な場合だけ、根拠を記録して例外扱いにする。

## Directory

| Directory | Purpose |
| --- | --- |
| [versions/](versions/) | Gradle 更新の詳細調査 |
| [summaries/](summaries/) | Gradle 更新の 1ページサマリ |

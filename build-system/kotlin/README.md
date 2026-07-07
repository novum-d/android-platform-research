# Kotlin 調査

Kotlin Gradle Plugin、Kotlin language / compiler、stdlib、JVM target、Android build への影響を調査する。

## Scope

- Kotlin version update
- Kotlin と AGP / Gradle / JDK / Compose Compiler / KSP の互換性
- compiler option 変更
- language behavior 変更
- warnings / errors の変化
- test / lint / CI への影響

## Out of Scope

- AGP 更新そのもの
- Gradle 更新そのもの
- Compose Compiler 更新そのもの
- KSP 更新そのもの

互換性上同時更新が必要な場合だけ、根拠を記録して例外扱いにする。

## Directory

| Directory | Purpose |
| --- | --- |
| [versions/](versions/) | Kotlin 更新の詳細調査 |
| [summaries/](summaries/) | Kotlin 更新の 1ページサマリ |

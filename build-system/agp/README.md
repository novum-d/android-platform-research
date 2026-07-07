# AGP 調査

Android Gradle Plugin (AGP) の version update、DSL 変更、variant API、lint、R8、resource processing、namespace、build feature、release artifact への影響を調査する。

## Scope

- AGP version update
- AGP と Gradle / JDK / Kotlin / compileSdk の互換性
- Android Gradle Plugin DSL 変更
- Variant API 変更
- Lint / R8 / resource processing の挙動変更
- AGP 更新に伴う CI 影響

## Out of Scope

- `targetSdkVersion` 更新そのもの
- `minSdk` 更新そのもの
- 任意の依存ライブラリ更新

これらは AGP 更新と同じ PR に混ぜない。ただし AGP 互換性上必須の場合は、根拠を記録する。

## Directory

| Directory | Purpose |
| --- | --- |
| [versions/](versions/) | AGP 更新の詳細調査 |
| [summaries/](summaries/) | AGP 更新の 1ページサマリ |

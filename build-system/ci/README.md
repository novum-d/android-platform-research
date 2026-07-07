# CI 調査

Build System 更新に伴う CI 環境、runner、JDK、Gradle cache、Android SDK / NDK setup、release job への影響を調査する。

## Scope

- CI image / runner
- JDK setup
- Gradle wrapper / cache / daemon
- Android SDK / build tools setup
- NDK / CMake setup
- secrets / signing / release artifact
- test shard / emulator / device farm

## Change Isolation

CI 更新は、AGP / Gradle / Kotlin / NDK 更新と分離する。

ただし、Build System 更新を CI で動かすために必須の CI 変更は同じ migration checklist に記録してよい。その場合も、CI 変更が必須である根拠と rollback plan を残す。

## Detection Method

確認対象:

- GitHub Actions / CircleCI / Bitrise / Jenkins などの workflow
- JDK setup
- Gradle cache key
- Android SDK install step
- NDK / CMake install step
- emulator / device test setup
- signing / release artifact step

## Verification Commands

ローカルで再現できる場合:

```bash
./gradlew assembleDebug
./gradlew test
./gradlew lint
```

CI でのみ確認する場合:

- 対象 workflow:
- 対象 job:
- 確認する artifact:
- rollback 方法:

## Directory

| Directory | Purpose |
| --- | --- |
| [summaries/](summaries/) | CI / build environment 更新の 1ページサマリ |

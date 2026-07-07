# NDK 調査

Android NDK、CMake、native build、ABI、toolchain、`.so` artifact、CI native build 環境への影響を調査する。

## Scope

- NDK version update
- NDK と AGP / Gradle / CMake の互換性
- ABI / toolchain 変更
- native dependency 影響
- `.so` artifact 変更
- release build / symbol upload / crash reporting への影響

## Out of Scope

- AGP 更新そのもの
- Gradle 更新そのもの
- native 以外の依存ライブラリ更新

互換性上同時更新が必要な場合だけ、根拠を記録して例外扱いにする。

## Directory

| Directory | Purpose |
| --- | --- |
| [versions/](versions/) | NDK 更新の詳細調査 |
| [summaries/](summaries/) | NDK 更新の 1ページサマリ |

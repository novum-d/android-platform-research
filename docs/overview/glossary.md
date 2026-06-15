# 用語集（Glossary）

このファイルは、調査レポートで使う用語の意味を揃え、読み手が前提知識を確認できるようにするための用語集です。

## Behavior Change（挙動変更）

Android OS の変更により、アプリの挙動に影響する可能性がある変更。

例:
- これまで取得できていた provider column が、特定 targetSdkVersion 以上では返らなくなる。
- 既存 API の戻り値、例外、権限要求、broadcast delivery timing が変わる。

## AOSP

Android Open Source Project.

## Traceability（追跡可能性）

公式ドキュメントの文言、AOSP根拠、調査結果、結論を追跡できる状態。

例:
- 公式原文: `For apps targeting Android 17...`
- AOSP 根拠: `CompatChanges.isChangeEnabled(...)` と `@EnabledAfter`
- 結論: Android 17 かつ targetSdkVersion 37 以上で適用。

## OS Update / All Apps（OS アップデートで全アプリ対象）

対象 Android バージョン上で動作する全アプリに適用され、targetSdkVersion に依存しない Behavior Change。

例:
- Android 17 にアップデートすると、targetSdkVersion 36 のままでも新挙動になる。

## targetSdkVersion Update（targetSdkVersion 更新で適用）

アプリが対象 Android バージョンの API level 以上を target にした場合に適用される Behavior Change。

例:
- Android 17 / targetSdkVersion 36 では旧挙動。
- Android 17 / targetSdkVersion 37 では新挙動。

## Applicability Gate（適用ゲート）

Behavior Change が適用される条件。例: OS version、targetSdkVersion、compat Change ID、device form factor、permission、manifest property、API usage。

例:
- `targetSdkVersion >= 37`
- `CompatChanges.isChangeEnabled(CHANGE_ID, uid)`
- `sw >= 600dp`
- 特定 permission が grant されていること。

## Compat Framework Default State（compat framework の初期状態）

Android compatibility framework 上で、対象 Change ID が全アプリで有効、targetSdkVersion 条件で有効、無効、logging only など、どの初期状態を持つかを示す情報。

例:
- `@EnabledAfter(targetSdkVersion = 36)` の場合、targetSdkVersion 37 以上で default enabled と判断する。

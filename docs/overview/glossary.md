# Glossary

このファイルは、調査レポートで使う用語の意味を揃え、読み手が前提知識を確認できるようにするための用語集です。

## Behavior Change

Android OS の変更により、アプリの挙動に影響する可能性がある変更。

## AOSP

Android Open Source Project.

## Traceability

公式ドキュメントの文言、AOSP根拠、調査結果、結論を追跡できる状態。

## OS Update / All Apps

対象 Android バージョン上で動作する全アプリに適用され、targetSdkVersion に依存しない Behavior Change。

## targetSdkVersion Update

アプリが対象 Android バージョンの API level 以上を target にした場合に適用される Behavior Change。

## Applicability Gate

Behavior Change が適用される条件。例: OS version、targetSdkVersion、compat Change ID、device form factor、permission、manifest property、API usage。

## Compat Framework Default State

Android compatibility framework 上で、対象 Change ID が全アプリで有効、targetSdkVersion 条件で有効、無効、logging only など、どの初期状態を持つかを示す情報。

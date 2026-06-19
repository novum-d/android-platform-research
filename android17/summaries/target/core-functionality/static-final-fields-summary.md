# static final field が変更不可に - 1ページ要約

## 対象

Android 17 Behavior Change

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

## 適用条件

- 主分類（Primary classification）: TARGET_SDK_37_CONDITIONAL
- OS アップデート / 全アプリ: 非該当。ART gate は targetSdkVersion / runtime SDK version 条件を持つ。
- targetSdkVersion 37 以上: 該当。static final field write が拒否される。
- その他の必須条件: static final field を reflection または JNI で変更しようとする場合。
- Compat Change ID: 見つからない。ART runtime の target SDK gate で制御。
- Compat default state: N/A
- Confidence: High

## 早見マトリクス

| シナリオ | 影響 |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 互換性維持。ART gate により旧挙動。 |
| Android 17 / targetSdkVersion 37 | static final field 変更が拒否される。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | reflection では `IllegalAccessException`、JNI では app crash の可能性がある。 |

## 要約

Android 17 では、Android 17 以上で動作し targetSdkVersion 37 以上のアプリが static final field を実行時に変更できなくなる。影響は reflection または JNI で static final field を書き換えるコードに集中する。ART の `ArtField::IsUnmodifiable()` と reflection / JNI write path で gate を確認した。

## 顧客影響

- reflection による static final field write は `IllegalAccessException` になる。
- JNI `SetStatic*Field()` による static final field write は modifiability check で拒否される。

## 影響対象

- 対象アプリ: targetSdkVersion 37 への更新を予定している Android アプリ。
- 対象機能: feature flag override、SDK 内部値の変更、hot patch、mocking、hooking、diagnostics、native instrumentation。
- 対象条件: 自社コードまたは SDK が reflection / JNI で static final field を変更している場合。

## 対応要否

- 必須対応: static final field の runtime write を棚卸しする。
- 推奨対応: mutable config、dependency injection、server-side config など、static final field 書き換えに依存しない設計へ移行する。
- 不要: static final field を読み取るだけで変更せず、関連 SDK も runtime write していないことを確認できる場合は、互換性対応は限定的。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 36 | Android 16 baseline。static final field write は互換的に許容される可能性がある。 |
| Android 17 | 36 | ART gate により旧挙動。 |
| Android 17 | 37 | static final field 変更が拒否される。 |

## 顧客向け説明

Android 17 では、targetSdkVersion 37 以上のアプリに対して static final field の実行時変更が禁止される予定です。reflection で変更しようとした場合は `IllegalAccessException`、JNI API で変更しようとした場合はアプリ crash になると公式文書は説明しています。自社コードだけでなく、組み込み SDK や native library が static final field を書き換えていないか確認する必要があります。

ART runtime の実装では targetSdkVersion 36 以下を互換扱いし、Android 17 / targetSdkVersion 37 以上で static final field を unmodifiable として扱います。

## 根拠

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-17
- 検証対象の原文: Android 17+ で動作し targetSdkVersion 37+ のアプリは static final field を変更できない。reflection では `IllegalAccessException`、JNI では crash。
- AOSP ファイル: `tmp/aosp-checkouts/art/runtime/art_field-inl.h`
- AOSP ファイル: `tmp/aosp-checkouts/art/runtime/native/java_lang_reflect_Field.cc`
- AOSP ファイル: `tmp/aosp-checkouts/art/runtime/jni/jni_internal.cc`
- AOSP test: `tmp/aosp-checkouts/art/test/2396-unmodifiable-final-fields`
- AOSP ソース文脈: app code -> reflection `Field.set*()` または JNI `SetStatic*Field()` -> ART runtime modifiability check。
- 差分解釈: static final field を初期化後 unmodifiable とし、targetSdkVersion 36 以下では互換性維持する changed condition。
- 適用ゲートの結論: Android 17 runtime かつ targetSdkVersion 37 以上。

## 人間の判断欄

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断

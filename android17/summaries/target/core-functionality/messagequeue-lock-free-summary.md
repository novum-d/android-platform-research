# MessageQueue の新しい lock-free 実装 - 1ページ要約

## 対象

Android 17 Behavior Change

比較元:
- android-16.0.0_r4

比較先:
- TBD: Android 17 AOSP タグ

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

## 適用条件

- 主分類（Primary classification）: UNKNOWN_NEEDS_MORE_EVIDENCE
- OS アップデート / 全アプリ: 未確認。公式文書は all apps ページではなく、apps targeting Android 17 or higher ページに掲載。
- targetSdkVersion 37 以上: 公式文書上は該当。ただし AOSP gate は未確認。
- その他の必須条件: `MessageQueue` private field / private method への reflection が互換性リスク条件。
- Compat Change ID: 未確認
- Compat default state: 未確認

## 早見マトリクス

| シナリオ | 影響 |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 未確認。公式文書上は targetSdkVersion 37 以上向けだが、AOSP gate は未確認。 |
| Android 17 / targetSdkVersion 37 | 新しい lock-free `MessageQueue` 実装が適用されると公式文書は説明。private reflection は破損リスクあり。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | `MessageQueue` private field / private method を reflection している場合、crash や監視機能不具合の可能性がある。 |

## 要約

Android 17 では、targetSdkVersion 37 以上のアプリに新しい lock-free `android.os.MessageQueue` 実装が適用される、と公式文書は説明している。通常の public API 利用よりも、private field / private method への reflection が互換性リスクになる。

## 顧客影響

- 要確認

## 影響対象

- 対象アプリ: targetSdkVersion 37 への更新を予定している Android アプリ。
- 対象機能: main thread monitoring、message queue instrumentation、ANR / jank monitoring、performance diagnostics。
- 対象条件: 自社コードまたは SDK が `MessageQueue` の private implementation detail に reflection している場合。

## 対応要否

- 必須対応: `MessageQueue` private field / private method への reflection 利用を棚卸しする。
- 推奨対応: 該当箇所を public API ベースに移行し、SDK を Android 17 対応版に更新する。Espresso は 3.7.0 以上、Robolectric は 4.17 以上に更新し、`@LooperMode(LEGACY)` は `@LooperMode(PAUSED)` へ移行する。
- 不要: public API のみを使っており、関連 SDK も private reflection していないことを確認できる場合は、互換性対応は限定的。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 36 | Android 16 baseline。Android 17 の lock-free implementation は対象外。 |
| Android 17 | 36 | 未確認。公式文書上は旧挙動維持が期待されるが、AOSP gate は未確認。 |
| Android 17 | 37 | 公式文書上は新しい lock-free `MessageQueue` 実装が適用される。 |
| Android 17 | 36 / debuggable | `adb am compat enable USE_NEW_MESSAGEQUEUE <package>` で新実装を test できると公式 guidance は説明。 |

## 顧客向け説明

Android 17 では、targetSdkVersion 37 以上のアプリに対して `MessageQueue` の内部実装が変わる予定です。性能改善が目的の変更ですが、`MessageQueue` の private field や private method を reflection で参照しているコードは、内部構造の変更により壊れる可能性があります。まず自社コードと組み込み SDK の reflection 利用を確認し、targetSdkVersion 37 更新前に Android 17 で実機または emulator テストを行う必要があります。

詳細 guidance では、新実装でも binary compatibility のため `mMessages` field は残るが常に `null` になると説明されています。`USE_NEW_MESSAGEQUEUE` compat flag を使って enable / disable し、原因切り分けを行えます。

ただし、現時点ではローカル AOSP checkout に Android 17 タグがないため、targetSdkVersion gate や compat flag の有無は未確認です。最終的な適用分類は Android 17 AOSP タグ公開後に再確認が必要です。

## 根拠

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-17
- Related guidance: https://developer.android.com/about/versions/17/changes/messagequeue
- API reference: https://developer.android.com/reference/android/os/MessageQueue
- 検証対象の原文: Android 17 から targetSdkVersion 37 以上のアプリが新しい lock-free `MessageQueue` 実装を受け取り、private field / method reflection client が壊れる可能性がある。
- AOSP ファイル: 未確認。ローカル `frameworks-base` に `android-17*` タグがない。
- AOSP ソース文脈: 未確認。タグ間 diff が実行できない。
- 差分解釈: 未分類。added behavior / changed condition / changed default の判定は Android 17 タグ待ち。
- 適用ゲートの結論: 未確認。公式文書は targetSdkVersion 37 以上を示すが、AOSP gate evidence は未取得。

## 人間の判断欄

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 追加調査が必要

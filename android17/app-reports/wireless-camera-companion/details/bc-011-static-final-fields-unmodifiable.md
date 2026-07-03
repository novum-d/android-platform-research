# BC-011: Static final fields are now unmodifiable

## 基本情報（Basic Information）

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/17/behavior-changes-17
- Section: Static final fields are now unmodifiable

Original statement:
> Android 17 以上で targetSdkVersion 37 以上のアプリは static final field を reflection / JNI で変更できない、という趣旨の公式説明。

調査対象 Android バージョン:
- From: android-16.0.0_r4
- To: android-17.0.0_r1

## 対象アプリとの関係（Relevance to Target App）

関連するアプリ機能:
- 古いアプリ / SDK の runtime patching。
- SDK 初期化時の feature flag / constant / debug setting 差し替え。
- JNI で static final field を変更する初期化処理。

関連する API / permission / component:
- Java reflection `Field.set*()`
- `setAccessible(true)`
- JNI `SetStatic*Field()`

アプリが該当する可能性:
- Conditional。通常の Camera API / Camera2 API 利用だけでは該当しない。古い SDK、debug tool、runtime patching 実装が reflection / JNI で `static final` field を書き換える場合に該当する。

確認したアプリ実装:
- File / module: 未確認。
- Symbol / entry point: `Field.set*()`、`SetStatic*Field()` 利用有無は未確認。
- Manifest / permission: 該当なし。
- Runtime condition: targetSdkVersion 37 以上で該当コードパスが実行される場合。

## 適用条件分類（Applicability Classification）

主分類（Primary classification）:
- TARGET_SDK_37_CONDITIONAL

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 原則 No | ART runtime の targetSdkVersion / SDK version gate。 |
| targetSdkVersion 37 以上が必要か | Yes | Android 17 runtime + targetSdkVersion 37 以上で static final が unmodifiable と扱われる。 |
| 追加の実行時条件があるか | Yes | reflection / JNI による `static final` field write。 |
| Compat Change ID が関係するか | 未確認 | static final 側の compat ChangeId は確認できない。 |

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 以上。
- targetSdkVersion: 37 以上。
- API/component condition: reflection / JNI による `static final` field write。
- App state/process condition: アプリ起動時、SDK 初期化時、debug / test hook 実行時。

Compat framework:
- Change ID: 確認されず。
- Default state: ART runtime targetSdkVersion / SDK version gate。
- Toggleable for testing: compat ChangeId は未確認。

## AOSP 調査（AOSP Investigation）

関連ファイル:
- `platform/art/runtime/art_field-inl.h`
- `platform/art/runtime/native/java_lang_reflect_Field.cc`
- `platform/art/runtime/jni/jni_internal.cc`
- `platform/art/test/2396-unmodifiable-final-fields`

確認したソース文脈（Source Context Reviewed）:

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `ArtField::IsUnmodifiable()` | 汎用 static final target 37 gate なし | targetSdkVersion / SDK version を見て static final field を unmodifiable と判断 | reflection / JNI の static final write rejection の中心。 |
| `java_lang_reflect_Field.cc` | static final の汎用 write rejection なし | `IsUnmodifiable()` の場合に `IllegalAccessException` | 公式文書の reflection failure path。 |
| `jni_internal.cc` / `SetStatic*Field()` | static final の汎用変更検出なし | `EnsureModifiable()` で static final write attempt を検出 | 公式文書の JNI crash / fatal path。 |

差分解釈（Diff Interpretation）:
- Added behavior: reflection / JNI の static final field write rejection。
- Changed condition / gate: Android 17 runtime + targetSdkVersion 37 以上。
- No behavior change found: 通常の Camera API / Camera2 API 呼び出し自体には直接関係しない。

適用ゲート根拠（Applicability Gate Evidence）:
- targetSdkVersion gate: ART runtime targetSdkVersion / SDK version gate。
- CompatChanges.isChangeEnabled / ChangeId: 確認できず。
- Build.VERSION / SDK_INT gate: Android 17 runtime が前提。
- Gate conclusion: Android 17 / targetSdkVersion 37 以上で、static final field write を行う場合に適用。

## 事実・観察・仮説・結論（Facts / Observations / Hypotheses / Conclusion）

事実（Facts）:
- Static final fields は ART 側で reflection / JNI write が拒否される。
- reflection では `IllegalAccessException`、JNI では fatal crash path になり得る。

観察（Observations）:
- カメラ連携アプリ自体の Camera API 利用とは直接関係しない。
- 古い SDK では reflection / JNI による内部値変更を持つ可能性がある。

仮説（Hypotheses）:
- 古い SDK が `static final` field を reflection / JNI で変更している場合、起動時または SDK 初期化時に失敗する可能性がある。

結論（Conclusion）:
- カメラ連携アプリでは要確認。通常のカメラ撮影 API だけではなく、同梱 SDK / debug tool / runtime patching 実装を含めて棚卸しする必要がある。

## アプリ影響（App Impact）

想定される影響:
- アプリ起動時または SDK 初期化時の crash / initialization failure。
- reflection では `IllegalAccessException`、JNI では fatal crash path。
- debug menu、feature flag、SDK internal constant の runtime patching が動作しない可能性。

ユーザー影響:
- アプリ起動失敗。
- ライブビュー、画像転送、動画処理、クラウド連携など、該当 SDK に依存する一部機能が使えない可能性。

開発者影響:
- `Field.set*()` / `setAccessible(true)` / JNI `SetStatic*Field()` の棚卸し。
- runtime patching ではなく DI、mutable holder、build-time config などへの移行。

推奨対応候補:
- アプリコードと SDK で `Field.set`、`SetStatic`、`static final` 書き換え処理を検索する。
- reflection / JNI failure を起動 / 機能初期化の failure として検出できるようにする。
- 該当 SDK がある場合は Android 17 / targetSdkVersion 37 対応版へ更新する。

## Confidence

Confidence:
- High

Confidence の根拠:
- ART runtime evidence を確認済み。

不足している根拠:
- 対象アプリおよび同梱 SDK の reflection / JNI 実装。
- 実際の targetSdkVersion 37 ビルドでの起動・SDK 初期化テスト。

---

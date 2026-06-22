# static final field が変更不可に

## 基本情報

### 調査対象 Android バージョン

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

### Behavior Change 文書

文書:
https://developer.android.com/about/versions/17/behavior-changes-17

セクション:
Static final fields are now unmodifiable

ページ種別:
- Apps targeting Android 17 or higher

### 分類スナップショット

主分類（Primary classification）:
- TARGET_SDK_37_CONDITIONAL

公式文書からの初期適用条件判断:
- 公式文書は、Android 17 以上で動作し、かつ targetSdkVersion 37 以上のアプリに適用される変更として説明している。
- static final field を reflection または JNI で変更しようとする場合に影響するため、一次分類としては `TARGET_SDK_37_CONDITIONAL` が近い。
- 追加 checkout の `platform/art` と `platform/libcore` で、reflection / JNI の static final field write enforcement と targetSdkVersion / SDK gate を確認したため、確定分類は `TARGET_SDK_37_CONDITIONAL` とする。

早見表:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 原則 No | ART は `Runtime::Current()->GetTargetSdkVersion()` と `Runtime::Current()->GetSdkVersion()` を参照し、Android C / targetSdkVersion C 以上で static final を unmodifiable にする。 |
| targetSdkVersion 37 以上が必要か | Yes | ART test は `-Xtarget-sdk-version:31` と `-Xtarget-sdk-version:37` を比較し、target > 36 で failure を期待する。 |
| 追加の実行時条件があるか | ある | static final field を reflection または JNI で変更しようとする場合に問題化する。 |
| Compat Change ID が関係するか | 確認できず | ART の該当 enforcement は targetSdkVersion / SDK version gate で、compat ChangeId は確認できなかった。 |

### 調査日

2026-06-10

### 信頼度

- High

### 適用条件分類

適用される条件:
- [ ] Android 17 上の全アプリ（targetSdkVersion に依存しない）
- [ ] Android 17 以上で targetSdkVersion >= 37
- [x] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [ ] 追加根拠が必要

必要な実行時条件:
- Android version: 公式文書上は Android 17 以上。
- targetSdkVersion: 公式文書上は 37 以上。
- Device/form factor: 公式抜粋では条件なし。
- Permission/API/component condition: reflection で static final field を変更する、または JNI API で static final field を変更する。
- App state/process condition: 公式抜粋では条件なし。

Compat framework:
- Change ID: 確認できず
- 変更名: 該当なし
- 既定状態: Android 17 / targetSdkVersion 37 以上で有効
- テスト時の切り替え可否: ART runtime option / targetSdkVersion test により確認可能

分類信頼度:
- High

分類根拠:
- 公式ドキュメントページ: `behavior-changes-17`
- 検証対象の適用条件文: Android 17+ で動作し、targetSdkVersion 37+ のアプリが対象。
- AOSP targetSdk gate: `platform/art` の `ArtField::IsUnmodifiable()` と `test/2396-unmodifiable-final-fields` で確認。
- Compat framework entry: 該当 ChangeId は確認できず。runtime targetSdkVersion / SDK version gate として実装されている。

---

# エグゼクティブサマリー

Android 17 では、Android 17 以上で動作し targetSdkVersion 37 以上のアプリが static final field を変更できなくなる、と公式 Behavior Change 文書は説明している。reflection で変更しようとすると `IllegalAccessException`、JNI の static field 書き換え API ではアプリ crash が発生するとされている。

影響を受けるのは、定数、feature flag、SDK 内部値、テスト用 hook などの static final field を実行時に書き換えるアプリや SDK である。ART では targetSdkVersion 37 以上かつ Android 17 以上で static final field が unmodifiable になり、reflection は `IllegalAccessException`、JNI の `SetStatic*Field()` は fatal path になる。

---

# 公式ドキュメント確認

## 原文（Statement）

Page title:
- Behavior changes: Apps targeting Android 17 or higher

Page URL:
- https://developer.android.com/about/versions/17/behavior-changes-17

ページ種別:
- apps targeting Android 17

Section title:
- Static final fields are now unmodifiable

検証対象の原文:

> cannot change static final fields

提供された公式文書の抜粋は、Android 17 以上で動作し API level 37 以上を対象とするアプリは static final field を変更できないと説明している。また、reflection による試行では `IllegalAccessException` が発生し、`SetStaticLongField()` など JNI による試行ではアプリが crash すると説明している。

## 解釈

この変更は、static final field を実行時に変更する実装パターンを禁止する互換性変更である。公式文書は OS 条件として Android 17 以上、targetSdkVersion 条件として 37 以上を明示している。

開発者への意味は、Java/Kotlin reflection や JNI を使って static final field を後から変更する実装が、targetSdkVersion 37 更新後に失敗する可能性があるということ。通常の field 読み取りや、static final field を変更しない通常の public API 利用は、この文言だけでは影響対象とは言えない。

---

# 変更内容

公式文書上の変更点:
- Android 17 以上で動作し、targetSdkVersion 37 以上のアプリは static final field を変更できない。
- reflection による変更 attempt は `IllegalAccessException` になる。
- JNI API による変更 attempt はアプリ crash になる。

AOSP で確認した点:
- `platform/art` の `runtime/art_field-inl.h` に `ArtField::IsUnmodifiable()` が追加され、targetSdkVersion と SDK version を参照して static final field を unmodifiable と判断する。
- `runtime/native/java_lang_reflect_Field.cc` は `IsUnmodifiable()` の場合に `IllegalAccessException` を投げる。
- `runtime/jni/jni_internal.cc` は `SetStatic*Field()` 系で `EnsureModifiable()` を呼び、static final field の変更 attempt を検出する。
- `test/2396-unmodifiable-final-fields` は `-Xtarget-sdk-version:31` と `-Xtarget-sdk-version:37` を比較し、target > 36 で static final write が失敗することを確認する。

## 適用条件

公式文書と ART evidence から、Android 17 以上、targetSdkVersion 37 以上、かつ static final field を変更しようとする場合に影響する。確定分類は `TARGET_SDK_37_CONDITIONAL` とする。

### OS アップデート時の挙動

- Android 17 にアップデートしただけで適用されるか: 原則 No。ART は targetSdkVersion 36 以下に互換性維持 path を持つ。
- targetSdkVersion に依存しない根拠: なし。公式文書は targetSdkVersion 37 以上を明示している。
- Android 16 以前での挙動: ART の Android 16 tag には `test/2396-unmodifiable-final-fields` と汎用 static final unmodifiable gate がない。

### targetSdkVersion 37 以上での挙動

- targetSdkVersion 37 以上で適用されるか: Yes。ART test と `Runtime::Current()->GetTargetSdkVersion()` gate で確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: 未確認。公式文書は Apps running on Android 17 or higher を条件にしているため、Android 17 platform behavior として扱う。
- opt-out / temporary override の有無: compat ChangeId は確認できない。debuggable runtime では未初期化 static final field を JNI で設定できる例外 test がある。

### その他の条件

- device/form factor: 公式抜粋では条件なし。
- permission: 公式抜粋では条件なし。
- API usage: reflection または JNI で static final field を変更しようとすること。
- manifest attribute: 未確認。
- component boundary: アプリコード、自社ライブラリ、サードパーティ SDK、native code のいずれでも static final field 変更 attempt があれば影響し得る。

---

# AOSP 調査

## checkout 状態

根拠を採用する前に確認したコマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list 'android-17*'
```

結果:
- `frameworks-base` working tree: 調査時点で clean。
- From tag: `android-16.0.0_r4` exists.
- To tag: `android-17.0.0_r1` exists.

根拠上の制約:
- `frameworks-base` では明示的な tag 比較と symbol 検索を実施したが、static final field write enforcement の直接実装、targetSdkVersion ゲート、Compat Change ID は確認できなかった。
- `tmp/aosp-checkouts/art` と `tmp/aosp-checkouts/libcore` に `platform/art` / `platform/libcore` の Android 16 / Android 17 tag を取得し、runtime / reflection / JNI evidence を確認した。
- 広域の `frameworks-base` tag diff では rename detection が skipped される警告が出たため、`--no-renames` と runtime / JNI / reflection 周辺 path 限定で再確認した。`NativeZygoteProcess`、`AndroidRuntime`、`core/java/android/os` には多数の差分があるが、reflection `Field.set*()` または JNI `SetStatic*Field()` の static final write enforcement は確認できなかった。
- この制約は解消済み。AOSP-backed conclusion は High confidence とする。

## 関連ファイル

追加 checkout で確認:
- `platform/art/runtime/art_field-inl.h`
- `platform/art/runtime/art_field.h`
- `platform/art/runtime/native/java_lang_reflect_Field.cc`
- `platform/art/runtime/jni/jni_internal.cc`
- `platform/art/test/2396-unmodifiable-final-fields`
- `platform/art/test/2400-setstaticfield-uninitialized`
- `platform/libcore/luni/src/test/java/libcore/java/lang/reflect/FieldTest.java`

## 確認したソース文脈

`frameworks-base` の Android 17 tag では直接実装はない。実装本体は ART / libcore 側で確認した。

| ファイル / シンボル | Android 16 基準挙動 | Android 17 挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `frameworks-base` / `core` / `packages` の static final / reflection / JNI 関連検索 | 関連 gate 未確認 | 関連 gate 未確認 | enforcement 実装が `frameworks-base` にあるかを確認したが、直接 evidence は見つからなかった。 |
| `ArtField::IsUnmodifiable()` | 汎用 static final target 37 gate なし | targetSdkVersion / SDK version を見て static final field を unmodifiable と判断 | reflection / JNI 双方が参照する enforcement 判断。 |
| `java_lang_reflect_Field.cc` | `IsMonotonic` / write-protected 中心 | `IsUnmodifiable()` なら `IllegalAccessException` を投げる | 公式文書の reflection failure path。 |
| `jni_internal.cc` / `SetStatic*Field()` | static final の汎用変更検出なし | `EnsureModifiable()` を呼び、変更 attempt を検出 | 公式文書の JNI crash / fatal path。 |
| `test/2396-unmodifiable-final-fields` | なし | target 31 と 37 を比較し、target > 36 で static final write failure を期待 | targetSdkVersion ゲートの test evidence。 |

必須記入項目:
- Entry point / caller: Java reflection field write と JNI static field write。
- Relevant class or service responsibility: ART / libcore の reflection / JNI / runtime enforcement 層。
- Runtime path from app API / system event to changed code: app code -> reflection `Field.set*()` または JNI `SetStatic*Field()` -> ART runtime modifiability check。
- 除外した無関係なコードパス: `core/api/current.txt` の多数の `public static final` API entries は単なる API surface 定義であり、runtime write enforcement ではないため除外。

## 差分解釈

| 確認した差分 | 解釈 | 挙動変更との関係 | 信頼度 |
| --- | --- | --- | --- |
| `frameworks-base` で関連 gate が見つからない | no behavior change found in frameworks-base scope | 実装本体は ART / runtime 側にあるため、frameworks-base 単体では根拠にならない。 | 高 |
| `ArtField::IsUnmodifiable()` | changed condition / gate | targetSdkVersion 36 以下を互換扱いし、Android C / targetSdkVersion C 以上で static final field を unmodifiable とする。 | 高 |
| `java_lang_reflect_Field.cc` | added enforcement path | reflection write attempt を `IllegalAccessException` に変換する。 | 高 |
| `jni_internal.cc` / `SetStatic*Field()` | added enforcement path | JNI static field write attempt に modifiability check を適用する。 | 高 |

必須分類:
- Added behavior: reflection / JNI の static final field write rejection。
- Removed behavior: targetSdkVersion 37 以上での static final field runtime write の互換許容。
- Changed condition / gate: Android C / targetSdkVersion C 以上で enforcement。
- Changed default: targetSdkVersion 37 以上では static final field が初期化後 unmodifiable。
- No behavior change found: `frameworks-base` scope では該当。ただし platform 全体の evidence は ART / libcore で確認済み。

## 事実

事実:
- 公式 Behavior Change 文書は、Android 17 以上で動作し targetSdkVersion 37 以上のアプリが static final field を変更できないと述べている。
- 公式文書は、reflection で static final field を変更しようとすると `IllegalAccessException` が発生すると述べている。
- 公式文書は、JNI API で static final field を変更しようとするとアプリが crash すると述べている。
- ローカル `frameworks-base` には `android-16.0.0_r4` タグがある。
- ローカル `frameworks-base` には `android-17.0.0_r1` タグがある。
- 調査時点で `frameworks-base` working tree は clean。
- `frameworks-base` 内の static final / reflection / JNI / compat 関連検索では、この Behavior Change に対応する直接 gate は確認できなかった。
- repo root には `art` checkout が存在しなかった。

観察:
- 公式ページ種別と原文は targetSdkVersion 37 以上の変更を示している。
- 原文は Android 17 以上という OS 条件も明示している。
- static final field を変更しようとする reflection / JNI usage が追加条件になる。
- `frameworks-base` では、実装が本当に targetSdkVersion 37 gate で制御されているかは未確認。
- Compat framework entry の有無も未確認。

仮説:
- 実機では ART test と同様に、targetSdkVersion 36 以下では互換 path が維持される。
- サードパーティ SDK の reflection / JNI write path が初期化時に実行される場合、targetSdkVersion 37 更新直後に顕在化しやすい。

結論:
- Android 17 以上かつ targetSdkVersion 37 以上で static final field write が拒否される。
- AOSP 根拠 は ART / libcore にあり、確定分類は `TARGET_SDK_37_CONDITIONAL`、Confidence は High。

## 適用ゲート根拠

- targetSdkVersion 適用ゲート: `ArtField::IsUnmodifiable()` が `Runtime::Current()->GetTargetSdkVersion()` を参照する。
- CompatChanges.isChangeEnabled / ChangeId: 該当 ChangeId は確認できない。runtime targetSdkVersion / SDK version gate として実装されている。
- @EnabledAfter / @EnabledSince / default state: N/A。
- Build.VERSION / SDK_INT 適用ゲート: `Runtime::Current()->GetSdkVersion()` を参照し、Android C 以上で static final を unmodifiable と扱う。
- DeviceConfig / resources config: 該当なし。
- Permission/AppOps 適用ゲート: 該当なし。
- Manifest/property 適用ゲート: 未確認。
- 適用ゲート未検出: `frameworks-base` scope では該当。ただし platform 全体の gate は ART で確認済み。
- 適用ゲートの結論: Android 17 runtime かつ targetSdkVersion 37 以上。
- ソース文脈からの推論: `frameworks-base` には該当 path がなく、ART / runtime 側の reflection / JNI enforcement 実装が主調査対象と推定。

確認済み:
- `frameworks-base` checkout status。
- `android-16.0.0_r4` tag の存在。
- `android-17.0.0_r1` tag の存在。
- `frameworks-base` 内の static final / reflection / JNI / compat 関連検索。
- repo root の `art` checkout 有無。

追加確認候補:
- 実機 / emulator での reflection exception stack trace。
- JNI fatal path のログ形式。

理由:
- 顧客向けには実機でのログ・例外形状まで確認できると troubleshooting 情報として有用なため。

---

# 影響分析

## 影響を受けるアプリ

影響を受ける可能性があるアプリ:
- targetSdkVersion 37 以上への更新を予定しているアプリ。
- reflection で static final field を書き換える自社コードを持つアプリ。
- JNI で static final field を書き換える native code を持つアプリ。
- feature flag、SDK 内部定数、build-time constant、テスト用 override、互換性回避のために static final field を実行時に変更しているアプリまたは SDK。
- 古い instrumentation、hot patch、mocking、hooking、diagnostics 系 SDK を組み込んでいるアプリ。

## 影響を受けにくいアプリ

影響が限定的と考えられるケース:
- static final field を読み取るだけで変更しないアプリ。
- reflection や JNI による static final field 書き換えを行っていないアプリ。
- targetSdkVersion 37 へ上げないアプリ。

---

# 顧客影響

## 影響度

- 人間による判断が必要

※ 最終 severity / priority は人間が判断する。このレポートでは確定しない。

## ビジネス影響

- ユーザー影響: 該当コードパスが実行されると、reflection では例外処理漏れによる機能停止や crash、JNI では直接 crash が発生する可能性がある。
- 運用影響: サードパーティ SDK や native library が原因の場合、アプリ側で検出しにくく、SDK vendor への確認や更新が必要になる可能性がある。
- 開発影響: targetSdkVersion 37 更新前に reflection / JNI field write の棚卸し、代替設計、Android 17 テストが必要。

---

# サービス影響例

このセクションは、公式文書と AOSP 根拠 から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1: 設定値を reflection で差し替えるアプリ / SDK

- 対象サービス例: A/B test SDK、feature flag framework、社内 debug tool。
- 影響を受ける実装パターン: `static final` fields を reflection / Unsafe / instrumentation で書き換える実装。
- 発生条件: Android 17 / targetSdkVersion 37 で `static final` fields が unmodifiable と扱われる場合。
- ユーザーに見える症状: feature flag が切り替わらない、debug menu の変更が反映されない、初期化時に例外が出る可能性。
- 開発・運用への影響: runtime patching 前提の設定更新、テスト環境の差し替え、SDK initialization の見直しが必要になる可能性。
- 推奨対応候補: mutable holder / DI / build-time config に移行し、`static final` 直接変更を避ける。
- 根拠: 公式 Behavior Change statement と ART / libcore evidence。
- 信頼度: 高
- 注意: 実際の影響は該当 SDK が static final field を実行時変更しているかに依存する。

## 例2: テスト / mocking framework に依存するアプリ

- 対象サービス例: 大規模 Android app の instrumented test、E2E test、SDK integration test。
- 影響を受ける実装パターン: production code の `static final` constant を test runtime で書き換える test utility。
- 発生条件: targetSdkVersion 37 の test build / app process で static final mutation が拒否される場合。
- ユーザーに見える症状: 直接の本番ユーザー影響は限定的だが、テスト失敗により release validation が詰まる可能性。
- 開発・運用への影響: test fixture、mocking strategy、CI の Android 17 対応が必要になる可能性。
- 推奨対応候補: constructor injection、interface abstraction、test-only build variants に移行する。
- 根拠: 公式 statement と ART / libcore evidence。
- 信頼度: 高
- 注意: 実サービス障害ではなく開発・検証 pipeline への影響例。

---

# 対応候補

## 必須対応（Must）

- static final field を reflection で変更している自社コードがないか確認する。
- JNI API で static final field を変更している native code がないか確認する。
- サードパーティ SDK に static final field の runtime override、hot patch、mocking、hooking が含まれていないか確認する。
- targetSdkVersion 37 更新前に Android 17 device / emulator で該当機能をテストする。

## 推奨対応（Recommended）

- static final field の実行時変更に依存しない設計へ移行する。
- 設定値や feature flag は mutable な設定 API、dependency injection、設定ファイル、server-side config などに移す。
- reflection failure を crash にしないため、例外処理と fallback を確認する。
- native library / SDK を Android 17 対応版に更新する。

## 任意対応（Optional）

- 実機 / emulator で exception type、JNI crash log、targetSdkVersion 36 / 37 の差を確認する。
- テスト用の static final override がある場合、test-only mechanism と production code を分離する。

---

# 検証方法

## 検証マトリクス

| 端末 OS | targetSdkVersion | Compat flag | 期待される挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | default | Android 16 baseline。汎用 static final unmodifiable gate はない。 |
| Android 17 | 36 | default | ART gate により互換 path。 |
| Android 17 | 37 | default | static final field 変更が拒否される。reflection は `IllegalAccessException`、JNI は app crash。 |
| Android 17 | 36 | force-enabled（利用可能な場合） | 該当なし。Compat ChangeId ではなく ART runtime gate。 |
| Android 17 | 37 | force-disabled（利用可能な場合） | 該当なし。Compat ChangeId ではなく ART runtime gate。 |

## 手順

- targetSdk変更: test app を targetSdkVersion 36 と 37 で build し、Android 17 上の挙動差を確認する。
- Compat framework コマンド: 該当なし。AOSP 根拠 上は compat ChangeId ではなく ART runtime gate。
- テスト方法: static final field を reflection で変更する最小再現コードと、JNI で変更する最小 native test を用意する。
- 再現手順: Android 17 上で targetSdkVersion 36 / 37 の両 APK を実行し、reflection の例外種別、JNI crash、stack trace、compat flag 有無を比較する。
- 期待結果: targetSdkVersion 37 では static final field 変更が拒否される。targetSdkVersion 36 では互換 path により旧挙動が維持される。

---

# 結論

公式文書は、Android 17 以上で動作し targetSdkVersion 37 以上のアプリが static final field を変更できなくなると説明している。主な互換性リスクは、reflection または JNI で static final field を実行時に書き換えるコードである。

AOSP 根拠 は `frameworks-base` ではなく ART / libcore にあり、`ArtField::IsUnmodifiable()`、reflection path、JNI path、ART test で確認できた。確定分類は `TARGET_SDK_37_CONDITIONAL`、信頼度は High とする。

# 人間の判断欄

最終優先度（Final Priority）:
- 人間による判断が必要

最終影響度:
- 人間による判断が必要

リリース判断:
- 人間による判断が必要

顧客通知優先度:
- 人間による判断が必要

次に必要な人間の判断:
- static final field runtime write を行う自社コード / SDK の棚卸し優先度を判断する。

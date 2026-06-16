# static final field が変更不可に

## 基本情報

### 調査対象 Android バージョン

比較元:
- android-16.0.0_r4

比較先:
- TBD: Android 17 AOSP タグ

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
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- 公式文書は、Android 17 以上で動作し、かつ targetSdkVersion 37 以上のアプリに適用される変更として説明している。
- static final field を reflection または JNI で変更しようとする場合に影響するため、一次分類としては `TARGET_SDK_37_CONDITIONAL` が近い。
- ただし、ローカル `frameworks-base` に Android 17 AOSP タグがないため、AOSP gate、Compat Change ID、default state を検証できていない。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

早見表:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 未確認 | 原文は Android 17+ と targetSdkVersion 37+ の両方を条件としているが、AOSP gate は未確認。 |
| targetSdkVersion 37 以上が必要か | 可能性は高いが未確認 | 原文は target Android 17 / API level 37 以上を明示している。AOSP evidence は未取得。 |
| 追加の実行時条件があるか | ある | static final field を reflection または JNI で変更しようとする場合に問題化する。 |
| Compat Change ID が関係するか | 未確認 | Android 17 タグと compat framework evidence が未確認。 |

### 調査日

2026-06-10

### 信頼度

- 低

### 適用条件分類

適用される条件:
- [ ] Android 17 上の全アプリ（targetSdkVersion に依存しない）
- [ ] Android 17 以上で targetSdkVersion >= 37
- [ ] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [x] 未確認 / 追加根拠が必要

必要な実行時条件:
- Android version: 公式文書上は Android 17 以上。
- targetSdkVersion: 公式文書上は 37 以上。
- Device/form factor: 公式抜粋では条件なし。
- Permission/API/component condition: reflection で static final field を変更する、または JNI API で static final field を変更する。
- App state/process condition: 公式抜粋では条件なし。

Compat framework:
- Change ID: 未確認
- 変更名: 未確認
- 既定状態: 未確認
- テスト時の切り替え可否: 未確認

分類信頼度:
- 低

分類根拠:
- 公式ドキュメントページ: `behavior-changes-17`
- 検証対象の適用条件文: Android 17+ で動作し、targetSdkVersion 37+ のアプリが対象。
- AOSP targetSdk gate: 未確認。ローカル `frameworks-base` に `android-17*` タグがない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# エグゼクティブサマリー

Android 17 では、Android 17 以上で動作し targetSdkVersion 37 以上のアプリが static final field を変更できなくなる、と公式 Behavior Change 文書は説明している。reflection で変更しようとすると `IllegalAccessException`、JNI の static field 書き換え API ではアプリ crash が発生するとされている。

影響を受けるのは、定数、feature flag、SDK 内部値、テスト用 hook などの static final field を実行時に書き換えるアプリや SDK である。ローカル `frameworks-base` に Android 17 AOSP タグがないため、現時点では AOSP gate と compat framework default state を検証できていない。

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

AOSP で未確認の点:
- Android 16 baseline で static final field 変更 attempt がどこまで許容されていたか。
- Android 17 で reflection と JNI それぞれの制御がどの層に追加されたか。
- targetSdkVersion 37 gate の実装箇所。
- Compat Change ID と default state。
- opt-out または temporary override の有無。

## 適用条件（Applicability）

公式文書の一次判断では、Android 17 以上、targetSdkVersion 37 以上、かつ static final field を変更しようとする場合に影響する。AOSP tag が未取得のため、確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

### OS アップデート時の挙動

- Android 17 にアップデートしただけで適用されるか: 未確認
- targetSdkVersion に依存しない根拠: なし。公式文書は targetSdkVersion 37 以上を明示している。
- Android 16 以前での挙動: AOSP タグ比較未実施。Android 16 baseline source は Android 17 タグとの比較ができないため、この調査では platform evidence として採用していない。

### targetSdkVersion 37 以上での挙動

- targetSdkVersion 37 以上で適用されるか: 公式文書上は Yes と読めるが、AOSP gate は未確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: 未確認。公式文書は Apps running on Android 17 or higher を条件にしているため、Android 17 platform behavior として扱う。
- opt-out / temporary override の有無: 未確認。compat framework evidence 未確認。

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
- To tag: ローカルに `android-17*` タグなし。

根拠上の制約:
- Android 17 AOSP タグがローカル `frameworks-base` に存在しないため、`git -C frameworks-base diff android-16.0.0_r4 <android-17-tag> -- ...` による明示的なタグ比較を実行できない。
- Repository rule に従い、Android 17 working tree や推測による source evidence は採用しない。
- この制約により、AOSP-backed conclusion は高信頼度にできない。

## 関連ファイル

未確認。Android 17 AOSP タグ取得後に、少なくとも以下の候補を確認する必要がある。

- `frameworks-base` 内の compat framework 定義ファイルで、static final field / reflection / JNI field update に関連する Change ID。
- `frameworks-base` 内に runtime behavior を参照する framework-side gate があるか。
- 実際の reflection / JNI enforcement は ART 側に存在する可能性があるが、本ミッションの AOSP evidence 範囲は `frameworks-base` の tag 比較に限定されているため、必要に応じて別途調査範囲の拡張判断が必要。

## 確認したソース文脈

Android 17 AOSP タグがないため、source context は未レビュー。

| ファイル / シンボル | Android 16 基準挙動 | Android 17 挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| 未レビュー | 未レビュー | 未レビュー | Android 17 タグがないため、公式文書の記述を AOSP diff で検証できない。 |

必須記入項目:
- Entry point / caller: 未確認。想定される entry point は Java reflection field write と JNI static field write だが、AOSP evidence としては未採用。
- Relevant class or service responsibility: 未確認。
- Runtime path from app API / system event to changed code: 未確認。
- 除外した無関係なコードパス: Android 17 タグ不在のため、source path の採否判断自体を保留。

## 差分解釈

| 確認した差分 | 解釈 | 挙動変更との関係 | 信頼度 |
| --- | --- | --- | --- |
| Android 17 タグ間差分は利用不可 | ソース差分の種別はまだ分類できない | 公式文書の static final field enforcement を source diff で裏取りできていない | 低 |

必須分類:
- Added behavior: 未確認。
- Removed behavior: 未確認。
- Changed condition / gate: 未確認。
- Changed default: 未確認。
- No behavior change found: 未確認。タグ不在のため「no behavior change」とは判断しない。

## 事実

事実:
- 公式 Behavior Change 文書は、Android 17 以上で動作し targetSdkVersion 37 以上のアプリが static final field を変更できないと述べている。
- 公式文書は、reflection で static final field を変更しようとすると `IllegalAccessException` が発生すると述べている。
- 公式文書は、JNI API で static final field を変更しようとするとアプリが crash すると述べている。
- ローカル `frameworks-base` には `android-16.0.0_r4` タグがある。
- ローカル `frameworks-base` には `android-17*` タグがない。
- 調査時点で `frameworks-base` working tree は clean。

観察:
- 公式ページ種別と原文は targetSdkVersion 37 以上の変更を示している。
- 原文は Android 17 以上という OS 条件も明示している。
- static final field を変更しようとする reflection / JNI usage が追加条件になる。
- AOSP タグがないため、実装が本当に targetSdkVersion 37 gate で制御されているかは未確認。
- Compat framework entry の有無も未確認。

仮説:
- Android 17 上で targetSdkVersion 37 以上のアプリに対し、reflection と JNI の static final field write が runtime enforcement により拒否される可能性が高い。
- targetSdkVersion 36 のアプリでは互換性維持のため旧挙動が残る可能性があるが、AOSP gate は未確認のため断定しない。
- 実装本体は `frameworks-base` ではなく ART / runtime 側にある可能性がある。

結論:
- 現時点で顧客向けに確定できるのは、「公式文書上は Android 17 以上かつ targetSdkVersion 37 以上で static final field 書き換えが禁止される」という範囲まで。
- AOSP gate と compat framework default state が未確認のため、主分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

## 適用ゲート根拠

- targetSdkVersion 適用ゲート: 未確認。Android 17 AOSP タグがないため、`targetSdkVersion` / `ApplicationInfo.targetSdkVersion` 検索は実施していない。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。Android 17 AOSP タグがないため、`CompatChanges.isChangeEnabled` / `@ChangeId` / `@EnabledAfter` / `@EnabledSince` 検索は実施していない。
- @EnabledAfter / @EnabledSince / default state: 未確認。
- Build.VERSION / SDK_INT 適用ゲート: 未確認。
- DeviceConfig / resources config: 未確認。
- Permission/AppOps 適用ゲート: 未確認。
- Manifest/property 適用ゲート: 未確認。
- 適用ゲート未検出: 未判断。検索不能のため「gate なし」とは扱わない。
- 適用ゲートの結論: 未確認。公式文書上の Android 17+ / targetSdkVersion 37+ 条件はあるが、AOSP evidence が不足している。
- ソース文脈からの推論: source context 未取得のため不可。

確認済み:
- `frameworks-base` checkout status。
- `android-16.0.0_r4` tag の存在。
- `android-17*` tag の存在。

未確認:
- Android 17 implementation files。
- Android 17 compat framework definitions。
- ART / runtime 側の reflection / JNI enforcement 実装。

理由:
- Android 17 target タグがローカル checkout に存在しないため、タグ間 diff による platform evidence が作れない。

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
- targetSdkVersion 37 へ上げないアプリ。ただし、これは公式文書からの一次判断であり、AOSP gate は未確認。

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

このセクションは、公式文書と AOSP evidence から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1: 設定値を reflection で差し替えるアプリ / SDK

- 対象サービス例: A/B test SDK、feature flag framework、社内 debug tool。
- 影響を受ける実装パターン: `static final` fields を reflection / Unsafe / instrumentation で書き換える実装。
- 発生条件: Android 17 / targetSdkVersion 37 で `static final` fields が unmodifiable と扱われる場合。
- ユーザーに見える症状: feature flag が切り替わらない、debug menu の変更が反映されない、初期化時に例外が出る可能性。
- 開発・運用への影響: runtime patching 前提の設定更新、テスト環境の差し替え、SDK initialization の見直しが必要になる可能性。
- 推奨対応候補: mutable holder / DI / build-time config に移行し、`static final` 直接変更を避ける。
- 根拠: 公式 Behavior Change statement と report の AOSP evidence limitation。
- 信頼度: 低
- 注意: どの API path で例外または no-op になるかは Android 17 AOSP タグ待ち。

## 例2: テスト / mocking framework に依存するアプリ

- 対象サービス例: 大規模 Android app の instrumented test、E2E test、SDK integration test。
- 影響を受ける実装パターン: production code の `static final` constant を test runtime で書き換える test utility。
- 発生条件: targetSdkVersion 37 の test build / app process で static final mutation が拒否される場合。
- ユーザーに見える症状: 直接の本番ユーザー影響は限定的だが、テスト失敗により release validation が詰まる可能性。
- 開発・運用への影響: test fixture、mocking strategy、CI の Android 17 対応が必要になる可能性。
- 推奨対応候補: constructor injection、interface abstraction、test-only build variants に移行する。
- 根拠: 公式 statement と report の targetSdkVersion gate 未確認事項。
- 信頼度: 低
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

- Android 17 AOSP タグ公開後、static final field enforcement の diff と compat Change ID を再調査する。
- テスト用の static final override がある場合、test-only mechanism と production code を分離する。

---

# 検証方法

## 検証マトリクス

| 端末 OS | targetSdkVersion | Compat flag | 期待される挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | default | Android 16 baseline。static final field 変更 attempt の挙動は Android 17 タグ比較待ち。 |
| Android 17 | 36 | default | 未確認。公式文書上は targetSdkVersion 37 以上向けのため旧挙動維持が期待されるが、AOSP gate は未確認。 |
| Android 17 | 37 | default | 公式文書上は static final field 変更が拒否される。reflection は `IllegalAccessException`、JNI は app crash。 |
| Android 17 | 36 | force-enabled（利用可能な場合） | 未確認。Compat Change ID 未確認。 |
| Android 17 | 37 | force-disabled（利用可能な場合） | 未確認。Compat Change ID 未確認。 |

## 手順

- targetSdk変更: test app を targetSdkVersion 36 と 37 で build し、Android 17 上の挙動差を確認する。
- Compat framework コマンド: Change ID 未確認のため未定。Android 17 タグ / compat page 確認後に追加する。
- テスト方法: static final field を reflection で変更する最小再現コードと、JNI で変更する最小 native test を用意する。
- 再現手順: Android 17 上で targetSdkVersion 36 / 37 の両 APK を実行し、reflection の例外種別、JNI crash、stack trace、compat flag 有無を比較する。
- 期待結果: targetSdkVersion 37 では公式文書どおり static final field 変更が拒否される。targetSdkVersion 36 の結果は AOSP gate 確認待ち。

---

# 結論

公式文書は、Android 17 以上で動作し targetSdkVersion 37 以上のアプリが static final field を変更できなくなると説明している。主な互換性リスクは、reflection または JNI で static final field を実行時に書き換えるコードである。

一方で、ローカル `frameworks-base` に Android 17 AOSP タグがないため、実装差分、targetSdkVersion gate、Compat Change ID、default state を検証できていない。現時点の主分類は `UNKNOWN_NEEDS_MORE_EVIDENCE`、信頼度は低とする。

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
- Android 17 AOSP タグ公開後に再調査するか、公式 documentation ベースの暫定注意喚起として扱うかを判断する。

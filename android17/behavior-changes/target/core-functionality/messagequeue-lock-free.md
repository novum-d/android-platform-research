# MessageQueue の新しい lock-free 実装

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

関連文書:
- https://developer.android.com/about/versions/17/changes/messagequeue
- https://developer.android.com/reference/android/os/MessageQueue

セクション:
New lock-free implementation of MessageQueue

ページ種別:
- Apps targeting Android 17 or higher

### 分類スナップショット

主分類（Primary classification）:
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- targetSdkVersion 37 以上のアプリに適用される変更として扱うのが自然。
- ただし、Android 17 AOSP タグがローカル `frameworks-base` に存在しないため、AOSP gate、Compat Change ID、default state を検証できていない。

早見表:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 未確認 | 公式文書は「apps targeting Android 17 (API level 37) or higher」と述べるが、AOSP gate は未確認。 |
| targetSdkVersion 37 以上が必要か | 可能性は高いが未確認 | 公式文書ページ種別と原文は targetSdkVersion 37+ を示す。AOSP evidence は未取得。 |
| 追加の実行時条件があるか | 未確認 | 公式抜粋からは追加条件は確認できない。詳細 guidance と AOSP タグ確認が必要。 |
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
- Android version: Android 17 であることが前提。ただし AOSP タグ未取得。
- targetSdkVersion: 公式文書上は 37 以上が条件と読める。AOSP gate 未確認。
- Device/form factor: 不明。
- Permission/API/component condition: `android.os.MessageQueue` の private field / private method へ reflection している場合に互換性リスクがあると公式文書が述べる。
- App state/process condition: 不明。

Compat framework:
- Change ID: 未確認
- 変更名: 未確認
- 既定状態: 未確認
- テスト時の切り替え可否: 未確認

分類信頼度:
- 低

分類根拠:
- 公式ドキュメントページ: `behavior-changes-17`
- 検証対象の適用条件文: "apps targeting Android 17 (API level 37) or higher receive..."
- AOSP targetSdk gate: 未確認。ローカル `frameworks-base` に `android-17*` タグがない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# エグゼクティブサマリー

Android 17 では、targetSdkVersion 37 以上のアプリに対して `android.os.MessageQueue` の新しい lock-free 実装が適用される、と公式 Behavior Change 文書は説明している。性能改善と missed frame 削減が目的だが、`MessageQueue` の private field / private method を reflection で参照しているアプリやライブラリは壊れる可能性がある。

ただし、現時点のローカル `frameworks-base` には Android 17 AOSP タグがないため、AOSP 上の targetSdkVersion gate、Compat Change ID、default state は未確認である。顧客向けの最終分類には、Android 17 AOSP タグ公開後の再調査が必要。

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
- New lock-free implementation of MessageQueue

検証対象の原文:

> apps targeting Android 17 (API level 37) or higher receive a new lock-free implementation

同じセクションでは、新しい `android.os.MessageQueue` 実装が性能改善と missed frame 削減を目的としており、`MessageQueue` の private fields / methods を reflection している client は壊れる可能性があると説明している。また、mitigation strategies について MessageQueue behavior change guidance を参照するよう案内している。

## 解釈

公式文書は、この変更を「Android 17 以上を targetSdkVersion として指定するアプリ向けの Behavior Change」として掲載している。原文も `apps targeting Android 17 (API level 37) or higher` と述べているため、一次分類は targetSdkVersion 37 以上で有効になる変更と考えられる。

互換性リスクは、通常の public API 利用ではなく、`MessageQueue` の private field / private method に reflection しているコードに集中する。該当する可能性があるのは、独自のメインスレッド監視、フレーム落ち検知、メッセージキュー計測、古い互換性回避コード、またはそれらを含むサードパーティ SDK である。

---

# 変更内容

公式文書上の変更点:
- Android 17 で `android.os.MessageQueue` に新しい lock-free 実装が導入される。
- 新実装は性能改善と missed frame 削減を目的としている。
- `MessageQueue` の private field / private method を reflection する client は壊れる可能性がある。

AOSP で未確認の点:
- Android 16 baseline 実装から Android 17 実装への具体的な source diff。
- lock-free 実装の導入箇所、entry point、caller。
- targetSdkVersion 37 gate の実装箇所。
- Compat Change ID と default state。
- opt-out または temporary override の有無。

詳細 guidance で追加確認した点:
- legacy implementation では `MessageQueue.mMessages` などの private field を reflection で参照する実装が存在したが、新しい lock-free implementation では internal data structure が変わる。
- binary compatibility のため `mMessages` field は残るが、新実装では queue に message があるかどうかに関係なく常に `null` と説明されている。
- Espresso は 3.7.0 以上へ更新することが推奨されている。
- Robolectric は 4.17 以上へ更新し、`@LooperMode(LEGACY)` を使っている場合は `@LooperMode(PAUSED)` へ移行することが推奨されている。
- debuggable build では `adb am compat enable USE_NEW_MESSAGEQUEUE <package>` で targetSdkVersion を上げずに挙動を test できる。
- targetSdkVersion 37 以上では default enabled と説明されており、原因切り分けのため `adb am compat disable USE_NEW_MESSAGEQUEUE <package>` で一時的に legacy lock-based implementation へ戻せる。

## 適用条件（Applicability）

この変更の適用条件は、現時点では公式文書からの一次判断に留まる。AOSP tag が未取得のため、確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

### OS アップデート時の挙動

- Android 17 にアップデートしただけで適用されるか: 未確認
- targetSdkVersion に依存しない根拠: なし。公式文書は targetSdkVersion 37 以上を示す。
- Android 16 以前での挙動: AOSP タグ比較未実施。Android 16 baseline source は Android 17 タグとの比較ができないため、この調査では platform evidence として採用していない。

### targetSdkVersion 37 以上での挙動

- targetSdkVersion 37 以上で適用されるか: 公式文書上は Yes と読めるが、AOSP gate は未確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: 未確認。公式抜粋は「Beginning with Android 17」と述べるため、少なくとも Android 17 platform behavior として扱う。
- opt-out / temporary override の有無: 未確認。compat framework evidence 未確認。

### その他の条件

- device/form factor: 公式抜粋では条件なし。
- permission: 公式抜粋では条件なし。
- API usage: `MessageQueue` private field / private method への reflection が互換性リスク条件。
- manifest attribute: 未確認。
- component boundary: アプリプロセス内の `MessageQueue` 利用が対象と考えられるが、AOSP 未確認。

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

未確認。Android 17 AOSP タグ取得後に、少なくとも以下の候補をタグ比較で確認する必要がある。

- `core/java/android/os/MessageQueue.java`
- `core/java/android/os/Looper.java`
- `core/java/android/os/Handler.java`
- native peer が存在する場合の `android_os_MessageQueue` 関連実装
- compat framework 定義ファイル内の `USE_NEW_MESSAGEQUEUE` / `MessageQueue` / lock-free / targetSdkVersion 37 関連 Change ID

## 確認したソース文脈

Android 17 AOSP タグがないため、source context は未レビュー。

| ファイル / シンボル | Android 16 基準挙動 | Android 17 挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| 未レビュー | 未レビュー | 未レビュー | Android 17 タグがないため、公式文書の記述を AOSP diff で検証できない。 |

必須記入項目:
- Entry point / caller: 未確認。
- Relevant class or service responsibility: `MessageQueue` が app thread の message dispatch queue として関連することは API 名から推定できるが、本調査では AOSP evidence として採用しない。
- Runtime path from app API / system event to changed code: 未確認。
- 除外した無関係なコードパス: Android 17 タグ不在のため、source path の採否判断自体を保留。

## 差分解釈

| 確認した差分 | 解釈 | 挙動変更との関係 | 信頼度 |
| --- | --- | --- | --- |
| Android 17 タグ間差分は利用不可 | ソース差分の種別はまだ分類できない | 公式文書の lock-free 実装導入を source diff で裏取りできていない | 低 |

必須分類:
- Added behavior: 未確認。
- Removed behavior: 未確認。
- Changed condition / gate: 未確認。
- Changed default: 未確認。
- No behavior change found: 未確認。タグ不在のため「no behavior change」とは判断しない。

## 事実

事実:
- 公式 Behavior Change 文書は、Android 17 から targetSdkVersion 37 以上のアプリが新しい lock-free `MessageQueue` 実装を受け取ると述べている。
- 公式文書は、新実装が性能改善と missed frame 削減を目的とすると述べている。
- 公式文書は、`MessageQueue` の private field / private method に reflection する client が壊れる可能性を述べている。
- ローカル `frameworks-base` には `android-16.0.0_r4` タグがある。
- ローカル `frameworks-base` には `android-17*` タグがない。
- 調査時点で `frameworks-base` working tree は clean。

観察:
- 公式ページ種別と原文は targetSdkVersion 37 以上の変更を示している。
- AOSP タグがないため、実装が本当に targetSdkVersion 37 gate で制御されているかは未確認。
- Compat framework entry の有無も未確認。

仮説:
- Android 17 上で targetSdkVersion 37 以上のアプリにのみ新実装が有効化され、targetSdkVersion 36 のアプリには旧挙動が維持される可能性がある。
- private API reflection をしていない通常の `Handler` / `Looper` 利用アプリでは、互換性破壊より性能面の影響が中心になる可能性がある。

結論:
- 現時点で顧客向けに確定できるのは、「公式文書上は targetSdkVersion 37 以上で注意すべき MessageQueue 実装変更がある」という範囲まで。
- AOSP gate と compat framework default state が未確認のため、適用分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

## 適用ゲート根拠

- targetSdkVersion 適用ゲート: 未確認。Android 17 AOSP タグがないため、`targetSdkVersion` / `ApplicationInfo.targetSdkVersion` 検索は実施していない。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。Android 17 AOSP タグがないため、`CompatChanges.isChangeEnabled` / `@ChangeId` / `@EnabledAfter` / `@EnabledSince` 検索は実施していない。
- @EnabledAfter / @EnabledSince / default state: 未確認。
- Build.VERSION / SDK_INT 適用ゲート: 未確認。
- DeviceConfig / resources config: 未確認。
- Permission/AppOps 適用ゲート: 未確認。
- Manifest/property 適用ゲート: 未確認。
- 適用ゲート未検出: 未判断。検索不能のため「gate なし」とは扱わない。
- 適用ゲートの結論: 未確認。公式文書上の targetSdkVersion 37 条件はあるが、AOSP evidence が不足している。
- ソース文脈からの推論: source context 未取得のため不可。

確認済み:
- `frameworks-base` checkout status。
- `android-16.0.0_r4` tag の存在。
- `android-17*` tag の存在。

未確認:
- Android 17 implementation files。
- Android 17 compat framework definitions。
- `USE_NEW_MESSAGEQUEUE` の AOSP compat definition / default state。

理由:
- Android 17 target タグがローカル checkout に存在しないため、タグ間 diff による platform evidence が作れない。

---

# 影響分析

## 影響を受けるアプリ

影響を受ける可能性があるアプリ:
- targetSdkVersion 37 以上への更新を予定しているアプリ。
- `android.os.MessageQueue` の private field / private method を reflection で参照しているアプリ。
- メインスレッド監視、ANR 監視、フレーム落ち検知、message queue 計測などのために private implementation detail に依存しているアプリまたは SDK。
- 古い performance monitoring SDK、diagnostics SDK、hooking / instrumentation 系 SDK を組み込んでいるアプリ。

## 影響を受けにくいアプリ

影響が限定的と考えられるケース:
- `Handler`、`Looper`、`MessageQueue` の public API のみを使っているアプリ。
- `MessageQueue` の private field / private method に reflection していないアプリ。
- targetSdkVersion 37 へ上げないアプリ。ただし、これは公式文書からの一次判断であり、AOSP gate は未確認。

---

# 顧客影響

## 影響度

- 人間による判断が必要

※ 最終 severity / priority は人間が判断する。このレポートでは確定しない。

## ビジネス影響

- ユーザー影響: private API reflection が壊れる場合、起動時 crash、監視機能の停止、UI thread 計測の不整合が発生する可能性がある。
- 運用影響: サードパーティ SDK が原因の場合、アプリ側では直接コードが見えにくく、SDK 更新や vendor 確認が必要になる可能性がある。
- 開発影響: targetSdkVersion 37 更新前に reflection usage の棚卸しと Android 17 テストが必要。

---

# サービス影響例

このセクションは、公式文書と AOSP evidence から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1: UI 操作が多い一般アプリ

- 対象サービス例: チャット、SNS、EC、ニュースなど、メインスレッドで UI 更新とイベント処理が多いアプリ。
- 影響を受ける実装パターン: `Handler` / `Looper` / `MessageQueue` の待機・dispatch timing に暗黙依存している実装。
- 発生条件: Android 17 の MessageQueue 実装変更が、アプリの timing assumption とずれる場合。
- ユーザーに見える症状: スクロール、タップ反応、画面遷移、アニメーションの timing が変わる可能性。
- 開発・運用への影響: flaky な UI test、race condition、main thread timing に依存した処理の再検証が必要になる可能性。
- 推奨対応候補: main thread blocking、busy wait、implicit ordering 依存を棚卸しし、Android 17 で UI / instrumentation test を実施する。
- 根拠: 公式 Behavior Change statement と report の AOSP evidence limitation。
- 信頼度: 低
- 注意: 実サービスで発生確認した事実ではない。AOSP タグ入手後に MessageQueue diff と gate を再確認する。

## 例2: SDK / framework が Looper timing に依存するアプリ

- 対象サービス例: analytics SDK、広告 SDK、リアルタイム通信 SDK、独自 UI framework を組み込むアプリ。
- 影響を受ける実装パターン: `postAtFrontOfQueue`、synchronous barrier、idle handler、message ordering に強く依存する処理。
- 発生条件: MessageQueue の lock-free 化により、従来の timing / ordering 前提が露呈する場合。
- ユーザーに見える症状: callback の順序違い、初期化遅延、画面表示直後のイベント欠落。
- 開発・運用への影響: SDK vendor への確認、race condition test、Android 17 beta / preview での回帰確認が必要になる可能性。
- 推奨対応候補: SDK 更新、callback ordering を明示した test、メインスレッド依存の削減。
- 根拠: MessageQueue behavior change の公式説明と report の missing AOSP evidence。
- 信頼度: 低
- 注意: 具体的な broken pattern は AOSP evidence と実機検証待ち。

---

# 対応候補

## 必須対応（Must）

- `android.os.MessageQueue` の private field / private method へ reflection している自社コードがないか確認する。
- サードパーティ SDK に `MessageQueue` reflection、main thread hook、message queue instrumentation が含まれていないか確認する。
- targetSdkVersion 37 更新前に Android 17 device / emulator で起動、画面遷移、メインスレッド監視、performance monitoring をテストする。
- Espresso を使う場合は 3.7.0 以上へ更新する。
- Robolectric を使う場合は 4.17 以上へ更新し、`@LooperMode(LEGACY)` 依存があれば `@LooperMode(PAUSED)` へ移行する。

## 推奨対応（Recommended）

- private implementation detail への依存を public API ベースの実装に置き換える。
- Android 17 の MessageQueue behavior change guidance を確認し、公式 mitigation strategy に沿って修正する。
- performance monitoring / diagnostics SDK を Android 17 対応版に更新する。
- reflection failure を crash ではなく機能無効化として扱えるように defensive coding を入れる。

## 任意対応（Optional）

- Android 17 AOSP タグ公開後、`MessageQueue` 関連 diff と compat Change ID を再調査する。
- UI jank / frame metrics の before / after を測定し、性能面の副作用がないか確認する。

---

# 検証方法

## 検証マトリクス

| 端末 OS | targetSdkVersion | Compat flag | 期待される挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | default | Android 16 baseline。lock-free implementation の Android 17 変更は適用されない想定。ただし本調査では AOSP baseline 未比較。 |
| Android 17 | 36 | default | 未確認。公式文書上は targetSdkVersion 37 以上向けのため旧挙動維持が期待されるが、AOSP gate は未確認。 |
| Android 17 | 37 | default | 公式文書上は新しい lock-free `MessageQueue` 実装が適用される。private reflection client は破損リスクあり。 |
| Android 17 | 36 | force-enabled（利用可能な場合） | 未確認。Compat Change ID 未確認。 |
| Android 17 | 37 | force-disabled（利用可能な場合） | 未確認。Compat Change ID 未確認。 |

## 手順

- targetSdk変更: test app を targetSdkVersion 36 と 37 で build し、Android 17 上の挙動差を確認する。
- Compat framework コマンド: 公式 guidance 上は debuggable build で次の command を使える。

```bash
adb am compat enable USE_NEW_MESSAGEQUEUE <your-package-name>
adb am compat disable USE_NEW_MESSAGEQUEUE <your-package-name>
```

- テスト方法: `MessageQueue` private reflection を行う最小再現コードと、public API のみを使う control app を比較する。
- 再現手順: Android 17 上で targetSdkVersion 36 / 37 の両 APK を実行し、reflection 成否、crash、main thread monitoring の結果を比較する。
- 期待結果: targetSdkVersion 37 で新実装により private field / method の reflection 前提が崩れる可能性がある。targetSdkVersion 36 の結果は AOSP gate 確認待ち。

---

# 結論

公式文書は、Android 17 で targetSdkVersion 37 以上のアプリに新しい lock-free `android.os.MessageQueue` 実装が適用されると説明している。主な互換性リスクは、`MessageQueue` private field / private method への reflection に依存するコードである。

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

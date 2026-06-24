# MessageQueue の新しい lock-free 実装

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

関連文書:
- https://developer.android.com/about/versions/17/changes/messagequeue
- https://developer.android.com/reference/android/os/MessageQueue

セクション:
New lock-free implementation of MessageQueue

ページ種別:
- Apps targeting Android 17 or higher

### 分類スナップショット

主分類（Primary classification）:
- TARGET_SDK_37

公式文書からの初期適用条件判断:
- targetSdkVersion 37 以上のアプリに適用される変更として扱う。
- AOSP では `USE_NEW_MESSAGEQUEUE` Change ID が `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)` として定義され、Android 16 / API 36 より後、すなわち targetSdkVersion 37 以上で デフォルト有効 になる。

早見表:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | No | `USE_NEW_MESSAGEQUEUE` は `@EnabledAfter(targetSdkVersion = BAKLAVA)` の compat change。targetSdkVersion 36 では デフォルト有効 ではない。 |
| targetSdkVersion 37 以上が必要か | Yes | 公式文書と AOSP の `@EnabledAfter(BAKLAVA)` が一致する。 |
| 追加の実行時条件があるか | Yes | 互換性リスクは `MessageQueue` private field / private method への reflection に依存するコードで顕在化する。 |
| Compat Change ID が関係するか | Yes | `USE_NEW_MESSAGEQUEUE = 421623328L`。 |

### 調査日

2026-06-18

### 信頼度

- High

### 適用条件分類

適用される条件:
- [ ] Android 17 上の全アプリ（targetSdkVersion に依存しない）
- [x] Android 17 以上で targetSdkVersion >= 37
- [ ] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [ ] 未確認 / 追加根拠が必要

必要な実行時条件:
- Android version: Android 17 以上。
- targetSdkVersion: 37 以上。AOSP の `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)` により、Android 16 / API 36 より後で デフォルト有効。
- Device/form factor: 条件なし。
- Permission/API/component condition: `android.os.MessageQueue` の private field / private method へ reflection している場合に互換性リスクがあると公式文書が述べる。
- App state/process condition: アプリプロセスで `MessageQueue` が生成されるときに実装選択が行われる。

Compat framework:
- Change ID: `421623328`
- 変更名: `USE_NEW_MESSAGEQUEUE`
- 既定状態: targetSdkVersion 37 以上で デフォルト有効。targetSdkVersion 36 では デフォルト無効。
- テスト時の切り替え可否: 公式 guidance は `adb am compat enable/disable USE_NEW_MESSAGEQUEUE <package>` を案内している。

分類信頼度:
- High

分類根拠:
- 公式ドキュメントページ: `behavior-changes-17`
- 検証対象の適用条件文: "apps targeting Android 17 (API level 37) or higher receive..."
- AOSP targetSdk gate: `core/java/android/os/CombinedMessageQueue/MessageQueue.java` の `USE_NEW_MESSAGEQUEUE` が `@EnabledAfter(targetSdkVersion = android.os.Build.VERSION_CODES.BAKLAVA)`。
- Compat framework entry: `USE_NEW_MESSAGEQUEUE = 421623328L`。`computeUseConcurrent()` が `CompatChanges.isChangeEnabled(USE_NEW_MESSAGEQUEUE)` を見て concurrent implementation を選択する。

---

# エグゼクティブサマリー

Android 17 では、targetSdkVersion 37 以上のアプリに対して `android.os.MessageQueue` の新しい lock-free 実装が適用される、と公式 Behavior Change 文書は説明している。性能改善と missed frame 削減が目的だが、`MessageQueue` の private field / private method を reflection で参照しているアプリやライブラリは壊れる可能性がある。

AOSP では `USE_NEW_MESSAGEQUEUE = 421623328L` が `@EnabledAfter(targetSdkVersion = BAKLAVA)` として定義され、`MessageQueue.computeUseConcurrent()` がこの compat change を見て新しい concurrent implementation を選択する。したがって OS アップデートだけではなく、Android 17 上で targetSdkVersion 37 以上にしたときの変更として分類できる。

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

AOSP で確認した点:
- Android 17 tag には `core/java/android/os/CombinedMessageQueue/MessageQueue.java` があり、legacy implementation と concurrent implementation を同一 class 内で切り替える。
- `USE_NEW_MESSAGEQUEUE = 421623328L` は `@ChangeId` かつ `@EnabledAfter(targetSdkVersion = android.os.Build.VERSION_CODES.BAKLAVA)`。
- `computeUseConcurrent()` は `CompatChanges.isChangeEnabled(USE_NEW_MESSAGEQUEUE)` または `Flags.useConcurrentMessageQueueInApps()` が true の場合に concurrent implementation を選ぶ。
- `mMessages` は binary compatibility のため残るが、`@UnsupportedAppUsage(maxTargetSdk = Build.VERSION_CODES.BAKLAVA)` として legacy 互換性の境界が置かれている。

詳細 guidance で追加確認した点:
- legacy implementation では `MessageQueue.mMessages` などの private field を reflection で参照する実装が存在したが、新しい lock-free implementation では internal data structure が変わる。
- binary compatibility のため `mMessages` field は残るが、新実装では queue に message があるかどうかに関係なく常に `null` と説明されている。
- Espresso は 3.7.0 以上へ更新することが推奨されている。
- Robolectric は 4.17 以上へ更新し、`@LooperMode(LEGACY)` を使っている場合は `@LooperMode(PAUSED)` へ移行することが推奨されている。
- debuggable build では `adb am compat enable USE_NEW_MESSAGEQUEUE <package>` で targetSdkVersion を上げずに挙動を test できる。
- targetSdkVersion 37 以上では デフォルト有効 と説明されており、原因切り分けのため `adb am compat disable USE_NEW_MESSAGEQUEUE <package>` で一時的に legacy lock-based implementation へ戻せる。

## 適用条件

この変更は、公式文書と AOSP の compat gate の両方から、Android 17 上で targetSdkVersion 37 以上のアプリに デフォルト有効 になる変更として扱う。

### OS アップデート時の挙動

- Android 17 にアップデートしただけで適用されるか: No。targetSdkVersion 36 のままでは `USE_NEW_MESSAGEQUEUE` は デフォルト有効 ではない。
- targetSdkVersion に依存しない根拠: なし。AOSP は `@EnabledAfter(targetSdkVersion = BAKLAVA)` を使う。
- Android 16 以前での挙動: legacy `MessageQueue` implementation が基準。Android 17 の combined / concurrent implementation は `android-17.0.0_r1` で確認した差分。

### targetSdkVersion 37 以上での挙動

- targetSdkVersion 37 以上で適用されるか: Yes。`USE_NEW_MESSAGEQUEUE` が `@EnabledAfter(BAKLAVA)` で デフォルト有効。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: Android 17 platform の `frameworks-base` 実装に依存する。Android 16 platform には本調査対象の new implementation はない。
- opt-out / temporary override の有無: debuggable build では `adb am compat disable USE_NEW_MESSAGEQUEUE <package>` で切り分けできる。公式 guidance と AOSP Change ID が一致する。

### その他の条件

- device/form factor: 公式抜粋では条件なし。
- permission: 公式抜粋では条件なし。
- API usage: `MessageQueue` private field / private method への reflection が互換性リスク条件。
- manifest attribute: なし。
- component boundary: アプリプロセス内の `MessageQueue` implementation selection。`Handler` / `Looper` の public API path から到達する。

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
- ソース根拠 は `android-16.0.0_r4` と `android-17.0.0_r1` の明示的なタグ比較、および `android-17.0.0_r1` 上の該当 symbol 確認に限定した。
- `frameworks-base` working tree は clean のため、ローカル作業ツリーの変更 を platform 根拠 として誤採用するリスクは確認されていない。

## 関連ファイル

- `core/java/android/os/CombinedMessageQueue/MessageQueue.java`
- `core/java/android/os/CombinedDeliMessageQueue/MessageQueue.java`
- `core/java/android/os/LegacyMessageQueue/MessageQueue.java`
- `core/java/android/os/Looper.java`
- `core/java/android/os/Handler.java`
- `core/java/android/app/ActivityThread.java`
- `core/java/android/app/compat/CompatChanges.java`
- `core/java/com/android/internal/compat/CompatibilityRules.java`

## 確認したソース文脈

| ファイル / シンボル | Android 16 基準挙動 | Android 17 挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `core/java/android/os/CombinedMessageQueue/MessageQueue.java` / `USE_NEW_MESSAGEQUEUE` | Android 16 tag にはこの combined concurrent implementation file は存在しない。legacy queue が既定。 | `@ChangeId` `USE_NEW_MESSAGEQUEUE = 421623328L` が追加され、`@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)` で デフォルト有効 条件を定義する。 | 公式文書の「targetSdkVersion 37 以上で新 MessageQueue 実装」を直接 gate する compat change である。 |
| `CombinedMessageQueue/MessageQueue.java` / `computeUseConcurrent()` | legacy implementation を使う。 | `CompatChanges.isChangeEnabled(USE_NEW_MESSAGEQUEUE)` または `Flags.useConcurrentMessageQueueInApps()` が true の場合に concurrent implementation を選ぶ。 | アプリプロセスでどの MessageQueue implementation が使われるかを決める実行時 gate である。 |
| `CombinedMessageQueue/MessageQueue.java` / `mMessages` | legacy queue の private linked-list head として reflection 依存が成立しうる。 | `mMessages` は binary compatibility のため残るが、`@UnsupportedAppUsage(maxTargetSdk = Build.VERSION_CODES.BAKLAVA)` により legacy 互換境界が置かれる。 | 公式文書が警告する private field reflection 破損リスクと対応する。 |
| `core/java/android/app/ActivityThread.java` / process start | Android 16 では combined queue 選択のための初期化 path はない。 | process startup で `Looper.prepareMainLooper()` より前に MessageQueue 関連の process-level 初期化が行われる。 | `MessageQueue` は app main looper 作成時に生成されるため、process lifetime の早い段階で implementation が決まる。 |
| `core/java/android/os/Handler.java` / `enqueueMessage()` | legacy queue へ message を enqueue する。 | `onBeforeEnqueue()` の呼び出し位置変更と sentinel handler 追加が入り、new queue 実装に合わせた内部処理が追加される。 | public `Handler` 利用から changed queue implementation へ到達する通常のアプリ API path である。 |
| `core/java/android/os/Looper.java` / dispatch path | legacy `MessageQueue.next()` から取得した message を dispatch する。 | dispatch path 周辺に新しい内部処理が追加されるが、`USE_NEW_MESSAGEQUEUE` の gate 本体は `MessageQueue` 側にある。 | `MessageQueue` の変更が app main thread dispatch path と結びつくことを確認するためにレビューした。 |

必須記入項目:
- Entry point / caller: app code の `Handler.post()` / `sendMessage()` などから `Handler.enqueueMessage()` を経由し、`MessageQueue.enqueueMessage()` と `Looper.loopOnce()` の dispatch path に到達する。
- Relevant class or service responsibility: `MessageQueue` は `Looper` に紐づく thread-local message dispatch queue で、UI thread / background looper thread の message scheduling を担う。
- Runtime path from app API / system event to changed code: app API / framework event -> `Handler` -> `MessageQueue` -> `Looper.loopOnce()` -> `Handler.dispatchMessage()`。
- 除外した無関係なコードパス: `Looper.LOOPER_CLEARS_THREAD_INTERRUPTED` は同じ `Looper.java` 差分に含まれる別 Change ID であり、本件の `USE_NEW_MESSAGEQUEUE` gate とは別変更として除外した。

## 差分解釈

| 確認した差分 | 解釈 | 挙動変更との関係 | 信頼度 |
| --- | --- | --- | --- |
| `CombinedMessageQueue/MessageQueue.java` と `CombinedDeliMessageQueue/MessageQueue.java` が Android 17 tag に存在し、`USE_NEW_MESSAGEQUEUE` compat change を定義する。 | added behavior / changed default gate | Android 17 で新しい concurrent / lock-free queue implementation を導入し、targetSdkVersion 37 以上で デフォルト有効 にする。 | High |
| `computeUseConcurrent()` が `CompatChanges.isChangeEnabled(USE_NEW_MESSAGEQUEUE)` を確認する。 | changed condition / gate | targetSdkVersion 36 と 37 で expected behavior が分かれる根拠。 | High |
| `mMessages` に `maxTargetSdk = BAKLAVA` の unsupported app usage 境界が置かれる。 | changed compatibility boundary | private field reflection 依存が targetSdkVersion 37 で互換性リスクになる説明を補強する。 | High |
| `Handler.java` / `Looper.java` に MessageQueue 周辺の内部変更がある。 | implementation support changes | public API path から新 implementation に到達することを補強するが、gate の主根拠ではない。 | Medium |

必須分類:
- Added behavior: new concurrent / lock-free MessageQueue implementation。
- Removed behavior: public API の削除は確認していない。
- Changed condition / gate: `USE_NEW_MESSAGEQUEUE` compat change が targetSdkVersion 37 以上で デフォルト有効。
- Changed default: targetSdkVersion 37 以上では legacy implementation ではなく new implementation が default。
- No behavior change found: 該当しない。

## 事実

事実:
- 公式 Behavior Change 文書は、Android 17 から targetSdkVersion 37 以上のアプリが新しい lock-free `MessageQueue` 実装を受け取ると述べている。
- 公式文書は、新実装が性能改善と missed frame 削減を目的とすると述べている。
- 公式文書は、`MessageQueue` の private field / private method に reflection する client が壊れる可能性を述べている。
- ローカル `frameworks-base` には `android-16.0.0_r4` タグがある。
- ローカル `frameworks-base` には `android-17.0.0_r1` タグがある。
- 調査時点で `frameworks-base` working tree は clean。
- AOSP では `USE_NEW_MESSAGEQUEUE = 421623328L` が `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)` として定義されている。
- `computeUseConcurrent()` は `CompatChanges.isChangeEnabled(USE_NEW_MESSAGEQUEUE)` を使って new implementation を選ぶ。

観察:
- 公式ページ種別と原文は targetSdkVersion 37 以上の変更を示している。
- AOSP gate も Android 16 / API 36 より後の targetSdkVersion で有効化されるため、公式文書と一致する。
- `Flags.useConcurrentMessageQueueInApps()` による flag override path も存在するが、顧客向け primary classification は compat change の default state に基づき `TARGET_SDK_37` とする。

仮説:
- private API reflection をしていない通常の `Handler` / `Looper` 利用アプリでは、互換性破壊より性能面の影響が中心になる可能性がある。

結論:
- 公式文書と AOSP gate が一致するため、主分類は `TARGET_SDK_37` とする。
- Android 17 / targetSdkVersion 36 では デフォルト無効、Android 17 / targetSdkVersion 37 では デフォルト有効 と説明できる。

## 適用ゲート根拠

- targetSdkVersion 適用ゲート: `@EnabledAfter(targetSdkVersion = android.os.Build.VERSION_CODES.BAKLAVA)`。Android 17 の targetSdkVersion 37 以上で デフォルト有効。
- CompatChanges.isChangeEnabled / ChangeId: `CompatChanges.isChangeEnabled(USE_NEW_MESSAGEQUEUE)`、Change ID `421623328L`。
- @EnabledAfter / @EnabledSince / default state: `@EnabledAfter(BAKLAVA)`。targetSdkVersion 36 では デフォルト無効、37 以上では デフォルト有効。
- Build.VERSION / SDK_INT 適用ゲート: 明示的な SDK_INT runtime gate は主根拠として確認していない。AOSP tag 自体が Android 17 platform 実装。
- DeviceConfig / resources config: `Flags.useConcurrentMessageQueueInApps()` による platform flag path は存在するが、公式 Behavior Change の targetSdkVersion ゲートとは別の override path として扱う。
- Permission/AppOps 適用ゲート: なし。
- Manifest/property 適用ゲート: なし。
- 適用ゲート未検出: 該当しない。
- 適用ゲートの結論: Android 17 上で targetSdkVersion 37 以上のアプリに デフォルト有効。
- ソース文脈からの推論: app の `Handler` / `Looper` 利用は `MessageQueue` に到達し、queue implementation selection は process-level に評価される。

確認済み:
- `frameworks-base` checkout status。
- `android-16.0.0_r4` tag の存在。
- `android-17.0.0_r1` tag の存在。
- `USE_NEW_MESSAGEQUEUE` Change ID と default state。
- `computeUseConcurrent()` の compat gate。

未確認:
- `Flags.useConcurrentMessageQueueInApps()` の device/config default が OEM image でどう設定されるか。
- private reflection 依存 SDK ごとの実害有無。

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
- targetSdkVersion 37 へ上げないアプリ。AOSP gate 上は targetSdkVersion 36 では デフォルト無効。

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

このセクションは、公式文書と AOSP 根拠 から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1: LINE / Slack / Instagram のような高頻度 UI 更新アプリ

- 具体サービス例: LINE / Slack のチャット画面、Instagram / X の feed、メルカリ / Amazon Shopping の商品一覧。
- 影響を受ける実装パターン: `Handler` / `Looper` / `MessageQueue` の待機・dispatch timing に暗黙依存している実装。
- 発生条件: Android 17 の MessageQueue 実装変更が、アプリの timing assumption とずれる場合。
- ユーザーに見える症状: スクロール、タップ反応、画面遷移、アニメーションの timing が変わる可能性。
- 技術的に起きていること: message enqueue / dispatch / idle callback の timing 前提が変わり、race condition や flaky test が表面化する。
- 開発・運用への影響: flaky な UI test、race condition、main thread timing に依存した処理の再検証が必要になる可能性。
- 推奨対応候補: main thread blocking、busy wait、implicit ordering 依存を棚卸しし、Android 17 で UI / instrumentation test を実施する。
- 根拠: 公式 Behavior Change statement、`USE_NEW_MESSAGEQUEUE` compat gate、`Handler` / `Looper` / `MessageQueue` の AOSP source context。
- 信頼度: Medium
- 注意: 上記サービスで発生確認した事実ではない。具体的な timing regression は個別アプリ / SDK のテストで確認する必要がある。

## 例2: Sentry / Datadog / Firebase Performance を組み込む監視・計測連携

- 具体サービス例: Sentry、Datadog Real User Monitoring、Firebase Performance Monitoring、New Relic Mobile を組み込むアプリ。
- 影響を受ける実装パターン: `postAtFrontOfQueue`、synchronous barrier、idle handler、message ordering に強く依存する処理。
- 発生条件: MessageQueue の lock-free 化により、従来の timing / ordering 前提が露呈する場合。
- ユーザーに見える症状: callback の順序違い、初期化遅延、画面表示直後のイベント欠落。
- 技術的に起きていること: SDK 側の main-thread instrumentation が private timing 前提を持つ場合、イベント収集や frame timing の順序が変わる。
- 開発・運用への影響: SDK vendor への確認、race condition test、Android 17 beta / preview での回帰確認が必要になる可能性。
- 推奨対応候補: SDK 更新、callback ordering を明示した test、メインスレッド依存の削減。
- 根拠: MessageQueue behavior change の公式説明、`mMessages` の legacy 互換境界、`USE_NEW_MESSAGEQUEUE` gate。
- 信頼度: Medium
- 注意: 上記 SDK で発生確認した事実ではない。具体的な broken pattern は SDK 実装と実機検証で確認する必要がある。

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

- UI jank / frame metrics の before / after を測定し、性能面の副作用がないか確認する。

---

# 検証方法

## 検証マトリクス

| 端末 OS | targetSdkVersion | Compat flag | 期待される挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | default | Android 16 baseline。lock-free implementation の Android 17 変更は適用されない想定。ただし本調査では AOSP baseline 未比較。 |
| Android 17 | 36 | default | `USE_NEW_MESSAGEQUEUE` は デフォルト無効。legacy implementation が維持される想定。 |
| Android 17 | 37 | default | 公式文書上は新しい lock-free `MessageQueue` 実装が適用される。private reflection client は破損リスクあり。 |
| Android 17 | 36 | force-enabled | `adb am compat enable USE_NEW_MESSAGEQUEUE <package>` で new implementation を検証できる。 |
| Android 17 | 37 | force-disabled | `adb am compat disable USE_NEW_MESSAGEQUEUE <package>` で legacy implementation に戻して原因切り分けできる。 |

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

公式文書は、Android 17 で targetSdkVersion 37 以上のアプリに新しい lock-free `android.os.MessageQueue` 実装が適用されると説明している。AOSP でも `USE_NEW_MESSAGEQUEUE = 421623328L` が `@EnabledAfter(targetSdkVersion = BAKLAVA)` として定義され、`computeUseConcurrent()` がこの compat change を見て new implementation を選択することを確認した。

主な互換性リスクは、`MessageQueue` private field / private method への reflection に依存するコードである。主分類は `TARGET_SDK_37`、信頼度は High とする。

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
- targetSdkVersion 37 対応時に、MessageQueue private reflection 利用の棚卸しをどの優先度で顧客へ案内するかを判断する。

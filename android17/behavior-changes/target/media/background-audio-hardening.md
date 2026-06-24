# バックグラウンド音声の制限強化

> 役割メモ:
> このファイルは、バックグラウンド音声の制限強化のうち、targetSdkVersion 37 以上で強まる追加条件を中心に扱う。
> Android 17 上の全アプリに関係する共通制限は [all/media/background-audio-hardening.md](../../all/media/background-audio-hardening.md) を参照する。

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
- https://developer.android.com/about/versions/17/behavior-changes-17

関連文書:
- https://developer.android.com/about/versions/17/behavior-changes-all
- https://developer.android.com/about/versions/17/changes/bg-audio
- https://developer.android.com/develop/background-work/services/alarms#exact
- https://developer.android.com/reference/android/media/AudioAttributes#USAGE_ALARM

セクション:
- Background audio hardening

ページ種別:
- Apps targeting Android 17 or higher

### 分類スナップショット

主分類（Primary classification）:
- TARGET_SDK_37_CONDITIONAL

公式文書からの初期適用条件判断:
- 公式文書は、Android 17 以降、audio playback、audio focus requests、volume change APIs などの background audio interactions に制限を適用すると説明している。
- 一部の audio restrictions は all apps に適用される一方、targetSdkVersion 37 以上のアプリではより厳格になる。
- targetSdkVersion 37 以上のアプリが background で audio と interaction する場合、foreground service が running である必要があり、さらに foreground service が while-in-use (WIU) capabilities を持つか、exact alarm permission を持ち `USAGE_ALARM` audio streams と interaction している必要がある。

早見表:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 共通制限は Yes / 追加制限は No | all-apps 共通制限は別ファイル。ここで扱う strict 条件は targetSdkVersion 37 以上で強まる。 |
| targetSdkVersion 37 以上が必要か | Yes | `HardeningEnforcer` が `targetSdk < Build.VERSION_CODES.CINNAMON_BUN` を緩和条件として扱い、CINNAMON_BUN 以上では strict level へ進む。 |
| 追加の実行時条件があるか | ある | background audio interaction、AppOps denial、FGS / foreground audio control capability、alarm exception、usage が関係する。 |
| Compat Change ID が関係するか | 確認できず | `frameworks-base` では compat ChangeId ではなく feature flags / AppOps / AudioPolicy hardening override が主要 gate。 |

### 調査日

2026-06-18

### 信頼度

- Medium

### 適用条件分類

適用される条件:
- [ ] Android 17 上の全アプリ（targetSdkVersion に依存しない）
- [ ] Android 17 以上で targetSdkVersion >= 37
- [x] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [ ] 未確認 / 追加根拠が必要

必要な実行時条件:
- Android version: Android 17 (`android-17.0.0_r1`)。
- targetSdkVersion: 37 以上。AOSP 上は `Build.VERSION_CODES.CINNAMON_BUN` 以上。
- Device/form factor: Android audio framework / audioserver が動作する端末。
- Permission/API/component condition: audio playback、audio focus request、volume change APIs、foreground service、WIU / foreground audio control capability、exact alarm permission、`AudioAttributes.USAGE_ALARM`。
- App state/process condition: アプリが background にいて、audio AppOps / process capability により operation が許可されない状態。

Compat framework:
- Change ID: 確認できず
- 変更名: 確認できず
- 既定状態: audio flags / AppOps / AudioPolicy hardening override に依存
- テスト時の切り替え可否: privileged `AudioManager.setHardeningOverride()` / shell `set-hardening` path が存在

分類信頼度:
- Medium

分類根拠:
- `services/core/java/com/android/server/audio/HardeningEnforcer.java`
- `services/core/java/com/android/server/audio/AudioService.java`
- `services/core/java/com/android/server/am/psc/OomAdjusterImpl.java`
- `services/core/java/com/android/server/am/psc/CapabilityController.java`
- `core/java/android/app/ActivityManager.java`

---

# エグゼクティブサマリー

Android 17 では、background からの audio playback、audio focus request、volume change APIs などに制限が入り、targetSdkVersion 37 以上ではより厳格になる。AOSP では、`HardeningEnforcer` が `targetSdk < Build.VERSION_CODES.CINNAMON_BUN` を緩和条件として扱い、CINNAMON_BUN 以上では strict level の制限へ進むことを確認した。

具体的には、audio focus は `OP_TAKE_AUDIO_FOCUS` と `OP_CONTROL_AUDIO`、volume は `OP_CONTROL_AUDIO_PARTIAL` と `OP_CONTROL_AUDIO` の AppOps 結果を見て partial / full の block state を作る。targetSdkVersion が 37 未満の場合は partial level まで緩和されるが、37 以上では strict flag や exception によっては full level の block になる。

信頼度は Medium とする。Java framework 側では targetSdkVersion ゲート、alarm exception、focus / volume の failure mode を確認できたが、playback mute の最終判定は native AudioPolicy / audioserver 側にもまたがる。

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
- Background audio hardening

検証対象の原文:
- Android 17 では audio framework が background audio interactions を制限する。
- 一部の audio restrictions は all apps に適用される。
- Android 17 / API level 37 を対象とするアプリでは制限がより厳しくなる。
- targetSdkVersion 37 以上のアプリが background audio interaction を行うには running foreground service が必要であり、さらに WIU capabilities、または exact alarm permission と `USAGE_ALARM` audio streams の操作が必要になる。

## 解釈

targetSdkVersion 37 追加条件は、全アプリ共通制限の上に重なる strict level の制限である。顧客向けには、Android 17 OS アップデートで発生しうる共通制限と、targetSdkVersion 37 へ更新した時に発生しうる追加制限を分けて説明する必要がある。

---

# 変更内容

AOSP で確認した変更点:
- `HardeningEnforcer.blockFocusMethod()` は `targetSdk < Build.VERSION_CODES.CINNAMON_BUN` を確認し、pre-CINNAMON_BUN では `DENIED_IF_PARTIAL` と `TARGET_SDK` exemption に緩和する。
- CINNAMON_BUN 以上では、`hardeningStrict()` が無効でない限り `DENIED_IF_FULL` に進み、`OP_TAKE_AUDIO_FOCUS` または `OP_CONTROL_AUDIO` の denial に応じて focus request が block される。
- `HardeningEnforcer.blockVolumeMethod()` も `targetSdk < Build.VERSION_CODES.CINNAMON_BUN` を確認し、pre-CINNAMON_BUN では partial level に緩和する。CINNAMON_BUN 以上では `DENIED_IF_FULL` に進む。
- focus の `USAGE_ALARM` では exact alarm permission または cached exact alarm eligibility がある場合に partial level に緩和される。
- volume でも exact alarm permission / eligibility が partial level 緩和に使われる。
- ActivityManager 側では `PROCESS_CAPABILITY_FOREGROUND_AUDIO_CONTROL` が FGS / process state と結びつき、BFGS より低い procstate では capability が剥がされる。

## 適用条件

### OS アップデート時の挙動

- Android 17 にアップデートしただけで適用されるか: 共通制限は Yes / この target 37 追加制限は No。
- targetSdkVersion に依存しない根拠: all-apps 共通制限は別ファイル参照。
- Android 16 以前での挙動: Android 16 にも hardening の土台はあるが、Android 17 では CINNAMON_BUN target 分岐、alarm exception、foreground audio control capability 連携、reason / usage logging が強化される。

### targetSdkVersion 37 以上での挙動

- targetSdkVersion 37 以上で適用されるか: Yes / Conditional。
- Android 17 / targetSdkVersion 36 と Android 17 / targetSdkVersion 37 の差分: targetSdkVersion 36 は partial level まで緩和される。targetSdkVersion 37 以上は strict level の制限に進みうる。
- opt-out / temporary override: privileged hardening override、feature flag、privileged audio permissions、exact alarm + `USAGE_ALARM` exception がある。一般アプリ向けの compat ChangeId opt-out は確認できない。

### その他の条件

- AppOps: `OP_TAKE_AUDIO_FOCUS`、`OP_CONTROL_AUDIO`、`OP_CONTROL_AUDIO_PARTIAL`、playback 側では `OP_PLAY_AUDIO` が関係する。
- Permission: exact alarm permission、`MODIFY_AUDIO_SETTINGS_PRIVILEGED`、`MODIFY_AUDIO_ROUTING`、`MODIFY_PHONE_STATE`、`BLUETOOTH_CONNECT`。
- Audio usage: focus では `AudioAttributes.USAGE_ALARM` が exact alarm exception の条件になる。
- Process state / FGS: foreground audio control capability は FGS / process state に依存し、background state では剥がされる。

---

# AOSP 調査

## checkout 状態

根拠を採用する前に確認したコマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list android-17.0.0_r1
```

結果:
- `frameworks-base` working tree: 調査時点で clean。
- From tag: `android-16.0.0_r4` exists.
- To tag: `android-17.0.0_r1` exists.

## 関連ファイル

- `services/core/java/com/android/server/audio/HardeningEnforcer.java`
- `services/core/java/com/android/server/audio/AudioService.java`
- `services/core/java/com/android/server/audio/AudioManagerShellCommand.java`
- `services/core/java/com/android/server/am/psc/OomAdjusterImpl.java`
- `services/core/java/com/android/server/am/psc/CapabilityController.java`
- `core/java/android/app/ActivityManager.java`
- `core/java/android/app/AppOpsManager.java`
- `media/java/android/media/AudioManager.java`
- `media/java/android/media/IAudioService.aidl`

## 確認したソース文脈

| ファイル / シンボル | Android 16 基準挙動 | Android 17 挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `HardeningEnforcer.blockFocusMethod()` | pre-VIC などの targetSdk 緩和と global hardening enable に近い制御 | `isPreCinnamonBun`、`hardeningPartial()`、`hardeningStrict()`、alarm exception、BT permission、privileged caller を見て partial / full enforcement を決める | targetSdkVersion 37 追加制限の中心 gate |
| `HardeningEnforcer.blockVolumeMethod()` | partial / full AppOps と global enable に近い制御 | `isPreCinnamonBun` と `hardeningPartialVolume()`、exact alarm eligibility を見て block level を決める | target 37 で volume API がより厳しくなる根拠 |
| `AudioService.requestAudioFocus()` | hardening block 時に focus request failed | Android 17 でも block 時に `AUDIOFOCUS_REQUEST_FAILED` を返す | developer-visible failure mode |
| `AudioManager.setHardeningOverride()` / `IAudioService.setHardeningOverride()` | `setEnableHardening(boolean)` 相当 | default / enable / disable / throw の override mode | テスト・debug 用 override の根拠 |
| `OomAdjusterImpl` / `CapabilityController` | 従来 OOM adjuster path | foreground audio control capability を FGS / procstate と結びつける | WIU / foreground service 条件の framework 側接続点 |

必須記入項目:
- Entry point / caller: `AudioManager.requestAudioFocus()` -> `AudioService.requestAudioFocus()` -> `HardeningEnforcer.blockFocusMethod()`、`AudioManager.setStreamVolume()` / `adjustStreamVolume()` -> `AudioService` -> `HardeningEnforcer.blockVolumeMethod()`。
- Relevant class or service responsibility: `HardeningEnforcer` は targetSdk / AppOps / exception 判定、`AudioService` は API failure mode、ActivityManager PSC は foreground audio control capability を担当する。
- Runtime path from app API / system event to changed code: targetSdkVersion 37 app が background で audio API を呼ぶ -> AppOps / process capability が denial を返す -> `HardeningEnforcer` が CINNAMON_BUN 以上として strict level を適用 -> focus は failed、volume は no-op、playback は native 側で mute。
- 除外した無関係なコードパス: audio route、Bluetooth device switching、volume group persistence、TV extension などは targetSdkVersion 37 gate の説明に直接関係しないため除外した。

## 差分解釈

| 確認した差分 | 解釈 | 挙動変更との関係 | 信頼度 |
| --- | --- | --- | --- |
| `targetSdk < Build.VERSION_CODES.CINNAMON_BUN` の緩和分岐 | changed condition / targetSdk gate | targetSdkVersion 37 以上で strict level に進む根拠 | High |
| `hardeningStrict()` / `hardeningPartial()` / `hardeningPartialVolume()` による段階制御 | changed default / feature gated enforcement | rollout / flag state によって enforcement level が変わる | Medium |
| exact alarm + `USAGE_ALARM` exception | added exception | alarm use case の緩和根拠 | High for Java focus path |
| `PROCESS_CAPABILITY_FOREGROUND_AUDIO_CONTROL` | added / changed condition | foreground service / WIU 相当条件との接続 | Medium |
| `AudioManager.setHardeningOverride()` | debug / privileged override | testability / temporary override の根拠 | High |

---

# 事実 / 観察 / 仮説 / 結論

## 事実

- `HardeningEnforcer.blockFocusMethod()` は `isPreCinnamonBun = targetSdk < Build.VERSION_CODES.CINNAMON_BUN` を計算する。
- pre-CINNAMON_BUN では focus / volume とも partial level の enforcement に緩和される。
- CINNAMON_BUN 以上では strict flag が無効でない限り full level の enforcement に進む。
- focus では `USAGE_ALARM` かつ exact alarm eligibility がある場合、partial level に緩和される。
- privileged permission や system UID は hardening を bypass できる。

## 観察

- AOSP では Compat ChangeId ではなく、feature flags / AppOps / AudioPolicy hardening override による gate が中心である。
- targetSdkVersion 37 追加条件は all-apps 共通制限の置き換えではなく、同じ hardening framework 内の strict level として実装されている。
- playback mute の最終判断は framework Java だけでは完結しない。

## 仮説

- 公式文書の WIU capability は、framework 実装上 `PROCESS_CAPABILITY_FOREGROUND_AUDIO_CONTROL` と AppOps foreground capability の組み合わせとして表現されている可能性が高い。

## 結論

- この target item は `TARGET_SDK_37_CONDITIONAL` と分類する。
- Android 17 / targetSdkVersion 37 以上で background audio interaction を行い、foreground audio control capability または alarm exception を満たせない場合に影響する。

---

# 顧客影響

影響しやすいアプリ:
- background で audio playback、audio focus request、volume change APIs を使うアプリ。

影響しやすい条件:
- targetSdkVersion 37 以上。
- background state で audio interaction を行う。
- FGS / foreground audio control capability を持たない。
- alarm use case なのに exact alarm permission または `USAGE_ALARM` を満たさない。

想定される症状:
- audio focus request が失敗する。
- volume / ringer mode API が効かない。
- playback が mute される。

---

# サービス影響例

このセクションは、公式文書と AOSP 根拠から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: Spotify / Pocket Casts / Audible の targetSdkVersion 37 更新

- 具体サービス例: Spotify、Pocket Casts、Audible、YouTube Music。
- 影響を受ける実装パターン: targetSdkVersion 37 へ更新後、background state で audio focus / playback / volume API を使うが、foreground audio control capability を満たさない実装。
- 発生条件: Android 17 / targetSdkVersion 37 以上、background audio interaction、`mediaPlayback` FGS や MediaSessionService などの条件が不足する場合。
- ユーザーに見える症状: targetSdkVersion 更新後だけ、バックグラウンド再生開始や再開が失敗する、無音になる、focus を取れない可能性。
- 技術的に起きていること: pre-CINNAMON_BUN 向けの partial 緩和から外れ、strict level の hardening 判定に進む。
- 推奨対応シーン: targetSdkVersion 37 への移行前の media playback regression test。
- 検証観点: targetSdkVersion 36 / 37 比較、FGS 開始タイミング、audio focus return value、hardening override を使った再現。
- 根拠: `HardeningEnforcer.blockFocusMethod()` / `blockVolumeMethod()` の `targetSdk < CINNAMON_BUN` 分岐、公式 target-side statement。
- Confidence（信頼度）: High for Java focus / volume path、Medium for playback mute。
- 注意: 上記サービスで発生確認した事実ではない。適切な media FGS / MediaSession を使う実装では影響しない可能性が高い。

## 例2（Example 2）: Google Clock / Todoist / 医療リマインダーの alarm 音

- 具体サービス例: Google Clock、Todoist、Medisafe のような medication reminder、カレンダー / reminder アプリ。
- 影響を受ける実装パターン: alarm / reminder 用の音を background から鳴らすが、exact alarm permission または `AudioAttributes.USAGE_ALARM` を満たさない実装。
- 発生条件: Android 17 / targetSdkVersion 37 以上で background audio interaction が strict 判定になり、alarm exception に入らない場合。
- ユーザーに見える症状: reminder 音が鳴らない、volume 変更が効かない、通知だけ表示され音が出ない可能性。
- 技術的に起きていること: focus path では exact alarm eligibility と `USAGE_ALARM` が partial 緩和条件になり、不足すると full block に進みうる。
- 推奨対応シーン: alarm、timer、medication reminder、calendar reminder の target 37 対応。
- 検証観点: exact alarm permission、`USAGE_ALARM`、notification channel sound、FGS / visible state、targetSdkVersion 36 / 37 比較。
- 根拠: `HardeningEnforcer.blockFocusMethod()` の alarm exception、official bg-audio guidance。
- Confidence（信頼度）: High for focus exception evidence。
- 注意: 上記サービスで発生確認した事実ではない。Google Clock など platform / privileged 実装は一般アプリと条件が異なる可能性がある。

---

# 推奨アクション候補

- targetSdkVersion 37 へ上げる前に、background audio interaction をすべて棚卸しする。
- background 再生は user-initiated flow から `mediaPlayback` FGS / Media3 `MediaSessionService` を開始する。
- FGS 開始時点が user visible / user initiated か確認する。
- alarm use case は exact alarm permission と `AudioAttributes.USAGE_ALARM` を合わせて確認する。
- audio focus request の戻り値を必ず処理する。

---

# One Page Summary

- [summary](../../../summaries/target/media/background-audio-hardening-summary.md)

# Human Decision

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断

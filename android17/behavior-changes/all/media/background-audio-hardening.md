# Background audio hardening

> 役割メモ:
> このファイルは Background audio hardening のうち、Android 17 上の全アプリに関係する共通制限を中心に扱う。
> targetSdkVersion 37 以上で強まる追加条件は [target/media/background-audio-hardening.md](../../target/media/background-audio-hardening.md) も参照する。

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

### Behavior Change 文書（Behavior Change Source）

文書:
- https://developer.android.com/about/versions/17/behavior-changes-all

関連文書:
- https://developer.android.com/about/versions/17/changes/bg-audio
- https://developer.android.com/reference/android/media/AudioManager
- https://developer.android.com/media/optimize/audio-focus
- https://developer.android.com/develop/background-work/services/fgs
- https://developer.android.com/reference/android/media/AudioAttributes#USAGE_ALARM

セクション:
- Background audio hardening

ページ種別:
- Behavior changes: all apps

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- OS_UPDATE_ALL_APPS

公式文書からの初期適用条件判断:
- 公式文書は Android 17 の `Behavior changes: all apps` ページにこの項目を掲載している。
- 詳細ページは、Android 17 上で対象の background audio interaction を行うすべての app は、visible activity を持つか、`SHORT_SERVICE` ではない foreground service を実行している必要があり、これは target API level 37 かどうかに関係なく適用されると説明している。
- targetSdkVersion 37 以上で強まる追加条件は別項目として [target/media/background-audio-hardening.md](../../target/media/background-audio-hardening.md) に整理する。

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | Yes / Conditional | all apps 文書に掲載。AOSP では AppOps と process capability に基づく audio hardening path が Android 17 tag に存在する。 |
| targetSdkVersion 37 以上が必要か | 共通制限には不要 | Android 17 の `HardeningEnforcer` は pre-CINNAMON_BUN に partial level の緩和を残す一方、background audio interaction の AppOps 判定自体は targetSdkVersion だけで無効化されない。 |
| 追加の実行時条件があるか | ある | background audio interaction、AppOps の audio restriction、visible / FGS / process capability、privileged caller、alarm exception、feature flag / override に依存する。 |
| Compat Change ID が関係するか | 未確認 | `frameworks-base` では compat ChangeId ではなく audio flags、AppOps、process capability、AudioPolicy hardening override が主要 gate として確認された。 |

### 調査日（Investigation Date）

2026-06-18

### 信頼度（Confidence）

- Medium

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [x] targetSdkVersion に関係なく Android 17 の全アプリへ適用
- [ ] Android 17 以上かつ targetSdkVersion 37 以上で適用
- [ ] targetSdkVersion 37 以上かつ追加の実行時条件を満たす場合に適用
- [ ] Mainline / Google Play system update に依存
- [ ] API 追加のみであり、挙動変更ではない
- [ ] 未確認 / 追加 evidence が必要

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 (`android-17.0.0_r1`)。
- targetSdkVersion: 共通制限は targetSdkVersion 37 を必須条件にしない。ただし targetSdkVersion 37 以上では strict level へ進む追加条件がある。
- Device/form factor: Android audio framework / audioserver が動作する端末。Automotive では volume API hardening が別途 `autoPublicVolumeApiHardening()` と privileged permission に依存する。
- Permission/API/component condition: audio playback、`AudioManager.requestAudioFocus()`、`AudioManager.setStreamVolume()`、`adjustStreamVolume()`、`adjustVolume()`、`adjustSuggestedStreamVolume()`、`setRingerMode()`、AppOps `OP_PLAY_AUDIO` / `OP_TAKE_AUDIO_FOCUS` / `OP_CONTROL_AUDIO` / `OP_CONTROL_AUDIO_PARTIAL`。
- App state/process condition: app が background audio interaction を行い、AppOps / process state / FGS capability により audio operation が許可されない場合。

Compat framework:
- Change ID: 確認できず
- 変更名: 確認できず
- 既定状態: audio flags / AppOps / native AudioPolicy 側の default に依存
- テスト時に切り替え可能か: `AudioManager.setHardeningOverride()` / `adb shell cmd audio set-enable-hardening` の privileged override path は存在する

分類信頼度（Classification confidence）:
- Medium

分類根拠（Classification evidence）:
- `services/core/java/com/android/server/audio/HardeningEnforcer.java`
- `services/core/java/com/android/server/audio/AudioService.java`
- `services/core/java/com/android/server/am/psc/OomAdjusterImpl.java`
- `services/core/java/com/android/server/am/psc/CapabilityController.java`
- `core/java/android/app/ActivityManager.java`
- `core/java/android/app/AppOpsManager.java`

---

# エグゼクティブサマリー

Android 17 では、background からの audio playback、audio focus request、volume / ringer mode API に対して audio hardening が強化される。AOSP では、`HardeningEnforcer` が AppOps の audio restriction を見て、volume API を no-op 化し、audio focus request を `AUDIOFOCUS_REQUEST_FAILED` にする経路が確認できた。playback については audioserver から `AudioService` へ `playbackHardeningEvent()` が通知され、`AudioHardening background playback ... muted` として記録される。

全アプリ共通の観点では、targetSdkVersion 37 は必須条件ではない。Android 17 の実装は、pre-CINNAMON_BUN app には partial level の緩和を残しつつ、background audio interaction が AppOps / process capability で制限される構造になっている。targetSdkVersion 37 以上で strict level へ進む追加条件は target 側レポートで扱う。

信頼度は Medium とする。Java framework 側では focus / volume / logging / process capability の証跡を確認できたが、actual playback mute の最終判定は native AudioPolicy / audioserver 側にもまたがるため、この checkout だけでは全条件を完全には閉じられない。

---

# 公式ドキュメント確認

## 原文（Statement）

ページタイトル:
- Behavior changes: all apps

ページ URL:
- https://developer.android.com/about/versions/17/behavior-changes-all

ページ種別:
- all apps

セクションタイトル:
- Background audio hardening

検証対象の原文:
- Android 17 から、audio framework は audio playback、audio focus request、volume change API を含む background audio interaction を制限する。
- app が valid lifecycle ではない状態で対象 audio API を呼ぶと、audio playback と volume change API は例外や failure message なしで silently fail する。
- audio focus API は `AUDIOFOCUS_REQUEST_FAILED` を返す。
- targetSdkVersion 37 以上の app では制限がより厳しく、background で動作する場合は foreground service が WIU capability を持つ必要がある。ただし exact alarm permission があり、`USAGE_ALARM` audio stream を扱う場合は例外である。

## 解釈（Interpretation）

この変更は単一の targetSdkVersion ゲートではなく、二層の適用条件を持つ。第一層は Android 17 上の all apps に対する background audio hardening で、AppOps / process state / foreground service capability により audio interaction が許可されない場合に制限される。第二層は targetSdkVersion 37 以上の app に対する追加制限で、CINNAMON_BUN 以降の targetSdkVersion が strict level の判定に使われる。

同じ `Background audio hardening` が、公式の `Behavior changes: all apps` と `Behavior changes: Apps targeting Android 17 or higher` の両方に掲載されている。これは独立した二つの変更ではなく、全アプリ共通の制限を土台として、targetSdkVersion 37 以上のアプリに追加条件が重なる構造である。

一般的なアプリに対する概念上の判定は、次のように整理できる。実際の実装には AppOps、privileged caller、feature flag などの追加条件があるため、以下は AOSP の適用条件を完全に表したものではない。

```text
background audio interaction を許可
  = visible activity
    または
    (
      SHORT_SERVICE 以外の foreground service が running
      かつ
      (
        targetSdkVersion < 37
        または foreground service が WIU capability を持つ
        または exact alarm permission + USAGE_ALARM exception
      )
    )
```

このため、Android 17 / targetSdkVersion 36 でも、foreground service を使わずにバックグラウンドから音声を扱う場合は共通制限の対象になる。一方、targetSdkVersion 37 以上では、foreground service が実行中でも、バックグラウンドから開始され、WIU capability を持たない場合は追加制限の対象になりうる。

---

# 変更内容（What Changed）

AOSP で確認した変更点:
- `HardeningEnforcer` が Android 17 で `mShouldEnableAllHardening` から `mHardeningOverride` に変わり、default / enable / disable / throw の hardening override を扱う。
- Volume API では `OP_CONTROL_AUDIO_PARTIAL` と `OP_CONTROL_AUDIO` を確認し、許可されない場合は `setStreamVolume()` / `adjustStreamVolume()` などを return で no-op 化する。
- Audio focus では `OP_TAKE_AUDIO_FOCUS` と `OP_CONTROL_AUDIO` を確認し、hardening により block される場合は `AudioService.requestAudioFocus()` が `AUDIOFOCUS_REQUEST_FAILED` を返す。
- Playback では audioserver から `AudioService.playbackHardeningEvent()` へ hardening event が通知され、partial / full、reason、usage が `AudioHardening background playback ... muted` としてログ・metrics に記録される。
- ActivityManager の process capability に `PROCESS_CAPABILITY_FOREGROUND_AUDIO_CONTROL` が使われ、`OomAdjusterImpl` は process state が `PROCESS_STATE_BOUND_FOREGROUND_SERVICE` より低い場合に `hardeningBfgs()` 条件で foreground audio control capability を落とす。

## 適用条件

### OS アップデート時の挙動（OS Update Behavior）

- Android 17 に OS アップデートしただけで適用されるか: Yes / Conditional。
- targetSdkVersion に依存しない根拠: `HardeningEnforcer` は AppOps の partial / full restriction を先に判定し、pre-CINNAMON_BUN でも partial level までの enforcement は残す。公式詳細ページも共通制限は target API level 37 に依存しないと説明している。
- Android 16 以前での挙動: Android 16 tag にも `HardeningEnforcer` は存在するが、Android 17 では alarm exception、usage/reason logging、hardening override、CINNAMON_BUN 分岐、foreground audio control capability との結合が強化されている。

### targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- targetSdkVersion 37 以上で適用されるか: 共通制限は targetSdkVersion 37 を必須にしない。
- Android 17 / targetSdkVersion 36 と Android 17 / targetSdkVersion 37 の差分: targetSdkVersion 36 では partial level の緩和が残る。targetSdkVersion 37 以上では strict level の制限へ進みうる。詳細は target 側レポートを参照。
- opt-out / exception: privileged audio permission、hardening override、feature flag、exact alarm / `USAGE_ALARM` exception がある。

### その他の条件（Other Conditions）

- privileged caller: `MODIFY_AUDIO_SETTINGS_PRIVILEGED`、`MODIFY_AUDIO_ROUTING`、`MODIFY_PHONE_STATE`、または app UID 未満の system UID は許可される。
- alarm exception: exact alarm permission または cached exact alarm eligibility があり、focus では `USAGE_ALARM` の場合に partial level まで緩和される。volume では exact alarm eligibility が partial level 緩和に使われる。
- foreground state: `PROCESS_CAPABILITY_FOREGROUND_AUDIO_CONTROL` は FGS / process state と結びつき、BFGS より下の procstate では `hardeningBfgs()` により落とされる。

---

# AOSP 調査（AOSP Investigation）

## チェックアウト状態

確認コマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list android-17.0.0_r1
```

結果:
- `frameworks-base` の `status --short` は空で、未コミット変更 は確認されなかった。
- `android-16.0.0_r4` tag は存在する。
- `android-17.0.0_r1` tag は存在する。

## 関連ファイル（Related Files）

- `services/core/java/com/android/server/audio/HardeningEnforcer.java`
- `services/core/java/com/android/server/audio/AudioService.java`
- `services/core/java/com/android/server/audio/PlaybackActivityMonitor.java`
- `services/core/java/com/android/server/am/psc/OomAdjusterImpl.java`
- `services/core/java/com/android/server/am/psc/CapabilityController.java`
- `core/java/android/app/ActivityManager.java`
- `core/java/android/app/AppOpsManager.java`
- `media/java/android/media/AudioManager.java`
- `media/java/android/media/AudioPlaybackConfiguration.java`

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル | Android 16 の基準挙動 | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `HardeningEnforcer.blockVolumeMethod()` | AppOps による partial / full 判定と global enable 相当の制御 | `mHardeningOverride`、CINNAMON_BUN target check、exact alarm cache、reason / metrics logging を使って block level を決める | volume API が silent no-op になる直接の Java framework gate |
| `AudioService.setStreamVolumeWithAttribution()` / `adjustStreamVolumeWithAttribution()` | volume path から hardening check | hardening block 時は `return` し、volume 変更を行わない | 公式文書の volume change API silently fail に対応 |
| `HardeningEnforcer.blockFocusMethod()` | pre-VIC などの緩和を持つ focus hardening | `OP_TAKE_AUDIO_FOCUS` / `OP_CONTROL_AUDIO`、usage、alarm exception、CINNAMON_BUN target check、strict flag で block を決める | audio focus request の failure mode を決める gate |
| `AudioService.requestAudioFocus()` | focus hardening block 時に failure | Android 17 でも block 時に `AUDIOFOCUS_REQUEST_FAILED` を返す | developer-visible result code の根拠 |
| `AudioService.playbackHardeningEvent()` | playback hardening event を受ける | Android 17 では reason と usage を受け取り、AudioAtomsLog にも記録する | playback mute は native 側判定を含むが、framework 側で公式挙動のイベントが確認できる |
| `OomAdjusterImpl` / `CapabilityController` | 従来の OOM adjuster path | `PROCESS_CAPABILITY_FOREGROUND_AUDIO_CONTROL` を FGS / process state と結びつけ、BFGS より下では capability を落とす | background / foreground service state と audio control permission の接続点 |
| `AppOpsManager` | audio appops は存在 | `OP_PLAY_AUDIO` / `OP_TAKE_AUDIO_FOCUS` / `OP_CONTROL_AUDIO` / `OP_CONTROL_AUDIO_PARTIAL` が audio restriction の key として使われる | audio operation ごとの許可判定の基礎 |

必須記入項目:
- Entry point / caller: `AudioManager.setStreamVolume()` / `adjustStreamVolume()` -> `AudioService` -> `HardeningEnforcer.blockVolumeMethod()`、`AudioManager.requestAudioFocus()` -> `AudioService.requestAudioFocus()` -> `HardeningEnforcer.blockFocusMethod()`、playback native path -> `IAudioManagerNative.playbackHardeningEvent()` -> `AudioService`。
- Relevant class or service responsibility: `AudioService` は public audio API の service-side enforcement、`HardeningEnforcer` は AppOps / targetSdk / exception 判定、ActivityManager PSC は foreground audio control capability の付与・剥奪を担当する。
- Runtime path from app API / system event to changed code: app が background で audio API を呼ぶ -> AppOps / process capability により operation が disallowed になる -> volume は no-op、focus は failure、playback は native AudioPolicy 側で mute され framework event が記録される。
- Why unrelated code paths were excluded: audio route / Bluetooth / mixer / TV extension / media metadata の差分は background audio hardening の適用条件や developer-visible failure mode を直接説明しないため除外した。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
| `HardeningEnforcer` が `mShouldEnableAllHardening` から `mHardeningOverride` と feature flags / targetSdk / exceptions に再構成 | changed condition / changed default control | enforcement の段階的適用、override、target 37 追加条件の根拠 | Medium |
| Volume API path が hardening block 時に return | added / changed enforcement | volume change API の silent failure に対応 | High |
| Focus path が hardening block 時に `AUDIOFOCUS_REQUEST_FAILED` | changed condition | audio focus request failure の根拠 | High |
| Playback hardening event が reason / usage 付きで framework に通知 | changed condition / observability improvement | playback mute の framework-visible 証跡 | Medium |
| foreground audio control capability が process state / FGS と結合 | changed condition | visible / FGS lifecycle 条件の実装側根拠 | Medium |

---

# 事実 / 観察 / 仮説 / 結論

## 事実（Facts）

- `android-17.0.0_r1` の `HardeningEnforcer.blockVolumeMethod()` は `OP_CONTROL_AUDIO_PARTIAL` と `OP_CONTROL_AUDIO` を確認する。
- `AudioService.setStreamVolumeWithAttribution()` と `adjustStreamVolumeWithAttribution()` は `blockVolumeMethod()` が true の場合に `return` する。
- `AudioService.requestAudioFocus()` は `blockFocusMethod()` が true の場合に `AudioManager.AUDIOFOCUS_REQUEST_FAILED` を返す。
- `AudioService.playbackHardeningEvent()` は audioserver UID からの event のみを受け、partial / full、reason、usage をログ・metrics に記録する。
- `OomAdjusterImpl` は `procState > PROCESS_STATE_BOUND_FOREGROUND_SERVICE` で `PROCESS_CAPABILITY_FOREGROUND_AUDIO_CONTROL` を落とす path を持つ。

## 観察（Observations）

- Android 16 にも hardening の土台はあるが、Android 17 では targetSdkVersion 37、exact alarm exception、usage/reason logging、foreground audio control capability との結合が強化されている。
- Compat framework ChangeId はこの checkout では主要 gate として確認できない。
- Playback の実際の mute 判定は native AudioPolicy / audioserver 側にもあるため、`frameworks-base` だけでは mute 条件を完全には説明できない。

## 仮説（Hypotheses）

- all apps 共通制限は AppOps / process capability / audio policy の デフォルト ポリシー により有効化され、targetSdkVersion 37 は strict level の追加条件に使われる。
- Media3 `MediaSessionService` や適切な `mediaPlayback` FGS は foreground audio control capability を得ることで、通常の継続再生を維持できる可能性が高い。

## 結論（Conclusions）

- この all-apps 項目は `OS_UPDATE_ALL_APPS` と分類する。
- ただし実際の影響は「Android 17 上で background audio interaction を行い、AppOps / lifecycle / FGS capability 条件を満たせない場合」に限定される。
- targetSdkVersion 37 以上での追加 strict 条件は target 側レポートで扱う。

---

# 顧客影響

影響しやすいアプリ:
- 音楽、podcast、radio、audiobook、video streaming、alarm、timer、reminder、background sound、通話・ナビゲーションなど、background で audio interaction を行うアプリ。

影響しやすい実装:
- background worker / receiver / boot flow から audio focus を取得する。
- visible activity や適切な FGS なしに playback を開始または継続する。
- background から volume / ringer mode を変更する。

想定される症状:
- audio focus request が `AUDIOFOCUS_REQUEST_FAILED` を返す。
- volume / ringer mode API が例外なしで効かない。
- playback が mute / silent suppression され、`AudioHardening` log に記録される。

---

# サービス影響例

このセクションは、公式文書と AOSP 根拠から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: Spotify / YouTube Music / Audible の background playback

- 具体サービス例: Spotify、YouTube Music、Audible、radiko。
- 影響を受ける実装パターン: visible activity や適切な foreground service なしに、background worker / receiver から audio focus を取得し再生を開始・継続する実装。
- 発生条件: Android 17 上で background audio interaction が AppOps / process capability により許可されない場合。
- ユーザーに見える症状: 再生が始まらない、途中で無音になる、再生ボタンを押しても音が出ない可能性。
- 技術的に起きていること: audio focus は `AUDIOFOCUS_REQUEST_FAILED`、playback は hardening event により mute、volume API は silent no-op になる。
- 推奨対応シーン: media playback service、notification playback control、boot / receiver 起点の再生。
- 検証観点: visible activity 有無、`mediaPlayback` FGS、Media3 `MediaSessionService`、focus request return value、`AudioHardening` log。
- 根拠: 公式文書、`HardeningEnforcer`、`AudioService.requestAudioFocus()`、`playbackHardeningEvent()`、foreground audio control capability evidence。
- Confidence（信頼度）: Medium。playback mute の最終判定は native AudioPolicy 側にもまたがる。
- 注意: 上記サービスで発生確認した事実ではない。実際の影響は再生開始経路と FGS / MediaSession 実装に依存する。

## 例2（Example 2）: Google Maps / Waze / Uber Driver のナビ・通知音

- 具体サービス例: Google Maps、Waze、Uber Driver、DoorDash Dasher。
- 影響を受ける実装パターン: background または画面非表示状態で音声案内、通知音、volume control、audio focus を扱う実装。
- 発生条件: Android 17 で app が valid lifecycle / FGS / foreground audio control capability を満たさず audio API を呼ぶ場合。
- ユーザーに見える症状: 音声案内や通知音が鳴らない、volume 調整が効かない、focus 取得に失敗する可能性。
- 技術的に起きていること: AppOps と process state により background audio interaction が制限され、例外なしの silent failure として見えることがある。
- 推奨対応シーン: navigation、driver / delivery、timer / reminder、background notification sound。
- 検証観点: foreground service type、process state、screen off / app background、exact alarm 例外との違い。
- 根拠: 公式文書と report の OS_UPDATE_ALL_APPS classification / AppOps / PSC evidence。
- Confidence（信頼度）: Medium。
- 注意: 上記サービスで発生確認した事実ではない。ナビ・配達アプリは user-visible flow で FGS を使うことが多く、実装ごとの確認が必要。

---

# 推奨アクション候補（Recommended Action Candidates）

- background audio API 呼び出し箇所を棚卸しし、呼び出し時点の visible / FGS / process state をテストする。
- 継続再生は Media3 `MediaSessionService` または user-initiated な `mediaPlayback` foreground service flow に寄せる。
- audio focus request の戻り値を必ず確認し、`AUDIOFOCUS_REQUEST_FAILED` 時に再試行・UI 誘導・silent fallback を設計する。
- volume / ringer mode 変更は background で成功すると仮定しない。
- alarm use case では exact alarm permission と `AudioAttributes.USAGE_ALARM` の利用条件を target 37 側の追加条件と合わせて確認する。

---

# 検証計画（Testing）

## 実行時条件の比較

| Android / targetSdkVersion | Activity / service の状態 | 期待結果 |
| --- | --- | --- |
| Android 17 / 36 | ユーザーに表示されている Activity がある | 音声操作が許可されることを確認する。 |
| Android 17 / 36 | バックグラウンド、FGS なし | 共通制限として、再生のミュート、audio focus の取得失敗、音量 / 着信モードの変更が反映されないことを確認する。 |
| Android 17 / 36 | バックグラウンド、`SHORT_SERVICE` 以外の FGS が実行中 | 全アプリ共通のライフサイクル条件を満たすことを確認する。 |
| Android 17 / 37 | ユーザーに見える操作、またはユーザー操作を起点に開始した、WIU capability を持つ FGS | 音声操作が許可されることを確認する。 |
| Android 17 / 37 | バックグラウンドから開始された、WIU capability を持たない FGS | strict / full level の制限を確認する。 |
| Android 17 / 37 | FGS + exact alarm permission + `USAGE_ALARM` | アラーム用途の例外を確認する。permission または usage の一方を外した失敗ケースも実施する。 |

API ごとの観測項目:
- 音声再生: 実際に音が出るか確認する。制限された場合は、API から例外が発生せず、音声がミュートされることを確認する。
- audio focus: `requestAudioFocus()` の戻り値が `AUDIOFOCUS_REQUEST_FAILED` になることを確認する。
- 音量 / 着信モード: 呼び出し前後の値を比較し、制限された場合は、例外が発生せず値も変更されないことを確認する。
- 診断情報: `adb shell dumpsys audio` と `logcat` で、パッケージ名を含む `AudioHardening` の記録を確認する。`level: partial` は FGS がない状態、`level: full` は FGS があっても WIU capability が不足している状態を識別する手掛かりになる。

## ADB による hardening の強制設定

公式の強制テスト用コマンド:

```bash
adb shell cmd audio set-enable-hardening enable
adb shell cmd audio set-enable-hardening disable
adb shell cmd audio set-enable-hardening throw
```

- `enable`: すべてのアプリに hardening の制限を強制し、targetSdkVersion にかかわらず WIU の要件を適用する。強制テスト中は、exact alarm + `USAGE_ALARM` の例外も適用されない。
- `disable`: hardening の制限を無効化し、症状が hardening に起因するかを比較する。
- `throw`: `enable` と同じ条件を強制したうえで、音量 / audio focus では `IllegalStateException`、明示的な書き込みによる音声再生ではエラーコードを返すなど、表面化しにくい失敗を検出しやすい形に変える。

`enable` / `throw` は targetSdkVersion 37 の適用条件とアラーム用途の例外を上書きするため、targetSdkVersion 36 / 37 の正式な比較や、アラーム用途の例外の確認には使用しない。これらは、hardening override を強制していない既定状態の Android 17 端末で別途確認する。

---

# One Page Summary

- [summary](../../../summaries/all/media/background-audio-hardening-summary.md)

# Human Decision

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断

---

## 再検証記録（2026-08-22）

### 調査日（Investigation Date）

- 2026-08-22

### 公式ドキュメント再確認（Original Documentation Recheck）

- Android 17 の all-apps / target Behavior Change ページを再取得し、このレポートが参照する公式 section の掲載と適用範囲を再確認した。
- 公式ページの最終更新表示: all-apps / target: 2026-08-14 UTC。
- Android 17 compat framework 一覧は 2026-08-22 時点でも HTTP 404 のため、公式 Behavior Change 文書と AOSP annotation / gate を正とした。
- 既存の引用は短い要約として扱い、適用条件は公式ページ種別と AOSP gate の両方で再評価した。

### AOSP 証拠ワークスペース（AOSP Evidence Workspaces）

| AOSP project | Official remote URL | Checkout path | Working tree | From tag / resolved commit | To tag / resolved commit | Comparison command | Dirty risk / limitations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `platform/frameworks/base` | `https://android.googlesource.com/platform/frameworks/base` | `frameworks-base/` | Clean | `android-16.0.0_r4` / `45034f0663f960d9ee5fb0a101a4732b71f6e2f4` | `android-17.0.0_r1` / `94b4c163b7dfe5ce3607f7bb8456f9573f7de57d` | `git -C frameworks-base diff --no-renames --name-only android-16.0.0_r4 android-17.0.0_r1` | なし。明示タグ比較のため working tree の内容は根拠に含めない。 |

### ソース文脈・差分解釈の再確認（Source Context Reviewed / Diff Interpretation）

- 各 official remote で Android 16 / 17 の最新通常リリースタグが `android-16.0.0_r4` / `android-17.0.0_r1` のままであることを確認した。
- 上表の project-level `--name-only` 比較を再実行し、既存本文の path / symbol 別 source context、gate、追加・削除・条件変更・既定値変更・差分なしの解釈を再確認した。
- タグと解決済み commit が既存調査の比較対象から変わっていないため、本文の evidence record を別タグへ機械的に置換していない。
- 実機 Observed は新規実施していない。既存の「未実施」「未確認」および不足根拠はそのまま維持した。

### 事実（Facts）

- `android-16.0.0_r4` と `android-17.0.0_r1` は 2026-08-22 時点の最新通常リリースタグである。
- 上表に再検証時の working tree 状態を記録し、official remote、両タグ、解決済み commit を確認した。展開中または dirty の working tree は根拠に使用していない。
- 公式 section と AOSP evidence の比較 pair は一致している。

### 観察（Observations）

- 最新タグが変わっていないため、今回の再検証で既存の source diff 解釈を変更する新しい AOSP tag evidence は生じなかった。
- report 内に残る Medium / Low confidence、OEM / Mainline / QPR 条件、未確認の module enforcement は解消したものとして扱わない。

### 仮説（Hypotheses）

- 新しい仮説は追加しない。既存本文で仮説または可能性として記載した事項は、実機・製品 build・未確認 module の evidence が得られるまで事実へ昇格しない。

### 結論（Conclusions）

- 既存本文の主分類、confidence、対応候補を維持する。既存の不足根拠がある場合はその制約も維持する。
- 全件再検証の横断記録は [`android17/analysis/REVALIDATION_2026-08-22.md`](../../../analysis/REVALIDATION_2026-08-22.md) を参照する。

### Human Decision

- この再検証では最終 priority、severity、release readiness、顧客説明優先度を変更していない。
- 人間の判断は [Android 17 Decision Log](../../../decisions/DECISION_LOG.md) を正とする。

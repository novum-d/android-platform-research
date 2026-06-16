# Background audio hardening

> 役割メモ:
> このファイルは Background audio hardening のうち、Android 17 上の全アプリに関係する共通制限を中心に扱う。
> targetSdkVersion 37 以上で強まる追加条件は [target/media/background-audio-hardening.md](../../target/media/background-audio-hardening.md) も参照する。

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

比較元:
- android-16.0.0_r4

比較先:
- TBD: Android 17 AOSP tag

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
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- 公式文書は Android 17 の `Behavior changes: all apps` ページにこの項目を掲載している。
- all apps ページと詳細ページは、Android 17 から audio playback、audio focus request、volume change API を含む background audio interaction に制限がかかると説明している。
- 詳細ページは、Android 17 上で対象の background audio interaction を行うすべての app は、visible activity を持つか、`SHORT_SERVICE` ではない foreground service を実行している必要があり、これは target API level 37 かどうかに関係なく適用されると説明している。
- 詳細ページは、targetSdkVersion 37 以上の app には追加制限があり、background で動作する場合、foreground service が while-in-use (WIU) capability を持つ必要があると説明している。ただし exact alarm permission が付与され、`USAGE_ALARM` audio stream を扱う場合は WIU requirement が免除される。
- ただし、local `frameworks-base` に Android 17 AOSP tag がないため、AudioService / AudioManager / audio focus / volume policy / foreground service WIU gate / compat framework entry は未確認である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 可能性は高いが条件付き、かつ未検証 | 詳細ページは all apps running on Android 17 に適用され、target API level 37 かどうかに関係ないと説明。AOSP gate 未確認。 |
| targetSdkVersion 37 以上が必要か | 一部で必要 | 共通制限は targetSdkVersion に依存しない。WIU capability requirement は targetSdkVersion 37 以上の追加制限。AOSP gate 未確認。 |
| 追加の実行時条件があるか | ある | app が background audio interaction を行い、valid lifecycle / visible activity / foreground service 条件を満たさない場合。target 37+ では WIU capability 条件も加わる。 |
| Compat Change ID が関係するか | 未確認 | Android 17 tag と compat framework evidence が未確認。 |

### 調査日（Investigation Date）

2026-06-15

### 信頼度（Confidence）

- Low

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] targetSdkVersion に関係なく Android 17 の全アプリへ適用
- [ ] Android 17 以上かつ targetSdkVersion 37 以上で適用
- [ ] targetSdkVersion 37 以上かつ追加の実行時条件を満たす場合に適用
- [ ] Mainline / Google Play system update に依存
- [ ] API 追加のみであり、挙動変更ではない
- [x] 未確認 / 追加 evidence が必要

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 以上。AOSP tag 未取得のため実装上の OS gate は未確認。
- targetSdkVersion: 共通制限は公式文書上 targetSdkVersion に依存しない。targetSdkVersion 37 以上では WIU capability requirement が追加される。
- Device/form factor: audio framework が動作する Android 17 device。
- Permission/API/component condition: audio playback、audio focus request、volume change API、`AudioManager.requestAudioFocus()`、`AudioTrack.write()`、AAudio / OpenSL ES、`AudioManager.setStreamVolume()`、`adjustStreamVolume()`、foreground service、`mediaPlayback` FGS、WIU capability、exact alarm permission、`USAGE_ALARM`。
- App state/process condition: app が visible activity を持たない、または適切な foreground service / WIU capability を持たない状態で background audio interaction を行う場合。

Compat framework:
- Change ID: 未確認
- 変更名: 未確認
- 既定状態: 未確認
- テスト時に切り替え可能か: 未確認

分類信頼度（Classification confidence）:
- Low

分類根拠（Classification evidence）:
- 公式ドキュメントページ: `behavior-changes-all`
- 検証対象の適用条件文: Android 17 から background audio interaction に制限がかかる。Android 17 上の all apps に target API level 37 かどうかに関係なく適用される共通条件と、targetSdkVersion 37 以上向けの追加 WIU 条件がある。
- AOSP targetSdk gate: 未確認。local `frameworks-base` に `android-17*` tag がない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# エグゼクティブサマリー（Executive Summary）

Android 17 では、background からの audio playback、audio focus request、volume change API などの background audio interaction に対して、audio framework が制限をかける。目的は、ユーザーが意図していない background audio operation を抑制することである。

公式詳細ページは、Android 17 上で対象の background audio interaction を行う app は、visible activity を持つか、`SHORT_SERVICE` ではない foreground service を実行している必要があると説明している。この条件は target API level 37 かどうかに関係なく適用される。一方、targetSdkVersion 37 以上の app では追加制限として、background で動作する foreground service に while-in-use (WIU) capability が必要になる。ただし exact alarm permission があり、`USAGE_ALARM` stream を扱う場合は免除される。

無効な lifecycle 状態で対象 API を呼ぶと、playback と volume change API は例外や failure message なしで silently fail し、audio focus request は `AUDIOFOCUS_REQUEST_FAILED` を返す。現時点では local `frameworks-base` に Android 17 AOSP tag がないため、実装上の gate、compat Change ID、targetSdkVersion 分岐は未確認である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE`、信頼度は Low とする。

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

関連する詳細ページの記述:
- Android 17 上で対象の background audio interaction を行うすべての app は、visible activity を持つか、`SHORT_SERVICE` ではない foreground service を実行している必要がある。
- この共通条件は target API level 37 かどうかに関係なく適用される。
- targetSdkVersion 37 以上の app には、foreground service の WIU capability requirement が追加される。

## 解釈（Interpretation）

この変更は単一の targetSdkVersion gate ではなく、二層の適用条件を持つ可能性がある。第一層は Android 17 上の all apps に対する background audio hardening で、visible activity または適切な foreground service が必要になる。第二層は targetSdkVersion 37 以上の app に対する追加制限で、background foreground service が WIU capability を持つ必要がある。

顧客向けには、OS update だけで発生しうる共通制限と、targetSdkVersion 37 化で強まる追加条件を分けて説明する必要がある。特に silent failure は検知しづらいため、`AudioHardening` log、`dumpsys audio`、audio focus result code を使った検証が重要になる。

---

# 変更内容（What Changed）

公式文書上の変更点:
- Android 17 から background audio interaction に audio framework level の制限がかかる。
- 対象は audio playback、audio focus request、volume change API。
- all apps running on Android 17 では、visible activity または `SHORT_SERVICE` ではない foreground service が必要。
- targetSdkVersion 37 以上では、background で動作する foreground service に WIU capability が必要。
- exact alarm permission があり `USAGE_ALARM` stream を扱う場合は WIU capability requirement が免除される。
- invalid lifecycle で対象 API を呼ぶと、playback / volume change は silently fail し、audio focus は `AUDIOFOCUS_REQUEST_FAILED` を返す。

AOSP で未確認の点:
- AudioService / AudioManager / AudioFocus / volume API の enforcement point。
- visible activity、foreground service、`SHORT_SERVICE` 除外、WIU capability の判定 path。
- targetSdkVersion 37 gate の実装箇所。
- exact alarm permission + `USAGE_ALARM` exception の判定 path。
- silent failure、`AUDIOFOCUS_REQUEST_FAILED`、`AudioHardening` log / dumpsys 出力の実装。
- compat framework Change ID と default state。

## 適用条件（Applicability）

この変更がいつ適用されるかを OS 条件と targetSdkVersion 条件に分けて説明する。

### OS アップデート時の挙動（OS Update Behavior）

- Android 17 に OS アップデートしただけで適用されるか: 公式文書上は Yes / Conditional。Android 17 上で対象 background audio interaction を行う all apps に適用され、target API level 37 かどうかに関係ないと詳細ページが説明している。ただし AOSP gate 未確認。
- targetSdkVersion に依存しない根拠: 詳細ページは共通条件について、whether or not the app targets API level 37 と説明している。
- Android 16 以前での挙動: background audio interaction に同じ hardening があったかは AOSP diff 未確認。公式文書は Android 17 から enforcement されると説明している。

### targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- targetSdkVersion 37 以上で適用されるか: Yes / Conditional candidate。targetSdkVersion 37 以上では、background で動作する foreground service に WIU capability が必要になると公式文書が説明している。
- Android 17 / targetSdkVersion 36 と Android 17 / targetSdkVersion 37 の差分: targetSdkVersion 36 でも共通制限は対象候補。targetSdkVersion 37 では WIU capability requirement が追加される候補。
- opt-out / exception: exact alarm permission が付与され、`USAGE_ALARM` audio stream を扱う場合は WIU capability requirement が免除される。compat opt-out の有無は未確認。

### その他の条件（Other Conditions）

- app lifecycle: visible activity がある場合は影響を受けにくい。PiP を含む visible-to-user 状態で audio API を使う場合は詳細ページ上、対象外と説明されている。
- foreground service: background audio を継続する場合は `mediaPlayback` FGS など、`SHORT_SERVICE` ではない foreground service が必要。
- WIU capability: targetSdkVersion 37 以上では、user-initiated operation または app visible 中に開始された FGS など、WIU capability を持つ foreground service が必要。
- exceptions: exact alarm permission + `USAGE_ALARM` stream。
- impacted use cases: app open 中または explicit user trigger に基づく audio interaction continuation model に従わない場合、silent suppression の可能性が高い。`BOOT_COMPLETE` に応答して FGS を開始し audio interaction する例は suppression 候補として公式文書に挙げられている。
- lower risk: Media3 `MediaSessionService` を使う background playback、Telecom API を使う VOIP、visible activity / PiP 中の audio operation。

---

# AOSP 調査（AOSP Investigation）

## checkout 状態（Checkout Status）

確認コマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list 'android-17*'
```

結果:
- `frameworks-base` の `status --short` は空で、dirty working tree は確認されなかった。
- `android-16.0.0_r4` tag は存在する。
- `android-17*` tag は local checkout に存在しない。

根拠上の制約:
- Android 17 AOSP tag が local `frameworks-base` にないため、`android-16.0.0_r4` と Android 17 tag の明示的な source diff は実行できない。
- そのため、local working tree や未確定 branch を platform evidence として扱わない。
- 本レポートの AOSP-backed conclusion は Low confidence に留める。

## 関連ファイル（Related Files）

Android 17 AOSP tag 未取得のため、tag diff に基づく related files は未確定。

Android 17 tag 公開後に確認すべき候補:
- `media/java/android/media/AudioManager.java`
- `media/java/android/media/AudioTrack.java`
- `services/core/java/com/android/server/audio/AudioService.java`
- `services/core/java/com/android/server/audio/MediaFocusControl.java`
- `services/core/java/com/android/server/am/ActiveServices.java`
- `services/core/java/com/android/server/am/ActivityManagerService.java`
- `services/core/java/com/android/server/pm/permission/` または exact alarm / app-op 判定 path
- API / constants for `AUDIOFOCUS_REQUEST_FAILED`
- dumpsys / logcat の `AudioHardening` 出力 path
- compat framework 定義ファイル内の background audio hardening 関連 Change ID

Note:
- 実際の playback write enforcement は framework Java 層だけでなく native audio path、AAudio、OpenSL ES、media server / AudioFlinger 側にある可能性がある。Android 17 tag 入手後は該当 project も evidence 対象として確認する必要がある。

## 確認したソース文脈（Source Context Reviewed）

AOSP tag diff は未実行。以下は公式文書から見た確認予定の source context であり、AOSP evidence ではない。

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| Audio playback enforcement path | 未確認 | invalid lifecycle では playback が silenced / fail すると公式文書が説明 | `AudioTrack.write()`、AAudio、OpenSL ES、Media3 / ExoPlayer への影響確認に必要なため |
| Audio focus request path | 未確認 | `AUDIOFOCUS_REQUEST_FAILED` を返すと公式文書が説明 | developer-visible failure signal がある API であり、検証と mitigation に直結するため |
| Volume / ringer mode API path | 未確認 | volume change / ringer mode calls が silently ignored と詳細ページが説明 | silent failure の主要対象であり、customer impact が大きいため |
| Foreground service / WIU capability gate | 未確認 | targetSdkVersion 37 以上では WIU capability が必要と公式文書が説明 | targetSdkVersion impact と exception 判定の根拠になるため |
| Exact alarm + `USAGE_ALARM` exception path | 未確認 | exact alarm permission + alarm stream は WIU requirement 免除と公式文書が説明 | app impact を絞る exception 条件であるため |
| compat framework entry | 未確認 | targetSdkVersion gate / testing toggle の有無は不明 | primary classification と confidence 確定に必要なため |

必須記入項目:
- Entry point / caller: 未確認。想定される entry point は `AudioTrack.write()` / AAudio / OpenSL ES playback write、`AudioManager.requestAudioFocus()`、`AudioManager.setStreamVolume()` / `adjustStreamVolume()` / `setRingerMode()`。
- Relevant class or service responsibility: audio playback enforcement、audio focus policy、volume / ringer mode policy、foreground service state / WIU capability 判定、exact alarm / audio usage exception。
- Runtime path from app API / system event to changed code: app が background で audio API を呼ぶ -> system が visible activity / foreground service / targetSdkVersion / WIU capability / exact alarm + `USAGE_ALARM` を判定 -> invalid lifecycle なら playback / volume API は silent suppression、audio focus は `AUDIOFOCUS_REQUEST_FAILED`、という path が想定される。AOSP evidence としては未確認。
- Why unrelated code paths were excluded: tag diff 未実行のため、除外判断は未完了。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
| Android 17 tag 未取得のため source diff 未確認 | 公式文書上は changed condition / added enforcement と読める | background audio interaction が lifecycle / FGS / WIU 条件で制限されると説明されている | Low |

必須分類:
- Added behavior: 未確認。audio hardening enforcement が追加された可能性がある。
- Removed behavior: 未確認。background からの自由な playback / focus / volume operation が制限された可能性がある。
- Changed condition: 公式文書上は該当候補。valid lifecycle、visible activity、foreground service、WIU capability、exact alarm + `USAGE_ALARM` によって許可 / 抑制が分岐すると読める。
- Changed default: 未確認。background audio operation の default allow / suppress 条件が変わった可能性がある。
- No behavior change: 現時点では公式文書上の説明と矛盾するため候補ではないが、AOSP tag diff で確認が必要。

---

# 影響分析（Impact Analysis）

## 影響を受ける可能性があるアプリ（Potentially Affected Apps）

- music streaming、radio、podcast、audiobook app。
- video streaming app で screen off / background playback を user affordance として提供する app。
- background service から short sound、notification-like sound、volume change、ringer mode change を行う app。
- alarm、timer、reminder app。特に `USAGE_ALARM` と exact alarm permission の条件確認が必要。
- game / communication / productivity app で background component が audio focus や volume API を呼ぶ実装。
- boot receiver や scheduled job から foreground service を開始し、user-visible trigger なしに audio interaction を行う app。

## 影響を受けにくいアプリ（Less Likely Affected）

- visible activity 中だけ audio API を使う app。
- PiP 中など user-visible 状態で audio を使う app。
- Media3 `MediaSessionService` で background playback lifecycle を管理している app。
- Telecom API を適切に使う VOIP / video calling app。
- audio playback、audio focus request、volume / ringer mode API を使わない app。

## 顧客向けリスク（Customer-facing Risk）

- background playback が silent に抑制され、例外や明示的 failure message が出ない。
- audio focus request が `AUDIOFOCUS_REQUEST_FAILED` になり、playback coordination が崩れる。
- volume / ringer mode changes が無視され、ユーザーの期待する音量変更が起きない。
- boot / alarm / scheduled work / background-started FGS からの audio interaction が Android 17 で動作しない可能性。
- silent failure のため、logcat / dumpsys / explicit result code check を入れていないと検知が遅れる。

---

# 対応候補（Recommended Action Candidates）

## 実装対応（Implementation）

- background audio interaction を行う箇所を棚卸しする。playback、audio focus、volume / ringer mode API を別々に確認する。
- background playback は Media3 `MediaSessionService` の利用を優先する。
- Media3 を使わない場合は、background audio が発生しうる user flow で、app が foreground にいる間に `mediaPlayback` foreground service を開始する。
- targetSdkVersion 37 以上では、foreground service が WIU capability を持つよう、user-initiated operation または visible state から開始する。
- transient buffering や `AUDIOFOCUS_LOSS_TRANSIENT` など 10 分未満の一時中断では、再開意図があるなら `mediaPlayback` FGS を維持する。
- playback 完了、`AUDIOFOCUS_LOSS`、UMO pause、media key pause、recover 不可能な failure では、audio interaction、foreground service、media session を終了し、再開は明示的な user action から行う。
- alarm use case は exact alarm permission と `USAGE_ALARM` stream の条件を明示的に確認する。

## 検証対応（Testing）

- Android 16 / targetSdkVersion 36 で background audio baseline を確認する。
- Android 17 / targetSdkVersion 36 と Android 17 / targetSdkVersion 37 の両方で、playback、audio focus、volume / ringer mode API を確認する。
- 詳細ページの ADB command を使って hardening を切り替えて確認する。

```bash
adb shell cmd audio set-enable-hardening <enable|disable|throw>
```

- `enable`: all apps に制限を有効化し、WIU FGS requirement も targetSdkVersion に関係なく適用する。exact alarm + alarm stream exception も無効化される。
- `disable`: audio hardening restrictions を無効化する。
- `throw`: `enable` と同様に制限を有効化し、volume / focus interaction では `IllegalStateException`、playback write では error / crash により loud failure を発生させる。
- `adb dumpsys audio` と `logcat` で `AudioHardening` prefix の記録を確認する。`level: full` は FGS はあるが WIU capability がない状態、`level: partial` は FGS がない状態を示す。

## 顧客説明候補（Customer Explanation）

Android 17 では、ユーザーが意図していない background audio operation を抑制するため、background audio interaction に制限が加わります。background で音声再生、audio focus request、volume / ringer mode change を行う app は、visible activity または適切な foreground service を持つ必要があります。targetSdkVersion 37 以上では、background foreground service に while-in-use capability が必要になるため、user-initiated flow から foreground service を開始する設計にしてください。

---

# 検証マトリクス（Verification Matrix）

| Device OS | targetSdkVersion | App condition | Expected behavior |
| --- | --- | --- | --- |
| Android 16 | 36 | background audio interaction | baseline。playback / focus / volume API の現行挙動を確認。 |
| Android 17 | 36 | visible activity または non-`SHORT_SERVICE` FGS なし | playback / volume は silent suppression、focus は `AUDIOFOCUS_REQUEST_FAILED` の可能性。AOSP gate 未確認。 |
| Android 17 | 36 | visible activity または non-`SHORT_SERVICE` FGS あり | 共通条件を満たす候補。実際の許可条件は AOSP tag で確認が必要。 |
| Android 17 | 37 | background FGS あり、WIU capability なし | target 37 追加制限により suppression の可能性。 |
| Android 17 | 37 | user-initiated / visible state から started FGS with WIU capability | background audio continuation が許可される候補。 |
| Android 17 | 37 | exact alarm permission + `USAGE_ALARM` stream | WIU capability requirement 免除候補。 |

---

# 未解決事項（Open Questions）

- Android 17 AOSP tag 上で、audio hardening enforcement はどの service / native path で実装されているか。
- 共通制限と targetSdkVersion 37 追加制限が compat framework Change ID で管理されているか。
- visible activity / PiP / foreground service / `SHORT_SERVICE` / WIU capability の判定順序。
- exact alarm permission + `USAGE_ALARM` exception の実装条件。
- AudioTrack、AAudio、OpenSL ES、Media3、ExoPlayer、Oboe で failure signal に差があるか。
- `cmd audio set-enable-hardening` の availability、Beta 3 以降の挙動、release build での扱い。

---

# 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

最終影響度:
- 人間による判断が必要

顧客通知要否（Customer Communication Required）:
- 人間による判断が必要

リリース判断:
- 人間による判断が必要

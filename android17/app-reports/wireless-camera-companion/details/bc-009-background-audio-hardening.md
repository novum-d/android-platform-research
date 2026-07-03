# BC-009: Background audio hardening

## 基本情報（Basic Information）

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/17/behavior-changes-all
- URL: https://developer.android.com/about/versions/17/behavior-changes-17
- Section: Background audio hardening

Original statement:
> Android 17 では background audio interaction が制限され、audio playback、audio focus request、volume change API などが、アプリの lifecycle / foreground service / capability 条件を満たさない場合に失敗または mute される、という趣旨の公式説明。

調査対象 Android バージョン:
- From: android-16.0.0_r4
- To: android-17.0.0_r1

## 対象アプリとの関係（Relevance to Target App）

関連するアプリ機能:
- カメラ接続完了音、転送完了音、エラー音。
- カメラのシャッター音や操作音をアプリ側で再生する機能。
- 転送完了、タイマー、リモート撮影通知に音声 / アラームを使う機能。
- バックグラウンドで音声再生、audio focus request、volume / ringer mode 変更を行う処理。

関連する API / permission / component:
- `AudioManager.requestAudioFocus()`
- `AudioManager.setStreamVolume()` / `adjustStreamVolume()` / `adjustVolume()`
- `AudioAttributes.USAGE_ALARM`
- foreground service
- exact alarm permission
- AppOps `OP_PLAY_AUDIO` / `OP_TAKE_AUDIO_FOCUS` / `OP_CONTROL_AUDIO`

アプリが該当する可能性:
- 低いから Conditional。カメラ連携・画像転送が主用途で、バックグラウンド音声再生が主要機能でなければ影響は限定的。ただし、バックグラウンドで転送完了音、アラーム、音声通知、音量変更を行う場合は該当し得る。

確認したアプリ実装:
- File / module: 未確認。
- Symbol / entry point: 未確認。
- Manifest / permission: foreground service / exact alarm permission の利用有無は未確認。
- Runtime condition: バックグラウンド状態で音声 API を呼ぶ場合。

## 適用条件分類（Applicability Classification）

主分類（Primary classification）:
- OS_UPDATE_ALL_APPS / TARGET_SDK_37_CONDITIONAL

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | Yes / Conditional | all apps 側の共通制限は targetSdkVersion 37 を必須にしない。 |
| targetSdkVersion 37 以上が必要か | 追加制限では Yes | target 側レポートでは CINNAMON_BUN 以上で strict level に進む条件を確認。 |
| 追加の実行時条件があるか | Yes | background audio interaction、AppOps、foreground service / foreground audio control capability、exact alarm / `USAGE_ALARM` 条件。 |
| Compat Change ID が関係するか | No / 未確認 | `frameworks-base` では compat ChangeId ではなく audio flags / AppOps / hardening override が主要条件。 |

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17。
- targetSdkVersion: 共通制限は条件なし。target 37 追加制限は targetSdkVersion 37 以上。
- Permission/API/component condition: audio playback、audio focus request、volume / ringer mode API、foreground service、exact alarm permission、`USAGE_ALARM`。
- App state/process condition: アプリが background にいて、audio AppOps / process capability により操作が許可されない状態。

Compat framework:
- Change ID: 確認されず。
- Change name: N/A
- Default state: audio flags / AppOps / AudioPolicy hardening override に依存。
- Toggleable for testing: privileged `AudioManager.setHardeningOverride()` / shell hardening override path。

## AOSP 調査（AOSP Investigation）

関連ファイル:
- `services/core/java/com/android/server/audio/HardeningEnforcer.java`
- `services/core/java/com/android/server/audio/AudioService.java`
- `services/core/java/com/android/server/am/psc/OomAdjusterImpl.java`
- `services/core/java/com/android/server/am/psc/CapabilityController.java`
- `core/java/android/app/ActivityManager.java`
- `core/java/android/app/AppOpsManager.java`

確認したソース文脈（Source Context Reviewed）:

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `HardeningEnforcer.blockVolumeMethod()` | AppOps による audio hardening の土台あり | AppOps、targetSdk、exact alarm、hardening override により volume API の block level を決める | volume API が silent no-op になる条件の根拠。 |
| `AudioService.requestAudioFocus()` | hardening block 時に focus request failure | Android 17 でも block 時に `AUDIOFOCUS_REQUEST_FAILED` を返す | audio focus request の開発者可視結果。 |
| `AudioService.playbackHardeningEvent()` | playback hardening event を受ける | reason / usage 付きで background playback mute をログ・metrics に記録 | playback mute の framework 側証跡。 |
| `OomAdjusterImpl` / `CapabilityController` | 従来の process capability 管理 | foreground audio control capability を FGS / process state と結びつける | foreground service / WIU 相当条件との接続点。 |

差分解釈（Diff Interpretation）:
- Changed condition / gate: AppOps、process capability、targetSdkVersion 37、exact alarm exception、hardening flags により block level が変わる。
- Changed default / enforcement: background の audio focus は failure、volume API は no-op、playback は mute され得る。
- No behavior change found: カメラ機能そのものの Camera API 変更ではない。

適用ゲート根拠（Applicability Gate Evidence）:
- targetSdkVersion gate: 共通制限では必須ではない。target 37 追加制限では CINNAMON_BUN 以上が strict level の条件。
- CompatChanges.isChangeEnabled / ChangeId: 確認されず。
- Permission/AppOps gate: `OP_PLAY_AUDIO` / `OP_TAKE_AUDIO_FOCUS` / `OP_CONTROL_AUDIO` / `OP_CONTROL_AUDIO_PARTIAL`。
- Gate conclusion: Android 17 上で background audio interaction を行い、visible activity / 適切な foreground service / foreground audio control capability / alarm exception を満たさない場合に影響する。

## 事実・観察・仮説・結論（Facts / Observations / Hypotheses / Conclusion）

事実（Facts）:
- Android 17 の `HardeningEnforcer` / `AudioService` は background audio interaction に対する focus / volume / playback hardening path を持つ。
- targetSdkVersion 37 以上では strict level の追加条件がある。

観察（Observations）:
- カメラ連携アプリでは、音声再生が主機能でない限り該当可能性は低い。
- ただし、転送完了音、アラーム、バックグラウンド通知音、音量変更を独自実装している場合は確認対象になる。

仮説（Hypotheses）:
- 対象アプリがバックグラウンド転送完了時に音声を鳴らす、またはリモート撮影タイマーで `USAGE_ALARM` を使う場合、Android 17 / targetSdkVersion 37 で failure mode が変わる可能性がある。

結論（Conclusion）:
- カメラ連携アプリでは「影響なしから軽微」と仮置きする。ただし background audio API usage がある場合は、Android 17 / targetSdkVersion 37 の個別確認が必要。

## アプリ影響（App Impact）

想定される影響:
- バックグラウンド状態で転送完了音やアラーム音が鳴らない。
- `requestAudioFocus()` が `AUDIOFOCUS_REQUEST_FAILED` を返す。
- volume / ringer mode API が silent no-op になる。

ユーザー影響:
- 転送完了やエラーを音で認識できない。
- タイマー撮影やリモート操作の音声フィードバックが期待通り動かない。

開発者影響:
- background audio interaction の棚卸し。
- user-initiated flow、foreground service、exact alarm + `USAGE_ALARM` の条件確認。
- audio focus failure の戻り値処理。

推奨対応候補:
- 音声再生 / audio focus / volume 変更 API の利用箇所を検索する。
- バックグラウンド転送中・画面消灯中・通知経由復帰時に音声フィードバックをテストする。
- アラーム用途なら exact alarm permission と `AudioAttributes.USAGE_ALARM` を確認する。

## Confidence

Confidence:
- Medium

Confidence の根拠:
- AOSP Java framework 側の focus / volume / capability path は確認済み。
- 実際の playback mute 最終判定は native AudioPolicy / audioserver 側にもまたがる。

不足している根拠:
- 対象アプリの background audio API usage。
- foreground service / exact alarm / audio usage 設定。

---

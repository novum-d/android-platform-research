# バックグラウンド音声の制限強化 - 1ページ要約

> 役割メモ:
> この要約は、バックグラウンド音声の制限強化の targetSdkVersion 37 追加条件を中心に扱う。
> Android 17 上の全アプリに関係する共通制限は [all/media/background-audio-hardening-summary.md](../../all/media/background-audio-hardening-summary.md) を参照する。

## 対象

Android 17 Behavior Change

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

## 適用条件

- 主分類（Primary classification）: TARGET_SDK_37_CONDITIONAL
- OS アップデート / 全アプリ: 共通制限は [all/media/background-audio-hardening-summary.md](../../all/media/background-audio-hardening-summary.md) 側で扱う。
- targetSdkVersion 37 以上: Android 17 の `HardeningEnforcer` は `targetSdk < Build.VERSION_CODES.CINNAMON_BUN` を緩和条件にしており、37 以上では strict level に進みうる。
- その他の必須条件: background audio interaction、AppOps denial、FGS / foreground audio control capability 不足、exact alarm + `USAGE_ALARM` exception を満たさないこと。
- Compat Change ID: 確認できず
- Compat default state: audio flags / AppOps / AudioPolicy hardening override に依存
- 信頼度: Medium

## 早見マトリクス

| シナリオ | 影響 |
| --- | --- |
| Android 17 / targetSdkVersion 36 | all-apps 共通制限の対象。pre-CINNAMON_BUN として partial level まで緩和される。 |
| Android 17 / targetSdkVersion 37 | strict level の追加制限に進みうる。 |
| Android 17 / targetSdkVersion 37 + exact alarm + `USAGE_ALARM` | focus path では partial level に緩和される。 |

## 要約

Android 17 では、targetSdkVersion 37 以上のアプリに対して background audio hardening がより厳しくなる。AOSP では `HardeningEnforcer` の CINNAMON_BUN target check、AppOps、alarm exception、foreground audio control capability が確認できる。

## 顧客影響

- targetSdkVersion 37 化後、background の audio focus request が失敗しやすくなる。
- background の volume / ringer mode 変更が no-op になる可能性がある。
- FGS があっても foreground audio control capability を満たせない場合、playback / focus / volume が制限される可能性がある。

## 影響対象

- 対象アプリ: background で audio playback、audio focus request、volume change APIs を使うアプリ。
- 対象機能: 音楽、ポッドキャスト、アラーム、通話、ナビゲーション、音声通知。
- 対象条件: targetSdkVersion 37 以上、background state、FGS / foreground audio control capability 不足、alarm exception 不成立。

## 対応要否

- 必須対応: targetSdkVersion 37 へ上げる前に background audio API 呼び出し箇所を棚卸しする。
- 推奨対応: Media3 `MediaSessionService` または user-initiated な `mediaPlayback` FGS flow を使う。
- alarm 対応: exact alarm permission と `AudioAttributes.USAGE_ALARM` を明確にする。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 36 | baseline。 |
| Android 17 | 36 | partial level の共通制限を確認。 |
| Android 17 | 37 | strict level の追加制限、focus failure、volume no-op、playback mute を確認。 |

## 顧客向け説明

Android 17 で targetSdkVersion 37 以上にすると、background audio interaction の条件がより厳しくなります。background で音声再生や audio focus request、volume change を行う場合は、適切な foreground service / foreground audio control capability を満たす設計にしてください。alarm use case は exact alarm permission と `USAGE_ALARM` の組み合わせを確認してください。

## 根拠

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-17
- AOSP ファイル:
  - `services/core/java/com/android/server/audio/HardeningEnforcer.java`
  - `services/core/java/com/android/server/audio/AudioService.java`
  - `services/core/java/com/android/server/am/psc/OomAdjusterImpl.java`
  - `services/core/java/com/android/server/am/psc/CapabilityController.java`
  - `core/java/android/app/ActivityManager.java`
- 差分解釈: `targetSdk < Build.VERSION_CODES.CINNAMON_BUN` の緩和分岐があり、targetSdkVersion 37 以上では strict level へ進みうる。
- 適用ゲートの結論: Android 17 + targetSdkVersion 37 以上 + background audio runtime condition。

## 人間の判断欄

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断

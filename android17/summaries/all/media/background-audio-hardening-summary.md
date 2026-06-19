# Background audio hardening - 1ページ要約

> 役割メモ:
> この要約は Background audio hardening の Android 17 全アプリ共通制限を中心に扱う。
> targetSdkVersion 37 追加条件は [target/media/background-audio-hardening-summary.md](../../target/media/background-audio-hardening-summary.md) も参照する。

## 対象（Target）

Android 17 Behavior Change

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

## 適用条件（Applicability）

- 主分類（Primary classification）: OS_UPDATE_ALL_APPS
- OS アップデート / 全アプリ（OS update / all apps）: Android 17 上で background audio interaction を行い、audio AppOps / lifecycle / FGS capability 条件を満たせない場合に影響する。
- targetSdkVersion 37 以上: 共通制限の必須条件ではない。target 37 では strict level の追加条件がある。
- その他の必須条件（Other required conditions）: audio playback、audio focus request、volume / ringer mode API を background で利用すること。
- Compat Change ID: 確認できず
- Compat default state: audio flags / AppOps / AudioPolicy hardening override に依存
- 信頼度: Medium

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 16 / targetSdkVersion 36 | baseline。hardening の土台はあるが、Android 17 の CINNAMON_BUN 分岐・alarm exception・capability 連携はない。 |
| Android 17 / targetSdkVersion 36 | 共通制限の対象。partial level の緩和は残るが、AppOps / process capability 次第で focus / volume / playback が制限される。 |
| Android 17 / targetSdkVersion 37 | 共通制限に加え、strict level の追加条件が入る。詳細は target 側要約を参照。 |

## 要約（Summary）

Android 17 では、background からの audio playback、audio focus request、volume / ringer mode API が audio hardening の対象になる。AOSP では `HardeningEnforcer`、`AudioService`、AppOps、foreground audio control capability の連携が確認できる。

## 顧客影響（Customer Impact）

- background から audio focus を取得する処理は `AUDIOFOCUS_REQUEST_FAILED` を受ける可能性がある。
- background から volume / ringer mode を変更する処理は例外なしで no-op になる可能性がある。
- playback は native AudioPolicy / audioserver 側で mute され、framework には `AudioHardening background playback ... muted` event が通知される。

## 影響対象（Who Is Affected）

- 対象アプリ: music、radio、podcast、audiobook、video streaming、alarm、timer、reminder、background sound、通話、ナビゲーション。
- 対象機能: background playback、audio focus request、volume / ringer mode change、boot / scheduled work からの audio interaction。
- 対象条件: visible activity または適切な foreground service / foreground audio control capability なしに background audio interaction を行う場合。

## 対応要否（Required Action）

- 必須対応: playback、audio focus、volume / ringer mode API の background 利用箇所を棚卸しする。
- 推奨対応: Media3 `MediaSessionService` または user-initiated な `mediaPlayback` FGS flow を使う。
- 実装確認: audio focus result code、`AudioHardening` log、`dumpsys audio` を確認する。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 16 | 36 | baseline を確認。 |
| Android 17 | 36 | background 条件次第で playback mute、volume no-op、focus failure。 |
| Android 17 | 37 | 上記に加えて strict level の追加条件を確認。 |

## 顧客向け説明（Explanation for Customers）

Android 17 では、ユーザーが意図しない background audio operation を防ぐため、background audio interaction が制限されます。background で音声再生、audio focus request、volume / ringer mode change を行う場合は、visible activity または適切な foreground service flow から実行してください。

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-all
- Detail documentation: https://developer.android.com/about/versions/17/changes/bg-audio
- AOSP ファイル:
  - `services/core/java/com/android/server/audio/HardeningEnforcer.java`
  - `services/core/java/com/android/server/audio/AudioService.java`
  - `services/core/java/com/android/server/am/psc/OomAdjusterImpl.java`
  - `services/core/java/com/android/server/am/psc/CapabilityController.java`
  - `core/java/android/app/AppOpsManager.java`
- 差分解釈: Android 17 では audio hardening の条件が AppOps、targetSdkVersion、alarm exception、foreground audio control capability、AudioPolicy override と結合されている。
- Gate conclusion: all-apps 共通制限は Android 17 OS 条件。targetSdkVersion 37 は追加 strict 条件。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断

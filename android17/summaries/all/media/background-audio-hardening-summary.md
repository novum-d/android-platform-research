# Background audio hardening - 1ページ要約（One Page Summary）

> 役割メモ:
> この要約は Background audio hardening の Android 17 全アプリ共通制限を中心に扱う。
> targetSdkVersion 37 追加条件は [target/media/background-audio-hardening-summary.md](../../target/media/background-audio-hardening-summary.md) も参照する。

## 対象（Target）

Android 17 Behavior Change

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP tag

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

## 適用条件（Applicability）

- 主分類（Primary classification）: UNKNOWN_NEEDS_MORE_EVIDENCE
- OS アップデート / 全アプリ（OS update / all apps）: 公式文書上は該当候補。Android 17 上で対象 background audio interaction を行う all apps に適用され、target API level 37 かどうかに関係ないと詳細ページが説明している。
- targetSdkVersion 37 以上: 追加条件あり。targetSdkVersion 37 以上では、background で動作する foreground service に while-in-use (WIU) capability が必要になる。
- その他の必須条件（Other required conditions）: app が visible activity または適切な foreground service なしに、background で audio playback、audio focus request、volume / ringer mode API を使うこと。
- Compat Change ID: Unknown
- Compat default state: Unknown

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 共通制限の対象候補。visible activity または non-`SHORT_SERVICE` FGS がない background audio interaction は抑制される可能性。 |
| Android 17 / targetSdkVersion 37 | 共通制限に加え、background FGS に WIU capability が必要になる候補。 |
| Android 17 / targetSdkVersion 37 + exact alarm + `USAGE_ALARM` | WIU capability requirement は免除候補。AOSP gate 未確認。 |

## 要約（Summary）

Android 17 では、background からの audio playback、audio focus request、volume / ringer mode API に制限がかかる。invalid lifecycle で呼ぶと playback / volume は silent failure、audio focus は `AUDIOFOCUS_REQUEST_FAILED` になる。

## 顧客影響（Customer Impact）

- 要確認

## 影響対象（Who Is Affected）

- 対象アプリ: music、radio、podcast、audiobook、video streaming、alarm、timer、reminder、background sound を使う app。
- 対象機能: background playback、audio focus request、volume / ringer mode change、boot / scheduled work からの audio interaction。
- 対象条件: visible activity または適切な foreground service / WIU capability なしに background audio interaction を行う場合。

## 対応要否（Required Action）

- 必須対応: playback、audio focus、volume / ringer mode API の background 利用箇所を棚卸しする。
- 推奨対応: Media3 `MediaSessionService` を使う。使わない場合は、user-initiated flow で app が foreground にいる間に `mediaPlayback` FGS を開始する。
- target 37 対応: FGS が WIU capability を持つよう、user action または visible state から開始する。alarm use case は exact alarm permission と `USAGE_ALARM` を確認する。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 16 | 36 | baseline。background audio interaction の現行挙動を確認。 |
| Android 17 | 36 | 共通制限の対象。playback / volume は silent suppression、focus は `AUDIOFOCUS_REQUEST_FAILED` の可能性。 |
| Android 17 | 37 | 共通制限に加え、background FGS の WIU capability requirement が追加される可能性。 |

## 顧客向け説明（Explanation for Customers）

Android 17 では、ユーザーが意図しない background audio operation を防ぐため、background audio interaction が制限されます。background で音声再生や audio focus request、volume / ringer mode change を行う場合は、visible activity または適切な foreground service が必要です。

targetSdkVersion 37 以上では、background foreground service に while-in-use capability が必要になります。音楽や podcast などの継続再生は Media3 `MediaSessionService` または user-initiated な `mediaPlayback` foreground service flow で確認してください。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-all
- Detail documentation: https://developer.android.com/about/versions/17/changes/bg-audio
- Original statement: Android 17 から background audio interaction に制限がかかり、playback / volume API は silently fail、audio focus は `AUDIOFOCUS_REQUEST_FAILED` を返す。targetSdkVersion 37 以上では WIU capability requirement が追加される。
- AOSP files: 未確認。local `frameworks-base` に `android-17*` tag がない。
- AOSP source context: 未確認。tag 間 diff が実行できない。
- Diff interpretation: 未分類。公式文書上は changed condition / added enforcement と読めるが、AOSP diff による確認は Android 17 tag 待ち。
- Gate conclusion: Unknown。公式文書上は Android 17 all apps 共通制限 + targetSdkVersion 37 追加 WIU 条件。targetSdkVersion gate / compat framework evidence は未取得。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Human decision required

判断（Decision）:
- Further investigation required after Android 17 AOSP tag is available

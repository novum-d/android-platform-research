# Touchpads deliver relative events by default during pointer capture - 1ページ要約（One Page Summary）

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
- OS アップデート / 全アプリ（OS update / all apps）: 公式文書上は該当候補。Android 17 の all apps ページに掲載され、targetSdkVersion 条件は示されていない。
- targetSdkVersion 37 以上: 公式文書上は不要。AOSP gate 未確認。
- その他の必須条件（Other required conditions）: app が pointer capture を使い、input device が touchpad で、captured event の座標解釈に依存していること。
- Compat Change ID: Unknown
- Compat default state: Unknown

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | touchpad + pointer capture で default relative motion event が届く可能性。AOSP gate 未確認。 |
| Android 17 / targetSdkVersion 37 | targetSdkVersion 36 と同様の可能性。公式文書に targetSdkVersion 条件なし。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | absolute coordinate 前提の pointer capture 実装で cursor movement / remote pointer mapping が変わる可能性。 |

## 要約（Summary）

Android 17 では、touchpad が pointer capture 中に default で relative motion event を deliver する。pointer capture 中の touchpad event を absolute coordinate として扱っている app は、入力解釈を見直す必要がある。

## 顧客影響（Customer Impact）

- 要確認

## 影響対象（Who Is Affected）

- 対象アプリ: pointer capture を使う game、remote desktop、streaming、emulator、virtualization、drawing、CAD、editor。
- 対象機能: camera control、remote cursor mapping、drag、pan、selection、viewport navigation。
- 対象条件: touchpad input を captured event として受け取り、absolute coordinate 前提で処理している場合。

## 対応要否（Required Action）

- 必須対応: pointer capture 利用箇所で touchpad event の座標解釈を確認する。
- 推奨対応: relative motion event 前提に処理するか、absolute coordinate behavior が必要な場合は Android 17 以上で `requestPointerCapture(int)` と `View.POINTER_CAPTURE_MODE_ABSOLUTE` を使う。
- 不要: pointer capture を使わない app、touchpad input を扱わない app、relative delta 前提の実装では直接影響は限定的。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 16 | 36 | baseline。touchpad + pointer capture の event coordinate behavior を確認。 |
| Android 17 | 36 | touchpad captured event は default relative motion event として届くと公式文書は説明。 |
| Android 17 | 37 | targetSdkVersion 36 と同じ期待。targetSdkVersion 条件は公式文書に記載なし。 |

## 顧客向け説明（Explanation for Customers）

Android 17 では、touchpad を pointer capture 中に使った場合、default で relative motion event が app に届くようになります。absolute coordinate 前提の実装では cursor movement や remote pointer mapping が変わる可能性があります。

従来の absolute coordinate behavior が必要な場合は、Android 17 の `requestPointerCapture(int)` で `View.POINTER_CAPTURE_MODE_ABSOLUTE` を指定してください。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-all
- Original statement: Android 17 から、touchpad は pointer capture 中に absolute coordinates ではなく relative motion events を default で deliver する。
- AOSP files: 未確認。local `frameworks-base` に `android-17*` tag がない。
- AOSP source context: 未確認。tag 間 diff が実行できない。
- Diff interpretation: 未分類。公式文書上は changed default / API addition with behavior mitigation と読めるが、AOSP diff による確認は Android 17 tag 待ち。
- Gate conclusion: Unknown。公式文書上は Android 17 all apps + touchpad + pointer capture condition。targetSdkVersion gate / compat framework evidence は未取得。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Human decision required

判断（Decision）:
- Further investigation required after Android 17 AOSP tag is available

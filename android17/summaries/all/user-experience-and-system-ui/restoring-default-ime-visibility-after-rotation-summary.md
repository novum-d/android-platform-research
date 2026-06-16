# Restoring default IME visibility after rotation - 1ページ要約（One Page Summary）

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
- その他の必須条件（Other required conditions）: rotation など configuration change が発生し、app がそれを自身で処理せず、previous IME visibility の自動復元を期待していること。
- Compat Change ID: Unknown
- Compat default state: Unknown

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | unhandled configuration change 後、previous IME visibility が自動復元されない可能性。AOSP gate 未確認。 |
| Android 17 / targetSdkVersion 37 | targetSdkVersion 36 と同様の可能性。公式文書に targetSdkVersion 条件なし。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | rotation 後に keyboard が閉じたままになり、明示的な IME 表示要求が必要になる可能性。 |

## 要約（Summary）

Android 17 では、rotation などの configuration change が発生し、その変更を app 自身が処理しない場合、以前表示されていた IME / soft keyboard は自動復元されない。rotation 後も keyboard を表示したい screen では、app が明示的に request する必要がある。

## 顧客影響（Customer Impact）

- 要確認

## 影響対象（Who Is Affected）

- 対象アプリ: 入力画面で rotation 後も keyboard 表示を継続したいアプリ。
- 対象機能: 検索、ログイン、チャット、メモ入力、業務入力フォーム。
- 対象条件: keyboard 表示中に configuration change が発生し、Activity recreation 後の IME 自動復元を期待している場合。

## 対応要否（Required Action）

- 必須対応: rotation / configuration change 後も keyboard が必要な screen を棚卸しする。
- 推奨対応: `android:windowSoftInputMode="stateAlwaysVisible"`、`Activity.onCreate()`、または `onConfigurationChanged()` で明示的に IME 表示を request する。
- 不要: rotation 後に keyboard 表示が不要な screen、入力欄がない screen、すでに focus / IME visibility を明示制御している screen では直接影響は限定的。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 16 | 36 | baseline。rotation 後の IME visibility restoration を確認。 |
| Android 17 | 36 | previous IME visibility は自動復元されないと公式文書は説明。 |
| Android 17 | 37 | targetSdkVersion 36 と同じ期待。targetSdkVersion 条件は公式文書に記載なし。 |

## 顧客向け説明（Explanation for Customers）

Android 17 では、画面回転などで app が処理しない configuration change が発生した後、変更前に表示されていた keyboard は system によって自動復元されません。

rotation 後も keyboard を表示したい場合は、`android:windowSoftInputMode="stateAlwaysVisible"` を設定するか、`Activity.onCreate()` または `onConfigurationChanged()` で明示的に IME 表示を request してください。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-all
- Original statement: Android 17 から、app が処理しない configuration change 後に previous IME visibility は復元されない。
- AOSP files: 未確認。local `frameworks-base` に `android-17*` tag がない。
- AOSP source context: 未確認。tag 間 diff が実行できない。
- Diff interpretation: 未分類。公式文書上は changed default / changed condition と読めるが、AOSP diff による確認は Android 17 tag 待ち。
- Gate conclusion: Unknown。公式文書上は Android 17 all apps + unhandled configuration change condition。targetSdkVersion gate / compat framework evidence は未取得。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Human decision required

判断（Decision）:
- Further investigation required after Android 17 AOSP tag is available

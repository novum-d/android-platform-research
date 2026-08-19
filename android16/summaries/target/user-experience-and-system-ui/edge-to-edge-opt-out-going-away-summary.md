# Edge to edge opt-out going away - 1ページ要約（One Page Summary）

## 対象（Target）

Android 16 Behavior Change

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:

## 適用条件（Applicability）

- 主分類（Primary classification）: `TARGET_SDK_36_CONDITIONAL`
- OS アップデート / 全アプリ（OS update / all apps）: No。targetSdkVersion 35 以下のアプリに OS アップデートだけで適用される根拠は確認していない。
- targetSdkVersion 36 以上: Yes。AOSP の `DISABLE_OPT_OUT_EDGE_TO_EDGE` は `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)`。
- その他の必須条件（Other required conditions）: Android 16 端末上で動作し、アプリが `R.attr.windowOptOutEdgeToEdgeEnforcement=true` に依存している場合に実質影響が出る。
- Compat Change ID: 377864165 / `DISABLE_OPT_OUT_EDGE_TO_EDGE`
- Compat default state: targetSdkVersion 36 以上で default enabled。公開 compat framework changes ページには該当 entry は見つからなかった。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 16 / targetSdkVersion 35 | 本変更による opt-out 無効化は適用されない |
| Android 16 / targetSdkVersion 36 | opt-out 属性は無効。edge-to-edge を回避できない |
| Android 16 / targetSdkVersion 36 + 必須条件 | `windowOptOutEdgeToEdgeEnforcement` 依存画面で UI overlap / insets 不備が顕在化する可能性がある |

## 要約（Summary）

Android 16 では、targetSdkVersion 36 以上のアプリで `windowOptOutEdgeToEdgeEnforcement` による edge-to-edge opt-out が無効になる。
Android 15 端末では targetSdkVersion 36 でも opt-out は引き続き機能すると公式文書が説明しているため、OS 条件と targetSdkVersion 条件を分けて扱う。

## 顧客影響（Customer Impact）

- 影響あり

## 影響対象（Who Is Affected）

- Android 15 の edge-to-edge 強制に対して `windowOptOutEdgeToEdgeEnforcement=true` で回避していたアプリ。
- targetSdkVersion 36 に更新し、Android 16 端末上で動作するアプリ。
- edge-to-edge / insets 対応が未完了の Activity / Window。

## 対応要否（Required Action）

- 必須対応: `windowOptOutEdgeToEdgeEnforcement` 利用箇所の棚卸しと Android 16 / targetSdkVersion 36 での UI 検証。
- 推奨対応: Compose / Views の insets guidance に沿って edge-to-edge 対応を実装し、opt-out 属性を削除する。
- 不要: すでに edge-to-edge 対応済みで、opt-out 属性に依存していない画面。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 15 | 35 | edge-to-edge enforcement は Android 15 の targetSdkVersion 35 変更として有効。ただし opt-out 属性は機能する |
| Android 15 | 36 | 公式文書上、opt-out 属性は引き続き機能する |
| Android 16 | 35 | 本変更による opt-out 無効化は適用されない |
| Android 16 | 36 | opt-out 属性は無効。edge-to-edge 表示を前提に insets 対応が必要 |

## 顧客向け説明（Explanation for Customers）

Android 16 で targetSdkVersion を 36 以上にすると、Android 15 で一時回避として使えた `windowOptOutEdgeToEdgeEnforcement` が効かなくなります。
そのため、Android 16 端末では edge-to-edge 表示を前提に、ステータスバー、ナビゲーションバー、カットアウト、IME とコンテンツが重ならないように対応する必要があります。
targetSdkVersion 35 以下のまま Android 16 に OS アップデートしただけでは、この opt-out 無効化は原則として発生しません。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/16/behavior-changes-16#edge-to-edge
- AOSP files: `PhoneWindow.java`, `attrs.xml`, `WindowManagerGlobal.java`, `ActivityRecord.java`, `current.txt`
- AOSP source context: `PhoneWindow.isEdgeToEdgeEnforced()` が `isOptingOutEdgeToEdgeEnforcement()` を呼び、`DISABLE_OPT_OUT_EDGE_TO_EDGE` Change ID で opt-out 可否を判定する。
- Diff interpretation: added behavior / changed condition / changed default。Android 16 で opt-out 無効化 Change ID が追加され、targetSdkVersion 36 以上で default enabled になる。
- Gate conclusion: Android 16 以上かつ targetSdkVersion 36 以上で適用。実質影響は opt-out 属性に依存していたアプリに限定される。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Critical / High / Medium / Low

判断（Decision）:
- Explain / Monitor / Ignore / Further investigation required

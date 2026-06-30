# Elegant font APIs deprecated and disabled - 1ページ要約（One Page Summary）

## 対象（Target）

Android 16 Behavior Change

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:
- `android16/AGENTS.md` の既定 scope は `android-16.0.0_r1` だが、この調査では依頼に従い `android-16.0.0_r4` を使用した。

## 適用条件（Applicability）

- 主分類（Primary classification）: `TARGET_SDK_36_CONDITIONAL`
- OS アップデート / 全アプリ（OS update / all apps）: No。Android 16 へ OS アップデートしただけで targetSdkVersion 35 以下の false override が無効化される根拠は確認していない。
- targetSdkVersion 36 以上: Yes。`DEPRECATE_UI_FONT_ENFORCE` が targetSdkVersion 36 以上で default enabled。
- その他の必須条件（Other required conditions）: `elegantTextHeight=false`、`TextView#setElegantTextHeight(false)`、`Paint#setElegantTextHeight(false)` の利用、または対象言語の行高・クリッピング・固定高さ UI への依存。
- Compat Change ID: `DEPRECATE_UI_FONT` / 279646685、`DEPRECATE_UI_FONT_ENFORCE` / 349519475
- Compat default state: 279646685 は targetSdkVersion 35 以上、349519475 は targetSdkVersion 36 以上で default enabled。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 16 / targetSdkVersion 35 | `elegantTextHeight` default true。`false` override は維持される想定 |
| Android 16 / targetSdkVersion 36 | `elegantTextHeight=false` が ignored / no-op になり、elegant text height が常に有効 |
| Android 16 / targetSdkVersion 36 + 必須条件 | 対象言語の行高、baseline、固定高さ container、複数行表示が変わる可能性 |
| Android 15 / targetSdkVersion 36 | 指定 Android 15 tag にも enforce gate は存在するが、実機・SDK 条件つきで要確認 |

## 要約（Summary）

Android 16 target のアプリでは、`elegantTextHeight=false` による compact font / compact metrics への opt-out が無視される。
影響は targetSdkVersion 36 化と、該当 API / attribute または対象言語 UI への依存が重なった場合に発生する。

## 顧客影響（Customer Impact）

- 要確認

理由:
- 未指定アプリは targetSdkVersion 35 以降で既に default true のため、差分は限定的。
- false override に依存する UI では、Arabic、Lao、Myanmar、Tamil、Gujarati、Kannada、Malayalam、Odia、Telugu、Thai の表示で行高・baseline・クリッピングが変わる可能性がある。

## 影響対象（Who Is Affected）

- `android:elegantTextHeight="false"` を指定している TextView / TextAppearance。
- `TextView#setElegantTextHeight(false)` または `Paint#setElegantTextHeight(false)` を呼ぶコード。
- 対象言語の文字表示で固定高さ、baseline、line spacing、複数行 clipping を厳密に調整している UI。
- Compose-only UI は直接影響が小さいが、platform font metrics 依存がある箇所は確認対象。

## 対応要否（Required Action）

- 必須対応: false override に依存する箇所があり、targetSdkVersion 36 へ上げる場合は layout 調整が必要。
- 推奨対応: 対象言語で visual regression を実施し、固定高さ container / padding / line spacing を見直す。
- 不要: `elegantTextHeight` を使っておらず、対象言語の表示にも厳密な寸法依存がない場合。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 15 | 35 | default true。`false` override は可能 |
| Android 16 | 35 | OS update だけでは false override 無効化は適用されない想定 |
| Android 16 | 36 | `false` override は ignored / no-op。elegant text height が有効 |

追加テスト:
- `android:elegantTextHeight="false"` 指定あり / なし。
- `TextView#setElegantTextHeight(false)` 呼び出しあり / なし。
- Arabic、Lao、Myanmar、Tamil、Gujarati、Kannada、Malayalam、Odia、Telugu、Thai の単一行、複数行、固定高さ container、EditText、RecyclerView 行。
- Android 15 / targetSdkVersion 36 は、検証可能な環境があれば Android 16 / targetSdkVersion 36 と比較する。

## 顧客向け説明（Explanation for Customers）

Android 16 へ OS アップデートしただけで、targetSdkVersion 35 以下のアプリに `elegantTextHeight=false` 無効化が適用されるとは判断しません。
targetSdkVersion 36 以上に上げると、Android 16 端末上では `elegantTextHeight=false` や `setElegantTextHeight(false)` が効かなくなり、対象言語の文字は elegant text height 前提で描画・測定されます。
固定高さの UI、複数行テキスト、入力欄、ボタン、リスト行などで対象言語の表示崩れがないか確認してください。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/16/behavior-changes-16#elegant-text-height
- AOSP files: `graphics/java/android/graphics/Paint.java`、`libs/hwui/jni/Paint.cpp`、`core/java/android/widget/TextView.java`、`core/java/android/text/style/TextAppearanceSpan.java`、`core/res/res/values/attrs.xml`、`core/api/current.txt`
- AOSP source context: XML/style -> `TextView` -> `TextPaint/Paint#setElegantTextHeight()` -> JNI/minikin family variant selection。
- Diff interpretation: targetSdkVersion 35 で default true、targetSdkVersion 36 で false override no-op。指定 tag 間の core gate 自体には実質差分なし。
- Gate conclusion: 公式 Behavior Change としては Android 16 以上かつ targetSdkVersion 36 以上。実質影響は false override または対象言語の font metrics 依存がある場合。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 未判断

判断（Decision）:
- 未判断

Owner notes:
- 最終優先度、severity、release readiness、顧客 communication priority は repository owner が判断する。

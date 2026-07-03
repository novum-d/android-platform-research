# BC-007: Large screen orientation / resizability / aspect ratio restrictions ignored

## 基本情報（Basic Information）

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/17/behavior-changes-17
- Section: Platform API changes to ignore orientation, resizability and aspect ratio constraints on large screens

Original statement:
> targetSdkVersion 37 以上では large screen 上で orientation / resizability / aspect ratio restrictions が ignored になる、という趣旨の公式説明。

調査対象 Android バージョン:
- From: android-16.0.0_r4
- To: android-17.0.0_r1

## 対象アプリとの関係（Relevance to Target App）

関連するアプリ機能:
- ライブビュー / リモート操作画面。
- 画像 / 動画一覧。
- 接続設定。
- 固定縦向きまたは固定横向き UI。

関連する API / permission / component:
- `screenOrientation`
- `resizeableActivity`
- `minAspectRatio` / `maxAspectRatio`
- `setRequestedOrientation()`
- Android 16 opt-out property

アプリが該当する可能性:
- Conditional。固定向き・固定比率・non-resizable に依存する UI がある場合に該当。

## 適用条件分類（Applicability Classification）

主分類（Primary classification）:
- TARGET_SDK_37_CONDITIONAL

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | No / Conditional | Android 17 target で opt-out が無効化される。 |
| targetSdkVersion 37 以上が必要か | Yes | `DISABLE_OPT_OUT_UNIVERSAL_RESIZABLE_BY_DEFAULT`。 |
| 追加の実行時条件があるか | Yes | `sw >= 600dp`、game 以外、orientation / resizability / aspect ratio restriction。 |
| Compat Change ID が関係するか | Yes | `357141415L`, `447301631L`。 |

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17。
- targetSdkVersion: 37 以上。
- Device/form factor: `sw >= 600dp`。
- Manifest/property condition: orientation / resizability / aspect ratio restriction、Android 16 opt-out 依存。

Compat framework:
- Change ID: `357141415L`, `447301631L`
- Change name: `UNIVERSAL_RESIZABLE_BY_DEFAULT`, `DISABLE_OPT_OUT_UNIVERSAL_RESIZABLE_BY_DEFAULT`
- Default state: Android 16 target で制約無視 enabled、Android 17 target で opt-out disabled。
- Toggleable for testing: compat change として確認候補。

## AOSP 調査（AOSP Investigation）

関連ファイル:
- `core/java/android/content/pm/ActivityInfo.java`
- `services/core/java/com/android/server/wm/AppCompatResizeOverrides.java`
- `services/core/java/com/android/server/wm/DisplayContent.java`
- `services/core/java/com/android/server/wm/ActivityRecord.java`

確認したソース文脈（Source Context Reviewed）:

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `ActivityInfo` / `UNIVERSAL_RESIZABLE_BY_DEFAULT` | Android 16 target 以上で large screen 制約無視 | Android 17 でも継続 | large screen resize policy の基本 gate。 |
| `AppCompatResizeOverrides` / `DISABLE_OPT_OUT_UNIVERSAL_RESIZABLE_BY_DEFAULT` | Android 16 opt-out property が効く | Android 17 target で opt-out disabled | targetSdkVersion 37 で既存 opt-out に依存できない根拠。 |

差分解釈（Diff Interpretation）:
- Changed condition / gate: Android 17 target で opt-out disabled。
- Changed default: large screen で app resize / orientation constraints の扱いが変わる。

適用ゲート根拠（Applicability Gate Evidence）:
- targetSdkVersion gate: targetSdkVersion 37 以上。
- Device condition: `smallestScreenWidthDp >= 600dp`。
- Gate conclusion: Android 17 / targetSdkVersion 37 / large screen / fixed constraints に適用。

## 事実・観察・仮説・結論（Facts / Observations / Hypotheses / Conclusion）

事実（Facts）:
- Android 17 target では large screen 制約無視への opt-out が無効になる。

観察（Observations）:
- カメラ連携アプリのライブビューやリモート操作 UI は固定比率・固定向きを前提にしている可能性がある。

仮説（Hypotheses）:
- tablet / foldable / desktop windowing で UI 崩れ、操作ボタン位置ずれ、ライブビュー aspect ratio 問題が出る可能性。

結論（Conclusion）:
- targetSdkVersion 37 更新前に large screen 検証が必要。

## アプリ影響（App Impact）

想定される影響:
- レイアウト崩れ、ライブビューの余白 / crop / stretch、操作 UI の重なり。

ユーザー影響:
- tablet / foldable で撮影操作や画像選択がしづらくなる可能性。

開発者影響:
- adaptive layout、configuration change、multi-window 対応確認が必要。

推奨対応候補:
- `sw >= 600dp` 端末、fold / unfold、multi-window resize、rotation で主要画面を確認する。

## Confidence

Confidence:
- High

Confidence の根拠:
- AOSP Change ID、large screen condition、opt-out disabled path を確認済み。

不足している根拠:
- 対象アプリの manifest / UI 実装。

---

# Virtual device owner overrides - 1ページ要約（One Page Summary）

## 対象（Target）

Android 16 Behavior Change:
- Virtual device owner overrides

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:
- `android16/AGENTS.md` は To tag を `android-16.0.0_r1` としているが、本調査では依頼スコープに従い `android-16.0.0_r4` を使用。

## 適用条件（Applicability）

- 主分類（Primary classification）: `OS_UPDATE_ALL_APPS`
- Android 16 OS update: Conditional Yes。virtual device owner projection 条件を満たす場合に影響し得る。
- targetSdkVersion 36 以上: No。本件の主要 gate ではない。
- local physical display: 原則影響なし。
- 必須条件: trusted / privileged virtual device owner が管理する selected virtual device / trusted virtual display で、orientation / aspect ratio / resizability restrictions を無視する override が有効。
- Compat Change ID: 本件そのものを直接 toggle する Change ID は確認できない。
- Aconfig / API: `vdm_force_app_universal_resizable_api`、`VirtualDisplayConfig.Builder#setIgnoreActivitySizeRestrictions(boolean)`。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 16 / targetSdkVersion 35 / local physical display | 本件の projection override は原則影響なし。 |
| Android 16 / targetSdkVersion 36 / local physical display | targetSdkVersion 35 と同じ。 |
| Android 16 / targetSdkVersion 35 / projected by virtual device owner | override 有効なら orientation / aspect ratio / resizability 制限が無視され得る。 |
| Android 16 / targetSdkVersion 36 / projected by virtual device owner | targetSdkVersion 35 と同じ。本件は targetSdkVersion 36 固有ではない。 |
| Android 16 / trusted or privileged virtual device owner | selected trusted virtual display に override を適用可能。 |
| Android 16 / ordinary app without virtual device owner privilege | 同じ override を任意には使えない。 |
| Android 16 / orientation restriction ignored | fixed orientation 前提が崩れる可能性あり。 |
| Android 16 / aspect ratio restriction ignored | min/max aspect ratio 前提が崩れる可能性あり。 |
| Android 16 / resizability restriction ignored | `resizeableActivity=false` 前提が崩れる可能性あり。 |
| Android 15 / targetSdkVersion 36 | Android 16 公式 behavior change としては扱わず、比較用 baseline。 |

## 要約（Summary）

Android 16 では、virtual device owner がアプリを virtual device 上で実行し remote / external display に投影する場合、select virtual device 上で app settings を override できる。代表例は orientation、aspect ratio、resizability restrictions の無視である。

これは targetSdkVersion 36 化の影響ではなく、Android 16 OS 上で trusted / privileged virtual device owner projection 経路に乗った場合の条件付き影響である。

## 顧客影響（Customer Impact）

- 影響あり / 要確認。
- phone portrait 専用 UI、fixed orientation、aspect ratio 制限、`resizeableActivity=false` に依存するアプリは、large screen / landscape / external display 上で UI が崩れる可能性がある。
- local phone display の通常実行と混同しない。
- PC、VR、car infotainment、Chromebook などへの projection / companion app streaming use case があるアプリは優先的に確認する。

## 影響対象（Who Is Affected）

- companion app streaming / virtual device projection で利用されるアプリ。
- phone portrait 専用 UI のアプリ。
- fixed orientation / fixed aspect ratio / unresizable 前提のアプリ。
- large screen / external display / desktop mode / Chromebook / car display / VR display で利用され得るアプリ。
- camera / media / map / game / productivity / document editing など window size / orientation / input modality に敏感なアプリ。
- WindowMetrics / DisplayMetrics / resources qualifier 前提が強い custom layout を持つアプリ。

## 対応要否（Required Action）

- 必須確認: projection / external display use case の有無を棚卸しする。
- 必須確認: `screenOrientation`、`resizeableActivity`、minAspectRatio / maxAspectRatio、fixed-size layout への依存を確認する。
- 推奨対応: WindowMetrics / adaptive layout / responsive UI へ移行する。
- 推奨対応: large screen、landscape、desktop-class bounds、keyboard / mouse / touch / controller input で QA する。
- 推奨対応: virtual device owner / privileged companion app と連携する場合、どの virtual display で override が有効か仕様確認する。

## テストマトリクス（Test Matrix）

| 端末 OS / 実行条件 | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 15 / local display | 35 | baseline。 |
| Android 16 / local display | 35 | 本件の projection override は原則なし。 |
| Android 16 / local display | 36 | targetSdkVersion 35 と同じ。 |
| Android 16 / virtual device owner projection | 35 | override 有効なら制限が無視され得る。 |
| Android 16 / virtual device owner projection | 36 | targetSdkVersion 35 と同じ。 |

追加テスト:

| 観点 | 確認内容 |
| --- | --- |
| owner condition | trusted / privileged virtual device owner の有無。 |
| display condition | selected virtual display override enabled / disabled。 |
| manifest restrictions | `screenOrientation`、`resizeableActivity=true/false`、min/max aspect ratio。 |
| UI | portrait-only activity を landscape / large display に投影。 |
| metrics | WindowMetrics / Configuration / DisplayInfo / resources qualifier の変化。 |
| workflows | camera preview、media playback、map、game、form、document editing。 |
| regression | clipping、letterboxing、stretching、pillarboxing、touch target、input modality。 |

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/16/behavior-changes-all#virtual-device-owner-overrides
- Official compat framework reference: https://developer.android.com/about/versions/16/reference/compat-framework-changes
- AOSP files:
  - `frameworks-base/core/java/android/hardware/display/VirtualDisplayConfig.java`
  - `frameworks-base/services/core/java/com/android/server/display/DisplayManagerService.java`
  - `frameworks-base/services/core/java/com/android/server/wm/DisplayWindowSettings.java`
  - `frameworks-base/services/core/java/com/android/server/wm/DisplayContent.java`
  - `frameworks-base/services/core/java/com/android/server/wm/AppCompatOrientationPolicy.java`
  - `frameworks-base/services/core/java/com/android/server/wm/AppCompatAspectRatioOverrides.java`
  - `frameworks-base/services/core/java/com/android/server/wm/AppCompatUtils.java`
  - `frameworks-base/core/java/android/companion/virtual/VirtualDeviceManager.java`
  - `frameworks-base/services/companion/java/com/android/server/companion/virtual/VirtualDeviceImpl.java`
  - `frameworks-base/core/res/AndroidManifest.xml`
- AOSP source context:
  - virtual display config が activity size restrictions ignore を表す。
  - DisplayManagerService が trusted display の場合だけ WindowManager に設定を伝える。
  - WindowManager が display setting として保持し、orientation / aspect ratio / resizability policy で参照する。
  - virtual device owner API は owner UID / internal-role permission / trusted display permission で制限される。

## Human decision placeholder

最終優先度（Final Priority）:
- Critical / High / Medium / Low

判断（Decision）:
- Explain / Monitor / Ignore / Further investigation required

補足:
- 最終優先度、顧客通知要否、release readiness は repository owner が判断する。

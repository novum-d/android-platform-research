# Common breaking changes 調査レポート

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:

Previous targetSdkVersion:
- 35

Target targetSdkVersion:
- 36

### Behavior Change 文書（Behavior Change Source）

Document:
- https://developer.android.com/about/versions/16/behavior-changes-all#common-breaking

Page:
- Behavior changes: all apps

Category:
- Device form factors

Parent section:
- Virtual device owner overrides

Section:
- Common breaking changes

Related sections:
- https://developer.android.com/about/versions/16/behavior-changes-all#virtual-device-owner-overrides
- https://developer.android.com/about/versions/16/behavior-changes-all#per-app_overrides

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `OS_UPDATE_ALL_APPS`

追加条件（Additional conditions）:
- Android 16 上で app が virtual device owner 管理下の virtual device / virtual display に投影されること。
- trusted / privileged virtual device owner が selected virtual device / trusted virtual display に対して activity size restrictions ignore を有効にすること。
- projection 先が car display、Chromebook、PC display、VR display などの large screen / external display であること。
- app UI が small portrait phone display、fixed orientation、fixed aspect ratio、`resizeableActivity=false`、letterbox / pillarbox 前提などに依存している場合に UI impact が出やすい。

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 16 に OS アップデートしただけで適用されるか | Conditional Yes | 公式 all apps ページの項目。AOSP gate は targetSdkVersion ではなく virtual display / trusted display / virtual device owner / aconfig flag / display settings。 |
| targetSdkVersion 36 以上が必要か | No | `VirtualDisplayConfig`、`DisplayManagerService`、WindowManager app-compat 経路に targetSdkVersion 36 gate は見つからない。 |
| local physical phone display の通常実行に影響するか | No | `DisplayWindowSettings` は display uniqueId と `Display.TYPE_VIRTUAL` に override を保存する。 |
| large screen projection では影響し得るか | Yes | 公式文書は car displays / Chromebooks など large screen UI impact を明記。AOSP は orientation / aspect ratio / resizability restriction ignore path を持つ。 |
| ordinary app が任意に同じ override を使えるか | No | `CREATE_VIRTUAL_DEVICE` は `internal|role`、`ADD_TRUSTED_DISPLAY` は `signature|role`。該当 API は `@SystemApi` / `@FlaggedApi`。 |
| Compat Change ID が直接関係するか | No direct Change ID | 関連する orientation / aspect ratio / large screen compat changes はあるが、本件の virtual device owner projection path とは別。 |

### 調査日（Investigation Date）

2026-07-06

### 信頼度（Confidence）

- Medium-High

理由:
- 公式文書が Android 16 all apps ページで `Common breaking changes` を明記している。
- AOSP `android-16.0.0_r4` で `VirtualDisplayConfig.Builder#setIgnoreActivitySizeRestrictions(boolean)`、trusted virtual display gate、WindowManager display setting、orientation / aspect ratio / resizability override path、virtual device owner 権限制御を確認した。
- `DisplayContent` / `TaskFragment` / `ConfigurationContainer` / `WindowMetrics` で、app が受け取る configuration / bounds / density が display / task bounds から計算されることを確認した。
- targetSdkVersion 36 gate が該当 code path にないことを確認した。
- ただし関連 API / aconfig flag は `android-15.0.0_r36` にも存在するため、From/To tag 差分だけで「Android 16 で完全新規追加」とは言えない。Android 16 公式 behavior change としての developer-facing impact は確認できるが、Android 15 build での feature enablement は別途 product config / 実機確認が必要。

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [x] OS update / all apps on Android 16 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 36 on Android 16+
- [ ] targetSdkVersion >= 36, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [ ] Unknown / needs more evidence

必要な実行時条件（Required runtime conditions）:
- Android version: Android 16。
- targetSdkVersion: 条件なし。35 と 36 で同じ projection 条件が適用される見込み。
- Device/form factor: trusted / privileged virtual device owner が作成・管理する selected virtual device / trusted virtual display。projection 先は car display、Chromebook、PC、VR、その他 external / large display が該当し得る。
- Permission/API/component condition: `CREATE_VIRTUAL_DEVICE` を持つ virtual device owner、trusted display のための `ADD_TRUSTED_DISPLAY`、`VirtualDisplayConfig.Builder#setIgnoreActivitySizeRestrictions(true)` 相当。
- App UI condition: small portrait phone display 前提、fixed orientation、aspect ratio restriction、resizability restriction、DisplayMetrics / WindowMetrics の固定前提があること。

Compat framework:
- Change ID: 本件の Common breaking changes / virtual device owner large-screen projection impact 自体を直接 toggle する Change ID は確認できない。
- Related changes:
  - `UNIVERSAL_RESIZABLE_BY_DEFAULT` / Change ID 357141415: targetSdkVersion 36+ large screen behavior。Virtual device owner projection path とは別項目。
  - `OVERRIDE_ANY_ORIENTATION_TO_USER`、`OVERRIDE_MIN_ASPECT_RATIO`、`FORCE_RESIZE_APP` など: app-compat testing / package override 用。本件の selected virtual display owner path と混同しない。
- Default state: N/A for direct compat change。
- Toggleable for testing: direct compat change は確認できない。virtual display config / trusted display / product feature flag / privileged owner implementation に依存する。

Aconfig:
- `com.android.window.flags.vdm_force_app_universal_resizable_api`
- description: "Whether the API for forcing apps to be universal resizable on virtual display is available"

---

# エグゼクティブサマリー（Executive Summary）

Android 16 の `Common breaking changes` は、virtual device owner projection により、phone portrait 前提の UI が large screen / external display 上で崩れる可能性を示す項目である。親項目の `Per-app overrides` により、trusted / privileged virtual device owner は selected virtual devices 上で orientation、aspect ratio、resizability restrictions を無視できる。

この変更は targetSdkVersion 36 化の影響ではなく、Android 16 上で virtual device owner projection 経路に乗った場合の条件付き影響である。local physical phone display で通常実行される場合には、本件の override は原則適用されない。

顧客向けには、以下を混ぜずに説明する必要がある。

| 観点 | 説明 |
| --- | --- |
| Android 16 OS update | projection 条件を満たす場合、targetSdkVersion を変えなくても影響し得る。 |
| targetSdkVersion 36 化 | 本件の必要条件ではない。targetSdkVersion 35 / 36 のどちらも projection 条件で影響し得る。 |
| virtual device owner projection | trusted / privileged owner が selected virtual display に override を適用する場合だけ問題になる。 |
| local physical display | 通常の phone display 実行では本件の selected virtual display override は適用されない。 |
| large screen UI impact | car display / Chromebook / PC / VR などで small portrait layout assumptions が露出する。 |

---

# 公式ドキュメント確認（Original Documentation）

## 原文要旨（Statements）

公式文書は `Common breaking changes` として以下を述べている。

- Android 16 behavior は car displays や Chromebooks など large screen form factors 上の UI に影響し得る。
- 特に small portrait display 向けに設計された layout が影響を受けやすい。
- すべての device form factors に適応するには adaptive layouts のガイドを参照する。

親項目 / 前段の `Per-app overrides` は以下を述べている。

- Android 16 / API level 36 では、virtual device owner が自分で管理する select virtual devices 上で app settings を override できる。
- app layout を改善する例として、external display へ app を投影するときに orientation、aspect ratio、resizability restrictions を無視できる。

## 公式本文との差分確認

調査開始時点で公式 URL の該当セクションを再確認した。依頼に含まれる Original statements と公式本文の主旨は一致している。

公式ページは `Behavior changes: all apps` であり、冒頭で Android 16 上で実行されるすべてのアプリに適用され得る変更で、targetSdkVersion に依存しない旨を示している。ただし、本件は全アプリに無条件適用されるのではなく、virtual device owner projection / selected virtual display / large screen という実行時条件を持つ。

## 解釈（Interpretation）

`Common breaking changes` は、個別 API の呼び出しそのものではなく、projection 環境で UI assumption が破綻する代表的な breakage を説明する subsection である。実装上の直接根拠は親項目の per-display override path にあり、common breakage はその結果として app が受け取る bounds / configuration / WindowMetrics が phone portrait 前提から外れる点にある。

---

# 変更内容（What Changed）

## 変更点

- virtual device owner は selected virtual device / trusted virtual display 上で app settings を override できる。
- `VirtualDisplayConfig.Builder#setIgnoreActivitySizeRestrictions(true)` 相当の設定により、fixed orientation、aspect ratio、resizability restrictions を無視できる。
- `DisplayManagerService` は trusted display 条件を満たす場合のみ WindowManager に display-level override を設定する。
- WindowManager app-compat policy は、その display 上の activity orientation request / aspect ratio / resizability restriction を通常の phone display と同じ前提で扱わない。
- app が受け取る `Configuration` / `WindowMetrics` / display metrics は projected display / task bounds に基づくため、small portrait phone UI 前提が large screen / landscape / desktop-class window で露出する。

## 変更されない点

- targetSdkVersion 36 に上げただけで、この virtual device owner projection path が有効になるわけではない。
- local physical phone display の通常実行で、すべての activity restrictions が無条件に無視されるわけではない。
- ordinary app が任意に trusted virtual display / virtual device owner として同じ override を使えるわけではない。
- Android 16 の targetSdkVersion 36 large screen compat change `UNIVERSAL_RESIZABLE_BY_DEFAULT` とは別項目である。

---

# AOSP 調査（AOSP Investigation）

## AOSP checkout hygiene

- `frameworks-base` working tree: clean。
- `android-15.0.0_r36` tag: present。
- `android-16.0.0_r4` tag: present。
- Evidence は local working tree の未コミット差分ではなく、tag comparison と `android-16.0.0_r4` source を基準に確認した。

## 関連ファイル（Related Files）

- `frameworks-base/core/java/android/hardware/display/VirtualDisplayConfig.java`
- `frameworks-base/services/core/java/com/android/server/display/DisplayManagerService.java`
- `frameworks-base/services/core/java/com/android/server/wm/DisplayWindowSettings.java`
- `frameworks-base/services/core/java/com/android/server/wm/DisplayContent.java`
- `frameworks-base/services/core/java/com/android/server/wm/AppCompatOrientationPolicy.java`
- `frameworks-base/services/core/java/com/android/server/wm/AppCompatAspectRatioOverrides.java`
- `frameworks-base/services/core/java/com/android/server/wm/AppCompatUtils.java`
- `frameworks-base/core/java/android/companion/virtual/VirtualDeviceManager.java`
- `frameworks-base/services/companion/java/com/android/server/companion/virtual/VirtualDeviceImpl.java`
- `frameworks-base/services/companion/java/com/android/server/companion/virtual/VirtualDeviceManagerService.java`
- `frameworks-base/core/res/AndroidManifest.xml`
- `frameworks-base/core/java/android/view/WindowMetrics.java`
- `frameworks-base/core/java/android/app/WindowConfiguration.java`
- `frameworks-base/services/core/java/com/android/server/wm/ConfigurationContainer.java`
- `frameworks-base/services/core/java/com/android/server/wm/TaskFragment.java`
- `frameworks-base/services/tests/wmtests/src/com/android/server/wm/AppCompatAspectRatioOverridesTest.java`
- `frameworks-base/services/tests/wmtests/src/com/android/server/wm/SizeCompatTests.java`

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル（File / symbol） | Android 15 の基準挙動（baseline） | Android 16 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `VirtualDisplayConfig#isIgnoreActivitySizeRestrictions()` / Builder method | `android-15.0.0_r36` にも flagged SystemApi として存在 | `android-16.0.0_r4` でも fixed orientation / aspect ratio / resizability ignore を表す SystemApi | 親項目 per-app override の入口。Common breaking changes の前提になる。 |
| `DisplayManagerService#createVirtualDisplayInternal` | trusted virtual display permission path は存在 | trusted flag がない場合は request を無視し、trusted の場合だけ WindowManager に設定 | selected virtual device / trusted display gate の実装根拠。 |
| `DisplayWindowSettings#setIgnoreActivitySizeRestrictionsOnDisplayLocked` | display override setting として存在 | display uniqueId / `Display.TYPE_VIRTUAL` に setting を保存 | local display ではなく selected virtual display 単位の override である根拠。 |
| `DisplayContent#isDisplayIgnoreActivitySizeRestrictions()` | display setting を参照 | app-compat policy が参照する display property | orientation / aspect ratio / resizability ignore が display property に基づく根拠。 |
| `AppCompatOrientationPolicy#overrideOrientationIfNeeded` | eligible display で orientation request を `SCREEN_ORIENTATION_USER` に変換 | Android 16 target でも同経路 | portrait-only / fixed orientation layout が large display 上で維持されない根拠。 |
| `AppCompatAspectRatioOverrides#hasFullscreenOverride` | display ignore condition を fullscreen override 条件に含む | Android 16 target でも同経路 | min/max aspect ratio や letterbox / pillarbox 前提が崩れ得る根拠。 |
| `AppCompatUtils#isDisplayIgnoreActivitySizeRestrictions` | aconfig flag + display setting gate | targetSdkVersion 36 ではなく flag / display 条件 | targetSdkVersion gate がない根拠。 |
| `VirtualDeviceManager#createVirtualDevice` | `CREATE_VIRTUAL_DEVICE` permission required | Android 16 でも system / role 前提 | ordinary app が任意に virtual device owner になれない根拠。 |
| `VirtualDeviceImpl#createVirtualDisplay` | owner UID check と owned display tracking | Android 16 でも caller owner / display ownership を検査 | virtual device owner が管理する display に限定される根拠。 |
| `AndroidManifest.xml` permissions | `CREATE_VIRTUAL_DEVICE` / `ADD_TRUSTED_DISPLAY` は public runtime permission ではない | `CREATE_VIRTUAL_DEVICE` は `internal|role`、`ADD_TRUSTED_DISPLAY` は `signature|role` | trusted / privileged owner 条件の根拠。 |
| `DisplayContent#computeScreenConfiguration` | display logical width / height / density から configuration を計算 | Android 16 でも display bounds / density を `screenWidthDp` / `screenHeightDp` / orientation に反映 | projected large display 上で app configuration が phone portrait 前提から外れる根拠。 |
| `ConfigurationContainer#applySizeOverrideIfNeeded` | app bounds 由来で `screenWidthDp` / `screenHeightDp` / `smallestScreenWidthDp` / orientation を補正 | Android 16 でも app bounds / density から configuration を計算 | Window / bounds 変更が resources qualifier / orientation に影響する根拠。 |
| `TaskFragment#computeConfigResourceOverrides` | task / parent bounds / display info から screen config を計算 | Android 16 でも stable bounds / density から widthDp / heightDp / orientation を計算 | projection / windowing により app が受ける configuration が変わる根拠。 |
| `WindowMetrics#getBounds()` / `getDensity()` | window bounds と density を公開 | Android 16 でも app が current / maximum window metrics で bounds / density を取得 | custom layout measurement / WindowMetrics assumption への影響を説明する根拠。 |

## 主要証跡（Key Evidence）

### Virtual display config

`VirtualDisplayConfig#isIgnoreActivitySizeRestrictions()` は、virtual display が app の fixed orientation、aspect ratio、resizability を無視するかを返す。Builder method は `@SystemApi` / `@FlaggedApi` で、true にするには `DisplayManager#VIRTUAL_DISPLAY_FLAG_TRUSTED` が必要であり、trusted でない display では property が無視される。

Diff interpretation:
- API / flag は Android 15 tag にも存在するため、単純な API surface 新規追加ではない。
- Android 16 公式文書では、この path が virtual device owner projection 時の behavior change として developer-facing に明示された。

### DisplayManagerService enforcement

`DisplayManagerService` は `virtualDisplayConfig.isIgnoreActivitySizeRestrictions()` が true でも、virtual display が trusted でなければ request を無視する。trusted display の場合だけ `WindowManagerInternal#setIgnoreActivitySizeRestrictionsOnDisplay(displayUniqueId, Display.TYPE_VIRTUAL, true)` を呼ぶ。

Diff interpretation:
- Common breaking changes は、すべての display ではなく selected trusted virtual display に限定される。
- ordinary app の通常 virtual display use case では同じ結果になるとは限らない。

### WindowManager app-compat policy

`AppCompatOrientationPolicy` は eligible virtual display で orientation request を無視する。`AppCompatAspectRatioOverrides` は display ignore condition を fullscreen override 条件に含める。`AppCompatUtils` は aconfig flag と display setting を gate とし、targetSdkVersion 36 を条件にしていない。

Diff interpretation:
- fixed portrait / aspect ratio / `resizeableActivity=false` により phone UI を守る前提は、projection 環境では成立しない可能性がある。

### Configuration / WindowMetrics

`DisplayContent#computeScreenConfiguration` は display logical width / height / density から `screenWidthDp`、`screenHeightDp`、orientation、densityDpi を計算する。`TaskFragment#computeConfigResourceOverrides` は task / parent bounds / stable bounds / density から app-facing configuration を計算する。`WindowMetrics` は window bounds と density を app-facing API として持つ。

Diff interpretation:
- projection 先が car display / Chromebook / PC / VR のような large display である場合、app は phone portrait display とは異なる widthDp / heightDp / orientation / WindowMetrics を受け取り得る。
- custom `DisplayMetrics` / `WindowMetrics` / resources qualifier assumptions を持つ app は、layout clipping、stretching、unexpected landscape layout、touch target regression、input modality mismatch などを起こし得る。

### Virtual device owner privilege

`VirtualDeviceManager#createVirtualDevice` は `CREATE_VIRTUAL_DEVICE` permission を要求し、doc は system apps holding specific roles に限定されると説明する。`AndroidManifest.xml` では `CREATE_VIRTUAL_DEVICE` が `internal|role`、`ADD_TRUSTED_DISPLAY` が `signature|role` で定義される。`VirtualDeviceImpl` は caller が owner UID であることや display が virtual device に属することを確認する。

Diff interpretation:
- Common breaking changes は、一般アプリが自分で勝手に他アプリの restrictions を無視する話ではない。
- trusted / privileged virtual device owner または product/OEM projection implementation が関係する。

---

# Facts / Observations / Hypotheses / Conclusions

## Facts

- 公式文書は `Behavior changes: all apps` に本項目を掲載し、Android 16 上で実行される app に targetSdkVersion に関係なく影響し得ると説明している。
- 公式文書は、virtual device owner が projected apps の app settings を select virtual devices 上で override できると説明している。
- 公式文書は、orientation、aspect ratio、resizability restrictions を無視できる例を示している。
- 公式文書は、car displays / Chromebooks など large screen form factors 上で、small portrait display 向け layout が影響を受け得ると説明している。
- AOSP `VirtualDisplayConfig` は fixed orientation、aspect ratio、resizability を無視する virtual display property を持つ。
- AOSP `DisplayManagerService` は trusted virtual display でない場合、この property request を無視する。
- AOSP WindowManager app-compat policy は display-level ignore state を参照して orientation / aspect ratio / fullscreen behavior を変える。
- AOSP permission 定義では virtual device / trusted display 作成は ordinary app 向け runtime permission ではない。

## Observations

- 本件の primary gate は targetSdkVersion 36 ではなく、Android 16 / virtual device owner / trusted virtual display / selected virtual device / large-screen projection 条件である。
- Android 15 tag にも関連 API / aconfig flag が存在するため、source diff だけでは「Android 16 でゼロから追加」とは言えない。
- Common breaking changes は、API behavior の低レベル仕様というより、projection と app-compat override の結果として UI assumptions が壊れる可能性を開発者へ知らせる subsection である。
- car display / Chromebook / PC / VR display の具体的な product behavior は、framework evidence と OEM / product implementation evidence を分けて扱う必要がある。

## Hypotheses

- Android 16 product build では、virtual device owner / companion app streaming use cases でこの override path が有効化され、Android 15 product build より開発者が遭遇しやすくなった可能性がある。
- phone portrait-only UI、fixed aspect ratio、letterbox / pillarbox 前提の app は、projection 先 display が landscape / large widthDp の場合に breakage が顕在化しやすい。
- keyboard / mouse / controller input は virtual device owner projection で同時に使われる可能性があり、layout breakage だけでなく focus navigation / hover / right click / text input assumptions も QA 対象になる。

## Conclusions

- Primary classification は `OS_UPDATE_ALL_APPS` が最も近い。理由は公式 all apps ページ掲載であり、AOSP evidence 上 targetSdkVersion 36 gate が見つからないためである。
- ただし、影響は「Android 16 端末上の全アプリに常時発生」ではない。virtual device owner projection、trusted virtual display、selected virtual device override、large screen / external display という条件付きである。
- 顧客向けには、targetSdkVersion 36 化のリスクではなく、Android 16 OS update 後に projection 環境で phone portrait UI assumptions が露出するリスクとして説明すべきである。
- 対応方針は、orientation / aspect ratio / resizability restrictions による回避ではなく、adaptive layout、large screen resource / WindowMetrics QA、external input modality QA を中心に置くべきである。

---

# 期待挙動マトリクス（Expected Behavior Matrix）

## OS / targetSdkVersion matrix

| OS / targetSdkVersion | 条件 | 期待挙動 |
| --- | --- | --- |
| Android 16 / targetSdkVersion 35 | local physical display | 本件の virtual device owner override は原則適用されない。 |
| Android 16 / targetSdkVersion 36 | local physical display | 本件の virtual device owner override は原則適用されない。targetSdkVersion 36 large screen compat change は別途確認。 |
| Android 16 / targetSdkVersion 35 | projected by virtual device owner | selected trusted virtual display で override が有効なら UI impact が出得る。 |
| Android 16 / targetSdkVersion 36 | projected by virtual device owner | targetSdkVersion 35 と同様に、projection / override 条件で UI impact が出得る。 |
| Android 15 / targetSdkVersion 36 | same app behavior if technically comparable | 関連 API / flag は tag 上存在するが、公式 Android 16 behavior change とは分ける。product enablement / 実機確認が必要。 |

## Scenario matrix

| Scenario | 期待挙動 / impact |
| --- | --- |
| Android 16 / app projected to car infotainment display | large landscape / vehicle-specific display bounds で phone portrait UI が崩れる可能性がある。 |
| Android 16 / app projected to Chromebook / large display | wide / resizable / desktop-class bounds で layout clipping、空白、stretching、touch target regression が出得る。 |
| Android 16 / app projected to PC display | keyboard / mouse 前提の focus / hover / resizing QA が必要。 |
| Android 16 / app projected to VR device display | unusual aspect ratio / input modality / density assumptions の検証が必要。 |
| Android 16 / phone portrait-only layout on large landscape display | orientation lock が無視されると landscape / wide bounds に晒され、breakage が出やすい。 |
| Android 16 / adaptive layout on large display | lower risk。window size class / responsive layout が正しく動作するかを確認する。 |
| Android 16 / trusted or privileged virtual device owner | `CREATE_VIRTUAL_DEVICE` / `ADD_TRUSTED_DISPLAY` / trusted display 条件を満たす場合、override path を使える。 |
| Android 16 / ordinary app without virtual device owner privilege | 同じ override を任意には使えない。 |
| Android 16 / selected virtual device with overrides enabled | orientation / aspect ratio / resizability restrictions が無視され得る。 |
| Android 16 / virtual device without overrides | app-declared restrictions が通常どおり尊重される可能性が高い。 |
| Android 16 / orientation restriction ignored | `screenOrientation` による portrait-only 前提が成立しない可能性がある。 |
| Android 16 / aspect ratio restriction ignored | min/max aspect ratio や letterbox 前提が崩れる可能性がある。 |
| Android 16 / resizability restriction ignored | `resizeableActivity=false` 前提の固定 UI が resizable / large bounds に晒される可能性がある。 |
| Android 16 / `resizeableActivity=false` | selected virtual display override では保護にならない可能性がある。 |
| Android 16 / fixed minAspectRatio / maxAspectRatio | selected virtual display override では保護にならない可能性がある。 |
| Android 16 / custom DisplayMetrics assumptions | display / window / density の固定前提が破綻し、誤った px / dp 計算になる可能性がある。 |
| Android 16 / WindowMetrics / Configuration changes under projection | projected display / task bounds に基づく widthDp / heightDp / orientation / density で UI が再評価される。 |
| Android 16 / keyboard / mouse / controller input under projection | focus order、hover、keyboard shortcuts、controller navigation、text input を確認する。 |
| Android 16 / layout clipping | fixed-size view / absolute positioning / unbounded text で発生しやすい。 |
| Android 16 / layout stretching | phone-only image / preview / canvas / camera layout で発生しやすい。 |
| Android 16 / letterboxing / pillarboxing expectation broken | app compatibility restrictions による保護を期待している場合、selected virtual display override で崩れ得る。 |
| app migrates to adaptive layouts | recommended。orientation / aspect / resizability restrictions 前提を減らす。 |
| app continues relying on small portrait layout assumptions | high risk in projected large-screen environments。 |

---

# 影響対象アプリ（Potentially Affected Apps）

- companion app streaming / virtual device projection で利用されるアプリ。
- phone portrait 専用 UI のアプリ。
- small display 前提の resource / layout を持つアプリ。
- fixed orientation を前提にするアプリ。
- aspect ratio 制限を前提にするアプリ。
- `resizeableActivity=false` や resizability 制限を持つアプリ。
- car display / Chromebook / PC / VR display で利用され得るアプリ。
- camera / media / map / game / productivity / form / document editing など、window size / orientation / input modality に敏感なアプリ。
- custom layout measurement / `DisplayMetrics` / `WindowMetrics` assumptions を持つアプリ。
- multi-window / freeform / large screen adaptive 対応が不十分なアプリ。
- adaptive layout / responsive UI へ移行すべきアプリ。
- virtual device owner / privileged companion app と連携するアプリ。

---

# テスト観点（Test Points）

- Android 15 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 36。
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較。
- local physical display 実行。
- virtual device owner による projection 実行。
- trusted / privileged virtual device owner の有無。
- selected virtual device override enabled / disabled。
- car display / Chromebook / PC / VR display projection。
- large landscape display。
- portrait-only activity projected to landscape display。
- adaptive layout comparison。
- `screenOrientation` manifest combinations。
- `resizeableActivity=true/false`。
- minAspectRatio / maxAspectRatio combinations。
- WindowMetrics / Configuration / DisplayInfo / resources qualifier changes。
- keyboard / mouse / touch / controller input under projection。
- camera preview / media playback / map / game / form / document workflows。
- screenshot / screen recording comparison。
- layout clipping / letterboxing / stretching / pillarboxing / touch target regression。
- text scaling / density / font scale under external display。
- graceful adaptive layout fallback。
- logs / dumpsys activity / dumpsys window / WM tracing / perfetto trace。
- automated UI tests and manual large-screen QA。

---

# 推奨対応候補（Recommended Action Candidates）

- `screenOrientation`、`resizeableActivity=false`、min/max aspect ratio を UI correctness の主な防御策として扱わない。
- Window size class、`WindowMetrics`、resource qualifiers、responsive/adaptive layout で large screen / external display に対応する。
- camera preview / media / map / game canvas は aspect ratio と letterbox / crop / fit strategy を明示的に設計する。
- keyboard / mouse / controller / touch の複数 input modality を QA に含める。
- virtual device owner projection を直接再現できない場合でも、large landscape display、freeform / multi-window、external display 相当の bounds で UI regression を先に検出する。
- customer communication では「Android 16 OS update だけ」「targetSdkVersion 36 化」「virtual device owner projection 時だけ」「local display 非影響」を分けて説明する。

---

# Evidence gaps / 注意点

- `android-15.0.0_r36` にも関連 API / aconfig flag が存在するため、AOSP From/To diff だけで feature の導入時点を断定しない。
- Android 16 公式文書は developer-facing behavior change として記載しているが、Android 15 product build で feature が有効だったかは build config / device behavior の確認が必要。
- car display / Chromebook / PC / VR の具体的な projection behavior は framework の一般実装と OEM / product implementation を分ける必要がある。
- `source.android.com` の companion app streaming reference は公式ページから参照されているが、調査時点では参照先の詳細確認が必要な場合がある。report の結論は主に Android Developers 公式文書と AOSP framework evidence に基づく。

---

# Human Decision Placeholder

以下は repository owner / human reviewer が決める項目であり、本調査では確定しない。

- Final priority:
- Final severity:
- Customer communication priority:
- Release readiness:
- Required app-side migration:
- Required QA scope:

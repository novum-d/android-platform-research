# Per-app overrides 調査レポート

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:
- `android16/AGENTS.md` は To tag を `android-16.0.0_r1` としているが、本調査では依頼スコープに従い公開済み Android 16 tag として `android-16.0.0_r4` を使用した。

Previous targetSdkVersion:
- 35

Target targetSdkVersion:
- 36

### Behavior Change 文書（Behavior Change Source）

Document:
- https://developer.android.com/about/versions/16/behavior-changes-all#per-app_overrides

Page:
- Behavior changes: all apps

Category:
- Device form factors

Parent section:
- Virtual device owner overrides

Section:
- Per-app overrides

Related section:
- https://developer.android.com/about/versions/16/behavior-changes-all#virtual-device-owner-overrides

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `OS_UPDATE_ALL_APPS`

追加条件（Additional conditions）:
- Android 16 上で app が virtual device owner 管理下の virtual device / virtual display に投影されること。
- virtual device owner が select virtual device / trusted virtual display に対して activity size restrictions ignore を有効にすること。
- app が fixed orientation、aspect ratio、resizability restrictions に依存している場合に UI impact が出やすい。

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 16 に OS アップデートしただけで適用されるか | Conditional Yes | 公式 all apps ページの項目。AOSP gate は targetSdkVersion ではなく virtual display / trusted display / aconfig flag / owner 権限。 |
| targetSdkVersion 36 以上が必要か | No | `VirtualDisplayConfig`、`DisplayManagerService`、WindowManager app-compat 経路に targetSdkVersion 36 gate は見つからない。 |
| local physical display の通常実行に影響するか | No | `DisplayWindowSettings` は display uniqueId と `Display.TYPE_VIRTUAL` に override を保存する。 |
| ordinary app が任意に override できるか | No | `CREATE_VIRTUAL_DEVICE` は `internal|role`、`ADD_TRUSTED_DISPLAY` は `signature|role`。該当 API は `@SystemApi` / `@FlaggedApi`。 |
| Compat Change ID が直接関係するか | No direct Change ID | 関連する orientation / aspect ratio / resizability compat changes はあるが、本件の virtual device owner per-display override 自体の direct toggle は確認できない。 |

### 調査日（Investigation Date）

2026-07-06

### 信頼度（Confidence）

- Medium-High

理由:
- 公式文書が Android 16 all apps ページで Per-app overrides を明記している。
- AOSP `android-16.0.0_r4` で `VirtualDisplayConfig.Builder#setIgnoreActivitySizeRestrictions(boolean)`、trusted virtual display gate、WindowManager display setting、orientation / aspect ratio / resizability override 経路、virtual device owner 権限制御を確認した。
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
- Device/form factor: virtual device owner が作成・管理する selected virtual device / trusted virtual display。remote / external display、large screen、PC、VR、car infotainment、Chromebook などが該当し得る。
- Permission/API/component condition: `CREATE_VIRTUAL_DEVICE` を持つ virtual device owner、trusted display のための `ADD_TRUSTED_DISPLAY`、`VirtualDisplayConfig.Builder#setIgnoreActivitySizeRestrictions(true)` 相当。
- App state/process condition: app が local physical display ではなく virtual display 上に起動・投影されていること。

Compat framework:
- Change ID: 本件の per-app / per-display override 自体を直接 toggle する Change ID は確認できない。
- Related changes:
  - `UNIVERSAL_RESIZABLE_BY_DEFAULT` / Change ID 357141415: targetSdkVersion 36+ large screen behavior。Per-app overrides とは別項目。
  - `OVERRIDE_ANY_ORIENTATION_TO_USER`、`OVERRIDE_MIN_ASPECT_RATIO`、`FORCE_RESIZE_APP` など: app-compat testing / package override 用で、本件の virtual device owner path とは分ける。
- Default state: N/A for direct compat change。
- Toggleable for testing: direct compat change は確認できない。virtual display config / trusted display / product feature flag / privileged owner 実装に依存する。

Aconfig:
- `com.android.window.flags.vdm_force_app_universal_resizable_api`
- description: "Whether the API for forcing apps to be universal resizable on virtual display is available"

---

# エグゼクティブサマリー（Executive Summary）

Android 16 の Per-app overrides では、trusted / privileged virtual device owner が管理する select virtual devices 上で、app settings を override できる。代表例は、external display へ app を投影するときに orientation、aspect ratio、resizability restrictions を無視することである。

これは targetSdkVersion 36 化の影響ではなく、Android 16 上で virtual device owner projection 経路に乗った場合の条件付き影響である。local physical display の通常実行では、本件の per-app / per-display override は原則適用されない。

影響を受けやすいのは、portrait-only、fixed orientation、`resizeableActivity=false`、min/max aspect ratio などに依存するアプリである。対応としては、制限指定を前提にせず、large screen / external display / arbitrary window size に耐える adaptive layout と QA が必要になる。

---

# 公式ドキュメント確認（Original Documentation）

## 原文要旨（Statements）

公式文書は Per-app overrides として以下を述べている。

- Android 16 / API level 36 を実行する device では、virtual device owners が自分で管理する select virtual devices 上で app settings を override できる。
- app layout を改善する例として、virtual device owner は external display へ app を投影するときに orientation、aspect ratio、resizability restrictions を無視できる。

## 公式本文との差分確認

調査開始時点で公式 URL の該当セクションを再確認した。依頼に含まれる Original statements と公式本文の主旨は一致している。

## 解釈（Interpretation）

Per-app overrides は、app 自身が manifest で宣言した orientation / aspect ratio / resizability restrictions を常に守れるという前提を、virtual device owner projection 環境では置けないことを示す項目である。

ただし、この項目は「すべての Android 16 通常起動で manifest restriction が無視される」という意味ではない。AOSP 実装上は virtual display config、trusted display、WindowManager display setting、app-compat policy がつながる条件付き経路である。

---

# 変更内容（What Changed）

## 変更点

- `VirtualDisplayConfig.Builder#setIgnoreActivitySizeRestrictions(boolean)` は、virtual display が app の fixed orientation、aspect ratio、resizability restrictions を無視するかを指定できる。
- `DisplayManagerService` は、この request が true でも display が trusted でなければ無視する。trusted display の場合だけ WindowManager に display-level override を設定する。
- WindowManager は display uniqueId / display type に紐付けて `mIgnoreActivitySizeRestrictions` を保持する。
- AppCompat policy はその display flag を見て、eligible virtual display 上の activity orientation request を `SCREEN_ORIENTATION_USER` 相当に扱い、aspect ratio / fullscreen override 条件にも含める。
- virtual device owner API は owner UID / permission / role で制限され、ordinary app が任意に同じ override を使う前提ではない。

## 適用条件（Applicability）

### OS アップデート時の挙動（OS Update Behavior）

- Android 16 に OS アップデートしただけで適用されるか: Conditional Yes。
- targetSdkVersion に依存しない根拠: AOSP の該当 path は targetSdkVersion 36 gate ではなく、virtual display config、trusted display、owner permission、aconfig flag、display setting を条件にする。
- Android 15 以前での挙動: `android-15.0.0_r36` にも関連 API / flag は存在する。Android 16 公式 behavior change としての公開挙動とは分け、Android 15 device / product build では feature enablement と実機挙動を別途確認する。

### targetSdkVersion 36 以上での挙動（targetSdkVersion 36 Behavior）

- targetSdkVersion 36 以上で適用されるか: No。targetSdkVersion 36 は本件の必要条件ではない。
- Android 16 以外で targetSdkVersion 36 にした場合の挙動: Android 15 上で targetSdkVersion 36 にしても、本件の Android 16 all apps behavior change としては扱わない。
- opt-out / temporary override の有無: `PROPERTY_COMPAT_ALLOW_ORIENTATION_OVERRIDE` など関連 app-compat property が一部 policy に影響するが、virtual device owner override の一般的・完全な app-side opt-out としては扱わない。

### その他の条件（Other Conditions）

- Device/form factor: selected virtual device / trusted virtual display / external display / large screen。
- Permission: `CREATE_VIRTUAL_DEVICE`、trusted display では `ADD_TRUSTED_DISPLAY`。
- API usage: `VirtualDisplayConfig.Builder#setIgnoreActivitySizeRestrictions(true)`。
- Manifest attribute: `screenOrientation`、`resizeableActivity`、minAspectRatio / maxAspectRatio などが影響対象。
- Component boundary: virtual device owner / platform services / WindowManager app-compat policy の境界。

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
- `frameworks-base/core/java/android/window/flags/large_screen_experiences_app_compat.aconfig`
- `frameworks-base/core/api/system-current.txt`
- `frameworks-base/services/tests/wmtests/src/com/android/server/wm/AppCompatAspectRatioOverridesTest.java`
- `frameworks-base/services/tests/wmtests/src/com/android/server/wm/SizeCompatTests.java`

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル（File / symbol） | Android 15 の基準挙動（baseline） | Android 16 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `VirtualDisplayConfig#isIgnoreActivitySizeRestrictions()` / Builder method | `android-15.0.0_r36` にも flagged SystemApi として存在 | `android-16.0.0_r4` でも fixed orientation / aspect ratio / resizability ignore を表す SystemApi | Per-app overrides の入口。公式文書の "ignore orientation, aspect ratio, and resizability restrictions" と一致する。 |
| `DisplayManagerService#createVirtualDisplayInternal` | trusted virtual display permission path は存在 | trusted flag がない場合は request を無視し、trusted の場合だけ WindowManager に設定 | select virtual devices / trusted display gate の実装根拠。 |
| `DisplayWindowSettings#setIgnoreActivitySizeRestrictionsOnDisplayLocked` | display override setting として存在 | display uniqueId / `Display.TYPE_VIRTUAL` に setting を保存 | app 単位ではなく display 単位の override である根拠。 |
| `DisplayContent#isDisplayIgnoreActivitySizeRestrictions()` | display setting を参照 | app-compat policy が参照する display property | local physical display と selected virtual display を分ける根拠。 |
| `AppCompatOrientationPolicy#overrideOrientationIfNeeded` | eligible display で orientation request を `SCREEN_ORIENTATION_USER` に変換 | Android 16 target でも同経路 | screenOrientation が virtual display owner override で無視される根拠。 |
| `AppCompatAspectRatioOverrides#hasFullscreenOverride` | display ignore condition を fullscreen override 条件に含む | Android 16 target でも同経路 | aspect ratio / resizability restriction が無視される根拠。 |
| `AppCompatUtils#isDisplayIgnoreActivitySizeRestrictions` | aconfig flag + display setting gate | targetSdkVersion 36 ではなく flag / display 条件 | targetSdkVersion gate がない根拠。 |
| `VirtualDeviceManager#createVirtualDevice` | `CREATE_VIRTUAL_DEVICE` permission required | Android 16 でも system / role 前提 | ordinary app が任意に virtual device owner になれない根拠。 |
| `VirtualDeviceImpl#createVirtualDisplay` | owner UID check と owned display tracking | Android 16 でも caller owner / display ownership を検査 | virtual device owner が管理する display に限定される根拠。 |
| `AndroidManifest.xml` permissions | `CREATE_VIRTUAL_DEVICE` / `ADD_TRUSTED_DISPLAY` は public runtime permission ではない | `CREATE_VIRTUAL_DEVICE` は `internal|role`、`ADD_TRUSTED_DISPLAY` は `signature|role` | trusted / privileged owner 条件の根拠。 |

## 主要証跡（Key Evidence）

### Virtual display config

`VirtualDisplayConfig#isIgnoreActivitySizeRestrictions()` は、virtual display が app の fixed orientation、aspect ratio、resizability を無視するかを返す。Builder method は `@SystemApi` / `@FlaggedApi` で、true にするには `DisplayManager#VIRTUAL_DISPLAY_FLAG_TRUSTED` が必要であり、そうでなければ property は無視される。

Diff interpretation:
- Android 15 tag にも同 API は存在する。Android 16 で完全新規の API surface ではなく、Android 16 公式文書で developer-facing behavior change として明示された項目と解釈する。

### DisplayManagerService trusted display gate

`DisplayManagerService` は `virtualDisplayConfig.isIgnoreActivitySizeRestrictions()` が true でも、virtual display が `VIRTUAL_DISPLAY_FLAG_TRUSTED` を持たない場合は warning を出して request を無視する。trusted の場合のみ `WindowManagerInternal#setIgnoreActivitySizeRestrictionsOnDisplay(displayUniqueId, Display.TYPE_VIRTUAL, true)` を呼ぶ。

Diff interpretation:
- "select virtual devices" は、virtual device owner が管理するすべての display ではなく、trusted 条件と config 条件を満たした display に限定される。

### WindowManager display-level state

`DisplayWindowSettings` は `mIgnoreActivitySizeRestrictions` を display override settings に保存し、`DisplayContent` は作成時にこの値を読み込む。`DisplayContent#isDisplayIgnoreActivitySizeRestrictions()` は fixed orientation、aspect ratio、resizability を無視する display かを返す。

Diff interpretation:
- local physical display 上の一般的な OS update behavior ではなく、display 単位の policy として適用される。

### AppCompat orientation / aspect ratio path

`AppCompatOrientationPolicy#overrideOrientationIfNeeded(...)` は、eligible virtual display で activity orientation request を無視し `SCREEN_ORIENTATION_USER` を返す。`AppCompatAspectRatioOverrides#hasFullscreenOverride()` は display ignore condition を fullscreen override 条件に含める。`AppCompatUtils#isDisplayIgnoreActivitySizeRestrictions(...)` は aconfig flag と display state を gate にする。

Diff interpretation:
- `screenOrientation`、min/max aspect ratio、`resizeableActivity=false` に依存する app で UI impact が出る根拠となる。
- targetSdkVersion 36 gate は確認できない。

### Virtual device owner privilege and ownership

`VirtualDeviceManager#createVirtualDevice` は `CREATE_VIRTUAL_DEVICE` permission を要求し、doc はこの permission が specific roles を持つ system apps にのみ利用可能と説明する。`VirtualDeviceImpl#createVirtualDisplay` は `checkCallerIsDeviceOwner()` を実行し、created display を virtual device の owned display として管理する。`AndroidManifest.xml` では `CREATE_VIRTUAL_DEVICE` が `internal|role`、`ADD_TRUSTED_DISPLAY` が `signature|role` である。

Diff interpretation:
- ordinary app が任意に同じ override を使う挙動ではない。

### CTS / unit test evidence

`AppCompatAspectRatioOverridesTest` は `FLAG_VDM_FORCE_APP_UNIVERSAL_RESIZABLE_API` を有効化した上で、display ignore activity size restrictions が true の場合に fullscreen override が true になること、false では true にならないこと、orientation override opt-out property false の場合には override されないことを検証している。

`SizeCompatTests` は `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` により activity / application level で restricted resizability opt-out が扱われることを検証している。

Diff interpretation:
- AOSP test は display ignore flag が app-compat aspect ratio / resizability policy に影響することを裏付ける。

## Compat framework evidence

公式 compat framework changes では、本件と隣接する以下の Change ID を確認した。

- `UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415: targetSdkVersion 36+ の large screen behavior。app orientation、resizability、aspect ratio constraints を large screens で無視する。これは本件の virtual device owner projection path とは別項目。
- `OVERRIDE_ANY_ORIENTATION_TO_USER` / 310816437: disabled for all apps。package override により orientation requested by activity を `SCREEN_ORIENTATION_USER` にできる。
- `OVERRIDE_MIN_ASPECT_RATIO` / 174042980: disabled for all apps。manifest minimum aspect ratio を override する gate。
- `FORCE_RESIZE_APP` / 174042936: disabled for all apps。package を resizable に force する。
- `FORCE_NON_RESIZE_APP` / 181146395: disabled for all apps。

本件の `VirtualDisplayConfig#setIgnoreActivitySizeRestrictions` / virtual device owner per-display override 自体を直接 toggle する compat Change ID は確認できない。

---

# Facts / Observations / Hypotheses / Conclusions

## Facts

- 公式文書は Per-app overrides を Android 16 all apps / Device form factors の項目として掲載している。
- 公式文書は Android 16 / API level 36 で virtual device owner が select virtual devices 上の app settings を override できると述べる。
- 公式文書は例として、external display projection 時に orientation、aspect ratio、resizability restrictions を無視できると述べる。
- AOSP では `VirtualDisplayConfig.Builder#setIgnoreActivitySizeRestrictions(boolean)` が fixed orientation、aspect ratio、resizability ignore を表す。
- AOSP ではこの request は trusted virtual display でない場合に無視される。
- AOSP では display uniqueId / type に紐付く WindowManager setting として `mIgnoreActivitySizeRestrictions` が保存される。
- AOSP では AppCompat orientation / aspect ratio policy がこの display setting を参照する。
- AOSP では `CREATE_VIRTUAL_DEVICE` が `internal|role`、`ADD_TRUSTED_DISPLAY` が `signature|role`。
- targetSdkVersion 36 gate は本件の主要 code path から確認できない。

## Observations

- "Per-app overrides" という公式見出しだが、AOSP 実装の中心は app package 単位だけではなく display-level setting である。影響は selected virtual device / display に限定される。
- 関連 API / flag は Android 15 tag にも存在するため、strict diff では完全新規追加ではない。
- Android 16 behavior change として顧客に説明すべき点は、projection 環境では app-declared restrictions を維持できない可能性があること。
- targetSdkVersion 36+ の `UNIVERSAL_RESIZABLE_BY_DEFAULT` は似た説明になるが、large screen targetSdk change であり、本件とは gate が異なる。

## Hypotheses

- Android 16 production / OEM / companion app streaming implementation でこの override が有効になると、従来は letterbox / fixed orientation / fixed aspect ratio で守られていた phone UI が、external display 上で広い bounds に展開される可能性がある。
- PC、VR、car infotainment、Chromebook などの投影先では、display density、input modality、window bounds の違いにより UI regression が製品ごとに異なる可能性がある。
- app compatibility property による一部 opt-out は存在するが、virtual device owner projection に対する包括的な app-side 回避策としては扱えない。

## Conclusions

- Primary classification は `OS_UPDATE_ALL_APPS`。ただし runtime condition として Android 16、trusted / privileged virtual device owner、selected trusted virtual display、override enabled が必要。
- targetSdkVersion 36 化の影響として説明してはいけない。Android 16 / targetSdkVersion 35 でも projection 条件を満たせば影響し得る。
- local physical display の通常実行影響として説明してはいけない。
- 顧客向けには、app-declared orientation / aspect ratio / resizability restrictions に依存せず、adaptive layout / WindowMetrics / large screen QA で対応する必要があると説明する。

---

# 期待挙動マトリクス（Expected Behavior Matrix）

## OS / targetSdkVersion matrix

| シナリオ（Scenario） | 期待挙動（Expected behavior） |
| --- | --- |
| Android 16 / targetSdkVersion 35 / local physical display | 本件の per-display projection override は原則適用されない。 |
| Android 16 / targetSdkVersion 36 / local physical display | targetSdkVersion 35 と同じ。本件だけでは local display に影響しない。 |
| Android 16 / targetSdkVersion 35 / projected by virtual device owner | selected trusted virtual display で override が有効なら、orientation / aspect ratio / resizability restrictions が無視され得る。 |
| Android 16 / targetSdkVersion 36 / projected by virtual device owner | targetSdkVersion 35 と同じ。本件の主要 gate は targetSdkVersion 36 ではない。 |
| Android 15 / targetSdkVersion 36 / same app behavior if technically comparable | 公式 Android 16 behavior としては扱わない。関連 API / flag がある build では product config / flag / 実機挙動を別途確認する。 |

## Owner / display matrix

| シナリオ（Scenario） | 期待挙動（Expected behavior） |
| --- | --- |
| Android 16 / trusted or privileged virtual device owner | `CREATE_VIRTUAL_DEVICE` / trusted display 権限と owner UID 条件を満たす場合、managed virtual display を作成・管理できる。 |
| Android 16 / ordinary app without virtual device owner privilege | 同じ override を任意に使う前提ではない。 |
| Android 16 / selected virtual device with per-app overrides enabled | orientation / aspect ratio / resizability restrictions が無視され得る。 |
| Android 16 / virtual device without overrides | 通常の display / app-compat policy に従う。 |
| Android 16 / app projected to PC display | desktop-like bounds / input modality で UI regression を確認する。 |
| Android 16 / app projected to VR device display | VR display の aspect ratio / density / input path に応じた確認が必要。 |
| Android 16 / app projected to car infotainment display | landscape / wide screen で portrait UI が崩れる可能性がある。 |
| Android 16 / app projected to Chromebook / large display | large screen / window resize / keyboard / mouse の確認が必要。 |

## Restriction matrix

| シナリオ（Scenario） | 期待挙動（Expected behavior） |
| --- | --- |
| Android 16 / orientation restriction ignored | activity の requested orientation は eligible virtual display で `SCREEN_ORIENTATION_USER` 相当に扱われ得る。 |
| Android 16 / orientation restriction respected | override disabled / non-trusted display / non-projection path では通常 policy に従う。 |
| Android 16 / aspect ratio restriction ignored | display ignore condition が fullscreen / aspect ratio override 条件になる。 |
| Android 16 / aspect ratio restriction respected | override がない display では manifest / app-compat policy に従う。 |
| Android 16 / resizability restriction ignored | `resizeableActivity=false` 前提が崩れ、large / external display に合わせて扱われ得る。 |
| Android 16 / resizability restriction respected | override がない display では通常の resizability policy に従う。 |
| Android 16 / portrait-only app projected to landscape large display | clipping、stretched layout、orientation-specific UI bug、camera preview issue を確認する。 |
| Android 16 / app with `resizeableActivity=false` | selected virtual display では unresizable 前提が無視され得る。 |
| Android 16 / app with fixed minAspectRatio / maxAspectRatio | selected virtual display では aspect ratio 制限が無視され得る。 |
| Android 16 / app already adaptive to large screens | 影響は低いが projection bounds / input / density の regression test は必要。 |
| Android 16 / app designed only for phone portrait | 高リスク。large screen / landscape / external input で要検証。 |
| Android 16 / WindowMetrics / configuration changes under projection | virtual display の bounds / density / orientation に応じた WindowMetrics / resources qualifier を前提に検証する。 |

## Migration matrix

| シナリオ（Scenario） | 期待挙動（Expected behavior） |
| --- | --- |
| app migrates to adaptive layouts | per-display override / projection 環境でも UI regression risk が下がる。 |
| app continues relying on orientation / aspect ratio / resizability restrictions | Android 16 projection flow で期待が破られる可能性が残る。 |

---

# 影響対象（Affected Apps）

影響を受けやすいアプリ:

- companion app streaming / virtual device projection で利用されるアプリ。
- phone portrait 専用 UI のアプリ。
- fixed orientation を前提にするアプリ。
- aspect ratio 制限を前提にするアプリ。
- `resizeableActivity=false` や resizability 制限を持つアプリ。
- large screen / external display / desktop mode / Chromebook / car display / VR display で利用され得るアプリ。
- camera / media / map / game / productivity / document editing など、window size / orientation / input modality に敏感なアプリ。
- custom layout measurement / display metrics / WindowMetrics assumptions を持つアプリ。
- multi-window / freeform / large screen adaptive 対応が不十分なアプリ。
- adaptive layout / responsive UI へ移行すべきアプリ。
- virtual device owner / privileged companion app と連携するアプリ。

低リスクまたは影響外になりやすいアプリ:

- virtual device owner projection 経路で使われないアプリ。
- local physical display でのみ通常実行されるアプリ。
- orientation / aspect ratio / resizability restrictions に依存しないアプリ。
- large screen / arbitrary window size / keyboard / mouse に対応済みの adaptive app。

---

# テスト観点（Test Points）

必須確認:

- Android 15 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 36。
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較。
- local physical display 実行。
- virtual device owner による projection 実行。
- trusted / privileged virtual device owner の有無。
- selected virtual device per-app override enabled / disabled。
- orientation restriction respected / ignored。
- aspect ratio restriction respected / ignored。
- resizability restriction respected / ignored。
- portrait-only activity projected to landscape display。
- `screenOrientation` manifest combinations。
- `resizeableActivity=true/false`。
- minAspectRatio / maxAspectRatio combinations。
- large display / desktop-class window / car display / VR display / Chromebook display。
- WindowMetrics / Configuration / DisplayInfo / resources qualifier changes。
- foldable / tablet / external display layout comparison。
- keyboard / mouse / touch / controller input under projection。
- camera preview / media playback / map / game / form / document workflows。
- screenshot / screen recording comparison。
- layout clipping / letterboxing / stretching / pillarboxing / touch target regression。
- graceful adaptive layout fallback。
- logs / `dumpsys activity` / `dumpsys window` / WM tracing / Perfetto trace。
- automated UI tests and manual large-screen QA。

---

# 顧客向け説明（Customer-facing Explanation）

Android 16 の Per-app overrides は、Android 16 に OS アップデートしたすべての通常起動で画面制限が無視されるという意味ではありません。影響が出るのは、trusted / privileged virtual device owner が app を virtual device 上で実行し、remote / external display に投影する場合です。

その投影環境では、virtual device owner が select virtual devices 上で app settings を override でき、orientation、aspect ratio、resizability restrictions が無視される可能性があります。したがって、portrait-only、fixed orientation、`resizeableActivity=false`、min/max aspect ratio を前提にした UI は、large screen / landscape / desktop-class bounds で崩れる可能性があります。

targetSdkVersion 36 へ上げたこと自体が本件の直接条件ではありません。Android 16 / targetSdkVersion 35 のままでも、projection 条件を満たせば影響し得ます。対応は manifest restriction への依存を減らし、WindowMetrics / adaptive layout / external display QA で UI を成立させることです。

---

# 推奨対応候補（Recommended Action Candidates）

- companion app streaming / virtual device projection / external display use case の有無を棚卸しする。
- `screenOrientation`、`resizeableActivity=false`、minAspectRatio / maxAspectRatio、custom display metrics assumptions を棚卸しする。
- portrait-only / phone-only layout を large screen / landscape / desktop-class bounds で確認する。
- WindowMetrics / size class / adaptive navigation / responsive layout へ移行する。
- camera / media / map / game / document / form など display size に敏感な workflow を projection 環境で手動確認する。
- SDK / library が fixed orientation や fixed aspect ratio を前提にしていないか確認する。
- virtual device owner / privileged companion app と連携する場合、どの virtual display に override が有効かを仕様として確認する。

---

# Evidence gaps / 注意点

- `android-15.0.0_r36` にも関連 API / flag が存在するため、AOSP tag diff だけで Android 16 新規挙動と断定しない。
- Android 16 production build での aconfig flag default、OEM / product build、virtual device owner 実装により実際の投影 behavior は差が出る可能性がある。
- Companion app streaming の正しい参照先は `https://source.android.com/docs/core/permissions/app-streaming`。参照先 path を取り違えないように注意が必要。
- PC / VR / car / Chromebook は公式文書上の例であり、AOSP framework evidence と product-specific implementation evidence は分けて扱う。

---

# Human decision placeholder

最終優先度（Final Priority）:
- Critical / High / Medium / Low

顧客通知要否（Customer Communication）:
- Required / Recommended / Not required

Release readiness 判断:
- Blocker / Non-blocker / Needs more testing / N/A

補足:
- 最終優先度、顧客通知要否、release readiness は repository owner が判断する。

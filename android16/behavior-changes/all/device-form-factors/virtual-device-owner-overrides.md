# Virtual device owner overrides 調査レポート

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
- https://developer.android.com/about/versions/16/behavior-changes-all#virtual-device-owner-overrides

Page:
- Behavior changes: all apps

Category:
- Device form factors

Section:
- Virtual device owner overrides

Subsections:
- Per-app overrides
- Common breaking changes
- References

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `OS_UPDATE_ALL_APPS`

追加条件（Additional conditions）:
- Android 16 上で、trusted / privileged virtual device owner が作成・管理する virtual device / trusted virtual display にアプリが投影されること。
- virtual display が `VirtualDisplayConfig.Builder#setIgnoreActivitySizeRestrictions(true)` 相当の設定で作成され、かつ trusted display であること。
- 影響は local physical display の通常実行ではなく、virtual device owner による projection / external display / large screen 実行に限定される。

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 16 に OS アップデートしただけで適用されるか | Conditional Yes | 公式 all apps ページの変更。AOSP では virtual display / trusted display / aconfig flag を条件にし、targetSdkVersion 36 gate は見つからない。 |
| targetSdkVersion 36 以上が必要か | No | `VirtualDisplayConfig`、`DisplayManagerService`、WindowManager app-compat 経路に targetSdkVersion 36 条件は見つからない。 |
| local phone display の通常実行に影響するか | No | override は display uniqueId / `Display.TYPE_VIRTUAL` に対する `DisplayWindowSettings` として設定される。 |
| ordinary app が任意に同じ override を使えるか | No | `CREATE_VIRTUAL_DEVICE` は `internal|role`、`ADD_TRUSTED_DISPLAY` は `signature|role`。API は `@SystemApi` / `@FlaggedApi`。 |
| Compat Change ID が関係するか | Indirect only | 公式 compat framework には関連する orientation / aspect ratio Change ID があるが、本件の virtual display owner override 自体を直接 toggle する Change ID は確認できない。 |

### 調査日（Investigation Date）

2026-07-05

### 信頼度（Confidence）

- Medium-High

理由:
- 公式文書が all apps ページで Android 16 の変更として明記している。
- AOSP `android-16.0.0_r4` で virtual display config、trusted display gate、WindowManager display setting、orientation / aspect ratio / resizability override 経路を確認した。
- targetSdkVersion 36 gate が該当経路にないことを確認した。
- ただし `VirtualDisplayConfig#setIgnoreActivitySizeRestrictions()` と aconfig flag は `android-15.0.0_r36` 側にも存在するため、From/To tag 差分だけで「Android 16 で完全新規追加」とは言えない。公式 Android 16 behavior change としての顧客影響は確認できるが、Android 15 tag 内の feature-flagged / product-enabled 状態は別途実機・build config 確認が必要。

---

# エグゼクティブサマリー（Executive Summary）

Android 16 では、trusted / privileged virtual device owner が管理する select virtual device 上でアプリを実行し、PC、VR device、car infotainment、Chromebook などの remote / external display に投影する場合に、アプリの orientation、aspect ratio、resizability 制限を virtual device owner 側で無視できる。

この変更は targetSdkVersion 36 化の影響ではなく、Android 16 OS 上で virtual device owner projection 経路に乗る場合の条件付き影響である。通常の phone local display 実行では、本件の override は適用されない。

影響が出るのは、portrait-only、固定方向、`resizeableActivity=false`、min/max aspect ratioなどに依存し、large screen / external display / landscape windowに適応していないアプリである。顧客向けには「OS更新だけ」「targetSdkVersion 36化」「virtual device owner projection時だけ」「large screen UI impact」を分けて説明する必要がある。

---

# 公式ドキュメント確認（Original Documentation）

## 原文要旨（Statements）

公式文書は以下を述べている。

- Android 16 には、virtual device owner によって display へ projected されるアプリ向けの変更が含まれる。
- virtual device owner は virtual device を作成・管理する trusted / privileged app である。
- virtual device owner は local device、たとえば phone 上にあり、virtual device 上でアプリを実行して remote device の display、たとえば personal computer、VR device、car infotainment system に投影する。
- Android 16 / API level 36 では、virtual device owner は自分が管理する select virtual devices 上で app settings を override できる。
- 例として、external display へ app を投影する際に、orientation、aspect ratio、resizability restrictions を無視できる。
- Android 16 behavior は car displays や Chromebooks など large screen form factors 上の UI、特に small portrait display 向け layout に影響し得る。
- adaptive layouts への対応を参照するよう案内している。

## 公式本文との差分確認

調査開始時点で公式 URL の該当セクションを再確認した。依頼に含まれる Original statements / Applicability details と公式本文の主旨は一致している。

## 解釈（Interpretation）

この項目は、通常の app launch や local phone display の挙動変更ではない。virtual device owner が投影対象の virtual display を作成・管理し、その display に対して activity size restrictions を無視する設定を適用した場合に、アプリ側の manifest / app compatibility restrictions が projection 上で期待どおり尊重されない可能性がある、という変更である。

---

# 適用条件（Applicability）

## 適用される条件（Applies when）

- Android version: Android 16。
- Page type: all apps。
- targetSdkVersion: 35 / 36 の差は本件の主要 gate ではない。
- Device / display condition: app が virtual device owner 管理下の virtual display / remote display に projected される。
- Owner condition: caller が virtual device owner であり、通常アプリではない。
- Display condition: select virtual device / virtual display に `ignoreActivitySizeRestrictions` が有効化され、trusted display 条件を満たす。
- UI condition: app が orientation / aspect ratio / resizability restrictions に依存している場合、large screen / external display 上で layout impact が出やすい。

## 適用されない、または低リスクの条件（Non-impact / Lower-impact）

- local physical display 上で通常実行されるアプリ。
- virtual device owner projection 経路に乗らないアプリ。
- app が adaptive layout / arbitrary window size / large screen に対応済みの場合。
- virtual device owner が override を適用しない virtual device。
- ordinary app が通常の `VirtualDisplay` を使うだけで trusted virtual device owner として動作していない場合。

## Compat / flag / API surface

- Direct compat Change ID: 本件の virtual device owner override 自体を直接 toggle する compat framework Change ID は確認できない。
- Related compat entries:
  - `UNIVERSAL_RESIZABLE_BY_DEFAULT` は targetSdkVersion 36+ の large screen behavior であり、本件とは別項目。
  - `OVERRIDE_ANY_ORIENTATION_TO_USER`、`OVERRIDE_MIN_ASPECT_RATIO` などは per-app app-compat testing / override 用で、本件の virtual display owner path と混同しない。
- Aconfig:
  - `com.android.window.flags.vdm_force_app_universal_resizable_api`
  - description: virtual display上でappをあらゆるウィンドウサイズへ変更可能な状態に強制するAPI availability。

---

# AOSP 調査（AOSP Investigation）

## AOSP checkout hygiene

- `frameworks-base` working tree: clean。
- `android-15.0.0_r36` tag: present。
- `android-16.0.0_r4` tag: present。
- Evidence は local working tree の未コミット差分ではなく、tag comparison と `android-16.0.0_r4` source を基準に確認した。

## Source context reviewed

### Virtual display API / trusted display gate

Files / symbols:
- `frameworks-base/core/java/android/hardware/display/VirtualDisplayConfig.java`
- `VirtualDisplayConfig#isIgnoreActivitySizeRestrictions()`
- `VirtualDisplayConfig.Builder#setIgnoreActivitySizeRestrictions(boolean)`

Relevant behavior:
- `isIgnoreActivitySizeRestrictions()`はdisplayが固定方向、aspect ratio、サイズ変更可否の制約を無視するかを返す。
- API は `@SystemApi` かつ `@FlaggedApi(com.android.window.flags.Flags.FLAG_VDM_FORCE_APP_UNIVERSAL_RESIZABLE_API)`。
- Builder method の doc は、true にするには `DisplayManager#VIRTUAL_DISPLAY_FLAG_TRUSTED` が必要で、trusted でない display では property が無視されると説明している。

Diff interpretation:
- この API / flag は Android 15 tag にも存在する。したがって From/To diff だけでは完全新規追加ではない。
- しかし Android 16 all apps 公式文書では、virtual device owner projection 時の app settings override として顧客向け behavior change が明示された。

### DisplayManagerService enforcement

Files / symbols:
- `frameworks-base/services/core/java/com/android/server/display/DisplayManagerService.java`
- virtual display creation path

Relevant behavior:
- `virtualDisplayConfig.isIgnoreActivitySizeRestrictions()` が true の場合、display が `VIRTUAL_DISPLAY_FLAG_TRUSTED` を持たなければ warning を出して request を無視する。
- trusted display の場合だけ `WindowManagerInternal#setIgnoreActivitySizeRestrictionsOnDisplay(displayUniqueId, Display.TYPE_VIRTUAL, true)` を呼ぶ。

Diff interpretation:
- override は app package ではなく display uniqueId / virtual display type に紐付く。
- 「select virtual devices」の実装上の意味は、virtual device owner が作成したすべての virtual display ではなく、該当 config と trusted 条件を満たした display だけに設定されること。

### WindowManager display setting

Files / symbols:
- `frameworks-base/services/core/java/com/android/server/wm/WindowManagerInternal.java`
- `WindowManagerInternal#setIgnoreActivitySizeRestrictionsOnDisplay(...)`
- `frameworks-base/services/core/java/com/android/server/wm/WindowManagerService.java`
- `frameworks-base/services/core/java/com/android/server/wm/DisplayWindowSettings.java`
- `frameworks-base/services/core/java/com/android/server/wm/DisplayContent.java`

Relevant behavior:
- `DisplayWindowSettings#setIgnoreActivitySizeRestrictionsOnDisplayLocked(...)` は `SettingsEntry#mIgnoreActivitySizeRestrictions` を display override settings に保存する。
- `DisplayContent`は作成時に`mIgnoreActivitySizeRestrictions`を読み込み、`isDisplayIgnoreActivitySizeRestrictions()`で固定方向、aspect ratio、サイズ変更可否の制約を無視するdisplayかを返す。
- `DisplayContent` の comment は、この値が `VirtualDisplayConfig.Builder#setIgnoreActivitySizeRestrictions` から設定され得ると説明している。

Diff interpretation:
- local physical display への一般的な OS update 影響ではなく、display 単位の WindowManager policy として適用される。

### Orientation / aspect ratio / resizability override path

Files / symbols:
- `frameworks-base/services/core/java/com/android/server/wm/AppCompatOrientationPolicy.java`
- `frameworks-base/services/core/java/com/android/server/wm/AppCompatAspectRatioOverrides.java`
- `frameworks-base/services/core/java/com/android/server/wm/AppCompatUtils.java`

Relevant behavior:
- `AppCompatOrientationPolicy#overrideOrientationIfNeeded(...)`はeligible virtual displayではactivityからの画面の向きの要求を無視し、`SCREEN_ORIENTATION_USER`を返す。
- `AppCompatAspectRatioOverrides#hasFullscreenOverride()` は `shouldIgnoreActivitySizeRestrictionsForDisplay()` を fullscreen override 条件に含める。
- `AppCompatUtils#isDisplayIgnoreActivitySizeRestrictions(...)` は aconfig flag と `DisplayContent#isDisplayIgnoreActivitySizeRestrictions()` の両方を gate にする。
- `AppCompatUtils#isChangeEnabled(...)` は display が restrictions を無視する場合、package-level compat change を適用しないようにしている。

Diff interpretation:
- official statement の「orientation, aspect ratio, resizability restrictions can be ignored」を支える主要な WM app-compat 経路である。
- targetSdkVersion 36 gate ではなく、display policy gate と aconfig flag gate が中心である。

### Virtual device owner / projection path

Files / symbols:
- `frameworks-base/core/java/android/companion/virtual/VirtualDeviceManager.java`
- `VirtualDeviceManager.VirtualDevice`
- `frameworks-base/services/companion/java/com/android/server/companion/virtual/VirtualDeviceImpl.java`
- `VirtualDeviceImpl#createVirtualDisplay(...)`
- `VirtualDeviceImpl#launchPendingIntent(...)`

Relevant behavior:
- `VirtualDeviceManager.VirtualDevice` の doc は、virtual device が own virtual displays / audio / sensors などを持てること、creator が virtual display output を別 device に stream し、remote device からの input / sensor events を inject できることを説明している。
- `VirtualDeviceImpl#createVirtualDisplay(...)` は `checkCallerIsDeviceOwner()` を通した caller だけが実行でき、作成した display を `mVirtualDisplays` に登録する。
- `launchPendingIntent(displayId, ...)` は display がこの virtual device に属することを検査し、activity intent の場合は `ActivityOptions#setLaunchDisplayId` 経由で virtual display に起動する。
- `checkCallerIsDeviceOwner()` は calling UID が owner UID と一致しなければ `SecurityException` を投げる。

Diff interpretation:
- 「virtual device owner が app を virtual device 上で実行し、remote display に project する」という公式説明と整合する。
- ordinary app が任意の display に同じ override を適用できるわけではない。

### Permission / privilege evidence

Files / symbols:
- `frameworks-base/core/res/AndroidManifest.xml`
- `android.permission.CREATE_VIRTUAL_DEVICE`
- `android.permission.ADD_TRUSTED_DISPLAY`

Relevant behavior:
- `CREATE_VIRTUAL_DEVICE` は `internal|role`。
- `ADD_TRUSTED_DISPLAY` は `signature|role`。
- `VirtualDeviceManager.VirtualDevice` constructor は `@RequiresPermission(android.Manifest.permission.CREATE_VIRTUAL_DEVICE)`。
- trusted display を作成するには `ADD_TRUSTED_DISPLAY` が関係する。

Diff interpretation:
- 公式の "trusted or privileged app" という virtual device owner 定義を裏付ける。
- third-party ordinary app が Play 配布だけでこの override を自由に使う前提は置けない。

### App compatibility properties

Files / symbols:
- `frameworks-base/core/java/android/view/WindowManager.java`
- `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY`

Relevant behavior:
- Android 16 / API level 36以降の「画面の向きの要求を無視するdisplay設定」上で、package / activityが固定方向、min/max aspect ratio、サイズ変更不可を宣言・要求できるかに関係するpropertyがある。

Diff interpretation:
- これは virtual device owner override そのものではなく、large screen / app compatibility override ecosystem の一部である。
- 顧客説明では、本件の virtual projection 条件と targetSdkVersion 36+ large screen changes を混同しない。

---

# Facts / Observations / Hypotheses / Conclusions

## Facts

- 公式文書は Android 16 all apps ページの Device form factors に本項目を掲載している。
- 公式文書は virtual device owner を trusted / privileged app と説明している。
- 公式文書は Android 16 / API level 36 で virtual device owner が select virtual devices 上の app settings を override できると述べている。
- AOSPには`VirtualDisplayConfig.Builder#setIgnoreActivitySizeRestrictions(boolean)`があり、固定方向、aspect ratio、サイズ変更可否の制約を無視するdisplay propertyとして定義されている。
- AOSP ではこの property は `@SystemApi` / `@FlaggedApi` であり、trusted display 条件を満たさない場合は DisplayManagerService が request を無視する。
- AOSP では `CREATE_VIRTUAL_DEVICE` が `internal|role`、`ADD_TRUSTED_DISPLAY` が `signature|role`。
- WindowManager は display setting として `mIgnoreActivitySizeRestrictions` を保持し、AppCompat policy が orientation / aspect ratio / resizability restriction を無視する判定に使う。
- targetSdkVersion 36 gate は本件の主要 code path から確認できない。

## Observations

- 影響範囲は「all apps」ではあるが、すべての通常起動アプリに常時適用されるわけではない。virtual device owner projection という強い条件がある。
- `android-15.0.0_r36` でも関連 API / flag は存在するため、From/To diff だけで単純な新規実装とは言い切れない。
- Android 16 公式文書は、Android 16 上の app projection behavior と developer-facing UI impact を behavior change として扱っている。
- large screen / external display で portrait-only UI、fixed aspect ratio UI、unresizable UI が露出しやすくなる。

## Hypotheses

- Android 16 production builds では、virtual device owner / companion app streaming / OEM privileged projection flows がこの API を使うことで、従来 letterbox / restricted bounds だった一部アプリが external display 上でより大きい window / landscape / arbitrary aspect ratio として起動される可能性がある。
- PC、VR、car infotainment、Chromebook などの product-specific projection implementation は AOSP framework と OEM / privileged app 実装の組み合わせであり、実際の見え方は製品ごとに異なる可能性がある。
- app 側の `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` 等は一部 opt-out / compatibility control に関係し得るが、本件だけで universal な回避策とは扱えない。

## Conclusions

- Primary classification は `OS_UPDATE_ALL_APPS`。ただし runtime condition として virtual device owner projection / selected trusted virtual display / override enabled が必要。
- targetSdkVersion 36 化の影響として説明してはいけない。Android 16 / targetSdkVersion 35 でも projection 条件を満たせば同様に影響し得る。
- local physical display の通常実行影響として説明してはいけない。
- 顧客向けには、projection / companion app streaming / external display / large screen / car / Chromebook / VR で使われるアプリに対し、orientation、aspect ratio、resizability 制限へ依存しない adaptive layout 対応を推奨する。

---

# 期待挙動マトリクス（Expected Behavior Matrix）

## OS / targetSdkVersion matrix

| シナリオ（Scenario） | 期待挙動（Expected behavior） |
| --- | --- |
| Android 16 / targetSdkVersion 35 / local physical display | 本件の virtual display override は原則適用されない。 |
| Android 16 / targetSdkVersion 36 / local physical display | targetSdkVersion 35 と同じ。本件だけでは local display に影響しない。 |
| Android 16 / targetSdkVersion 35 / projected by virtual device owner | selected trusted virtual display で override が有効なら、orientation / aspect ratio / resizability restrictions が無視され得る。 |
| Android 16 / targetSdkVersion 36 / projected by virtual device owner | targetSdkVersion 35 と同じ。本件の主要 gate は targetSdkVersion 36 ではない。 |
| Android 15 / targetSdkVersion 36 / same app behavior if technically comparable | 公式 Android 16 behavior としては扱わない。関連 API / flag が存在する build では別途 product config / flag / device behavior を検証する。 |

## Projection / owner / display matrix

| シナリオ（Scenario） | 期待挙動（Expected behavior） |
| --- | --- |
| Android 16 / app projected to PC display | virtual device owner が override を適用すると large / desktop-like bounds で UI 影響が出得る。 |
| Android 16 / app projected to VR device display | VR remote display の bounds / aspect ratio に合わせて制限が無視され得る。製品実装差は別途確認。 |
| Android 16 / app projected to car infotainment display | landscape / wide display で portrait-only UI が崩れる可能性がある。 |
| Android 16 / app projected to Chromebook / large display | large screen layout と arbitrary window size の検証が必要。 |
| Android 16 / trusted or privileged virtual device owner | virtual device / trusted virtual display を作成し、条件を満たせば override を適用可能。 |
| Android 16 / ordinary app without virtual device owner privilege | `CREATE_VIRTUAL_DEVICE` / `ADD_TRUSTED_DISPLAY` 権限がなく、同じ前提では利用不可。 |
| Android 16 / selected virtual device with overrides enabled | orientation / aspect ratio / resizability restriction が無視され得る。 |
| Android 16 / virtual device without overrides | app-declared restrictions は通常の display policy / app compat policy に従う。 |

## Restriction matrix

| シナリオ（Scenario） | 期待挙動（Expected behavior） |
| --- | --- |
| Android 16 / orientation restriction ignored | `AppCompatOrientationPolicy`がeligible virtual displayでactivityからの画面の向きの要求を`SCREEN_ORIENTATION_USER`相当に扱う。 |
| Android 16 / orientation restriction respected | override disabled / non-eligible display / app opt-out 条件では通常 policy に従う。 |
| Android 16 / aspect ratio restriction ignored | display-level ignore setting が fullscreen / aspect ratio override 条件に入る。 |
| Android 16 / aspect ratio restriction respected | override がない display では manifest / app compat policy に従う。 |
| Android 16 / resizability restriction ignored | display-level ignore setting により unresizable 前提が無視され得る。 |
| Android 16 / resizability restriction respected | override がない display では通常の resizability policy に従う。 |
| Android 16 / portrait-only app projected to landscape large display | phone portrait 専用 UI の clipping、stretch、layout density / orientation bug を確認する必要がある。 |
| Android 16 / app with `resizeableActivity=false` | selected virtual display では制限が無視され得る。 |
| Android 16 / app with fixed minAspectRatio / maxAspectRatio | selected virtual display では aspect ratio 制限が無視され得る。 |
| Android 16 / app already adaptive to large screens | UI 影響は低い。WindowMetrics / configuration 変化の regression test は推奨。 |
| Android 16 / app designed only for phone portrait | 高リスク。large screen / landscape / external input で要検証。 |
| Android 16 / WindowMetrics / configuration changes under projection | virtual display bounds / density / orientation に応じた WindowMetrics / resources qualifier を前提に検証する。 |

## Migration matrix

| シナリオ（Scenario） | 期待挙動（Expected behavior） |
| --- | --- |
| app migrates to adaptive layouts | projection / large screen / arbitrary aspect ratio の UX risk が下がる。 |
| app continues relying on orientation / aspect ratio / resizability restrictions | Android 16 projection flow で期待が破られる可能性が残る。 |

---

# 影響対象（Affected Apps）

影響を受けやすいアプリ:

- companion app streaming / virtual device projection で利用されるアプリ。
- phone portrait 専用 UI のアプリ。
- 固定方向を前提にするアプリ。
- aspect ratio 制限を前提にするアプリ。
- `resizeableActivity=false` や resizability 制限を持つアプリ。
- large screen / external display / desktop mode / Chromebook / car display / VR display で利用され得るアプリ。
- camera / media / map / game / productivity / document editing など、window size / orientation / input modality に敏感なアプリ。
- custom layout measurement / display metrics / WindowMetrics assumptions を持つアプリ。
- multi-window / freeform / large screen adaptive 対応が不十分なアプリ。
- adaptive layout / responsive UI へ移行すべきアプリ。
- virtual device owner / privileged companion app と連携するアプリ。

低リスクまたは影響外になりやすいアプリ:

- projection flow で使われないアプリ。
- local phone display だけで通常実行されるアプリ。
- arbitrary window size / orientation / aspect ratio に対応済みの adaptive app。
- virtual device owner が override を適用しない環境だけを対象にするアプリ。

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
- selected virtual device override enabled / disabled。
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

この変更は、Android 16 に OS アップデートしたすべての通常起動で即座に画面制限が無視される、という意味ではありません。影響が出るのは、trusted / privileged virtual device owner がアプリを virtual device 上で実行し、PC、VR device、car infotainment、Chromebook などの remote / external display に投影する場合です。

その projection 環境では、virtual device owner が select virtual device 上で orientation、aspect ratio、resizability の制限を無視できるため、portrait-only や fixed-size 前提の UI が large screen / landscape / arbitrary window size で表示される可能性があります。

targetSdkVersion 36 へ上げたこと自体が本件の直接条件ではありません。Android 16 / targetSdkVersion 35 のままでも、projection 条件を満たせば影響し得ます。対応としては、orientation lock や aspect ratio restriction を最終防衛線にせず、WindowMetrics / adaptive layout / large screen QA で UI を成立させる必要があります。

---

# 推奨対応候補（Recommended Action Candidates）

- app が companion app streaming / virtual device projection / external display use case に入るか棚卸しする。
- `screenOrientation`、`resizeableActivity=false`、min/max aspect ratio、custom display metrics assumptions を棚卸しする。
- portrait-only / phone-only layout を large screen / landscape / desktop-class bounds で確認する。
- WindowMetrics / size class / responsive layout / adaptive navigation へ移行する。
- camera / media / map / game / document / form など display size に敏感な workflow を projection 環境で手動確認する。
- SDK / libraryが固定方向や固定aspect ratioを前提にしていないか確認する。
- virtual device owner / privileged companion app と連携する場合、どの virtual display に override が有効か契約・仕様として確認する。

---

# Evidence gaps / 注意点

- `android-15.0.0_r36` にも関連 API / flag が存在するため、AOSP tag diff だけで Android 16 新規挙動と断定しない。
- Android 16 production build での aconfig flag default、OEM / product build、virtual device owner 実装により実際の投影 behavior は差が出る可能性がある。
- PC / VR / car / Chromebook は公式文書上の例であり、AOSP framework evidence と product-specific implementation evidence は分けて扱う。
- 本調査では AOSP framework / services を中心に確認した。Pixel / OEM companion app streaming 実装の具体的 UX は別途実機確認が必要。

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

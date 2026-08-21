# References 調査レポート

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
- https://developer.android.com/about/versions/16/behavior-changes-all#references

Page:
- Behavior changes: all apps

Category:
- Device form factors

Parent section:
- Virtual device owner overrides

Section:
- References

Referenced document:
- Companion app streaming
- https://source.android.com/docs/core/permissions/app-streaming

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `OS_UPDATE_ALL_APPS`

重要な補足:
- `References` section 自体は independent runtime behavior change ではない。
- 利用可能な正式分類ラベルに `DOCUMENTATION_POINTER_ONLY` がないため、親項目 `Virtual device owner overrides` に合わせて `OS_UPDATE_ALL_APPS` を primary classification とする。
- 顧客向け説明では、`References` section の存在と、親項目 `Virtual device owner overrides` / `Per-app overrides` / `Common breaking changes` の実際の impact を混ぜない。

追加条件（Additional conditions inherited from parent section）:
- Android 16 上で app が virtual device owner 管理下の virtual device / virtual display に投影されること。
- trusted / privileged virtual device owner が selected virtual device / trusted virtual display に対して activity size restrictions ignore を有効にすること。
- app が orientation、aspect ratio、resizability restrictions、phone portrait layout、large screen 非対応 UI に依存している場合に影響が出やすい。

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| References section 自体が runtime behavior change か | No | 公式本文は `Companion app streaming` への参照リンクのみ。 |
| 親項目の behavior change と関係するか | Yes | Companion app streaming / virtual device owner projection の背景参照として置かれている。 |
| Android 16 に OS アップデートしただけで影響し得るか | Conditional Yes | 親項目は all apps ページ掲載。targetSdkVersion ではなく virtual device owner projection 条件が gate。 |
| targetSdkVersion 36 以上が必要か | No | 親項目の AOSP path に targetSdkVersion 36 gate は見つからない。 |
| local physical display の通常実行に影響するか | No | 親項目の override は selected virtual display / display-level setting に依存する。 |
| ordinary app が任意に同じ override を使えるか | No | `CREATE_VIRTUAL_DEVICE` は `internal|role`、`ADD_TRUSTED_DISPLAY` は `signature|role`。 |

### 調査日（Investigation Date）

2026-07-06

### 信頼度（Confidence）

- Medium

理由:
- 公式 Android Developers ページ上で `References` section が `Companion app streaming` への参照だけであることを確認した。
- Source Android の正しい参照先 `https://source.android.com/docs/core/permissions/app-streaming` を確認し、`COMPANION_DEVICE_APP_STREAMING` role、virtual device / virtual display、remote display への app streaming、remote input injection の説明を確認した。
- 親項目の AOSP evidence として、virtual device owner / trusted virtual display / orientation・aspect ratio・resizability override path を確認した。
- targetSdkVersion 36 gate が親項目の主要 code path にないことを確認した。

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [x] OS update / all apps on Android 16 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 36 on Android 16+
- [ ] targetSdkVersion >= 36, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [ ] Unknown / needs more evidence

分類の注記:
- この checkbox は親項目 `Virtual device owner overrides` の runtime behavior を反映する。
- `References` section 単体は documentation pointer only であり、独立した runtime behavior change として扱わない。

---

# エグゼクティブサマリー（Executive Summary）

Android 16 all apps ページの `Virtual device owner overrides` 配下にある `References` section は、`Companion app streaming` へのリンクだけで構成されている。したがって、この subsection 自体は独立した behavior change implementation ではない。

この参照は、virtual device owner が app を virtual device 上で実行し、remote / external display に投影する背景を理解するための導線である。実際の互換性影響は、親項目 `Per-app overrides` と `Common breaking changes` にある。具体的には、trusted / privileged virtual device owner が selected virtual display 上で orientation、aspect ratio、resizability restrictions を無視できるため、large screen / external display 上で phone portrait 前提の UI が崩れる可能性がある。

顧客向けには、以下を明確に分ける。

| 観点 | 説明 |
| --- | --- |
| References section | Companion app streaming への documentation pointer only。 |
| Parent behavior change | Virtual device owner projection 時の app settings override。 |
| Android 16 OS update impact | projection 条件を満たす場合、targetSdkVersion を変えなくても影響し得る。 |
| targetSdkVersion 36 impact | 本件の必要条件ではない。 |
| local physical display | 通常実行では本件の selected virtual display override は原則影響外。 |

---

# 公式ドキュメント確認（Original Documentation）

## 原文要旨（Statements）

公式文書の `References` section は以下のみを示している。

- `Companion app streaming`

親項目では以下を述べている。

- Android 16 では、virtual device owner によって display へ projected される apps に関する変更がある。
- virtual device owner は trusted / privileged app で、virtual device を作成・管理する。
- virtual device owner は app を virtual device 上で実行し、personal computer、VR device、car infotainment system など remote device の display に投影する。
- Android 16 では virtual device owner が selected virtual devices 上で app settings を override でき、orientation、aspect ratio、resizability restrictions を無視できる。
- large screen form factors 上で、small portrait display 向け layout が影響を受け得る。

## 公式本文との差分確認

調査開始時点で公式 URL の該当セクションを再確認した。依頼に含まれる Original statement `"Companion app streaming"` と公式本文は一致している。

参照先として確認すべき正しい Source Android ページは `https://source.android.com/docs/core/permissions/app-streaming` である。この文書は、`COMPANION_DEVICE_APP_STREAMING` role holder が virtual display を作成し、app をその display で起動して connected device に video stream として表示し、remote input / microphone events を local device 側へ inject できることを説明している。

## 解釈（Interpretation）

`References` は、親項目を理解するための背景リンクであり、単独で app behavior を変更するものではない。調査・顧客説明では、`References` を独立の breaking change として扱わず、`Virtual device owner overrides` の projection model を補足する関連資料として扱う。

---

# AOSP 調査（AOSP Investigation）

## AOSP checkout hygiene

- `frameworks-base` working tree: clean。
- `android-15.0.0_r36` tag: present。
- `android-16.0.0_r4` tag: present。
- Evidence は local working tree の未コミット差分ではなく、tag comparison と `android-16.0.0_r4` source を基準に確認した。

## 関連ファイル（Related Files）

- `frameworks-base/core/java/android/companion/virtual/VirtualDeviceManager.java`
- `frameworks-base/services/companion/java/com/android/server/companion/virtual/VirtualDeviceImpl.java`
- `frameworks-base/services/companion/java/com/android/server/companion/virtual/VirtualDeviceManagerService.java`
- `frameworks-base/core/res/AndroidManifest.xml`
- `frameworks-base/core/java/android/hardware/display/VirtualDisplayConfig.java`
- `frameworks-base/services/core/java/com/android/server/display/DisplayManagerService.java`
- `frameworks-base/services/core/java/com/android/server/wm/DisplayWindowSettings.java`
- `frameworks-base/services/core/java/com/android/server/wm/DisplayContent.java`
- `frameworks-base/services/core/java/com/android/server/wm/AppCompatOrientationPolicy.java`
- `frameworks-base/services/core/java/com/android/server/wm/AppCompatAspectRatioOverrides.java`
- `frameworks-base/services/core/java/com/android/server/wm/AppCompatUtils.java`
- `frameworks-base/core/java/android/view/WindowMetrics.java`
- `frameworks-base/core/api/system-current.txt`
- `frameworks-base/core/java/android/window/flags/large_screen_experiences_app_compat.aconfig`
- `frameworks-base/services/tests/wmtests/src/com/android/server/wm/AppCompatAspectRatioOverridesTest.java`
- `frameworks-base/services/tests/wmtests/src/com/android/server/wm/SizeCompatTests.java`

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル（File / symbol） | Android 15 の基準挙動（baseline） | Android 16 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| Android Developers `#references` | N/A | `Companion app streaming` への参照のみ | References section が独立 behavior change ではない根拠。 |
| Source Android `app-streaming` documentation | N/A | `COMPANION_DEVICE_APP_STREAMING` role、virtual display、remote display streaming、remote input injection を説明 | References が virtual device owner projection model の背景参照である根拠。 |
| `VirtualDeviceManager#createVirtualDevice` | `CREATE_VIRTUAL_DEVICE` permission required | Android 16 でも system / role 前提 | virtual device owner が trusted / privileged component である根拠。 |
| `VirtualDeviceImpl#createVirtualDisplay` | owner UID check と owned display tracking | Android 16 でも caller owner / display ownership を検査 | companion app streaming / projection の display ownership 境界を示す。 |
| `AndroidManifest.xml` permissions | `CREATE_VIRTUAL_DEVICE` / `ADD_TRUSTED_DISPLAY` は public runtime permission ではない | `CREATE_VIRTUAL_DEVICE` は `internal|role`、`ADD_TRUSTED_DISPLAY` は `signature|role` | ordinary app が任意に same override を使えない根拠。 |
| `VirtualDisplayConfig#isIgnoreActivitySizeRestrictions()` / Builder method | `android-15.0.0_r36`にもflagged SystemApiとして存在 | Android 16でも固定方向 / aspect ratio / サイズ変更可否の制約を無視することを表すSystemApi | 親項目per-app overrideの入口。 |
| `DisplayManagerService#createVirtualDisplayInternal` | trusted virtual display permission path は存在 | trusted flag がない場合は request を無視し、trusted の場合だけ WindowManager に設定 | selected virtual device / trusted display gate の実装根拠。 |
| `DisplayWindowSettings#setIgnoreActivitySizeRestrictionsOnDisplayLocked` | display override setting として存在 | display uniqueId / `Display.TYPE_VIRTUAL` に setting を保存 | local physical display と projected virtual display を分ける根拠。 |
| `AppCompatOrientationPolicy#overrideOrientationIfNeeded` | eligible displayで画面の向きの要求を`SCREEN_ORIENTATION_USER`に変換 | Android 16 targetでも同経路 | orientation restriction ignoredの根拠。 |
| `AppCompatAspectRatioOverrides#hasFullscreenOverride` | display ignore condition を fullscreen override 条件に含む | Android 16 target でも同経路 | aspect ratio / resizability override impact の根拠。 |
| `AppCompatUtils#isDisplayIgnoreActivitySizeRestrictions` | aconfig flag + display setting gate | targetSdkVersion 36 ではなく flag / display 条件 | targetSdkVersion gate がない根拠。 |
| `WindowMetrics#getBounds()` / `getDensity()` | window bounds と density を公開 | Android 16 でも app-facing metrics として存在 | projected display / large screen bounds が app layout に影響する説明根拠。 |
| `system-current.txt` | relevant APIs が存在 | `VirtualDeviceManager`、`VirtualDisplayConfig`、`VIRTUAL_DISPLAY_FLAG_TRUSTED`、`CREATE_VIRTUAL_DEVICE` が system API surface に存在 | API surface 上の関連 evidence。 |
| `AppCompatAspectRatioOverridesTest` | tests exist | display ignore true / false の fullscreen override behavior を test | override behavior が unit test で検証されている根拠。 |

## AOSP evidence summary

### Documentation pointer

公式 `References` section には `Companion app streaming` のリンクだけが置かれている。ここには独立した OS behavior、API call、manifest condition、permission state の説明はない。

Diff interpretation:
- `References` section 自体は no runtime behavior change。
- 親項目の behavior change を説明するための reference section と解釈する。

### Companion app streaming / virtual device owner boundary

Source Android の Companion app streaming 文書は、`COMPANION_DEVICE_APP_STREAMING` role holder が virtual display を作成し、app をその virtual display で起動して connected device に stream し、remote input / microphone events を local device に inject できることを説明する。AOSP では `VirtualDeviceManager#createVirtualDevice` が `CREATE_VIRTUAL_DEVICE` permission を要求し、system apps holding specific roles に限定される。`VirtualDeviceImpl` は caller が virtual device owner であること、display がその virtual device に属することを確認する。

Diff interpretation:
- Companion app streaming という背景は、ordinary app が同じ projection behavior を任意に発生させるという意味ではない。
- trusted / privileged virtual device owner / role / permission が必要である。

### Projection display override path

`VirtualDisplayConfig.Builder#setIgnoreActivitySizeRestrictions(boolean)`は固定方向、aspect ratio、サイズ変更可否の制約を無視するvirtual display propertyを設定する。`DisplayManagerService`はtrusted virtual displayでない場合に要求を無視し、trustedの場合のみWindowManagerにdisplay-level settingを渡す。

Diff interpretation:
- 親項目 `Per-app overrides` の実装根拠であり、`References` section から直接発生する変更ではない。

### WindowManager app-compat path

`AppCompatOrientationPolicy`と`AppCompatAspectRatioOverrides`はdisplay ignore stateを参照し、画面の向きの要求 / fullscreen / aspect ratio behaviorに影響させる。`AppCompatUtils`はaconfig flagとdisplay settingをgateにしており、targetSdkVersion 36 gateは確認できない。

Diff interpretation:
- Android 16 / targetSdkVersion 35 と Android 16 / targetSdkVersion 36 を分けても、本件の virtual display owner path 自体は targetSdkVersion 36 を必要条件としない。

### API surface / Android 15 baseline

`system-current.txt` には `VirtualDeviceManager#createVirtualDevice`、`VIRTUAL_DISPLAY_FLAG_TRUSTED`、`VirtualDisplayConfig#isIgnoreActivitySizeRestrictions()`、Builder method が存在する。From/To diff では、一部 API が flag 解除 / restricted environment annotation 追加などを受けているが、`ignoreActivitySizeRestrictions` 自体は Android 15 tag にも存在する。

Diff interpretation:
- Android 16 公式 behavior change としての developer-facing impact は確認できる。
- ただし AOSP diff だけで `Companion app streaming` reference や ignore API の導入時点を断定しない。

---

# Facts / Observations / Hypotheses / Conclusions

## Facts

- 公式 Android 16 all apps ページの `References` section は `Companion app streaming` へのリンクのみである。
- `References` section には独立した runtime behavior、API invocation、manifest requirement、permission grant condition は記載されていない。
- 親項目 `Virtual device owner overrides` は、trusted / privileged virtual device owner が remote display projection を行う model を説明している。
- 親項目 `Per-app overrides` は、orientation、aspect ratio、resizability restrictions を無視できることを説明している。
- 親項目 `Common breaking changes` は、large screen form factors 上で small portrait display 向け layout が影響を受け得ることを説明している。
- AOSP は virtual device owner / trusted virtual display / display-level activity size restriction ignore path を持つ。
- AOSP 該当 path に targetSdkVersion 36 gate は見つからない。

## Observations

- `References` を独立した behavior change として report すると、顧客向け説明で実装変更の所在を誤る。
- 正しくは、`References` は parent behavior を理解するための documentation pointer として扱う。
- 正しい Source Android 参照先は `source.android.com/docs/core/permissions/app-streaming` であり、companion app streaming と virtual device / virtual display / remote display projection の関係を説明している。
- 親項目の AOSP evidence は十分にあるが、References section の evidence は「リンクがあること」と「独立 runtime change ではないこと」が中心である。

## Hypotheses

- Android Developers 側のリンク表示だけでは URL path が分かりにくいため、参照先 path を取り違えないように注意が必要である。
- 参照先本文は virtual device owner / virtual display / remote display projection model の背景説明として有用だが、References section 自体の分類は documentation pointer only のままである。

## Conclusions

- Primary classification は、許可ラベル上は親項目に合わせて `OS_UPDATE_ALL_APPS` とする。
- ただし `References` section 自体は independent runtime behavior change ではない。
- 顧客向けには、`References` を「Companion app streaming への背景参照」と説明し、実際の互換性影響は `Per-app overrides` と `Common breaking changes` に紐付ける。
- OS update impact と targetSdkVersion impact は親項目と同じく分離する。Android 16 上の projection 条件が重要であり、targetSdkVersion 36 化は本件の必要条件ではない。

---

# 期待挙動マトリクス（Expected Behavior Matrix）

## OS / targetSdkVersion matrix

| OS / targetSdkVersion | 条件 | 期待挙動 |
| --- | --- | --- |
| Android 16 / targetSdkVersion 35 | local physical display | `References` section 自体の runtime change はない。親項目 override も原則適用されない。 |
| Android 16 / targetSdkVersion 36 | local physical display | 同上。targetSdkVersion 36 だけで References 起因の挙動変更はない。 |
| Android 16 / targetSdkVersion 35 | projected by virtual device owner | 親項目の projection / override 条件を満たせば影響し得る。References は背景参照。 |
| Android 16 / targetSdkVersion 36 | projected by virtual device owner | targetSdkVersion 35 と同様に、projection / override 条件で影響し得る。 |
| Android 15 / targetSdkVersion 36 | same app behavior if technically comparable | Android 16 References section 起因の変更はない。親項目関連 API / flag は tag 上存在するため product enablement 確認が必要。 |

## Scenario matrix

| Scenario | 期待挙動 / impact |
| --- | --- |
| References section / documentation pointer only | 独立 runtime behavior change ではない。 |
| Companion app streaming reference / relevant background | `COMPANION_DEVICE_APP_STREAMING` role、virtual display、remote display streaming、remote input injection を理解する背景資料。 |
| Android 16 / companion app streaming flow | trusted / privileged virtual device owner projection として親項目の影響条件になり得る。 |
| Android 16 / trusted or privileged virtual device owner | `CREATE_VIRTUAL_DEVICE` / `ADD_TRUSTED_DISPLAY` などの privileged boundary がある。 |
| Android 16 / ordinary app without virtual device owner privilege | 同じ override を任意には使えない。 |
| Android 16 / selected virtual device with overrides enabled | orientation / aspect ratio / resizability restrictions が無視され得る。 |
| Android 16 / virtual device without overrides | 親項目の override impact は出にくい。 |
| Android 16 / app projected to PC display | large / desktop-class bounds と input modality を確認する。 |
| Android 16 / app projected to VR device display | unusual display metrics / aspect ratio / input assumptions を確認する。 |
| Android 16 / app projected to car infotainment display | vehicle display bounds / landscape / input constraints を確認する。 |
| Android 16 / app projected to Chromebook / large display | large screen / resizable window assumptions を確認する。 |
| Android 16 / orientation restriction ignored | `screenOrientation` 前提は保護にならない可能性。 |
| Android 16 / aspect ratio restriction ignored | min/max aspect ratio や letterbox / pillarbox 前提が崩れ得る。 |
| Android 16 / resizability restriction ignored | `resizeableActivity=false` 前提が崩れ得る。 |
| Android 16 / large screen UI impact | phone-only UI では clipping、stretching、touch target regression が出得る。 |
| app reads reference documentation and migrates to adaptive layouts | recommended。References は背景理解として使う。 |
| app ignores projection guidance and continues relying on phone-only assumptions | projection 環境で高リスク。 |

---

# 影響対象アプリ（Potentially Affected Apps）

- companion app streaming / virtual device projection で利用されるアプリ。
- virtual device owner / privileged companion app と連携するアプリ。
- phone portrait 専用 UI のアプリ。
- 固定方向を前提にするアプリ。
- aspect ratio 制限を前提にするアプリ。
- `resizeableActivity=false` や resizability 制限を持つアプリ。
- large screen / external display / desktop mode / Chromebook / car display / VR display で利用され得るアプリ。
- adaptive layout / responsive UI へ移行すべきアプリ。
- References / companion app streaming documentation を確認すべきアプリ。

---

# テスト観点（Test Points）

- Android 15 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 36。
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較。
- References section が independent runtime change ではないこと。
- companion app streaming documentation の確認。
- local physical display 実行。
- virtual device owner による projection 実行。
- trusted / privileged virtual device owner の有無。
- selected virtual device override enabled / disabled。
- PC / VR / car infotainment / Chromebook / large display projection。
- orientation / aspect ratio / resizability restriction respected / ignored。
- WindowMetrics / Configuration / DisplayInfo / resources qualifier changes。
- screenshot / screen recording comparison。
- layout clipping / letterboxing / stretching / pillarboxing / touch target regression。
- logs / dumpsys activity / dumpsys window / WM tracing / perfetto trace。
- automated UI tests and manual large-screen QA。

---

# 推奨対応候補（Recommended Action Candidates）

- `References` section を独立した breaking change として扱わず、親項目の背景参照として扱う。
- Companion app streaming / virtual device owner projection の QA 対象アプリを棚卸しする。
- projection 対象になり得るアプリでは、orientation / aspect ratio / resizability restrictions を UI correctness の主要防御策として扱わない。
- adaptive layouts、WindowMetrics、large screen / external display QA、input modality QA を整備する。
- source.android の正しい参照先 `https://source.android.com/docs/core/permissions/app-streaming` を公開ドキュメント確認時に再確認する。

---

# Evidence gaps / 注意点

- 正しい参照先は `https://source.android.com/docs/core/permissions/app-streaming`。参照先 path を取り違えないように注意が必要である。
- Android 15 tag にも関連 API / aconfig flag が存在するため、AOSP diff だけで Android 16 での完全新規導入とは断定しない。
- car / Chromebook / PC / VR の具体的な projection behavior は OEM / product implementation と framework evidence を分ける必要がある。
- References section は documentation pointer only であり、実装根拠は親項目 `Virtual device owner overrides` の AOSP path から確認する。

---

# Human Decision Placeholder

以下は repository owner / human reviewer が決める項目であり、本調査では確定しない。

- Final priority:
- Final severity:
- Customer communication priority:
- Release readiness:
- Required documentation follow-up:
- Required app-side migration:
- Required QA scope:

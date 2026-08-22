# 16 KB page size compatibility mode 調査レポート

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
- https://developer.android.com/about/versions/16/behavior-changes-all#16-kb-compatibility-mode

Page:
- Behavior changes: all apps

Category:
- Core functionality

Section:
- 16 KB page size compatibility mode

Related official source:
- https://source.android.com/docs/core/architecture/16kb-page-size/16kb-backcompat-option

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `OS_UPDATE_ALL_APPS`

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 16 に OS アップデートしただけで適用されるか | Conditional Yes | 公式 all apps ページの変更。AOSP では `ScanPackageUtils` / `ProcessList` / zygote が targetSdkVersion ではなく、16 KB device と page-size compat flags を条件にする。 |
| targetSdkVersion 36 以上が必要か | No | 該当コードパスに targetSdkVersion 36 gate は見つからない。Android 16 / targetSdkVersion 35 でも 16 KB device かつ 4 KB-aligned native library 条件を満たすと影響し得る。 |
| 追加の実行時条件があるか | Yes | 16 KB page-size device、native library / ELF LOAD segment / APK 内 uncompressed library alignment、feature flag、manifest/settings override、app が native code を含むこと。 |
| Compat Change ID が関係するか | No | compat framework 公式一覧で本件の toggleable Change ID は確認できない。AOSP では aconfig flag `app_compat_option_16kb` / `app_compat_warnings_16kb` が関係する。 |

### 調査日（Investigation Date）

2026-07-05

### 信頼度（Confidence）

- High

理由:
- 公式文書が all apps ページで Android 16 の変更として明記している。
- AOSP `android-16.0.0_r4` で manifest 属性、PackageManager scan、native library alignment check、zygote runtime flag、warning dialog の主要経路を確認した。
- targetSdkVersion 36 gate が該当経路にないことを確認した。
- Android 15 tag にも staging / feature-flagged 実装が存在するため、Android 15 baseline との差分は「まったく存在しない機能」ではなく、「Android 16 SDK/API ID と warning / settings / alignment detail が固まった公開挙動」として解釈する。

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [x] OS update / all apps on Android 16 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 36 on Android 16+
- [ ] targetSdkVersion >= 36, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [ ] Unknown / needs more evidence

必要な実行時条件（Required runtime conditions）:
- Android version: Android 16 以上。
- targetSdkVersion: 条件なし。35 と 36 の両方で同じ OS 側条件が適用される見込み。
- Device/form factor: 16 KB memory page size device。4 KB page-size device では app launch の 16 KB compat runtime mode は不要。
- Permission/API/component condition: native library / JNI / `.so` を含み、APK alignment または ELF LOAD segment alignment が 16 KB 非対応であること。`android:pageSizeCompat` は `<application>` manifest 属性。
- App state/process condition: app install / package scan、native library copy / extraction、app process start、activity launch warning dialog。

Compat framework:
- Change ID: 確認できない。
- Change name: N/A。
- Default state: N/A。
- Toggleable for testing: compat framework ではなく system property / manifest / Settings override 経路がある。

Aconfig / property:
- `android.content.pm.app_compat_option_16kb`: page-size compat mode の manifest / PackageManager / settings 経路を有効化する fixed read-only flag。
- `android.content.pm.app_compat_warnings_16kb`: alignment warning check に関係する fixed read-only flag。
- `bionic.linker.16kb.app_compat.enabled`: linker 側 16 KB app compat mode property。true の場合は warning dialog を出さない。
- `pm.16kb.app_compat.disabled`: PackageManager native library extraction 側の compat disabled property。

分類信頼度（Classification confidence）:
- High

分類根拠（Classification evidence）:
- Official documentation page: `behavior-changes-all` の `16 KB page size compatibility mode`。
- Original applicability statement: all apps ページは Android 16 上で実行される全アプリに適用される変更として掲載している。
- AOSP targetSdk gate: 見つからない。
- Compat framework entry: 公式 compat framework changes ページで `16KB` / `pageSizeCompat` に該当する Change ID は確認できない。

---

# エグゼクティブサマリー（Executive Summary）

Android 16 では、16 KB memory page size device 上で、4 KB page size 前提で作られた一部アプリを動かすための page-size compatibility mode が使われる。対象は主に native library / JNI / `.so` を含み、APK 内 uncompressed library または ELF LOAD segment が 16 KB alignment に対応していないアプリである。

この変更は targetSdkVersion 36 化の影響ではない。targetSdkVersion 35 のままでも、Android 16 の 16 KB device 上で実行されると、compat mode、native library extraction、warning dialog の対象になり得る。

`android:pageSizeCompat="enabled"` を Android 16 SDK で使うとアプリ単位で compat mode を明示でき、起動時 warning dialog を抑止できる。ただしこれは移行の代替ではなく、最終的には native dependencies を 16 KB aligned にすることが推奨される。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statement）

公式文書は以下を述べている。

- Android 15 は platform performance 最適化のため 16 KB memory pages をサポートした。
- Android 16 は compatibility mode を追加し、4 KB memory pages 向けに作られた一部アプリが 16 KB memory page device で動けるようにする。
- Android 16 以上の 16 KB device で、Android が 4 KB aligned memory pages を検出すると、自動的に compatibility mode を使い、user-facing notification dialog を表示する。
- `AndroidManifest.xml` で `android:pageSizeCompat` property を使って backwards compatibility mode を有効にすると、アプリ起動時の dialog 表示を防げる。
- `android:pageSizeCompat` property を使うには Android 16 SDK で compile する必要がある。
- performance / reliability / stability のため、アプリは引き続き 16 KB aligned にすべきである。

source.android.com の backcompat option 文書は、16 KB kernel で動作する device で backcompat option が利用でき、PackageManager は 4 KB LOAD segment alignment の ELF や 4 KB zip aligned の uncompressed ELF を持つアプリを 16 KB backcompat mode で実行すると説明している。また `bionic.linker.16kb.app_compat.enabled` と `pm.16kb.app_compat.disabled` の 2 つの property、`android:pageSizeCompat`、App info page の per-app setting に触れている。

## 公式本文との差分確認

調査開始時点で公式本文を再確認した。依頼に含まれる Original statements と公式本文は実質的に一致している。表現上は公式本文が "display a notification dialog" としており、ここでは user-facing warning / notification dialog として扱う。

## 解釈（Interpretation）

この項目は、16 KB page-size device で 4 KB 前提の native library を含むアプリを救済する互換機能である。影響の中心は targetSdkVersion 36 ではなく、OS が Android 16 以上であること、device が 16 KB page size であること、アプリまたは依存 native library が 16 KB alignment に対応していないことにある。

`android:pageSizeCompat` は「targetSdkVersion 36 にしたら自動的に必要になる設定」ではなく、Android 16 SDK で compile したときに manifest で指定できる属性である。compile SDK 条件と targetSdkVersion 条件は分けて説明する必要がある。

---

# 変更内容（What Changed）

## 変更点

- `R.attr.pageSizeCompat` が Android 16 current API surface で concrete resource ID 付きの public flagged API になった。
- `<application android:pageSizeCompat="enabled|disabled">` を PackageParser が読み取り、`ApplicationInfo` / parsed package / `PackageSetting` に page-size compat flags として保存する。
- PackageManager scan は 16 KB device または explicit alignment-check mode で native library alignment を検査し、APK 内 uncompressed library offset と ELF LOAD segment alignment の問題を flags と library list に記録する。
- app process start 時、`ProcessList` は 16 KB device かつ `PackageManager.isPageSizeCompatEnabled(package)` が true の場合、zygote runtime flag `ENABLE_PAGE_SIZE_APP_COMPAT` を設定する。
- zygote native code は `ENABLE_PAGE_SIZE_APP_COMPAT` を受けると `android_set_16kb_appcompat_mode(true)` を呼び、4 KB ELF を 16 KB device で読み込むための appcompat mode を有効にする。
- Activity launch 時、`AppWarnings` は `PackageManager.getPageSizeCompatWarningMessage()` が返す warning message を使って `PageSizeMismatchDialog` を表示する。manifest / settings / property による override で dialog が抑止される経路がある。

## 適用条件（Applicability）

### OS アップデート時の挙動（OS Update Behavior）

- Android 16 に OS アップデートしただけで適用されるか: Conditional Yes。
- targetSdkVersion に依存しない根拠: `ScanPackageUtils`、`PackageSetting.isPageSizeAppCompatEnabled()`、`ProcessList`、zygote native の該当経路は targetSdkVersion 36 を gate にしていない。
- Android 15 以前での挙動: Android 15 tag にも 16 KB support / backcompat の staging 実装は存在するが、公式 all apps behavior change は Android 16 の compatibility mode として説明している。Android 15 / targetSdkVersion 36 だけで Android 16 と同じ公開挙動になるとは扱わない。

### targetSdkVersion 36 以上での挙動（targetSdkVersion 36 Behavior）

- targetSdkVersion 36 以上で適用されるか: No。targetSdkVersion 36 は必要条件ではない。
- Android 16 以外で targetSdkVersion 36 にした場合の挙動: Android 15 platform 上では Android 16 の all apps behavior change としての扱いはない。16 KB support staging code がある場合でも、targetSdkVersion 36 そのものが gate ではない。
- opt-out / temporary override の有無: `android:pageSizeCompat="disabled"`、settings override disabled、`pm.16kb.app_compat.disabled=true` により compat mode を使わない方向にできる。ただし一般アプリの通常設定というより、manifest / system / settings 側の制御である。

### その他の条件（Other Conditions）

- Device condition: 16 KB page-size device。`Os.sysconf(_SC_PAGESIZE) == 16384` が複数箇所で使われる。
- API / packaging condition: `.so` を含むこと、uncompressed native library が 16 KB aligned でないこと、ELF LOAD segment `p_align == 0x1000` であること。
- Manifest condition: `android:pageSizeCompat="enabled"` は app-level override。`disabled` は compat mode を使わず失敗を明確にする用途がある。
- Compile SDK condition: `R.attr.pageSizeCompat` は Android 16 SDK の API surface で concrete ID 付きになっており、公式文書も Android 16 SDK で compile する必要を述べる。

---

# AOSP 調査（AOSP Investigation）

## 関連ファイル（Related Files）

- `frameworks-base/core/res/res/values/attrs_manifest.xml`
- `frameworks-base/core/api/current.txt`
- `frameworks-base/core/java/android/content/pm/flags.aconfig`
- `frameworks-base/core/java/android/content/pm/ApplicationInfo.java`
- `frameworks-base/core/java/com/android/internal/pm/pkg/parsing/ParsingPackageUtils.java`
- `frameworks-base/core/java/com/android/internal/pm/parsing/pkg/PackageImpl.java`
- `frameworks-base/core/java/com/android/internal/content/NativeLibraryHelper.java`
- `frameworks-base/core/jni/com_android_internal_content_NativeLibraryHelper.cpp`
- `frameworks-base/services/core/java/com/android/server/pm/ScanPackageUtils.java`
- `frameworks-base/services/core/java/com/android/server/pm/PackageAbiHelperImpl.java`
- `frameworks-base/services/core/java/com/android/server/pm/PackageSetting.java`
- `frameworks-base/services/core/java/com/android/server/pm/PackageManagerService.java`
- `frameworks-base/services/core/java/com/android/server/am/ProcessList.java`
- `frameworks-base/core/java/com/android/internal/os/Zygote.java`
- `frameworks-base/core/jni/com_android_internal_os_Zygote.cpp`
- `frameworks-base/services/core/java/com/android/server/wm/AppWarnings.java`
- `frameworks-base/services/core/java/com/android/server/wm/PageSizeMismatchDialog.java`

Checkout hygiene:
- `git -C frameworks-base status --short`: clean。
- `git -C frameworks-base tag --list android-15.0.0_r36`: tag exists。
- `git -C frameworks-base tag --list android-16.0.0_r4`: tag exists。
- evidence は working tree ではなく `git show android-16.0.0_r4:<path>` と `git diff android-15.0.0_r36 android-16.0.0_r4 -- <path>` を使って確認した。

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル（File / symbol） | Android 15 の基準挙動（baseline） | Android 16 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `attrs_manifest.xml` / `pageSizeCompat` | flagged attr として staging されている。 | attr comment が拡張され、4 KB / 16 KB system、enabled / disabled の意味、install specialization、linker special mode が説明される。 | manifest property の意味と `enabled` / `disabled` 値の根拠。 |
| `core/api/current.txt` / `R.attr.pageSizeCompat` | `@FlaggedApi` だが concrete resource ID がない。 | `pageSizeCompat = 16844459` として current API surface に現れる。 | Android 16 SDK compile requirement / API surface 差分の根拠。 |
| `ParsingPackageUtils.parseBaseApplication()` | flag enabled 時に `AndroidManifestApplication_pageSizeCompat` を読む staging code がある。 | `Flags.appCompatOption16kb()` 配下で manifest attr を読み、`pkg.setPageSizeAppCompatFlags()` に反映する。 | manifest property が parsed package に入る entry point。 |
| `PackageImpl` / `ApplicationInfo` | page-size compat flags を保持する。 | `PackageImpl` が `ApplicationInfo#setPageSizeAppCompatFlags()` に反映し、PackageSetting へも保存される。 | manifest / scan 結果が process start / warning 判定へ渡る根拠。 |
| `ScanPackageUtils` | 16 KB device 上で app compat option が有効な場合に alignment check を行う。 | 16 KB device または request alignment checks で alignment check を行い、upgrade 時に flags を clear して再評価する。 | package scan 時に 4 KB-aligned app / `.so` を検出する根拠。 |
| `NativeLibraryHelper.checkAlignmentForCompatMode()` | alignment check は int flags を返す。 | `AlignmentResult` と library list を返し、uncompressed library offset と ELF LOAD segment alignment を記録する。 | APK / ELF alignment detection path の根拠。 |
| `com_android_internal_content_NativeLibraryHelper.cpp` / `app_compat_16kb_enabled()` | 16 KB page-size device で `pm.16kb.app_compat.disabled=false` なら fallback extraction 可能。 | 同様に 16 KB device のみで有効。さらに `pageSizeCompat=disabled` の場合は非 aligned library を抽出せず install failure にする。 | native library install / extraction behavior の直接根拠。 |
| `PackageSetting.isPageSizeAppCompatEnabled()` | flags に基づき compat enabled を返す。 | manifest/settings disabled を優先して false にし、ELF_NOT_ALIGNED / manifest enabled / settings enabled のいずれかで true を返す。 | process start 時に compat mode が必要か決める PackageManager 状態。 |
| `ProcessList` / runtime flags | app process start 時に runtime flags を構築する。 | 16 KB device かつ `isPageSizeCompatEnabled()` true の場合、`Zygote.ENABLE_PAGE_SIZE_APP_COMPAT` を立てる。 | app process が compat mode で起動するかの根拠。 |
| `Zygote.java` / `ENABLE_PAGE_SIZE_APP_COMPAT` | 4 KB ELF を 16 KB device で appcompat mode にする runtime flag を定義。 | 同 flag が `1 << 26` として定義される。 | Java runtime flag と native zygote の対応根拠。 |
| `com_android_internal_os_Zygote.cpp` | zygote child specialization で runtime flags を処理する。 | `ENABLE_PAGE_SIZE_APP_COMPAT` があると `android_set_16kb_appcompat_mode(true)` を呼ぶ。 | compatibility mode の実体が zygote / bionic 側へ渡る根拠。 |
| `PackageSetting.getPageSizeCompatWarningMessage()` | warning string を返す。 | settings override enabled / disabled の場合は null。alignment flags から APK / ELF warning と library detail を生成する。 | dialog 表示条件と抑止条件の根拠。 |
| `AppWarnings.showPageSizeMismatchDialogIfNeeded()` | Android 15 では 16 KB device の場合に dialog path へ進む。 | Android 16 r4 では `bionic.linker.16kb.app_compat.enabled=true` の場合に return し、それ以外は warning message が non-null なら dialog path へ進む。 | user-facing warning dialog の trigger。 |
| `PageSizeMismatchDialog` | warning dialog を表示する。 | `Do not show again` / OK、link clickable、title `Android App Compatibility` を持つ overlay dialog を表示する。 | 公式の notification dialog / compatibility dialog の実装根拠。 |

必須記入項目（Required context）:
- Entry point / caller: APK install / scan -> `ScanPackageUtils` -> `NativeLibraryHelper` alignment check -> `PackageSetting` flags; app process start -> `ProcessList` -> zygote runtime flag -> `android_set_16kb_appcompat_mode(true)`; activity launch -> `AppWarnings` -> `PageSizeMismatchDialog`。
- Relevant class or service responsibility: PackageManager は alignment と per-package flags を管理し、ActivityManager / zygote は app process の runtime mode を決め、WindowManager は user-facing warning を表示する。
- Runtime path from app API / system event to changed code: app install / update、activity launch、process start が主な発火点。アプリコードが直接 API を呼ぶ必要はない。
- Why unrelated code paths were excluded: SQLite page size、printer page size、MTE / memtag、general memory safety flags は本件の 16 KB page-size native library compatibility mode とは別の機能であるため除外した。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
| Android 16 `current.txt` で `R.attr.pageSizeCompat = 16844459` が concrete ID 付きになる。 | API surface / SDK availability の変更。 | Android 16 SDK で compile する必要があるという公式文書と整合する。 | High |
| Android 16 `attrs_manifest.xml` の `pageSizeCompat` doc が、4 KB system では無視、16 KB system かつ 4 KB-built app に影響、enabled / disabled の用途を説明する。 | Manifest attribute semantics の明確化。 | `android:pageSizeCompat` が dialog suppression だけでなく compat mode control として扱われる根拠。 | High |
| `ScanPackageUtils` が 16 KB device / explicit alignment checks で native library alignment を確認し、manifest override を優先しつつ platform detection flags も保存する。 | Added / changed condition。 | 4 KB-aligned app を自動検出して compat mode / warning につなげる根拠。 | High |
| `NativeLibraryHelper` が uncompressed library offset と ELF LOAD segment alignment を確認する。 | Added / refined behavior。 | 4 KB aligned memory pages / ELF を検出する具体的な経路。 | High |
| `ProcessList` が `isPageSizeCompatEnabled()` に基づいて zygote runtime flag を立て、zygote native が `android_set_16kb_appcompat_mode(true)` を呼ぶ。 | Added behavior / runtime mode activation。 | compatibility mode の実体が app process 起動時に有効化される根拠。 | High |
| `PackageSetting.getPageSizeCompatWarningMessage()` が settings override の場合 null を返す。 | Changed condition / dialog suppression。 | override 時に dialog が表示されない根拠。ただし manifest override enabled の warning 抑止は `isPageSizeCompatEnabled()` と dialog class comment / source doc も合わせて解釈する。 | Medium |
| Android 15 tag にも staging 実装がある。 | Baseline nuance。 | 公式文書の「Android 16 adds」は SDK/API と公開挙動の説明として扱う。tag 差分のみでは Android 15 製品上の全挙動を単純に否定しない。 | Medium |

必須分類（Required interpretation）:
- Added behavior: Android 16 public API surface として `R.attr.pageSizeCompat` が concrete ID 付きになる。zygote runtime flag / PackageManager state / warning dialog が統合される。
- Changed condition: Android 16 r4 では alignment warnings 用 flag、alignment detail collection、upgrade 時再評価、`pageSizeCompat=disabled` の install failure path が追加 / 強化される。
- Changed default: targetSdkVersion 36 での default change は見つからない。device / feature flag / system property / package alignment が実質条件。
- No behavior change found: targetSdkVersion 36 gate は見つからない。compat framework Change ID も確認できない。

---

# Facts / Observations / Hypotheses / Conclusions

## Facts

- 公式 all apps ページは Android 16 の 16 KB page size compatibility mode を全アプリ向け Behavior Change として掲載している。
- source.android.com は 16 KB kernel/device で backcompat option が利用でき、PackageManager が 4 KB LOAD segment alignment または 4 KB zip aligned uncompressed ELF を持つアプリを backcompat mode で動かすと説明している。
- AOSP `android-16.0.0_r4` では `R.attr.pageSizeCompat` が `@FlaggedApi("android.content.pm.app_compat_option_16kb")` かつ concrete ID `16844459` として current API surface にある。
- `ProcessList` は targetSdkVersion ではなく、16 KB device と `isPageSizeCompatEnabled()` に基づいて `Zygote.ENABLE_PAGE_SIZE_APP_COMPAT` を設定する。
- zygote native code は `ENABLE_PAGE_SIZE_APP_COMPAT` により `android_set_16kb_appcompat_mode(true)` を呼ぶ。
- `NativeLibraryHelper` は 16 KB alignment に合わない APK 内 uncompressed library offset と ELF LOAD segment `p_align == 0x1000` を検出する。
- 公式 compat framework changes ページには本件の Change ID は確認できない。

## Observations

- Android 15 tag にも `pageSizeCompat` や PageSizeMismatchDialog の staging code は存在する。ただし Android 16 tag では public API ID、warning detail、alignment check request、settings / manifest override の扱いがより明確になっている。
- `android:pageSizeCompat="enabled"` は「compat mode を明示的に使う」方向であり、source.android.com はこの property が設定されると launch warning が表示されないと説明する。
- `android:pageSizeCompat="disabled"` は 16 KB 対応済みであることを前提に、compat mode を使わず regression を明確な failure として検出する用途がある。
- app に native code がなければ alignment check の実質的な影響は低い。

## Hypotheses

- OEM device では 16 KB page-size device の採用有無、Settings UI の表示、launcher / dialog 表示 timing に差が出る可能性がある。ただし AOSP の主要 gate は 16 KB page size と package alignment である。
- `android-16.0.0_r4` は Android 16 base tag であり、今後の QPR / branch で 16 KB warning UX や settings UI がさらに変わる可能性がある。
- Android 15 製品 build に staging code が含まれていても、公式に説明される Android 16 compatibility mode と同じ公開 SDK / UX として利用できるとは限らない。

## Conclusions

- 主分類は `OS_UPDATE_ALL_APPS`。ただし影響は 16 KB page-size device と native library alignment に強く条件付けられる。
- targetSdkVersion 36 化だけで発生する変更ではない。Android 16 / targetSdkVersion 35 のままでも影響し得る。
- `android:pageSizeCompat` を使うには Android 16 SDK で compile する必要があるが、これは targetSdkVersion 36 gate ではなく compile SDK / API surface availability の問題である。
- compatibility mode は移行支援であり、長期的な対応は native dependencies を 16 KB aligned に rebuild / update することである。

---

# 期待挙動マトリクス（Expected Behavior Matrix）

## OS / targetSdkVersion 別

| シナリオ | 期待挙動 |
| --- | --- |
| Android 16 / targetSdkVersion 35 | 16 KB device かつ 4 KB-aligned native library 条件を満たすと compat mode / warning dialog 対象になり得る。targetSdkVersion 36 は不要。 |
| Android 16 / targetSdkVersion 36 | targetSdkVersion 35 と同じ OS 側条件。targetSdkVersion 36 化だけで追加 gate はない。 |
| Android 15 / targetSdkVersion 36 | Android 16 all apps behavior としては適用されない。AOSP tag に staging code はあるが、Android 16 と同じ公開挙動とは断定しない。 |

## 詳細シナリオ別

| シナリオ | 期待挙動 |
| --- | --- |
| Android 16 / targetSdkVersion 35 / 16 KB page-size device / 4 KB-aligned app | compat mode が有効化され得る。warning dialog が表示され得る。 |
| Android 16 / targetSdkVersion 36 / 16 KB page-size device / 4 KB-aligned app | 同上。targetSdkVersion 36 固有ではない。 |
| Android 16 / targetSdkVersion 35 / 16 KB page-size device / 16 KB-aligned app | compat mode / warning は不要。 |
| Android 16 / targetSdkVersion 36 / 16 KB page-size device / 16 KB-aligned app | compat mode / warning は不要。 |
| Android 16 / 4 KB page-size device / 4 KB-aligned app | app launch の 16 KB compat mode は不要。debug / alignment warning check は別条件で発生し得る。 |
| Android 16 / 4 KB page-size device / 16 KB-aligned app | 16 KB compat mode の実質影響なし。 |
| Android 16 / `android:pageSizeCompat` declared true | app 単位で compat mode を明示する。source doc 上、launch warning を表示しない。 |
| Android 16 / `android:pageSizeCompat` absent | platform が alignment を検出して compat flags を設定する。必要なら warning dialog が出る。 |
| Android 16 / compileSdkVersion 36 / `android:pageSizeCompat` | `R.attr.pageSizeCompat` を使える。 |
| Android 16 / compileSdkVersion 35 or lower / no manifest property availability | manifest property を通常の SDK API として使えない。targetSdkVersion とは別問題。 |
| Android 16 / automatic compatibility mode enabled | `ProcessList` が zygote runtime flag を立て、zygote が appcompat mode を有効化する。 |
| Android 16 / compatibility dialog displayed | `PackageManager.getPageSizeCompatWarningMessage()` が non-null で、hide flag がない場合に表示。 |
| Android 16 / compatibility dialog suppressed by manifest property | `android:pageSizeCompat="enabled"` を使うと公式 doc / source doc 上 dialog は表示されない。 |
| Android 16 / app with native `.so` dependencies | native dependency の alignment が影響条件になる。 |
| Android 16 / app with no native code | 基本的に影響低。 |
| Android 16 / third-party SDK native library not 16 KB aligned | app 全体が compat mode / warning 対象になり得る。 |
| Android 16 / all native libraries rebuilt for 16 KB | compat mode 不要。性能 / reliability / stability 上望ましい。 |
| Android 15 / targetSdkVersion 36 / 16 KB page-size device | Android 16 公式挙動としては扱わない。device / build 固有 staging behavior は実機確認が必要。 |
| Android 15 / targetSdkVersion 36 / no Android 16 compatibility mode | targetSdkVersion 36 だけでは Android 16 mode は発生しない。 |
| app migrates from compatibility mode to full 16 KB alignment | warning / compat dependency が解消される。 |
| app relies on compatibility mode long term | performance / reliability / stability の懸念が残る。 |

---

# 開発者影響（Developer Impact）

## 影響対象

- native code / JNI を含むアプリ。
- NDK を使うアプリ。
- `.so` ファイルを含むアプリ。
- third-party native SDK を含むアプリ。
- game engine / rendering engine を使うアプリ。
- media / audio / video / camera native pipeline を持つアプリ。
- database / storage / compression / crypto native library を含むアプリ。
- ML / inference runtime を含むアプリ。
- browser / WebView extension / custom loader / plugin framework を含むアプリ。
- 4 KB page-size assumption を持つ native code。
- 16 KB page-size device に配布されるアプリ。
- `android:pageSizeCompat` を一時 mitigation として使うアプリ。
- 16 KB alignment 対応済みアプリ。
- Java / Kotlin only で native code を含まないアプリ。

## 顧客向け説明で混ぜてはいけない点

- Android 16 OS update impact: 16 KB page-size device かつ 4 KB-aligned native library 条件で発生し得る。
- targetSdkVersion 36 impact: 本件では主要 gate ではない。
- compileSdkVersion 36 impact: `android:pageSizeCompat` を使うための SDK/API availability 条件。
- 16 KB device condition: 4 KB page-size device では app launch compat mode の実質影響はない。
- dialog suppression: `android:pageSizeCompat="enabled"` は dialog を抑止するが、16 KB alignment 対応を完了したことを意味しない。
- long-term migration: compatibility mode は救済策であり、best performance / reliability / stability には 16 KB alignment が必要。

## 推奨対応候補

- APK / AAB 内の native libraries を棚卸しし、16 KB alignment に対応しているか確認する。
- third-party native SDK / game engine / ML runtime / database / crypto library を最新化する。
- Android 16 SDK で compile し、必要に応じて `android:pageSizeCompat="enabled"` を一時 mitigation として使う。
- 16 KB page-size device で app startup、native library load、JNI initialization、dynamic loading をテストする。
- compatibility mode で動くことだけを release readiness とせず、16 KB aligned build へ移行する。

---

# テスト観点（Testing Guidance）

| 観点 | 確認内容 |
| --- | --- |
| Android 15 端末上の targetSdkVersion 35 | baseline。16 KB compat mode の Android 16 影響と分ける。 |
| Android 16 端末上の targetSdkVersion 35 | OS update impact を確認。 |
| Android 16 端末上の targetSdkVersion 36 | targetSdkVersion 35 と差がないことを確認。 |
| Android 15 端末上の targetSdkVersion 36 | targetSdkVersion 36 だけでは本件が発生しないことを比較。 |
| 16 KB page-size device | `getconf PAGE_SIZE` などで device page size を記録。 |
| 4 KB page-size device | non-impact / debug alignment warning の有無を比較。 |
| APK / AAB 内 `.so` alignment | uncompressed library offset、ELF LOAD segment `p_align` を確認。 |
| app startup | warning dialog、startup crash、compat mode の有無を確認。 |
| native library load | `UnsatisfiedLinkError`、linker error、native crash を確認。 |
| JNI initialization | 依存 native library の初期化成功 / failure を確認。 |
| dynamic loading / plugin loading | `System.loadLibrary` 以外の loader 経路も確認。 |
| memory mapping / mmap behavior | page-size assumption を持つ native code を確認。 |
| compatibility mode が有効になる条件 | PackageManager flags、process runtime flag、system property を確認。 |
| compatibility dialog / notification | 表示有無、文言、Do not show again、リンク挙動を確認。 |
| `android:pageSizeCompat` declared / absent | dialog suppression と compat mode を分けて確認。 |
| Android 16 SDK compile | manifest property が build / install 可能か確認。 |
| compileSdkVersion 35 以下 | property が使えない場合の build failure / ignore を確認。 |
| all native dependencies rebuilt | warning / compat mode が不要になることを確認。 |
| third-party native SDK update | update 前後の alignment / startup を比較。 |
| performance / reliability / stability | compatibility mode と full 16 KB alignment build を比較。 |

---

# Evidence Gaps / 注意点

- bionic / linker の `android_set_16kb_appcompat_mode` 実体は `frameworks-base` から呼び出しまで確認した。本調査では `platform/bionic` tag checkout までは取得していないため、bionic 内部の詳細は source.android.com と call site evidence に基づく。
- Android 15 tag に staging code が存在するため、「Android 15 に一切存在しない機能が Android 16 で初めて追加された」とは書かない。公式文書の Android 16 statement と API surface / public behavior の差分を重視する。
- OEM / device ごとの 16 KB page-size 採用状況と Settings UI 表示は実機確認が必要。

---

# 最終結論（Conclusion）

`16 KB page size compatibility mode` は、Android 16 の all apps behavior change として扱う。targetSdkVersion 36 化ではなく、Android 16 以上の 16 KB page-size device で、native libraries が 16 KB alignment に対応していない場合に影響する。

`android:pageSizeCompat` は Android 16 SDK で compile したアプリが使える manifest property であり、compat mode の明示と warning dialog 抑止に使える。ただし最終対応は 16 KB aligned native library への移行である。

## Human Decision placeholder

最終優先度（Final Priority）:
- Critical / High / Medium / Low

判断（Decision）:
- Explain / Monitor / Ignore / Further investigation required

補足:
- 最終優先度、顧客通知要否、release readiness は repository owner が判断する。

---

## 再検証記録（2026-08-22）

### 調査日（Investigation Date）

- 2026-08-22

### 公式ドキュメント再確認（Original Documentation Recheck）

- Android 16 の all-apps / target Behavior Change ページを再取得し、このレポートが参照する公式 section の掲載と適用範囲を再確認した。
- 公式ページの最終更新表示: all-apps: 2026-08-14 UTC / target: 2026-08-17 UTC。
- Android 16 compat framework 一覧も 2026-08-22 に再取得した。
- 既存の引用は短い要約として扱い、適用条件は公式ページ種別と AOSP gate の両方で再評価した。

### AOSP 証拠ワークスペース（AOSP Evidence Workspaces）

| AOSP project | Official remote URL | Checkout path | Working tree | From tag / resolved commit | To tag / resolved commit | Comparison command | Dirty risk / limitations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `platform/frameworks/base` | `https://android.googlesource.com/platform/frameworks/base` | `frameworks-base/` | Clean | `android-15.0.0_r36` / `396d32905ded85c082232bc510b525c9e372e585` | `android-16.0.0_r4` / `45034f0663f960d9ee5fb0a101a4732b71f6e2f4` | `git -C frameworks-base diff --no-renames --name-only android-15.0.0_r36 android-16.0.0_r4` | なし。明示タグ比較のため working tree の内容は根拠に含めない。 |

### ソース文脈・差分解釈の再確認（Source Context Reviewed / Diff Interpretation）

- 各 official remote で Android 15 / 16 の最新通常リリースタグが `android-15.0.0_r36` / `android-16.0.0_r4` のままであることを確認した。
- 上表の project-level `--name-only` 比較を再実行し、既存本文の path / symbol 別 source context、gate、追加・削除・条件変更・既定値変更・差分なしの解釈を再確認した。
- タグと解決済み commit が既存調査の比較対象から変わっていないため、本文の evidence record を別タグへ機械的に置換していない。
- 実機 Observed は新規実施していない。既存の「未実施」「未確認」および不足根拠はそのまま維持した。

### 事実（Facts）

- `android-15.0.0_r36` と `android-16.0.0_r4` は 2026-08-22 時点の最新通常リリースタグである。
- 上表に再検証時の working tree 状態を記録し、official remote、両タグ、解決済み commit を確認した。展開中または dirty の working tree は根拠に使用していない。
- 公式 section と AOSP evidence の比較 pair は一致している。

### 観察（Observations）

- 最新タグが変わっていないため、今回の再検証で既存の source diff 解釈を変更する新しい AOSP tag evidence は生じなかった。
- report 内に残る Medium / Low confidence、OEM / Mainline / QPR 条件、未確認の module enforcement は解消したものとして扱わない。

### 仮説（Hypotheses）

- 新しい仮説は追加しない。既存本文で仮説または可能性として記載した事項は、実機・製品 build・未確認 module の evidence が得られるまで事実へ昇格しない。

### 結論（Conclusions）

- 既存本文の主分類、confidence、対応候補を維持する。既存の不足根拠がある場合はその制約も維持する。
- 全件再検証の横断記録は [`android16/analysis/REVALIDATION_2026-08-22.md`](../../../analysis/REVALIDATION_2026-08-22.md) を参照する。

### Human Decision

- この再検証では最終 priority、severity、release readiness、顧客説明優先度を変更していない。
- 人間の判断は [Android 16 Decision Log](../../../decisions/DECISION_LOG.md) を正とする。

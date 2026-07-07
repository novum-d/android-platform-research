# 16 KB page size compatibility mode - 1ページ要約（One Page Summary）

## 対象（Target）

Android 16 Behavior Change:
- 16 KB page size compatibility mode

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:
- `android16/AGENTS.md` は To tag を `android-16.0.0_r1` としているが、本調査では依頼スコープに従い `android-16.0.0_r4` を使用。

## 適用条件（Applicability）

- 主分類（Primary classification）: `OS_UPDATE_ALL_APPS`
- Android 16 OS update: Conditional Yes。16 KB page-size device かつ 4 KB-aligned native library / ELF 条件を満たす場合に影響し得る。
- targetSdkVersion 36 以上: No。本件の主要 gate ではない。
- その他の必須条件（Other required conditions）: native `.so` / JNI / third-party native SDK を含み、16 KB alignment に対応していないこと。4 KB page-size device では app launch compat mode は不要。
- Compat Change ID: 確認できない。
- Compat default state: N/A。AOSP aconfig flag `app_compat_option_16kb` / system properties / manifest / settings override が関係する。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 16 / targetSdkVersion 35 / 16 KB device / 4 KB-aligned native libs | 影響あり。compat mode / warning dialog 対象になり得る。 |
| Android 16 / targetSdkVersion 36 / 16 KB device / 4 KB-aligned native libs | targetSdkVersion 35 と同じ。targetSdk 36 固有ではない。 |
| Android 16 / 16 KB device / 16 KB-aligned native libs | 原則影響なし。compat mode 不要。 |
| Android 16 / 4 KB page-size device | 16 KB compat mode の実質影響なし。 |
| Android 16 / `android:pageSizeCompat="enabled"` | compat mode を明示し、公式 doc 上 warning dialog を抑止。 |
| Android 16 / `android:pageSizeCompat="disabled"` | compat mode を使わず、alignment 問題を失敗として検出しやすい。 |
| Android 16 / compileSdkVersion 36 | `R.attr.pageSizeCompat` を使える。 |
| Android 16 / compileSdkVersion 35 以下 | manifest property の通常利用は不可。targetSdkVersion とは別条件。 |
| Android 15 / targetSdkVersion 36 | Android 16 all apps behavior としては扱わない。 |

## 要約（Summary）

Android 16 は、16 KB page-size device 上で 4 KB page-size 前提の一部アプリを動かす compatibility mode を提供する。対象は主に native library / JNI / third-party `.so` を含むアプリで、targetSdkVersion 36 化ではなく OS / device / native alignment 条件で発生する。

## 顧客影響（Customer Impact）

- 影響あり / 要確認。
- Java / Kotlin only で native code がないアプリは低リスク。
- native dependencies を持つアプリは、16 KB device で warning dialog、compat mode、startup / linker / native crash を確認する必要がある。
- `android:pageSizeCompat` は一時 mitigation として使えるが、長期的には 16 KB aligned build が必要。

## 影響対象（Who Is Affected）

- native code / JNI を含むアプリ。
- NDK / `.so` / third-party native SDK を含むアプリ。
- game engine、rendering engine、media engine、ML runtime、database、crypto、compression、custom native loader を使うアプリ。
- 16 KB page-size device に配布されるアプリ。
- `android:pageSizeCompat` で warning dialog 抑止を検討するアプリ。
- 16 KB alignment 済みか未確認の native dependency を持つアプリ。

## 対応要否（Required Action）

- 必須対応: APK / AAB 内 native library の 16 KB alignment を確認する。
- 推奨対応: third-party native SDK を 16 KB 対応版へ更新する。
- 推奨対応: Android 16 SDK で compile し、必要に応じて `android:pageSizeCompat="enabled"` を一時 mitigation として使う。
- 推奨対応: compatibility mode と full 16 KB aligned build の startup / performance / crash 差を比較する。
- 不要: native code を含まないアプリは通常の regression test で十分。

## テストマトリクス（Test Matrix）

| 端末 OS / device | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 15 / 4 KB device | 35 | baseline。Android 16 compat mode impact なし。 |
| Android 16 / 16 KB device | 35 | 4 KB-aligned native libs があれば compat mode / dialog 対象。 |
| Android 16 / 16 KB device | 36 | targetSdkVersion 35 と同じ。 |
| Android 15 / 16 KB device if available | 36 | Android 16 公式挙動とは分けて実機確認。 |

追加テスト:

| 観点 | 確認内容 |
| --- | --- |
| device page size | `getconf PAGE_SIZE` 等で 4 KB / 16 KB を記録。 |
| native `.so` alignment | APK offset と ELF LOAD segment alignment を確認。 |
| app startup | warning dialog、linker error、native crash を確認。 |
| `android:pageSizeCompat` | declared / absent / enabled / disabled の挙動差を確認。 |
| compileSdkVersion | 36 で property を使えること、35 以下では使えないことを確認。 |
| third-party native SDK | SDK update 前後で warning / crash が減るか確認。 |
| performance / reliability | compat mode と full 16 KB aligned build を比較。 |

## 顧客向け説明（Explanation for Customers）

この変更は targetSdkVersion 36 に上げた時だけの変更ではありません。Android 16 以上の 16 KB page-size device で、アプリまたは依存 native library が 4 KB alignment 前提のままだと、OS が compatibility mode を使い、起動時に warning dialog を表示する可能性があります。

`android:pageSizeCompat="enabled"` を Android 16 SDK で使うと dialog を抑止できますが、これは移行猶予のための互換設定です。最終的には native libraries を 16 KB aligned に rebuild / update してください。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/16/behavior-changes-all#16-kb-compatibility-mode
- AOSP docs: https://source.android.com/docs/core/architecture/16kb-page-size/16kb-backcompat-option
- AOSP files:
  - `frameworks-base/core/res/res/values/attrs_manifest.xml`
  - `frameworks-base/core/api/current.txt`
  - `frameworks-base/core/java/android/content/pm/flags.aconfig`
  - `frameworks-base/core/java/com/android/internal/pm/pkg/parsing/ParsingPackageUtils.java`
  - `frameworks-base/core/java/com/android/internal/content/NativeLibraryHelper.java`
  - `frameworks-base/core/jni/com_android_internal_content_NativeLibraryHelper.cpp`
  - `frameworks-base/services/core/java/com/android/server/pm/ScanPackageUtils.java`
  - `frameworks-base/services/core/java/com/android/server/pm/PackageSetting.java`
  - `frameworks-base/services/core/java/com/android/server/am/ProcessList.java`
  - `frameworks-base/core/jni/com_android_internal_os_Zygote.cpp`
  - `frameworks-base/services/core/java/com/android/server/wm/AppWarnings.java`
  - `frameworks-base/services/core/java/com/android/server/wm/PageSizeMismatchDialog.java`
- AOSP source context:
  - Package scan で alignment flags を保存。
  - app process start で zygote runtime flag を設定。
  - zygote native が `android_set_16kb_appcompat_mode(true)` を呼ぶ。
  - activity launch で warning dialog を表示。
- Diff interpretation:
  - Android 16 SDK/API surface で `R.attr.pageSizeCompat` が concrete ID 付きになる。
  - targetSdkVersion 36 gate は見つからない。
- Gate conclusion:
  - Android 16 以上、16 KB page-size device、native library alignment 条件が主 gate。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Critical / High / Medium / Low

判断（Decision）:
- Explain / Monitor / Ignore / Further investigation required

補足:
- 最終優先度、顧客通知要否、release readiness は repository owner が判断する。

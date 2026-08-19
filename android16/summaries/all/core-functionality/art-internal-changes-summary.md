# ART internal changes - 1ページ要約（One Page Summary）

## 対象（Target）

Android 16 Behavior Change:
- ART internal changes

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:

## 適用条件（Applicability）

- 主分類（Primary classification）: `MAINLINE_OR_PLAY_SYSTEM_UPDATE`
- Android 16 OS update: Yes。Android 16 platform image は updated ART を含む。
- targetSdkVersion 36 以上: No。本項目全体に targetSdkVersion 36 gate は見つからない。
- Android 12+ / Google Play System Update: Yes。ART module update により Android 16 以外でも影響し得る。
- その他の必須条件（Other required conditions）: app code / library / SDK が ART internals、non-SDK interfaces、hidden API、unsupported reflection / JNI / runtime assumptions に依存すること。
- Compat Change ID: 本 Behavior Change 全体の toggleable compat Change ID は確認できない。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 16 / targetSdkVersion 35 / public API only | 原則低リスク。通常 regression test は必要。 |
| Android 16 / targetSdkVersion 36 / public API only | 原則低リスク。targetSdk 36 固有ではない。 |
| Android 16 / ART internals 使用 | 影響あり得る。 |
| Android 16 / hidden API reflection | warning / deny / crash / linkage error の可能性。 |
| Android 16 / JNI runtime assumptions | JNI lookup failure / native crash の可能性。 |
| Android 16 / hooking / hotfix / instrumentation SDK | 高リスク。 |
| Android 12+ / updated ART Mainline module | Android 16 以外でも同種の影響があり得る。 |
| targetSdkVersion 36 化のみ / ART module change なし | 本項目単独の主要リスクは増えない。 |
| ART module update / targetSdkVersion change なし | 本項目の互換性リスクが発生し得る。 |

## 要約（Summary）

Android 16 には ART の最新更新が含まれる。ART は Mainline / Google Play System Update でも配信されるため、この変更は Android 16 platform image だけに閉じない。ART internals に依存する app / library は Android 16 または Android 12+ の updated ART module で動作不良になる可能性がある。

## 顧客影響（Customer Impact）

- 影響あり / 要確認。
- public API のみを使うアプリは低リスク。
- hidden API、non-SDK、JNI runtime internals、bytecode instrumentation、hooking、hotfix、anti-tamper、profiling / monitoring SDK を含む場合は重点確認が必要。
- targetSdkVersion 36 化の影響ではなく、Android 16 OS update と ART Mainline update の影響として説明する。

## 影響対象（Who Is Affected）

- ART internals に依存するアプリ。
- non-SDK interfaces / hidden API reflection を使うアプリ。
- JNI / native code で runtime internals を前提にするアプリ。
- bytecode weaving / instrumentation / hooking / hotfix framework を使うアプリ。
- plugin / dynamic loading framework を使うアプリ。
- obfuscation / anti-tamper / anti-cheat SDK を使うアプリ。
- crash reporting / profiling / tracing / monitoring SDK を使うアプリ。
- known issues に掲載された HiddenApiBypass / FlyCore before `v2025.0224.1629` を含むアプリ。
- Android 12+ の ART Mainline update 影響を受け得るアプリ。

## 対応要否（Required Action）

- 必須対応: ART internals / hidden API / non-SDK / runtime assumptions を使う code / dependency を棚卸しする。
- 推奨対応: Android 16 と Android 12+ updated ART module device の両方で regression test を行う。
- 推奨対応: hidden API warning、StrictMode signal、`NoSuchMethodError`、`IllegalAccessError`、`ClassNotFoundException`、JNI failure、native crash をログ化する。
- 推奨対応: public API alternative へ移行し、不足 API は feature request として報告する。
- 不要: public API のみで ART internals に依存しないアプリは通常 regression test で十分。

## テストマトリクス（Test Matrix）

| 端末 / module 状態 | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 15 / ART module 未更新 | 35 | baseline。Android 16 ART update は適用されない。 |
| Android 16 | 35 | ART update が適用される。OS update impact を確認。 |
| Android 16 | 36 | targetSdkVersion 35 と同じ ART update risk。 |
| Android 15 / ART module 未更新 | 36 | targetSdkVersion 36 だけでは本項目の主要 risk は発生しない。 |
| Android 12+ / updated ART module | 任意 | Android 16 以外でも ART Mainline impact を確認。 |

追加テスト:

| 観点 | 期待確認 |
| --- | --- |
| ART APEX / module version | OS version と別に記録。 |
| app startup / class loading | startup crash / `ClassNotFoundException` を確認。 |
| reflection / hidden API | warning / deny / `IllegalAccessError` を確認。 |
| JNI calls | `GetMethodID` / `GetFieldID` failure、native crash を確認。 |
| dynamic code loading / bytecode instrumentation | verifier / class loading / linkage error を確認。 |
| hooking / hotfix / anti-tamper SDK | SDK 初期化と主要 flow を確認。 |
| crash reporting / profiling / monitoring SDK | runtime internal access がないか確認。 |
| known issues libraries | HiddenApiBypass / FlyCore version を確認。 |
| dependency update before / after | update で crash / warning が解消するか確認。 |

## 顧客向け説明（Explanation for Customers）

Android 16 の ART 更新は、targetSdkVersion 36 に上げた時だけの変更ではありません。targetSdkVersion 35 のままでも、ART internals に依存する app / library は Android 16 端末で影響を受ける可能性があります。

さらに ART は Google Play System Update で Android 12 以上にも配信されるため、Android 16 以外の端末でも ART module update による影響があり得ます。OS version だけでなく ART APEX / module version を記録して検証してください。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/16/behavior-changes-all#art-changes
- AOSP ART module doc: https://source.android.com/docs/core/ota/modular-system/art
- AOSP files:
  - `platform/art/build/README.md`
  - `platform/art/build/apex/Android.bp`
  - `platform/art/build/boot/Android.bp`
  - `platform/art/runtime/hidden_api.cc`
  - `platform/art/libartbase/base/hiddenapi_flags.h`
  - `platform/libcore/api/current.txt`
- Known issues:
  - HiddenApiBypass (`org.lsposed.hiddenapibypass:hiddenapibypass`)
  - FlyCore (`cn.fly:FlyCore`) before `v2025.0224.1629`
- Gate conclusion:
  - targetSdkVersion 36 gate なし。
  - Android 16 OS update と Android 12+ ART Mainline update を分けて扱う。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Critical / High / Medium / Low

判断（Decision）:
- Explain / Monitor / Ignore / Further investigation required

補足:
- 最終優先度、顧客通知要否、release readiness は repository owner が判断する。

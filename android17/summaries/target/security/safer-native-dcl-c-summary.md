# Safer Native DCL-C - 1ページ要約（One Page Summary）

## 対象（Target）

Android 17 Behavior Change

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP tag

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

## 適用条件（Applicability）

- 主分類（Primary classification）: UNKNOWN_NEEDS_MORE_EVIDENCE
- OS アップデート / 全アプリ（OS update / all apps）: Unknown。原文は targetSdkVersion 37+ を明示しているが、AOSP gate 未確認。
- targetSdkVersion 37 以上: 公式文書上は該当。AOSP gate 未確認。
- その他の必須条件（Other required conditions）: `System.load()`、native file dynamic loading、native file が read-only として mark されていること。
- Compat Change ID: Unknown
- Compat default state: Unknown

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | Unknown。この section は targetSdkVersion 37+ 向けだが、AOSP gate 未確認。 |
| Android 17 / targetSdkVersion 37 | 公式文書上、`System.load()` で読み込む native files は read-only 必須。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | native file が read-only でない場合、`UnsatisfiedLinkError` が発生する。 |

## 要約（Summary）

Android 17 では、targetSdkVersion 37 以上のアプリで Safer DCL protection が native libraries に拡張され、`System.load()` で読み込む native files は read-only 必須になる、と公式文書は説明している。

## 顧客影響（Customer Impact）

- 要確認

## 影響対象（Who Is Affected）

- 対象アプリ: 実行時に `.so` などの native library をダウンロード、生成、展開、更新してから `System.load()` するアプリ。
- 対象機能: plugin、hotfix、feature module、ML / game engine / media engine、dynamic native component。
- 対象条件: targetSdkVersion 37 以上、`System.load()`、read-only ではない native file。

## 対応要否（Required Action）

- 必須対応: `System.load()` の利用箇所と native file の permission / 保存先 / 生成元を棚卸しする。
- 推奨対応: dynamic native code loading を避け、必要な場合は書き込み完了後に native file を read-only として mark してから load する。
- 不要: dynamic native library loading を行わないアプリでは直接影響は限定的。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 16 | 36 | Android 16 baseline。具体挙動は Android 17 tag 比較待ち。 |
| Android 17 | 36 | Unknown。この section は targetSdkVersion 37+ 向けだが、AOSP gate 未確認。 |
| Android 17 | 37 | `System.load()` する native files は read-only 必須。違反時は `UnsatisfiedLinkError` と公式文書は説明。 |

## 顧客向け説明（Explanation for Customers）

Android 17 では、targetSdkVersion 37 以上のアプリに対して、Android 14 で DEX / JAR に導入された Safer Dynamic Code Loading protection が native libraries にも拡張されます。`System.load()` で読み込む native file は read-only として mark されている必要があり、writable なままだと `UnsatisfiedLinkError` が発生します。

dynamic code loading は code injection / code tampering のリスクを高めるため、可能な限り避けることが推奨されます。現時点では local AOSP checkout に Android 17 tag がないため、targetSdkVersion gate、read-only 判定、compat flag の有無は未確認です。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-17
- Original statement: targetSdkVersion 37 以上のアプリでは、Android 14 で DEX / JAR files に導入された Safer DCL protection が native libraries に拡張される。`System.load()` で読み込まれる native files は read-only 必須で、違反時は `UnsatisfiedLinkError`。
- AOSP files: 未確認。local `frameworks-base` に `android-17*` tag がない。
- AOSP source context: 未確認。tag 間 diff が実行できない。
- Diff interpretation: 未分類。公式文書上は added behavior / changed condition と読めるが、AOSP diff による確認は Android 17 tag 待ち。
- Gate conclusion: Unknown。公式文書は targetSdkVersion 37+ を示すが、AOSP gate evidence は未取得。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Human decision required

判断（Decision）:
- Further investigation required

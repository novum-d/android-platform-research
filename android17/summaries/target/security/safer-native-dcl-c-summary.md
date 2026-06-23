# Safer Native DCL-C - 1ページ要約

## 対象

Android 17 Behavior Change

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

## 適用条件

- 主分類（Primary classification）: TARGET_SDK_37_CONDITIONAL
- OS アップデート / 全アプリ（OS update / all apps）: 非該当。AOSP gate は targetSdkVersion 37 以上で有効。
- targetSdkVersion 37 以上: 該当。writable な native file を `System.load()` すると `UnsatisfiedLinkError` になる。
- その他の必須条件（Other required conditions）: `System.load()` による dynamic native library loading、native file が read-only でないこと。
- Compat Change ID: `463348571` (`THROW_ERROR_FOR_WRITABLE_DCL`)
- Compat default state: `@EnabledSince(targetSdkVersion = VersionCodes.CINNAMON_BUN)`
- Confidence: High

## 要約

Android 17 では、targetSdkVersion 37 以上のアプリで、`System.load()` する native file が read-only として mark されていない場合に `UnsatisfiedLinkError` になる、と公式文書は説明している。

libcore の `Runtime.load0()` と `VMRuntime` で、writable native file の検出、compat ChangeId `463348571`、targetSdkVersion 37 gate、`UnsatisfiedLinkError` path を確認した。

## 顧客影響

- 実行時に `.so` をダウンロード、生成、展開、更新して `System.load()` するアプリに影響する可能性がある。
- 画像・動画処理、codec、AI / ML delegate、ネットワーク処理、暗号処理などの native library をアプリ起動後に展開・更新して読み込むアプリ / SDK も確認対象。
- `System.load()` 前に、読み込む native file を read-only にしておく必要がある。
- dynamic native loading は code injection / tampering risk が高いため、可能な限り避けることが推奨される。

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-17
- AOSP checkout: `frameworks-base` と `tmp/aosp-checkouts/libcore` の `android-16.0.0_r4` / `android-17.0.0_r1` tag を確認。
- AOSP: `libart/src/main/java/dalvik/system/VMRuntime.java` に `THROW_ERROR_FOR_WRITABLE_DCL = 463348571` と `@EnabledSince(targetSdkVersion = VersionCodes.CINNAMON_BUN)`。
- AOSP: `ojluni/src/main/java/java/lang/Runtime.java` の `load0()` は writable file を検出し、flag / compat / SDK 条件が揃う場合に `UnsatisfiedLinkError("Attempt to load writable file: ...")` を throw する。
- 差分解釈: warning/logging path から、targetSdkVersion 37 以上では error に変わる changed condition。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断

# Exceptions - 1ページ要約（One Page Summary）

## 対象（Target）

Android 16 Behavior Change

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:

## 適用条件（Applicability）

- 主分類（Primary classification）: `TARGET_SDK_36_CONDITIONAL`
- OS アップデート / 全アプリ（OS update / all apps）: No。Android 16 へ OS アップデートしただけで targetSdkVersion 35 以下の全アプリに既定適用されるとは判断しない。
- targetSdkVersion 36 以上: Yes。`UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415 が targetSdkVersion 36 以上で default enabled。
- その他の必須条件（Other required conditions）: Android 16 以上、display `sw >= 600dp`、game ではない、user aspect ratio setting exception なし、temporary opt-out なし、OEM / device config による抑止なし。
- Compat Change ID: `UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415
- Compat default state: Android 16 / API level 36 以上を target するアプリで enabled。
- Temporary opt-out: `android.window.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY=true` を application または activity property として指定。ただし公式文書と AOSP TODO は API 37 以降で使えなくなる予定を示す。

## 公式文書との差分（Documentation Drift）

確認時点の公式 `#exceptions` section は、例外として game、user aspect ratio setting、`sw600dp` 未満の 3 つを列挙していた。

依頼文に含まれる `OEMs can provide overrides to the Android 16 behavior through device configurations.` は、現在の公式 `#exceptions` section では見つからなかった。AOSP には DeviceConfig override の証跡があるため、summary では公式 section の statement と端末実装差の evidence を分けて扱う。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ | 期待挙動 |
| --- | --- |
| Android 16 / targetSdkVersion 35 | targetSdkVersion 36 起因の base behavior は既定適用対象外 |
| Android 16 / targetSdkVersion 36 / `sw >= 600dp` / non-game / no user exception / no opt-out | orientation / resizability / aspect ratio restrictions は無視 |
| Android 16 / targetSdkVersion 36 / `sw < 600dp` | large screen gate を満たさないため例外 |
| Android 16 / targetSdkVersion 36 / game app | `ApplicationInfo.CATEGORY_GAME` により例外 |
| Android 16 / targetSdkVersion 36 / user aspect ratio setting exception | user が app default behavior を選ぶと例外になり得る |
| Android 16 / targetSdkVersion 36 / OEM override enabled | DeviceConfig により端末ごとの差があり得る |
| Android 16 / targetSdkVersion 36 / OEM package opt-out | config path から外れる |
| Android 16 / targetSdkVersion 36 / Activity opt-out | 該当 activity は一時的に従来挙動 |
| Android 16 / targetSdkVersion 36 / Application opt-out | package 全体で一時的に従来挙動 |
| Android 15 / targetSdkVersion 36 | Android 16 の large screen default ignore 差分はないため、同一挙動とは結論しない |

## 要約（Summary）

`Exceptions` は、Android 16 adaptive layouts の base behavior が適用されない条件を扱う節である。
公式文書の例外は、game、user が aspect ratio settings で app default behavior を明示選択する場合、`sw600dp` 未満の screen。
AOSP では game は `ApplicationInfo.CATEGORY_GAME`、small screen は `DisplayContent#isLargeScreen()`、user setting は `AppCompatAspectRatioOverrides` を通じて `ActivityRecord#isUniversalResizeable()` に接続される。

## 顧客影響（Customer Impact）

- 要確認

理由:
- 例外条件に入る場合、Android 16 / targetSdkVersion 36 でも base behavior は抑止される。
- 例外条件に入らないlarge screenでは、固定方向、サイズ変更不可、min/max aspect ratio、pillarboxingの前提が崩れる。
- OEM / DeviceConfig と user aspect ratio settings により、端末やユーザー設定ごとに見え方が変わる可能性がある。

## 影響対象（Who Is Affected）

- games / `android:appCategory="game"` を指定しているアプリ。
- game だが `appCategory` を指定していないアプリ。
- user aspect ratio settings に依存するアプリ。
- OEM device configuration の影響を受ける可能性があるアプリ。
- `sw < 600dp` の phone / small screen 前提のアプリ。
- temporary opt-out 済みアプリ。
- portrait / landscape 固定に依存するアプリ。
- `resizeableActivity=false` に依存するアプリ。
- `minAspectRatio` / `maxAspectRatio` に依存するアプリ。
- pillarboxing / compatibility mode に依存するアプリ。
- Compose UI / View UI のどちらも対象。

## 対応要否（Required Action）

- 必須対応: targetSdkVersion 36 化する large screen 対応対象アプリで、例外条件に入らない場合。
- 要確認: game は `ApplicationInfo.category` が `CATEGORY_GAME` になっているか確認する。
- 要確認: user aspect ratio settings の app default / fullscreen / custom ratio で表示差を確認する。
- 要確認: OEM device / emulator / Pixel で DeviceConfig や package opt-out による差を記録する。
- 一時対応: `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY=true` は Android 16 では使えるが、API 37 以降に向けた恒久対応ではない。

## テストマトリクス（Test Matrix）

| 端末 OS | targetSdkVersion | 条件 | 期待挙動 / 確認点 |
| --- | --- | --- | --- |
| Android 15 | 35 | baseline | 従来挙動 |
| Android 16 | 35 | OS update only | targetSdkVersion 36 起因の base behavior は既定適用対象外 |
| Android 16 | 36 | `sw >= 600dp` / non-game / no exception | restrictions は無視 |
| Android 16 | 36 | `sw < 600dp` | large screen gate を満たさない |
| Android 16 | 36 | `android:appCategory="game"` | game exception |
| Android 16 | 36 | user aspect ratio app default | user setting exception を確認 |
| Android 16 | 36 | OEM override enabled / disabled | DeviceConfig / package opt-out の差を確認 |
| Android 16 | 36 | Activity opt-out | 該当 activity は一時的に従来挙動 |
| Android 16 | 36 | Application opt-out | package 全体で一時的に従来挙動 |

追加テスト:
- Android 15 / targetSdkVersion 36 が検証可能な場合の比較。
- game app category あり / なし。
- `screenOrientation` / `setRequestedOrientation()` / `getRequestedOrientation()` の exception 有無による差。
- `resizeableActivity=false`、`minAspectRatio`、`maxAspectRatio` 指定あり / なし。
- full-screen と multi-window。
- pillarboxing / compatibility mode の有無。
- visual regression / screenshot testing。

## 顧客向け説明（Explanation for Customers）

Android 16 へ OS アップデートしただけで、targetSdkVersion 35 以下のアプリにこの変更が既定適用されるとは説明しません。
targetSdkVersion 36 以上に上げると、Android 16 端末の large screen では orientation / resizability / aspect ratio restrictions が無視されますが、game、user aspect ratio setting、`sw600dp` 未満、temporary opt-out、端末固有 DeviceConfig では挙動が変わります。
公式の例外条件と OEM / device configuration による端末差は分けて説明してください。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/16/behavior-changes-16#exceptions
- Compat framework: `UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415、Android 16 / API 36 以上 target で enabled。
- AOSP files: `ActivityInfo.java`、`ApplicationInfo.java`、`PackageParser.java`、`WindowManager.java`、`DisplayContent.java`、`ActivityRecord.java`、`AppCompatAspectRatioOverrides.java`、`AppCompatResizeOverrides.java`、`WindowManagerConstants.java`。
- AOSP source context: manifest category / display size / user setting / DeviceConfig / opt-out property -> `ActivityRecord#isUniversalResizeable()`。
- Diff interpretation: Android 16 tagでlarge screen default ignore経路が追加。例外条件では、あらゆるウィンドウサイズへ変更可能とする処理経路から外れる。
- Gate conclusion: Android 16 以上 + targetSdkVersion 36 以上 + `sw >= 600dp` + non-game + user exception なし + opt-out なし + OEM package opt-out なし。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 未判断

判断（Decision）:
- 未判断

Owner notes:
- 最終優先度、severity、release readiness、顧客 communication priority は repository owner が判断する。

## 再検証記録（2026-08-22）

- Android 16 の公式 Behavior Change 一覧と最新通常AOSPタグを再確認した。
- 対応する[主レポート](../../../behavior-changes/target/device-form-factors/exceptions-adaptive-layouts.md)で official section、AOSP project / remote / checkout、解決済み commit、比較 command、dirty risk を再検証した。
- 主レポートの分類、confidence、未確認事項を維持し、実機未実施の項目を Observed 済みへ変更していない。
- 全件の結果は[再検証台帳](../../../analysis/REVALIDATION_2026-08-22.md)を参照する。

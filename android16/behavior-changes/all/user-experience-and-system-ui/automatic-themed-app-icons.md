# Automatic themed app icons

## 調査メタデータ

| 項目 | 内容 |
|---|---|
| Android version | Android 16 QPR2 |
| Version directory | `android16` |
| From tag | `android-15.0.0_r36` |
| To tag | `android-16.0.0_r4` |
| Previous targetSdkVersion | 35 |
| Target targetSdkVersion | 36 |
| 公式ドキュメント | https://developer.android.com/about/versions/16/behavior-changes-all#themed-app-icons |
| 公式カテゴリ | User experience and system UI |
| Page type | Behavior changes: all apps |
| 出力 | `android16/behavior-changes/all/user-experience-and-system-ui/automatic-themed-app-icons.md` |

注意: `android16/AGENTS.md` の To tag は `android-16.0.0_r1` だが、この調査では依頼スコープに従い `android-16.0.0_r4` を確認した。公式本文は “Beginning with Android 16 QPR 2” としており、`android-16.0.0_r4` で見える実装部品と、QPR2 リリースで実際に有効化される挙動は分けて扱う。

## Original statements

| 公式文 | 検証結果 |
|---|---|
| Beginning with Android 16 QPR 2, Android automatically applies themes to app icons to create a cohesive home screen experience. | 公式本文と一致。AOSP では Launcher3 / iconloaderlib に、monochrome layer がない adaptive icon から themed bitmap を生成する経路と aconfig flag がある。QPR2 の製品有効化状態は `android-16.0.0_r4` だけでは完全には確定できない。 |
| This occurs if an app does not provide its own themed app icon. | 公式本文と一致。`AdaptiveIconDrawable#getMonochrome()` が null の場合に、`forceMonochromeAppIcons()` と theme controller 条件で `MonochromeIconFactory.wrap()` を使う fallback が確認できる。 |
| Apps can control the design of their themed app icon by including a monochrome layer within their adaptive icon and previewing what their app icon will look like in Android Studio. | 公式本文と一致。framework は `<monochrome>` child と `getMonochrome()` を持ち、公式 adaptive icon docs / Android Studio docs は monochrome layer と preview を案内している。 |

公式ページ最終更新は 2026-06-24 UTC。関連 adaptive icon docs は、Android 13 以降の themed icons baseline、Android 16 QPR2 以降の自動 theme、`<monochrome>` layer、Android Studio preview を説明している。

## Applicability classification

Primary classification: `OS_UPDATE_ALL_APPS`

追加条件:

- Android 16 QPR2 以降であること。
- launcher / system UI 側の themed icons feature が有効であること。
- 対象 launcher が automatic themed icon generation を実装していること。
- アプリが自前の themed app icon、具体的には adaptive icon の `monochrome` layer を提供していないこと。
- targetSdkVersion 35 / 36 の差ではなく、OS/QPR/launcher 側の表示挙動であること。

targetSdkVersion gate: 見つからなかった。公式 all apps ページは “regardless of targetSdkVersion” と説明しており、Android 16 compat framework changes ページで themed icon / monochrome / launcher に対応する app compat Change ID は確認できなかった。

Confidence: Medium

理由:

- 公式文書は明確に Android 16 QPR2 開始と説明している。
- AOSP `android-16.0.0_r4` の Launcher3 / iconloaderlib に fallback 生成経路、feature flag、テストがある。
- ただし QPR2 専用 feature のため、`android-16.0.0_r4` が QPR2 製品 tag そのものではない場合、最終的な有効化条件や Pixel Launcher 固有挙動は QPR2 branch/tag またはデバイス実機で追加確認が必要。

## Facts

- Android 16 all apps 公式ページは、Android 16 QPR2 から、アプリが自前の themed app icon を提供しない場合に Android が app icon に自動で theme を適用すると説明している。
- 同じ公式文は、アプリが adaptive icon に monochrome layer を含めることで themed icon の見た目を制御でき、Android Studio で preview できると説明している。
- `frameworks-base` は `AdaptiveIconDrawable` に `<monochrome>` child を扱う実装と `getMonochrome()` public API を持つ。`core/api/current.txt` でも `AdaptiveIconDrawable(Drawable, Drawable, Drawable)` と `getMonochrome()` が public API として公開されている。
- `packages/apps/Launcher3` の `aconfig/launcher.aconfig` には `force_monochrome_app_icons` があり、説明は “app が提供しない場合に monochromatic icons を生成する能力を有効化する” という内容である。`force_monochrome_app_icons_adapt_colors` は生成 monochrome icon の色適応を示す。
- Launcher3 の `MonoIconThemeFactory` は `MonoIconThemeController(shouldForceThemeIcon = true)` を提供し、theme が有効なときに mono icon theme controller を作る。
- `frameworks/libs/systemui` の iconloaderlib では、`BaseIconFactory` が `themeController` を受け取り、adaptive icon の場合に `themeController.createThemedBitmap()` で `BitmapInfo.themedBitmap` を作る。
- `MonoIconThemeController` は、アプリが `monochrome` layer を提供する場合はそれを使う。提供しない場合でも `Flags.forceMonochromeAppIcons()` かつ `shouldForceThemeIcon` が true なら `MonochromeIconFactory.wrap(icon)` で monochrome bitmap を生成する。
- `BitmapInfo.newIcon()` は `FLAG_THEMED` が指定され、`themedBitmap` が `NOT_SUPPORTED` でない場合に themed drawable delegate を使う。
- Launcher3 の `ThemeManager` / `ThemePreference` は launcher preference の theme value から `themeController` を解決し、theme が無効なら `themeController == null` になる。
- Android Studio docs は Image Asset Studio の Monochrome Layer tab と themed app icon preview を案内している。

## Observations

- Android 13 以降の baseline は “アプリが monochrome layer を提供していれば themed icons に使える” というモデルであり、Android 16 QPR2 の差分は “提供していない場合も launcher/system UI が自動生成して theme を適用し得る” ことにある。
- AOSP Launcher3 / iconloaderlib は themed icon の一般部品であり、Pixel Launcher や OEM launcher は同じ実装を使う場合も独自実装を持つ場合もある。したがって customer-facing impact は launcher-dependent として扱うべきである。
- `android:icon` / `android:roundIcon` / activity / activity-alias icon のどれが使われるかは launcher の icon 解決経路に依存する。アプリが複数 launcher activity や activity-alias に別 icon を持つ場合、各 icon resource ごとに monochrome layer / fallback 生成を確認する必要がある。
- `android-16.0.0_r4` には実装・flag・テストが存在するが、公式の開始条件は Android 16 QPR2 である。Android 16 base release で同じ見た目になるとは扱わない。
- compat framework の app-level Change ID は確認できないため、`targetSdkVersion 36` 化だけで発火する変更とは分類しない。

## Hypotheses

- QPR2 製品 build では、Launcher3/Pixel Launcher 側で `force_monochrome_app_icons` 相当の flag と themed icons setting が有効な場合、monochrome layer のない adaptive icon も自動生成 monochrome bitmap により themed 表示される。
- OEM launcher は AOSP Launcher3 と異なる icon cache / rendering 実装を持つ可能性があるため、Android 16 QPR2 以降でも自動 themed icon の見た目、適用範囲、cache invalidation は端末依存になる可能性がある。
- legacy bitmap icon や roundIcon only の扱いは launcher の adaptive wrapping / icon normalization に依存するため、adaptive icon with no monochrome layer よりも見た目差が出やすい。

## Conclusions

- この変更は targetSdkVersion 36 化の影響ではなく、Android 16 QPR2 以降の launcher/system UI 表示変更である。
- Android 16 base release へ OS アップデートしただけでは、公式上の “Automatic themed app icons” 開始条件とは扱わない。Android 16 QPR2 以降、かつ themed icons が有効な launcher で確認する。
- `monochrome` layer を提供していないアプリは、launcher が自動生成した themed icon により、ホーム画面上のブランド色・ロゴ認識性・コントラストが変わる可能性がある。
- アプリ側が見た目を制御したい場合は、adaptive icon に明示的な `<monochrome>` layer を追加し、Android Studio preview と実機 launcher screenshot で確認するのが推奨される。

## AOSP evidence

### framework: adaptive icon / monochrome layer

Source:

- `frameworks-base` tag `android-16.0.0_r4`
- `graphics/java/android/graphics/drawable/AdaptiveIconDrawable.java`
- `core/api/current.txt`

Reviewed context:

- `AdaptiveIconDrawable` class documentation states that an alternate drawable can be specified with `<monochrome>` and tinted according to device or surface theme.
- `MONOCHROME_ID` is a child layer id.
- XML inflation handles the `"monochrome"` child.
- Public constructor accepts background / foreground / monochrome drawables.
- `getMonochrome()` returns the monochrome drawable.
- `current.txt` exposes the 3-argument constructor and `getMonochrome()`.

Diff interpretation:

- This is public API / resource model evidence, not the QPR2 automatic fallback itself.
- It supports the conclusion that developer-provided monochrome layer is the controlled path.

### Launcher3: feature flag and launcher theme state

Source:

- `tmp/aosp-checkouts/Launcher3`
- Tags `android-15.0.0_r36` and `android-16.0.0_r4`
- `aconfig/launcher.aconfig`
- `src/com/android/launcher3/graphics/ThemeManager.kt`
- `src/com/android/launcher3/graphics/theme/ThemePreference.kt`
- `src/com/android/launcher3/graphics/theme/MonoIconThemeFactory.kt`

Reviewed context:

- `force_monochrome_app_icons` description: app が提供しない場合に monochromatic icons を生成する能力を有効化する。
- `force_monochrome_app_icons_adapt_colors` description: generated monochromatic icons の色適応。
- `ThemeManager.isIconThemeEnabled` は `themeController != null`。
- `ThemePreference` は `icon_theme_id` と legacy `themed_icons` preference を管理し、`MONO_THEME_VALUE` を `MonoIconThemeFactory` に結びつける。
- `MonoIconThemeFactory` は `MonoIconThemeController(shouldForceThemeIcon = true)` を返す。

Diff interpretation:

- `android-15.0.0_r36` から `android-16.0.0_r4` で `ThemeManager.kt`, `ThemePreference.kt`, `MonoIconThemeFactory.kt` などが追加・変更されている。
- ただし Android 15 側にも iconloaderlib の mono controller / monochrome generation 部品は存在するため、差分は “monochrome 生成アルゴリズムの初出” ではなく、QPR2 公式挙動に向けた launcher theme 管理・有効化・fallback 適用条件として読む。

### iconloaderlib: automatic fallback generation

Source:

- `tmp/aosp-checkouts/systemui-libs`
- Tags `android-15.0.0_r36` and `android-16.0.0_r4`
- `iconloaderlib/src/com/android/launcher3/icons/BaseIconFactory.kt`
- `iconloaderlib/src/com/android/launcher3/icons/BitmapInfo.kt`
- `iconloaderlib/src/com/android/launcher3/icons/mono/MonoIconThemeController.kt`
- `iconloaderlib/src/com/android/launcher3/icons/mono/MonoThemedBitmap.kt`

Reviewed context:

- `BaseIconFactory` constructor accepts `themeController`.
- `createBadgedIconBitmap()` creates `themedBitmap` for `AdaptiveIconDrawable` when `themeController` is non-null.
- `MonoIconThemeController.createThemedBitmap()` first uses `icon.monochrome` if present.
- If monochrome is absent and `Flags.forceMonochromeAppIcons()` plus `shouldForceThemeIcon` are true, it uses `MonochromeIconFactory.wrap(icon)` and stores generated mono bitmap.
- `createThemedAdaptiveIcon()` uses app-provided monochrome layer first; otherwise it can inject previously generated `MonoThemedBitmap`.
- `BitmapInfo.newIcon()` uses themed delegate only when `FLAG_THEMED` is requested and the themed bitmap is supported.

Diff interpretation:

- Added/changed behavior: Android 16 r4 path explicitly separates app-provided monochrome from force-generated monochrome and uses `ThemedBitmap.NOT_SUPPORTED` for unsupported cases.
- This supports the official statement that an app without its own themed icon can still be automatically themed, provided launcher feature state requests themed rendering.

### Tests

Source:

- `tmp/aosp-checkouts/Launcher3`
- `tests/multivalentTests/src/com/android/launcher3/icons/mono/MonoIconThemeControllerTest.kt`
- `tests/multivalentTests/src/com/android/launcher3/icons/mono/MonoThemedBitmapTest.kt`

Reviewed context:

- Test with app-provided monochrome drawable expects themed bitmap support.
- Test with mono generation disabled expects `ThemedBitmap.NOT_SUPPORTED`.
- Test with `Flags.FLAG_FORCE_MONOCHROME_APP_ICONS` enabled and `shouldForceThemeIcon = true` expects themed bitmap support even with no monochrome drawable.
- Test verifies `createThemedAdaptiveIcon()` can use app-provided monochrome or generated `BitmapInfo`.

Diff interpretation:

- Test evidence directly validates the enabled/disabled behavior of automatic monochrome generation and the fallback path.

## 対象アプリ種別

- monochrome adaptive icon layer を提供していないアプリ。
- adaptive icon はあるが themed icon を未対応のアプリ。
- legacy launcher icon のみを提供するアプリ。
- brand color / logo shape / icon recognizability を重視するアプリ。
- 複数 launcher icon / activity-alias / dynamic icon を使うアプリ。
- white-label / multi-brand icon を持つアプリ。
- OEM launcher / Pixel Launcher / AOSP Launcher3 で見た目差を検証する必要があるアプリ。
- Android Studio preview で themed icon を確認する必要があるアプリ。
- Play Store / marketing asset と launcher icon の一貫性を重視するアプリ。

## 期待挙動マトリクス

| 条件 | 期待挙動 | targetSdkVersion 36 化の影響 |
|---|---|---|
| Android 15 / targetSdkVersion 36 | Android 16 QPR2 automatic themed icon は対象外。Android 13+ baseline の themed icon は launcher / monochrome layer 次第。 | なし |
| Android 16 base / targetSdkVersion 35 | 公式上の QPR2 automatic themed icon 開始条件ではない。 | なし |
| Android 16 QPR2 / targetSdkVersion 35 | themed icons 有効、launcher 対応、monochrome layer なしなら自動 themed 表示され得る。 | なし |
| Android 16 QPR2 / targetSdkVersion 36 | targetSdk 35 と同じ。 | なし |
| themed icons setting enabled | launcher が `FLAG_THEMED` 相当で themed drawable を要求し得る。 | なし |
| themed icons setting disabled | standard / adaptive icon 表示。automatic themed icon の影響なし。 | なし |
| adaptive icon with monochrome layer | app-provided monochrome layer が優先され、見た目を制御しやすい。 | なし |
| adaptive icon without monochrome layer | QPR2 以降、launcher が自動生成 themed icon を使う可能性。 | なし |
| legacy bitmap launcher icon | launcher の adaptive wrapping / fallback 実装依存。実機確認が必要。 | なし |
| roundIcon only | circular icon を選ぶ launcher では roundIcon 経路も確認が必要。 | なし |
| application icon | launcher activity が icon override を持たなければ app icon が使われる。 | なし |
| activity icon override | activity icon resource ごとに monochrome layer / fallback を確認。 | なし |
| activity-alias icon | alias icon resource ごとに確認。dynamic icon switch では cache invalidation も確認。 | なし |
| AOSP Launcher3 | AOSP evidence あり。theme preference / iconloaderlib 経路で説明可能。 | なし |
| Pixel Launcher | AOSP Launcher3 由来の可能性はあるが、Pixel 固有挙動は実機または Pixel source evidence が必要。 | なし |
| OEM launcher with support | OEM 実装次第で自動 themed icon が適用される。 | なし |
| OEM launcher without support | automatic themed icon は表示されない。 | なし |
| app updates to add monochrome layer | 自動生成ではなく developer-provided themed icon に寄せられる。 | なし |
| app does not update icon resources | QPR2 以降の launcher が生成した見た目に依存。 | なし |
| Android Studio preview matches device | preview を出荷判断に使いやすいが、launcher 差は残る。 | なし |
| Android Studio preview differs from device | device launcher / OEM / cache / wallpaper palette を優先して判断。 | なし |

## 詳細マトリクス

| ケース | 期待される確認結果 |
|---|---|
| Android 16 base / targetSdkVersion 35 / no monochrome layer | 公式 QPR2 feature としては対象外。既存 themed icon support は launcher 実装依存。 |
| Android 16 QPR2 / targetSdkVersion 35 / no monochrome layer | themed icons が有効なら自動生成 themed icon が表示され得る。 |
| Android 16 QPR2 / targetSdkVersion 36 / no monochrome layer | targetSdk 35 と同じ。 |
| Android 16 QPR2 / targetSdkVersion 35 / monochrome layer provided | app-provided monochrome layer が使われる。 |
| Android 16 QPR2 / targetSdkVersion 36 / monochrome layer provided | targetSdk 35 と同じ。 |
| Android 16 QPR2 / themed icons setting enabled | icon theme controller / themed drawable 経路が有効になり得る。 |
| Android 16 QPR2 / themed icons setting disabled | automatic themed icon の表示影響なし。 |
| Android 16 QPR2 / adaptive icon with monochrome layer | 推奨パス。ブランド制御可能。 |
| Android 16 QPR2 / adaptive icon without monochrome layer | automatic fallback generation の主要対象。 |
| Android 16 QPR2 / legacy bitmap launcher icon | launcher の wrapping / generation 対応を実機確認。 |
| Android 16 QPR2 / roundIcon only | circular launcher / icon shape 設定で見た目確認。 |
| Android 16 QPR2 / application icon | app-level icon resource の monochrome layer を確認。 |
| Android 16 QPR2 / activity icon override | activity-level icon resource を個別確認。 |
| Android 16 QPR2 / activity-alias icon | alias icon resource と dynamic switch 後の cache を確認。 |
| Android 16 QPR2 / dynamic launcher icon switching | switch 前後で themed icon / cache invalidation を確認。 |
| Android 16 QPR2 / AOSP Launcher3 | AOSP evidence あり。 |
| Android 16 QPR2 / Pixel Launcher | 実機 evidence が必要。 |
| Android 16 QPR2 / OEM launcher with automatic themed icon support | OEM 実装依存で適用。 |
| Android 16 QPR2 / OEM launcher without automatic themed icon support | 非適用。 |
| Android 15 / targetSdkVersion 36 | QPR2 automatic feature は対象外。 |

## テスト観点

- Android 15 端末上の targetSdkVersion 35。
- Android 16 base 端末上の targetSdkVersion 35。
- Android 16 QPR2 端末上の targetSdkVersion 35。
- Android 16 QPR2 端末上の targetSdkVersion 36。
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較。
- themed icons setting enabled / disabled。
- adaptive icon with monochrome layer。
- adaptive icon without monochrome layer。
- legacy icon only。
- `roundIcon` / `icon` の違い。
- activity / activity-alias icon override。
- dynamic launcher icon switching。
- app update before / after adding monochrome layer。
- light / dark wallpaper theme variation。
- different wallpaper colors / Material You palette。
- AOSP Launcher3 / Pixel Launcher / OEM launcher comparison。
- Android Studio preview。
- actual device screenshot comparison。
- icon recognizability / contrast / brand compliance。
- launcher icon cache invalidation after app update。
- work profile / secondary user / cloned app, if relevant。
- regression testing for launcher shortcuts and pinned shortcuts, if icon path is shared。

## Recommended action candidates

- 全 launcher icon resource を棚卸しし、`<adaptive-icon>` に `<monochrome>` layer があるか確認する。
- 複数 activity / activity-alias / dynamic icon を使う場合は、表示されるすべての icon resource を対象にする。
- Android Studio の themed app icon preview で基本形を確認する。
- Android 16 QPR2 以降の実機または emulator で themed icons setting enabled / disabled、複数 wallpaper palette、light/dark の screenshot を取得する。
- 自動生成結果がブランド要件を満たさない場合は、専用の monochrome layer を追加する。
- Pixel Launcher / AOSP Launcher3 / 主要 OEM launcher で見た目差を QA 対象にする。

## Evidence gaps

- `android-16.0.0_r4` は依頼された To tag だが、公式文の開始点は Android 16 QPR2 である。QPR2 final branch/tag、Pixel Launcher 実機、OEM launcher 実機での有効化状態は追加確認が必要。
- Android Studio preview は公式 tooling docs として確認したが、device launcher rendering と完全一致する保証はない。
- legacy bitmap icon / pinned shortcut / work profile / cloned app の細部は launcher 実装依存で、AOSP source だけでは customer device の最終表示を断定できない。

## Human decision placeholder

- Human decision: 未判断
- Priority: 未判断
- Severity: 未判断
- Release readiness impact: 未判断
- Customer communication priority: 未判断

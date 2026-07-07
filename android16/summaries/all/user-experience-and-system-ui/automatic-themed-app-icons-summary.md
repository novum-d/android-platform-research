# Automatic themed app icons summary

## One page summary

Android 16 QPR2 以降では、themed icons が有効な launcher / system UI 上で、アプリが自前の themed app icon、つまり adaptive icon の `monochrome` layer を提供していない場合でも、Android が app icon に自動で theme を適用する可能性がある。これは targetSdkVersion 36 化そのものの影響ではなく、Android 16 QPR2 以降の OS / launcher 表示挙動である。

Primary classification: `OS_UPDATE_ALL_APPS`

追加条件:

- Android 16 QPR2 以降。
- themed icons setting が有効。
- launcher が automatic themed icon generation を実装している。
- アプリが monochrome adaptive icon layer を提供していない。
- targetSdkVersion 35 / 36 で挙動差は確認できない。

## Facts

- 公式ドキュメントは Android 16 QPR2 から automatic themed app icons が始まると説明している。
- `AdaptiveIconDrawable` は `<monochrome>` layer と `getMonochrome()` を public API として持つ。
- Launcher3 / iconloaderlib には、monochrome layer がある場合はそれを使い、ない場合は `force_monochrome_app_icons` と theme controller 条件で generated monochrome bitmap を使う経路がある。
- Launcher3 tests は mono generation disabled では unsupported、enabled では supported になることを検証している。
- compat framework Change ID / targetSdkVersion gate は確認できなかった。

## Observations

- Android 13 以降の baseline は「monochrome layer を提供したアプリが themed icons に対応できる」モデル。
- Android 16 QPR2 の差分は「提供していないアプリにも launcher が自動生成 themed icon を適用し得る」点。
- Pixel Launcher / OEM launcher の最終表示は実装依存なので、AOSP evidence だけで全端末の見た目は断定しない。

## Hypotheses

- QPR2 製品 build では、themed icons が有効な launcher が `force_monochrome_app_icons` 相当を有効にし、monochrome layer のない icon も自動生成で themed 表示する。
- legacy bitmap icon、roundIcon only、activity-alias icon は launcher の icon 解決・cache 実装によって見た目差が出る可能性がある。

## Conclusions

- Android 16 base への OS アップデート、targetSdkVersion 36 化、Android 16 QPR2 へのアップデート、monochrome layer の有無を混ぜて説明しない。
- ブランド制御が必要なアプリは、automatic generation に任せず adaptive icon に明示的な `<monochrome>` layer を追加するべき。
- Android Studio preview は有用だが、最終確認は Android 16 QPR2 以降の実機 launcher screenshot で行う。

## Expected behavior matrix

| 条件 | 期待挙動 |
|---|---|
| Android 16 base / targetSdkVersion 35 / no monochrome layer | 公式 QPR2 feature としては対象外。 |
| Android 16 QPR2 / targetSdkVersion 35 / no monochrome layer | themed icons 有効なら自動 themed 表示され得る。 |
| Android 16 QPR2 / targetSdkVersion 36 / no monochrome layer | targetSdk 35 と同じ。 |
| Android 16 QPR2 / monochrome layer provided | app-provided icon が優先され、見た目を制御可能。 |
| themed icons setting disabled | 影響なし。 |
| Android 15 / targetSdkVersion 36 | QPR2 automatic feature は対象外。 |

## Test focus

- Android 16 QPR2 / targetSdkVersion 35 と 36 の比較。
- themed icons setting enabled / disabled。
- adaptive icon with / without monochrome layer。
- legacy icon、roundIcon、activity-alias、dynamic icon。
- Pixel Launcher / AOSP Launcher3 / OEM launcher screenshot。
- wallpaper palette / light-dark variation。
- app update 後の launcher icon cache invalidation。

## Human decision placeholder

- Human decision: 未判断
- Priority: 未判断
- Severity: 未判断
- Release readiness impact: 未判断
- Customer communication priority: 未判断

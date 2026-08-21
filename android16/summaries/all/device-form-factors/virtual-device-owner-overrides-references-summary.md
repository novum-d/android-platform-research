# References One Page Summary

## 対象

- Android version: Android 16
- From / To: `android-15.0.0_r36` -> `android-16.0.0_r4`
- Previous / Target targetSdkVersion: 35 -> 36
- Official documentation: https://developer.android.com/about/versions/16/behavior-changes-all#references
- Category: Device form factors
- Parent section: Virtual device owner overrides
- Section: References

## 結論

Primary classification:
- `OS_UPDATE_ALL_APPS`

ただし、`References` section 自体は independent runtime behavior change ではない。公式本文は `Companion app streaming` への参照リンクのみである。正式分類に documentation-reference-only がないため、親項目 `Virtual device owner overrides` に合わせて `OS_UPDATE_ALL_APPS` を使う。

実際の互換性影響は、親項目の `Per-app overrides` と `Common breaking changes` に属する。trusted / privileged virtual device owner が selected virtual display 上で orientation、aspect ratio、resizability restrictions を無視できる場合、large screen / external display 上で phone portrait 前提 UI が崩れ得る。

## References section の扱い

| 観点 | 判定 |
| --- | --- |
| 独立した runtime change | No |
| 参照先 | Companion app streaming |
| 親項目との関係 | virtual device owner projection model の背景参照 |
| targetSdkVersion 36 条件 | なし |
| local physical display impact | References 起因ではなし |
| customer-facing impact | 親項目の projection / override impact として説明する |

## AOSP / documentation evidence

- Android Developers 公式ページでは、`References` section は `Companion app streaming` link のみ。
- Source Android の正しい参照先は `https://source.android.com/docs/core/permissions/app-streaming`。同文書は `COMPANION_DEVICE_APP_STREAMING` role、virtual display、remote display streaming、remote input injection を説明している。
- 親項目の AOSP evidence では、`VirtualDeviceManager#createVirtualDevice` が `CREATE_VIRTUAL_DEVICE` を要求し、ordinary app 向けではない。
- `VirtualDisplayConfig.Builder#setIgnoreActivitySizeRestrictions(boolean)`は固定方向、aspect ratio、サイズ変更可否の制約を無視するvirtual display propertyを設定する。
- `DisplayManagerService` は trusted virtual display でない場合、この request を無視する。
- WindowManager app-compat path は display ignore state を参照し、orientation / aspect ratio / fullscreen behavior に影響する。
- 該当 path に targetSdkVersion 36 gate は見つからない。

## 期待挙動マトリクス

| Scenario | Expected behavior |
| --- | --- |
| References section / documentation pointer only | 独立 runtime behavior change ではない。 |
| Companion app streaming reference / relevant background | 親項目の projection model を理解する背景資料。正しい参照先は `source.android.com/docs/core/permissions/app-streaming`。 |
| Android 16 / targetSdkVersion 35 / local physical display | References 起因の runtime change はない。 |
| Android 16 / targetSdkVersion 36 / local physical display | 同上。targetSdkVersion 36 だけでは変わらない。 |
| Android 16 / targetSdkVersion 35 / projected by virtual device owner | 親項目の projection / override 条件で影響し得る。 |
| Android 16 / targetSdkVersion 36 / projected by virtual device owner | targetSdkVersion 35 と同様。 |
| Android 16 / companion app streaming flow | trusted / privileged virtual device owner projection として親項目の影響条件になり得る。 |
| Android 16 / ordinary app without virtual device owner privilege | 同じ override を任意には使えない。 |
| Android 16 / selected virtual device with overrides enabled | orientation / aspect ratio / resizability restrictions が無視され得る。 |
| Android 16 / app projected to PC / VR / car / Chromebook | large screen / external display UI QA が必要。 |
| Android 15 / targetSdkVersion 36 | Android 16 References section 起因の change はない。親項目関連 API の enablement は別途確認。 |
| app reads reference documentation and migrates to adaptive layouts | recommended。 |
| app ignores projection guidance and continues relying on phone-only assumptions | projection 環境で高リスク。 |

## 影響対象

- companion app streaming / virtual device projection で利用されるアプリ。
- virtual device owner / privileged companion app と連携するアプリ。
- phone portrait 専用 UI のアプリ。
- 固定方向 / aspect ratio / `resizeableActivity=false`に依存するアプリ。
- large screen / external display / desktop mode / Chromebook / car display / VR display で利用され得るアプリ。
- adaptive layout / responsive UI へ移行すべきアプリ。
- References / companion app streaming documentation を確認すべきアプリ。

## テスト観点

- References section が independent runtime change ではないこと。
- companion app streaming documentation の参照先が有効か。
- Android 16 / targetSdkVersion 35 と 36 の比較。
- local physical display と virtual device owner projection の比較。
- trusted / privileged virtual device owner の有無。
- selected virtual device override enabled / disabled。
- PC / VR / car infotainment / Chromebook / large display projection。
- orientation / aspect ratio / resizability restriction respected / ignored。
- WindowMetrics / Configuration / DisplayInfo / resources qualifier changes。
- screenshot / screen recording による layout clipping / stretching / letterboxing / pillarboxing 確認。

## Recommended action candidates

- `References` を独立 breaking change として扱わない。
- 実際の migration / QA は親項目 `Per-app overrides` と `Common breaking changes` に紐付ける。
- projection 対象になり得る app は adaptive layout / large screen / external input QA を行う。
- source.android の正しい参照先 `https://source.android.com/docs/core/permissions/app-streaming` を継続確認する。

## Evidence gaps

- 正しい参照先は `https://source.android.com/docs/core/permissions/app-streaming`。参照先 path を取り違えないように注意が必要。
- Android 15 tag にも関連 API / aconfig flag が存在するため、AOSP diff だけで導入時点は断定しない。
- OEM / product-specific projection behavior は framework evidence と分けて確認する。

## Human Decision Placeholder

- Final priority:
- Final severity:
- Customer communication priority:
- Release readiness:
- Required documentation follow-up:
- Required app-side migration:
- Required QA scope:

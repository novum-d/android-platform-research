# Apps targeting Android 16 cross-reference - 1ページ要約（One Page Summary）

## 対象（Target）

Android 16 documentation cross-reference

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Official documentation:
- https://developer.android.com/about/versions/16/behavior-changes-all#targeting-16
- https://developer.android.com/about/versions/16/behavior-changes-16

Category:
- Overview / Cross-reference

## 適用条件（Applicability）

- 主分類（Primary classification）: `UNKNOWN_NEEDS_MORE_EVIDENCE`
- 分類注記: 正式ラベルに `DOCUMENTATION_REFERENCE_ONLY` / `OVERVIEW_ONLY` がないための placeholder。runtime 挙動が未知という意味ではない。
- Independent runtime behavior change: No
- all-apps page: Android 16 上で実行される全アプリ向け、targetSdkVersion に関係しない。
- target-only page: Android 16 / API 36 以上を target するアプリ向け。
- AOSP evidence: cross-reference 自体の実装なし。API 36 定義として `Build.VERSION_CODES.BAKLAVA = 36` を確認。

## 要約（Summary）

この項目は Android 16 の runtime behavior change ではなく、all-apps page と apps-targeting-Android-16 page を相互に確認するための documentation cross-reference である。

顧客説明では、Android 16 OS アップデートだけで発生する影響、targetSdkVersion 36 へ移行した時の影響、両方を同時に行った場合の影響を分ける必要がある。

## Anchor / Documentation Note

- requested anchor: `#targeting-16`
- 現行 all-apps HTML では `targeting-16` 文字列は確認できなかった。
- 最寄りの公式内容は、all-apps page 冒頭の target-only page への cross-link。

## Facts / Observations / Hypotheses / Conclusions

Facts:
- all-apps page は Android 16 runtime 上の全アプリ向け変更を扱う。
- target-only page は Android 16 / API 36 以上を target するアプリ向け変更を扱う。
- cross-reference 自体には AOSP implementation path がない。

Observations:
- `OS_UPDATE_ALL_APPS` と分類すると documentation-only item を runtime change と誤読しやすい。
- `TARGET_SDK_36` と分類すると all-apps page 全体まで target-gated と誤読しやすい。

Hypotheses:
- repository に `DOCUMENTATION_REFERENCE_ONLY` label が追加されれば、この item は再分類すべき。

Conclusions:
- この item は investigation / triage / QA matrix の導線であり、child behavior-change section ごとに AOSP evidence を取る必要がある。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ | 結論 |
| --- | --- |
| Documentation cross-reference only | runtime impact なし |
| Android 16 / targetSdkVersion 35 / all-apps changes | 対象 |
| Android 16 / targetSdkVersion 36 / all-apps changes | 対象 |
| Android 16 / targetSdkVersion 35 / target-only changes | 原則対象外 |
| Android 16 / targetSdkVersion 36 / target-only changes | 対象 |
| Android 15 / targetSdkVersion 36 | target-only child section ごとに確認 |
| Android 16 OS update only | all-apps changes を重点確認 |
| targetSdkVersion 36 migration only | target-only changes を重点確認 |
| OS update plus target migration | all-apps + target-only の両方を確認 |

## テスト観点（Test Viewpoints）

- Android 15 / targetSdkVersion 35
- Android 16 / targetSdkVersion 35
- Android 16 / targetSdkVersion 36
- Android 15 / targetSdkVersion 36
- runtime `Build.VERSION.SDK_INT`
- manifest targetSdkVersion
- compileSdkVersion と targetSdkVersion の区別
- all-apps report と target-only report の分類混同がないこと
- customer-facing explanation が OS update impact と targetSdkVersion migration impact を分けていること

## Human Decision Placeholder

最終優先度（Final Priority）:
- TBD by human

最終 severity（Final Severity）:
- TBD by human

顧客説明優先度（Customer communication priority）:
- TBD by human

分類ラベル追加要否（Need repository classification label update）:
- TBD by human

リリース判定（Release readiness decision）:
- TBD by human

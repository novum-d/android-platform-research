# BC-010: Virtual device owner overrides

## 基本情報

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/16/behavior-changes-all#virtual-device-owner-overrides
- Section: Virtual device owner overrides

既存調査:
- [android16/behavior-changes/all/device-form-factors/virtual-device-owner-overrides.md](../../../behavior-changes/all/device-form-factors/virtual-device-owner-overrides.md)
- [android16/summaries/all/device-form-factors/virtual-device-owner-overrides-summary.md](../../../summaries/all/device-form-factors/virtual-device-owner-overrides-summary.md)

## 対象アプリとの関係

関連するアプリ機能:
- PC / car / Chromebook / VR への projection。
- companion app streaming。
- external display 上の live view / remote control。
- fixed orientation / non-resizable UI。

アプリが該当する可能性:
- Conditional。virtual device owner projection で使われる場合に該当。

## 適用条件分類

主分類:
- `OS_UPDATE_ALL_APPS`

必要条件:
- Android 16。
- trusted / privileged virtual device owner。
- selected virtual display で override enabled。
- app が projected display 上で実行される。

Confidence:
- High。

## AOSP / 公式根拠

既存 Android16 調査で確認済み:
- `VirtualDisplayConfig.Builder#setIgnoreActivitySizeRestrictions(boolean)`。
- trusted display requirement。
- WindowManager の orientation / aspect ratio / resizability policy が display setting を参照。
- local physical display の通常実行とは別。

## アプリ影響

想定される影響:
- projection 上で fixed orientation / aspect ratio / resizability restrictions が無視される。
- car display / PC / Chromebook で phone portrait UI が崩れる。
- local phone display では問題が出ないため QA で見落としやすい。

推奨対応:
- projection use case の有無を確認する。
- external display / virtual display で camera live view、remote control、image viewer をテストする。
- WindowMetrics / Configuration / input modality を記録する。

## テスト観点

- local physical display。
- virtual device owner projection。
- selected virtual device override enabled / disabled。
- PC / VR / car / Chromebook。
- orientation / aspect ratio / resizability restriction respected / ignored。

## Human Decision

- Final priority: TBD by human
- Release readiness impact: TBD by human

# Android 16 対応例一覧

このディレクトリは、Android 16 Behavior Changesを実装・設定・テストへ落とすためのcompanion examplesである。

[Android 16対応例テンプレート](../../templates/implementation-examples-template.md)を使用する。
根拠、適用条件、classification、confidence、Human Decisionは[Behavior Changes一覧](../README.md)と各主レポートを正とする。

## 対応例

| 対応例 | 主な内容 | 主レポート |
| --- | --- | --- |
| [Adaptive layouts](adaptive-layouts-implementation-examples.md) | Compose、Navigation 3、adaptive grid、state restoration、screenshot test | [Adaptive layouts](../target/device-form-factors/adaptive-layouts.md) |
| [Fixed rate work scheduling optimization](fixed-rate-work-scheduling-optimization-implementation-examples.md) | fixed-rate callback、reconciliation、Timer / executor、test | [Fixed rate work scheduling optimization](../target/core-functionality/fixed-rate-work-scheduling-optimization.md) |
| [Predictive Back](migration-or-opt-out-required-for-predictive-back-implementation-examples.md) | Compose / Views、dispatcher、animation、temporary opt-out、test | [Migration or opt-out required for Predictive Back](../target/user-experience-and-system-ui/migration-or-opt-out-required-for-predictive-back.md) |

## ディレクトリ責務

- Kotlin、Java、Manifest、XML、native、testの具体例はこのディレクトリへ置く。
- Before / Afterを含む`*-implementation-examples.md`は`case-guides/`へ置かない。
- `case-guides/`にはケース選択、カテゴリ別対応手順、Manifest / APIなどの挙動ガイドを置く。
- 実装例は完成品ではなく、対象アプリのarchitectureへ調整して組み込む移行例として扱う。
- 実機・projectで実行していない結果はObservedまたはPassにしない。

## Human Decision

このファイル群では最終priority、severity、release readiness、customer communication priorityを決定しない。

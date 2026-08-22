# [Behavior Change Title] - Android 17 対応例

## 位置づけ

このファイルは主レポートの対応候補を、実装・設定・検証へ落とすcompanionである。
classification、confidence、AOSP evidence、Human Decisionは主レポートを正とする。

- 主レポート:
- 1ページ要約:
- Android 16→17挙動比較:

## 対象と適用条件

- Android OS:
- targetSdkVersion:
- API / device / permission / process条件:
- Compat Change ID / feature flag:
- 対象外:

## 使い方

- 掲載するコードはそのまま貼り付けて使う完成品ではなく、対象アプリの既存architectureへ調整して組み込む移行例として扱う。
- state management、navigation、dependency injection、error policy、lifecycle、threading、test strategyのうち、各例に関係する調整点を明記する。
- 「既存実装の検出」「移行前」「移行後」「失敗処理」「検証」をセットで記載する。
- API level、permission、targetSdk、OEM / module条件を省略しない。
- temporary opt-outには適用範囲、risk、削除条件を付ける。
- primary reportでgate未解決のAPIは、確定実装例ではなく検証用pseudocodeとして明記する。

## 移行対象の見つけ方

```bash
rg -n "<API|manifest|pattern>" app src
```

| Existing pattern | Android 17対応 | 優先度 | 理由 |
| --- | --- | --- | --- |
| [記入] | [記入] | Must / Recommended / Optional | [記入] |

## 対応方針

- 推奨:
- 一時対応:
- 避ける:

## 例1: [Scenario]

目的:

- [記入]

移行前:

```kotlin
// Before
```

移行後:

```kotlin
// After
```

既存architectureへの調整点:

- [記入]

失敗処理:

- [記入]

検証:

- Android 16 / targetSdkVersion 36:
- Android 17 / targetSdkVersion 36:
- Android 17 / targetSdkVersion 37:

## 例2: [Manifest / XML / Native / Test]

```xml
<!-- Example -->
```

既存architectureへの調整点:

- [記入]

注意:

- [記入]

## 完了条件

- 対象コードを検出した。
- Android 16 baselineを記録した。
- Android 17 / target 36とtarget 37を分離した。
- success / denial / revoke / exception / process deathを必要に応じて確認した。
- ObservedをExpectedから分離した。

## References

- 公式文書:
- 主レポート:
- 比較資料:

## Human Decision

この対応例では最終priority、severity、release readinessを決定しない。
主レポートまたはdecision logの人間による判断を参照する。

# [Behavior Change] - Android [Baseline] → [Target] 挙動比較

このテンプレートは、同じアプリ、同じ初期状態、同じ操作または system event
に対して、Android OS バージョン間で実行時挙動がどう変わるかを説明するための
companion file である。

主レポートの classification、confidence、evidence、Human Decision を再判定しない。
それらは主レポートを正とし、このファイルでは読者が挙動差と対応手順を追える形に
変換する。

---

## 1. 関連資料と比較範囲

- Behavior Change:
- 主レポート:
- 1ページ要約:
- 関連 companion:
- 比較対象:
- 比較対象外:

| 項目 | Baseline | Target |
| --- | --- | --- |
| Android OS | Android [N] | Android [N+1] |
| AOSP tag | `android-[N tag]` | `android-[N+1 tag]` |
| targetSdkVersion | [同一値を記載] | [同一値を記載] |
| アプリ build | [version / commit] | [同一 version / commit] |
| 端末 / OEM | [device] | [device] |
| transport / API | [条件] | [同一条件] |

主分類:
- 主レポートの分類を引用する。ここでは再判定しない。

信頼度:
- 主レポートの信頼度を引用する。

## 2. 比較契約（Comparison Contract）

比較で固定する条件:

- アプリ build:
- targetSdkVersion:
- manifest / permission:
- feature flag / compat change:
- 端末 role:
- 接続方式 / transport:
- 初期状態:
- 入力または trigger:
- foreground / background:
- network / accessory condition:

固定できない条件と理由:

- [条件]:

> OS 差を検証する行では、上記以外を同じにする。targetSdkVersion やアプリ実装も
> 変更する場合は別の比較行とし、OS 差と混ぜない。

## 3. 用語

| 用語 | この資料での意味 |
| --- | --- |
| Baseline | 比較元の Android OS 上の挙動 |
| Target | 比較先の Android OS 上の挙動 |
| System behavior | framework / system service / module が実行する処理 |
| App-visible signal | broadcast、callback、例外、return value、状態値など、アプリから観測できる情報 |
| Expected | 公式文書と AOSP 根拠から導いた期待結果 |
| Observed | 実機または自動テストで実際に観測した結果 |

必要に応じて Behavior Change 固有の用語を追加する。

## 4. 先に結論

[同じ trigger に対して何が変わり、アプリのどの前提が成立しなくなるかを 3～5 文で説明する。]

| 観点 | Android [Baseline] | Android [Target] | アプリへの影響 |
| --- | --- | --- | --- |
| trigger 後の system 処理 |  |  |  |
| 状態遷移 |  |  |  |
| app-visible signal |  |  |  |
| system UI |  |  |  |
| recovery の主体 |  |  |  |

## 5. 同一条件での状態遷移

### Android [Baseline]

```text
[Initial state]
-> [Trigger]
-> [System action]
-> [App-visible signal]
-> [End state]
```

### Android [Target]

```text
[Initial state]
-> [Trigger]
-> [Changed system action]
-> [Changed app-visible signal]
-> [End state]
```

差分の要点:

- 追加された処理:
- 削除された処理:
- 条件が変わった処理:
- default が変わった処理:
- 変わらない処理:

## 6. シナリオ別比較

最低限、通常経路、失敗経路、回復経路、OEM / fallback を検討する。
該当しないシナリオは理由を記載して削除してよい。

### Scenario 1: [代表的な通常経路]

前提:

- [記入]

| Phase | Android [Baseline] | Android [Target] |
| --- | --- | --- |
| 1. 初期状態 |  |  |
| 2. trigger |  |  |
| 3. system 処理 |  |  |
| 4. app-visible signal |  |  |
| 5. 終了状態 |  |  |

アプリの対応:

1. [記入]
2. [記入]

### Scenario 2: [失敗または retry 経路]

前提:

- [記入]

| Phase | Android [Baseline] | Android [Target] |
| --- | --- | --- |
| 1. 初期状態 |  |  |
| 2. trigger |  |  |
| 3. system 処理 |  |  |
| 4. app-visible signal |  |  |
| 5. 終了状態 |  |  |

無限 retry、二重 UI、誤った状態判定が起きないかを記載する。

### Scenario 3: [回復経路]

- 回復開始条件:
- Baseline の回復手順:
- Target の回復手順:
- 回復完了を判断する signal:

### Scenario 4: OEM / fallback

- AOSP default:
- OEM 差が想定される箇所:
- primary signal がない場合の fallback:
- transient failure と確定的な behavior change event の区別:

## 7. OS 差と targetSdkVersion 差

| Android OS | targetSdkVersion | System behavior | App-visible API / signal | 判定 |
| --- | --- | --- | --- | --- |
| Android [Baseline] | previous target |  |  |  |
| Android [Baseline] | target target |  |  |  |
| Android [Target] | previous target |  |  |  |
| Android [Target] | target target |  |  |  |

注意:

- OS update だけで変わる処理:
- targetSdkVersion update で変わる処理:
- API level / permission / manifest により観測可否だけが変わる処理:
- Compat Change ID と default state:

## 8. System behavior とアプリ観測の対応

| System event / state | App-visible signal | Baseline | Target | 注意点 |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

アプリから観測できない system 内部状態を、単一 callback だけから断定しない。

## 9. アプリ側の対応手順

### 最小対応

1. [記入]
2. [記入]
3. [記入]

### 推奨状態モデル

| App state | 進入条件 | 許可する処理 | 終了条件 |
| --- | --- | --- | --- |
|  |  |  |  |

### やってはいけない前提

- [記入]

## 10. 検証仕様

### テストマトリクス

| Case | OS | targetSdk | 初期状態 | Trigger | Expected | Observed |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Android [Baseline] |  |  |  |  | 未実施 |
| 2 | Android [Target] |  |  |  |  | 未実施 |

### 観測点

- app callback / broadcast:
- system UI:
- framework state:
- logcat:
- dumpsys:
- module / protocol log:

### 合格条件

- 同一条件で baseline / target の差を再現できる。
- OS 差と targetSdkVersion 差を個別に説明できる。
- Expected と Observed を混同していない。
- primary signal がない端末でも fallback 手順が暴走しない。

## 11. Facts / Observations / Hypotheses / Conclusions

### Facts

- [記入]

### Observations

- 実機未検証の場合は「未実施」と記載する。

### Hypotheses

- [記入]

### Conclusions

- [記入]

## 12. Evidence と信頼度

| Fact | Evidence | Confidence |
| --- | --- | --- |
|  |  | High / Medium / Low |

確認した AOSP source context:

| File / symbol / caller | Baseline | Target | 関連性 |
| --- | --- | --- | --- |
|  |  |  |  |

除外した経路:

- [記入]

## 13. 制約と未検証事項

- [記入]

## 14. References

Entry Point:

- 公式 Behavior Change 文書:

Primary evidence:

- 主レポート:
- AOSP:

Related:

- 1ページ要約:
- 関連 companion:

## 15. Human Decision

この companion file では判断しない。主レポートおよび対象 version の
decision log を参照する。

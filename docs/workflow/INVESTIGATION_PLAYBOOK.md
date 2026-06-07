# Investigation Playbook

このファイルは、Behavior Change セクションを顧客向け調査レポートへ落とし込む標準手順をまとめたものです。

## Standard Flow

1. Behavior Changes の対象セクションを決める
2. 公式ドキュメントの原文を抜き出す
3. 調査対象バージョンを確認する
4. Behavior Change の適用条件を一次分類する
5. 関連AOSPファイルを特定する
6. 差分を確認する
7. AOSP の gate と compat framework の default state で適用条件を検証する
8. 事実・観察・仮説・結論を分ける
9. 顧客説明向けレポートを書く
10. 1ページ要約を書く
11. 人間が重要度・最終結論を判断する
12. DECISION_LOG に残す

## Applicability Classification

公式ドキュメントのページ種別で一次分類する。

| Documentation page | Initial classification | Required verification |
| --- | --- | --- |
| `behavior-changes-all` | OS update / all apps | AOSP に targetSdkVersion gate がないこと、または targetSdkVersion に依存しない gate であること |
| `behavior-changes-<version>` | targetSdkVersion <api>+ | AOSP に targetSdkVersion <api>、compat ChangeId、または API <api> 条件の gate があること |
| `compat-framework-changes` | compat framework controlled | Change ID、change name、default state、toggleability が Behavior Change と一致すること |
| API reference / release note only | API addition or supporting evidence | Behavior Change 原文に紐づけられること |

分類は以下のいずれかを必ず選ぶ。

- OS update / all apps on target Android version regardless of targetSdkVersion
- targetSdkVersion >= target API on target Android version+
- targetSdkVersion >= target API, with additional runtime conditions
- Mainline / Google Play system update dependent
- API addition only, not a behavior change
- Unknown / needs more evidence

## AOSP Gate Checks

適用条件の検証では、関連ファイル内で以下を確認する。

- `targetSdkVersion`
- `ApplicationInfo.targetSdkVersion`
- `Build.VERSION.SDK_INT`
- target release `Build.VERSION_CODES.<codename>`
- `CompatChanges.isChangeEnabled`
- `@ChangeId`
- `@EnabledAfter`
- `@EnabledSince`
- `@Disabled`
- `DeviceConfig`
- resource config
- manifest property
- permission / AppOps check

gate が見つからない場合は、`No gate found` と明記し、OS update / all apps と解釈できるかを追加確認する。gate 不明のまま High confidence にしない。

## AOSP Source Context

AOSP 根拠は、ファイル名だけでは不十分。各レポートでは、どの部分を見てどのような差分だと判断したかを必ず明記する。

必須項目:

- file / symbol / entry point / caller
- そのコードパスが Behavior Change の根拠になる理由
- baseline Android version の挙動
- target Android version behavior の挙動
- 差分の種類: added behavior / removed behavior / changed condition / changed default / no behavior change
- 適用 gate 判断とのつながり
- 無関係または対象外と判断したコードパスがある場合、その理由

書き方:

```text
Source context:
- Reviewed: <file>::<symbol>
- Entry path: <app API or system event> -> <service/class> -> <changed branch>
- Baseline Android behavior: <what happened before>
- Target Android behavior: <what happens now>
- Diff interpretation: <added/removed/gated/default changed>
- Applicability reasoning: <why this means OS update / targetSdkVersion update / conditional / unknown>
```

## Verification Matrix

各レポートは最低限、次の期待結果を分ける。

| Device OS | targetSdkVersion | Compat flag | Purpose |
| --- | --- | --- | --- |
| Baseline Android version | previous targetSdkVersion | default | old behavior baseline |
| Target Android version | previous targetSdkVersion | default | OS update impact |
| Target Android version | new targetSdkVersion | default | targetSdkVersion update impact |
| Target Android version | previous targetSdkVersion | force-enabled if available | isolated targeted change |
| Target Android version | new targetSdkVersion | force-disabled if available | rollback/opt-out behavior |

## Confidence Rule

High confidence は、公式原文、AOSP gate、compat framework default state、顧客影響説明が整合している場合のみ付与する。

Medium confidence は、公式原文と AOSP gate は確認したが、compat framework、CTS、実機再現、または例外条件の確認が不足している場合。

Low confidence は、公式原文または AOSP gate のいずれかが未確認、もしくは分類が `Unknown / needs more evidence` の場合。

## Commands

```bash
git -C frameworks-base diff --name-only <from-tag> <to-tag>
git -C frameworks-base diff <from-tag> <to-tag> -- <file>
git -C frameworks-base grep -n "targetSdkVersion\\|ApplicationInfo.targetSdkVersion\\|CompatChanges.isChangeEnabled\\|@ChangeId\\|@EnabledAfter\\|@EnabledSince" <to-tag> -- <file-or-dir>
```

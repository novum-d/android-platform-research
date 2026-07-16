# [Behavior Change / API] - 実行挙動比較（Runtime Behavior Comparison）

## 位置づけ（Scope）

このファイルは、同じ入力条件に対する複数 API / 実装方式の実行順序、実行時刻、callback 選択、fallback を比較する companion document である。
Behavior Change の根拠、適用条件、classification、confidence、Human Decision は primary report / one-page summary を正とする。

Primary report:
- `<relative path>`

One-page summary:
- `<relative path>`

Implementation examples:
- `<relative path>`

## 対象（Target）

Android Behavior Change / API:
- Document: `<URL>`
- Section: `<Section Name>`

適用条件の要点:
- OS アップデート / 全アプリ:
- targetSdkVersion:
- その他の必須条件:

## 使い方（How to Use）

- 比較対象には同じ入力、初期状態、clock、thread / lifecycle 条件を与える。
- conceptual timeline、API 仕様から導く expected behavior、実機で観測した observed behavior を分ける。
- 「処理される / されない」だけでなく、入口、選択順、開始、終了、次回予定、fallback を記録する。
- production code と挙動確認用の `sleep` / fake clock / event recorder を混同しない。
- API の優劣を一律に決めず、要件との対応関係を Human Decision の入力として示す。

## 比較契約（Comparison Contract）

| 条件 | 値 |
| --- | --- |
| Initial state | `<state>` |
| Input / event | `<input>` |
| Initial delay | `<duration / N/A>` |
| Period / delay | `<duration / N/A>` |
| Task duration | `<duration / N/A>` |
| Pause / freeze interval | `<interval / N/A>` |
| Thread / callback owner | `<owner>` |
| Android version | `<version>` |
| targetSdkVersion | `<version>` |
| Compat / manifest state | `<state>` |
| Clock | `<elapsed / wall clock / N/A>` |

比較を変える条件:
- `<condition>`

比較から除外する条件:
- `<excluded condition and reason>`

## 比較対象（Comparison Targets）

| ID | API / implementation | Entry point | Selection / scheduling semantics | Fallback |
| --- | --- | --- | --- | --- |
| A | `<API A>` | `<entry>` | `<semantics>` | `<fallback>` |
| B | `<API B>` | `<entry>` | `<semantics>` | `<fallback>` |
| C | `<API C>` | `<entry>` | `<semantics>` | `<fallback>` |

## 早見比較（At-a-Glance）

| 比較項目 | A | B | C |
| --- | --- | --- | --- |
| 基準時刻 / event source | `<value>` | `<value>` | `<value>` |
| 最初に選ばれる処理 | `<value>` | `<value>` | `<value>` |
| 遅延 / unhandled 時 | `<value>` | `<value>` | `<value>` |
| 次回 / fallback | `<value>` | `<value>` | `<value>` |
| lifecycle / cancel | `<value>` | `<value>` | `<value>` |
| 主なリスク | `<value>` | `<value>` | `<value>` |

## 用語（Terminology）

- Planned / selected: `<definition>`
- Actual start / invoked: `<definition>`
- Actual end / consumed: `<definition>`
- Next / fallback: `<definition>`
- Missed / unhandled: `<definition>`

## 共通の観測コード（Common Instrumentation）

目的:
- 比較対象ごとに同じ event format を記録する。

```kotlin
data class RuntimeEvent(
    val implementation: String,
    val invocation: Int,
    val event: String,
    val elapsedMillis: Long,
    val state: String,
)
```

記録する event:
- `input`
- `selected` / `scheduled`
- `start` / `invoked`
- `end` / `consumed`
- `next` / `fallback`
- `cancelled` / `exception`

注意点:
- 実時間を使う manual test と fake clock を使う unit test を分ける。
- `Thread.sleep` を使う場合は挙動確認専用であることを明記する。

## Scenario 1: 通常状態（Normal Path）

### 条件

- `<condition>`

### Expected timeline / flow

```text
<timeline or event flow>
```

### 実行記録

| Invocation | Planned / input | Actual start / invoked | Actual end / consumed | Next / fallback |
| ---: | --- | --- | --- | --- |
| 1 | `<value>` | `<value>` | `<value>` | `<value>` |

### 解釈

- `<what is equal>`
- `<what differs>`

## Scenario 2: 遅延 / callback 競合（Delayed or Competing Path）

### 条件

- `<condition>`

### Expected timeline / flow

```text
<timeline or event flow>
```

### 比較

| Implementation | 実行 / callback 順 | 回数 | Next / fallback | 結果 |
| --- | --- | ---: | --- | --- |
| A | `<order>` | `<count>` | `<value>` | `<result>` |
| B | `<order>` | `<count>` | `<value>` | `<result>` |

## Scenario 3: 長時間処理 / handler が処理しない場合

### 条件

- `<condition>`

### Expected timeline / flow

```text
<timeline or event flow>
```

確認すること:
- 重複または再帰が発生するか。
- 後続処理 / fallback に到達するか。
- 終了後の next state が一致するか。

## Scenario 4: 例外 / cancel / lifecycle 終了

確認すること:
- 例外後も次回処理が継続するか。
- cancel / owner destruction 後に callback や task が残らないか。
- fallback や process recreation で処理が重複しないか。

## Android バージョン / 設定比較

| OS | targetSdkVersion | Compat / manifest | Expected behavior | Notes |
| --- | ---: | --- | --- | --- |
| `<OS>` | `<target>` | `<state>` | `<behavior>` | `<notes>` |

## Expected / Observed

| Scenario | Expected | Observed | Result | Evidence |
| --- | --- | --- | --- | --- |
| Normal | `<expected>` | `<observed / 未実施>` | Pass / Fail / 未実施 | `<log / test>` |
| Delayed / competing | `<expected>` | `<observed / 未実施>` | Pass / Fail / 未実施 | `<log / test>` |
| Long / unhandled | `<expected>` | `<observed / 未実施>` | Pass / Fail / 未実施 | `<log / test>` |

## 実装選択マップ（Implementation Decision Input）

| 要件 | 実装候補 | 理由 | 追加確認 |
| --- | --- | --- | --- |
| `<requirement>` | `<implementation>` | `<reason>` | `<verification>` |

この表は最終優先度や採用 API を決定しない。最終判断は Human Decision とする。

## テスト仕様（Verification Specification）

- Given: `<initial state>`
- When: `<input / event>`
- Then: `<expected order / count / state>`
- And: `<fallback / next state>`

必要なテスト層:
- Unit / fake clock:
- JVM / Robolectric:
- Instrumentation:
- Manual / device:

## Fact / Evidence / Confidence

| Fact | Evidence | Confidence |
| --- | --- | --- |
| `<fact>` | `<official doc / source / test>` | High / Medium / Low |

## References

### Entry Point

- `<Behavior Change URL>`

### Official Documentation

- `<API / migration guide URL>`

### Source Code

- `<AOSP / library source URL>`

### Validation

- `<test / log / sample project>`

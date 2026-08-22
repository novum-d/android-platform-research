# Safer Intents: Testing and debugging

## 調査メタデータ

- Android version: Android 16
- Version directory: `android16`
- From tag: `android-15.0.0_r36`
- To tag: `android-16.0.0_r4`
- Previous targetSdkVersion: 35
- Target targetSdkVersion: 36
- Behavior Change section: Testing and debugging
- Parent section: Safer Intents
- Official documentation URL: https://developer.android.com/about/versions/16/behavior-changes-16#testing-and-debugging
- Official documentation category: Security
- Applicability classification: `OPT_IN_ONLY`
- Confidence: High


Confidence note: 公式文書はAndroid 16初期impactをmanifest opt-inに限定している。AOSPでも`android:intentMatchingFlags` / feature flag / cross-app resolutionが実際の適用条件であり、targetSdkVersion 36だけでは有効にならないことを確認できるため、`OPT_IN_ONLY`としてHigh confidenceとする。

## Official Documentation Review

2026-07-03 に公式ドキュメントの Safer Intents / Testing and Debugging セクションを再確認した。対象ページは 2026-07-01 UTC 更新として表示されていた。

確認した公式本文:

- enforcement が active の場合、intent caller が intent を正しく populate していれば app は正しく機能する。
- blocked intents は `PackageManager` tag で warning log を出す。
- message 例は `"Intent does not match component's intent filter:"` と `"Access blocked:"`。
- これは app に影響し得る潜在的問題を示し、対応が必要。
- logcat filter 例は `tag=:PackageManager & (message:"Intent does not match component's intent filter:" | message: "Access blocked:")`。

依頼文との差分:

- 依頼文に含まれる same-app / multiple-app 条件と `android:intentMatchingFlags` の application / component level 制御は、Testing subsection 本文ではなく Safer Intents 親項目および Implementation 文脈に属する。調査では AOSP evidence として確認し、本 report に含める。
- 依頼文の「Use these logs to identify and fix mismatched intents」は公式 Testing subsection の趣旨と一致するが、同じ文言としては確認していない。

## Facts

### Manifest attribute / flags

Android 16 の `attrs_manifest.xml` には `android:intentMatchingFlags` が定義されている。

指定可能な tags:

- `<application>`
- `<activity>`
- `<activity-alias>`
- `<receiver>`
- `<service>`
- `<provider>`

Supported flags:

- `none` (`0x0001`): special matching rules を無効化する。
- `enforceIntentFilter` (`0x0002`): explicit intents は target component の intent filter と一致し、action がない intents は intent filter に match しない、という stricter matching を適用する。
- `allowNullAction` (`0x0004`): `enforceIntentFilter` と併用し、action が null の intent を許可する。

Reviewed source:

- `core/res/res/values/attrs_manifest.xml`
- `core/api/current.txt`
- `core/res/res/values/public-final.xml`

### Manifest parsing / override

Application-level flags は `ParsingPackageUtils` が読み取る。Component-level flags は activity / activity-alias / receiver / service / provider parsing path で読み取られる。

`ParsedMainComponentUtils.resolveIntentMatchingFlags(applicationFlags, componentFlags)` は、component flags が 0 の場合は application flags を継承し、component flags が指定されている場合は component flags を優先する。

Unit test evidence:

- `ParsedMainComponentUtilsTest#testResolveIntentMatchingFlags`
- application-level `enforceIntentFilter` + component-level `none` は `none`
- application-level `enforceIntentFilter|allowNullAction` + component-level `enforceIntentFilter` は `enforceIntentFilter`
- application-level 未指定 + component-level `enforceIntentFilter|allowNullAction` は component flags

### Warning log and actual block path

PackageManager の resolution path は `SaferIntentUtils.enforceIntentFilterMatching(...)` を呼ぶ。

Android 16 の manifest opt-in path:

- `Flags.enableIntentMatchingFlags()` が true の場合、`enforceIntentFilterMatchingWithIntentMatchingFlags(...)` が使われる。
- caller が system / root 相当の場合は skip。
- caller と target component が same app の場合は `UserHandle.isSameApp(...)` で skip。
- target component に intent filters がない場合は skip。
- component flags が 0、`none`、または `enforceIntentFilter` を含まない場合は enforcement しない。
- `enforceIntentFilter` が有効で、incoming intent が filter mismatch、または action が null かつ `allowNullAction` がない場合、`blockIntent = true` になる。
- `blockIntent = true` の場合に warning log が出る。
- warning log の直後に `resolveInfos.remove(i)` が呼ばれ、該当 component は resolution result から除外される。

Reviewed source:

- `services/core/java/com/android/server/pm/SaferIntentUtils.java`
- `services/core/java/com/android/server/pm/ComputerEngine.java`
- `services/core/java/com/android/server/pm/ResolveIntentHelper.java`

Warning messages:

- `"Intent does not match component's intent filter: " + args.intent`
- `"Access blocked: " + comp.getComponentName()`

Tag:

- `PackageManager` (`PackageManagerService.TAG` 経由)

### Debugging signals beyond warning log

`SaferIntentUtils.reportUnsafeIntentEvent(...)` は unsafe intent event を `FrameworkStatsLog.UNSAFE_INTENT_EVENT_REPORTED` に書き、`ActivityManagerInternal.triggerUnsafeIntentStrictMode(...)` を呼ぶ。

`IntentArgs.reportEvent(...)` は `resolveForStart` の場合だけこの報告を行う。Android 16 opt-in path では、null action または filter mismatch の場合に reportEvent が呼ばれ、blocked かどうかは boolean として渡される。

重要な分離:

- `PackageManager` warning log は `blockIntent = true` の場合に出るため、actual block と強く対応する。
- unsafe intent stats / StrictMode signal は mismatch 検出時に報告され得るが、`blocked` boolean が false の場合もあり得る。
- `Intent.EXTENDED_FLAG_FILTER_MISMATCH` は `Flags.enforceIntentFilterMatch()` が true で、null action または filter mismatch の場合に付与され得る。これは warning log と同一条件ではない。

Reviewed source:

- `services/core/java/com/android/server/pm/SaferIntentUtils.java`
- `services/core/java/com/android/server/am/ActivityManagerService.java`
- `core/java/android/os/StrictMode.java`
- `core/java/android/content/Intent.java`

### App-compat fallback path

`SaferIntentUtils` には Android 15 由来の AppCompat path も残っている。

- Change ID: `161252188`
- Symbol: `ENFORCE_INTENTS_TO_MATCH_INTENT_FILTERS`
- Annotation: `@Disabled`
- `@Overridable`

`IntentFilter.BLOCK_NULL_ACTION_INTENTS` は Change ID `293560872` で `@Disabled`。ただし Android 16 の documented Safer Intents opt-in behavior は manifest `android:intentMatchingFlags` path が主対象である。

公式 Android 16 compat framework changes ページでは、2026-07-03 の検索時点で Safer Intents 関連 entry は確認できなかった。

## Observations

### Testing subsection の中心は blocked intent log

公式 Testing and Debugging は、`PackageManager` warning log を見て mismatched intents を検出する guidance である。AOSP 実装上、該当 warning は block path 内で出るため、log が出た場合は component が resolution result から除外された可能性が高い。

### Warning log が出ない代表条件

次の条件では warning log は出ない、または出ない可能性が高い。

- `android:intentMatchingFlags` 未指定
- component flags が `none`
- component flags に `enforceIntentFilter` がない
- same-app caller
- system / root 相当 caller
- target component に intent filter がない
- explicit intent が target component の intent filter に match する
- null action intent だが `allowNullAction` が指定されている

### Warning log と telemetry / StrictMode は同じではない

`PackageManager` warning log は actual block の debugging signal として扱える。一方、unsafe intent event / StrictMode / `EXTENDED_FLAG_FILTER_MISMATCH` は mismatch 検出や diagnostic 用の signal であり、必ずしも app-facing block と同義ではない。

### targetSdkVersion gate

AOSP の `intentMatchingFlags` parsing / enforcement path では、targetSdkVersion 36 を直接確認する gate は見つからなかった。公式 behavior change page は target SDK 36 以上向けだが、実装上の主 gate は manifest opt-in である。

### Future roadmap

公式 Safer Intents 文脈では将来 default behavior へ広げる計画が説明されている。一方、`android-16.0.0_r4` の AOSP evidence では future default / opt-out / mandatory enforcement の具体的 API level gate、TODO、公開 compat entry は確認できなかった。

## Hypotheses

- targetSdkVersion 35 のアプリでも、Android 16 上で `android:intentMatchingFlags` が parser に認識され、`enforceIntentFilter` が保存される場合、実装上は enforcement 対象になる可能性がある。
- 実務上は Android 16 SDK で `intentMatchingFlags` が public final attr になるため、targetSdkVersion 36 化と同時に opt-in するケースが中心になる可能性が高い。
- warning log を QA / CI で検出できれば、外部 partner app からの legacy explicit intent mismatch を release 前に発見できる可能性が高い。

これらは AOSP 実装からの推論であり、実機 / CTS / SDK tooling で追加確認すべきである。

## Applicability Classification

Primary classification: `OPT_IN_ONLY`

追加条件:

- Android 16 以上の platform / `enable_intent_matching_flags` feature flag が有効
- receiving app または receiving component が `android:intentMatchingFlags` で `enforceIntentFilter` に opt-in
- cross-app intent resolution が発生
- target component が intent filter を持つ
- incoming explicit intent が filter に match しない、または action が null で `allowNullAction` がない

Classification caveat:

- AOSP evidence では targetSdkVersion 36 gate は確認できなかった。
- `OPT_IN_ONLY` は、公式文書の opt-in statement と AOSP manifest opt-in gate に直接対応する分類。
- 顧客向けには「Android 16 へ OS update しただけ」「targetSdkVersion 36 にしただけ」「manifest opt-in した時」「warning log が出る時」「actual block が起きる時」を分けて説明する。

Compat framework:

- AppCompat fallback path: `ENFORCE_INTENTS_TO_MATCH_INTENT_FILTERS` (`161252188`), `@Disabled`, `@Overridable`
- Null action fallback path: `IntentFilter.BLOCK_NULL_ACTION_INTENTS` (`293560872`), `@Disabled`
- Android 16 documented opt-in path: manifest `android:intentMatchingFlags`
- 公式 compat framework changes ページでは Safer Intents 関連 entry は確認できなかったため、force-enable / force-disable は公式 evidence から断定しない。

## Expected Behavior Matrix

| Scenario | Expected behavior | Debugging signal |
|---|---|---|
| Android 16 / targetSdkVersion 35 | `intentMatchingFlags` 未指定なら従来挙動。AOSP 上、opt-in 指定があれば enforcement される可能性は残る | 通常 warning なし |
| Android 16 / targetSdkVersion 36 | `intentMatchingFlags` 未指定なら従来挙動。opt-in した receiving app / component だけ enforcement | opt-in + mismatch で warning |
| Android 15 / targetSdkVersion 36 | Android 16 documented opt-in behavior の対象外。attr / feature flag 状態は platform build 依存 | 参考扱い |

## Detailed Scenario Matrix

| Scenario | Expected behavior / signal |
|---|---|
| Android 16 / targetSdkVersion 36 / no `android:intentMatchingFlags` | enforcement なし。warning log なし |
| application-level `enforceIntentFilter` | component が override しなければ app 内 components に継承 |
| component-level `enforceIntentFilter` | 該当 component に enforcement |
| application-level `enforceIntentFilter` + component-level `none` | 該当 component は enforcement なし。warning log なし |
| `enforceIntentFilter + allowNullAction` | filter mismatch は block。null action は許容 |
| conflicting flags including `none` | `none` は special matching rules を無効化する意図。component flags 指定時は component が優先 |
| explicit intent matches target component's filter | block されない。warning log なし |
| explicit intent does not match target component's filter | cross-app かつ opt-in 済みなら warning log + block |
| intent without action | `allowNullAction` なしの opt-in component では warning log + block |
| same-app explicit intent | enforcement 対象外。warning log なし |
| cross-app explicit intent | enforcement 対象 |
| exported receiver | cross-app receiver intent が filter 不一致なら warning log + block |
| exported activity | cross-app activity start が filter 不一致なら warning log + block |
| exported service | cross-app service resolution が filter 不一致なら warning log + block |
| external partner app sends legacy explicit intent | filter/action が合わなければ warning log + integration failure |
| blocked intent warning log appears | `PackageManager` tag に 2 種類の warning。actual block と強く対応 |
| warning log absent because same-app | same-app skip |
| warning log absent because opt-in disabled | enforcement disabled |
| `Intent.EXTENDED_FLAG_FILTER_MISMATCH` set | feature flag と mismatch 条件に依存。block と同義ではない |
| StrictMode or unsafe intent telemetry signal | `resolveForStart` かつ mismatch/null action で報告され得る。blocked boolean を別途見る必要 |

## Developer Impact

影響対象:

- Safer Intents に opt-in するアプリ
- exported activity / receiver / service / provider を持つアプリ
- cross-app explicit intents を受けるアプリ
- action のない intent を受ける可能性があるアプリ
- intent filter と一致しない explicit intent を受けるアプリ
- partner app / SDK / launcher / shortcut / notification / broadcast sender と連携するアプリ
- deep link / app link / custom action / implicit-to-explicit migration を行っているアプリ
- application-level enforcement と component-level override を混在させるアプリ
- blocked intent log を QA / CI / manual testing で確認する必要があるアプリ
- Safer Intents に opt-in しないが、将来 default enforcement に備える必要があるアプリ

## Recommended Action Candidates

- Android 16 端末で opt-in 済み app を動かし、logcat を `PackageManager` tag と該当 message で filter する。
- warning が出た intent について、送信側 intent の action / category / data / type と受信側 component の intent filter を照合する。
- partner app / SDK / launcher / shortcut / notification / broadcast sender の legacy explicit intent を重点的に検証する。
- 互換性が必要な component は component-level `none` で一時的に除外する。
- null action を許容する正当な要件がある場合だけ `allowNullAction` を使う。
- warning log が出ない場合でも、same-app / opt-in disabled / feature flag disabled の可能性を分けて確認する。

## Test Considerations

- Android 15 端末上の targetSdkVersion 35
- Android 16 端末上の targetSdkVersion 35
- Android 16 端末上の targetSdkVersion 36
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較
- `android:intentMatchingFlags` 未指定
- `android:intentMatchingFlags="enforceIntentFilter"`
- `android:intentMatchingFlags="none"`
- `android:intentMatchingFlags="enforceIntentFilter|allowNullAction"`
- application-level と component-level の override
- explicit intent が target component filter と一致する場合
- explicit intent が target component filter と一致しない場合
- action なし intent
- same-app intent
- cross-app intent
- exported activity / receiver / service / provider
- partner app からの legacy explicit intent
- blocked intent 時の app behavior
- logcat tag `PackageManager` の warning
- warning log が出る場合 / 出ない場合
- `Intent.EXTENDED_FLAG_FILTER_MISMATCH` の有無
- StrictMode / unsafe intent telemetry signal の有無
- fallback / compatibility handling
- future default enforcement を想定した regression testing

## Conclusions

- Testing and Debugging セクションの中心は、blocked intent を `PackageManager` warning log で検出すること。
- AOSP evidence では、warning log は `blockIntent = true` の branch 内で出力され、その直後に `resolveInfos.remove(i)` が実行されるため、actual block と強く対応する。
- same-app intent、opt-in disabled、component-level `none`、filter match、`allowNullAction` 付き null action では warning log が出ない。
- unsafe intent telemetry / StrictMode / `EXTENDED_FLAG_FILTER_MISMATCH` は debugging signal だが、warning log や actual block と同義ではない。
- AOSP evidence では targetSdkVersion 36 gate は確認できないため、「targetSdkVersion 36 化だけで warning / block が出る」と説明してはいけない。

---

## 再検証記録（2026-08-22）

### 調査日（Investigation Date）

- 2026-08-22

### 公式ドキュメント再確認（Original Documentation Recheck）

- Android 16 の all-apps / target Behavior Change ページを再取得し、このレポートが参照する公式 section の掲載と適用範囲を再確認した。
- 公式ページの最終更新表示: all-apps: 2026-08-14 UTC / target: 2026-08-17 UTC。
- Android 16 compat framework 一覧も 2026-08-22 に再取得した。
- 既存の引用は短い要約として扱い、適用条件は公式ページ種別と AOSP gate の両方で再評価した。

### AOSP 証拠ワークスペース（AOSP Evidence Workspaces）

| AOSP project | Official remote URL | Checkout path | Working tree | From tag / resolved commit | To tag / resolved commit | Comparison command | Dirty risk / limitations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `platform/frameworks/base` | `https://android.googlesource.com/platform/frameworks/base` | `frameworks-base/` | Clean | `android-15.0.0_r36` / `396d32905ded85c082232bc510b525c9e372e585` | `android-16.0.0_r4` / `45034f0663f960d9ee5fb0a101a4732b71f6e2f4` | `git -C frameworks-base diff --no-renames --name-only android-15.0.0_r36 android-16.0.0_r4` | なし。明示タグ比較のため working tree の内容は根拠に含めない。 |

### ソース文脈・差分解釈の再確認（Source Context Reviewed / Diff Interpretation）

- 各 official remote で Android 15 / 16 の最新通常リリースタグが `android-15.0.0_r36` / `android-16.0.0_r4` のままであることを確認した。
- 上表の project-level `--name-only` 比較を再実行し、既存本文の path / symbol 別 source context、gate、追加・削除・条件変更・既定値変更・差分なしの解釈を再確認した。
- タグと解決済み commit が既存調査の比較対象から変わっていないため、本文の evidence record を別タグへ機械的に置換していない。
- 実機 Observed は新規実施していない。既存の「未実施」「未確認」および不足根拠はそのまま維持した。

### 事実（Facts）

- `android-15.0.0_r36` と `android-16.0.0_r4` は 2026-08-22 時点の最新通常リリースタグである。
- 上表に再検証時の working tree 状態を記録し、official remote、両タグ、解決済み commit を確認した。展開中または dirty の working tree は根拠に使用していない。
- 公式 section と AOSP evidence の比較 pair は一致している。

### 観察（Observations）

- 最新タグが変わっていないため、今回の再検証で既存の source diff 解釈を変更する新しい AOSP tag evidence は生じなかった。
- report 内に残る Medium / Low confidence、OEM / Mainline / QPR 条件、未確認の module enforcement は解消したものとして扱わない。

### 仮説（Hypotheses）

- 新しい仮説は追加しない。既存本文で仮説または可能性として記載した事項は、実機・製品 build・未確認 module の evidence が得られるまで事実へ昇格しない。

### 結論（Conclusions）

- 既存本文の主分類、confidence、対応候補を維持する。既存の不足根拠がある場合はその制約も維持する。
- 全件再検証の横断記録は [`android16/analysis/REVALIDATION_2026-08-22.md`](../../../analysis/REVALIDATION_2026-08-22.md) を参照する。

### Human Decision

- この再検証では最終 priority、severity、release readiness、顧客説明優先度を変更していない。
- 人間の判断は [Android 16 Decision Log](../../../decisions/DECISION_LOG.md) を正とする。

# Safer Intents

## 調査メタデータ

- Android version: Android 16
- Version directory: `android16`
- From tag: `android-15.0.0_r36`
- To tag: `android-16.0.0_r4`
- Previous targetSdkVersion: 35
- Target targetSdkVersion: 36
- Behavior Change section: Safer Intents
- Official documentation URL: https://developer.android.com/about/versions/16/behavior-changes-16#safer-intents
- Official documentation category: Security
- Applicability classification: `OPT_IN_ONLY`
- Confidence: High


Confidence note: 公式文書は Android 16 初期 impact を manifest opt-in に限定している。AOSP でも `android:intentMatchingFlags` / feature flag / cross-app resolution が実効 gate であり、targetSdkVersion 36 だけでは有効にならないことを確認できるため、`OPT_IN_ONLY` として High confidence とする。

## Official Documentation Review

2026-07-03 に公式ドキュメントの Safer Intents セクションを再確認した。対象ページは 2026-07-01 UTC 更新として表示されていた。

確認した公式記述:

- Safer Intents は Android の intent resolution mechanism の security を高める multi-phase initiative。
- Android 15 では sending app 側に焦点があり、Android 16 では receiving app 側が manifest で strict intent resolution に opt-in できる。
- explicit intent が component を直接指定する場合、その component の intent filter と一致すべき。
- action がない intent は intent filter に match すべきではない。
- これらの変更は複数 app が関与する場合にだけ適用され、同一 app 内の intent handling には影響しない。
- Android 16 初期の impact は opt-in に限定されるが、将来は strict intent resolution を default にする roadmap がある。

依頼文の Original statements / Applicability details と公式本文に実質差分は見つからなかった。

## Facts

### Manifest attribute / flags

Android 16 の `attrs_manifest.xml` には `android:intentMatchingFlags` が定義されている。この attribute は `<application>` と component tags に指定できる。

対象 tags:

- `<application>`
- `<activity>`
- `<activity-alias>`
- `<receiver>`
- `<service>`
- `<provider>`

Supported flags:

- `none` (`0x0001`): special matching rules を無効化する。conflicting values では `none` を優先する意図が documented。
- `enforceIntentFilter` (`0x0002`): incoming intents に対して strict matching を適用する。
- `allowNullAction` (`0x0004`): `enforceIntentFilter` と併用し、action が null の intent を許容する。

Reviewed source:

- `core/res/res/values/attrs_manifest.xml`
- `core/api/current.txt`
- `core/res/res/values/public-final.xml`

### API surface / Android 15 baseline

Android 16 `core/api/current.txt` では `android.R.attr.intentMatchingFlags` が `@FlaggedApi("android.security.enable_intent_matching_flags")` 付きで public attr として固定 ID を持つ。

Android 15 tag にも同 attr と parsing / enforcement code は存在するが、API surface では public staging 側であり、Android 16 で public final attr に移っている。したがって Android 16 / API 36 SDK で manifest attribute として利用される behavior と整理する。

### Manifest parsing / inheritance

Application-level:

- `ParsingPackageUtils` が `R.styleable.AndroidManifestApplication_intentMatchingFlags` を読み、package-level flags に保存する。

Component-level:

- `ParsedActivityUtils`
- `ParsedServiceUtils`
- `ParsedProviderUtils`
- receiver / activity-alias parsing path

`ParsedMainComponentUtils.parseMainComponent(...)` は、`android.security.Flags.enableIntentMatchingFlags()` が有効な場合に application flags と component flags を解決し、component に保存する。

`resolveIntentMatchingFlags(applicationFlags, componentFlags)` の挙動:

- component flags が 0 の場合は application flags を継承する。
- component flags が指定されている場合は component flags を優先する。

Unit test evidence:

- `ParsedMainComponentUtilsTest#testResolveIntentMatchingFlags`
- application-level `enforceIntentFilter` + component-level `none` は `none`
- application-level `enforceIntentFilter|allowNullAction` + component-level `enforceIntentFilter` は `enforceIntentFilter`
- application-level 未指定 + component-level `enforceIntentFilter|allowNullAction` は component flags

### Enforcement path

PackageManager の resolution path から `SaferIntentUtils.enforceIntentFilterMatching(...)` が呼ばれる。

Reviewed source:

- `services/core/java/com/android/server/pm/ComputerEngine.java`
- `services/core/java/com/android/server/pm/ResolveIntentHelper.java`
- `services/core/java/com/android/server/pm/SaferIntentUtils.java`

Android 16 の manifest opt-in path:

- `Flags.enableIntentMatchingFlags()` が true の場合、`enforceIntentFilterMatchingWithIntentMatchingFlags(...)` が使われる。
- caller が system / root 相当の場合は skip。
- caller と target component が same app の場合は `UserHandle.isSameApp(...)` で skip。
- target component に intent filter がない場合は skip。
- component flags が 0、`none`、または `enforceIntentFilter` を含まない場合は enforcement しない。
- `enforceIntentFilter` が有効な場合、explicit intent が target component の intent filter に match しないと block 対象。
- intent action が null の場合、`allowNullAction` がない限り block 対象。
- block 時は `PackageManager` tag で `"Intent does not match component's intent filter:"` と `"Access blocked:"` が warning log として出る。

### Component scope

AOSP の `SaferIntentUtils.infoToComponent(...)` は ActivityInfo と ServiceInfo を扱い、receiver は ActivityInfo として解決される。Provider は manifest attribute の parsing 対象だが、調査した intent resolution enforcement path では provider を intent で起動する経路は確認できなかった。

このため、顧客向けには exported provider を「attribute は指定可能だが、Safer Intents の主な runtime impact は activity / receiver / service の cross-app intent resolution」として分けて説明する。

### Android 15 sender-side / app-compat path

`SaferIntentUtils` には Android 15 由来の AppCompat path もある。

- Change ID: `161252188`
- Symbol: `ENFORCE_INTENTS_TO_MATCH_INTENT_FILTERS`
- Annotation: `@Disabled`
- `@Overridable`

この path は `Flags.enforceIntentFilterMatch()` と compat change によって sending app 側の enforcement を扱う既存実装である。一方、Android 16 の公式 Safer Intents セクションで説明される主 mechanism は receiving app 側の manifest opt-in `android:intentMatchingFlags` である。

公式 Android 16 compat framework changes ページでは、2026-07-03 の検索時点で Safer Intents 関連 Change ID は確認できなかった。

## Observations

### Receiving app opt-in の根拠

Android 16 の新 path は receiving app の manifest に保存された component flags を読み、`enforceIntentFilter` が指定された component だけで strict matching を有効化する。これは公式文書の「Android 16 では receiving app 側に control が移る」という説明と一致する。

### Explicit intent matching

`SaferIntentUtils` は target component の `ParsedIntentInfo` から `IntentFilter` を取り出し、`IntentResolver.intentMatchesFilter(...)` で incoming intent と比較する。どの filter にも match しない場合、opt-in 済み component では resolution result から削除される。

### Null action intent

`args.intent.getAction() == null` の場合、`allowNullAction` がなければ block 対象になる。この経路は公式文書の「Intents Without an Action Cannot Match any Intent Filter」を実装で裏付けている。

### Same-app は対象外

caller UID と target UID が same app の場合、enforcement loop は continue する。これにより同一アプリ内の explicit intent handling は対象外になる。

### Opt-in disabled の場合

`intentMatchingFlags` 未指定では component flags は 0 となり、`enforceIntentFilter` が false になる。したがって Android 16 初期時点の影響は manifest opt-in に限定され、既存アプリ破壊リスクは抑えられる。

### targetSdkVersion gate

AOSP の `intentMatchingFlags` parsing / enforcement path では、targetSdkVersion 36 を直接確認する gate は見つからなかった。公式 behavior change page は target SDK 36 以上向けだが、実装上の主 gate は manifest opt-in である。

### Future roadmap

公式文書は将来 strict intent resolution を default behavior にする計画を述べている。しかし `android-16.0.0_r4` の AOSP evidence では、future default / opt-out / mandatory enforcement の具体的 API level gate、TODO、公開 compat entry は確認できなかった。

## Hypotheses

- targetSdkVersion 35 のアプリでも、Android 16 上で `android:intentMatchingFlags` が parser に認識され、`enforceIntentFilter` が保存される場合、実装上は enforcement 対象になる可能性がある。
- 実務上は `intentMatchingFlags` が Android 16 SDK で public final attr になったため、targetSdkVersion 36 化と同時に opt-in するケースが中心になる可能性が高い。
- 将来 default enforcement になる場合、現在 opt-in していない receiving apps も cross-app explicit intent の filter mismatch による互換性問題を受ける可能性がある。

これらは AOSP 実装と公式 roadmap からの推論であり、実機 / CTS / SDK tooling で追加確認すべきである。

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
- 顧客向けには「Android 16 へ OS update しただけ」「targetSdkVersion 36 にしただけ」「manifest opt-in した時」を分けて説明する。

Compat framework:

- AppCompat fallback path の Change ID: `161252188` / `ENFORCE_INTENTS_TO_MATCH_INTENT_FILTERS`
- Default state: `@Disabled`
- Override: `@Overridable`
- Android 16 documented opt-in path は manifest `intentMatchingFlags`
- 公式 compat framework changes ページでは Safer Intents 関連 entry は確認できなかったため、force-enable / force-disable は公式 evidence から断定しない。

## Expected Behavior Matrix

| Scenario | Expected behavior | Customer explanation |
|---|---|---|
| Android 16 / targetSdkVersion 35 | `intentMatchingFlags` 未指定なら従来挙動。AOSP 上、opt-in 指定があれば enforcement される可能性は残る | OS update だけでは通常 impact なし |
| Android 16 / targetSdkVersion 36 | `intentMatchingFlags` 未指定なら従来挙動。opt-in した receiving app / component だけ enforcement | targetSdkVersion 36 化だけではなく manifest opt-in が必要 |
| Android 15 / targetSdkVersion 36 | Android 16 documented opt-in behavior の対象外。attr / feature flag 状態は platform build 依存 | Android 15 端末上の target 36 検証は参考扱い |

## Detailed Scenario Matrix

| Scenario | Expected behavior |
|---|---|
| Android 16 / targetSdkVersion 36 / no `android:intentMatchingFlags` | enforcement なし。従来挙動 |
| application-level `enforceIntentFilter` | component が override しなければ app 内 components に継承 |
| component-level `enforceIntentFilter` | 該当 component に enforcement |
| application-level `enforceIntentFilter` + component-level `none` | component-level `none` が優先され、該当 component は opt-out |
| `enforceIntentFilter + allowNullAction` | filter match は要求するが null action は許容 |
| conflicting flags including `none` | `none` は special matching rules を無効化する意図。component flags 指定時は component が優先 |
| explicit intent matches target component's filter | block されない |
| explicit intent does not match target component's filter | cross-app かつ opt-in 済みなら block |
| intent without action | `allowNullAction` なしの opt-in component では block |
| same-app explicit intent | enforcement 対象外 |
| cross-app explicit intent | enforcement 対象 |
| exported receiver | cross-app receiver intent が filter 不一致なら block |
| exported activity | cross-app activity start が filter 不一致なら block |
| exported service | cross-app service resolution が filter 不一致なら block |
| exported provider | attr は parsing 対象だが、今回確認した runtime enforcement path は provider を直接扱わない |
| external partner app sends legacy explicit intent | filter/action が合わなければ integration break |
| blocked intent warning log | `PackageManager` tag で `"Intent does not match component's intent filter:"` / `"Access blocked:"` |
| app does not opt in | Android 16 初期時点では従来挙動 |
| app opts in globally but disables one receiver | receiver-level `none` により該当 receiver は除外 |

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
- Safer Intents に opt-in しないが、将来 default enforcement に備える必要があるアプリ

Android 16 初期時点では、opt-in しないアプリの既存 behavior は原則維持される。したがって、顧客向け説明では次を混ぜない。

- Android 16 へ OS update しただけの影響
- targetSdkVersion 36 化しただけの影響
- manifest で Safer Intents に opt-in した時の影響

## Recommended Action Candidates

- exported components の intent filters と、外部 app から届く explicit intents を棚卸しする。
- `android:intentMatchingFlags="enforceIntentFilter"` を application-level で入れる前に、partner app / SDK / launcher / notification / shortcut 連携を検証する。
- 互換性が必要な component は component-level `none` で一時的に除外する。
- null action を受ける正当な互換要件がある場合のみ `allowNullAction` を検討する。
- blocked intent log を QA で確認する。
- 将来 default enforcement に備え、opt-in しない場合でも explicit intent が target component の filter と一致するよう送信側 / 受信側を修正する。

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
- fallback / compatibility handling
- future default enforcement を想定した regression testing

## Conclusions

- Android 16 の Safer Intents は receiving app が manifest で opt-in した場合に、cross-app incoming intents をより厳格に matching する security feature として整理できる。
- explicit intent が target component の intent filter に match しない場合、または action が null で `allowNullAction` がない場合、opt-in 済み component では resolution result から削除される。
- same-app intent handling は明示的に skip される。
- `intentMatchingFlags` 未指定では enforcement されないため、Android 16 初期時点の impact は opt-in に限定される。
- AOSP evidence では targetSdkVersion 36 gate は確認できないため、「targetSdkVersion 36 化だけで壊れる」と説明してはいけない。
- 将来 default / opt-out / mandatory enforcement への移行は公式 roadmap として記録するが、Android 16 `android-16.0.0_r4` の AOSP evidence では具体的 gate は確認できなかった。

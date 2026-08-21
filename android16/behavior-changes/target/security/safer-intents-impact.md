# Safer Intents: Impact

## 調査メタデータ

- Android version: Android 16
- Version directory: `android16`
- From tag: `android-15.0.0_r36`
- To tag: `android-16.0.0_r4`
- Previous targetSdkVersion: 35
- Target targetSdkVersion: 36
- Behavior Change section: Impact
- Parent section: Safer Intents
- Official documentation URL: https://developer.android.com/about/versions/16/behavior-changes-16#impact
- Official documentation category: Security
- Applicability classification: `OPT_IN_ONLY`
- Confidence: High


Confidence note: 公式文書はAndroid 16初期impactをmanifest opt-inに限定している。AOSPでも`android:intentMatchingFlags` / feature flag / cross-app resolutionが実際の適用条件であり、targetSdkVersion 36だけでは有効にならないことを確認できるため、`OPT_IN_ONLY`としてHigh confidenceとする。

## Official Documentation Review

2026-07-03 に公式ドキュメントの Safer Intents / Impact セクションを再確認した。対象ページは 2026-07-01 UTC 更新として表示されていた。

確認した公式記述:

- Safer Intents は Android 16 初期時点では opt-in であり、manifest で明示的に有効化する必要がある。
- 影響は Safer Intents を認識し、より厳格な intent handling を採用する開発者のアプリに限定される。
- opt-in approach により、現在の permissive な intent resolution behavior に依存する既存アプリを壊すリスクを抑える。
- 将来リリースではより広い影響が予定され、strict intent resolution を最終的に default にする計画がある。
- opt-out / mandatory enforcement への移行では互換性問題に注意が必要。

依頼文の Original statements / Applicability details と公式本文に実質差分は見つからなかった。

## Facts

### Manifest attribute / supported flags

Android 16 の `attrs_manifest.xml` には `android:intentMatchingFlags` が定義されている。この attribute は `<application>` と component tags に指定できる。

対応 component:

- `<activity>`
- `<activity-alias>`
- `<receiver>`
- `<service>`
- `<provider>`

Supported flags:

- `none` (`0x0001`): special matching rules を無効化する。複数 flag 指定時に conflicting values は `none` 優先。
- `enforceIntentFilter` (`0x0002`): incoming intent に対して stricter matching を強制する。
- `allowNullAction` (`0x0004`): `enforceIntentFilter` と併用し、action が null の intent を許可する緩和 flag。

Reviewed source:

- `core/res/res/values/attrs_manifest.xml`
- `core/api/current.txt`
- `core/res/res/values/public-final.xml`

### API surface

Android 16 `core/api/current.txt` では `android.R.attr.intentMatchingFlags` が `@FlaggedApi("android.security.enable_intent_matching_flags")` 付きで public attr として固定 ID を持つ。

Android 15 tag では同 attr は存在するが、public staging 側であり、Android 16 で public final に移った差分がある。これにより、通常の SDK 利用としては Android 16 / API 36 で manifest attribute として扱いやすくなったと解釈できる。

### Manifest parsing

Application-level parsing:

- `ParsingPackageUtils` が `R.styleable.AndroidManifestApplication_intentMatchingFlags` を読み、package-level intent matching flags に保存する。

Component-level parsing:

- `ParsedActivityUtils`
- `ParsedServiceUtils`
- `ParsedProviderUtils`
- activity-alias / receiver parsing path

Component parsing では `ParsedMainComponentUtils.parseMainComponent(...)` が application flags と component flags を `resolveIntentMatchingFlags(...)` で解決し、component に保存する。

`resolveIntentMatchingFlags(...)` は component flags が 0 の場合に application flags を継承し、component flags が指定されている場合は component flags を優先する。

関連 unit test:

- `ParsedMainComponentUtilsTest#testResolveIntentMatchingFlags`
- application-level `enforceIntentFilter` + component-level `none` は `none`
- application-level `enforceIntentFilter|allowNullAction` + component-level `enforceIntentFilter` は `enforceIntentFilter`
- application-level 未指定 + component-level `enforceIntentFilter|allowNullAction` は component flags

### Enforcement path

PackageManager の intent resolution path から `SaferIntentUtils.enforceIntentFilterMatching(...)` が呼ばれる。

Reviewed source:

- `services/core/java/com/android/server/pm/ComputerEngine.java`
- `services/core/java/com/android/server/pm/ResolveIntentHelper.java`
- `services/core/java/com/android/server/pm/SaferIntentUtils.java`

`SaferIntentUtils` の Android 16 path は `Flags.enableIntentMatchingFlags()` が true の場合に `enforceIntentFilterMatchingWithIntentMatchingFlags(...)` を使う。

この path では次を確認する。

- system / root 相当 caller は skip
- caller と target component が same app の場合は skip
- target component に intent filter がない場合は skip
- component flags が 0、`none`、または `enforceIntentFilter` なしの場合は enforcement しない
- `enforceIntentFilter` がある場合、explicit intent が target component の intent filter に match しないと block 対象
- action が null の intent は、`allowNullAction` がない限り block 対象
- block 時には `PackageManager` tag で `"Intent does not match component's intent filter:"` と `"Access blocked:"` が warning log として出る

### App-compat path

`SaferIntentUtils` には Android 15 由来の AppCompat path も残っている。

- Change ID: `161252188`
- Symbol: `ENFORCE_INTENTS_TO_MATCH_INTENT_FILTERS`
- Annotation: `@Disabled`
- `@Overridable`

ただし Android 16 の Impact / Implementation セクションで説明される opt-in mechanism は manifest attribute `android:intentMatchingFlags` が中心である。公式 compat framework changes ページでは、2026-07-03 の検索時点で Safer Intents 関連 Change ID は確認できなかった。

## Observations

### Impact が opt-in に限定される根拠

AOSP の `intentMatchingFlags` path では、component の resolved flags に `enforceIntentFilter` が含まれない限り `enforceIntentFilter` が false になる。attribute 未指定の場合、component flags は 0 であり enforcement されない。

このため、Android 16 初期時点の実装は公式文書の通り、manifest opt-in した app / component に限定して impact を持つ。

### Existing app breakage が限定される根拠

`android:intentMatchingFlags` 未指定では従来挙動が維持される。さらに same-app intent handling は `UserHandle.isSameApp(callingUid, targetUid)` で skip される。したがって、同一アプリ内 component 起動は Safer Intents enforcement の対象外であり、破壊リスクは主に cross-app explicit intent に限定される。

### targetSdkVersion gate

AOSP の `enforceIntentFilterMatchingWithIntentMatchingFlags(...)` および manifest parsing path では、targetSdkVersion 36 を直接確認する gate は見つからなかった。

公式ページは Android 16 targeting apps 向けの behavior changes として掲載しているが、本文は Android 16 初期 impact を opt-in と説明している。AOSP の直接 gate も targetSdkVersion ではなく `android:intentMatchingFlags` opt-in であるため、primary classification は `OPT_IN_ONLY` とする。

### Future roadmap

公式文書は将来 default behavior へ移行する計画を述べている。一方、`android-16.0.0_r4` の AOSP evidence から、将来 release で default / opt-out / mandatory enforcement に切り替わる具体的な API level gate、TODO、公開 compat entry は確認できなかった。

そのため将来 default 化は公式 roadmap statement として扱い、Android 16 の確定実装とは分ける。

## Hypotheses

- targetSdkVersion 35 のアプリでも、Android 16 上で `android:intentMatchingFlags` が package parser に認識され、component に `enforceIntentFilter` が保存される場合、AOSP 実装上は enforcement 対象になる可能性がある。
- ただし通常の開発フローでは `intentMatchingFlags` は Android 16 SDK で public final attr として利用されるため、実務上は targetSdkVersion 36 化と同時に採用される可能性が高い。
- 将来 Android release で default enforcement になる場合、現在 opt-in していない app も同様の cross-app intent compatibility 問題を受ける可能性がある。

これらは AOSP 実装からの推論であり、実機 / CTS / SDK tooling で追加確認すべきである。

## Applicability Classification

Primary classification: `OPT_IN_ONLY`

追加条件:

- Android 16 以上の platform / feature flag `enable_intent_matching_flags` が有効
- app または component が `android:intentMatchingFlags` で `enforceIntentFilter` に opt-in
- cross-app intent resolution が発生
- target component が intent filter を持つ
- incoming intent が filter に match しない、または action が null で `allowNullAction` がない

Classification caveat:

- AOSP evidence では targetSdkVersion 36 gate は確認できなかった。
- `OPT_IN_ONLY` は、公式文書の opt-in statement と AOSP manifest opt-in gate に直接対応する分類である。
- 実装上の主 gate は manifest opt-in であり、「targetSdkVersion 36 にしただけ」では impact は発生しない。

Compat framework:

- AppCompat fallback path には `ENFORCE_INTENTS_TO_MATCH_INTENT_FILTERS` (`161252188`) があるが、`@Disabled`。
- Android 16 の documented opt-in behavior は manifest `intentMatchingFlags` path。
- 公式 Android 16 compat framework changes ページでは Safer Intents 関連 entry は確認できなかった。
- force-enable / force-disable は公式 evidence からは断定しない。

## Expected Behavior Matrix

| Scenario | Expected behavior | Customer explanation |
|---|---|---|
| Android 16 / targetSdkVersion 35 | `intentMatchingFlags` 未指定なら従来挙動。AOSP 上、opt-in 指定があれば enforcement される可能性は残る | OS update だけでは通常 impact なし |
| Android 16 / targetSdkVersion 36 | `intentMatchingFlags` 未指定なら従来挙動。opt-in した app / component だけ enforcement | targetSdkVersion 36 化だけではなく manifest opt-in が必要 |
| Android 15 / targetSdkVersion 36 | Android 16 の documented opt-in behavior の対象外。attr / feature flag 状態は platform build 依存 | Android 15 端末での target 36 検証は参考扱い |

## Detailed Scenario Matrix

| Scenario | Expected behavior |
|---|---|
| Android 16 / targetSdkVersion 36 / no `android:intentMatchingFlags` | enforcement なし。従来挙動 |
| application-level `enforceIntentFilter` | component が override しなければ app 内 components に継承 |
| component-level `enforceIntentFilter` | 該当 component に enforcement |
| application-level `enforceIntentFilter` + component-level `none` | component-level `none` が優先され、該当 component は opt-out |
| `enforceIntentFilter + allowNullAction` | intent filter match は要求するが null action は許容 |
| conflicting flags including `none` | `none` が special matching rules を無効化する意図。component flags 指定時は component が優先 |
| explicit intent matches target component filter | block されない |
| explicit intent does not match target component filter | cross-app かつ opt-in なら block |
| intent without action | `allowNullAction` なしの opt-in component では block |
| same-app explicit intent | skip される |
| cross-app explicit intent | enforcement 対象 |
| exported receiver | cross-app receiver intent が filter 不一致なら block |
| exported activity | cross-app activity start が filter 不一致なら block |
| exported service | cross-app service resolution が filter 不一致なら block |
| external partner app sends legacy explicit intent | filter/action が合わなければ integration break |
| blocked intent warning log | `PackageManager` tag で `"Intent does not match component's intent filter:"` / `"Access blocked:"` |

## Developer Impact

影響対象:

- Safer Intents に opt-in するアプリ
- exported activity / receiver / service を持つアプリ
- cross-app explicit intents を受けるアプリ
- action のない intent を受ける可能性があるアプリ
- intent filter と一致しない explicit intent を受けるアプリ
- partner app / SDK / launcher / shortcut / notification / broadcast sender と連携するアプリ
- deep link / app link / custom action / implicit-to-explicit migration を行っているアプリ
- application-level enforcement と component-level override を混在させるアプリ
- Safer Intents に opt-in しないが将来 default enforcement に備える必要があるアプリ

Android 16 初期時点では、opt-in しないアプリの既存 behavior は原則維持される。したがって、顧客向け説明では次を混ぜない。

- Android 16 へ OS update しただけの影響
- targetSdkVersion 36 化しただけの影響
- manifest で Safer Intents に opt-in した時の影響

## Recommended Action Candidates

- まず exported components の intent filters と、実際に外部 app から届く explicit intents を棚卸しする。
- `android:intentMatchingFlags="enforceIntentFilter"` を application-level で入れる前に、partner app / SDK / launcher / notification / shortcut 連携を検証する。
- 互換性が必要な component は component-level `none` で一時的に除外する。
- null action を受ける正当な互換要件がある場合のみ `allowNullAction` を検討する。
- blocked intent log を CI / manual QA で確認する。
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
- exported activity / receiver / service
- partner app からの legacy explicit intent
- blocked intent 時の app behavior
- logcat tag `PackageManager` の warning
- fallback / compatibility handling
- future default enforcement を想定した regression testing

## Conclusions

- Android 16 の Safer Intents / Impact は、初期時点では opt-in impact として説明するのが適切である。
- AOSP evidence は、manifest `android:intentMatchingFlags` が未指定なら enforcement されず、`enforceIntentFilter` を指定した component だけが stricter matching 対象になることを示している。
- same-app intent handling は明示的に skip されるため、主な risk は cross-app explicit intent integration に限定される。
- targetSdkVersion 36 gate は AOSP の enforcement path では確認できなかったため、顧客向けには「targetSdkVersion 36 化だけで壊れる」ではなく「Android 16 上で Safer Intents に opt-in した場合に壊れ得る」と説明する。
- 将来 default enforcement への roadmap は公式文書上の方針として記録するが、Android 16 `android-16.0.0_r4` の AOSP evidence では具体的な future API level gate は確認できなかった。

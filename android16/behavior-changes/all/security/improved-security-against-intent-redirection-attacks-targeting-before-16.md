# For applications compiling against Android 15 (API level 35) or lower 調査レポート

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:
- AOSP checkout `frameworks-base` は clean で、`android-15.0.0_r36` / `android-16.0.0_r4` tag の存在を確認した。

Previous targetSdkVersion:
- 35

Target targetSdkVersion:
- 36

### Behavior Change 文書（Behavior Change Source）

Document:
- https://developer.android.com/about/versions/16/behavior-changes-all#targeting-before-16

Parent section:
- Improved security against Intent redirection attacks

Grandparent section:
- Opt out of Intent redirection handling

Page:
- Behavior changes: all apps

Category:
- Security

Section:
- For applications compiling against Android 15 (API level 35) or lower

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `OS_UPDATE_ALL_APPS`

追加条件（Additional conditions）:
- この subsection は Android 16 default Intent redirection hardening そのものではなく、compileSdkVersion 35 以下のアプリが `Intent#removeLaunchSecurityProtection()` を直接参照できない場合の reflection fallback guidance である。
- 実行時に意味を持つのは、Android 16 上で nested / sub-level Intent launch が default hardening 対象になり、かつアプリが対象 Intent object に reflection で `removeLaunchSecurityProtection()` を呼ぶ場合。
- `targetSdkVersion 36` は reflection fallback の実行時 gate ではない。
- `compileSdkVersion 35 以下` は直接 API 参照の可否に関係する compile-time 条件であり、runtime behavior gate ではない。

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| この subsection は default hardening そのものか | No | `Opt out` 内の compileSdkVersion 35-or-lower 向け呼び出し方法。 |
| Android 16 OS 上の all-apps 変更に関係するか | Yes / Conditional | 親項目は Android 16 all-apps Security 変更。reflection fallback は nested Intent hardening を明示的に opt out する場合のみ関係する。 |
| targetSdkVersion 36 が必要か | No | AOSP Activity launch enforcement / opt-out method に targetSdkVersion 36 gate は見つからない。 |
| compileSdkVersion 35 以下が条件か | Yes, for this subsection | 公式文書は API 35 以下で compile する場合に reflection fallback を示している。 |
| reflection は推奨か | No | 公式文書は not recommended / fragile と説明し、可能なら compile SDK 36 以上で direct API を使うよう促す。 |
| Android 15 baseline で method が存在しないか | Not conclusive | `android-15.0.0_r36` の `core/api/current.txt` にも flagged method が見える。製品 SDK / device image / flag exposure は実機検証が必要。 |

### 調査日（Investigation Date）

2026-07-06

### 信頼度（Confidence）

- Medium

理由:
- 公式文書の該当 subsection 本文は確認できたが、現行 HTML で `#targeting-before-16` anchor 文字列は確認できなかった。
- AOSP では `Intent#removeLaunchSecurityProtection()` の public flagged API surface、実装、Activity launch hardening path、関連 tests を確認した。
- Android 15 tag にも `removeLaunchSecurityProtection()` flagged symbol があるため、公式の「compile against Android 15 SDK or lower」説明と AOSP tag の API surface を単純に対応づけられない。
- reflection の成功 / 失敗は compile SDK ではなく、実行先 OS image に method が存在するか、API exposure / flag 状態、reflection 呼び出し例外処理に依存するため、実機検証が必要である。

---

## 公式ドキュメント確認（Original Documentation）

### 原文要旨（Statements Verified）

公式文書は、Android 15 / API 35 SDK 以下で compile しているアプリについて、以下を説明している。

- 推奨はしないが、reflection で `removeLaunchSecurityProtection()` にアクセスできる。
- reflection は将来 Android version で underlying API が変わると壊れやすく、エラーを起こしやすい。
- 可能なら compile SDK を Android 16 / API 36 以上に更新し、API を直接使うべきである。

### Anchor validation

- Requested URL: `https://developer.android.com/about/versions/16/behavior-changes-all#targeting-before-16`
- 現行公式 HTML では `targeting-before-16` 文字列を確認できなかった。
- 最寄りの公式 content は `Opt out of Intent redirection handling` 配下の “For applications compiling against Android 15 (API level 35) or lower” subsection である。

### Documentation drift

- Original statements と現行公式本文に実質的な差分は見つからなかった。
- 差分として、requested anchor の literal id は確認できなかった点を記録する。

---

## Facts

- 公式文書は compileSdkVersion 35 以下のアプリについて、reflection による `removeLaunchSecurityProtection()` 呼び出しを非推奨 fallback として示している。
- Android 16 tag の `Intent#removeLaunchSecurityProtection()` は `@FlaggedApi(FLAG_PREVENT_INTENT_REDIRECT)` 付き public method として存在する。
- Android 16 実装では `removeLaunchSecurityProtection()` が `EXTENDED_FLAG_MISSING_CREATOR_OR_INVALID_TOKEN` をクリアし、`removeCreatorTokenInfo()` を呼んで creator token info を削除する。
- Android 16 `core/api/current.txt` では `removeLaunchSecurityProtection()` が `@FlaggedApi("android.security.prevent_intent_redirect")` の public method として現れる。
- Android 15 `core/api/current.txt` にも同じ flagged method が見えるため、今回の AOSP tag comparison では「Android 15 tag に method が存在しない」とは言えない。
- `ActivityStarter` には `ENABLE_PREVENT_INTENT_REDIRECT_TAKE_ACTION = 29623414` が `@ChangeId` / `@Overridable` として定義され、missing / invalid token、URI grant、start permission などの hardening path で参照される。
- `ActivityStarter` の確認範囲では targetSdkVersion 36 gate は見つからない。
- `IntentTest` は creator token info removal、nested key collection、fillIn merge を検証している。
- `ActivityManagerServiceTest` は creator token 付与、不正に差し込まれた nested Intent への missing / invalid flag 設定を検証している。

## Observations

- この subsection は `removeLaunchSecurityProtection()` の安全性を保証するものではなく、直接 API を参照できない compileSdkVersion 35 以下アプリ向けの暫定的な呼び出し方法を示すだけである。
- reflection fallback は source compatibility の回避策であり、runtime で method が存在しない場合は `NoSuchMethodException` / `MethodNotFound` 相当の failure が発生し得る。
- `getDeclaredMethod()` / `invoke()` は、method lookup failure、access failure、invocation target exception を app 側で扱う必要がある。
- broad reflection opt-out は、Android 16 Intent redirection hardening を弱めるため、security regression の原因になり得る。
- compileSdkVersion 36 へ移行して direct API を使っても、opt-out が security protection を外すこと自体は変わらない。
- service / bind / broadcast path では `prepareToLeaveProcess()` は確認したが、Activity launch と同等の creator-token enforcement は未確認である。

## Hypotheses

- compileSdkVersion 35 以下のアプリが Android 16 実機上で reflection fallback を呼ぶ場合、method lookup は成功し、direct API と同様に対象 Intent object の creator token protection を外す可能性が高い。
- Android 15 実機では、AOSP tag 上の symbol presence だけでは reflection / direct call の成功を保証できない。製品 SDK、flag state、device image により method lookup / invocation が異なる可能性がある。
- 正当な first-party nested Intent flow で一時的に reflection opt-out が必要な場合でも、長期的には nested Intent validation を修正し、opt-out 自体を削除する方が安全である。

## Conclusions

- この subsection の主な結論は、compileSdkVersion 35 以下でも reflection で `removeLaunchSecurityProtection()` を呼べる可能性があるが、非推奨で壊れやすく、security review が必須という点である。
- 分類は親項目に合わせて `OS_UPDATE_ALL_APPS` とする。ただしこの subsection 固有の適用条件として `compileSdkVersion 35 以下`、`reflection fallback`、`explicit opt-out` を必ず併記する。
- 顧客向け説明では、Android 16 OS update による default hardening、targetSdkVersion 36 migration、compileSdkVersion 35 以下の direct API 不可、reflection fragility、opt-out による security protection removal を分離する。
- 推奨対応は reflection fallback の恒久利用ではなく、compileSdkVersion 36 への移行、nested Intent validation、必要最小限の first-party flow への限定である。

---

## AOSP 調査（AOSP Investigation）

### 関連ファイル（Related Files）

- `frameworks-base/core/java/android/content/Intent.java`
- `frameworks-base/core/api/current.txt`
- `frameworks-base/core/java/android/security/responsible_apis_flags.aconfig`
- `frameworks-base/services/core/java/com/android/server/wm/ActivityStarter.java`
- `frameworks-base/services/core/java/com/android/server/am/ActivityManagerService.java`
- `frameworks-base/core/tests/coretests/src/android/content/IntentTest.java`
- `frameworks-base/services/tests/mockingservicestests/src/com/android/server/am/ActivityManagerServiceTest.java`

### 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル | Android 15 baseline | Android 16 target | relevance |
| --- | --- | --- | --- |
| `Intent#removeLaunchSecurityProtection()` | `android-15.0.0_r36` の API surface に flagged symbol が見える。 | `@FlaggedApi(FLAG_PREVENT_INTENT_REDIRECT)`。missing flag と creator token info を削除。 | reflection fallback が呼ぶ method の実体。 |
| `core/api/current.txt` | flagged method が存在。 | flagged method が存在。 | compile SDK guidance と AOSP tag evidence の差分注意点。 |
| `Intent#maybeMarkAsMissingCreatorTokenInternal()` | foreign parcel 由来かつ trusted creator token がない場合に missing / invalid flag を付ける実装がある。 | 同様。 | opt-out 前に何が hardening 対象になるかの根拠。 |
| `Intent#writeToParcel()` / `readFromParcel()` | Intent state を parcel する。 | `mExtendedFlags` と creator token info を parcel state として扱う。 | opt-out が per Intent object/state である根拠。 |
| `ActivityStarter` | creator token / missing token check path がある。 | `ENABLE_PREVENT_INTENT_REDIRECT_TAKE_ACTION` と URI grant / permission check path を確認。 | default hardening と opt-out の意味を説明する根拠。 |
| `responsible_apis_flags.aconfig` | `prevent_intent_redirect` family が存在。 | 同様。 | opt-out API / hardening が flagged API / feature flag family に属する根拠。 |
| `IntentTest` | N/A | creator token info removal、extra key collection、fillIn merge を検証。 | Intent state behavior の test evidence。 |
| `ActivityManagerServiceTest` | N/A | creator token 付与と missing flag 設定を検証。 | nested Intent hardening の test evidence。 |

### 差分解釈（Diff Interpretation）

| 確認した差分 / 状態 | 解釈 | Behavior Change との関係 | 信頼度 |
| --- | --- | --- | --- |
| `removeLaunchSecurityProtection()` は missing / invalid token flag と creator token info を削除する | reflection で呼ぶと direct API と同じ method body が実行される。 | reflection fallback の実装根拠。 | High |
| Android 15 / Android 16 両 tag の `current.txt` に flagged method が見える | AOSP tag だけでは compileSdkVersion 35 以下で直接参照不可という公式説明を完全には説明できない。 | SDK artifact / flagged API exposure は別途確認が必要。 | Medium |
| `ActivityStarter` が missing token / creator URI grant / permission failure を扱う | opt-out しない default hardening の Activity launch path。 | reflection opt-out が何を回避し得るかの前提。 | High |
| targetSdkVersion 36 gate が見つからない | runtime hardening / opt-out は targetSdkVersion 36 固有ではない。 | `OS_UPDATE_ALL_APPS` + compile SDK condition とする根拠。 | Medium-High |
| service / bind / broadcast の同等 enforcement は未確認 | request の service / broadcast path は evidence gap。 | Activity launch を confirmed path として限定する根拠。 | Medium |

### Reflection failure model

| failure | 発生条件 | app 側の扱い |
| --- | --- | --- |
| `NoSuchMethodException` | 実行 OS / framework に method が存在しない、または name / signature が変わった場合。 | fallback し、default hardening が残る前提で user-visible failure / retry を扱う。 |
| `IllegalAccessException` | reflection access が許可されない場合。 | fallback し、broad catch で握りつぶさず telemetry に残す。 |
| `InvocationTargetException` | method body 実行中の例外が wrapper される場合。 | cause を記録し、security-sensitive flow として扱う。 |
| `NullPointerException` / invalid target | nested Intent が null など、reflection target が不正な場合。 | launch しない。validation failure として扱う。 |

### Compat framework

| 項目 | 確認結果 |
| --- | --- |
| Change ID | `29623414` |
| Symbol | `ENABLE_PREVENT_INTENT_REDIRECT_TAKE_ACTION` |
| AOSP annotation | `@ChangeId`, `@Overridable` |
| targetSdkVersion gate | 確認範囲では見つからない |
| Default state | `@Disabled` / `@EnabledAfter` は見つからない。公式 compat framework 一覧では未確認 |
| opt-out API 自体の compat flag | `@FlaggedApi(FLAG_PREVENT_INTENT_REDIRECT)`。aconfig `prevent_intent_redirect` family と関係 |

---

## 適用条件（Applicability）

### Android 16 / targetSdkVersion 35

- default hardening: nested Intent Activity launch pattern では適用され得る。
- compileSdkVersion 35 以下: direct API 参照ができない場合、公式文書上 reflection fallback が示される。
- reflection opt-out: method lookup / invocation が成功した場合のみ opt-out として機能する。

### Android 16 / targetSdkVersion 36

- default hardening: targetSdkVersion 35 と同様。
- reflection opt-out: targetSdkVersion 36 固有ではない。
- compileSdkVersion 35 以下のまま targetSdkVersion 36 にする構成では、direct API ではなく reflection fallback を検討する余地があるが非推奨。

### Android 15 / targetSdkVersion 36

- Android 16 公式挙動とは分ける。
- AOSP tag では Android 15 側にも flagged method が見えるが、実機 / SDK artifact / flag state の検証なしに reflection success は保証しない。
- Android 15 runtime で compileSdkVersion 36 direct API compiled app を実行する場合も、method resolution risk を実機で確認する。

---

## 期待挙動マトリクス（Expected Behavior Matrix）

| シナリオ | 期待挙動 / 調査結論 |
| --- | --- |
| Android 16 / targetSdkVersion 35 / compileSdkVersion 35 or lower / no opt-out | default hardening が残る。nested Intent Activity launch が block / exception 対象になり得る。 |
| Android 16 / targetSdkVersion 36 / compileSdkVersion 35 or lower / no opt-out | targetSdkVersion 35 と同様。 |
| Android 16 / targetSdkVersion 35 / compileSdkVersion 35 or lower / reflection opt-out | reflection 成功時のみ対象 Intent object の protection を外す。 |
| Android 16 / targetSdkVersion 36 / compileSdkVersion 35 or lower / reflection opt-out | targetSdkVersion 35 と同様。 |
| Android 16 / compileSdkVersion 36 or higher / direct API call | sibling subsection の direct API path。reflection は不要。 |
| Android 16 / compileSdkVersion 35 or lower / reflection call | 公式上は可能だが非推奨。 |
| Android 16 / reflection succeeds | `removeLaunchSecurityProtection()` method body が実行され、missing flag / creator token info が削除され得る。 |
| Android 16 / reflection fails | opt-out されない。fallback / error handling が必要。 |
| Android 16 / `NoSuchMethodException` | method 不在 / signature change として扱う。 |
| Android 16 / `InvocationTargetException` or `IllegalAccessException` | reflection failure として扱い、security-sensitive telemetry に残す。 |
| Android 15 / targetSdkVersion 36 / compileSdkVersion 35 or lower / reflection call | 技術的比較が必要。AOSP tag の symbol presence だけでは保証しない。 |
| Android 15 / targetSdkVersion 36 / compileSdkVersion 36 direct API compiled app | method resolution risk を実機確認。 |
| Android 16 / top-level Intent only | 通常は reflection opt-out 不要。 |
| Android 16 / nested Intent from trusted in-app source | allowlist validation を優先。reflection opt-out は必要最小限。 |
| Android 16 / nested Intent from untrusted external source | reflection opt-out すべきではない。 |
| Android 16 / nested Intent with explicit component | private / permission-protected component targeting を検証。 |
| Android 16 / nested Intent with implicit action | action / category / data allowlist が必要。 |
| Android 16 / nested Intent with package set | package allowlist が必要。 |
| Android 16 / nested Intent with URI grant flags | URI grant leakage risk があるため opt-out は高リスク。 |
| Android 16 / nested Intent with ClipData URI | ClipData URI も validation / grant stripping 対象。 |
| Android 16 / startActivity nested Intent | confirmed Activity launch enforcement path。 |
| Android 16 / startActivityForResult nested Intent | Activity launch path として検証対象。 |
| Android 16 / PendingIntent-based flow | PendingIntent creator semantics と nested Intent forwarding を分けて確認。 |
| Android 16 / chooser / selector Intent flow | selector / chooser 内の Intent state と opt-out scope を個別確認。 |
| Android 16 / startService / bindService nested Intent, if relevant | Activity launch と同等 enforcement は未確認。 |
| Android 16 / sendBroadcast nested Intent, if relevant | 要検証。 |
| Android 16 / app validates nested Intent before launch | 推奨対応。 |
| Android 16 / app forwards nested Intent without validation | default hardening の block / exception 対象になり得る。 |
| Android 16 / app uses reflection opt-out only for allowlisted first-party flows | 例外対応候補。ただし threat model / code review 必須。 |
| Android 16 / app broadly uses reflection opt-out for all nested Intents | 非推奨。security regression risk が高い。 |
| app migrates from reflection fallback to compileSdkVersion 36 direct API | reflection fragility は減るが opt-out risk は残る。 |
| app removes opt-out after fixing nested Intent validation | 最も望ましい長期対応。 |

---

## 影響対象（Affected App Categories）

- compileSdkVersion 35 以下のアプリ
- compileSdkVersion 36 へまだ更新できないアプリ
- Intent router / dispatcher Activity を持つアプリ
- deep link / app link / auth callback を中継するアプリ
- SSO / login / payment / identity verification flow を扱うアプリ
- notification / shortcut / widget から nested Intent を起動するアプリ
- third-party SDK から渡された Intent を起動するアプリ
- plugin / mini-app / dynamic feature / modular navigation を持つアプリ
- file picker / document provider / media sharing など URI grant を扱うアプリ
- enterprise / companion / device management flow で Intent forwarding を使うアプリ
- legacy code で `getParcelableExtra()` した Intent をそのまま `startActivity()` するアプリ
- reflection fallback を検討しているアプリ
- compileSdkVersion 36 へ更新して direct API へ移行すべきアプリ
- セキュリティレビューなしに reflection opt-out すると危険なアプリ

---

## 推奨対応候補（Recommended Action Candidates）

- まず nested Intent forwarding を棚卸しし、untrusted source 由来の Intent をそのまま launch しない。
- component / package / action / data / categories / flags / ClipData / URI grants を allowlist validation する。
- reflection fallback は first-party / allowlisted flow に限定し、広範な catch-all opt-out にしない。
- reflection failure を握りつぶさず、failure type と affected flow を telemetry / log に残す。
- compileSdkVersion 36 へ移行できる場合は direct API に移行する。ただし direct API 化は security risk を解消しないため、validation fix を優先する。
- 長期的には opt-out を削除し、nested Intent validation / IntentSanitizer 相当の sanitizer で対応する。

---

## テスト観点（Test Viewpoints）

- Android 15 端末上の targetSdkVersion 35
- Android 16 端末上の targetSdkVersion 35
- Android 16 端末上の targetSdkVersion 36
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較
- compileSdkVersion 35 以下 reflection fallback
- compileSdkVersion 36 direct API build
- default hardening enabled / no opt-out
- `removeLaunchSecurityProtection()` called by reflection / not called
- reflection `getDeclaredMethod()` success / failure
- `NoSuchMethodException` / `InvocationTargetException` / `IllegalAccessException` handling
- nested Intent launch from trusted source
- nested Intent launch from untrusted source
- explicit component / implicit action / package set の違い
- `exported=false` component targeting attempt
- permission-protected component targeting attempt
- URI grant flags and ClipData URI access
- `startActivity()` / `startActivityForResult()` / ActivityResult
- PendingIntent / chooser / selector Intent
- service / broadcast path, if applicable
- app-side validation: component allowlist, package allowlist, action allowlist, data scheme/host validation, flag stripping, URI grant stripping
- logcat / security warning / exception / launch failure / successful launch
- user-visible regression and fallback behavior
- reflection fallback が想定 flow だけに限定されていること
- security regression testing for Intent redirection attacks
- compileSdkVersion 36 へ移行後に direct API で同等挙動になること
- opt-out を削除して validation fix へ移行できること

---

## Evidence gaps

- 現行公式 HTML で `#targeting-before-16` anchor literal は確認できなかった。該当 subsection 本文は確認済み。
- Android 15 AOSP tag の `current.txt` にも flagged method が見えるため、API 35 SDK artifact で direct reference が実際に不可か、flagged API exposure がどう扱われるかは別途 SDK 実物で確認が必要。
- Android 15 device 上で reflection / direct API compiled app がどう動くかは実機検証が必要。
- service / bind / broadcast path の enforcement は Activity launch と同等とは確認できない。
- reflection fallback を使う場合の hidden API / flagged API / verifier / optimizer 影響は app build / device image 条件で確認が必要。

---

## Human Decision Placeholder

最終優先度（Final Priority）:
- TBD by human

最終 severity（Final Severity）:
- TBD by human

顧客説明優先度（Customer communication priority）:
- TBD by human

reflection fallback 許可方針（Reflection fallback approval policy）:
- TBD by human

リリース判定（Release readiness decision）:
- TBD by human

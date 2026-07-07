# Opt out of Intent redirection handling 調査レポート

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:
- `android16/AGENTS.md` は To tag を `android-16.0.0_r1` としているが、本調査では依頼スコープに従い公開済み Android 16 tag として `android-16.0.0_r4` を使用した。
- AOSP checkout `frameworks-base` は clean で、`android-15.0.0_r36` / `android-16.0.0_r4` tag の存在を確認した。

Previous targetSdkVersion:
- 35

Target targetSdkVersion:
- 36

### Behavior Change 文書（Behavior Change Source）

Document:
- https://developer.android.com/about/versions/16/behavior-changes-all#opt-out

Parent document:
- https://developer.android.com/about/versions/16/behavior-changes-all#intent-redirect-attacks

Page:
- Behavior changes: all apps

Category:
- Security

Parent section:
- Improved security against Intent redirection attacks

Section:
- Opt out of Intent redirection handling

Subsections:
- For applications compiling against Android 16 (API level 36) SDK or higher
- For applications compiling against Android 15 (API level 35) or lower

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `OS_UPDATE_ALL_APPS`

追加条件（Additional conditions）:
- この subsection 自体は、Android 16 の既定 Intent redirection hardening を明示的に opt out する API / guidance である。
- 実行時に影響するのは、アプリが nested / sub-level Intent を launch し、かつ対象 Intent object に `Intent#removeLaunchSecurityProtection()` を呼ぶ、または reflection で同メソッドを呼ぶ場合。
- `targetSdkVersion 36` は opt-out API の実行時 gate ではない。`compileSdkVersion 36` は直接 API 参照の可否に関係する。

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 16 に OS アップデートしただけで default hardening は適用されるか | Yes / Conditional | 親項目は Android 16 all apps ページ掲載。AOSP Activity launch path で targetSdkVersion 36 gate は見つからない。影響は nested Intent forwarding pattern を持つ場合。 |
| opt-out は自動適用されるか | No | `Intent#removeLaunchSecurityProtection()` を対象 Intent object に明示的に呼ぶ必要がある。 |
| targetSdkVersion 36 が opt-out の条件か | No | AOSP の opt-out method / Activity launch enforcement に targetSdkVersion 36 gate は見つからない。 |
| compileSdkVersion 36 が関係するか | Yes | 公式文書は API 36 SDK 以上で `removeLaunchSecurityProtection()` を直接利用、API 35 以下で reflection fallback と説明している。 |
| opt-out は安全な推奨対応か | No / Exceptional | 公式文書は security protection の opt-out は脆弱性リスクを増やすため、絶対に必要な場合だけ使うよう注意している。 |
| Activity 以外の service / broadcast に同じ enforcement があるか | Evidence gap | `prepareToLeaveProcess()` は確認したが、`ActivityStarter` 相当の creator-token enforcement は未確認。 |

### 調査日（Investigation Date）

2026-07-06

### 信頼度（Confidence）

- Medium

理由:
- 公式文書の `#opt-out` / `#targeting-16` / `#targeting-before-16` 節を 2026-07-06 に再確認し、依頼文の Original statements と実質一致することを確認した。
- AOSP では `Intent#removeLaunchSecurityProtection()` の public API surface、実装、creator token / missing token flag、Activity launch path の enforcement、関連 unit test を確認した。
- `android-15.0.0_r36` tag の `core/api/current.txt` にも flagged `removeLaunchSecurityProtection()` が存在するため、AOSP tag 間の単純な API 追加差分としては扱わない。公式 SDK / compile guidance と実機 SDK availability は別途検証対象。
- service / bind / broadcast では同じ protection が activity launch と同等に適用される根拠を確認できていない。

---

## 公式ドキュメント確認（Original Documentation）

### 原文要旨（Statements Verified）

公式文書は以下を説明している。

- Android 16 は launch security protections から opt out する新 API を導入する。
- default security behavior が正当な app use case と干渉する特定ケースでは opt-out が必要になる場合がある。
- opt-out は security vulnerability risk を増やすため、絶対に必要な場合に限り、security impact を評価してから使うべきである。
- Android 16 / API 36 SDK 以上で compile するアプリは `Intent#removeLaunchSecurityProtection()` を直接呼べる。
- Android 15 / API 35 SDK 以下で compile するアプリは reflection で同メソッドにアクセスできるが、推奨されない。
- reflection は将来 API が変わると壊れやすいため、可能なら compile SDK を Android 16 / API 36 以上へ更新して直接 API を使うべきである。

### 差分確認（Documentation Drift）

- 2026-07-06 時点で、依頼文の Original statements と公式本文に実質的な差分は見つからなかった。
- `#opt-out` は親項目の subsection であり、独立した default behavior ではなく、Android 16 Intent redirection hardening に対する例外手段として記述されている。

---

## Facts

- `Intent#removeLaunchSecurityProtection()` は Android 16 tag の `frameworks-base/core/java/android/content/Intent.java` に `@FlaggedApi(FLAG_PREVENT_INTENT_REDIRECT)` 付きで存在する。
- Android 16 の `Intent#removeLaunchSecurityProtection()` は、対象 Intent object の `EXTENDED_FLAG_MISSING_CREATOR_OR_INVALID_TOKEN` をクリアし、`removeCreatorTokenInfo()` により creator token info を削除する。
- `core/api/current.txt` では `removeLaunchSecurityProtection()` が `@FlaggedApi("android.security.prevent_intent_redirect")` の public method として現れる。
- `ActivityStarter` には `ENABLE_PREVENT_INTENT_REDIRECT_TAKE_ACTION = 29623414` が `@ChangeId` / `@Overridable` として定義され、missing / invalid token、URI grant、start permission、IntentFirewall、PermissionPolicy 関連の abort / exception path で参照される。
- `ActivityStarter` の確認範囲では、`targetSdkVersion 36` を条件にする gate は見つからない。
- `Intent` の copy constructor、`cloneForCreatorToken()`、`fillIn()`、parcel read/write は、`mExtendedFlags` と `mCreatorTokenInfo` を Intent state として扱う。opt-out は app-wide 設定ではなく、対象 Intent state に対する操作である。
- `IntentTest` は extra Intent key collection、creator token info removal、fillIn 時の creator token info merge を検証している。
- `ActivityManagerServiceTest` は `addCreatorToken()`、fill-in Intent への token 付与、不正に差し込まれた Intent への `EXTENDED_FLAG_MISSING_CREATOR_OR_INVALID_TOKEN` 設定を検証している。
- `android-15.0.0_r36` の `core/api/current.txt` にも flagged `removeLaunchSecurityProtection()` symbol が見つかるため、今回の tag comparison では「Android 16 tag で初めて symbol が追加された」とは結論しない。

## Observations

- opt-out API は default hardening を無効化する互換性 escape hatch であり、通常の移行策ではない。
- opt-out は「この app 全体を Intent redirection hardening から外す」設定ではなく、launch しようとしている specific Intent object の creator token / missing token state を外す操作として実装されている。
- Android 16 の Activity launch path は、nested Intent の creator token が欠落または不正な場合、または creator 側が URI grant / activity launch 権限を満たさない場合に、SecurityException / abort / logging の対象にできる。
- compileSdkVersion 36 は、Java/Kotlin source から `removeLaunchSecurityProtection()` を直接参照できるかの条件であり、runtime で hardening が適用されるかの targetSdkVersion gate ではない。
- compileSdkVersion 35 以下の reflection fallback は、公式文書上は可能とされるが、将来 API 変更や実行 OS に method が存在しないケースで壊れやすい。
- `startService()` / `bindService()` / broadcast path でも `prepareToLeaveProcess()` は通るが、今回確認した強い enforcement は `ActivityStarter` の Activity launch path である。

## Hypotheses

- Android 16 実機では、default hardening によって壊れる正当な first-party nested Intent flow がある場合、対象 nested Intent にだけ `removeLaunchSecurityProtection()` を呼ぶと launch が通る可能性が高い。
- Android 15 device 上で API 36 compile app が直接 method を呼ぶ場合、実際の platform SDK / runtime availability と desugaring ではなく通常の framework method resolution に依存するため、対象 OS image に method がなければ実行時エラーになり得る。今回の AOSP tag では Android 15 側にも symbol が見えるが、製品 SDK / device image での挙動は実機検証が必要である。
- service / broadcast で nested Intent forwarding を行うアプリも、将来または別 code path で hardening の影響を受ける可能性はあるが、今回の AOSP evidence だけでは Activity launch と同等とは言えない。

## Conclusions

- この subsection の主な結論は、Android 16 Intent redirection hardening には opt-out API があるが、利用は例外的・限定的にすべき、という点である。
- 影響分類は親項目に合わせて `OS_UPDATE_ALL_APPS` とする。ただし opt-out path は、アプリが明示的に `removeLaunchSecurityProtection()` を呼ぶ場合だけ成立する追加条件付き behavior として扱う。
- 顧客向け説明では、Android 16 OS update による default hardening、targetSdkVersion 36 化、compileSdkVersion 36 による直接 API 利用可否、opt-out による security protection removal を分ける必要がある。
- 推奨対応は、広範な opt-out ではなく、nested Intent の origin / component / package / action / data / categories / flags / ClipData / URI grants を allowlist validation することである。

---

## AOSP 調査（AOSP Investigation）

### 関連ファイル（Related Files）

- `frameworks-base/core/java/android/content/Intent.java`
- `frameworks-base/core/api/current.txt`
- `frameworks-base/core/java/android/security/responsible_apis_flags.aconfig`
- `frameworks-base/services/core/java/com/android/server/am/ActivityManagerService.java`
- `frameworks-base/services/core/java/com/android/server/wm/ActivityStarter.java`
- `frameworks-base/services/core/java/com/android/server/wm/ActivityStartController.java`
- `frameworks-base/core/java/android/app/ContextImpl.java`
- `frameworks-base/core/java/android/app/Instrumentation.java`
- `frameworks-base/core/tests/coretests/src/android/content/IntentTest.java`
- `frameworks-base/services/tests/mockingservicestests/src/com/android/server/am/ActivityManagerServiceTest.java`

### 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル（File / symbol） | Android 15 baseline | Android 16 target | relevance |
| --- | --- | --- | --- |
| `Intent#removeLaunchSecurityProtection()` | `android-15.0.0_r36` の API surface に flagged symbol が見える。 | `@FlaggedApi(FLAG_PREVENT_INTENT_REDIRECT)`。missing / invalid token flag を消し creator token info を削除。 | 公式 opt-out API の実装根拠。 |
| `Intent#mExtendedFlags` / `mCreatorTokenInfo` | creator token state は Intent 内部状態として扱われる。 | copy / fillIn / parcel path でも Intent state として扱われる。 | opt-out が per Intent object/state である根拠。 |
| `Intent#maybeMarkAsMissingCreatorTokenInternal()` | foreign parcel 由来かつ trusted token がない Intent を missing / invalid と扱う実装がある。 | 同様に `EXTENDED_FLAG_MISSING_CREATOR_OR_INVALID_TOKEN` を付与。 | default hardening が opt-out 前に何を検知するかの根拠。 |
| `ActivityManagerService#addCreatorToken()` | nested Intent に creator token を付与する。 | server-side collection / stats logging の強化を含む。 | top-level Intent から sub-level Intent へ creator 情報を紐づける根拠。 |
| `ActivityStarter` | missing token / creator permission / URI grant check path がある。 | `ENABLE_PREVENT_INTENT_REDIRECT_TAKE_ACTION` により abort / throw path を制御。 | Activity launch の default hardening が実際に使われる根拠。 |
| `ContextImpl#startServiceCommon()` / bind path | `prepareToLeaveProcess()` は呼ぶ。 | 同様。 | service / bind に関する evidence gap を切り分けるために確認。 |
| `IntentTest` | N/A | creator token info removal、nested key collection、fillIn merge を検証。 | opt-out が触る内部 state の test evidence。 |
| `ActivityManagerServiceTest` | N/A | nested Intent token 付与、不正差し込み Intent の missing flag を検証。 | attack pattern 検出の test evidence。 |

### 差分解釈（Diff Interpretation）

| 確認した差分 / 状態（Observed diff/state） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度 |
| --- | --- | --- | --- |
| Android 16 `removeLaunchSecurityProtection()` は missing / invalid token flag と creator token info を外す | opt-out は default hardening の creator token protection を外す API。 | 公式 `Opt out of Intent redirection handling` の直接根拠。 | High |
| Android 16 `ActivityStarter` は missing token / creator URI grant / permission failure を abort / exception 対象にする | opt-out しない場合の default hardening。 | opt-out の意味を説明する前提。 | High |
| `ENABLE_PREVENT_INTENT_REDIRECT_TAKE_ACTION = 29623414` は `@Overridable` | compat override 可能な Change ID として実装されている。 | testing / rollback の可能性はあるが、公式 compat list には未確認。 | Medium |
| Android 15 tag にも flagged API symbol が存在 | API surface の tag diff だけでは「Android 16 で新規追加」とは言えない。 | 公式 SDK guidance と AOSP tag の前段実装を分ける必要がある。 | Medium |
| service / bind / broadcast の同等 enforcement は未確認 | Activity launch に比べて evidence が弱い。 | request の startService / bindService / sendBroadcast は要検証扱い。 | Medium |

### Compat framework

| 項目 | 確認結果 |
| --- | --- |
| Change ID | `29623414` |
| Symbol | `ENABLE_PREVENT_INTENT_REDIRECT_TAKE_ACTION` |
| AOSP annotation | `@ChangeId`, `@Overridable` |
| targetSdkVersion gate | 確認範囲では見つからない |
| Default state | `@Disabled` / `@EnabledAfter` は見つからない。公式 compat framework 一覧には該当 ID を確認できない |
| opt-out API 自体の compat flag | `@FlaggedApi(FLAG_PREVENT_INTENT_REDIRECT)`。aconfig `prevent_intent_redirect` family と関係 |

---

## 適用条件（Applicability）

### Android 16 / targetSdkVersion 35

- default hardening: nested Intent Activity launch pattern では適用され得る。
- opt-out: runtime 上 method が存在し、対象 Intent に呼ばれれば opt-out になり得る。
- direct compile access: compileSdkVersion 36 でなければ通常は source から直接参照できない。

### Android 16 / targetSdkVersion 36

- default hardening: targetSdkVersion 35 と同様。
- opt-out: targetSdkVersion 36 固有ではない。
- direct compile access: compileSdkVersion 36 以上なら直接 API として呼べる。

### Android 15 / targetSdkVersion 36

- Android 16 公式挙動と同一とは扱わない。
- 今回の AOSP tag では Android 15 側にも flagged API symbol と前段実装が見えるため、Android 15 実機 / SDK / flag state の比較検証が必要。
- Android 15 device で reflection / direct call を使う場合は、対象 device image に method が存在するか、flag 状態、hidden/flagged API exposure を確認する。

---

## 期待挙動マトリクス（Expected Behavior Matrix）

| シナリオ | 期待挙動 / 調査結論 |
| --- | --- |
| Android 16 / targetSdkVersion 35 / default hardening / no opt-out | nested Intent Activity launch が hardening 対象になり得る。 |
| Android 16 / targetSdkVersion 36 / default hardening / no opt-out | targetSdkVersion 35 と同様。targetSdkVersion 36 固有ではない。 |
| Android 16 / targetSdkVersion 35 / `removeLaunchSecurityProtection()` opt-out | 対象 Intent object の creator token protection を外す。security review 必須。 |
| Android 16 / targetSdkVersion 36 / `removeLaunchSecurityProtection()` opt-out | targetSdkVersion 35 と同様。 |
| Android 16 / compileSdkVersion 36 / direct API call | source から `Intent#removeLaunchSecurityProtection()` を直接呼べる。 |
| Android 16 / compileSdkVersion 35 or lower / reflection call | 公式は可能だが非推奨。fragile / future breakage risk。 |
| Android 16 / reflection succeeds | 対象 method が runtime に存在し、呼び出しが成功すれば direct API と同等に opt-out し得る。 |
| Android 16 / reflection fails | fallback 失敗。default hardening が残るか、app 側で例外処理が必要。 |
| Android 15 / targetSdkVersion 36 / direct API compiled app | 技術的比較が必要。AOSP tag には symbol があるが、Android 16 公式挙動とは分ける。 |
| Android 15 / targetSdkVersion 36 / reflection call | 技術的比較が必要。method 不在なら reflection failure。 |
| Android 16 / top-level Intent only | 通常の Intent launch なら影響軽微。 |
| Android 16 / nested Intent from trusted in-app source | default hardening にかかる可能性はある。opt-out より allowlist / first-party validation を優先。 |
| Android 16 / nested Intent from untrusted external source | opt-out すべきではない。attack risk が高い。 |
| Android 16 / nested Intent with explicit component | private / permission-protected component targeting は hardening で問題化しやすい。 |
| Android 16 / nested Intent with implicit action | action / category / data allowlist が必要。 |
| Android 16 / nested Intent with package set | package allowlist と component/exported/permission check が必要。 |
| Android 16 / nested Intent with URI grant flags | creator の URI grant 権限も問題になる。opt-out は data exposure risk を増やす。 |
| Android 16 / nested Intent with ClipData URI | ClipData URI も validation / grant stripping 対象。 |
| Android 16 / startActivity nested Intent | confirmed Activity launch enforcement path。 |
| Android 16 / startActivityForResult nested Intent | Activity launch path として同様に検証対象。 |
| Android 16 / PendingIntent-based flow | PendingIntent の creator semantics と混同せず、nested Intent forwarding があるか確認。 |
| Android 16 / chooser / selector Intent flow | selector / chooser 内の nested Intent state と validation を個別確認。 |
| Android 16 / startService / bindService nested Intent | `prepareToLeaveProcess()` は確認。Activity launch と同等 enforcement は未確認。 |
| Android 16 / sendBroadcast nested Intent | 要検証。今回の confirmed enforcement には含めない。 |
| Android 16 / app validates nested Intent before launch | 推奨対応。component / package / action / data / flags / URI grants を allowlist。 |
| Android 16 / app forwards nested Intent without validation | default hardening により block / exception / abort の対象になり得る。 |
| Android 16 / app opts out only for allowlisted first-party flows | 例外対応として許容され得るが、security review と regression test が必要。 |
| Android 16 / app broadly opts out for all nested Intents | 非推奨。Intent redirection vulnerability risk を増やす。 |

---

## 影響対象（Affected App Categories）

- Intent router / dispatcher Activity を持つアプリ
- deep link / app link / auth callback を中継するアプリ
- SSO / login / payment / identity verification flow を扱うアプリ
- notification / shortcut / widget から nested Intent を起動するアプリ
- third-party SDK から渡された Intent を起動するアプリ
- plugin / mini-app / dynamic feature / modular navigation を持つアプリ
- file picker / document provider / media sharing など URI grant を扱うアプリ
- enterprise / companion / device management flow で Intent forwarding を使うアプリ
- legacy code で `getParcelableExtra()` した `Intent` をそのまま `startActivity()` するアプリ
- compileSdkVersion 36 へ更新して opt-out API を直接使う可能性があるアプリ
- compileSdkVersion 35 以下で reflection fallback を検討しているアプリ
- セキュリティレビューなしに opt-out すると危険なアプリ

---

## 推奨対応候補（Recommended Action Candidates）

- nested Intent を launch する前に、component / package / action / data / categories / flags / extras / ClipData / URI grants を allowlist validation する。
- `IntentSanitizer` または同等の sanitizer を導入し、外部入力由来の Intent をそのまま launch しない。
- URI grant flags と ClipData URI は、必要な allowlisted flow 以外では strip する。
- `removeLaunchSecurityProtection()` は、first-party 由来が確認できる互換性 flow に限定して呼ぶ。
- opt-out 呼び出し箇所には threat model、理由、対象 caller、許可 component / action、URI grant 方針を code review で残す。
- compileSdkVersion 35 以下で reflection fallback を使う場合は、method 不在 / invocation failure / future API change に対する fallback を用意する。ただし可能なら compileSdkVersion 36 へ更新して直接 API を使う。

---

## テスト観点（Test Viewpoints）

- Android 15 端末上の targetSdkVersion 35
- Android 16 端末上の targetSdkVersion 35
- Android 16 端末上の targetSdkVersion 36
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較
- compileSdkVersion 36 direct API build
- compileSdkVersion 35 以下 reflection fallback
- default hardening enabled / no opt-out
- `removeLaunchSecurityProtection()` called / not called
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
- opt-out scope regression: opt-out が想定 flow だけに限定されていること
- security regression testing for Intent redirection attacks

---

## Evidence gaps

- `android-15.0.0_r36` tag に flagged symbol があるため、Android 15 実機での default flag state、SDK stub exposure、reflection / direct call の実挙動は別途端末検証が必要。
- 公式 compat framework change list では `29623414` を確認できなかったため、ユーザー向け compat override command は未確認。
- service / bind / broadcast path の enforcement は Activity launch と同等とは確認できない。
- `removeLaunchSecurityProtection()` を呼んだ Intent が clone / parcel / fillIn / selector / chooser を経由する各パターンの最終挙動は、source 上の state propagation に基づく推定を含むため、実機 regression test が必要。

---

## Human Decision Placeholder

最終優先度（Final Priority）:
- TBD by human

最終 severity（Final Severity）:
- TBD by human

顧客説明優先度（Customer communication priority）:
- TBD by human

opt-out 許可方針（Opt-out approval policy）:
- TBD by human

リリース判定（Release readiness decision）:
- TBD by human

# Activity 起動のセキュリティ強化

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

### Behavior Change 文書（Behavior Change Source）

文書:
https://developer.android.com/about/versions/17/behavior-changes-17

関連文書:
- https://developer.android.com/guide/components/activities/secure-bal
- https://developer.android.com/reference/android/app/ActivityOptions#MODE_BACKGROUND_ACTIVITY_START_ALLOWED
- https://developer.android.com/reference/android/app/ActivityOptions#MODE_BACKGROUND_ACTIVITY_START_ALLOW_ALWAYS
- https://developer.android.com/reference/android/app/ActivityOptions#MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE
- https://developer.android.com/reference/android/content/IntentSender

セクション:
- Activity Security

ページ種別:
- Android 17 以上をターゲットにするアプリ

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- TARGET_SDK_37_CONDITIONAL

公式文書からの適用条件判断:
- 公式文書は、Android 17 で Activity 起動まわりを secure-by-default に近づけ、Background Activity Launch (BAL) restrictions を refined し、IntentSender にも protection を拡張すると説明している。
- 開発者は legacy `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` から、`MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` や `MODE_BACKGROUND_ACTIVITY_START_ALLOW_ALWAYS` のような granular controls へ移行する必要がある。
- Activity security guide は、foreground ではない app、visible activity を持たない app、または他 app から受け取った `PendingIntent` が Activity を起動しようとする場合を BAL と説明している。また、通知タップのように system が送信した `PendingIntent` からの起動は、background activity start が許可される例外として説明している。
- Activity security guide は、`PendingIntent` / `IntentSender` による起動では creator または sender のどちらかが BAL privileges を明示的に opt-in し、かつその app が BAL exception を満たす必要があると説明している。通常はユーザーが直接操作している sender 側が `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` を使うことが推奨される。
- AOSP では `BackgroundActivityStartController.ASM_RESTRICTIONS = 230590090L` が `@EnabledAfter(targetSdkVersion = BAKLAVA)` として定義され、Android 17 target 相当から activity security rules が有効になることを示す。

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 主条件ではない | `ASM_RESTRICTIONS` は `@EnabledAfter(targetSdkVersion = BAKLAVA)`。旧 targetSdkVersion は compat default で緩和される。 |
| targetSdkVersion 37 以上が必要か | Yes | `BAKLAVA` は Android 16 / API 36 相当で、`EnabledAfter` により Android 17 / API 37 target から有効。 |
| 追加の実行時条件があるか | ある | PendingIntent / IntentSender 経由の background activity start、ActivityOptions BAL mode、caller / real caller の visibility、permission / allowlist 状態。 |
| Compat Change ID が関係するか | Yes | `ASM_RESTRICTIONS = 230590090L`。 |

### 調査日（Investigation Date）

2026-06-18

### 信頼度（Confidence）

- High

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] targetSdkVersion に関係なく Android 17 の全アプリへ適用
- [ ] Android 17 以上かつ targetSdkVersion 37 以上で適用
- [x] targetSdkVersion 37 以上かつ追加の実行時条件を満たす場合に適用
- [ ] Mainline / Google Play system update に依存
- [ ] API 追加のみであり、挙動変更ではない
- [ ] 未確認 / 追加 evidence が必要

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 以上。
- targetSdkVersion: 37 以上。
- API condition: `PendingIntent` / `IntentSender` 実行時に `ActivityOptions#setPendingIntentBackgroundActivityStartMode` または関連 BAL mode を使う。
- App state condition: caller / real caller が background か visible か、visible window / foreground process / permission / allowlist / grace period のどれに該当するか。
- Option condition: `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` は visible 条件だけを評価し、`MODE_BACKGROUND_ACTIVITY_START_ALLOW_ALWAYS` は permission / allowlist など広い exemption を許す。

Compat framework:
- Change ID: `230590090L`
- 変更名: `ASM_RESTRICTIONS`
- 既定状態: `@EnabledAfter(targetSdkVersion = BAKLAVA)`。targetSdkVersion 37 以上で enabled。
- テスト時に切り替え可能か: `@Overridable` 付き compat change のため切り替え可能。

分類信頼度（Classification confidence）:
- High

分類根拠（Classification evidence）:
- 公式 Behavior Change 文書は Activity Security / BAL / IntentSender hardening を Android 17 target changes として説明している。
- 公式 Activity security guide は、通知タップを system-sent `PendingIntent` による BAL exception の例として示し、sender 側 opt-in では `ALLOW_IF_VISIBLE` を推奨している。
- AOSP `ActivityOptions` は `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` を deprecated とし、`ALLOW_IF_VISIBLE` / `ALLOW_ALWAYS` への移行を明記している。
- AOSP `BackgroundActivityStartController` は `ASM_RESTRICTIONS` ChangeId を `@EnabledAfter(BAKLAVA)` として定義する。
- AOSP `BackgroundActivityStartController` は `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` の場合に caller / real caller の visible / foreground 系 check に限定する。
- AOSP `MODE_BACKGROUND_ACTIVITY_START_ALLOW_ALWAYS` の場合に BAL permission、SYSTEM_ALERT_WINDOW、allowlisted uid / component などの広い exemption を評価する。

---

# エグゼクティブサマリー

Android 17 では、Background Activity Launch (BAL) restrictions がさらに強化され、PendingIntent / IntentSender 経由の Activity 起動でも、起動を許可する条件をより明示的に選ぶ必要がある。従来の broad opt-in である `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` は deprecated になり、通常は `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE`、本当に常時許可が必要な特殊用途だけ `MODE_BACKGROUND_ACTIVITY_START_ALLOW_ALWAYS` を使う設計へ移行する。

AOSP では `BackgroundActivityStartController.ASM_RESTRICTIONS = 230590090L` が `@EnabledAfter(targetSdkVersion = BAKLAVA)` として定義されている。これは Android 16 target までは互換扱い、Android 17 / targetSdkVersion 37 以上では新しい Activity Security rules が enabled になることを示す。

この変更は、通知、アラーム、認証、決済、デバイス連携、外部アプリ連携などで background から画面を起動する設計に影響する。特に PendingIntent を他者に渡す、または IntentSender を実行する箇所は、visible 条件で十分か、常時許可が本当に必要かを見直す必要がある。

---

# 公式ドキュメント確認

## 原文（Statement）

ページタイトル:
- Behavior changes: Apps targeting Android 17 or higher

ページ URL:
- https://developer.android.com/about/versions/17/behavior-changes-17

セクションタイトル:
- Activity Security

検証対象の原文:
- Android 17 は secure-by-default architecture へ移行し、phishing、interaction hijacking、confused deputy attacks などを緩和する。
- BAL restrictions が refined され、protections が `IntentSender` に拡張される。
- 開発者は legacy `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` から、`MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` などの granular controls へ移行する必要がある。

参考 URL:
- https://developer.android.com/guide/components/activities/secure-bal

参考 URL から確認した補足:
- BAL は、foreground ではない app、visible activity を持たない app、または他 app から受け取った `PendingIntent` が Activity を起動しようとする場合に発生する。
- Background activity start が許可される例外には、app が visible window を持つ場合、system が送信した `PendingIntent` から Activity が起動される場合、launcher / widget などユーザー操作に基づく場合が含まれる。
- `PendingIntent` / `IntentSender` による Activity 起動では、creator または sender が BAL privileges を opt-in しており、かつその app が BAL exception を満たす必要がある。
- sender 側 opt-in では `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` が推奨される。この mode は、`PendingIntent` 送信時に sender app が画面上で visible な場合だけ許可するため、ユーザー操作に紐づく起動であることを強める。

## 解釈（Interpretation）

この変更は、background から Activity を起動できる条件を targetSdkVersion 37 以上でより限定する Activity launch security change である。ユーザーに見えている文脈からの起動は `ALLOW_IF_VISIBLE` で許可し、visible でない状態からの起動は通知タップなど、より明示的な user interaction path に寄せることが求められる。

通知タップについては、system が通知の `PendingIntent` を送信する flow であり、公式 guide 上も許可例外として扱われる。そのため、他アプリ操作中に Foreground Service notification や push notification をユーザーがタップし、通知の Activity `PendingIntent` が直接 Activity を起動する場合は、通常 BAL 制限の主な問題ではない。一方、通知タップ後に broadcast receiver / service / 非同期 callback を挟み、その component から改めて Activity を起動する実装では、system-sent notification tap の例外から外れる可能性があるため、別途確認が必要である。

---

# 変更内容（What Changed）

公式文書上の変更点:
- Android 17 は Activity 起動まわりを secure-by-default に近づける。
- BAL restrictions が refined され、IntentSender に protection が拡張される。
- `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` 依存から granular controls への移行が必要。
- `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` は calling app が visible な場合に activity start を限定する。
- Activity security guide は、通知タップを system-sent `PendingIntent` による許可例外として扱う。
- `PendingIntent` / `IntentSender` では、creator または sender が BAL privileges を opt-in し、かつその app が visible window などの BAL exception を満たす必要がある。
- strict mode / lint checks により legacy pattern の検出が推奨される。

AOSP で確認した変更点:
- `ActivityOptions.MODE_BACKGROUND_ACTIVITY_START_ALLOWED` は deprecated となり、`ALLOW_IF_VISIBLE` または `ALLOW_ALWAYS` の利用を案内する。
- `ActivityOptions.MODE_BACKGROUND_ACTIVITY_START_ALLOW_ALWAYS` は、privileged context を含む広い BAL privileges を付与する mode として定義され、慎重な利用が必要と説明される。
- `ActivityOptions.MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` は、app が visible window を持つ場合だけ BAL privileges を付与する推奨 mode として定義される。
- `BackgroundActivityStartController.ASM_RESTRICTIONS` は `@EnabledAfter(targetSdkVersion = BAKLAVA)` かつ `@Overridable` の compat change。
- `BackgroundActivityStartController.checkBackgroundActivityStartAllowedByCaller` / `checkBackgroundActivityStartAllowedByRealCaller` は `ALLOW_IF_VISIBLE` の場合に visible / foreground 系 check に限定する。
- `ALLOW_ALWAYS` の場合は BAL permission、SYSTEM_ALERT_WINDOW、allowlisted uid / component など広い exemption を評価する。

---

# AOSP 調査（AOSP Investigation）

## チェックアウト状態

根拠利用前に確認したコマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list android-17.0.0_r1
```

結果:
- `frameworks-base` working tree: clean at the time of investigation.
- From tag: `android-16.0.0_r4` exists.
- To tag: `android-17.0.0_r1` exists.

## 関連ファイル（Related Files）

- `core/java/android/app/ActivityOptions.java`
- `core/java/android/app/PendingIntent.java`
- `core/java/android/content/IntentSender.java`
- `services/core/java/com/android/server/wm/BackgroundActivityStartController.java`
- `services/core/java/com/android/server/wm/ActivityStarter.java`
- `services/core/java/com/android/server/wm/ActivityTaskManagerService.java`

## 確認したソース文脈（Source Context Reviewed）

| File / symbol | Android 16 baseline | Android 17 behavior | 関連性 |
| --- | --- | --- | --- |
| `ActivityOptions.MODE_BACKGROUND_ACTIVITY_START_ALLOWED` | BAL broad opt-in として利用 | deprecated。`ALLOW_IF_VISIBLE` / `ALLOW_ALWAYS` への移行を案内 | 公式文書の legacy constant migration。 |
| `ActivityOptions.MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` | 既存だが Android 17 で推奨 migration path として強調 | visible window を持つ場合だけ BAL privileges を付与する mode | 推奨される granular control。 |
| `ActivityOptions.MODE_BACKGROUND_ACTIVITY_START_ALLOW_ALWAYS` | 既存だが Android 17 で broad privilege として明確化 | privileged context を含む広い BAL privileges を付与 | 特殊用途向けの強い opt-in。 |
| `BackgroundActivityStartController.ASM_RESTRICTIONS` | ChangeId はあるが Android 17 target までは disabled | `@EnabledAfter(targetSdkVersion = BAKLAVA)` により targetSdkVersion 37 以上で enabled | targetSdkVersion ゲートの中核 evidence。 |
| `checkBackgroundActivityStartAllowedByCaller` | broad BAL exemption を評価 | `ALLOW_IF_VISIBLE` では caller visible / non-app visible / foreground process のみ評価 | visible-only mode の enforcement。 |
| `checkBackgroundActivityStartAllowedByRealCaller` | broad BAL exemption を評価 | `ALLOW_IF_VISIBLE` では real caller visible / foreground 系のみ評価。`ALLOW_ALWAYS` で permission / allowlist 系を評価 | IntentSender / PendingIntent sender 側の enforcement。 |

Source context の補足:
- Entry point / caller: `PendingIntent.send()` / `IntentSender` 実行時に `ActivityOptions` の BAL mode が `BackgroundActivityStartController` へ渡る。
- 関連性: Activity 起動の可否を最終的に判断する WM policy が、ActivityOptions の mode と caller visibility を使って BAL を許可 / 拒否する。
- Baseline Android behavior: Android 16 target 相当では `ASM_RESTRICTIONS` が compat デフォルト無効。
- Target Android behavior: Android 17 / targetSdkVersion 37 以上では `ASM_RESTRICTIONS` が enabled になり、visible-only / always の granular mode に基づく判定が適用される。
- Source diff type: changed condition / gate、changed default、added API guidance。
- Excluded code paths: ordinary foreground `startActivity`、accessibility global actions、drag and drop など BAL / IntentSender 起動と直接関係しない activity launch path は除外した。

## 差分解釈（Diff Interpretation）

| 観測した diff | 解釈 | Behavior Change との関連 | 信頼度 |
| --- | --- | --- | --- |
| `ASM_RESTRICTIONS` `@EnabledAfter(BAKLAVA)` | changed condition / gate | Android 17 target で Activity Security rules が enabled | High |
| `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` deprecated | changed API guidance | broad opt-in から granular mode への移行を促す | High |
| `ALLOW_IF_VISIBLE` visible-only branch | changed behavior | visible な caller / real caller だけ BAL privileges を許可 | High |
| `ALLOW_ALWAYS` broad exemption branch | changed behavior | 常時許可が必要な特殊用途を explicit opt-in に分離 | High |

---

# 事実・観察・仮説・結論

## 事実（Facts）

- `frameworks-base` の `android-16.0.0_r4` と `android-17.0.0_r1` tag は存在し、調査時点の working tree は clean。
- `ActivityOptions.MODE_BACKGROUND_ACTIVITY_START_ALLOWED` は deprecated で、`ALLOW_IF_VISIBLE` / `ALLOW_ALWAYS` への移行を案内している。
- `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` は app が visible window を持つ場合だけ BAL privileges を付与する。
- `MODE_BACKGROUND_ACTIVITY_START_ALLOW_ALWAYS` は privileged context を含む広い BAL privileges を付与する。
- `BackgroundActivityStartController.ASM_RESTRICTIONS = 230590090L` は `@EnabledAfter(targetSdkVersion = BAKLAVA)` と `@Overridable` を持つ。
- `ALLOW_IF_VISIBLE` の場合、caller / real caller の判定は visible / foreground 系 check に限定される。

## 観察（Observations）

- 公式文書の「secure-by-default」「IntentSender への BAL protection 拡張」は、AOSP 上では `ActivityOptions` の granular modes と WM の BAL evaluation branch として確認できる。
- `ALLOW_ALWAYS` は従来の broad allow と近いが、名前と documentation がより明示的になり、通常用途では `ALLOW_IF_VISIBLE` が推奨される。
- `ASM_RESTRICTIONS` は targetSdkVersion 37 以上で有効になるため、OS update だけではなく target update 時の互換性リスクとして扱うべきである。

## 仮説（Hypotheses）

- strict mode / lint checks は `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` や broad PendingIntent BAL opt-in の利用を検出し、Android 17 target 移行前の修正を促す目的で追加されている。

## 結論（Conclusions）

- この Behavior Change は `TARGET_SDK_37_CONDITIONAL` と分類する。
- PendingIntent / IntentSender 経由で background activity start を許可しているアプリは、targetSdkVersion 37 で `ALLOW_IF_VISIBLE` または `ALLOW_ALWAYS` への明示的な移行判断が必要。
- 通常用途では `ALLOW_IF_VISIBLE` を優先し、visible でない状態からの画面起動は通知などの user-mediated path へ寄せるべきである。
- Foreground Service や通知を使っていても、それ自体が background Activity 起動を常に許可するわけではない。ユーザーが通知、popup、visible Activity 上のボタンを明示的にタップして PendingIntent / IntentSender を実行する flow では影響は限定的と考えられる一方、service / receiver がユーザー操作なしで Activity を前面表示しようとする flow は制限対象になり得る。
- 他アプリを操作中に Foreground Service notification や push notification をユーザーがタップする flow は、通知 `contentIntent` / action の PendingIntent が直接 Activity を開く限り user-mediated launch として扱えるため、通常は BAL 制限の主な問題ではない。ただし、通知タップ後に broadcast receiver / service を挟み、その component から改めて Activity を起動する notification trampoline 型の実装や、tap 後に非同期処理を経て background から起動する実装は別途制限対象になり得る。
- 信頼度は High。AOSP targetSdk gate、API deprecation、visible-only enforcement branch が確認できた。

---

# 開発者影響

影響を受ける可能性が高いアプリ:
- notification / alarm / reminder から画面起動するアプリ
- authentication / payment / device pairing で PendingIntent を使うアプリ
- companion device / external device prompt に応答して画面起動するアプリ
- 他アプリや system component に IntentSender を渡すアプリ

対応候補:
- `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` の利用箇所を棚卸しする。
- ほとんどの user-visible flow では `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` に移行する。
- connected device prompt など visible でなくても直ちに画面起動が必要な特殊用途だけ `MODE_BACKGROUND_ACTIVITY_START_ALLOW_ALWAYS` を検討する。
- 通知タップ、表示中 popup、表示中 Activity のボタン押下など、ユーザー操作に直結する PendingIntent 実行は `ALLOW_IF_VISIBLE` で足りるかを優先確認する。Foreground Service からユーザー操作なしで Activity を直接起動する設計は、通知経由などの user-mediated path へ変更する。
- 通知経由の起動は、notification の `contentIntent` / action が Activity PendingIntent か、broadcast / service trampoline かを分けて確認する。前者は影響限定的、後者は設計変更候補として扱う。
- targetSdkVersion 37 で caller visible / background、real caller visible / background、permission / allowlist ありなしを分けてテストする。

---

# サービス影響例

このセクションは、公式文書と AOSP 根拠から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: Uber Driver / DoorDash Dasher の緊急画面・注文画面起動

- 具体サービス例: Uber Driver、DoorDash Dasher、出前館配達員アプリ、タクシー配車ドライバーアプリ。
- 影響を受ける実装パターン: background service / receiver がユーザー操作なしで Activity を前面起動する、または broad `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` に依存する PendingIntent を渡す実装。
- 発生条件: Android 17 / targetSdkVersion 37 以上で `ASM_RESTRICTIONS` が有効になり、caller / real caller が visible ではないのに `ALLOW_IF_VISIBLE` 相当の flow で Activity 起動しようとする場合。
- ユーザーに見える症状: 新規注文、緊急確認、デバイス接続 prompt などが自動で前面表示されず、通知経由の操作が必要になる可能性。
- 技術的に起きていること: BAL privileges が granular mode で評価され、visible window を持たない caller には `ALLOW_IF_VISIBLE` での background Activity start が許可されない。
- 推奨対応シーン: driver / delivery / field service の high-priority prompt、connected device prompt、alarm / reminder 起動。
- 検証観点: notification tap 直結の Activity PendingIntent、broadcast / service trampoline、caller visible / background、`ALLOW_ALWAYS` が本当に必要な flow。
- 根拠: `ASM_RESTRICTIONS` `@EnabledAfter(BAKLAVA)`、`ALLOW_IF_VISIBLE` / `ALLOW_ALWAYS` branch、Activity security guide。
- Confidence（信頼度）: High。
- 注意: 上記サービスで発生確認した事実ではない。通知タップから直接 Activity PendingIntent を開く flow は通常影響が限定的。

## 例2（Example 2）: Google Calendar / Slack / Microsoft Teams の通知タップ・リマインダー

- 具体サービス例: Google Calendar、Slack、Microsoft Teams、Todoist。
- 影響を受ける実装パターン: notification action や reminder から直接 Activity PendingIntent ではなく、broadcast receiver / service を挟んで後から Activity を起動する notification trampoline 型実装。
- 発生条件: targetSdkVersion 37 で background component が user-mediated exception から外れた状態で Activity を起動する場合。
- ユーザーに見える症状: 通知をタップしても対象画面が開かない、非同期処理後の確認画面が前面表示されない可能性。
- 技術的に起きていること: system-sent notification PendingIntent 自体は許可例外になり得るが、receiver / service を挟んで再度 background start すると BAL 判定対象になる。
- 推奨対応シーン: notification contentIntent / action、calendar reminder、chat call / meeting join、auth prompt。
- 検証観点: Activity PendingIntent 直結か、trampoline か、非同期処理後の startActivity か、`ALLOW_IF_VISIBLE` で足りるか。
- 根拠: 公式 Activity security guide、report の notification tap 例外整理、AOSP の real caller / caller visibility branch。
- Confidence（信頼度）: High。
- 注意: 上記サービスで発生確認した事実ではない。通知設計と PendingIntent 実行経路を個別に確認する必要がある。

---

# テスト観点（Test Matrix）

| 端末 OS | targetSdkVersion | BAL mode | Caller state | 期待挙動 |
| --- | --- | --- | --- | --- |
| Android 17 | 36 | `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` | background | 互換扱い。`ASM_RESTRICTIONS` は デフォルト無効。 |
| Android 17 | 37 | `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` | visible | Activity start が許可される想定。 |
| Android 17 | 37 | `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` | background | Activity start が拒否される想定。 |
| Android 17 | 37 | `MODE_BACKGROUND_ACTIVITY_START_ALLOW_ALWAYS` | background + valid exemption | Activity start が許可される可能性。用途を限定して確認が必要。 |

---

# 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断

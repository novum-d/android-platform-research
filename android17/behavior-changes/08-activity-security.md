# Activity Security

## Metadata

### Android Versions

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP tag

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

### Behavior Change Source

Document:
https://developer.android.com/about/versions/17/behavior-changes-17

Related documents:
- https://developer.android.com/reference/android/content/IntentSender
- https://developer.android.com/reference/android/app/ActivityOptions#MODE_BACKGROUND_ACTIVITY_START_ALLOWED
- https://developer.android.com/reference/android/app/ActivityOptions#MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE

Section:
Activity Security

Page type:
- Apps targeting Android 17 or higher

### Classification Snapshot

Primary classification:
- UNKNOWN_NEEDS_MORE_EVIDENCE

Initial applicability assumption from official documentation:
- 公式文書は、Android 17 で phishing、interaction hijacking、confused deputy attacks のような high-severity exploits を抑制するため、Activity 起動まわりを secure-by-default architecture へ近づけると説明している。
- 開発者影響として、Background Activity Launch (BAL) restrictions を IntentSender へ拡張し、legacy `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` から、より細かい `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` などへ移行する必要があると説明している。
- 追加条件として、background activity start、IntentSender 経由の activity launch、ActivityOptions の BAL opt-in mode、呼び出し元アプリの visible state が関係する。
- ただし、local `frameworks-base` に Android 17 AOSP tag がないため、BAL hardening の実装差分、IntentSender への保護拡張、targetSdkVersion gate、strict mode / lint 対応、Compat Change ID、default state は未検証である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

At-a-glance impact:

| Question | Answer | Evidence |
| --- | --- | --- |
| Android 17 OS update only? | Unknown | 公式ページは apps targeting Android 17 向けだが、AOSP gate 未確認。 |
| targetSdkVersion 37 required? | Likely, but unverified | ページ種別は Android 17 / API level 37 以上を target としているが、原文は gate の詳細を示していない。 |
| Additional runtime conditions? | Yes | BAL、IntentSender、ActivityOptions BAL mode、calling app visibility が関係する。 |
| Compat Change ID involved? | Unknown | Android 17 tag と compat framework evidence が未確認。 |

### Investigation Date

2026-06-10

### Confidence

- Low

### Applicability Classification

Applies when:
- [ ] OS update / all apps on Android 17 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 37 on Android 17+
- [ ] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [x] Unknown / needs more evidence

Required runtime conditions:
- Android version: Android 17 以上が前提と考えられるが、AOSP tag 未取得。
- targetSdkVersion: 公式ページ種別上は 37 以上が主対象。ただし AOSP gate 未確認。
- Device/form factor: 公式抜粋では条件なし。
- Permission/API/component condition: background activity launch、IntentSender、ActivityOptions BAL mode、`MODE_BACKGROUND_ACTIVITY_START_ALLOWED`、`MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE`。
- App state/process condition: app が background / visible か、呼び出し元または送信元が Activity 起動を許可できる状態か。

Compat framework:
- Change ID: Unknown
- Change name: Unknown
- Default state: Unknown
- Toggleable for testing: Unknown

Classification confidence:
- Low

Classification evidence:
- Official documentation page: `behavior-changes-17`
- Original applicability statement: Activity Security、BAL hardening、IntentSender への保護拡張、legacy BAL opt-in constant から granular controls への移行。
- AOSP targetSdk gate: 未確認。local `frameworks-base` に `android-17*` tag がない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# Executive Summary

Android 17 では、Activity 起動まわりの security hardening として、Background Activity Launch (BAL) restrictions が IntentSender にも拡張される、と公式文書は説明している。開発者は legacy `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` から、呼び出し元が visible な場合などに限定する `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` のような granular controls へ移行する必要がある。

この変更は、通知、アラーム、認証、外部連携、PendingIntent / IntentSender 経由の画面起動など、background から Activity を起動する設計に影響する可能性がある。目的は phishing、interaction hijacking、confused deputy attacks の攻撃面を減らすことである。

ただし、現時点の local `frameworks-base` には Android 17 AOSP tag がないため、実装差分、targetSdkVersion gate、IntentSender の具体的な適用範囲、Compat Change ID は未確認である。

---

# Original Documentation

## Statement

Page title:
- Behavior changes: Apps targeting Android 17 or higher

Page URL:
- https://developer.android.com/about/versions/17/behavior-changes-17

Page type:
- apps targeting Android 17

Section title:
- Activity Security

Original statement being verified:

> In Android 17, the platform continues its shift toward a "secure-by-default" architecture, introducing a suite of enhancements designed to mitigate high-severity exploits such as phishing, interaction hijacking, and confused deputy attacks.

The supplied official text states that BAL restrictions are refined by extending protections to `IntentSender`. It also states that developers must migrate away from the legacy `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` constant and adopt granular controls such as `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE`, which restricts activity starts to cases where the calling app is visible.

## Interpretation

この変更は、アプリが background から Activity を起動できる条件をより限定し、IntentSender 経由の起動も同じ安全設計に寄せる Activity launch security change である。

アプリ開発者にとって重要なのは、従来の broad opt-in である `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` に依存した設計が、Android 17 / targetSdkVersion 37 以降で互換性リスクになる可能性がある点である。代わりに、起動を許可する条件を明示する granular mode を選び、呼び出し元が visible な場合だけ Activity start を許可するなど、ユーザー文脈と合う起動に限定する必要がある。

---

# What Changed

公式文書上の変更点:
- Android 17 は Activity 起動まわりを secure-by-default architecture へ近づける。
- 目的は phishing、interaction hijacking、confused deputy attacks など high-severity exploits の緩和。
- Background Activity Launch restrictions が refined され、protections が IntentSender に拡張される。
- 開発者は legacy `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` constant から移行する必要がある。
- 推奨される移行先として、より細かい `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` などの granular controls が示されている。
- `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` は、calling app が visible な場合に activity start を制限することで attack surface を下げる、と説明されている。
- strict mode と updated lint checks を使い、legacy pattern と将来の target SDK requirement への準備状況を検出することが推奨されている。

AOSP で未確認の点:
- Android 16 baseline の BAL / IntentSender の扱い。
- Android 17 で IntentSender に追加された BAL protections の実装箇所。
- `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` の扱いが廃止、警告、無効化、または条件変更のどれに該当するか。
- `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` の exact gate と visible state 判定。
- targetSdkVersion 37 gate の実装箇所。
- strict mode signal と lint check の対象 pattern。
- Compat Change ID と default state。

## Applicability

公式文書の一次判断では、Android 17 以上、targetSdkVersion 37 以上、IntentSender / ActivityOptions を使って background activity launch を許可するアプリが主対象と考えられる。AOSP tag が未取得のため、確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

### OS Update Behavior

- Android 17 にアップデートしただけで適用されるか: Unknown
- targetSdkVersion に依存しない根拠: なし。公式ページは targetSdkVersion 37+ 向けだが、原文だけでは実装 gate を確認できない。
- Android 16 以前での挙動: 未確認。Android 17 tag との明示的な比較ができないため、Android 16 source だけから platform evidence として断定しない。

### targetSdkVersion 37 Behavior

- targetSdkVersion 37 以上で適用されるか: 公式ページ種別上は Yes と推定されるが、AOSP gate 未確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: Unknown。公式文書は Android 17 Behavior Changes として説明しているため、Android 17 platform behavior として扱う。
- opt-out / temporary override の有無: Unknown。granular opt-in mode は示されているが、compat force enable / disable や temporary override は未確認。

### Other Conditions

- device/form factor: 公式抜粋では条件なし。
- permission: 公式抜粋では permission 条件なし。Activity launch policy、process visibility、BAL permission / privilege、system exception が関係する可能性はあるが AOSP 未確認。
- API usage: `IntentSender`、`ActivityOptions`、background activity start、`MODE_BACKGROUND_ACTIVITY_START_ALLOWED`、`MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE`、strict mode、lint checks。
- manifest attribute: 公式抜粋では条件なし。
- component boundary: app process、IntentSender / PendingIntent sender、ActivityTaskManager / Activity launch policy、calling app visibility、system exceptions にまたがる。

---

# AOSP Investigation

## Checkout Status

Commands checked before evidence use:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list 'android-17*'
```

Result:
- `frameworks-base` working tree: clean at the time of investigation.
- From tag: `android-16.0.0_r4` exists.
- To tag: no local `android-17*` tag found.

Evidence limitation:
- Android 17 AOSP tag が local `frameworks-base` に存在しないため、`git -C frameworks-base diff android-16.0.0_r4 <android-17-tag> -- ...` による明示的な tag 比較を実行できない。
- Repository rule に従い、Android 17 working tree や推測による source evidence は採用しない。
- この制約により、AOSP-backed conclusion は High confidence にできない。

## Related Files

未確認。Android 17 AOSP tag 取得後に、少なくとも以下の候補を tag 比較で確認する必要がある。

- `core/java/android/app/ActivityOptions.java`
- `core/java/android/content/IntentSender.java`
- `core/java/android/app/PendingIntent.java`
- `services/core/java/com/android/server/wm/ActivityTaskManagerService.java`
- `services/core/java/com/android/server/wm/ActivityStartController.java`
- `services/core/java/com/android/server/wm/BackgroundActivityStartController.java`
- compat framework 定義ファイル内の BAL / IntentSender / ActivityOptions / targetSdkVersion 37 関連 Change ID

## Source Context Reviewed

Android 17 AOSP tag がないため、source context は未レビュー。

| File / symbol | Android 16 baseline | Android 17 behavior | Why this code path matters |
| --- | --- | --- | --- |
| Not reviewed | Not reviewed | Not reviewed | Android 17 tag がないため、公式文書の記述を AOSP diff で検証できない。 |

Required context:
- Entry point / caller: 未確認。想定される entry point は `IntentSender.sendIntent()`、`PendingIntent.send()`、`ActivityOptions` による BAL mode 指定、ActivityTaskManager の activity start 判定だが、AOSP evidence としては未採用。
- Relevant class or service responsibility: 未確認。
- Runtime path from app API / system event to changed code: 未確認。
- Why unrelated code paths were excluded: Android 17 tag 不在のため、source path の採否判断自体を保留。

## Diff Interpretation

| Observed diff | Interpretation | Behavior Change relevance | Confidence |
| --- | --- | --- | --- |
| No Android 17 tag diff available | Source diff type cannot be classified yet | 公式文書の BAL hardening、IntentSender protection extension、legacy mode migration、visible-only opt-in、targetSdkVersion gate を source diff で裏取りできていない | Low |

Required interpretation:
- Added behavior: 未確認。
- Removed behavior: 未確認。
- Changed condition / gate: 未確認。
- Changed default: 未確認。
- No behavior change found: 未確認。tag 不在のため「no behavior change」とは判断しない。

## Evidence

Facts:
- 公式 Behavior Change 文書は、Android 17 が Activity 起動まわりを secure-by-default architecture へ近づけると述べている。
- 公式文書は、phishing、interaction hijacking、confused deputy attacks のような high-severity exploits の緩和を目的としていると述べている。
- 公式文書は、BAL restrictions を refining し、protections を `IntentSender` に拡張すると述べている。
- 公式文書は、legacy `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` constant から移行する必要があると述べている。
- 公式文書は、`MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` のような granular controls を採用すべきと述べている。
- 公式文書は、strict mode と updated lint checks を使って legacy patterns と future target SDK requirements への readiness を確認するよう促している。
- local `frameworks-base` には `android-16.0.0_r4` tag がある。
- local `frameworks-base` には `android-17*` tag がない。
- 調査時点で `frameworks-base` working tree は clean。

Observations:
- 公式ページ種別は targetSdkVersion 37 以上向けである。
- この項目は targetSdkVersion 37 条件に加えて、IntentSender 経由の Activity 起動、ActivityOptions BAL mode、呼び出し元 visibility という runtime / API usage condition を含む。
- `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` は broad opt-in と読める一方、`MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` は visible state に限定するため、バックグラウンドからの予期しない画面起動を減らす方向の変更である。
- strict mode と lint は実行時互換性そのものではなく、移行検出・準備支援の位置づけと考えられる。
- AOSP tag がないため、実装が本当に targetSdkVersion 37 gate で制御されているかは未確認。
- Compat framework entry の有無も未確認。

Hypotheses:
- Android 17 / targetSdkVersion 37 以上では、IntentSender / PendingIntent 経由で Activity を起動する場合、従来の broad BAL opt-in ではなく visible state などのより限定的な条件が必要になる可能性が高い。
- Android 17 / targetSdkVersion 36 のアプリでは旧挙動が維持される可能性があるが、AOSP gate 未確認のため断定しない。
- lint / strict mode により、`MODE_BACKGROUND_ACTIVITY_START_ALLOWED` の利用や broad BAL opt-in が検出対象になる可能性があるが、具体的な check name と default behavior は未確認。

Conclusions:
- 現時点で顧客向けに確定できるのは、「公式文書上は Android 17 で BAL restrictions が IntentSender に拡張され、legacy `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` から `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` などへ移行する必要がある」という範囲まで。
- AOSP gate、IntentSender 適用範囲、ActivityOptions mode の実装差分、visible state 判定、compat framework default state が未確認のため、primary classification は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

## Applicability Gate Evidence

- targetSdkVersion gate: 未確認。公式ページ種別は targetSdkVersion 37 以上を示すが、AOSP gate evidence はない。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。Android 17 tag がないため検索未実施。
- @EnabledAfter / @EnabledSince / default state: 未確認。Android 17 tag がないため検索未実施。
- Build.VERSION / SDK_INT gate: 未確認。
- DeviceConfig / resources config: 未確認。
- Permission/AppOps gate: 未確認。BAL policy、system privilege、visibility state、PendingIntent sender / creator relationship が関係する可能性はあるが、AOSP evidence はない。
- Manifest/property gate: 未確認。
- No gate found: 未確認。Android 17 tag がないため「gate がない」とは判断しない。
- Gate conclusion: Unknown。公式ページ種別と原文から targetSdkVersion 37 + API usage conditions と推定されるが、AOSP で検証できていない。
- Reasoning from source context: source context 未レビューのため未確定。

---

# Impact Analysis

## Affected Apps

影響を受ける可能性があるアプリ:
- background から Activity を起動する設計を持つアプリ。
- `IntentSender` または `PendingIntent` 経由で画面起動を委譲するアプリ。
- `ActivityOptions.MODE_BACKGROUND_ACTIVITY_START_ALLOWED` に依存しているアプリ。
- 通知、着信、アラーム、認証、決済、デバイス連携、外部アプリ連携などで、ユーザーがアプリを直接見ていない状態から Activity 起動を試みるアプリ。
- targetSdkVersion 37 への更新を予定しており、BAL opt-in logic をまだ棚卸ししていないアプリ。

## Non-Affected Apps

影響が限定的または対象外と考えられるケース:
- background activity launch を行わないアプリ。
- Activity 起動が常に foreground / visible な user action から始まるアプリ。
- `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` を使っていないアプリ。
- IntentSender / PendingIntent で Activity 起動を委譲していないアプリ。
- Android 17 AOSP tag 取得後に対象外 gate や exemption が確認されたケース。

---

# Customer Impact

顧客説明用。

## Impact Level

- Human decision required

※ 仮評価。最終判断は人間が行う。

## Business Impact

- ユーザー影響: background からの画面起動が抑制されると、通知・認証・アラーム・連携フローで期待した画面が表示されない可能性がある。一方で、意図しない画面遷移や phishing 的な割り込みを減らす security benefit がある。
- 運用影響: targetSdkVersion 37 更新前に、BAL opt-in 利用箇所、IntentSender / PendingIntent 経由の画面起動、通知経由 UX を棚卸しする必要がある可能性がある。
- 開発影響: legacy `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` から granular BAL mode へ移行し、strict mode / lint の警告を解消する作業が必要になる可能性がある。

---

# Service Impact Examples（サービス影響例）

このセクションは、公式文書と AOSP evidence から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## Example 1（例1）: 通知 / 外部イベントから画面起動するアプリ

- 対象サービス例: チャット着信、決済承認、配車・配送通知、認証 prompt。
- 影響を受ける実装パターン: `IntentSender` / `PendingIntent` と broad BAL opt-in で background から Activity を起動する実装。
- 発生条件: Android 17 / targetSdkVersion 37 で BAL protections が IntentSender に拡張され、legacy mode が不十分になる場合。
- ユーザーに見える症状: 期待した画面が自動で開かない、通知 tap 後の遷移が変わる可能性。
- 開発・運用への影響: notification flow、PendingIntent sender / creator 責務、foreground visibility 条件の見直しが必要になる可能性。
- 推奨対応候補: `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` など granular controls へ移行する。
- 根拠: 公式 statement と report の missing AOSP evidence。
- Confidence（信頼度）: Low
- 注意: failure mode と compat toggle は未確認。

## Example 2（例2）: SDK が Activity 起動を委譲する連携機能

- 対象サービス例: OAuth / SSO SDK、決済 SDK、端末連携 SDK、広告 SDK。
- 影響を受ける実装パターン: host app と SDK / 外部 app の間で IntentSender による Activity 起動を委譲する実装。
- 発生条件: calling app visibility や BAL opt-in mode が新要件と合わない場合。
- ユーザーに見える症状: 認証画面や確認画面が表示されない、flow が途中で止まる可能性。
- 開発・運用への影響: SDK version 更新、integration guide 変更、strict mode / lint 対応が必要になる可能性。
- 推奨対応候補: Activity 起動を user-initiated / visible context に寄せ、legacy constant 利用を棚卸しする。
- 根拠: 公式 statement と report の action candidates。
- Confidence（信頼度）: Low
- 注意: 実サービス名を出す場合は owner 確認が必要。

---

# Required Actions

## Must

- `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` の利用箇所を検索し、なぜ background activity start が必要かをユースケースごとに確認する。
- `IntentSender` / `PendingIntent` 経由で Activity を起動する path を棚卸しする。
- Android 17 / targetSdkVersion 37 のテスト環境が利用可能になったら、background、foreground、visible、not visible の状態別に Activity 起動結果を確認する。
- Android 17 AOSP tag 入手後に、targetSdkVersion gate、compat Change ID、ActivityOptions mode の実装差分を再確認する。

## Recommended

- legacy broad opt-in を避け、`MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` など、ユーザーがアプリを見ている場合に限定する mode へ移行する。
- background から即時画面起動する設計を、通知、ユーザー操作、foreground-visible な文脈へ寄せる。
- strict mode と lint checks を CI / local build で有効化し、将来 target SDK requirement に抵触する pattern を早めに検出する。
- confused deputy 的な委譲が起きないよう、IntentSender / PendingIntent の creator / sender / caller の責務を整理する。

## Optional

- Activity 起動失敗時の fallback UX、ログ、メトリクスを整備する。
- security review の観点で、外部 Intent、PendingIntent mutability、task / back stack、notification trampoline 相当の設計も併せて確認する。

---

# Verification Method

## Matrix

| Device OS | targetSdkVersion | Compat flag | Expected behavior |
| --- | --- | --- | --- |
| Android 16 | 36 | default | Android 16 baseline。BAL / IntentSender の具体挙動は Android 17 tag 比較待ち。 |
| Android 17 | 36 | default | Unknown。この section は targetSdkVersion 37+ 向けだが、AOSP gate 未確認。 |
| Android 17 | 37 | default | 公式文書上は、IntentSender へ BAL protections が拡張され、legacy `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` から granular controls への移行が必要。 |
| Android 17 | 36 | force-enabled if available | Unknown。Compat Change ID 未確認。 |
| Android 17 | 37 | force-disabled if available | Unknown。Compat Change ID 未確認。 |

## Steps

- targetSdk変更: targetSdkVersion 36 と 37 の test build を用意する。
- compat framework command: 未確認。Android 17 compat framework entry / Change ID が判明後に記録する。
- テスト方法: `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` と `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` を使うケースを分け、IntentSender / PendingIntent 経由の Activity 起動を visible / background 状態で比較する。
- 再現手順: Android 17 device / emulator で対象アプリを install し、呼び出し元が visible な状態と background 状態の両方から Activity start を試す。strict mode / lint の検出結果も確認する。
- 期待結果: targetSdkVersion 37 のアプリでは、legacy broad opt-in への依存が問題になり、visible state などに限定した granular BAL mode への移行が必要になる。具体的な failure mode は AOSP tag と実機検証待ち。

---

# Conclusion

公式文書上、Android 17 は Activity 起動まわりの security hardening として BAL restrictions を IntentSender に拡張し、legacy `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` から `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` などの granular controls への移行を求めている。

ただし、Android 17 AOSP tag が local checkout にないため、実装 gate、IntentSender 適用範囲、compat framework の確認は未完了である。最終的な適用分類と顧客向け確定説明は、Android 17 AOSP tag 入手後に再調査が必要である。

---

# Human Decision Placeholder

Final Priority:
- Human decision required

Final Severity:
- Human decision required

Release Readiness:
- Human decision required

Customer Communication Priority:
- Human decision required

Decision:
- Further investigation required

Decision notes:
- Android 17 AOSP tag 入手後に、AOSP evidence と compat framework evidence を確認してから最終判断する。

---

# References

## Documentation

- https://developer.android.com/about/versions/17/behavior-changes-17
- https://developer.android.com/reference/android/content/IntentSender
- https://developer.android.com/reference/android/app/ActivityOptions#MODE_BACKGROUND_ACTIVITY_START_ALLOWED
- https://developer.android.com/reference/android/app/ActivityOptions#MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE

## AOSP

- Not available for Android 17 in local `frameworks-base`.
- From tag checked: `android-16.0.0_r4`
- To tag checked: no local `android-17*` tag found.

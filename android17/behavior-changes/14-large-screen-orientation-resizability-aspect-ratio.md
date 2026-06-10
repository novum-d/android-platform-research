# Platform API changes to ignore orientation, resizability and aspect ratio constraints on large screens (sw>=600dp)

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
- https://developer.android.com/about/versions/16/behavior-changes-16#ignore-orientation
- https://developer.android.com/about/versions/17/changes/ff-restrictions-ignored

Section:
Platform API changes to ignore orientation, resizability and aspect ratio constraints on large screens (sw>=600dp)

Page type:
- Apps targeting Android 17 or higher

### Classification Snapshot

Primary classification:
- UNKNOWN_NEEDS_MORE_EVIDENCE

Initial applicability assumption from official documentation:
- 公式文書は、Android 16 で targetSdkVersion 36 以上のアプリに対し、large screens (`sw >= 600dp`) で orientation、aspect ratio、resizability restrictions を無視する Platform API changes が導入されたと説明している。
- Android 16 / SDK 36 では developers が opt out できたが、Android 17 / API level 37 以上を target するアプリでは、この opt-out が利用できなくなると説明している。
- 追加条件として、large screen (`sw >= 600dp`)、orientation / resizability / aspect ratio constraints、Android 16 の opt-out mechanism、Android 17 targetSdkVersion 37 が関係する。
- ただし、local `frameworks-base` に Android 17 AOSP tag がないため、opt-out removal、targetSdkVersion 37 gate、large screen 判定、ActivityInfo / WindowManager / ActivityTaskManager の enforcement path、Compat Change ID、default state は未検証である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

At-a-glance impact:

| Question | Answer | Evidence |
| --- | --- | --- |
| Android 17 OS update only? | Unknown | Android 16 で targetSdkVersion 36+ 向けに導入済みだが、Android 17 の opt-out removal gate は AOSP 未確認。 |
| targetSdkVersion 37 required? | Likely, but unverified | 原文は opt-out が apps that target Android 17 / API level 37 or higher では利用不可と述べている。 |
| Additional runtime conditions? | Yes | large screens (`sw >= 600dp`) と orientation / resizability / aspect ratio constraints が関係する。 |
| Compat Change ID involved? | Unknown | Android 17 tag と compat framework evidence が未確認。 |

### Investigation Date

2026-06-11

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
- targetSdkVersion: 公式文書上は 37 以上で opt-out unavailable。Android 16 では 36 以上で opt-out 可能だったと説明されている。
- Device/form factor: large screens / `sw >= 600dp`。
- Permission/API/component condition: orientation request、resizability restriction、aspect ratio constraint、Android 16 opt-out mechanism。
- App state/process condition: Activity launch / configuration / windowing mode / display size evaluation 時点。

Compat framework:
- Change ID: Unknown
- Change name: Unknown
- Default state: Unknown
- Toggleable for testing: Unknown

Classification confidence:
- Low

Classification evidence:
- Official documentation page: `behavior-changes-17`
- Original applicability statement: Android 16 introduced ignoring orientation / aspect ratio / resizability restrictions on large screens for API 36+ with opt-out; Android 17 / API 37+ removes that opt-out.
- AOSP targetSdk gate: 未確認。local `frameworks-base` に `android-17*` tag がない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# Executive Summary

Android 16 では、targetSdkVersion 36 以上のアプリについて、large screens (`sw >= 600dp`) で orientation、aspect ratio、resizability の制約を platform が無視する変更が導入された、と公式文書は説明している。Android 16 では opt-out が可能だったが、Android 17 / targetSdkVersion 37 以上ではその opt-out が利用できなくなる。

この変更により、タブレット、折りたたみ端末、デスクトップサイズのウィンドウなどで、アプリが portrait 固定、non-resizable、固定 aspect ratio を指定していても、platform がより大きな画面に適した表示・リサイズを優先する可能性がある。既存 UI が固定向き・固定比率を前提としている場合は、large screen 対応の確認が必要である。

ただし、現時点の local `frameworks-base` には Android 17 AOSP tag がないため、opt-out removal の実装差分、targetSdkVersion gate、large screen 判定、Compat Change ID は未確認である。

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
- Platform API changes to ignore orientation, resizability and aspect ratio constraints on large screens (sw>=600dp)

Original statement being verified:

> We introduced Platform API changes in Android 16 to ignore orientation, aspect ratio, and resizability restrictions on large screens (sw >= 600dp) for apps targeting API level 36 or higher.

The supplied official text also states that developers had the option to opt out of these changes with SDK 36, but this opt-out is no longer available for apps that target Android 17 / API level 37 or higher.

## Interpretation

この変更は、large screen でアプリの orientation / resizability / aspect ratio 制約よりも platform の画面適応を優先する large-screen compatibility behavior change である。Android 17 では、Android 16 で許されていた SDK 36 向け opt-out が targetSdkVersion 37 以上では使えなくなる点が中心である。

アプリ開発者にとって重要なのは、targetSdkVersion 37 へ更新すると、large screen 上で portrait 固定、resize 不可、最大 / 最小 aspect ratio などの制約に依存したレイアウト保護が効かなくなる可能性がある点である。UI は `sw >= 600dp` を含む large screen / multi-window / foldable / desktop windowing を前提に検証する必要がある。

---

# What Changed

公式文書上の変更点:
- Android 16 で、large screens (`sw >= 600dp`) において orientation、aspect ratio、resizability restrictions を無視する Platform API changes が導入された。
- Android 16 の対象は API level 36 以上を target するアプリ。
- SDK 36 では developers が opt out できた。
- Android 17 / API level 37 以上を target するアプリでは、この opt-out が利用できなくなる。
- 詳細は Android 16 の behavior change と Android 17 の `Restrictions on orientation and resizability are ignored` 関連ページに誘導されている。

AOSP で未確認の点:
- Android 16 baseline で orientation / aspect ratio / resizability restrictions を無視する実装と opt-out mechanism。
- Android 17 で targetSdkVersion 37 以上の opt-out を無効化する実装箇所。
- `sw >= 600dp` 判定の exact condition。
- Activity requested orientation、`resizeableActivity`、min / max aspect ratio、letterbox / compatibility mode、multi-window mode の扱い。
- Android 16 opt-out property / manifest / compat framework と Android 17 removal の関係。
- Compat Change ID と default state。

## Applicability

公式文書の一次判断では、Android 17 以上、targetSdkVersion 37 以上、large screens (`sw >= 600dp`) で orientation / resizability / aspect ratio constraints を指定しているアプリに適用される。Android 16 / targetSdkVersion 36 で存在した opt-out が Android 17 / targetSdkVersion 37 では使えないという変更である。AOSP tag が未取得のため、確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

### OS Update Behavior

- Android 17 にアップデートしただけで適用されるか: Unknown
- targetSdkVersion に依存しない根拠: なし。原文は Android 17 / API level 37 以上を target するアプリで opt-out unavailable と述べている。
- Android 16 以前での挙動: 公式文書は Android 16 / API level 36+ で制約無視が導入され、SDK 36 では opt-out 可能だったと述べている。AOSP tag 比較は未実施。

### targetSdkVersion 37 Behavior

- targetSdkVersion 37 以上で適用されるか: 公式文書上は Yes と読めるが、AOSP gate 未確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: Unknown。公式文書は Android 17 Behavior Changes として説明しているため、Android 17 platform behavior として扱う。
- opt-out / temporary override の有無: 公式文書上、SDK 36 の opt-out は Android 17 / targetSdkVersion 37 以上では利用不可。AOSP による具体的 opt-out 名、manifest property、compat toggle は未確認。

### Other Conditions

- device/form factor: large screens / `sw >= 600dp`。tablet、foldable inner display、desktop / freeform windowing、large screen emulator などが関係する可能性。
- permission: 公式抜粋では条件なし。
- API usage: requested orientation、resizability、aspect ratio constraints、Activity manifest attributes、WindowManager / ActivityTaskManager behavior。
- manifest attribute: `screenOrientation`、`resizeableActivity`、`minAspectRatio` / `maxAspectRatio`、Android 16 opt-out property が関係する可能性。
- component boundary: Activity launch、task / windowing mode、display metrics、configuration changes、letterbox / compatibility handling にまたがる。

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

- `core/java/android/content/pm/ActivityInfo.java`
- `core/java/android/R.styleable` / manifest attribute definitions
- `services/core/java/com/android/server/wm/ActivityRecord.java`
- `services/core/java/com/android/server/wm/ActivityTaskManagerService.java`
- `services/core/java/com/android/server/wm/DisplayContent.java`
- `services/core/java/com/android/server/wm/LetterboxUiController.java`
- `services/core/java/com/android/server/wm/SizeCompatPolicy.java`
- `services/core/java/com/android/server/wm/AspectRatioPolicy.java`
- compat framework 定義ファイル内の orientation / resizability / aspect ratio / large screen / targetSdkVersion 37 関連 Change ID

## Source Context Reviewed

Android 17 AOSP tag がないため、source context は未レビュー。

| File / symbol | Android 16 baseline | Android 17 behavior | Why this code path matters |
| --- | --- | --- | --- |
| Not reviewed | Not reviewed | Not reviewed | Android 17 tag がないため、公式文書の記述を AOSP diff で検証できない。 |

Required context:
- Entry point / caller: 未確認。想定される entry point は Activity launch、manifest parsing、requested orientation evaluation、resizeability / aspect ratio policy、large screen display metrics 判定だが、AOSP evidence としては未採用。
- Relevant class or service responsibility: 未確認。
- Runtime path from app API / system event to changed code: 未確認。
- Why unrelated code paths were excluded: Android 17 tag 不在のため、source path の採否判断自体を保留。

## Diff Interpretation

| Observed diff | Interpretation | Behavior Change relevance | Confidence |
| --- | --- | --- | --- |
| No Android 17 tag diff available | Source diff type cannot be classified yet | 公式文書の Android 16 behavior、SDK 36 opt-out、Android 17 / targetSdkVersion 37 opt-out removal、large screen condition を source diff で裏取りできていない | Low |

Required interpretation:
- Added behavior: 未確認。
- Removed behavior: 未確認。公式文書上は Android 16 の opt-out が Android 17 / targetSdkVersion 37 以上では removed / unavailable になる可能性がある。
- Changed condition / gate: 未確認。targetSdkVersion 37 と `sw >= 600dp` gate がある可能性は高いが、AOSP 未確認。
- Changed default: 未確認。
- No behavior change found: 未確認。tag 不在のため「no behavior change」とは判断しない。

## Evidence

Facts:
- 公式 Behavior Change 文書は、Android 16 で API level 36 以上を target するアプリに対し、large screens (`sw >= 600dp`) で orientation、aspect ratio、resizability restrictions を無視する Platform API changes が導入されたと述べている。
- 公式文書は、SDK 36 では developers が opt out できたと述べている。
- 公式文書は、Android 17 / API level 37 以上を target するアプリでは、この opt-out が no longer available と述べている。
- local `frameworks-base` には `android-16.0.0_r4` tag がある。
- local `frameworks-base` には `android-17*` tag がない。
- 調査時点で `frameworks-base` working tree は clean。

Observations:
- 公式ページ種別は targetSdkVersion 37 以上向けである。
- この項目は targetSdkVersion 37 条件に加えて、large screen (`sw >= 600dp`) という device/form factor condition を含む。
- Android 16 ですでに制約無視が導入されており、Android 17 の主な変更は SDK 36 で使えた opt-out の終了である。
- fixed orientation / fixed aspect ratio / non-resizable 前提の UI は、targetSdkVersion 37 で large screen 上の表示崩れや予期しない configuration change に遭遇する可能性がある。
- AOSP tag がないため、実装が本当に targetSdkVersion 37 gate で制御されているかは未確認。
- Compat framework entry の有無も未確認。

Hypotheses:
- Android 17 / targetSdkVersion 37 以上では、Android 16 の opt-out manifest property または compat override を指定しても large screen 上で orientation / resizability / aspect ratio restrictions が無視される可能性が高い。
- Android 17 / targetSdkVersion 36 のアプリでは Android 16 と同様に opt-out が有効な可能性があるが、AOSP gate 未確認のため断定しない。
- `sw >= 600dp` の判定は display / window metrics / smallest width configuration に依存する可能性があるが、exact condition は未確認である。

Conclusions:
- 現時点で顧客向けに確定できるのは、「公式文書上は Android 17 / targetSdkVersion 37 以上のアプリでは、large screen で orientation / resizability / aspect ratio restrictions を無視する Android 16 変更への opt-out が利用できなくなる」という範囲まで。
- AOSP gate、large screen 判定、opt-out mechanism、compat framework default state が未確認のため、primary classification は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

## Applicability Gate Evidence

- targetSdkVersion gate: 未確認。公式文書は targetSdkVersion 37 以上を示すが、AOSP gate evidence はない。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。Android 17 tag がないため検索未実施。
- @EnabledAfter / @EnabledSince / default state: 未確認。Android 17 tag がないため検索未実施。
- Build.VERSION / SDK_INT gate: 未確認。
- DeviceConfig / resources config: 未確認。`sw >= 600dp` condition は公式文書上の device condition だが、AOSP 判定箇所は未確認。
- Permission/AppOps gate: 公式抜粋では条件なし。
- Manifest/property gate: 未確認。Android 16 opt-out mechanism と Android 17 removal の具体的 manifest / property 名は AOSP 未確認。
- No gate found: 未確認。Android 17 tag がないため「gate がない」とは判断しない。
- Gate conclusion: Unknown。公式文書の wording から targetSdkVersion 37 + large screen condition と推定されるが、AOSP で検証できていない。
- Reasoning from source context: source context 未レビューのため未確定。

---

# Impact Analysis

## Affected Apps

影響を受ける可能性があるアプリ:
- targetSdkVersion 37 へ更新し、large screens (`sw >= 600dp`) で動作するアプリ。
- `screenOrientation` で portrait / landscape 固定を前提にしているアプリ。
- `resizeableActivity=false` または固定 window size / non-resizable 前提の設計を持つアプリ。
- `minAspectRatio` / `maxAspectRatio` や固定 aspect ratio に依存するアプリ。
- Android 16 / SDK 36 で opt-out を利用して large screen 制約無視を回避していたアプリ。
- tablet、foldable、desktop windowing、ChromeOS など large screen 展開があるアプリ。

## Non-Affected Apps

影響が限定的または対象外と考えられるケース:
- large screen (`sw >= 600dp`) で利用されないアプリ。
- すでに orientation / resizability / aspect ratio constraints に依存せず adaptive UI を実装しているアプリ。
- Android 16 / targetSdkVersion 36 で opt-out を使っておらず、large screen で検証済みのアプリ。
- Android 17 AOSP tag 取得後に対象外 gate や exemption が確認されたケース。

---

# Customer Impact

顧客説明用。

## Impact Level

- Human decision required

※ 仮評価。最終判断は人間が行う。

## Business Impact

- ユーザー影響: large screen 上で固定向き / 固定比率前提の UI が広がる、回転する、リサイズされる、letterbox されないなどにより、表示崩れや操作不能が起きる可能性がある。
- 運用影響: tablet / foldable / desktop windowing の QA matrix、Android 16 opt-out 利用状況、targetSdkVersion 37 移行計画を確認する必要がある可能性がある。
- 開発影響: adaptive layout、multi-window、configuration change、responsive resource、Jetpack WindowManager / Compose adaptive UI などの対応が必要になる可能性がある。

---

# Service Impact Examples（サービス影響例）

このセクションは、公式文書と AOSP evidence から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## Example 1（例1）: Portrait 固定のスマートフォン前提 UI

- 対象サービス例: 決済、本人確認、縦長 feed、camera / scanner UI。
- 影響を受ける実装パターン: `screenOrientation="portrait"`、固定 aspect ratio、non-resizable 前提の Activity。
- 発生条件: Android 17 / targetSdkVersion 37、`sw >= 600dp` large screen で Android 16 opt-out が使えない場合。
- ユーザーに見える症状: tablet / foldable で横向きや大きな window に広がり、UI が崩れる可能性。
- 開発・運用への影響: large screen QA、adaptive layout、configuration change handling の見直しが必要になる可能性。
- 推奨対応候補: fixed orientation 前提を減らし、responsive layout と state restoration を整備する。
- 根拠: 公式 statement と report の expected behavior。
- Confidence（信頼度）: Low
- 注意: exact opt-out mechanism と large screen 判定は AOSP tag 待ち。

## Example 2（例2）: Tablet / foldable で non-resizable を指定する業務アプリ

- 対象サービス例: POS、医療業務、教育、店舗管理、在庫管理。
- 影響を受ける実装パターン: `resizeableActivity=false` や固定 window size 前提で画面密度・サイズを決め打ちする UI。
- 発生条件: targetSdkVersion 37 で large screen 制約無視が opt-out できない場合。
- ユーザーに見える症状: split-screen / freeform resize でボタン重なり、入力欄切れ、操作不能が起きる可能性。
- 開発・運用への影響: multi-window、fold / unfold、external display の test matrix 更新が必要になる可能性。
- 推奨対応候補: window size に応じた layout 分岐、scrollable content、minimum touch target を整備する。
- 根拠: 公式 statement と report の action candidates。
- Confidence（信頼度）: Low
- 注意: 実サービスでの発生確認ではない。

---

# Required Actions

## Must

- Android 16 の opt-out mechanism を利用しているか確認する。
- `screenOrientation`、`resizeableActivity`、`minAspectRatio`、`maxAspectRatio` など large screen 制約に関わる manifest / API usage を棚卸しする。
- `sw >= 600dp` 相当の tablet / foldable / desktop windowing 環境で、targetSdkVersion 37 build を検証する。
- orientation change、multi-window resize、split-screen、fold / unfold、freeform resize で UI が崩れないか確認する。
- Android 17 AOSP tag 入手後に、targetSdkVersion gate、opt-out removal、compat Change ID を再確認する。

## Recommended

- fixed orientation / fixed aspect ratio 前提を減らし、layout を adaptive / responsive にする。
- state restoration と configuration change handling を確認し、回転やリサイズで入力中データが失われないようにする。
- large screen 用 resource、navigation layout、two-pane / supporting pane、window size class 相当の layout 分岐を整備する。
- Android 16 の関連 behavior change と Android 17 の opt-out removal を分けて、既存 opt-out 依存のリスクを管理する。

## Optional

- foldable posture、external display、ChromeOS / desktop mode など、`sw >= 600dp` 以外の large screen 実利用条件もテストする。
- UI screenshot / automated layout test を追加し、targetSdkVersion 37 移行時の表示崩れを検出する。

---

# Verification Method

## Matrix

| Device OS | targetSdkVersion | Compat flag | Expected behavior |
| --- | --- | --- | --- |
| Android 16 | 36 | default / opt-out if configured | 公式文書上、large screen 制約無視は導入済みだが SDK 36 では opt-out 可能。 |
| Android 17 | 36 | default / opt-out if available | Unknown。SDK 36 opt-out が維持されるかは AOSP gate 未確認。 |
| Android 17 | 37 | default | 公式文書上、SDK 36 で利用できた opt-out は利用不可。large screen で orientation / aspect ratio / resizability restrictions が無視される。 |
| Android 17 | 36 | force-enabled if available | Unknown。Compat Change ID 未確認。 |
| Android 17 | 37 | force-disabled if available | Unknown。Compat Change ID 未確認。 |

## Steps

- targetSdk変更: targetSdkVersion 36 と 37 の test build を用意する。
- compat framework command: 未確認。Android 17 compat framework entry / Change ID が判明後に記録する。
- テスト方法: `sw >= 600dp` の emulator / tablet / foldable で、orientation fixed / resizable false / fixed aspect ratio の Activity を起動し、Android 16 opt-out あり / なし、targetSdkVersion 36 / 37 を比較する。
- 再現手順: Android 17 device / emulator で対象アプリを install し、portrait / landscape、split-screen、freeform resize、fold / unfold を実施する。requested orientation、actual orientation、window bounds、configuration changes、layout breakage を記録する。
- 期待結果: targetSdkVersion 37 のアプリでは、Android 16 で使えた opt-out が効かず、large screen 上で orientation / aspect ratio / resizability restrictions が platform により無視される。具体的な opt-out failure mode は AOSP tag と実機検証待ち。

---

# Conclusion

公式文書上、Android 17 / targetSdkVersion 37 以上のアプリでは、Android 16 で導入された large screen 上の orientation / resizability / aspect ratio constraints 無視に対する SDK 36 opt-out が利用できなくなる。large screen で固定向き・固定比率・非リサイズ前提の UI を持つアプリは、targetSdkVersion 37 移行前に adaptive UI と configuration change 対応を確認する必要がある。

ただし、Android 17 AOSP tag が local checkout にないため、実装 gate、opt-out removal、large screen 判定、compat framework の確認は未完了である。最終的な適用分類と顧客向け確定説明は、Android 17 AOSP tag 入手後に再調査が必要である。

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
- https://developer.android.com/about/versions/16/behavior-changes-16#ignore-orientation
- https://developer.android.com/about/versions/17/changes/ff-restrictions-ignored

## AOSP

- Not available for Android 17 in local `frameworks-base`.
- From tag checked: `android-16.0.0_r4`
- To tag checked: no local `android-17*` tag found.

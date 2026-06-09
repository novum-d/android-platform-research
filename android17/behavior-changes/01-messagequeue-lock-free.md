# New lock-free implementation of MessageQueue

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
- https://developer.android.com/about/versions/17/changes/messagequeue
- https://developer.android.com/reference/android/os/MessageQueue

Section:
New lock-free implementation of MessageQueue

Page type:
- Apps targeting Android 17 or higher

### Classification Snapshot

Primary classification:
- UNKNOWN_NEEDS_MORE_EVIDENCE

Initial applicability assumption from official documentation:
- targetSdkVersion 37 以上のアプリに適用される変更として扱うのが自然。
- ただし、Android 17 AOSP tag が local `frameworks-base` に存在しないため、AOSP gate、Compat Change ID、default state を検証できていない。

At-a-glance impact:

| Question | Answer | Evidence |
| --- | --- | --- |
| Android 17 OS update only? | Unknown | 公式文書は「apps targeting Android 17 (API level 37) or higher」と述べるが、AOSP gate 未確認。 |
| targetSdkVersion 37 required? | Likely, but unverified | 公式文書ページ種別と原文は targetSdkVersion 37+ を示す。AOSP evidence は未取得。 |
| Additional runtime conditions? | Unknown | 公式抜粋からは追加条件は確認できない。詳細 guidance と AOSP tag 確認が必要。 |
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
- Android version: Android 17 であることが前提。ただし AOSP tag 未取得。
- targetSdkVersion: 公式文書上は 37 以上が条件と読める。AOSP gate 未確認。
- Device/form factor: 不明。
- Permission/API/component condition: `android.os.MessageQueue` の private field / private method へ reflection している場合に互換性リスクがあると公式文書が述べる。
- App state/process condition: 不明。

Compat framework:
- Change ID: Unknown
- Change name: Unknown
- Default state: Unknown
- Toggleable for testing: Unknown

Classification confidence:
- Low

Classification evidence:
- Official documentation page: `behavior-changes-17`
- Original applicability statement: "apps targeting Android 17 (API level 37) or higher receive..."
- AOSP targetSdk gate: 未確認。local `frameworks-base` に `android-17*` tag がない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# Executive Summary

Android 17 では、targetSdkVersion 37 以上のアプリに対して `android.os.MessageQueue` の新しい lock-free 実装が適用される、と公式 Behavior Change 文書は説明している。性能改善と missed frame 削減が目的だが、`MessageQueue` の private field / private method を reflection で参照しているアプリやライブラリは壊れる可能性がある。

ただし、現時点の local `frameworks-base` には Android 17 AOSP tag がないため、AOSP 上の targetSdkVersion gate、Compat Change ID、default state は未確認である。顧客向けの最終分類には、Android 17 AOSP tag 公開後の再調査が必要。

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
- New lock-free implementation of MessageQueue

Original statement being verified:

> apps targeting Android 17 (API level 37) or higher receive a new lock-free implementation

The same section states that the new `android.os.MessageQueue` implementation is intended to improve performance and reduce missed frames, and that clients reflecting on `MessageQueue` private fields or methods may break. It points readers to the MessageQueue behavior change guidance for mitigation strategies.

## Interpretation

公式文書は、この変更を「Android 17 以上を targetSdkVersion として指定するアプリ向けの Behavior Change」として掲載している。原文も `apps targeting Android 17 (API level 37) or higher` と述べているため、一次分類は targetSdkVersion 37 以上で有効になる変更と考えられる。

互換性リスクは、通常の public API 利用ではなく、`MessageQueue` の private field / private method に reflection しているコードに集中する。該当する可能性があるのは、独自のメインスレッド監視、フレーム落ち検知、メッセージキュー計測、古い互換性回避コード、またはそれらを含むサードパーティ SDK である。

---

# What Changed

公式文書上の変更点:
- Android 17 で `android.os.MessageQueue` に新しい lock-free 実装が導入される。
- 新実装は性能改善と missed frame 削減を目的としている。
- `MessageQueue` の private field / private method を reflection する client は壊れる可能性がある。

AOSP で未確認の点:
- Android 16 baseline 実装から Android 17 実装への具体的な source diff。
- lock-free 実装の導入箇所、entry point、caller。
- targetSdkVersion 37 gate の実装箇所。
- Compat Change ID と default state。
- opt-out または temporary override の有無。

## Applicability

この変更の適用条件は、現時点では公式文書からの一次判断に留まる。AOSP tag が未取得のため、確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

### OS Update Behavior

- Android 17 にアップデートしただけで適用されるか: Unknown
- targetSdkVersion に依存しない根拠: なし。公式文書は targetSdkVersion 37 以上を示す。
- Android 16 以前での挙動: AOSP tag 比較未実施。Android 16 baseline source は Android 17 tag との比較ができないため、この調査では platform evidence として採用していない。

### targetSdkVersion 37 Behavior

- targetSdkVersion 37 以上で適用されるか: 公式文書上は Yes と読めるが、AOSP gate 未確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: Unknown。公式抜粋は「Beginning with Android 17」と述べるため、少なくとも Android 17 platform behavior として扱う。
- opt-out / temporary override の有無: Unknown。compat framework evidence 未確認。

### Other Conditions

- device/form factor: 公式抜粋では条件なし。
- permission: 公式抜粋では条件なし。
- API usage: `MessageQueue` private field / private method への reflection が互換性リスク条件。
- manifest attribute: Unknown。
- component boundary: アプリプロセス内の `MessageQueue` 利用が対象と考えられるが、AOSP 未確認。

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

- `core/java/android/os/MessageQueue.java`
- `core/java/android/os/Looper.java`
- `core/java/android/os/Handler.java`
- native peer が存在する場合の `android_os_MessageQueue` 関連実装
- compat framework 定義ファイル内の `MessageQueue` / lock-free / targetSdkVersion 37 関連 Change ID

## Source Context Reviewed

Android 17 AOSP tag がないため、source context は未レビュー。

| File / symbol | Android 16 baseline | Android 17 behavior | Why this code path matters |
| --- | --- | --- | --- |
| Not reviewed | Not reviewed | Not reviewed | Android 17 tag がないため、公式文書の記述を AOSP diff で検証できない。 |

Required context:
- Entry point / caller: 未確認。
- Relevant class or service responsibility: `MessageQueue` が app thread の message dispatch queue として関連することは API 名から推定できるが、本調査では AOSP evidence として採用しない。
- Runtime path from app API / system event to changed code: 未確認。
- Why unrelated code paths were excluded: Android 17 tag 不在のため、source path の採否判断自体を保留。

## Diff Interpretation

| Observed diff | Interpretation | Behavior Change relevance | Confidence |
| --- | --- | --- | --- |
| No Android 17 tag diff available | Source diff type cannot be classified yet | 公式文書の lock-free 実装導入を source diff で裏取りできていない | Low |

Required interpretation:
- Added behavior: 未確認。
- Removed behavior: 未確認。
- Changed condition / gate: 未確認。
- Changed default: 未確認。
- No behavior change found: 未確認。tag 不在のため「no behavior change」とは判断しない。

## Evidence

Facts:
- 公式 Behavior Change 文書は、Android 17 から targetSdkVersion 37 以上のアプリが新しい lock-free `MessageQueue` 実装を受け取ると述べている。
- 公式文書は、新実装が性能改善と missed frame 削減を目的とすると述べている。
- 公式文書は、`MessageQueue` の private field / private method に reflection する client が壊れる可能性を述べている。
- local `frameworks-base` には `android-16.0.0_r4` tag がある。
- local `frameworks-base` には `android-17*` tag がない。
- 調査時点で `frameworks-base` working tree は clean。

Observations:
- 公式ページ種別と原文は targetSdkVersion 37 以上の変更を示している。
- AOSP tag がないため、実装が本当に targetSdkVersion 37 gate で制御されているかは未確認。
- Compat framework entry の有無も未確認。

Hypotheses:
- Android 17 上で targetSdkVersion 37 以上のアプリにのみ新実装が有効化され、targetSdkVersion 36 のアプリには旧挙動が維持される可能性がある。
- private API reflection をしていない通常の `Handler` / `Looper` 利用アプリでは、互換性破壊より性能面の影響が中心になる可能性がある。

Conclusions:
- 現時点で顧客向けに確定できるのは、「公式文書上は targetSdkVersion 37 以上で注意すべき MessageQueue 実装変更がある」という範囲まで。
- AOSP gate と compat framework default state が未確認のため、適用分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

## Applicability Gate Evidence

- targetSdkVersion gate: 未確認。Android 17 AOSP tag がないため、`targetSdkVersion` / `ApplicationInfo.targetSdkVersion` 検索は実施していない。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。Android 17 AOSP tag がないため、`CompatChanges.isChangeEnabled` / `@ChangeId` / `@EnabledAfter` / `@EnabledSince` 検索は実施していない。
- @EnabledAfter / @EnabledSince / default state: 未確認。
- Build.VERSION / SDK_INT gate: 未確認。
- DeviceConfig / resources config: 未確認。
- Permission/AppOps gate: 未確認。
- Manifest/property gate: 未確認。
- No gate found: 未判断。検索不能のため「gate なし」とは扱わない。
- Gate conclusion: Unknown。公式文書上の targetSdkVersion 37 条件はあるが、AOSP evidence が不足している。
- Reasoning from source context: source context 未取得のため不可。

Searched:
- `frameworks-base` checkout status。
- `android-16.0.0_r4` tag の存在。
- `android-17*` tag の存在。

Not searched yet:
- Android 17 implementation files。
- Android 17 compat framework definitions。
- MessageQueue guidance page の詳細な mitigation strategy。

Reason:
- Android 17 target tag が local checkout に存在しないため、tag 間 diff による platform evidence が作れない。

---

# Impact Analysis

## Affected Apps

影響を受ける可能性があるアプリ:
- targetSdkVersion 37 以上への更新を予定しているアプリ。
- `android.os.MessageQueue` の private field / private method を reflection で参照しているアプリ。
- メインスレッド監視、ANR 監視、フレーム落ち検知、message queue 計測などのために private implementation detail に依存しているアプリまたは SDK。
- 古い performance monitoring SDK、diagnostics SDK、hooking / instrumentation 系 SDK を組み込んでいるアプリ。

## Non-Affected Apps

影響が限定的と考えられるケース:
- `Handler`、`Looper`、`MessageQueue` の public API のみを使っているアプリ。
- `MessageQueue` の private field / private method に reflection していないアプリ。
- targetSdkVersion 37 へ上げないアプリ。ただし、これは公式文書からの一次判断であり、AOSP gate 未確認。

---

# Customer Impact

## Impact Level

- Human decision required

※ 最終 severity / priority は人間が判断する。このレポートでは確定しない。

## Business Impact

- ユーザー影響: private API reflection が壊れる場合、起動時 crash、監視機能の停止、UI thread 計測の不整合が発生する可能性がある。
- 運用影響: サードパーティ SDK が原因の場合、アプリ側では直接コードが見えにくく、SDK 更新や vendor 確認が必要になる可能性がある。
- 開発影響: targetSdkVersion 37 更新前に reflection usage の棚卸しと Android 17 テストが必要。

---

# Required Actions

## Must

- `android.os.MessageQueue` の private field / private method へ reflection している自社コードがないか確認する。
- サードパーティ SDK に `MessageQueue` reflection、main thread hook、message queue instrumentation が含まれていないか確認する。
- targetSdkVersion 37 更新前に Android 17 device / emulator で起動、画面遷移、メインスレッド監視、performance monitoring をテストする。

## Recommended

- private implementation detail への依存を public API ベースの実装に置き換える。
- Android 17 の MessageQueue behavior change guidance を確認し、公式 mitigation strategy に沿って修正する。
- performance monitoring / diagnostics SDK を Android 17 対応版に更新する。
- reflection failure を crash ではなく機能無効化として扱えるように defensive coding を入れる。

## Optional

- Android 17 AOSP tag 公開後、`MessageQueue` 関連 diff と compat Change ID を再調査する。
- UI jank / frame metrics の before / after を測定し、性能面の副作用がないか確認する。

---

# Verification Method

## Matrix

| Device OS | targetSdkVersion | Compat flag | Expected behavior |
| --- | --- | --- | --- |
| Android 16 | 36 | default | Android 16 baseline。lock-free implementation の Android 17 変更は適用されない想定。ただし本調査では AOSP baseline 未比較。 |
| Android 17 | 36 | default | Unknown。公式文書上は targetSdkVersion 37 以上向けのため旧挙動維持が期待されるが、AOSP gate 未確認。 |
| Android 17 | 37 | default | 公式文書上は新しい lock-free `MessageQueue` 実装が適用される。private reflection client は破損リスクあり。 |
| Android 17 | 36 | force-enabled if available | Unknown。Compat Change ID 未確認。 |
| Android 17 | 37 | force-disabled if available | Unknown。Compat Change ID 未確認。 |

## Steps

- targetSdk変更: test app を targetSdkVersion 36 と 37 で build し、Android 17 上の挙動差を確認する。
- compat framework command: Change ID 未確認のため未定。Android 17 tag / compat page 確認後に追加する。
- テスト方法: `MessageQueue` private reflection を行う最小再現コードと、public API のみを使う control app を比較する。
- 再現手順: Android 17 上で targetSdkVersion 36 / 37 の両 APK を実行し、reflection 成否、crash、main thread monitoring の結果を比較する。
- 期待結果: targetSdkVersion 37 で新実装により private field / method の reflection 前提が崩れる可能性がある。targetSdkVersion 36 の結果は AOSP gate 確認待ち。

---

# Conclusion

公式文書は、Android 17 で targetSdkVersion 37 以上のアプリに新しい lock-free `android.os.MessageQueue` 実装が適用されると説明している。主な互換性リスクは、`MessageQueue` private field / private method への reflection に依存するコードである。

一方で、local `frameworks-base` に Android 17 AOSP tag がないため、実装差分、targetSdkVersion gate、Compat Change ID、default state を検証できていない。現時点の primary classification は `UNKNOWN_NEEDS_MORE_EVIDENCE`、confidence は Low とする。

Human decision placeholder:
- Final priority: Human decision required
- Final severity: Human decision required
- Release readiness: Human decision required
- Customer communication priority: Human decision required
- Next required human decision: Android 17 AOSP tag 公開後に再調査するか、公式 documentation ベースの暫定注意喚起として扱うかを判断する。

# Background audio hardening

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP tag

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

### Behavior Change 文書（Behavior Change Source）

Document:
https://developer.android.com/about/versions/17/behavior-changes-17

Related documents:
- https://developer.android.com/develop/background-work/services/alarms#exact
- https://developer.android.com/reference/android/media/AudioAttributes#USAGE_ALARM
- https://developer.android.com/about/versions/17/changes/bg-audio

Section:
Background audio hardening

Page type:
- Apps targeting Android 17 or higher

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- 公式文書は、Android 17 以降、audio playback、audio focus requests、volume change APIs などの background audio interactions に制限を適用し、ユーザーが意図して開始した変更であることを保証すると説明している。
- 一部の audio restrictions は all apps に適用される一方、targetSdkVersion 37 以上のアプリではより厳格になると説明している。
- targetSdkVersion 37 以上のアプリが background で audio と interaction する場合、foreground service が running である必要があり、さらに foreground service が while-in-use (WIU) capabilities を持つか、exact alarm permission を持ち `USAGE_ALARM` audio streams と interaction している必要がある。
- ただし、local `frameworks-base` に Android 17 AOSP tag がないため、audio framework の enforcement path、all apps 制限と targetSdkVersion 37 制限の分岐、foreground service / WIU / exact alarm / `USAGE_ALARM` gate、Compat Change ID、default state は未検証である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | Conditional / Unknown | 公式文書は一部制限が all apps に適用されると述べるが、詳細と AOSP gate は未確認。 |
| targetSdkVersion 37 以上が必要か | Partially, but unverified | 原文は targetSdkVersion 37 以上では restrictions are more stringent と述べている。 |
| 追加の実行時条件があるか | Yes | background audio interaction、foreground service running、WIU capabilities、exact alarm permission、`USAGE_ALARM`。 |
| Compat Change ID が関係するか | Unknown | Android 17 tag と compat framework evidence が未確認。 |

### 調査日（Investigation Date）

2026-06-11

### 信頼度（Confidence）

- Low

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] OS update / all apps on Android 17 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 37 on Android 17+
- [ ] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [x] Unknown / needs more evidence

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 以上が前提と考えられるが、AOSP tag 未取得。
- targetSdkVersion: 一部制限は all apps、より厳格な制限は公式文書上 37 以上。
- Device/form factor: 公式抜粋では条件なし。
- Permission/API/component condition: audio playback、audio focus request、volume change APIs、foreground service、WIU capabilities、exact alarm permission、`AudioAttributes.USAGE_ALARM`。
- App state/process condition: アプリが background にいる状態で audio と interaction する場合。

Compat framework:
- Change ID: Unknown
- Change name: Unknown
- Default state: Unknown
- Toggleable for testing: Unknown

分類信頼度（Classification confidence）:
- Low

分類根拠（Classification evidence）:
- Official documentation page: `behavior-changes-17`
- Original applicability statement: some restrictions apply to all apps; restrictions are more stringent for apps targeting Android 17 / API level 37; background audio interaction requires foreground service plus WIU capability and/or exact alarm + `USAGE_ALARM` condition.
- AOSP targetSdk gate: 未確認。local `frameworks-base` に `android-17*` tag がない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# エグゼクティブサマリー（Executive Summary）

Android 17 では、background からの audio playback、audio focus request、volume change APIs などに制限が入り、ユーザーが意図して開始した audio interaction であることを保証する方向に hardening される、と公式文書は説明している。

一部の制限は全アプリに適用されるが、targetSdkVersion 37 以上のアプリではより厳格になり、background で audio と interaction するには foreground service が running であることに加え、WIU capabilities または exact alarm permission + `USAGE_ALARM` audio stream の条件が必要になる。

ただし、現時点の local `frameworks-base` には Android 17 AOSP tag がないため、実装差分、all-apps 制限と targetSdkVersion 37 制限の境界、gate、Compat Change ID は未確認である。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statement）

Page title:
- Behavior changes: Apps targeting Android 17 or higher

Page URL:
- https://developer.android.com/about/versions/17/behavior-changes-17

Page type:
- apps targeting Android 17

Section title:
- Background audio hardening

Original statement being verified:

> Beginning with Android 17, the audio framework enforces restrictions on background audio interactions including audio playback, audio focus requests, and volume change APIs to ensure that these changes are started intentionally by the user.

The supplied official text also states that some audio restrictions apply to all apps, but restrictions are more stringent for apps targeting Android 17 / API level 37. For those apps, background audio interaction requires a running foreground service and either WIU capabilities, or exact alarm permission with interaction on `USAGE_ALARM` audio streams.

## 解釈（Interpretation）

この変更は、background にいるアプリがユーザーの明示的な文脈なしに音声再生、audio focus、音量変更を行うことを抑える audio framework hardening である。

アプリ開発者にとって重要なのは、targetSdkVersion 37 に更新した後、background audio interaction が foreground service の存在だけでは足りず、WIU capability または alarm use case に限定された条件も必要になる可能性がある点である。音楽、アラーム、通話、ナビゲーション、録音、音声通知などの background audio use case は、foreground service type、permission、audio usage を見直す必要がある。

---

# 変更内容（What Changed）

公式文書上の変更点:
- Android 17 では audio framework が background audio interactions に制限を適用する。
- 対象 interaction には audio playback、audio focus requests、volume change APIs が含まれる。
- 目的は、これらの変更がユーザーにより意図して開始されたものであることを保証すること。
- 一部の audio restrictions は all apps に適用される。
- targetSdkVersion 37 以上のアプリでは制限がより厳格になる。
- targetSdkVersion 37 以上のアプリが background で audio と interaction する場合、foreground service が running である必要がある。
- さらに、foreground service が WIU capabilities を持つ、または app が exact alarm permission を持ち `USAGE_ALARM` audio streams と interaction している、の一方または両方を満たす必要がある。

AOSP で未確認の点:
- Android 16 baseline の background audio playback / focus / volume API の許可条件。
- Android 17 の all apps restriction と targetSdkVersion 37+ restriction の実装差分。
- targetSdkVersion 37 gate の実装箇所。
- background state、foreground service running、WIU capabilities の判定箇所。
- exact alarm permission と `AudioAttributes.USAGE_ALARM` の組み合わせ判定。
- 制限違反時の failure mode。例: playback blocked、focus denied、volume API ignored / exception / error code。
- Compat Change ID と default state。

## 適用条件（Applicability）

公式文書の一次判断では、Android 17 上の background audio interaction に一部 all-apps 制限があり、targetSdkVersion 37 以上では foreground service + WIU / alarm 条件を伴う追加制限がある。AOSP tag が未取得で all-apps 部分と targetSdkVersion 37 部分の境界を確認できないため、確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

### OS アップデート時の挙動（OS Update Behavior）

- Android 17 にアップデートしただけで適用されるか: Conditional / Unknown
- targetSdkVersion に依存しない根拠: 公式文書は "Some audio restrictions apply to all apps" と述べている。ただし、どの API / 条件が all apps に適用されるかは AOSP 未確認。
- Android 16 以前での挙動: 未確認。Android 17 tag との明示的な比較ができないため、Android 16 source だけから platform evidence として断定しない。

### targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- targetSdkVersion 37 以上で適用されるか: 公式文書上は Yes と読めるが、AOSP gate 未確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: Unknown。公式文書は Android 17 Behavior Changes として説明しているため、Android 17 platform behavior として扱う。
- opt-out / temporary override の有無: Unknown。公式抜粋には opt-out は示されていない。compat framework による force enable / disable は未確認。

### その他の条件（Other Conditions）

- device/form factor: 公式抜粋では条件なし。
- permission: exact alarm permission。foreground service / WIU capabilities に関わる permission / foreground service type が関係する可能性。
- API usage: audio playback、audio focus request、volume change APIs、`AudioAttributes.USAGE_ALARM`。
- manifest attribute: foreground service type、exact alarm permission declaration が関係する可能性があるが、AOSP 未確認。
- component boundary: app process、audio framework、AudioService / AudioManager、foreground service state、alarm permission、process/background state にまたがる。

---

# AOSP 調査（AOSP Investigation）

## checkout 状態（Checkout Status）

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

根拠上の制約（Evidence limitation）:
- Android 17 AOSP tag が local `frameworks-base` に存在しないため、`git -C frameworks-base diff android-16.0.0_r4 <android-17-tag> -- ...` による明示的な tag 比較を実行できない。
- Repository rule に従い、Android 17 working tree や推測による source evidence は採用しない。
- この制約により、AOSP-backed conclusion は High confidence にできない。

## 関連ファイル（Related Files）

未確認。Android 17 AOSP tag 取得後に、少なくとも以下の候補を tag 比較で確認する必要がある。

- `media/java/android/media/AudioManager.java`
- `media/java/android/media/AudioAttributes.java`
- `services/core/java/com/android/server/audio/AudioService.java`
- `services/core/java/com/android/server/audio/MediaFocusControl.java`
- `services/core/java/com/android/server/am/ActiveServices.java`
- `services/core/java/com/android/server/alarm/AlarmManagerService.java`
- `core/java/android/app/ForegroundServiceTypePolicy.java`
- `core/java/android/Manifest.java`
- compat framework 定義ファイル内の background audio / audio focus / volume API / targetSdkVersion 37 関連 Change ID

## 確認したソース文脈（Source Context Reviewed）

Android 17 AOSP tag がないため、source context は未レビュー。

| File / symbol | Android 16 baseline | Android 17 behavior | Why this code path matters |
| --- | --- | --- | --- |
| Not reviewed | Not reviewed | Not reviewed | Android 17 tag がないため、公式文書の記述を AOSP diff で検証できない。 |

Required context:
- Entry point / caller: 未確認。想定される entry point は `AudioTrack` / media playback start、`AudioManager.requestAudioFocus()`、volume change APIs、AudioService enforcement、foreground service / alarm permission check だが、AOSP evidence としては未採用。
- Relevant class or service responsibility: 未確認。
- Runtime path from app API / system event to changed code: 未確認。
- Why unrelated code paths were excluded: Android 17 tag 不在のため、source path の採否判断自体を保留。

## 差分解釈（Diff Interpretation）

| Observed diff | Interpretation | Behavior Change relevance | Confidence |
| --- | --- | --- | --- |
| No Android 17 tag diff available | Source diff type cannot be classified yet | 公式文書の background audio restriction、all apps / targetSdkVersion 37 分岐、FGS / WIU / exact alarm / `USAGE_ALARM` gate を source diff で裏取りできていない | Low |

Required interpretation:
- Added behavior: 未確認。公式文書上は制限追加または enforcement 強化の可能性がある。
- Removed behavior: 未確認。
- Changed condition / gate: 未確認。targetSdkVersion 37、background state、foreground service、WIU、exact alarm、`USAGE_ALARM` の gate がある可能性は高いが、AOSP 未確認。
- Changed default: 未確認。
- No behavior change found: 未確認。tag 不在のため「no behavior change」とは判断しない。

## 事実（Evidence）

Facts:
- 公式 Behavior Change 文書は、Android 17 から audio framework が background audio interactions に制限を適用すると述べている。
- 公式文書は、対象に audio playback、audio focus requests、volume change APIs が含まれると述べている。
- 公式文書は、一部の audio restrictions が all apps に適用されると述べている。
- 公式文書は、targetSdkVersion 37 以上のアプリでは制限がより厳格になると述べている。
- 公式文書は、targetSdkVersion 37 以上の background audio interaction には foreground service running が必要と述べている。
- 公式文書は、追加条件として foreground service の WIU capabilities、または exact alarm permission + `USAGE_ALARM` audio streams の一方または両方を満たす必要があると述べている。
- local `frameworks-base` には `android-16.0.0_r4` tag がある。
- local `frameworks-base` には `android-17*` tag がない。
- 調査時点で `frameworks-base` working tree は clean。

Observations:
- 公式ページ種別は targetSdkVersion 37 以上向けであるが、原文には all apps に適用される制限も含まれている。
- この項目は targetSdkVersion 37 条件に加えて、background state、audio API usage、foreground service running、WIU capabilities、exact alarm permission、`USAGE_ALARM` という複数の runtime / permission condition を含む。
- all apps 制限と targetSdkVersion 37 以上の追加制限が混在するため、AOSP gate なしに `TARGET_SDK_37_CONDITIONAL` と確定するのは危険である。
- AOSP tag がないため、実装がどの条件で targetSdkVersion 37 gate を使うかは未確認。
- Compat framework entry の有無も未確認。

Hypotheses:
- Android 17 / targetSdkVersion 37 以上では、background で音声再生、audio focus request、volume change API を使うアプリが foreground service を持たない場合、操作が拒否される可能性が高い。
- foreground service が running でも WIU capabilities がない場合、alarm use case 以外では拒否される可能性があるが、AOSP 未確認のため断定しない。
- exact alarm permission + `USAGE_ALARM` は alarm apps の例外経路として機能する可能性がある。

結論:
- 現時点で顧客向けに確定できるのは、「公式文書上は Android 17 で background audio interaction が hardening され、targetSdkVersion 37 以上では foreground service + WIU または exact alarm + `USAGE_ALARM` 条件が必要になる」という範囲まで。
- all apps 制限の範囲、targetSdkVersion 37 gate、failure mode、compat framework default state が未確認のため、primary classification は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

## 適用ゲート根拠（Applicability Gate Evidence）

- targetSdkVersion gate: 未確認。公式文書は targetSdkVersion 37 以上で制限がより厳格と述べるが、AOSP gate evidence はない。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。Android 17 tag がないため検索未実施。
- @EnabledAfter / @EnabledSince / default state: 未確認。Android 17 tag がないため検索未実施。
- Build.VERSION / SDK_INT gate: 未確認。
- DeviceConfig / resources config: 未確認。
- Permission/AppOps gate: 未確認。公式文書上は exact alarm permission、foreground service / WIU capability が条件だが、AOSP の permission / AppOps path は未確認。
- Manifest/property gate: foreground service type、exact alarm permission declaration が関係する可能性はあるが、AOSP evidence は未確認。
- No gate found: 未確認。Android 17 tag がないため「gate がない」とは判断しない。
- Gate conclusion: Unknown。公式文書の wording から all apps 制限 + targetSdkVersion 37 conditional hardening と推定されるが、AOSP で検証できていない。
- Reasoning from source context: source context 未レビューのため未確定。

---

# 影響分析（Impact Analysis）

## 影響を受けるアプリ（Affected Apps）

影響を受ける可能性があるアプリ:
- background で audio playback を開始または継続するアプリ。
- background で `AudioManager.requestAudioFocus()` を呼ぶアプリ。
- background で volume change APIs を使うアプリ。
- foreground service なし、または WIU capabilities なしで background audio interaction を行うアプリ。
- alarm 音を扱うが exact alarm permission や `AudioAttributes.USAGE_ALARM` の利用が不十分なアプリ。
- targetSdkVersion 37 への更新を予定している音楽、ポッドキャスト、アラーム、通話、ナビゲーション、録音、音声通知系アプリ。

## 影響を受けないアプリ（Non-Affected Apps）

影響が限定的または対象外と考えられるケース:
- background audio interaction を行わないアプリ。
- audio 操作が foreground UI からのみ開始されるアプリ。
- background audio interaction 時に適切な foreground service と WIU capabilities を満たすアプリ。
- alarm use case で exact alarm permission と `USAGE_ALARM` audio stream 条件を満たすアプリ。
- Android 17 AOSP tag 取得後に対象外 gate や exemption が確認されたケース。

---

# 顧客影響（Customer Impact）

顧客説明用。

## 影響度（Impact Level）

- Human decision required

※ 仮評価。最終判断は人間が行う。

## ビジネス影響（Business Impact）

- ユーザー影響: background での再生開始、アラーム音、通知音、音量変更、audio focus 獲得が失敗すると、音声機能の信頼性が下がる可能性がある。
- 運用影響: audio use case ごとに foreground service、WIU capability、exact alarm permission、audio usage の組み合わせを確認する必要がある可能性がある。
- 開発影響: background audio 操作の起点をユーザー操作へ寄せ、FGS type / permission / `AudioAttributes` / error handling / targetSdkVersion 37 テストを見直す必要がある可能性がある。

---

# サービス影響例（Service Impact Examples）

このセクションは、公式文書と AOSP evidence から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: 音楽 / ポッドキャスト再生アプリ

- 対象サービス例: 音楽 streaming、podcast、radio、meditation audio。
- 影響を受ける実装パターン: background から playback start / audio focus request を行うが、running FGS や WIU capability を満たさない実装。
- 発生条件: Android 17 / targetSdkVersion 37 で background audio interaction が厳格化される場合。
- ユーザーに見える症状: 再生開始に失敗する、通知操作後に音が出ない、focus が取れない可能性。
- 開発・運用への影響: FGS type、user-initiated flow、audio focus handling、telemetry の見直しが必要になる可能性。
- 推奨対応候補: background audio を適切な foreground service と user-visible control に紐づける。
- 根拠: 公式 statement と report の expected behavior。
- Confidence（信頼度）: Low
- 注意: all apps 制限と targetSdkVersion 37 制限の境界は未確認。

## 例2（Example 2）: アラーム / リマインダーアプリ

- 対象サービス例: アラーム、服薬リマインダー、タイマー、カレンダー通知。
- 影響を受ける実装パターン: background で alarm sound を鳴らすが exact alarm permission や `USAGE_ALARM` を満たしていない実装。
- 発生条件: targetSdkVersion 37 で exact alarm + `USAGE_ALARM` 条件が必要になる場合。
- ユーザーに見える症状: アラーム音が鳴らない、volume change が効かない、通知だけ表示される可能性。
- 開発・運用への影響: exact alarm permission UX、AudioAttributes、FGS / WIU capability の見直しが必要になる可能性。
- 推奨対応候補: alarm use case を `USAGE_ALARM` と exact alarm permission に整合させる。
- 根拠: 公式 statement と report の action candidates。
- Confidence（信頼度）: Low
- 注意: 実際の failure mode は AOSP tag / 実機検証待ち。

---

# 対応候補（Required Actions）

## 必須対応（Must）

- background で audio playback、audio focus request、volume change APIs を使う箇所を棚卸しする。
- targetSdkVersion 37 で background audio interaction を行う必要がある場合、foreground service が running であることを確認する。
- foreground service が WIU capabilities を満たすか、alarm use case では exact alarm permission と `USAGE_ALARM` を満たすか確認する。
- audio API の failure / denied / ignored を前提に error handling と fallback UX を確認する。
- Android 17 / targetSdkVersion 37 のテスト環境が利用可能になったら、foreground / background、FGS あり / なし、WIU あり / なし、alarm condition あり / なしを分けて検証する。
- Android 17 AOSP tag 入手後に、all apps 制限、targetSdkVersion 37 gate、failure mode、compat Change ID を再確認する。

## 推奨対応（Recommended）

- background からの audio 操作を、通知 action、visible UI、user-initiated flow へ寄せる。
- alarm app は exact alarm permission と `AudioAttributes.USAGE_ALARM` の利用を明確にし、通常の media / notification usage と混在させない。
- audio focus と volume change APIs の呼び出しに telemetry を追加し、Android 17 での拒否や失敗を検出できるようにする。
- Background audio hardening の詳細ページで mitigation strategies を確認する。

## 任意対応（Optional）

- 音声系機能を use case 別に分類し、media playback、alarm、call、navigation、accessibility 的 audio feedback の権限・FGS 要件を整理する。
- Android 17 tag 入手後に CTS / 実機ログで AudioService の rejection reason を確認する。

---

# 検証方法（Verification Method）

## 検証マトリクス（Matrix）

| Device OS | targetSdkVersion | Compat flag | Expected behavior |
| --- | --- | --- | --- |
| Android 16 | 36 | default | Android 16 baseline。background audio interaction の具体挙動は Android 17 tag 比較待ち。 |
| Android 17 | 36 | default | Unknown。一部 all apps 制限があると公式文書は述べるが、範囲と gate は未確認。 |
| Android 17 | 37 | default | 公式文書上、background audio interaction には running foreground service と WIU capability または exact alarm + `USAGE_ALARM` 条件が必要。 |
| Android 17 | 36 | force-enabled if available | Unknown。Compat Change ID 未確認。 |
| Android 17 | 37 | force-disabled if available | Unknown。Compat Change ID 未確認。 |

## 手順（Steps）

- targetSdk変更: targetSdkVersion 36 と 37 の test build を用意する。
- compat framework command: 未確認。Android 17 compat framework entry / Change ID が判明後に記録する。
- テスト方法: background / foreground、FGS あり / なし、WIU capability あり / なし、exact alarm permission あり / なし、`USAGE_ALARM` / non-alarm usage を組み合わせて audio playback、audio focus、volume API を実行する。
- 再現手順: Android 17 device / emulator で対象アプリを install し、app を background にした状態で audio API を呼び出す。API return value、exception、system log、実際の音声出力、focus state を記録する。
- 期待結果: targetSdkVersion 37 の background audio interaction は、公式文書の条件を満たさない場合に制限される。具体的な failure mode は AOSP tag と実機検証待ち。

---

# 結論（Conclusion）

公式文書上、Android 17 では background audio interaction が hardening され、targetSdkVersion 37 以上のアプリでは background で audio と interaction するために running foreground service と WIU capability、または exact alarm permission + `USAGE_ALARM` 条件が必要になる。

ただし、Android 17 AOSP tag が local checkout にないため、all apps 制限の範囲、targetSdkVersion 37 gate、failure mode、compat framework の確認は未完了である。最終的な適用分類と顧客向け確定説明は、Android 17 AOSP tag 入手後に再調査が必要である。

---

# 人間の判断欄（Human Decision Placeholder）

最終優先度（Final Priority）:
- Human decision required

Final Severity:
- Human decision required

Release Readiness:
- Human decision required

Customer Communication Priority:
- Human decision required

判断（Decision）:
- Further investigation required

Decision notes:
- Android 17 AOSP tag 入手後に、AOSP evidence と compat framework evidence を確認してから最終判断する。

---

# 参照（References）

## ドキュメント（Documentation）

- https://developer.android.com/about/versions/17/behavior-changes-17
- https://developer.android.com/develop/background-work/services/alarms#exact
- https://developer.android.com/reference/android/media/AudioAttributes#USAGE_ALARM
- https://developer.android.com/about/versions/17/changes/bg-audio

## AOSP

- Not available for Android 17 in local `frameworks-base`.
- From tag checked: `android-16.0.0_r4`
- To tag checked: no local `android-17*` tag found.

# バックグラウンド音声の制限強化

> 役割メモ:
> このファイルは、バックグラウンド音声の制限強化のうち、targetSdkVersion 37 以上で強まる追加条件を中心に扱う。
> Android 17 上の全アプリに関係する共通制限は [all/media/background-audio-hardening.md](../../all/media/background-audio-hardening.md) を参照する。
> 公式詳細ページ `changes/bg-audio` には全アプリ共通制限と targetSdkVersion 37 追加条件の両方が記載されているため、13 と 24 は相互補完の関係として扱う。

## 基本情報

### 調査対象 Android バージョン

比較元:
- android-16.0.0_r4

比較先:
- TBD: Android 17 AOSP タグ

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

### Behavior Change 文書

文書:
https://developer.android.com/about/versions/17/behavior-changes-17

現在の関連公式文書:
- https://developer.android.com/about/versions/17/behavior-changes-all
- https://developer.android.com/about/versions/17/changes/bg-audio

関連文書:
- https://developer.android.com/develop/background-work/services/alarms#exact
- https://developer.android.com/reference/android/media/AudioAttributes#USAGE_ALARM
- https://developer.android.com/about/versions/17/changes/bg-audio

セクション:
Background audio hardening

ページ種別:
- Apps targeting Android 17 or higher

現在の source split:
- `behavior-changes-all`: Android 17 上の全アプリに関係する共通制限。
- `changes/bg-audio`: 共通制限に加え、targetSdkVersion 37 以上で強まる WIU capability 条件を説明。

### 分類スナップショット

主分類（Primary classification）:
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- このファイルでは、バックグラウンド音声の制限強化のうち targetSdkVersion 37 以上で強まる追加条件を中心に整理する。Android 17 上の全アプリに関係する共通制限は [all/media/background-audio-hardening.md](../../all/media/background-audio-hardening.md) に整理している。
- 公式文書は、Android 17 以降、audio playback、audio focus requests、volume change APIs などの background audio interactions に制限を適用し、ユーザーが意図して開始した変更であることを保証すると説明している。
- 一部の audio restrictions は all apps に適用される一方、targetSdkVersion 37 以上のアプリではより厳格になると説明している。
- targetSdkVersion 37 以上のアプリが background で audio と interaction する場合、foreground service が running である必要があり、さらに foreground service が while-in-use (WIU) capabilities を持つか、exact alarm permission を持ち `USAGE_ALARM` audio streams と interaction している必要がある。
- ただし、ローカル `frameworks-base` に Android 17 AOSP タグがないため、audio framework の enforcement path、all apps 制限と targetSdkVersion 37 制限の分岐、foreground service / WIU / exact alarm / `USAGE_ALARM` gate、Compat Change ID、default state は未検証である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

早見表:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | Conditional / 未確認 | 公式文書は一部制限が all apps に適用されると述べるが、詳細と AOSP gate は未確認。 |
| targetSdkVersion 37 以上が必要か | 一部該当するが未確認 | 原文は targetSdkVersion 37 以上では restrictions are more stringent と述べている。 |
| 追加の実行時条件があるか | ある | background audio interaction、foreground service running、WIU capabilities、exact alarm permission、`USAGE_ALARM`。 |
| Compat Change ID が関係するか | 未確認 | Android 17 タグと compat framework evidence が未確認。 |

### 調査日

2026-06-11

### 信頼度

- 低

### 適用条件分類

適用される条件:
- [ ] Android 17 上の全アプリ（targetSdkVersion に依存しない）
- [ ] Android 17 以上で targetSdkVersion >= 37
- [ ] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [x] 未確認 / 追加根拠が必要

必要な実行時条件:
- Android version: Android 17 以上が前提と考えられるが、AOSP タグ未取得。
- targetSdkVersion: 一部制限は all apps、より厳格な制限は公式文書上 37 以上。
- Device/form factor: 公式抜粋では条件なし。
- Permission/API/component condition: audio playback、audio focus request、volume change APIs、foreground service、WIU capabilities、exact alarm permission、`AudioAttributes.USAGE_ALARM`。
- App state/process condition: アプリが background にいる状態で audio と interaction する場合。

Compat framework:
- Change ID: 未確認
- 変更名: 未確認
- 既定状態: 未確認
- テスト時の切り替え可否: 未確認

分類信頼度:
- 低

分類根拠:
- 公式ドキュメントページ: `behavior-changes-17`
- 検証対象の適用条件文: some restrictions apply to all apps; restrictions are more stringent for apps targeting Android 17 / API level 37; background audio interaction requires foreground service plus WIU capability and/or exact alarm + `USAGE_ALARM` condition.
- AOSP targetSdk gate: 未確認。ローカル `frameworks-base` に `android-17*` タグがない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# エグゼクティブサマリー

Android 17 では、background からの audio playback、audio focus request、volume change APIs などに制限が入り、ユーザーが意図して開始した audio interaction であることを保証する方向に hardening される、と公式文書は説明している。

一部の制限は全アプリに適用されるが、targetSdkVersion 37 以上のアプリではより厳格になり、background で audio と interaction するには foreground service が running であることに加え、WIU capabilities または exact alarm permission + `USAGE_ALARM` audio stream の条件が必要になる。

ただし、現時点のローカル `frameworks-base` には Android 17 AOSP タグがないため、実装差分、all-apps 制限と targetSdkVersion 37 制限の境界、gate、Compat Change ID は未確認である。

---

# 公式ドキュメント確認

## 原文（Statement）

Page title:
- Behavior changes: Apps targeting Android 17 or higher

Page URL:
- https://developer.android.com/about/versions/17/behavior-changes-17

ページ種別:
- apps targeting Android 17

Section title:
- Background audio hardening

検証対象の原文:

> Beginning with Android 17, the audio framework enforces restrictions on background audio interactions including audio playback, audio focus requests, and volume change APIs to ensure that these changes are started intentionally by the user.

提供された公式文書の抜粋は、一部の audio restrictions が all apps に適用される一方、Android 17 / API level 37 を対象とするアプリでは制限がより厳しくなると説明している。これらのアプリでは、background audio interaction に running foreground service が必要であり、さらに WIU capabilities、または exact alarm permission と `USAGE_ALARM` audio streams の操作が必要になる。

## 解釈

この変更は、background にいるアプリがユーザーの明示的な文脈なしに音声再生、audio focus、音量変更を行うことを抑える audio framework hardening である。

アプリ開発者にとって重要なのは、targetSdkVersion 37 に更新した後、background audio interaction が foreground service の存在だけでは足りず、WIU capability または alarm use case に限定された条件も必要になる可能性がある点である。音楽、アラーム、通話、ナビゲーション、録音、音声通知などの background audio use case は、foreground service type、permission、audio usage を見直す必要がある。

---

# 変更内容

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

### OS アップデート時の挙動

- Android 17 にアップデートしただけで適用されるか: Conditional / 未確認
- targetSdkVersion に依存しない根拠: 公式文書は "Some audio restrictions apply to all apps" と述べている。ただし、どの API / 条件が all apps に適用されるかは AOSP 未確認。
- Android 16 以前での挙動: 未確認。Android 17 タグとの明示的な比較ができないため、Android 16 source だけから platform evidence として断定しない。

### targetSdkVersion 37 以上での挙動

- targetSdkVersion 37 以上で適用されるか: 公式文書上は Yes と読めるが、AOSP gate は未確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: 未確認。公式文書は Android 17 Behavior Changes として説明しているため、Android 17 platform behavior として扱う。
- opt-out / temporary override の有無: 未確認。公式抜粋には opt-out は示されていない。compat framework による force enable / disable は未確認。

### その他の条件

- device/form factor: 公式抜粋では条件なし。
- permission: exact alarm permission。foreground service / WIU capabilities に関わる permission / foreground service type が関係する可能性。
- API usage: audio playback、audio focus request、volume change APIs、`AudioAttributes.USAGE_ALARM`。
- manifest attribute: foreground service type、exact alarm permission declaration が関係する可能性があるが、AOSP 未確認。
- component boundary: app process、audio framework、AudioService / AudioManager、foreground service state、alarm permission、process/background state にまたがる。

---

# AOSP 調査

## checkout 状態

根拠を採用する前に確認したコマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list 'android-17*'
```

結果:
- `frameworks-base` working tree: 調査時点で clean。
- From tag: `android-16.0.0_r4` exists.
- To tag: ローカルに `android-17*` タグなし。

根拠上の制約:
- Android 17 AOSP タグがローカル `frameworks-base` に存在しないため、`git -C frameworks-base diff android-16.0.0_r4 <android-17-tag> -- ...` による明示的なタグ比較を実行できない。
- Repository rule に従い、Android 17 working tree や推測による source evidence は採用しない。
- この制約により、AOSP-backed conclusion は高信頼度にできない。

## 関連ファイル

未確認。Android 17 AOSP タグ取得後に、少なくとも以下の候補をタグ比較で確認する必要がある。

- `media/java/android/media/AudioManager.java`
- `media/java/android/media/AudioAttributes.java`
- `services/core/java/com/android/server/audio/AudioService.java`
- `services/core/java/com/android/server/audio/MediaFocusControl.java`
- `services/core/java/com/android/server/am/ActiveServices.java`
- `services/core/java/com/android/server/alarm/AlarmManagerService.java`
- `core/java/android/app/ForegroundServiceTypePolicy.java`
- `core/java/android/Manifest.java`
- compat framework 定義ファイル内の background audio / audio focus / volume API / targetSdkVersion 37 関連 Change ID

## 確認したソース文脈

Android 17 AOSP タグがないため、source context は未レビュー。

| ファイル / シンボル | Android 16 基準挙動 | Android 17 挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| 未レビュー | 未レビュー | 未レビュー | Android 17 タグがないため、公式文書の記述を AOSP diff で検証できない。 |

必須記入項目:
- Entry point / caller: 未確認。想定される entry point は `AudioTrack` / media playback start、`AudioManager.requestAudioFocus()`、volume change APIs、AudioService enforcement、foreground service / alarm permission check だが、AOSP evidence としては未採用。
- Relevant class or service responsibility: 未確認。
- Runtime path from app API / system event to changed code: 未確認。
- 除外した無関係なコードパス: Android 17 タグ不在のため、source path の採否判断自体を保留。

## 差分解釈

| 確認した差分 | 解釈 | 挙動変更との関係 | 信頼度 |
| --- | --- | --- | --- |
| Android 17 タグ間差分は利用不可 | ソース差分の種別はまだ分類できない | 公式文書の background audio restriction、all apps / targetSdkVersion 37 分岐、FGS / WIU / exact alarm / `USAGE_ALARM` gate を source diff で裏取りできていない | 低 |

必須分類:
- Added behavior: 未確認。公式文書上は制限追加または enforcement 強化の可能性がある。
- Removed behavior: 未確認。
- Changed condition / gate: 未確認。targetSdkVersion 37、background state、foreground service、WIU、exact alarm、`USAGE_ALARM` の gate がある可能性は高いが、AOSP 未確認。
- Changed default: 未確認。
- No behavior change found: 未確認。タグ不在のため「no behavior change」とは判断しない。

## 事実

事実:
- 公式 Behavior Change 文書は、Android 17 から audio framework が background audio interactions に制限を適用すると述べている。
- 公式文書は、対象に audio playback、audio focus requests、volume change APIs が含まれると述べている。
- 公式文書は、一部の audio restrictions が all apps に適用されると述べている。
- 公式文書は、targetSdkVersion 37 以上のアプリでは制限がより厳格になると述べている。
- 公式文書は、targetSdkVersion 37 以上の background audio interaction には foreground service running が必要と述べている。
- 公式文書は、追加条件として foreground service の WIU capabilities、または exact alarm permission + `USAGE_ALARM` audio streams の一方または両方を満たす必要があると述べている。
- ローカル `frameworks-base` には `android-16.0.0_r4` タグがある。
- ローカル `frameworks-base` には `android-17*` タグがない。
- 調査時点で `frameworks-base` working tree は clean。

観察:
- 公式ページ種別は targetSdkVersion 37 以上向けであるが、原文には all apps に適用される制限も含まれている。
- この項目は targetSdkVersion 37 条件に加えて、background state、audio API usage、foreground service running、WIU capabilities、exact alarm permission、`USAGE_ALARM` という複数の runtime / permission condition を含む。
- all apps 制限と targetSdkVersion 37 以上の追加制限が混在するため、AOSP gate なしに `TARGET_SDK_37_CONDITIONAL` と確定するのは危険である。
- AOSP タグがないため、実装がどの条件で targetSdkVersion 37 gate を使うかは未確認。
- Compat framework entry の有無も未確認。

仮説:
- Android 17 / targetSdkVersion 37 以上では、background で音声再生、audio focus request、volume change API を使うアプリが foreground service を持たない場合、操作が拒否される可能性が高い。
- foreground service が running でも WIU capabilities がない場合、alarm use case 以外では拒否される可能性があるが、AOSP 未確認のため断定しない。
- exact alarm permission + `USAGE_ALARM` は alarm apps の例外経路として機能する可能性がある。

結論:
- 現時点で顧客向けに確定できるのは、「公式文書上は Android 17 で background audio interaction が hardening され、targetSdkVersion 37 以上では foreground service + WIU または exact alarm + `USAGE_ALARM` 条件が必要になる」という範囲まで。
- all apps 制限の範囲、targetSdkVersion 37 gate、failure mode、compat framework default state が未確認のため、主分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

## 適用ゲート根拠

- targetSdkVersion 適用ゲート: 未確認。公式文書は targetSdkVersion 37 以上で制限がより厳格と述べるが、AOSP gate evidence はない。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。Android 17 タグがないため検索未実施。
- @EnabledAfter / @EnabledSince / default state: 未確認。Android 17 タグがないため検索未実施。
- Build.VERSION / SDK_INT 適用ゲート: 未確認。
- DeviceConfig / resources config: 未確認。
- Permission/AppOps 適用ゲート: 未確認。公式文書上は exact alarm permission、foreground service / WIU capability が条件だが、AOSP の permission / AppOps path は未確認。
- Manifest/property 適用ゲート: foreground service type、exact alarm permission declaration が関係する可能性はあるが、AOSP evidence は未確認。
- 適用ゲート未検出: 未確認。Android 17 タグがないため「gate がない」とは判断しない。
- 適用ゲートの結論: 未確認。公式文書の wording から all apps 制限 + targetSdkVersion 37 conditional hardening と推定されるが、AOSP で検証できていない。
- ソース文脈からの推論: source context 未レビューのため未確定。

---

# 影響分析

## 影響を受けるアプリ

影響を受ける可能性があるアプリ:
- background で audio playback を開始または継続するアプリ。
- background で `AudioManager.requestAudioFocus()` を呼ぶアプリ。
- background で volume change APIs を使うアプリ。
- foreground service なし、または WIU capabilities なしで background audio interaction を行うアプリ。
- alarm 音を扱うが exact alarm permission や `AudioAttributes.USAGE_ALARM` の利用が不十分なアプリ。
- targetSdkVersion 37 への更新を予定している音楽、ポッドキャスト、アラーム、通話、ナビゲーション、録音、音声通知系アプリ。

## 影響を受けにくいアプリ

影響が限定的または対象外と考えられるケース:
- background audio interaction を行わないアプリ。
- audio 操作が foreground UI からのみ開始されるアプリ。
- background audio interaction 時に適切な foreground service と WIU capabilities を満たすアプリ。
- alarm use case で exact alarm permission と `USAGE_ALARM` audio stream 条件を満たすアプリ。
- Android 17 AOSP タグ取得後に対象外 gate や exemption が確認されたケース。

---

# 顧客影響

## 影響度

- 人間による判断が必要

※ 最終 severity / priority は人間が判断する。このレポートでは確定しない。

## ビジネス影響

- ユーザー影響: background での再生開始、アラーム音、通知音、音量変更、audio focus 獲得が失敗すると、音声機能の信頼性が下がる可能性がある。
- 運用影響: audio use case ごとに foreground service、WIU capability、exact alarm permission、audio usage の組み合わせを確認する必要がある可能性がある。
- 開発影響: background audio 操作の起点をユーザー操作へ寄せ、FGS type / permission / `AudioAttributes` / error handling / targetSdkVersion 37 テストを見直す必要がある可能性がある。

---

# サービス影響例

このセクションは、公式文書と AOSP evidence から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1: 音楽 / ポッドキャスト再生アプリ

- 対象サービス例: 音楽 streaming、podcast、radio、meditation audio。
- 影響を受ける実装パターン: background から playback start / audio focus request を行うが、running FGS や WIU capability を満たさない実装。
- 発生条件: Android 17 / targetSdkVersion 37 で background audio interaction が厳格化される場合。
- ユーザーに見える症状: 再生開始に失敗する、通知操作後に音が出ない、focus が取れない可能性。
- 開発・運用への影響: FGS type、user-initiated flow、audio focus handling、telemetry の見直しが必要になる可能性。
- 推奨対応候補: background audio を適切な foreground service と user-visible control に紐づける。
- 根拠: 公式 statement と report の expected behavior。
- 信頼度: 低
- 注意: all apps 制限と targetSdkVersion 37 制限の境界は未確認。

## 例2: アラーム / リマインダーアプリ

- 対象サービス例: アラーム、服薬リマインダー、タイマー、カレンダー通知。
- 影響を受ける実装パターン: background で alarm sound を鳴らすが exact alarm permission や `USAGE_ALARM` を満たしていない実装。
- 発生条件: targetSdkVersion 37 で exact alarm + `USAGE_ALARM` 条件が必要になる場合。
- ユーザーに見える症状: アラーム音が鳴らない、volume change が効かない、通知だけ表示される可能性。
- 開発・運用への影響: exact alarm permission UX、AudioAttributes、FGS / WIU capability の見直しが必要になる可能性。
- 推奨対応候補: alarm use case を `USAGE_ALARM` と exact alarm permission に整合させる。
- 根拠: 公式 statement と report の action candidates。
- 信頼度: 低
- 注意: 実際の failure mode は AOSP タグ / 実機検証待ち。

---

# 対応候補

## 必須対応（Must）

- background で audio playback、audio focus request、volume change APIs を使う箇所を棚卸しする。
- targetSdkVersion 37 で background audio interaction を行う必要がある場合、foreground service が running であることを確認する。
- foreground service が WIU capabilities を満たすか、alarm use case では exact alarm permission と `USAGE_ALARM` を満たすか確認する。
- audio API の failure / denied / ignored を前提に error handling と fallback UX を確認する。
- Android 17 / targetSdkVersion 37 のテスト環境が利用可能になったら、foreground / background、FGS あり / なし、WIU あり / なし、alarm condition あり / なしを分けて検証する。
- Android 17 AOSP タグ入手後に、all apps 制限、targetSdkVersion 37 gate、failure mode、compat Change ID を再確認する。

## 推奨対応（Recommended）

- background からの audio 操作を、通知 action、visible UI、user-initiated flow へ寄せる。
- alarm app は exact alarm permission と `AudioAttributes.USAGE_ALARM` の利用を明確にし、通常の media / notification usage と混在させない。
- audio focus と volume change APIs の呼び出しに telemetry を追加し、Android 17 での拒否や失敗を検出できるようにする。
- Background audio hardening の詳細ページで mitigation strategies を確認する。

## 任意対応（Optional）

- 音声系機能を use case 別に分類し、media playback、alarm、call、navigation、accessibility 的 audio feedback の権限・FGS 要件を整理する。
- Android 17 タグ入手後に CTS / 実機ログで AudioService の rejection reason を確認する。

---

# 検証方法

## 検証マトリクス

| 端末 OS | targetSdkVersion | Compat flag | 期待される挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | default | Android 16 baseline。background audio interaction の具体挙動は Android 17 タグ比較待ち。 |
| Android 17 | 36 | default | 未確認。一部 all apps 制限があると公式文書は述べるが、範囲と gate は未確認。 |
| Android 17 | 37 | default | 公式文書上、background audio interaction には running foreground service と WIU capability または exact alarm + `USAGE_ALARM` 条件が必要。 |
| Android 17 | 36 | force-enabled（利用可能な場合） | 未確認。Compat Change ID 未確認。 |
| Android 17 | 37 | force-disabled（利用可能な場合） | 未確認。Compat Change ID 未確認。 |

## 手順

- targetSdk変更: targetSdkVersion 36 と 37 の test build を用意する。
- Compat framework コマンド: 未確認。Android 17 compat framework entry / Change ID が判明後に記録する。
- テスト方法: background / foreground、FGS あり / なし、WIU capability あり / なし、exact alarm permission あり / なし、`USAGE_ALARM` / non-alarm usage を組み合わせて audio playback、audio focus、volume API を実行する。
- 再現手順: Android 17 device / emulator で対象アプリを install し、app を background にした状態で audio API を呼び出す。API return value、exception、system log、実際の音声出力、focus state を記録する。
- 期待結果: targetSdkVersion 37 の background audio interaction は、公式文書の条件を満たさない場合に制限される。具体的な failure mode は AOSP タグと実機検証待ち。

---

# 結論

公式文書上、Android 17 では background audio interaction が hardening され、targetSdkVersion 37 以上のアプリでは background で audio と interaction するために running foreground service と WIU capability、または exact alarm permission + `USAGE_ALARM` 条件が必要になる。

ただし、Android 17 AOSP タグがローカル checkout にないため、all apps 制限の範囲、targetSdkVersion 37 gate、failure mode、compat framework の確認は未完了である。最終的な適用分類と顧客向け確定説明は、Android 17 AOSP タグ入手後に再調査が必要である。

---

# 人間の判断欄

最終優先度（Final Priority）:
- 人間による判断が必要

最終影響度:
- 人間による判断が必要

リリース判断:
- 人間による判断が必要

顧客通知優先度:
- 人間による判断が必要

判断（Decision）:
- 追加調査が必要

判断メモ:
- Android 17 AOSP タグ入手後に、AOSP evidence と compat framework evidence を確認してから最終判断する。

---

# 参照（References）

## ドキュメント

- https://developer.android.com/about/versions/17/behavior-changes-17
- https://developer.android.com/develop/background-work/services/alarms#exact
- https://developer.android.com/reference/android/media/AudioAttributes#USAGE_ALARM
- https://developer.android.com/about/versions/17/changes/bg-audio

## AOSP

- ローカル `frameworks-base` では Android 17 は利用不可。
- From tag checked: `android-16.0.0_r4`
- To tag checked: ローカルに `android-17*` タグなし。

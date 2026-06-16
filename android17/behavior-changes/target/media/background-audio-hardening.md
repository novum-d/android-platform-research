# バックグラウンド音声の制限強化

> 役割メモ:
> このファイルは バックグラウンド音声の制限強化 のうち、targetSdkVersion 37 以上で強まる追加条件を中心に扱う。
> Android 17 上の全アプリに関係する共通制限は [all/media/background-audio-hardening.md](../../all/media/background-audio-hardening.md) を参照する。
> 公式詳細ページ `changes/bg-audio` には全アプリ共通制限と targetSdkVersion 37 追加条件の両方が記載されているため、13 と 24 は相互補完の関係として扱う。

## 基本情報

### 調査対象 Android バージョン

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP タグ

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

### Behavior Change 文書

Document:
https://developer.android.com/about/versions/17/behavior-changes-17

現在の関連公式文書:
- https://developer.android.com/about/versions/17/behavior-changes-all
- https://developer.android.com/about/versions/17/changes/bg-audio

関連文書:
- https://developer.android.com/develop/background-work/services/alarms#exact
- https://developer.android.com/reference/android/media/AudioAttributes#USAGE_ALARM
- https://developer.android.com/about/versions/17/changes/bg-audio

Section:
バックグラウンド音声の制限強化

Page type:
- Apps targeting Android 17 or higher

現在の source split:
- `behavior-changes-all`: Android 17 上の全アプリに関係する共通制限。
- `changes/bg-audio`: 共通制限に加え、targetSdkVersion 37 以上で強まる WIU capability 条件を説明。

### 分類スナップショット

主分類（Primary classification）:
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- このファイルでは、バックグラウンド音声の制限強化のうち、targetSdkVersion 37 以上で強まる追加条件を中心に整理する。Android 17 上の全アプリに関係する共通制限は [all/media/background-audio-hardening.md](../../all/media/background-audio-hardening.md) に整理している。
- 公式文書は、Android 17 以降、音声再生、オーディオフォーカス要求、音量変更 API などのバックグラウンドでの音声操作に制限を適用し、ユーザーが意図して開始した変更であることを保証すると説明している。
- 一部の音声制限は全アプリに適用される一方、targetSdkVersion 37 以上のアプリではより厳格になると説明している。
- targetSdkVersion 37 以上のアプリがバックグラウンドで音声とやり取りする場合、フォアグラウンドサービスが実行中である必要があり、さらにフォアグラウンドサービスが while-in-use (WIU) capabilities を持つか、正確なアラーム権限を持ち `USAGE_ALARM` 音声ストリームと interaction している必要がある。
- ただし、ローカルの `frameworks-base` に Android 17 AOSP タグがないため、音声フレームワークの適用パス、全アプリ制限と targetSdkVersion 37 制限の分岐、フォアグラウンドサービス / WIU / 正確なアラーム / `USAGE_ALARM` 適用ゲート、Compat Change ID、デフォルト状態は未検証である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

早見表:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | Conditional / 未確認 | 公式文書は一部制限が全アプリに適用されると述べるが、詳細と AOSP 適用ゲートは未確認。 |
| targetSdkVersion 37 以上が必要か | 一部該当するが未確認 | 原文は targetSdkVersion 37 以上では制限が more stringent になると述べている。 |
| 追加の実行時条件があるか | Yes | バックグラウンドでの音声操作、フォアグラウンドサービス running、WIU capabilities、正確なアラーム権限、`USAGE_ALARM`。 |
| Compat Change ID が関係するか | 未確認 | Android 17 タグと Compat framework 根拠が未確認。 |

### 調査日

2026-06-11

### 信頼度

- 低

### 適用条件分類

適用される条件（Applies when）:
- [ ] Android 17 上の全アプリ（targetSdkVersion に依存しない）
- [ ] Android 17 以上で targetSdkVersion >= 37
- [ ] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play システムアップデート dependent
- [ ] API addition only, not a behavior change
- [x] 未確認 / 追加根拠が必要

必要な実行時条件（必要な実行時条件）:
- Android バージョン: Android 17 以上が前提と考えられるが、AOSP タグは未取得。
- targetSdkVersion: 一部制限は 全アプリ、より厳格な制限は公式文書上 37 以上。
- 端末/フォームファクター: 公式抜粋では条件なし。
- Permission/API/コンポーネント条件: 音声再生、オーディオフォーカス要求、音量変更 APIs、フォアグラウンドサービス、WIU capabilities、正確なアラーム permission、`AudioAttributes.USAGE_ALARM`。
- アプリ状態/プロセス条件: アプリがバックグラウンドにいる状態で音声とやり取りする場合。

Compat framework:
- 変更 ID: 未確認
- 変更 name: 未確認
- デフォルト状態: 未確認
- テスト時の切り替え可否: 未確認

分類信頼度:
- 低

分類根拠:
- Official documentation page: `behavior-changes-17`
- 検証対象の適用条件文: 一部制限は全アプリに適用される。Android 17 / API level 37 を対象とするアプリでは制限が more stringent になり、バックグラウンド音声操作にはフォアグラウンドサービスに加え、WIU capability または正確なアラーム + `USAGE_ALARM` 条件が必要になる。
- AOSP targetSdk 適用ゲート: 未確認。ローカルの `frameworks-base` に `android-17*` タグがない。
- Compat framework エントリ: 未確認。Android 17 Compat framework 根拠が未取得。

---

# エグゼクティブサマリー

Android 17 では、バックグラウンドからの音声再生、オーディオフォーカス要求、音量変更 API などに制限が入り、ユーザーが意図して開始した音声操作であることを保証する方向に hardening される、と公式文書は説明している。

一部の制限は全アプリに適用されるが、targetSdkVersion 37 以上のアプリではより厳格になり、バックグラウンドで音声とやり取りするにはフォアグラウンドサービスが実行中であることに加え、WIU capabilities または正確なアラーム権限 + `USAGE_ALARM` 音声ストリームの条件が必要になる。

ただし、現時点のローカルの `frameworks-base` には Android 17 AOSP タグがないため、実装差分、全アプリ制限と targetSdkVersion 37 制限の境界、適用ゲート、Compat Change ID は未確認である。

---

# 公式ドキュメント確認

## 原文（Statement）

Page title:
- Behavior changes: Apps targeting Android 17 or higher

Page URL:
- https://developer.android.com/about/versions/17/behavior-changes-17

Page type:
- Android 17 を対象とするアプリ

Section title:
- バックグラウンド音声の制限強化

検証対象の原文:

> Android 17 から、音声フレームワークは、音声再生、オーディオフォーカス要求、音量変更 API などのバックグラウンドでの音声操作に制限を適用し、これらの操作がユーザーの意図によって開始されるようにする。

提供された公式文書の抜粋は、一部の音声制限は全アプリに適用される一方、Android 17 / API level 37 を対象とするアプリでは制限がより厳しくなると説明している。これらのアプリでは、バックグラウンドでの音声操作に実行中のフォアグラウンドサービスが必要であり、さらに WIU 能力、または正確なアラーム権限と `USAGE_ALARM` 音声ストリームの操作が必要になる。

## 解釈

この変更は、バックグラウンドにいるアプリがユーザーの明示的な文脈なしに音声再生、オーディオフォーカス、音量変更を行うことを抑える音声フレームワーク hardening である。

アプリ開発者にとって重要なのは、targetSdkVersion 37 に更新した後、バックグラウンドでの音声操作がフォアグラウンドサービスの存在だけでは足りず、WIU capability または alarm ユースケースに限定された条件も必要になる可能性がある点である。音楽、アラーム、通話、ナビゲーション、録音、音声通知などのバックグラウンド音声ユースケースでは、フォアグラウンドサービス type、権限、音声用途を見直す必要がある。

---

# 変更内容

公式文書上の変更点:
- Android 17 では音声フレームワークがバックグラウンドでの音声操作に制限を適用する。
- 対象 interaction には音声再生、オーディオフォーカス要求、音量変更 API が含まれる。
- 目的は、これらの変更がユーザーにより意図して開始されたものであることを保証すること。
- 一部の音声制限は全アプリに適用される。
- targetSdkVersion 37 以上のアプリでは制限がより厳格になる。
- targetSdkVersion 37 以上のアプリがバックグラウンドで音声とやり取りする場合、フォアグラウンドサービスが実行中である必要がある。
- さらに、フォアグラウンドサービスが WIU capabilities を持つ、またはアプリが正確なアラーム権限を持ち `USAGE_ALARM` 音声ストリームと interaction している、の一方または両方を満たす必要がある。

AOSP で未確認の点:
- Android 16 基準挙動におけるバックグラウンド音声再生 / focus / 音量 API の許可条件。
- Android 17 の全アプリ restriction と targetSdkVersion 37+ restriction の実装差分。
- targetSdkVersion 37 適用ゲートの実装箇所。
- バックグラウンド状態、フォアグラウンドサービス running、WIU capabilities の判定箇所。
- 正確なアラーム権限と `AudioAttributes.USAGE_ALARM` の組み合わせ判定。
- 制限違反時の挙動。例: 再生 blocked、focus denied、音量 API が無視される / exception / error code。
- Compat Change ID とデフォルト状態。

## 適用条件（Applicability）

公式文書の一次判断では、Android 17 上のバックグラウンドでの音声操作に一部全アプリ制限があり、targetSdkVersion 37 以上ではフォアグラウンドサービス + WIU / alarm 条件を伴う追加制限がある。AOSP タグが未取得で全アプリ部分と targetSdkVersion 37 部分の境界を確認できないため、確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

### OS アップデート時の挙動

- Android 17 にアップデートしただけで適用されるか: Conditional / 未確認
- targetSdkVersion に依存しない根拠: 公式文書は "Some audio restrictions apply to all apps" と述べている。ただし、どの API / 条件が全アプリに適用されるかは AOSP 未確認。
- Android 16 以前での挙動: 未確認。Android 17 タグとの明示的な比較ができないため、Android 16 source だけから platform 根拠として断定しない。

### targetSdkVersion 37 以上での挙動

- targetSdkVersion 37 以上で適用されるか: 公式文書上は Yes と読めるが、AOSP 適用ゲートは未確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: 未確認。公式文書は Android 17 挙動変更として説明しているため、Android 17 platform 挙動として扱う。
- opt-out / temporary override の有無: 未確認。公式抜粋には opt-out は示されていない。Compat framework による force enable / disable は未確認。

### その他の条件

- 端末/フォームファクター: 公式抜粋では条件なし。
- 権限: 正確なアラーム権限。フォアグラウンドサービス / WIU capabilities に関わる権限 / フォアグラウンドサービス type が関係する可能性。
- API 使用: 音声再生、オーディオフォーカス要求、音量変更 APIs、`AudioAttributes.USAGE_ALARM`。
- manifest attribute: フォアグラウンドサービス type、正確なアラーム権限 declaration が関係する可能性があるが、AOSP 未確認。
- コンポーネント境界: アプリプロセス、音声フレームワーク、AudioService / AudioManager、フォアグラウンドサービス状態、alarm 権限、プロセス/バックグラウンド状態にまたがる。

---

# AOSP 調査

## checkout 状態

根拠利用前に確認したコマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list 'android-17*'
```

Result:
- `frameworks-base` 作業ツリー: 調査時点で clean。
- From タグ: `android-16.0.0_r4` exists.
- To タグ: ローカルに `android-17*` タグなし。

根拠上の制約:
- Android 17 AOSP タグがローカルの `frameworks-base` に存在しないため、`git -C frameworks-base diff android-16.0.0_r4 <android-17-tag> -- ...` による明示的なタグ比較を実行できない。
- Repository rule に従い、Android 17 作業ツリーや推測によるソース根拠は採用しない。
- この制約により、AOSP-backed 結論は高信頼度にできない。

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
- Compat framework 定義ファイル内のバックグラウンド音声 / オーディオフォーカス / 音量 API / targetSdkVersion 37 関連 Change ID

## 確認したソース文脈

Android 17 AOSP タグがないため、ソース文脈は未レビュー。

| ファイル / シンボル | Android 16 基準挙動 | Android 17 挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| 未レビュー | 未レビュー | 未レビュー | Android 17 タグがないため、公式文書の記述を AOSP 差分で検証できない。 |

必須記入項目:
- 入口 / 呼び出し元: 未確認。想定される入口は `AudioTrack` / media 再生開始、`AudioManager.requestAudioFocus()`、音量変更 API、AudioService 適用、フォアグラウンドサービス / alarm 権限 check だが、AOSP 根拠としては未採用。
- Relevant class or service responsibility: 未確認。
- アプリ API またはシステムイベントから変更箇所までの実行時パス: 未確認。
- 除外した無関係なコードパス: Android 17 タグ不在のため、ソースパスの採否判断自体を保留。

## 差分解釈

| 確認した差分 | 解釈 | 挙動変更 との関係 | 信頼度 |
| --- | --- | --- | --- |
| Android 17 タグ間差分は利用不可 | ソース差分の種別はまだ分類できない | 公式文書のバックグラウンド音声 restriction、全アプリ / targetSdkVersion 37 分岐、FGS / WIU / 正確なアラーム / `USAGE_ALARM` 適用ゲートをソース差分で裏取りできていない | 低 |

必須分類:
- Added behavior: 未確認。公式文書上は制限追加または適用強化の可能性がある。
- Removed behavior: 未確認。
- Changed condition / gate: 未確認。targetSdkVersion 37、バックグラウンド状態、フォアグラウンドサービス、WIU、正確なアラーム、`USAGE_ALARM` の適用ゲートがある可能性は高いが、AOSP 未確認。
- Changed default: 未確認。
- No behavior change found: 未確認。タグ不在のため「no behavior change」とは判断しない。

## 事実

事実:
- 公式 Behavior Change 文書は、Android 17 から音声フレームワークがバックグラウンドでの音声操作に制限を適用すると述べている。
- 公式文書は、対象に 音声再生、オーディオフォーカス要求、音量変更 API が含まれると述べている。
- 公式文書は、一部の音声制限が全アプリに適用されると述べている。
- 公式文書は、targetSdkVersion 37 以上のアプリでは制限がより厳格になると述べている。
- 公式文書は、targetSdkVersion 37 以上のバックグラウンドでの音声操作にはフォアグラウンドサービス running が必要と述べている。
- 公式文書は、追加条件としてフォアグラウンドサービスの WIU capabilities、または正確なアラーム権限 + `USAGE_ALARM` 音声ストリームの一方または両方を満たす必要があると述べている。
- ローカルの `frameworks-base` には `android-16.0.0_r4` タグがある。
- ローカルの `frameworks-base` には `android-17*` タグがない。
- 調査時点で `frameworks-base` 作業ツリーは clean。

観察:
- 公式ページ種別は targetSdkVersion 37 以上向けであるが、原文には全アプリに適用される制限も含まれている。
- この項目は targetSdkVersion 37 条件に加えて、バックグラウンド状態、音声 API 使用、フォアグラウンドサービス running、WIU capabilities、正確なアラーム権限、`USAGE_ALARM` という複数の実行時 / 権限条件を含む。
- 全アプリ制限と targetSdkVersion 37 以上の追加制限が混在するため、AOSP 適用ゲートなしに `TARGET_SDK_37_CONDITIONAL` と確定するのは危険である。
- AOSP タグがないため、実装がどの条件で targetSdkVersion 37 適用ゲートを使うかは未確認。
- Compat framework エントリの有無も未確認。

仮説:
- Android 17 / targetSdkVersion 37 以上では、バックグラウンドで音声再生、オーディオフォーカス要求、音量変更 API を使うアプリがフォアグラウンドサービスを持たない場合、操作が拒否される可能性が高い。
- フォアグラウンドサービスが実行中でも WIU capabilities がない場合、alarm ユースケース以外では拒否される可能性があるが、AOSP 未確認のため断定しない。
- 正確なアラーム権限 + `USAGE_ALARM` は alarm アプリの例外経路として機能する可能性がある。

結論:
- 現時点で顧客向けに確定できるのは、「公式文書上は Android 17 でバックグラウンドでの音声操作が hardening され、targetSdkVersion 37 以上ではフォアグラウンドサービス + WIU または正確なアラーム + `USAGE_ALARM` 条件が必要になる」という範囲まで。
- 全アプリ制限の範囲、targetSdkVersion 37 適用ゲート、失敗時の挙動、Compat framework デフォルト状態が未確認のため、主分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

## 適用ゲート根拠

- targetSdkVersion 適用ゲート: 未確認。公式文書は targetSdkVersion 37 以上で制限がより厳格と述べるが、AOSP 適用ゲート根拠はない。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。Android 17 タグがないため検索未実施。
- @EnabledAfter / @EnabledSince / デフォルト状態: 未確認。Android 17 タグがないため検索未実施。
- Build.VERSION / SDK_INT 適用ゲート: 未確認。
- DeviceConfig / resources 設定: 未確認。
- 権限/AppOps 適用ゲート: 未確認。公式文書上は正確なアラーム権限、フォアグラウンドサービス / WIU capability が条件だが、AOSP の権限 / AppOps パスは未確認。
- Manifest/property 適用ゲート: フォアグラウンドサービス type、正確なアラーム権限 declaration が関係する可能性はあるが、AOSP 根拠は未確認。
- 適用ゲート未検出: 未確認。Android 17 タグがないため「適用ゲートがない」とは判断しない。
- 適用ゲートの結論: 未確認。公式文書の wording から全アプリ制限 + targetSdkVersion 37 conditional hardening と推定されるが、AOSP で検証できていない。
- ソース文脈からの推論: ソース文脈未レビューのため未確定。

---

# 影響分析

## 影響を受けるアプリ

影響を受ける可能性があるアプリ:
- バックグラウンドで音声再生を開始または継続するアプリ。
- バックグラウンドで `AudioManager.requestAudioFocus()` を呼ぶアプリ。
- バックグラウンドで音量変更 API を使うアプリ。
- フォアグラウンドサービスなし、または WIU capabilities なしでバックグラウンドでの音声操作を行うアプリ。
- alarm 音を扱うが、正確なアラーム権限や `AudioAttributes.USAGE_ALARM` の利用が不十分なアプリ。
- targetSdkVersion 37 への更新を予定している音楽、ポッドキャスト、アラーム、通話、ナビゲーション、録音、音声通知系アプリ。

## 影響を受けにくいアプリ

影響が限定的または対象外と考えられるケース:
- バックグラウンドでの音声操作を行わないアプリ。
- audio 操作がフォアグラウンド UI からのみ開始されるアプリ。
- バックグラウンドでの音声操作時に適切なフォアグラウンドサービスと WIU capabilities を満たすアプリ。
- alarm ユースケースで正確なアラーム権限と `USAGE_ALARM` 音声ストリーム条件を満たすアプリ。
- Android 17 AOSP タグ取得後に対象外適用ゲートや exemption が確認されたケース。

---

# 顧客影響

顧客説明用。

## 影響度

- Human decision required

※ 仮評価。最終判断は人間が行う。

## ビジネス影響

- ユーザー影響: バックグラウンドでの再生開始、アラーム音、通知音、音量変更、オーディオフォーカス獲得が失敗すると、音声機能の信頼性が下がる可能性がある。
- 運用影響: audio ユースケースごとにフォアグラウンドサービス、WIU capability、正確なアラーム権限、音声用途の組み合わせを確認する必要がある可能性がある。
- 開発影響: バックグラウンド音声操作の起点をユーザー操作へ寄せ、FGS type / 権限 / `AudioAttributes` / エラーハンドリング / targetSdkVersion 37 テストを見直す必要がある可能性がある。

---

# サービス影響例

このセクションは、公式文書と AOSP 根拠から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1: 音楽 / ポッドキャスト再生アプリ

- 対象サービス例: 音楽 streaming、podcast、radio、meditation audio。
- 影響を受ける実装パターン: バックグラウンドから再生 start / オーディオフォーカス要求を行うが、実行中の FGS や WIU capability を満たさない実装。
- 発生条件: Android 17 / targetSdkVersion 37 でバックグラウンドでの音声操作が厳格化される場合。
- ユーザーに見える症状: 再生開始に失敗する、通知操作後に音が出ない、focus が取れない可能性。
- 開発・運用への影響: FGS type、ユーザー起点のフロー、オーディオフォーカス handling、テレメトリの見直しが必要になる可能性。
- 推奨対応候補: バックグラウンド音声を適切なフォアグラウンドサービスとユーザーに見える制御に紐づける。
- 根拠: 公式文書の記述とレポートの期待される挙動。
- 信頼度: 低
- 注意: 全アプリ制限と targetSdkVersion 37 制限の境界は未確認。

## 例2: アラーム / リマインダーアプリ

- 対象サービス例: アラーム、服薬リマインダー、タイマー、カレンダー通知。
- 影響を受ける実装パターン: バックグラウンドで alarm sound を鳴らすが、正確なアラーム権限や `USAGE_ALARM` を満たしていない実装。
- 発生条件: targetSdkVersion 37 で正確なアラーム + `USAGE_ALARM` 条件が必要になる場合。
- ユーザーに見える症状: アラーム音が鳴らない、音量変更が効かない、通知だけ表示される可能性。
- 開発・運用への影響: 正確なアラーム権限 UX、AudioAttributes、FGS / WIU capability の見直しが必要になる可能性。
- 推奨対応候補: alarm ユースケースを `USAGE_ALARM` と正確なアラーム権限に整合させる。
- 根拠: 公式文書の記述とレポートの対応候補。
- 信頼度: 低
- 注意: 実際の失敗時の挙動は AOSP タグ / 実機検証待ち。

---

# 対応候補

## 必須対応（Must）

- バックグラウンドで音声再生、オーディオフォーカス要求、音量変更 API を使う箇所を棚卸しする。
- targetSdkVersion 37 でバックグラウンドでの音声操作を行う必要がある場合、フォアグラウンドサービスが実行中であることを確認する。
- フォアグラウンドサービスが WIU capabilities を満たすか、alarm ユースケースでは正確なアラーム権限と `USAGE_ALARM` を満たすか確認する。
- 音声 API の失敗 / denied / 無視されるケースを前提に、エラーハンドリングと fallback UX を確認する。
- Android 17 / targetSdkVersion 37 のテスト環境が利用可能になったら、フォアグラウンド / バックグラウンド、FGS あり / なし、WIU あり / なし、alarm 条件 あり / なしを分けて検証する。
- Android 17 AOSP タグ入手後に、全アプリ制限、targetSdkVersion 37 適用ゲート、失敗時の挙動、Compat Change ID を再確認する。

## 推奨対応（Recommended）

- バックグラウンドからの audio 操作を、通知 action、表示中 UI、ユーザー起点のフローへ寄せる。
- alarm アプリは正確なアラーム権限と `AudioAttributes.USAGE_ALARM` の利用を明確にし、通常の media / 通知用途と混在させない。
- オーディオフォーカスと音量変更 API の呼び出しにテレメトリを追加し、Android 17 での拒否や失敗を検出できるようにする。
- バックグラウンド音声の制限強化の詳細ページで mitigation strategies を確認する。

## 任意対応（Optional）

- 音声系機能をユースケース別に分類し、media 再生、alarm、call、navigation、accessibility 的 audio feedback の権限・FGS 要件を整理する。
- Android 17 タグ入手後に CTS / 実機ログで AudioService の rejection reason を確認する。

---

# 検証方法

## 検証マトリクス

| 端末 OS | targetSdkVersion | Compat flag | 期待される挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | デフォルト | Android 16 基準挙動。バックグラウンドでの音声操作の具体挙動は Android 17 タグ比較待ち。 |
| Android 17 | 36 | デフォルト | 未確認。一部全アプリ制限があると公式文書は述べるが、範囲と適用ゲートは未確認。 |
| Android 17 | 37 | デフォルト | 公式文書上、バックグラウンドでの音声操作には running フォアグラウンドサービスと WIU capability または正確なアラーム + `USAGE_ALARM` 条件が必要。 |
| Android 17 | 36 | force-enabled（利用可能な場合） | 未確認。Compat Change ID 未確認。 |
| Android 17 | 37 | force-disabled（利用可能な場合） | 未確認。Compat Change ID 未確認。 |

## 手順

- targetSdkVersion 変更: targetSdkVersion 36 と 37 のテストビルドを用意する。
- Compat framework コマンド: 未確認。Android 17 Compat framework エントリ / Change ID が判明後に記録する。
- テスト方法: バックグラウンド / フォアグラウンド、FGS あり / なし、WIU capability あり / なし、正確なアラーム権限あり / なし、`USAGE_ALARM` / non-alarm 使用を組み合わせて、音声再生、オーディオフォーカス、音量 API を実行する。
- 再現手順: Android 17 端末 / emulator で対象アプリをインストールし、アプリをバックグラウンドにした状態で音声 API を呼び出す。API return value、exception、システム log、実際の音声出力、focus 状態を記録する。
- 期待結果: targetSdkVersion 37 のバックグラウンドでの音声操作は、公式文書の条件を満たさない場合に制限される。具体的な失敗時の挙動は AOSP タグと実機検証待ち。

---

# 結論

公式文書上、Android 17 ではバックグラウンドでの音声操作が hardening され、targetSdkVersion 37 以上のアプリではバックグラウンドで音声とやり取りするために running フォアグラウンドサービスと WIU capability、または正確なアラーム権限 + `USAGE_ALARM` 条件が必要になる。

ただし、Android 17 AOSP タグがローカル checkout にないため、全アプリ制限の範囲、targetSdkVersion 37 適用ゲート、失敗時の挙動、Compat framework の確認は未完了である。最終的な適用分類と顧客向け確定説明は、Android 17 AOSP タグ入手後に再調査が必要である。

---

# 人間の判断欄

最終優先度（Final Priority）:
- Human decision required

最終影響度（Final Severity）:
- Human decision required

リリース判断（Release Readiness）:
- Human decision required

顧客通知優先度（Customer Communication Priority）:
- Human decision required

判断（Decision）:
- 追加調査が必要

判断メモ:
- Android 17 AOSP タグ入手後に、AOSP 根拠と Compat framework 根拠を確認してから最終判断する。

---

# 参照（References）

## ドキュメント

- https://developer.android.com/about/versions/17/behavior-changes-17
- https://developer.android.com/develop/background-work/services/alarms#exact
- https://developer.android.com/reference/android/media/AudioAttributes#USAGE_ALARM
- https://developer.android.com/about/versions/17/changes/bg-audio

## AOSP

- ローカルの `frameworks-base` では Android 17 は利用不可。
- From タグ checked: `android-16.0.0_r4`
- To タグ checked: ローカルに `android-17*` タグなし。

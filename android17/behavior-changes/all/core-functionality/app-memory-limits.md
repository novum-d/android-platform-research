# アプリのメモリ上限

## 基本情報（Metadata）

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
- https://developer.android.com/about/versions/17/behavior-changes-all

Related documents:
- https://developer.android.com/topic/performance/memory
- https://developer.android.com/tools/adb
- https://developer.android.com/tools/dumpsys#uid_stats
- https://developer.android.com/reference/android/app/ApplicationExitInfo
- https://developer.android.com/reference/android/app/ApplicationExitInfo#getDescription%28%29
- https://developer.android.com/reference/android/app/ApplicationExitInfo#REASON_OTHER
- https://developer.android.com/topic/performance/tracing/profiling-manager/trigger-based-capture
- https://developer.android.com/about/versions/17/features#anomaly-profiling-trigger

Section:
- アプリのメモリ上限

Page type:
- Behavior changes: 全アプリ

### 分類スナップショット

主分類（Primary classification）:
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- 公式文書は Android 17 の `Behavior changes: all apps` ページにこの項目を掲載しているため、一次判断では `OS_UPDATE_ALL_APPS` 候補である。
- ただし、ローカルの `frameworks-base` に Android 17 AOSP タグがないため、メモリリミッターの実装、targetSdkVersion 適用ゲートの有無、対象端末条件の適用ゲート、DeviceConfig / resource 設定、Compat framework の default state は未確認である。
- 公式文書は「一部の Android 端末のみでメモリ上限が課される」と明記しているため、OS アップデートによる影響であっても、端末条件付きの挙動として扱う必要がある。

早見表:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 可能性あり / 条件付き。ただし未検証 | `behavior-changes-all` ページに掲載。公式文書は全アプリ対象ページであるが、AOSP 適用ゲートは未確認。 |
| targetSdkVersion 37 以上が必要か | 公式文書上は不要と読めるが、AOSP では未確認 | 全アプリ向けページの説明から targetSdkVersion 非依存と読むのが自然。ただし AOSP の targetSdkVersion 適用ゲートは未確認。 |
| 追加の実行時条件があるか | あり | 公式文書は、メモリ上限が一部の Android 端末のみに課されると説明している。 |
| Compat Change ID が関係するか | 未確認 | Android 17 タグと Compat framework の根拠が未確認。 |

### 調査日（Investigation Date）

2026-06-15

### 信頼度

- 低

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] Android 17 上の全アプリ（targetSdkVersion に依存しない）
- [ ] Android 17 以上で targetSdkVersion >= 37
- [ ] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [x] 未確認 / 追加根拠が必要

必要な実行時条件:
- Android バージョン: Android 17 であることが前提。Android 17 AOSP タグ未取得のため、実装上の OS 適用ゲートは未確認。
- targetSdkVersion: 公式文書上は targetSdkVersion に依存しない全アプリ向け変更と読める。AOSP 適用ゲートは未確認。
- 端末/フォームファクター: 一部の Android 端末のみ。端末の総 RAM 容量、対象端末条件、設定 / DeviceConfig 条件は AOSP タグ待ち。
- 権限/API/コンポーネント条件: アプリが制限値を超えるメモリ使用量、特に極端なメモリリーク / 外れ値に該当する場合に影響が顕在化する。
- アプリ状態/プロセス条件: 表示中 / 非表示プロセス別の上限が存在する可能性があると、公式テストコマンドの `status` 説明から読めるが、実装は未確認。

Compat framework:
- Change ID: 未確認
- 変更名: 未確認
- default state: 未確認
- テスト時の切り替え可否: 公式文書は compat flag ではなく、`am memory-limiter` コマンドによるテスト制御を説明している。Compat framework エントリは未確認。

分類信頼度:
- 低

分類根拠:
- Official documentation page: `behavior-changes-all`
- 検証対象の適用条件文: Android 17 の全アプリ向けページは、この変更が targetSdkVersion に関係なく Android 17 上の全アプリに適用されると説明している。
- AOSP targetSdk 適用ゲート: 未確認。ローカルの `frameworks-base` に `android-17*` タグがない。
- Compat framework エントリ: 未確認。Android 17 Compat framework の根拠が未取得。

---

# エグゼクティブサマリー

Android 17 では、端末の総 RAM 容量に基づくアプリのメモリ上限が導入される。公式文書は、極端なメモリリークや外れ値が、システム全体の不安定化、UI のカクつき、バッテリー消費、アプリの強制終了につながる前に制御することを目的としている、と説明している。

この項目は Android 17 の全アプリ向けページに掲載されているため、targetSdkVersion 37 への更新有無に関係なく Android 17 上で影響する可能性がある。ただし、公式文書はメモリ上限が一部の Android 端末のみに課されると説明しているため、全端末で必ず発生する変更ではない。

現時点ではローカルの `frameworks-base` に Android 17 AOSP タグがないため、メモリリミッターの実装、対象端末条件、targetSdkVersion 適用ゲートの不存在、Compat framework エントリは未確認である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とし、Android 17 AOSP タグ公開後に再調査する。

---

# 公式ドキュメント確認

## 原文（Statement）

Page title:
- Behavior changes: 全アプリ

Page URL:
- https://developer.android.com/about/versions/17/behavior-changes-all

Page type:
- 全アプリ

Section title:
- アプリのメモリ上限

検証対象の原文:
- Android 17 では、端末の総 RAM 容量に基づくアプリのメモリ上限が導入される。
- この上限は、アプリと Android ユーザーにとってより安定し、予測しやすい環境を作ることを目的としている。
- 主な対象は、システム全体の不安定化を引き起こす前の極端なメモリリークやメモリ外れ値である。
- メモリ上限は、一部の Android 端末にのみ課される。
- 影響を受けたセッションは、`ApplicationExitInfo.getDescription()` に `MemoryLimiter:AnonSwap` が含まれ、終了理由が `REASON_OTHER` になることで診断できる。
- `TRIGGER_TYPE_ANOMALY` によるトリガーベースのプロファイリングで、上限到達時のヒープダンプを取得できる。

検証サブセクションの原文:
- `Test your app's behavior under the memory constraints` は `App memory limits` 配下の検証サブセクションであり、別の挙動変更ではない。
- 開発者は ADB とシェルコマンド `am` を使い、メモリ上限を課す端末上でメモリ上限を調整または無効化できる。
- `am memory-limiter` のサブコマンドは、`ignore <uid>|none|all`、`manual <pid> <limit>|max|none`、`status` である。
- これらのコマンドは、メモリ上限を課さない端末では効果がない。
- `ignore <uid>` は、その UID に関連付けられたすべてのプロセスで適用を無視する。`all` は全アプリを無視し、`none` は以前の ignore 設定を解除する。
- UID を `ignore` していても、同じアプリ内のプロセスには `manual` でメモリ上限を適用できる。
- `manual <pid> <limit>` は、指定したプロセスに MB 単位のメモリ制約を課す。`max` はそのプロセスの全メモリ上限を削除し、`none` は手動上限を解除してシステムデフォルトの上限があれば復元する。
- `status` は、表示中 / 非表示プロセスに課される上限を含む、現在のメモリリミッター状態を報告する。

## 解釈

公式文書は、この変更を Android 17 上で動作する全アプリ向けの挙動変更として掲載している。したがって一次判断では、targetSdkVersion 37 化ではなく Android 17 OS アップデート側の影響候補である。

ただし、適用は「一部の Android 端末」のみに限定される。顧客説明では「Android 17 で全アプリが対象になり得る」ことと、「全端末 / 全セッションで必ずメモリ上限による強制終了が発生するわけではない」ことを分けて説明する必要がある。

アプリ側で観測できるシグナルは、`ApplicationExitInfo.getDescription()` 内の `MemoryLimiter:AnonSwap` と `REASON_OTHER` である。公式文書は、開発・検証では `am memory-limiter` サブコマンドにより、制限の無視、手動上限、状態確認を行えると説明している。

`Test your app's behavior under the memory constraints` は、挙動変更本体ではなく検証手段の説明である。したがって分類を別項目として分けず、`App memory limits` の検証方法として扱う。顧客向けには、`am memory-limiter` は本番での緩和策ではなく、対象端末上でメモリリミッターの有無・手動上限・無視状態を切り替えて挙動を確認するための開発 / QA 手段として説明する。

---

# 変更内容

公式文書上の変更点:
- Android 17 で、端末の総 RAM 容量に基づくアプリのメモリ上限が導入される。
- 制限値は Android 17 では保守的に設定され、システムの基準挙動を作る目的と説明されている。
- 主な対象は極端なメモリリークやメモリ外れ値である。
- 問題がシステム全体の不安定化、UI のカクつき、バッテリー消費、アプリの強制終了につながる前に制御することが目的である。
- 影響を受けたアプリセッションは `ApplicationExitInfo` で診断できる。
- `am memory-limiter` コマンドでテスト制御が提供される。
- `am memory-limiter` コマンドは、メモリ上限を課す端末上でのみ効果を持つ。メモリ上限を課さない端末では効果がない。
- `ignore` は UID 単位または全アプリ単位で適用を無視させる。
- `manual` は PID 単位で MB 指定のメモリ制約を課す。
- `status` は表示中 / 非表示プロセスに課されるメモリ上限状態を報告する。

AOSP で未確認の点:
- メモリリミッターの実装ファイル、service / daemon / LMKD との関係。
- 上限がどのプロセス状態、UID、cgroup、匿名スワップ計測、表示中 / 非表示プロセスに適用されるか。
- 端末の総 RAM 容量から上限を算出する具体式。
- 一部端末の判定条件。
- targetSdkVersion 適用ゲートが本当に存在しないか。
- Compat framework Change ID の有無。

## 適用条件（Applicability）

この変更がいつ適用されるかを OS 条件と targetSdkVersion 条件に分けて説明する。

### OS アップデート時の挙動

- Android 17 にアップデートしただけで適用されるか: 公式文書上は Yes / Conditional。`behavior-changes-all` ページに掲載されているため、targetSdkVersion に依存しない全アプリ向け変更と読む。
- targetSdkVersion に依存しない根拠: 公式ページ全体が「Android 17 上で動作する全アプリに適用される」と説明している。
- Android 16 以前での挙動: この挙動変更としてのアプリのメモリ上限は、公式文書上 Android 17 で導入されたと説明されている。AOSP 基準挙動の実装差分は未確認。

### targetSdkVersion 37 以上での挙動

- targetSdkVersion 37 以上で適用されるか: 公式文書上、targetSdkVersion 37 は必要条件として示されていない。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: 未確認。公式文書は Android 17 全アプリ向け変更として説明しているため、Android 17 platform / 端末条件が前提と考えられる。
- opt-out / temporary override の有無: compat opt-out は未確認。公式文書は `am memory-limiter ignore <uid>|none|all` と手動上限によるテスト制御を説明している。

### その他の条件

- 端末/フォームファクター: 一部の Android 端末のみ。端末の総 RAM 容量と対象端末条件が関係する。
- 権限: 公式文書からは特定の権限条件は確認できない。
- API 使用: 診断には `ApplicationExitInfo.getDescription()`、`ApplicationExitInfo.REASON_OTHER`、トリガーベースのプロファイリング / `TRIGGER_TYPE_ANOMALY` が関連する。
- manifest attribute: 公式文書からは確認できない。
- コンポーネント境界: プロセス / UID 単位で制限される可能性がある。`am memory-limiter ignore <uid>` と `manual <pid>` から UID / PID 境界のテスト制御があることは読み取れるが、実装境界は AOSP タグ待ち。

---

# AOSP 調査

## checkout 状態

確認コマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list 'android-16.0.0_r4'
git -C frameworks-base tag --list 'android-17*'
```

結果:
- `frameworks-base` の `status --short` は空で、dirty な作業ツリーは確認されなかった。
- `android-16.0.0_r4` タグは存在する。
- `android-17*` タグはローカル checkout に存在しない。

根拠上の制約:
- Android 17 AOSP タグがローカルの `frameworks-base` にないため、`android-16.0.0_r4` と Android 17 タグの明示的なソース差分は実行できない。
- そのため、ローカル作業ツリーや未確定 branch を platform 根拠として扱わない。
- 本レポートの AOSP に基づく結論は低信頼度に留める。

## 関連ファイル

Android 17 AOSP タグ未取得のため、タグ間差分に基づく関連ファイルは未確定。

Android 17 タグ 公開後に確認すべき候補:
- `services/core/java/com/android/server/am/` 以下のプロセス / メモリ management パス
- `services/core/java/com/android/server/` 以下のメモリリミッターコマンド / シェルコマンド実装
- `cmds/am/` または ActivityManager シェルコマンドの `memory-limiter` サブコマンド
- UID / PID lookup、シェル権限、呼び出し元権限、ユーザー境界を扱うコマンドパス
- LMKD / ProcessList / OOM adjustment / cgroup / memory pressure 関連パス
- `core/java/android/app/ApplicationExitInfo.java`
- トリガーベースのプロファイリング / `ProfilingManager` / anomaly trigger 関連 API surface

## 確認したソース文脈

AOSP タグ間差分は未実行。以下は公式文書から見た確認予定のソース文脈であり、AOSP 根拠ではない。

| ファイル / シンボル | Android 16 の基準挙動 | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| ActivityManager / プロセスメモリ management パス | 未確認 | 端末の総 RAM 容量に基づくアプリのメモリ上限の適用が存在する可能性 | アプリプロセスにメモリ上限を課す中心パスと考えられる |
| ActivityManager シェルコマンド `am memory-limiter` | 未確認 | `ignore` / `manual` / `status` サブコマンドが提供されると公式文書が説明 | 開発者向けテスト制御の実装起点になる可能性 |
| UID / PID コマンド handling | 未確認 | `ignore` は UID、`manual` は PID を受け取ると公式文書が説明 | アプリ全体の無視とプロセス単位の手動上限の境界を確認するため |
| 表示中 / 非表示プロセス状態の報告 | 未確認 | `status` が表示中 / 非表示プロセス上限を報告すると公式文書が説明 | プロセス状態ごとの上限が存在するかを確認するため |
| `ApplicationExitInfo.getDescription()` / `REASON_OTHER` | 未確認 | メモリリミッター影響時に `MemoryLimiter:AnonSwap` を含む説明を返すと公式文書が説明 | アプリ開発者が影響を観測する public API |
| トリガーベースのプロファイリング / `TRIGGER_TYPE_ANOMALY` | 未確認 | メモリ上限到達時のヒープダンプ収集に使えると公式文書が説明 | メモリ上限到達時の診断パス |

必須記入項目:
- 入口 / 呼び出し元: 未確認。Android 17 タグ公開後に、`adb shell am memory-limiter ...` -> ActivityManager シェルコマンド -> メモリリミッターサービス / コントローラーのコマンドパス、プロセスメモリ計測 / 強制終了パス、`ApplicationExitInfo` 記録パスを確認する。
- Relevant class or service responsibility: プロセスメモリ上限の適用、終了 reason / 説明の記録、開発者 diagnostics。
- アプリ API またはシステムイベントから変更箇所までの実行時パス: アプリプロセスのメモリ使用量が上限を超える -> システムメモリリミッターが適用 -> プロセス終了 / 記録 -> アプリが後続起動時に `ApplicationExitInfo` から診断、というパスが想定される。検証パスとしては、`adb shell am memory-limiter status` で対象端末 / 現在の上限を確認し、`adb shell am memory-limiter manual <pid> <limit>` でプロセス単位の手動上限を設定する。
- 除外した無関係なコードパス: タグ間差分未実行のため、除外判断は未完了。

## 差分解釈

| 確認した差分 | 解釈 | 挙動変更との関係 | 信頼度 |
| --- | --- | --- | --- |
| Android 17 タグ未取得のためソース差分は未確認 | 公式文書上は、追加された挙動 / 変更された条件と読める | アプリのメモリ上限の新規導入、一部端末条件、diagnostic シグナルが説明されている | 低 |

必須分類:
- Added behavior: 公式文書上、Android 17 でアプリのメモリ上限が導入される。
- Removed behavior: 未確認。
- Changed condition / gate: 公式文書上、一部端末でのみ課される。AOSP 適用ゲートは未確認。
- Changed default: 未確認。Android 17 の platform default として有効になる可能性があるが、端末 / 設定 default は AOSP タグ待ち。
- No behavior change found: 未確認。

## 事実（根拠）

事実:
- 公式文書は `App memory limits` を Android 17 `Behavior changes: all apps` ページに掲載している。
- 公式文書は、Android 17 が端末の総 RAM 容量に基づくアプリのメモリ上限を導入すると説明している。
- 公式文書は、上限が conservative に設定され、システムの基準挙動を作る目的だと説明している。
- 公式文書は、対象を極端なメモリリークとメモリ外れ値と説明している。
- 公式文書は、メモリ上限が一部の Android 端末のみに課されると説明している。
- 公式文書は、影響を受けたセッションの終了 reason が `REASON_OTHER` になり、説明に `MemoryLimiter:AnonSwap` が含まれると説明している。
- 公式文書は、`TRIGGER_TYPE_ANOMALY` によるトリガーベースのプロファイリングを診断手段として挙げている。
- 公式文書は、`am memory-limiter ignore`、`manual`、`status` をテストコマンドとして挙げている。
- 公式文書は、`am memory-limiter` コマンドが、メモリ上限を課さない端末では効果を持たないと説明している。
- 公式文書は、`ignore <uid>` がその UID に属する全プロセスの適用を無視し、`all` が全アプリ、`none` が以前の無視設定解除を意味すると説明している。
- 公式文書は、UID を `ignore` していても、同じアプリ内プロセスには `manual` メモリ上限を適用できると説明している。
- 公式文書は、`manual <pid> <limit>` が PID 単位で MB 指定のメモリ制約を課し、`max` がすべてのメモリ上限を削除し、`none` が手動上限を解除してシステム default の上限があれば復元すると説明している。
- 公式文書は、`status` が表示中 / 非表示プロセスに課されるメモリ上限を含む現在の状態を報告すると説明している。

観察:
- 全アプリ向けページに掲載されているため、一次分類は `OS_UPDATE_ALL_APPS` 候補である。
- 一部端末条件があるため、顧客向けには「Android 17 全アプリ対象候補」かつ「対象端末条件付き」と説明する必要がある。
- テストコマンドは Compat framework ではなく ActivityManager シェルコマンドとして提供される可能性がある。
- `ignore` と `manual` の UID / PID の分かれ方から、アプリレベルの無視とプロセスレベルの手動上限は別の制御面として扱われる可能性がある。
- `status` が表示中 / 非表示プロセスの上限を報告することから、プロセス状態ごとの上限が存在する可能性がある。

仮説:
- 適用は targetSdkVersion 37 適用ゲートではなく、Android 17 platform / 端末設定 / プロセス状態 / メモリ使用量により制御される可能性が高い。
- 表示中 / 非表示プロセスに異なる上限がある可能性がある。
- `MemoryLimiter:AnonSwap` は、匿名スワップ使用またはメモリ計測に基づく適用 reason を示している可能性がある。
- `am memory-limiter` サブコマンドは、シェル / ADB 経由の開発者向けテストフックであり、通常のアプリ本番での緩和策ではない可能性が高い。

結論:
- 現時点の確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE`。公式文書上は `OS_UPDATE_ALL_APPS` 候補だが、AOSP タグ未取得のため高信頼度にはできない。

## 適用ゲート根拠

- targetSdkVersion 適用ゲート: 未確認。公式文書上は targetSdkVersion 条件なし。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。
- @EnabledAfter / @EnabledSince / default state: 未確認。
- Build.VERSION / SDK_INT 適用ゲート: 未確認。公式文書上は Android 17 で導入された変更である。
- DeviceConfig / resources 設定: 未確認。一部端末のみという条件から、端末設定 / resource 設定 / 機能フラグが存在する可能性がある。
- 権限/AppOps 適用ゲート: 公式文書からは確認できない。
- Manifest/property 適用ゲート: 公式文書からは確認できない。
- 適用ゲート未検出: 未確認。AOSP タグ未取得のため、適用ゲートの検索は未実行。
- 適用ゲートの結論: 公式文書上は Android 17 全アプリ + 一部端末条件。AOSP 根拠未取得のため `UNKNOWN_NEEDS_MORE_EVIDENCE`。
- ソース文脈からの推論: ソース文脈は未確認。公式文書の page type と statement のみから一次判断している。

---

# 影響分析

## 影響を受けるアプリ

- Android 17 上で動作するアプリ。
- 対象となる一部端末上で実行されるアプリ。
- 極端なメモリリーク、大きな匿名メモリ使用量、メモリ外れ値があるアプリ。
- 長時間稼働、画像 / 動画処理、ML inference、大量キャッシュ、WebView / ネイティブヒープ / ビットマップなどでメモリ使用量が増えやすいアプリ。
- バックグラウンドプロセスや非表示プロセスでメモリを保持し続けるアプリ。

## 影響を受けないアプリ

- Android 17 以外の端末上で動作する場合。
- メモリ上限が課されない端末上で動作する場合。
- メモリ基準値が安定しており、極端なリーク / 外れ値がない場合。
- メモリ上限に達していないアプリセッション。
- ただし、AOSP タグ未取得のため、正確な影響対象外条件は未確定。

---

# 顧客影響

顧客説明用。

## 影響度

- 要確認

※ 仮評価。最終判断は人間が行う。

## ビジネス影響

- ユーザー影響: メモリ上限に達したセッションではアプリプロセスが終了し、ユーザーにはアプリ再起動、作業中断、状態消失として見える可能性がある。
- 運用影響: クラッシュ報告だけでは通常のクラッシュとして分類されない可能性があるため、`ApplicationExitInfo` と終了説明の収集が必要になる。
- 開発影響: メモリ基準値、リーク検出、ヒープダンプ、大きなキャッシュ / ネイティブヒープ / ビットマップ使用の見直しが必要になる。

---

# サービス影響例

このセクションは、公式文書と AOSP 根拠 から導いた「起こりうる影響例」を記録する。
特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: 画像 / 動画編集アプリ

- 対象サービス例: 画像加工、動画編集、メディア生成、大きなビットマップを扱うエディタ。
- 影響を受ける実装パターン: 高解像度画像、temporary ビットマップ、decoded frame、ネイティブ buffer を長時間保持する。
- 発生条件: Android 17、メモリリミッター対象端末、プロセスメモリが上限に到達する。
- ユーザーに見える症状: 編集中のアプリ再起動、作業中断、未保存状態の喪失。
- 開発・運用への影響: メモリ基準値測定、ビットマップ / ネイティブ buffer ライフサイクル、autosave / restore パスの確認が必要。
- 推奨対応候補: ヒープダンプ、トリガーベースのプロファイリング、大きな割り当てパスの棚卸し、`ApplicationExitInfo` 収集。
- 根拠: 公式文書は極端なメモリリーク / outliers を対象とし、`MemoryLimiter:AnonSwap` で診断可能と説明している。
- 信頼度: 低。AOSP 適用条件は未確認。
- 注意: 実サービスで発生確認した事実ではない。

## 例2（Example 2）: 長時間 バックグラウンド 同期 / キャッシュ 保持アプリ

- 対象サービス例: file sync、offline キャッシュ、document scanner、map / media キャッシュ。
- 影響を受ける実装パターン: バックグラウンドプロセスが大きなキャッシュ、queue、ネイティブヒープ、decoded data を保持し続ける。
- 発生条件: Android 17、メモリリミッター対象端末、表示中 / 非表示プロセスの上限に到達する。
- ユーザーに見える症状: バックグラウンド task の中断、次回起動時の同期や処理のやり直し。
- 開発・運用への影響: バックグラウンド work の checkpoint、idempotency、memory pressure handling の確認が必要。
- 推奨対応候補: WorkManager / フォアグラウンド work の状態復旧、キャッシュ削除、メモリリーク監視、`am memory-limiter manual` を使った再現試験。
- 根拠: 公式文書は、状態コマンドが表示中 / 非表示プロセスのメモリ上限を報告すると説明している。
- 信頼度: 低。プロセス状態別の適用は AOSP タグ待ち。
- 注意: 実サービスで発生確認した事実ではない。

---

# 対応候補

## 必須対応（Must）

- Android 17 対象端末でメモリ基準値を測定する。
- `ApplicationExitInfo` の取得・保存・分析パスを確認し、`REASON_OTHER` と `MemoryLimiter:AnonSwap` を検出できるようにする。
- メモリリーク / 大きな割り当て / unbounded キャッシュ / ネイティブヒープ growth の既知 issue を棚卸しする。
- アプリ再起動やプロセス終了に備えて、重要なユーザー状態の保存・復元を確認する。

## 推奨対応（Recommended）

- `am memory-limiter status` で対象端末のメモリリミッター状態を確認する。
- `am memory-limiter manual <pid> <limit>` を使い、メモリ上限到達時のアプリ挙動を再現する。
- `am memory-limiter ignore <uid>|none|all` を使い、メモリリミッター有無による差分を検証する。
- トリガーベースのプロファイリングで `TRIGGER_TYPE_ANOMALY` を設定し、上限到達時のヒープダンプを取得する。
- Android 開発者向けのメモリ best practices に沿ってメモリ使用量を最適化する。

## 任意対応（Optional）

- 大きなメモリを使う機能に対する機能フラグ / 段階的な機能低下を検討する。
- 端末 RAM class / メモリ class / low RAM 端末条件に応じたキャッシュサイズ調整を見直す。
- QA matrix に、メモリリミッター対象端末と非対象端末の比較を追加する。

---

# 検証方法

変更を確認する方法。

## 検証マトリクス

| 端末 OS | targetSdkVersion | Compat flag / テスト制御 | 期待挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | デフォルト | Android 17 のアプリメモリ上限は対象外。メモリの基準挙動を測定する。 |
| Android 17 | 36 | デフォルト | 公式文書上は全アプリ向け変更のため、対象端末ではメモリリミッターが適用される可能性がある。AOSP 適用ゲートは未確認。 |
| Android 17 | 37 | デフォルト | targetSdkVersion 36 と同様に、対象端末ではメモリリミッターが適用される可能性がある。 |
| Android 17 | 36 | `am memory-limiter manual <pid> <limit>` | 手動上限により、メモリ上限到達時のプロセス挙動を再現する。 |
| Android 17 | 37 | `am memory-limiter ignore <uid>` | メモリリミッターの ignore により、適用差分を確認する。 |

## `am memory-limiter` サブコマンド

| コマンド | 入力単位 | 目的 | 注意 |
| --- | --- | --- | --- |
| `am memory-limiter ignore <uid>` | UID | 指定 UID に属する全プロセスの適用を無視する | UID を `ignore` していても、同じアプリ内プロセスに `manual` 上限は適用できる |
| `am memory-limiter ignore all` | 全アプリ | 全アプリの適用を無視する | QA 中に system-wide に影響するため、検証後に戻す |
| `am memory-limiter ignore none` | none | 以前の無視設定を解除する | クリーンアップ |
| `am memory-limiter manual <pid> <limit>` | PID / MB | 指定プロセスに MB 単位のメモリ制約を課す | 例: `30` = 30MB |
| `am memory-limiter manual <pid> max` | PID | 指定プロセスの全メモリ上限を削除する | システム default との差分は AOSP タグ公開後に確認する |
| `am memory-limiter manual <pid> none` | PID | 手動上限を解除し、システム default の上限があれば復元する | default 上限の有無は対象端末依存 |
| `am memory-limiter status` | 端末状態 | メモリリミッターの現在状態を表示する | 表示中 / 非表示プロセス上限を含む |

## 手順（Steps）

- targetSdk 変更: targetSdkVersion 36 / 37 の両方で検証し、targetSdkVersion 差分ではなく OS / 端末 / メモリ条件の差分として観測されるか確認する。
- Compat framework コマンド: 公式文書上 compat flag は未確認。代わりに `am memory-limiter` コマンドを使う。
- テスト方法:
  - `am memory-limiter status`
  - `am memory-limiter manual <pid> <limit>|max|none`
  - `am memory-limiter ignore <uid>|none|all`
  - `ApplicationExitInfo.getDescription()` の収集
  - トリガーベースのプロファイリングで `TRIGGER_TYPE_ANOMALY`
- 再現手順:
  - Android 17 対象端末でアプリを起動する。
  - `am memory-limiter status` を実行し、その端末がメモリ上限を課しているか確認する。課さない端末ではコマンドは効果を持たない。
  - メモリ基準値を測定する。
  - 手動メモリ上限を設定する。
  - 必要に応じて `am memory-limiter ignore <uid>` / `am memory-limiter ignore none` で適用有無の差分を確認する。
  - 大きな割り当て / 既知のメモリ負荷が高いフローを実行する。
  - プロセス終了後、`ApplicationExitInfo` の reason / 説明を確認する。
- 期待結果:
  - 上限到達時にアプリセッションが影響を受ける。
  - 終了 reason は `REASON_OTHER`。
  - 説明に `MemoryLimiter:AnonSwap` が含まれる。
  - ヒープダンプ / プロファイリング artifact が取得できる場合、メモリ growth の原因を分析できる。

---

# 結論

アプリのメモリ上限は Android 17 全アプリ向けページに掲載されているため、targetSdkVersion 更新ではなく Android 17 OS アップデート側の影響候補である。ただし、一部端末のみで課される条件付き変更であり、AOSP タグ未取得のため確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

Android アプリ開発者は、Android 17 対応の一環として、メモリ基準値、リーク / 外れ値検出、`ApplicationExitInfo` による診断、`am memory-limiter` を使った再現検証を準備する必要がある。

---

# 人間の判断欄

最終優先度（Final Priority）:
- Human decision required

判断（Decision）:
- Android 17 AOSP タグが利用可能になった後に追加調査が必要

判断理由候補:
- 公式文書上は全アプリ向け変更だが、一部端末条件と AOSP 適用ゲート未確認が残っている。
- 顧客影響はメモリ使用量パターンに依存するため、実サービスのメモリ基準値とクラッシュ / 終了テレメトリを見て判断する必要がある。

---

# 参照（References）

## ドキュメント

- https://developer.android.com/about/versions/17/behavior-changes-all
- https://developer.android.com/topic/performance/memory
- https://developer.android.com/tools/adb
- https://developer.android.com/tools/dumpsys#uid_stats
- https://developer.android.com/reference/android/app/ApplicationExitInfo
- https://developer.android.com/reference/android/app/ApplicationExitInfo#getDescription%28%29
- https://developer.android.com/reference/android/app/ApplicationExitInfo#REASON_OTHER
- https://developer.android.com/topic/performance/tracing/profiling-manager/trigger-based-capture
- https://developer.android.com/about/versions/17/features#anomaly-profiling-trigger

## AOSP

- 未確認。ローカルの `frameworks-base` に Android 17 AOSP タグがないため、タグ間差分によるソース根拠は未取得。

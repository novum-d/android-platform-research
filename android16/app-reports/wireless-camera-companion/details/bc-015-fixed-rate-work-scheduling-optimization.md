# BC-015: 固定間隔処理のスケジューリング最適化（Fixed rate work scheduling optimization）

## 基本情報

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/16/behavior-changes-16#schedule-at-fixed-rate
- セクション: Fixed rate work scheduling optimization

既存調査:
- [android16/behavior-changes/target/core-functionality/fixed-rate-work-scheduling-optimization.md](../../../behavior-changes/target/core-functionality/fixed-rate-work-scheduling-optimization.md)
- [android16/summaries/target/core-functionality/fixed-rate-work-scheduling-optimization-summary.md](../../../summaries/target/core-functionality/fixed-rate-work-scheduling-optimization-summary.md)
- [android16/behavior-changes/target/core-functionality/fixed-rate-work-scheduling-optimization-implementation-examples.md](../../../behavior-changes/target/core-functionality/fixed-rate-work-scheduling-optimization-implementation-examples.md)

## 対象アプリとの関係

関連するアプリ機能:
- カメラ状態 / 接続状態の定期ポーリング。
- Bluetooth / Wi-Fi 接続の監視と再接続の試行。
- 画像 / 動画のメタデータ、サムネイル、転送状態の同期。
- セッション、一時ファイル、キャッシュの後処理。
- テレメトリ / メトリクスの送信。

アプリが該当する可能性:
- 条件付きで該当する。`ScheduledThreadPoolExecutor` / `ScheduledExecutorService` または `Timer` の `scheduleAtFixedRate` を使用し、凍結や一時停止などで実行できなかった周期分を、復帰後にまとめて実行する回数に依存している場合に影響する。
- WorkManager / JobScheduler / AlarmManager のみを使い、内部でも executor / Timer の `scheduleAtFixedRate` を併用していない場合は直接影響しない。

## 適用条件分類

主分類:
- `TARGET_SDK_36_CONDITIONAL`

必要条件:
- Android 16。
- targetSdkVersion 36 以上。
- `ScheduledThreadPoolExecutor#scheduleAtFixedRate`、`ScheduledExecutorService#scheduleAtFixedRate`、または `Timer#scheduleAtFixedRate` 利用。
- プロセスの凍結や CPU の一時停止などにより、fixed-rate の周期を複数回実行できないまま復帰する。

Confidence:
- High。

## OS アップデート影響と targetSdkVersion 影響

OS アップデート影響:
- Android 16 へ OS アップデートしただけでは、targetSdkVersion 35 以下のアプリに新しい挙動が既定で適用されるとは判断しない。

targetSdkVersion 影響:
- Android 16 / targetSdkVersion 36 では、復帰時に即時実行される `scheduleAtFixedRate` の未実行分は最大1回になる。
- 従来のように複数回分の未実行処理が連続実行されることを前提とした実装では、実行回数が減る。

## AOSP / 公式根拠

既存 Android16 調査で確認済み:
- executor 側 Compat Change ID は `STPE_SKIP_MULTIPLE_MISSED_PERIODIC_TASKS` / 288912692。
- Timer 側 AOSP Change ID は `SKIP_MULTIPLE_MISSED_PERIODIC_TASKS` / 351566728。
- AOSP libcore の両 Change ID には `@EnabledAfter(targetSdkVersion = VersionCodes.VANILLA_ICE_CREAM)` があり、targetSdkVersion 36 以上で既定で有効になる。
- `ScheduledFutureTask#setNextRunTime()` は、変更が有効な fixed-rate の処理について、次回時刻を最後に実行できなかった周期へ補正し、複数回分の未実行処理が連続実行されることを抑制する。
- `scheduleWithFixedDelay`、WorkManager、JobScheduler、AlarmManager は本件の直接対象ではない。`Timer#scheduleAtFixedRate` は別 Change ID 351566728 で同じ最適化の対象となる。

## アプリ影響

想定される影響:
- 復帰直後のカメラ状態のポーリング / 接続確認の回数が従来より減る。
- 再試行回数を実行できなかった周期数として扱う実装では、再接続や転送再開の試行回数が減る。
- 同期、後処理、メトリクス送信を実行回数に基づいて補う設計では、一部の周期分が処理されない。
- fixed-rate の処理が冪等でない場合、旧挙動と新挙動でデータ更新回数や副作用が変わる。

推奨対応:
- executor / Timer の `scheduleAtFixedRate` 利用箇所と、wrapper / third-party SDK 内での利用を棚卸しする。
- API は `@Deprecated` ではないが、Android Lint の `DiscouragedApi` は本 Behavior Change と同じ cached-process catch-up 問題を警告しているため、無関係として除外しない。
- カメラ状態のポーリング / 接続監視は、前回の実際の開始時刻を基準にしてよければ `Timer#schedule(..., period)`、前回の処理完了から一定間隔を空ける必要があれば `ScheduledExecutorService#scheduleWithFixedDelay` へ移行する。
- 実行できなかった周期数だけ処理する必要がある場合は、callback がまとめて呼ばれる回数に依存せず、最終成功時刻と現在時刻から必要な処理量を計算する。
- ポーリング、再試行、同期、後処理が、復帰直後に最大1回だけ実行される場合でも正しく収束するか確認する。
- WorkManager / JobScheduler / AlarmManager は、本件の等価な移行先として扱わない。プロセス終了後の再実行など、カメラのポーリングとは別のバックグラウンド処理要件がある場合に限って、別途設計する。
- Before / After、Timer、Java、テストコードは [Fixed rate work scheduling optimization - 実装例](../../../behavior-changes/target/core-functionality/fixed-rate-work-scheduling-optimization-implementation-examples.md) を参照する。

## テスト観点

- Android 16 / targetSdkVersion 35 / default。
- Android 16 / targetSdkVersion 36 / default。
- `STPE_SKIP_MULTIPLE_MISSED_PERIODIC_TASKS` enabled / disabled。
- `Timer#scheduleAtFixedRate` と AOSP Change ID 351566728 enabled / disabled。
- プロセスを Cached Apps Freezer / CPU の一時停止に相当する状態へ置き、複数周期を実行できない状態から復帰させる。
- カメラ状態のポーリング、Bluetooth / Wi-Fi の再接続、転送状態の同期、キャッシュの後処理について、実行回数と最終状態を確認する。
- `scheduleAtFixedRate` と `scheduleWithFixedDelay` の比較。
- 処理がネットワーク、DB、UI、ファイル I/O を更新する場合の欠落、重複、副作用。

## 人間の判断欄

- 最終優先度: 人間が判断する
- リリース判断への影響: 人間が判断する

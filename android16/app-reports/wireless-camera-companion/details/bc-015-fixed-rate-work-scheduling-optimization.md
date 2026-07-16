# BC-015: Fixed rate work scheduling optimization

## 基本情報

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/16/behavior-changes-16#schedule-at-fixed-rate
- Section: Fixed rate work scheduling optimization

既存調査:
- [android16/behavior-changes/target/core-functionality/fixed-rate-work-scheduling-optimization.md](../../../behavior-changes/target/core-functionality/fixed-rate-work-scheduling-optimization.md)
- [android16/summaries/target/core-functionality/fixed-rate-work-scheduling-optimization-summary.md](../../../summaries/target/core-functionality/fixed-rate-work-scheduling-optimization-summary.md)
- [android16/behavior-changes/target/core-functionality/fixed-rate-work-scheduling-optimization-implementation-examples.md](../../../behavior-changes/target/core-functionality/fixed-rate-work-scheduling-optimization-implementation-examples.md)

## 対象アプリとの関係

関連するアプリ機能:
- camera status / connection health の定期 polling。
- Bluetooth / Wi-Fi 接続監視と reconnect retry。
- 画像 / 動画 metadata、thumbnail、転送状態の同期。
- session / temporary file / cache cleanup。
- telemetry / metrics upload。

アプリが該当する可能性:
- Conditional。`ScheduledThreadPoolExecutor` / `ScheduledExecutorService` または `Timer` の `scheduleAtFixedRate` を利用し、freeze / suspend 等で missed した period の catch-up 回数に依存する場合に該当。
- WorkManager / JobScheduler / AlarmManager のみを使い、内部でも executor / Timer の `scheduleAtFixedRate` を併用していない場合は直接影響しない。

## 適用条件分類

主分類:
- `TARGET_SDK_36_CONDITIONAL`

必要条件:
- Android 16。
- targetSdkVersion 36 以上。
- `ScheduledThreadPoolExecutor#scheduleAtFixedRate`、`ScheduledExecutorService#scheduleAtFixedRate`、または `Timer#scheduleAtFixedRate` 利用。
- process freeze / CPU suspend 等で fixed-rate period を複数回 missed した後に復帰。

Confidence:
- High。

## OS アップデート影響と targetSdkVersion 影響

OS アップデート影響:
- Android 16 へ OS アップデートしただけでは、targetSdkVersion 35 以下のアプリに新挙動が default 適用されるとは判断しない。

targetSdkVersion 影響:
- Android 16 / targetSdkVersion 36 では、復帰時に即時実行される missed `scheduleAtFixedRate` execution は最大 1 回になる。
- 従来のように複数回分の missed task が連続 catch-up されることを前提とした処理では、実行回数が減る。

## AOSP / 公式根拠

既存 Android16 調査で確認済み:
- executor 側 Compat Change ID は `STPE_SKIP_MULTIPLE_MISSED_PERIODIC_TASKS` / 288912692。
- Timer 側 AOSP Change ID は `SKIP_MULTIPLE_MISSED_PERIODIC_TASKS` / 351566728。
- AOSP libcore の両 Change ID には `@EnabledAfter(targetSdkVersion = VersionCodes.VANILLA_ICE_CREAM)` があり、targetSdkVersion 36 以上で default enabled。
- `ScheduledFutureTask#setNextRunTime()` は change enabled の fixed-rate task で次回時刻を最後の missed period へ補正し、複数 missed executions の連続 catch-up を抑制する。
- `scheduleWithFixedDelay`、WorkManager、JobScheduler、AlarmManager は本件の直接対象ではない。`Timer#scheduleAtFixedRate` は別 Change ID 351566728 で同じ最適化の対象となる。

## アプリ影響

想定される影響:
- 復帰直後の camera status polling / connection check 回数が従来より減る。
- retry 回数を missed period 数として扱う実装では、再接続や転送再開の試行回数が減る。
- sync / cleanup / metrics upload を実行回数ベースで補填する設計では、一部 period 分の処理が行われない。
- fixed-rate task が idempotent でない場合、旧挙動と新挙動でデータ更新回数や副作用が変わる。

推奨対応:
- executor / Timer の `scheduleAtFixedRate` 利用箇所と wrapper / third-party SDK 内の利用を棚卸しする。
- API は `@Deprecated` ではないが、Android Lint の `DiscouragedApi` は本 Behavior Change と同じ cached-process catch-up 問題を警告しているため、無関係として除外しない。
- camera status polling / 接続監視は、前回の実際の開始時刻基準でよければ `Timer#schedule(..., period)`、前回処理完了から一定間隔を空けたければ `ScheduledExecutorService#scheduleWithFixedDelay` へ移行する。
- missed period 数だけ処理する必要がある場合は、callback の catch-up 回数に依存せず、最終成功時刻と現在時刻から必要な処理量を計算する。
- polling / retry / sync / cleanup が最大 1 回の immediate catch-up でも正しく収束するか確認する。
- WorkManager / JobScheduler / AlarmManager は本件の等価な移行先として扱わない。process death 後の再実行など、camera polling とは別の background work 要件がある場合に限って別途設計する。
- Before / After、Timer、Java、テストコードは [Fixed rate work scheduling optimization - 実装例](../../../behavior-changes/target/core-functionality/fixed-rate-work-scheduling-optimization-implementation-examples.md) を参照する。

## テスト観点

- Android 16 / targetSdkVersion 35 / default。
- Android 16 / targetSdkVersion 36 / default。
- `STPE_SKIP_MULTIPLE_MISSED_PERIODIC_TASKS` enabled / disabled。
- `Timer#scheduleAtFixedRate` と AOSP Change ID 351566728 enabled / disabled。
- process を Cached Apps Freezer / CPU suspend 相当の状態に置き、複数 period missed 後に復帰。
- camera status polling、Bluetooth / Wi-Fi reconnect retry、transfer state sync、cache cleanup の実行回数と最終状態。
- `scheduleAtFixedRate` と `scheduleWithFixedDelay` の比較。
- task が network、DB、UI、file I/O を更新する場合の欠落、重複、副作用。

## Human Decision

- Final priority: TBD by human
- Release readiness impact: TBD by human

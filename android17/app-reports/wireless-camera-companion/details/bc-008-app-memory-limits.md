# BC-008: App memory limits

## 基本情報（Basic Information）

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/17/behavior-changes-all
- Section: App memory limits

Original statement:
> Android 17 では device total RAM に基づく app memory limits が導入され、一部の Android devices で適用される、という趣旨の公式説明。

調査対象 Android バージョン:
- From: android-16.0.0_r4
- To: android-17.0.0_r1

## 対象アプリとの関係（Relevance to Target App）

関連するアプリ機能:
- 画像 / 動画一覧。
- サムネイル生成。
- RAW / high-resolution image transfer。
- 動画転送。
- キャッシュ。
- WebView。

関連する API / permission / component:
- `ApplicationExitInfo`
- `am memory-limiter`
- trigger-based profiling

アプリが該当する可能性:
- Conditional。対象 device で memory outlier がある場合に該当。

## 適用条件分類（Applicability Classification）

主分類（Primary classification）:
- OS_UPDATE_ALL_APPS

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | Yes / Conditional | AOSP に targetSdkVersion gate は確認されず、device / vendor config 条件で有効。 |
| targetSdkVersion 37 以上が必要か | No | targetSdkVersion gate は確認されない。 |
| 追加の実行時条件があるか | Yes | 対象 device、vendor config、RAM、process state、memory usage。 |
| Compat Change ID が関係するか | No | compat framework ではなく feature flag / vendor config / DeviceConfig 依存。 |

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17。
- targetSdkVersion: 条件なし。
- Device/form factor: memory limiter 対象 device。
- App state/process condition: memory usage が configured limit に到達。
- Mainline/module condition: vendor config / DeviceConfig / feature enabled。

Compat framework:
- Change ID: 確認されず。
- Change name: N/A
- Default state: vendor config / feature flag / DeviceConfig に依存。
- Toggleable for testing: `am memory-limiter` commands。

## AOSP 調査（AOSP Investigation）

関連ファイル:
- `MemoryLimiter.java`
- `com_android_server_am_MemoryLimiter.cpp`
- `ActivityManagerService.java`
- `ActivityManagerShellCommand.java`
- `ProcessRecord.java`
- `memory-limiter-config.xsd`
- `MemoryLimiter.md`

確認したソース文脈（Source Context Reviewed）:

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `MemoryLimiter` | app memory limits なし | process state に応じた memory / swap limits を native cgroup layer に渡す | app process kill / memory anomaly に直接関係する。 |
| `ActivityManagerShellCommand` / `am memory-limiter` | command なし | ignore / manual / status command 追加 | 公式検証手段。 |

差分解釈（Diff Interpretation）:
- Added behavior: MemoryLimiter 本体、JNI、vendor config schema、shell command。
- Changed condition: vendor config と RAM 条件で対象 device が決まる。

適用ゲート根拠（Applicability Gate Evidence）:
- targetSdkVersion gate: 見つからない。
- CompatChanges.isChangeEnabled / ChangeId: 見つからない。
- DeviceConfig / resources config: vendor config / DeviceConfig に依存。
- Gate conclusion: Android 17 上の対象 device で、対象 app process が configured limit に達した場合に適用。

## 事実・観察・仮説・結論（Facts / Observations / Hypotheses / Conclusion）

事実（Facts）:
- Android 17 で app memory limits が追加され、targetSdkVersion gate は確認されない。

観察（Observations）:
- 画像 / 動画処理は memory usage が大きくなりやすい。

仮説（Hypotheses）:
- 大量画像一覧、動画転送、サムネイルキャッシュ、長時間接続で memory outlier がある場合、対象 device で process exit が起きる可能性。

結論（Conclusion）:
- OS update impact として memory baseline と exit reason 収集を推奨。

## アプリ影響（App Impact）

想定される影響:
- memory limit 到達時の process kill。

ユーザー影響:
- 転送中断、アプリ再起動、画像一覧のリロード。

開発者影響:
- memory baseline、cache limit、bitmap lifecycle、transfer pipeline の見直し。

推奨対応候補:
- `ApplicationExitInfo.getDescription()` で `MemoryLimiter:AnonSwap` を確認する。
- `am memory-limiter status` と manual limit で再現性を確認する。
- 画像 / 動画転送の長時間テストを行う。

## Confidence

Confidence:
- High

Confidence の根拠:
- AOSP MemoryLimiter 本体と shell command を確認済み。

不足している根拠:
- 対象 device での vendor config。
- 対象アプリ memory profile。

---

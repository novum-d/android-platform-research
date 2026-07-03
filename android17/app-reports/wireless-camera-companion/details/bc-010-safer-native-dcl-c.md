# BC-010: Safer Native DCL-C

## 基本情報（Basic Information）

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/17/behavior-changes-17
- Section: Safer Native DCL-C

Original statement:
> targetSdkVersion 37 以上では、`System.load()` で読み込む native file が read-only である必要があり、条件を満たさない場合は `UnsatisfiedLinkError` になる、という趣旨の公式説明。

調査対象 Android バージョン:
- From: android-16.0.0_r4
- To: android-17.0.0_r1

## 対象アプリとの関係（Relevance to Target App）

関連するアプリ機能:
- 画像・動画処理 SDK、codec、AI / ML delegate、ネットワーク処理 SDK。
- 実行時に native library を download / generate / extract / update して `System.load()` する機能。

関連する API / permission / component:
- `System.load(path)`
- `Runtime.load0()`
- `VMRuntime.THROW_ERROR_FOR_WRITABLE_DCL`

アプリが該当する可能性:
- Conditional。通常の Camera API / Camera2 API 利用だけでは該当しない。native plugin、画像・動画処理 module、ネットワーク処理 module が writable native file loading を行う場合に該当する。

確認したアプリ実装:
- File / module: 未確認。
- Symbol / entry point: `System.load()` 利用有無は未確認。
- Manifest / permission: 該当なし。
- Runtime condition: targetSdkVersion 37 以上で該当コードパスが実行される場合。

## 適用条件分類（Applicability Classification）

主分類（Primary classification）:
- TARGET_SDK_37_CONDITIONAL

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 原則 No | Native DCL-C は compat ChangeId `463348571` の targetSdkVersion 37 gate。 |
| targetSdkVersion 37 以上が必要か | Yes | `@EnabledSince(CINNAMON_BUN)`。 |
| 追加の実行時条件があるか | Yes | writable native file を `System.load()` する場合。 |
| Compat Change ID が関係するか | Yes | `THROW_ERROR_FOR_WRITABLE_DCL = 463348571`。 |

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 以上。
- targetSdkVersion: 37 以上。
- API/component condition: `System.load(path)` による dynamic native loading。
- File condition: `System.load()` で読み込む native file が read-only でない場合。
- App state/process condition: アプリ起動時、SDK 初期化時、画像・動画処理 module / native plugin 初期化時。

Compat framework:
- Change ID: `463348571`
- Change name: `THROW_ERROR_FOR_WRITABLE_DCL`
- Default state: `@EnabledSince(targetSdkVersion = CINNAMON_BUN)`
- Toggleable for testing: compat change / runtime flags により切り替え可能。

## AOSP 調査（AOSP Investigation）

関連ファイル:
- `platform/libcore/ojluni/src/main/java/java/lang/Runtime.java`
- `platform/libcore/libart/src/main/java/dalvik/system/VMRuntime.java`

確認したソース文脈（Source Context Reviewed）:

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `Runtime.load0()` | writable native file は warning 中心 | writable file を検出し、条件を満たすと `UnsatisfiedLinkError` | `System.load(path)` の app-facing failure path。 |
| `VMRuntime.THROW_ERROR_FOR_WRITABLE_DCL` | ChangeId なし | `463348571` / `@EnabledSince(CINNAMON_BUN)` | Native DCL-C の targetSdkVersion 37 gate。 |

差分解釈（Diff Interpretation）:
- Added enforcement: `System.load(path)` で writable native file を拒否する path。
- Changed condition / gate: Android 17 runtime + targetSdkVersion 37 以上、または `THROW_ERROR_FOR_WRITABLE_DCL` enabled。
- No behavior change found: 通常の Camera API / Camera2 API 呼び出し自体には直接関係しない。

適用ゲート根拠（Applicability Gate Evidence）:
- targetSdkVersion gate: `@EnabledSince(CINNAMON_BUN)`。
- CompatChanges.isChangeEnabled / ChangeId: `463348571`。
- Build.VERSION / SDK_INT gate: Android 17 runtime が前提。
- Gate conclusion: Android 17 / targetSdkVersion 37 以上で、writable native file `System.load()` を行う場合に適用。

## 事実・観察・仮説・結論（Facts / Observations / Hypotheses / Conclusion）

事実（Facts）:
- Safer Native DCL-C は libcore `Runtime.load0()` と `VMRuntime.THROW_ERROR_FOR_WRITABLE_DCL` で確認できる。

観察（Observations）:
- カメラ連携アプリでも、画像・動画処理、codec、AI / ML delegate、ネットワーク処理 SDK は native library を含む可能性がある。
- 古い SDK では実行時展開した `.so` の load path を持つ可能性がある。

仮説（Hypotheses）:
- 対象アプリが native plugin を実行時に展開・更新して `System.load()` している場合、targetSdkVersion 37 更新後に `UnsatisfiedLinkError` が起きる可能性がある。

結論（Conclusion）:
- カメラ連携アプリでは要確認。通常のカメラ撮影 API だけではなく、同梱 SDK / native module / plugin 更新処理を含めて棚卸しする必要がある。

## アプリ影響（App Impact）

想定される影響:
- アプリ起動時または SDK 初期化時の crash / initialization failure。
- 画像・動画処理、codec、AI / ML delegate、ネットワーク処理 module の読み込み失敗。
- `System.load()` 時の `UnsatisfiedLinkError`。

ユーザー影響:
- アプリ起動失敗。
- ライブビュー、画像転送、動画処理、サムネイル生成、クラウド連携などの一部機能が使えない。

開発者影響:
- `System.load()` / native library 展開・更新処理の棚卸し。
- `System.load()` 前に native file を read-only にし、その後に書き換えない実装への変更。

推奨対応候補:
- アプリコードと SDK で `System.load(`、`.so` 展開処理を検索する。
- dynamic native loading を避け、APK / App Bundle 配布時点の native library に寄せる。
- どうしても動的読み込みが必要な場合は、write 完了後に read-only 化してから `System.load()` する。
- `UnsatisfiedLinkError` を起動 / 機能初期化の failure として検出できるようにする。

## Confidence

Confidence:
- High

Confidence の根拠:
- libcore `Runtime.load0()` / `VMRuntime` evidence を確認済み。

不足している根拠:
- 対象アプリおよび同梱 SDK の native loading 実装。
- 実際の targetSdkVersion 37 ビルドでの起動・画像 / 動画処理・転送テスト。

---

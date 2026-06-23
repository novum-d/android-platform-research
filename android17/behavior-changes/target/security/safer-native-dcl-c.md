# Safer Native DCL-C

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

### Behavior Change 文書（Behavior Change Source）

文書:
https://developer.android.com/about/versions/17/behavior-changes-17

セクション:
- Safer Native DCL-C

ページ種別:
- Android 17 以上をターゲットにするアプリ

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- TARGET_SDK_37_CONDITIONAL

公式文書からの初期適用条件判断:
- 公式文書は、targetSdkVersion 37 以上のアプリでは Android 14 で DEX / JAR files に導入された Safer Dynamic Code Loading protection が native libraries にも拡張されると説明している。
- `System.load()` で読み込まれる native files は read-only として mark されている必要があり、そうでない場合は `UnsatisfiedLinkError` が throw される。
- 追加 checkout の `platform/libcore` で、`Runtime.load0()` の writable file check、`UnsatisfiedLinkError` path、compat ChangeId `THROW_ERROR_FOR_WRITABLE_DCL = 463348571`、`@EnabledSince(CINNAMON_BUN)` を確認した。

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 原則 No | compat ChangeId が `@EnabledSince(targetSdkVersion = CINNAMON_BUN)`。 |
| targetSdkVersion 37 以上が必要か | Yes | `VMRuntime.THROW_ERROR_FOR_WRITABLE_DCL = 463348571` が `@EnabledSince(CINNAMON_BUN)`。 |
| 追加の実行時条件があるか | ある | `System.load()` で native file を動的に読み込み、読み込み時点で file が read-only でない場合。 |
| Compat Change ID が関係するか | Yes | `THROW_ERROR_FOR_WRITABLE_DCL = 463348571`。 |

### 調査日（Investigation Date）

2026-06-19

### 信頼度（Confidence）

- High

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] targetSdkVersion に関係なく Android 17 の全アプリへ適用
- [ ] Android 17 以上かつ targetSdkVersion 37 以上で適用
- [x] targetSdkVersion 37 以上かつ追加の実行時条件を満たす場合に適用
- [ ] Mainline / Google Play system update に依存
- [ ] API 追加のみであり、挙動変更ではない
- [ ] 追加 evidence が必要

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 以上。
- targetSdkVersion: 公式文書上は 37 以上。
- API / component condition: `System.load()` による dynamic native library loading。
- File condition: native file が read-only として mark されていること。
- Error condition: read-only 条件を満たさない場合に `UnsatisfiedLinkError`。

Compat framework:
- Change ID: `463348571`
- 変更名: `THROW_ERROR_FOR_WRITABLE_DCL`
- 既定状態: `@EnabledSince(targetSdkVersion = VersionCodes.CINNAMON_BUN)`
- テスト時に切り替え可能か: compat change と runtime flags により切り替え可能

分類信頼度（Classification confidence）:
- High

分類根拠（Classification evidence）:
- 公式 Behavior Change 文書は targetSdkVersion 37 以上と `System.load()` / read-only / `UnsatisfiedLinkError` 条件を説明している。
- `platform/libcore` Android 17 tag の `Runtime.load0()` が writable file を検出し、`VMRuntime.isReadOnlyDynamicCodeLoadThrowExceptionEnabled()`、`VMRuntime.isThrowErrorForWritableDclEnabled()`、SDK version `CINNAMON_BUN` 以上を満たす場合に `UnsatisfiedLinkError` を投げる。
- `VMRuntime` に `THROW_ERROR_FOR_WRITABLE_DCL = 463348571` が追加され、`@EnabledSince(targetSdkVersion = VersionCodes.CINNAMON_BUN)` が付いている。

---

# エグゼクティブサマリー

Android 17 では、targetSdkVersion 37 以上のアプリに対し、Safer Dynamic Code Loading protection が native libraries にも拡張される、と公式文書は説明している。`System.load()` で読み込む native file は read-only として mark されている必要があり、条件を満たさない場合は `UnsatisfiedLinkError` が発生する。

この変更は、実行時に `.so` をダウンロード、生成、展開、更新してから `System.load()` する設計に影響する可能性がある。dynamic code loading は code injection / code tampering risk を高めるため、可能な限り避けることが推奨される。

信頼度は High とする。`platform/libcore` で `System.load()` / `Runtime.load0()` の writable file check、`UnsatisfiedLinkError`、compat ChangeId、targetSdkVersion 37 gate を確認した。

---

# 公式ドキュメント確認

## 原文（Statement）

ページタイトル:
- Behavior changes: Apps targeting Android 17 or higher

ページ URL:
- https://developer.android.com/about/versions/17/behavior-changes-17

セクションタイトル:
- Safer Native DCL-C

検証対象の原文:
- Android 17 / API level 37 以上を target する場合、Android 14 で DEX / JAR files に導入された Safer Dynamic Code Loading protection が native libraries にも拡張される。
- `System.load()` で読み込まれるすべての native files は read-only として mark されている必要がある。
- 条件を満たさない場合は `UnsatisfiedLinkError`。

## 解釈（Interpretation）

この変更は、動的に読み込む native code が writable な状態で改ざんされるリスクを減らす security behavior change である。targetSdkVersion 37 へ更新するアプリで dynamic native loading を行っている場合、load 前に file permission / seal / read-only state を満たす必要がある。

---

# AOSP 調査（AOSP Investigation）

## チェックアウト状態

根拠利用前に確認したコマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list android-17.0.0_r1
```

結果:
- `frameworks-base` working tree: clean at the time of investigation.
- From tag: `android-16.0.0_r4` exists.
- To tag: `android-17.0.0_r1` exists.

## 関連ファイル（Related Files）

frameworks-base で確認した候補:
- `core/java/android/app/NativeActivity.java`
- `core/java/android/app/ApplicationLoaders.java`
- `core/java/android/app/LoadedApk.java`
- `core/java/android/os/Build.java`

追加で必要な AOSP project:
- なし。`tmp/aosp-checkouts/libcore` に `platform/libcore` の Android 16 / Android 17 tag を取得して確認済み。

差分確認メモ:
- 広域の `frameworks-base` tag diff では rename detection が skipped される警告が出るため、根拠確認では `--no-renames` と native loading 周辺 path 限定の diff を併用した。
- `LoadedApk` には `LinkerNamespaceParams`、`NativeZygoteProcess` には native zygote 起動 / native child zygote 用の linker namespace 引数を渡す差分がある。
- これらは package native library / native zygote の loading boundary であり、公式文書が述べる app の `System.load(path)` に対する read-only file enforcement ではないため、Safer Native DCL-C の直接 evidence には採用しない。
- `platform/libcore` の `ojluni/src/main/java/java/lang/Runtime.java` と `libart/src/main/java/dalvik/system/VMRuntime.java` を直接 evidence として採用する。

## 確認したソース文脈（Source Context Reviewed）

| File / symbol | Android 16 baseline | Android 17 behavior | 関連性 |
| --- | --- | --- | --- |
| `NativeActivity.loadNativeCode` | native code load boundary は存在 | read-only enforcement evidence なし | `NativeActivity` の native load path だが、公式文書の `System.load()` enforcement とは直接一致しない。 |
| `ApplicationLoaders` / `LoadedApk` | classloader native library path を libnativeloader に渡す | read-only enforcement evidence なし | package native library path の loader boundary。dynamic file `System.load()` の read-only check ではない。 |
| `Build.VERSION_CODES.CINNAMON_BUN` | なし | API 37 constant あり | targetSdkVersion 37 参照先だが、DCL gate そのものではない。 |
| `Runtime.load0(Class, String)` | writable native file は warning 中心 | non-root/system/shell UID で writable file を検出し、条件を満たすと `UnsatisfiedLinkError` | app の `System.load(path)` 実行 path。 |
| `VMRuntime.THROW_ERROR_FOR_WRITABLE_DCL` | なし | ChangeId `463348571`、`@EnabledSince(CINNAMON_BUN)` | targetSdkVersion 37 gate。 |

Source context の補足:
- Entry point / caller: app code の `System.load(path)`。
- 関連 class / service の責務: `Runtime.load0()` が file state を確認し、`VMRuntime` が compat ChangeId の有効状態を返す。
- Baseline Android behavior: Android 16 libcore では writable file に対して将来 throw する warning path が中心。
- Target Android behavior: Android 17 libcore では writable file、compat change enabled、SDK version 37 以上の場合に `UnsatisfiedLinkError` を投げる。
- Source diff type: changed condition / added enforcement。
- Excluded code paths: SQLite / ContentProvider / SharedMemory など read-only 文字列を含む無関係な code path、`NativeActivity` の app bundle native library load path。

## 差分解釈（Diff Interpretation）

| 観測した diff | 解釈 | Behavior Change との関連 | 信頼度 |
| --- | --- | --- | --- |
| frameworks-base に native DCL read-only gate は見つからない | no relevant behavior change found in frameworks-base | 実装本体は ART/native loader 側と判断 | Medium |
| 公式文書は targetSdkVersion 37 条件を明示 | documentation evidence | 適用条件の一次判断 | Medium |
| libcore `Runtime.load0()` に writable file throw path が追加 | added enforcement | `System.load(path)` で writable native file を拒否する本体 | High |
| `VMRuntime.THROW_ERROR_FOR_WRITABLE_DCL = 463348571` | compat gate | targetSdkVersion 37 以上で デフォルト有効 | High |

---

# 事実・観察・仮説・結論

## 事実（Facts）

- `frameworks-base` の `android-16.0.0_r4` と `android-17.0.0_r1` tag は存在し、調査時点の working tree は clean。
- 公式文書は targetSdkVersion 37 以上で native DCL read-only requirement が適用されると説明している。
- `frameworks-base` grep では `System.load()` native file read-only enforcement、DCL-C ChangeId、`UnsatisfiedLinkError` path は見つからなかった。
- `platform/libcore` Android 17 tag で `Runtime.load0()` の writable file check と `UnsatisfiedLinkError` path を確認した。
- `VMRuntime.THROW_ERROR_FOR_WRITABLE_DCL = 463348571` は `@EnabledSince(CINNAMON_BUN)`。

## 観察（Observations）

- この Behavior Change は `frameworks-base` ではなく libcore / ART API boundary に属する。
- bionic linker まで追わなくても、app-facing exception と target gate は `Runtime.load0()` / `VMRuntime` で確認できる。

## 仮説（Hypotheses）

- runtime flags と compat change が有効な Android 17 build で、non-root/system/shell UID の app が writable native file を `System.load()` すると `UnsatisfiedLinkError` になる。

## 結論（Conclusions）

- `TARGET_SDK_37_CONDITIONAL` と分類する。
- targetSdkVersion 37 以上、`System.load(path)`、writable native file、runtime enforcement flags enabled が条件。
- Confidence は High。

---

# 開発者影響

影響を受ける可能性が高いアプリ:
- 実行時に `.so` をダウンロード / 生成 / 展開 / 更新して `System.load()` するアプリ
- plugin / scripting / ML delegate / game engine extension など native module を動的に差し替えるアプリ
- 画像・動画処理、codec、AI / ML delegate、ネットワーク処理、暗号処理などの native library をアプリ起動後に展開・更新して読み込むアプリ / SDK

対応候補:
- dynamic native loading を避け、APK / App Bundle 配布時点の native library に寄せる。
- どうしても必要な場合、`System.load()` 前に native file を read-only として確定し、その後に内容を書き換えない。
- `UnsatisfiedLinkError` を認証 /起動 / feature initialization の failure として扱えるよう fallback を実装する。

---

# 追加調査 TODO

- ART/libcore の `System.load()` / `Runtime.load0()` path を Android 16 / Android 17 tag で比較する。
- native loader / bionic linker で read-only file state と targetSdkVersion 37 gate を確認する。
- Compat ChangeId と default state を確認する。
- `System.loadLibrary()` と `System.load(path)` の扱い差を確認する。

---

# 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断

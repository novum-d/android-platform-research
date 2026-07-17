# BC-014: GPU syscall filtering - PM向け概要

## この文書の目的

Android 16 の GPU syscall filtering について、カメラアプリの PM が変更概要、用語、影響予測、調査の進め方を把握するための概要である。

この文書は最終的な release readiness や severity を決定するものではない。公式文書と AOSP evidence に基づく事実、対象カメラアプリへの影響予測、確認が必要な事項を分けて記載する。

## 公式文書

- Entry Point: [Android 16 - GPU syscall filtering](https://developer.android.com/about/versions/16/behavior-changes-16#gpu-syscall-filtering)
- Arm overview: [Arm products - Mali GPUs](https://www.arm.com/products)
- Detailed investigation: [GPU syscall filtering](../../../behavior-changes/target/security/gpu-syscall-filtering.md)
- Reader FAQ: [GPU syscall filtering - 基礎概念 FAQ](../../../behavior-changes/target/security/gpu-syscall-filtering-concepts-faq.md)
- One page summary: [GPU syscall filtering summary](../../../summaries/target/security/gpu-syscall-filtering-summary.md)
- Camera app detail: [BC-014 GPU syscall filtering](bc-014-gpu-syscall-filtering.md)

## エグゼクティブサマリー

Android 16 では、Mali GPU driver に送られる一部の低レベル命令を production build で制限する。deprecated / GPU development-only IOCTL は block され、GPU profiling 用 IOCTL は shell process または debuggable app に限定される。公式の Pixel scope は Mali GPU を使う Pixel 6-9 である。

通常の CameraX / Camera2、MediaCodec、Vulkan、OpenGL ES など supported API の利用は、公式文書上は影響しない。カメラアプリで注意が必要なのは、app 本体または bundled native SDK / graphics middleware / profiler が `/dev/mali0` に直接アクセスし、制限対象の IOCTL を発行している場合である。

対象アプリの source code / dependencies は未確認であるため、現時点の影響予測は次のとおりとする。

- 通常の camera preview / recording / playback / supported GPU rendering: 低リスク予測。
- native image processing / ML / graphics SDK: 利用実態が不明なため要調査。
- custom GPU profiling / diagnostics / benchmark / vendor-specific access: 条件付きで影響リスクあり。
- 最終 priority / severity / release readiness: Human decision。現時点では未判断。

Confidence: Medium。公式 policy と AOSP の filtering mechanism は確認済みだが、対象アプリの実装、bundled SDK、実機 denial は未確認である。

## 変更概要

通常の描画経路は次のとおりである。

```text
camera app / graphics feature
  -> CameraX / Camera2 / MediaCodec / Vulkan / OpenGL ES / EGL
  -> userspace driver / Android system service
  -> ioctl system call
  -> kernel driver
  -> camera device / Mali GPU
```

今回の変更は GPU access や `ioctl` 全体を禁止するものではない。Mali GPU driver に対する IOCTL command を category 単位で判定する。

| IOCTL category | Android 16 production build の扱い |
|---|---|
| 通常の supported graphics API に必要な command | 許可される想定 |
| deprecated command | block |
| GPU development-only / restricted command | block |
| profiling / instrumentation command | shell process または debuggable app に限定 |

制限対象の IOCTL が拒否されると、`ioctl()` は caller へ error を返し、logcat には `/dev/mali0` に対する SELinux `avc: denied { ioctl }` が記録され得る。その後に app が継続、機能無効化、fallback、crash のどれになるかは、app / SDK の error handling に依存する。

## 適用条件

Primary classification: `OS_UPDATE_ALL_APPS`

この分類は、すべての app が実際に壊れるという意味ではない。`targetSdkVersion 36` への更新ではなく、OS / device policy による変更であることを示す。

| 実行条件 | 想定挙動 |
|---|---|
| Android 16 / Pixel 6-9 Mali / targetSdkVersion 35 | blocked IOCTL なら拒否され得る |
| Android 16 / Pixel 6-9 Mali / targetSdkVersion 36 | target 35 と同様。target SDK 固有ではない |
| Android 16 / non-debuggable release app | profiling / restricted IOCTL は拒否され得る |
| Android 16 / debuggable app または shell | profiling IOCTL は許可される想定 |
| Android 16 / supported Vulkan / OpenGL ES | 公式文書上は影響なし |
| non-Mali GPU | 今回確認した公式 scope 外 |
| Pixel 以外の Mali device | OEM / SoC vendor の opt-in policy 次第 |

## 用語一覧

| 用語 | PM向け説明 |
|---|---|
| GPU | 画面描画、3D rendering、画像処理などを並列実行する processor |
| Mali GPU | Arm の GPU 製品。今回の公式 Pixel scope は Pixel 6-9 |
| shell command | 人が terminal に入力する `cd` や `cat` などの command |
| syscall / system call | program が Linux kernel の機能を利用するための interface。shell commandそのものではない |
| shell | command を解釈し、shell 自身が処理するか program を起動する software。syscall を使う主体の一つ |
| IOCTL | device 固有の control command を kernel driver に送る syscall |
| `/dev/mali0` | Mali GPU kernel driver へアクセスするための device node |
| driver | OS と hardware の間で device を制御する software |
| SELinux | Android で process / resource / command のアクセスを制御する security mechanism |
| production build | 一般ユーザーへ提供される retail / user build を中心とする実運用条件 |
| debuggable app | debug を許可した app。profiling IOCTL の例外対象になり得る |
| supported graphics API | Vulkan、OpenGL ES、EGL など Android / driver が正式に対応する graphics interface |
| bundled native SDK | APK / AAB に含まれる C / C++ の `.so` library。app code に直接記述がなくても低レベルアクセスを含む可能性がある |

## shell command と syscall の関係

shell command が一つの syscall に変換されるわけではない。

```text
人が「cat file.txt」を入力
  -> shell が cat program を起動
  -> cat が openat / read / write / close など複数の syscall を呼ぶ
  -> Linux kernel が file access と出力を処理する
```

Android app、framework、native library、GPU driver も shell を経由せず syscall を使う。したがって、GPU syscall filtering は terminal command を禁止する変更ではなく、app / library から GPU kernel driver へ送られる低レベル要求を制限する変更である。

## カメラアプリに対する影響予測

### 事実

- 公式文書は supported Vulkan / OpenGL を影響対象外としている。
- 公式 Pixel scope は Mali GPU を使う Pixel 6-9 である。
- targetSdkVersion 36 gate と対応する compat Change ID は確認できない。
- 主な diagnostic signal は `/dev/mali0` に対する `avc: denied { ioctl }` である。

### 対象アプリへの予測

| カメラアプリ機能 | 影響予測 | 理由 / 未確認事項 |
|---|---|---|
| CameraX / Camera2 preview | 低 | 通常は Android supported API / system service 経由。今回の direct Mali IOCTL とは別経路と予測 |
| 動画 recording / playback / MediaCodec | 低 | 今回の変更は Mali GPU IOCTL filtering。codec固有問題は別途評価が必要 |
| OpenGL ES / Vulkan を使う live view rendering | 低 | supported graphics API は公式文書上影響なし |
| GPU filter / image processing | 低から不明 | supported APIだけなら低いが、bundled native SDK の実装は要確認 |
| on-device ML / native image SDK | 不明 | GPU backend / vendor-specific library / `.so` dependency の棚卸しが必要 |
| GPU profiling / diagnostics / benchmark | 中から高 | production app から profiling / restricted IOCTL を直接使う場合は拒否され得る |
| `/dev/mali0` direct access | 高 | 制限対象 command なら SELinux denial と機能失敗の可能性 |

現時点では、live view や camera feature 自体が直ちに壊れる変更とは予測しない。主なリスクは、camera feature の周辺に含まれる native graphics SDK、profiling、diagnostics、vendor-specific optimization である。

## 対応候補: 主な調査方法

### 1. Source code と依存 SDK の棚卸し

対象範囲:

- app の C / C++ / JNI code
- APK / AAB に含まれる `.so`
- image processing / ML / graphics middleware
- monitoring / profiling / benchmark / anti-cheat / diagnostics SDK

```bash
rg -n -i '/dev/mali0|ioctl\s*\(|mali|gpu_device' <native-source-or-sdk-directory>
rg -a -n -i '/dev/mali0|mali' <directory-containing-so-files>
```

検索結果がなくても、strip 済み `.so` や indirect call を完全には否定できない。SDK vendor documentation、version、release notes、問い合わせ結果も evidence として残す。

### 2. 実機条件の確認

Pixel 6-9 の Android 16 retail / user build と、配布相当の non-debuggable release app を主条件にする。

```bash
adb shell getprop ro.product.model
adb shell getprop ro.build.version.release
adb shell getprop ro.build.version.sdk
adb shell getprop ro.build.type
adb shell getprop ro.hardware.egl
adb shell getprop ro.hardware.vulkan
```

### 3. カメラ機能を操作して denial log を確認

最低限の操作:

- app startup / camera connection
- live preview の開始・停止
- recording / playback
- GPU filter / image processing / ML feature
- background / foreground 復帰
- diagnostics / profiling SDK initialization

```bash
adb logcat -c
# 上記の対象操作を release app で実行
adb logcat -d | rg 'avc: denied.*ioctl|/dev/mali0|gpu_device'
```

denial が出た場合は、次を一組で記録する。

- device / Android build / targetSdkVersion / app version
- debug / non-debuggable release
- package name / 操作手順 / 発生時刻
- `ioctlcmd`, `scontext`, `tcontext`, `tclass`
- crash、feature failure、fallback、diagnostic-only failure のどれか

### 4. 比較テスト

| 比較 | 目的 |
|---|---|
| Android 15 vs Android 16 | OS update による差か |
| targetSdkVersion 35 vs 36 | target SDK 固有ではないことを確認する |
| debug vs non-debuggable release | profiling exception に依存するか |
| Pixel Mali vs non-Mali device | Mali policy に依存するか |
| supported rendering vs native SDK feature | direct / restricted IOCTL pathだけが失敗するか |

### 5. 調査結果の判定

| 結果 | PM向け判定候補 |
|---|---|
| direct Mali accessなし、denialなし、主要機能正常 | 現行構成では低リスク候補 |
| denialあり、主要機能正常 | diagnostics / optional SDKを含め発生元を特定。将来リスクとして管理 |
| denialと特定機能失敗が一致 | Android 16 compatibility issue候補。SDK update / fallback / supported API移行を検討 |
| denial後にnative crash | 高優先の修正候補。release blockerかはHuman decision |
| blocked IOCTLが業務上必要 | 再現手順とlogを添えてAndroid bugをfileし、公式案内の宛先へassign |

## PMが開発チームへ確認する項目

- app に native `.so` や third-party graphics / ML SDK が含まれるか。
- `/dev/mali0` または Mali-specific API を直接使う実装があるか。
- Pixel 6-9 / Android 16 / release build で主要カメラ機能を検証したか。
- `avc: denied { ioctl }` が出ていないか。
- denial が出た場合、どのSDK・どの機能・どの`ioctlcmd`か。
- SDK update、機能無効化、supported APIへの移行、fallbackの候補があるか。

## Human Decision Placeholder

- Final priority: TBD by human
- Final severity: TBD by human
- Release readiness impact: TBD by human
- Customer communication priority: TBD by human
- Investigation owner / due date: TBD by human
- Owner decision / next action: TBD by human

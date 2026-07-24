# BC-014: GPU syscall filtering - PM向け概要

## この文書の目的

Android 16 の GPU syscall filtering について、カメラアプリの PM が変更概要、用語、影響予測、調査の進め方を把握するための概要である。

この文書は、最終的なリリース判断や影響度を決定するものではない。公式文書と AOSP 根拠に基づく事実、対象カメラアプリへの影響予測、確認が必要な事項を分けて記載する。

## 公式文書

- 調査の起点: [Android 16 - GPU syscall filtering](https://developer.android.com/about/versions/16/behavior-changes-16#gpu-syscall-filtering)
- Arm の概要: [Arm products - Mali GPUs](https://www.arm.com/products)
- 詳細調査: [GPU syscall filtering](../../../behavior-changes/target/security/gpu-syscall-filtering.md)
- 読者向け FAQ: [GPU syscall filtering - 基礎概念 FAQ](../../../behavior-changes/target/security/gpu-syscall-filtering-concepts-faq.md)
- 1ページ要約: [GPU syscall filtering summary](../../../summaries/target/security/gpu-syscall-filtering-summary.md)
- カメラアプリ向け詳細: [BC-014 GPU syscall filtering](bc-014-gpu-syscall-filtering.md)

## エグゼクティブサマリー

Android 16 では、Mali GPU driver に送られる一部の低レベル命令を製品版ビルドで制限する。非推奨または GPU 開発専用の IOCTL は拒否され、GPU profiling 用 IOCTL は shell process または debuggable app に限定される。公式に示されている Pixel の対象機種は、Mali GPU を使う Pixel 6〜9 である。

通常の CameraX / Camera2、MediaCodec、Vulkan、OpenGL ES など、正式に対応している API の利用には、公式文書上は影響しない。カメラアプリで注意が必要なのは、アプリ本体、同梱された native SDK、graphics middleware、profiler が `/dev/mali0` に直接アクセスし、制限対象の IOCTL を発行している場合である。

対象アプリのソースコードと依存関係は未確認であるため、現時点の影響予測は次のとおりとする。

- 通常のカメラプレビュー、録画、再生、対応済み GPU API による描画: 低リスクと予測する。
- native の画像処理、ML、graphics SDK: 利用実態が不明なため調査が必要である。
- 独自の GPU profiling、診断、ベンチマーク、ベンダー固有のアクセス: 条件次第で影響する可能性がある。
- 最終優先度、影響度、リリース判断: 人間が判断する。現時点では未判断である。

Confidence: Medium。公式方針と AOSP の filtering mechanism は確認済みだが、対象アプリの実装、同梱 SDK、実機での拒否結果は未確認である。

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

今回の変更は、GPU へのアクセスや `ioctl` 全体を禁止するものではない。Mali GPU driver に対する IOCTL command を分類ごとに判定する。

| IOCTL の分類 | Android 16 の製品版ビルドでの扱い |
|---|---|
| 通常の対応済み graphics API に必要な command | 許可される想定 |
| 非推奨の command | 拒否 |
| GPU 開発専用 / 制限対象の command | 拒否 |
| profiling / instrumentation 用の command | shell process または debuggable app に限定 |

制限対象の IOCTL が拒否されると、`ioctl()` は呼び出し元へエラーを返し、logcat には `/dev/mali0` に対する SELinux の `avc: denied { ioctl }` が記録される可能性がある。その後、アプリが動作を継続するのか、機能を無効化するのか、代替処理へ切り替えるのか、クラッシュするのかは、アプリや SDK のエラー処理に依存する。

## 適用条件

主分類: `OS_UPDATE_ALL_APPS`

この分類は、すべてのアプリで実際に問題が発生するという意味ではない。`targetSdkVersion 36` への更新ではなく、OS と端末の policy による変更であることを示す。

| 実行条件 | 想定挙動 |
|---|---|
| Android 16 / Pixel 6〜9 Mali / targetSdkVersion 35 | 制限対象の IOCTL は拒否される可能性がある |
| Android 16 / Pixel 6-9 Mali / targetSdkVersion 36 | target 35 と同様。target SDK 固有ではない |
| Android 16 / non-debuggable の製品版アプリ | profiling 用または制限対象の IOCTL は拒否される可能性がある |
| Android 16 / debuggable app または shell | profiling IOCTL は許可される想定 |
| Android 16 / 対応済みの Vulkan / OpenGL ES | 公式文書上は影響なし |
| Mali 以外の GPU | 今回確認した公式な対象外 |
| Pixel 以外の Mali 搭載端末 | OEM / SoC ベンダーの opt-in policy 次第 |

## 用語一覧

| 用語 | PM向け説明 |
|---|---|
| GPU | 画面描画、3D rendering、画像処理などを並列実行するプロセッサ |
| Mali GPU | Arm の GPU 製品。今回公式に示された Pixel の対象は Pixel 6〜9 |
| shell command | 人がターミナルへ入力する `cd` や `cat` などのコマンド |
| syscall / system call | プログラムが Linux kernel の機能を利用するためのインターフェース。shell command そのものではない |
| shell | コマンドを解釈し、shell 自身で処理するかプログラムを起動するソフトウェア。syscall を使う主体の一つ |
| IOCTL | 端末固有の制御コマンドを kernel driver へ送る syscall |
| `/dev/mali0` | Mali GPU の kernel driver へアクセスするための device node |
| driver | OS とハードウェアの間で端末を制御するソフトウェア |
| SELinux | Android でプロセス、リソース、コマンドへのアクセスを制御するセキュリティ機構 |
| production build | 一般ユーザーへ提供する retail / user build を中心とした実運用向けビルド |
| debuggable app | debug を許可したアプリ。profiling 用 IOCTL の例外対象になる可能性がある |
| supported graphics API | Vulkan、OpenGL ES、EGL など、Android や driver が正式に対応している graphics interface |
| bundled native SDK | APK / AAB に含まれる C / C++ の `.so` library。アプリのコードに直接記述がなくても、低レベルアクセスを含む可能性がある |

## shell command と syscall の関係

shell command が一つの syscall に変換されるわけではない。

```text
人が「cat file.txt」を入力
  -> shell が cat program を起動
  -> cat が openat / read / write / close など複数の syscall を呼ぶ
  -> Linux kernel が file access と出力を処理する
```

Android アプリ、framework、native library、GPU driver も、shell を経由せず syscall を使う。したがって、GPU syscall filtering はターミナルコマンドを禁止する変更ではなく、アプリや library から GPU kernel driver へ送られる低レベル要求を制限する変更である。

## カメラアプリに対する影響予測

### 事実

- 公式文書は supported Vulkan / OpenGL を影響対象外としている。
- 公式 Pixel scope は Mali GPU を使う Pixel 6-9 である。
- targetSdkVersion 36 gate と対応する compat Change ID は確認できない。
- 主な診断情報は、`/dev/mali0` に対する `avc: denied { ioctl }` である。

### 対象アプリへの予測

| カメラアプリ機能 | 影響予測 | 理由 / 未確認事項 |
|---|---|---|
| CameraX / Camera2 のプレビュー | 低 | 通常は Android の対応済み API / system service を経由する。今回の Mali IOCTL の直接呼び出しとは別経路と予測する |
| 動画 recording / playback / MediaCodec | 低 | 今回の変更は Mali GPU IOCTL filtering。codec固有問題は別途評価が必要 |
| OpenGL ES / Vulkan を使うライブビュー描画 | 低 | 対応済みの graphics API は公式文書上影響なし |
| GPU フィルター / 画像処理 | 低から不明 | 対応済み API だけなら低いが、同梱された native SDK の実装は要確認 |
| on-device ML / native image SDK | 不明 | GPU backend / vendor-specific library / `.so` dependency の棚卸しが必要 |
| GPU profiling / diagnostics / benchmark | 中から高 | production app から profiling / restricted IOCTL を直接使う場合は拒否され得る |
| `/dev/mali0` への直接アクセス | 高 | 制限対象の command であれば、SELinux による拒否と機能失敗の可能性がある |

現時点では、ライブビューやカメラ機能自体が直ちに動作しなくなる変更とは予測しない。主なリスクは、カメラ機能の周辺に含まれる native graphics SDK、profiling、診断機能、ベンダー固有の最適化である。

## 対応候補: 主な調査方法

### 1. ソースコードと依存 SDK の棚卸し

対象範囲:

- アプリの C / C++ / JNI コード
- APK / AAB に含まれる `.so`
- image processing / ML / graphics middleware
- monitoring / profiling / benchmark / anti-cheat / diagnostics SDK

```bash
rg -n -i '/dev/mali0|ioctl\s*\(|mali|gpu_device' <native-source-or-sdk-directory>
rg -a -n -i '/dev/mali0|mali' <directory-containing-so-files>
```

検索結果がなくても、strip 済みの `.so` や間接呼び出しを完全には否定できない。SDK ベンダーの文書、バージョン、リリースノート、問い合わせ結果も根拠として残す。

### 2. 実機条件の確認

Pixel 6〜9 の Android 16 retail / user build と、配布版相当の non-debuggable アプリを主な確認条件とする。

```bash
adb shell getprop ro.product.model
adb shell getprop ro.build.version.release
adb shell getprop ro.build.version.sdk
adb shell getprop ro.build.type
adb shell getprop ro.hardware.egl
adb shell getprop ro.hardware.vulkan
```

### 3. カメラ機能を操作して拒否ログを確認

最低限の操作:

- アプリの起動 / カメラ接続
- ライブプレビューの開始・停止
- 録画 / 再生
- GPU filter / image processing / ML feature
- バックグラウンド / フォアグラウンドからの復帰
- diagnostics / profiling SDK initialization

```bash
adb logcat -c
# 上記の対象操作を release app で実行
adb logcat -d | rg 'avc: denied.*ioctl|/dev/mali0|gpu_device'
```

拒否ログが出た場合は、次を一組で記録する。

- 端末 / Android build / targetSdkVersion / アプリのバージョン
- debug / non-debuggable の製品版
- パッケージ名 / 操作手順 / 発生時刻
- `ioctlcmd`, `scontext`, `tcontext`, `tclass`
- クラッシュ、機能停止、代替処理への切り替え、診断ログだけの失敗のどれか

### 4. 比較テスト

| 比較 | 目的 |
|---|---|
| Android 15 と Android 16 | OS アップデートによる差か |
| targetSdkVersion 35 vs 36 | target SDK 固有ではないことを確認する |
| debug と non-debuggable の製品版 | profiling の例外に依存するか |
| Pixel Mali と Mali 以外の端末 | Mali の policy に依存するか |
| 対応済みの描画経路と native SDK の機能 | IOCTL の直接呼び出しまたは制限対象の経路だけが失敗するか |

### 5. 調査結果の判定

| 結果 | PM向け判定候補 |
|---|---|
| Mali への直接アクセスなし、拒否ログなし、主要機能は正常 | 現行構成では低リスク候補 |
| 拒否ログあり、主要機能は正常 | 診断機能や任意 SDK を含めて発生元を特定し、将来のリスクとして管理する |
| 拒否ログと特定機能の失敗が一致 | Android 16 の互換性問題候補。SDK の更新、代替処理、対応済み API への移行を検討する |
| 拒否後に native crash | 優先度の高い修正候補。リリースを止めるかは人間が判断する |
| 制限対象の IOCTL が業務上必要 | 再現手順とログを添えて Android の不具合として報告し、公式案内の宛先を担当に指定する |

## PMが開発チームへ確認する項目

- アプリに native `.so` や third-party の graphics / ML SDK が含まれるか。
- `/dev/mali0` または Mali-specific API を直接使う実装があるか。
- Pixel 6〜9 / Android 16 / 製品版ビルドで主要カメラ機能を検証したか。
- `avc: denied { ioctl }` が出ていないか。
- 拒否ログが出た場合、どの SDK、どの機能、どの `ioctlcmd` が原因か。
- SDK の更新、機能の無効化、対応済み API への移行、代替処理の候補があるか。

## 人間の判断欄

- 最終優先度: 人間が判断する
- 最終影響度: 人間が判断する
- リリース判断への影響: 人間が判断する
- 顧客通知の優先度: 人間が判断する
- 調査担当者 / 期限: 人間が判断する
- 管理者の判断 / 次の対応: 人間が判断する

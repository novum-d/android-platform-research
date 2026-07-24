# GPU syscall filtering - 基礎概念 FAQ

## 位置づけ

このファイルは、GPU syscall filtering の主レポートを読む際に生じる、用語や処理経路に関する疑問を補足する FAQ である。公式ドキュメントの `FAQ` subsection を調査する [GPU syscall filtering FAQ](gpu-syscall-filtering-faq.md) とは目的が異なる。

根拠、適用条件、分類、confidence、人間の判断は、主レポートと1ページ要約を正とする。この FAQ 自体で、新しい Behavior Change や独立した適用条件分類は定義しない。

主レポート:
- [GPU syscall filtering](gpu-syscall-filtering.md)

1ページ要約:
- [GPU syscall filtering summary](../../../summaries/target/security/gpu-syscall-filtering-summary.md)

カメラアプリの PM 向け概要:
- [BC-014 GPU syscall filtering - PM向け概要](../../../app-reports/wireless-camera-companion/details/bc-014-gpu-syscall-filtering-pm-overview.md)

## 調査メタデータ

- Android バージョン: Android 16
- 比較元タグ: `android-15.0.0_r36`
- 比較先タグ: `android-16.0.0_r4`
- 親セクション: GPU syscall filtering
- FAQ の範囲: shell command / syscall / IOCTL / 呼び出し元 / 拒否された場合の結果
- 継承する適用条件分類: `OS_UPDATE_ALL_APPS`
- 継承する confidence: Medium

## FAQ

### Q1. syscall は `cd` や `cat` などのコマンドか

短い回答:

異なる。`cd` や `cat` は人が shell に入力するコマンドであり、syscall はプログラムが Linux kernel の機能を利用するためのインターフェースである。

説明:

一つの shell command が一つの syscall に置き換わるわけではない。例えば、`cd` では shell 自身が `chdir` syscall を呼ぶ。`cat file.txt` では、shell が `execve` などで `cat` プログラムを起動し、起動された `cat` が `openat`、`read`、`write`、`close` など複数の syscall を使う。

```text
人が shell command を入力
  -> shell が command を解釈
  -> shell 自身が処理、または program を起動
  -> shell / program / library が必要な syscall を呼ぶ
  -> Linux kernel が処理する
```

本件との関係:

GPU syscall filtering はターミナルコマンドを禁止する変更ではない。アプリや library から GPU kernel driver へ送られる低レベル要求を制限する。

### Q2. syscall は、shell command が kernel 向けのコマンドへ変換されたものか

短い回答:

厳密には異なる。shell はコマンドを解釈して処理やプログラムの起動を行い、その shell または起動されたプログラム / library が必要な syscall を呼ぶ。

説明:

shell は syscall の呼び出し元になることもあるが、shell command を syscall へ機械的に変換するだけの層ではない。Android アプリ、framework、native library、driver は、shell を経由せず syscall を使う。

```text
shell command
  -> shell builtin の処理、または program 起動
  -> 一つ以上の library call / syscall
  -> Linux kernel
```

本件との関係:

Android アプリの GPU アクセスは通常、shell ではなく、Vulkan / OpenGL ES / EGL と userspace driver を経由する。

### Q3. どのようなアプリが `ioctl` を呼ぶか

短い回答:

多くの Android アプリは、framework / library / driver を通じて間接的に `ioctl` を使う。アプリ開発者が NDK の C / C++ コードから `ioctl()` を直接呼び出すのは、端末との統合やベンダー固有のツールなど、限られた実装である。

代表例:

| アプリ / 機能 | `ioctl` の使われ方 |
| --- | --- |
| Android アプリのプロセス間通信 | Binder library / driver が `/dev/binder` を制御する |
| ゲーム / グラフィックスアプリ | Vulkan / OpenGL userspace driver が GPU driver を制御する |
| カメラ / 音声 / USB 機能 | framework、system service、native library が device driver を制御する |
| profiler / benchmark / diagnostics | native code が profiling / instrumentation command を発行し得る |
| ベンダー固有の middleware / 不正対策 | 非公開の device command を直接使う可能性がある |

本件で確認する条件:

1. アプリプロセスまたは同梱された native SDK が `/dev/mali0` にアクセスしているか。
2. その IOCTL が非推奨、開発専用、profiling 用のいずれかに分類されるか。
3. shell / debuggable app ではなく、non-debuggable の製品版アプリから発行しているか。

「どこかで `ioctl` が使われている」というだけでは、影響の有無を判断できない。通常の CameraX / Camera2 / MediaCodec / Vulkan / OpenGL ES 利用で対応済みの driver が内部的に発行する許可対象の IOCTL と、アプリや SDK が非公開の Mali IOCTL を直接発行する実装を分けて扱う。

### Q4. `/dev/mali0` にアクセスして `ioctl` を呼ぶと何が起きるか

短い回答:

`ioctl` command が許可されれば Mali kernel driver が処理し、拒否されれば呼び出し元へエラーが返る。その後、アプリが動作を継続するのか、機能を停止するのか、クラッシュするのかは、アプリや SDK のエラー処理に依存する。

概念上の code:

```c
int fd = open("/dev/mali0", O_RDWR);
int result = ioctl(fd, command, &data);
```

処理の流れ:

```text
open("/dev/mali0")
  -> GPU driver への file descriptor を取得
ioctl(fd, command, data)
  -> SELinux / kernel が command を許可するか判定
  -> 許可: driver が command を実行
  -> 拒否: ioctl が失敗し、caller へ error を返す
```

Android 16 の filtering では、device node の `open` が成功しても、個別の `ioctlcmd` が SELinux policy により拒否される可能性がある。

| 結果 | driver / アプリの挙動 |
| --- | --- |
| IOCTL が許可される | driver が memory allocation、GPU job submission、state query など command に対応する処理を行う |
| IOCTL が拒否される | `ioctl()` が失敗し、一般には `-1` と権限に関する errno が呼び出し元へ返る |
| 呼び出し元が失敗を処理する | 任意機能を無効化する、対応済み API を使う代替処理へ切り替える、エラーを表示するなどして動作を継続できる |
| 呼び出し元が成功を前提にする | native crash、機能停止、不正な状態などにつながる可能性がある |

判定上の注意:

SELinux の拒否ログは、policy が command を拒否した根拠である。ただし、それだけで顧客影響は確定しない。アプリや SDK が戻り値と errno をどのように処理するかを確認し、クラッシュ、機能停止、安全な代替処理への切り替え、診断ログだけの失敗のどれに該当するかを判定する。

## 用語早見表

| 用語 | 説明 |
| --- | --- |
| shell command | 人が shell に入力する `cd` や `cat` などの command |
| shell | command を解釈し、builtin 処理または program 起動を行う software |
| syscall | application と Linux kernel の基本 interface |
| `ioctl` | device 固有の control command を file descriptor 経由で送る syscall |
| `/dev/mali0` | Mali GPU kernel driver の device node |
| `ioctlcmd` | driver へ要求する操作を識別する command value |
| SELinux denial | security policy が操作を拒否したことを示す audit log |

## 確認方法

実装、依存 SDK、実機の拒否ログを確認する手順は、主レポートの [確認方法](gpu-syscall-filtering.md#確認方法) を参照する。

## 参照資料

- [Android 16 - GPU syscall filtering](https://developer.android.com/about/versions/16/behavior-changes-16#gpu-syscall-filtering)
- [Linux system calls manual](https://man7.org/linux/man-pages/man2/syscalls.2.html)
- [Linux ioctl manual](https://man7.org/linux/man-pages/man2/ioctl.2.html)
- [Linux execve manual](https://man7.org/linux/man-pages/man2/execve.2.html)
- [GPU syscall filtering primary report](gpu-syscall-filtering.md)

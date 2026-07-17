# GPU syscall filtering - 基礎概念 FAQ

## 位置づけ

このファイルは、GPU syscall filtering の primary report を読む際に生じた用語・処理経路の疑問を補足する FAQ companion である。公式ドキュメントの `FAQ` subsection を調査する [GPU syscall filtering FAQ](gpu-syscall-filtering-faq.md) とは目的が異なる。

根拠、適用条件、classification、confidence、Human Decision は primary report / one-page summary を正とする。この FAQ 自体で新しい Behavior Change や独立した適用分類を定義しない。

Primary report:
- [GPU syscall filtering](gpu-syscall-filtering.md)

One-page summary:
- [GPU syscall filtering summary](../../../summaries/target/security/gpu-syscall-filtering-summary.md)

Camera app PM overview:
- [BC-014 GPU syscall filtering - PM向け概要](../../../app-reports/wireless-camera-companion/details/bc-014-gpu-syscall-filtering-pm-overview.md)

## 調査メタデータ

- Android version: Android 16
- From tag: `android-15.0.0_r36`
- To tag: `android-16.0.0_r4`
- Parent section: GPU syscall filtering
- FAQ scope: shell command / syscall / IOCTL / caller / denial result
- Inherited applicability classification: `OS_UPDATE_ALL_APPS`
- Inherited confidence: Medium

## FAQ

### Q1. syscall は `cd` や `cat` などの command か

短い回答:

異なる。`cd` や `cat` は人が shell に入力する command であり、syscall は program が Linux kernel の機能を利用するための interface である。

説明:

一つの shell command が一つの syscall に置き換わるわけではない。例えば、`cd` は shell 自身が `chdir` syscall を呼ぶ。`cat file.txt` では、shell が `execve` などで `cat` program を起動し、起動された `cat` が `openat`, `read`, `write`, `close` など複数の syscall を使う。

```text
人が shell command を入力
  -> shell が command を解釈
  -> shell 自身が処理、または program を起動
  -> shell / program / library が必要な syscall を呼ぶ
  -> Linux kernel が処理する
```

本件との関係:

GPU syscall filtering は terminal command を禁止する変更ではない。app / library から GPU kernel driver へ送られる低レベル要求を制限する。

### Q2. syscall は shell command が kernel 向け command に変換されたものか

短い回答:

厳密には異なる。shell は command を解釈して処理や program 起動を行い、その shell または起動された program / library が必要な syscall を呼ぶ。

説明:

shell は syscall の呼び出し元になり得るが、shell command を syscall に機械的に翻訳するだけの層ではない。Android app、framework、native library、driver は shell を経由せず syscall を使う。

```text
shell command
  -> shell builtin の処理、または program 起動
  -> 一つ以上の library call / syscall
  -> Linux kernel
```

本件との関係:

Android app の GPU access は通常、shell ではなく Vulkan / OpenGL ES / EGL と userspace driver を経由する。

### Q3. どのような app が `ioctl` を呼ぶか

短い回答:

多くの Android app は framework / library / driver を通じて間接的に `ioctl` を使う。app developer が NDK の C / C++ code から `ioctl()` を直接書くのは、device integration や vendor-specific tooling などの限定された実装である。

代表例:

| app / feature | `ioctl` の使われ方 |
| --- | --- |
| Android app の process communication | Binder library / driver が `/dev/binder` を制御する |
| game / graphics app | Vulkan / OpenGL userspace driver が GPU driver を制御する |
| camera / audio / USB feature | framework、system service、native library が device driver を制御する |
| profiler / benchmark / diagnostics | native code が profiling / instrumentation command を発行し得る |
| vendor-specific middleware / anti-cheat | non-public device command を直接使う可能性がある |

本件で確認する条件:

1. app process または bundled native SDK が `/dev/mali0` にアクセスしているか。
2. その IOCTL が deprecated / development-only / profiling category か。
3. shell / debuggable app ではなく、production の non-debuggable app から発行しているか。

「どこかで `ioctl` が使われている」だけでは影響判定にならない。通常の CameraX / Camera2 / MediaCodec / Vulkan / OpenGL ES 利用で supported driver が内部的に発行する allowed IOCTL と、app / SDK が non-public Mali IOCTL を直接発行する実装を分けて扱う。

### Q4. `/dev/mali0` にアクセスして `ioctl` を呼ぶと何が起きるか

短い回答:

`ioctl` command が許可されれば Mali kernel driver が処理し、拒否されれば caller へ error が返る。その後に app が継続するか、機能停止するか、crash するかは app / SDK の error handling に依存する。

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

| 結果 | driver / app の挙動 |
| --- | --- |
| IOCTL が許可される | driver が memory allocation、GPU job submission、state query など command に対応する処理を行う |
| IOCTL が拒否される | `ioctl()` が失敗し、一般には `-1` と permission-related errno が caller に返る |
| caller が失敗を処理する | optional feature を無効化する、supported API へ fallback する、error を表示するなどして継続できる |
| caller が成功を前提にする | native crash、feature failure、不正な状態などにつながり得る |

判定上の注意:

SELinux denial は policy が command を拒否した evidence だが、それだけで customer impact は確定しない。app / SDK が return value と errno をどう処理するかを確認し、crash、feature failure、graceful fallback、diagnostic-only failure のどれに該当するか判定する。

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

## Verification

実装・依存 SDK・実機 denial の確認手順は primary report の [確認方法](gpu-syscall-filtering.md#確認方法) を参照する。

## References

- [Android 16 - GPU syscall filtering](https://developer.android.com/about/versions/16/behavior-changes-16#gpu-syscall-filtering)
- [Linux system calls manual](https://man7.org/linux/man-pages/man2/syscalls.2.html)
- [Linux ioctl manual](https://man7.org/linux/man-pages/man2/ioctl.2.html)
- [Linux execve manual](https://man7.org/linux/man-pages/man2/execve.2.html)
- [GPU syscall filtering primary report](gpu-syscall-filtering.md)

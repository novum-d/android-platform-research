# GPU syscall filtering - One Page Summary

## Summary

Android 16 の GPU syscall filtering は、Mali GPU の deprecated / development-only / profiling IOCTL を production build で制限する platform-level hardening。公式 scope は Mali GPU を使う Pixel devices、具体的には Pixel 6-9。

通常の Vulkan / OpenGL 利用は影響しないとされる。影響が疑われるのは、app や native library が `/dev/mali0` に直接 IOCTL を発行している場合。

Mali は Arm が設計し、SoC / device vendor が chip に組み込む GPU IP の名称である。通常の app は Mali を直接操作せず、`app -> Vulkan / OpenGL ES / EGL -> userspace driver -> /dev/mali0 kernel driver -> GPU` という supported path を使う。今回の filtering は GPU access や `ioctl` 全体を止めるのではなく、deprecated / development-only / profiling などの IOCTL command を category 単位で制限する。

## Applicability

- Classification: `OS_UPDATE_ALL_APPS`
- Practical conditions:
  - Android 16 以上
  - Pixel 6-9 など Mali GPU device
  - production build
  - app process から `/dev/mali0` に direct IOCTL
  - deprecated / development-only / profiling IOCTL に該当
- Not targetSdk-gated:
  - AOSP public evidence では targetSdkVersion 36 gate は確認できなかった。
  - targetSdkVersion 35 / 36 どちらでも、該当 device / policy / IOCTL 条件を満たせば影響し得る。

## Key Evidence

- Android 16 `system/sepolicy` に `set_xperm_filter(...)` macro が追加されている。
- macro は appdomain に対し、unprivileged IOCTL を allow、restricted IOCTL を deny、instrumentation IOCTL を shell / `runas_app` / allowlist target に限定する。
- Android 15 tag には `set_xperm_filter` は見つからない。
- Pixel `gs101`, `gs201`, `zuma` device repos は `libGLES_mali`, `vulkan.mali`, `/dev/mali0` を示す。
- 具体的な Mali IOCTL category list / vendor policy invocation は公開 checkout では未確認。

## Expected Behavior

| Scenario | Expected behavior |
|---|---|
| Android 16 / Pixel Mali / targetSdkVersion 35 | blocked IOCTL なら deny され得る |
| Android 16 / Pixel Mali / targetSdkVersion 36 | target 35 と同様 |
| Android 16 / debuggable app | profiling IOCTL は許可される想定 |
| Android 16 / shell process | profiling IOCTL は許可される想定 |
| Android 16 / non-debuggable app | profiling / restricted IOCTL は deny される想定 |
| Vulkan / OpenGL | 公式文書上、影響なし |
| non-Mali GPU | 今回の公式 scope 外 |

## Customer Impact

通常の game / graphics app が Vulkan / OpenGL ES の supported APIs だけを使っている場合、影響は想定されない。

要注意:

- `/dev/mali0` を直接 open / ioctl する
- custom GPU middleware / profiling / tracing / diagnostics / benchmark tool を含む
- production app で GPU profiling IOCTL を使う
- anti-cheat / vendor-specific GPU access code がある

主要な diagnostic signal は SELinux denial:

`avc: denied { ioctl } ... path="/dev/mali0" ... tcontext=u:object_r:gpu_device:s0 tclass=chr_file`

## Recommended Actions

- direct Mali IOCTL 使用の有無を native code / bundled SDK / middleware で確認する。
- Pixel 6-9 / Android 16 production build で SELinux denial を確認する。
- denial の `ioctlcmd`, `scontext`, `tcontext`, `tclass`, package name を記録する。
- supported graphics API で代替できる場合は Vulkan / OpenGL / EGL 経由にする。
- blocked IOCTL が必要な場合は bug を file し、`android-partner-security@google.com` に assign する。

Quick verification:

```bash
rg -n -i '/dev/mali0|ioctl\s*\(|mali|gpu_device' <native-source-or-sdk-directory>
rg -a -n -i '/dev/mali0|mali' <directory-containing-so-files>

adb shell getprop ro.product.model
adb shell getprop ro.build.version.release
adb shell getprop ro.build.type
adb logcat -c
# release app で対象操作を実行
adb logcat -d | rg 'avc: denied.*ioctl|/dev/mali0|gpu_device'
```

debuggable app では profiling / instrumentation IOCTL が許可される可能性があるため、non-debuggable release build を必ず含める。denial が出た場合は、Android 15 / 16、targetSdkVersion 35 / 36、debug / release、通常 graphics API / direct native feature を比較し、crash、feature failure、graceful fallback、diagnostic-only failure のどれになるかまで確認する。詳細手順は [primary report の「確認方法」](../../../behavior-changes/target/security/gpu-syscall-filtering.md#確認方法)を参照する。

## Human Decision Placeholder

- Final priority: TBD by human
- Final severity: TBD by human
- Release readiness impact: TBD by human
- Customer communication priority: TBD by human
- Owner decision / next action: TBD by human

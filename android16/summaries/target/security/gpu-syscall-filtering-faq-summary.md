# GPU syscall filtering: FAQ summary

## One Page Summary

### 対象

- Android version: Android 16
- From tag: `android-15.0.0_r36`
- To tag: `android-16.0.0_r4`
- Previous targetSdkVersion: 35
- Target targetSdkVersion: 36
- Official documentation URL: https://developer.android.com/about/versions/16/behavior-changes-16#faq
- Parent section: GPU syscall filtering
- Category: Security
- Report: `android16/behavior-changes/target/security/gpu-syscall-filtering-faq.md`

### 結論

GPU syscall filtering FAQ は、targetSdkVersion 36 で有効になる API behavior change ではなく、Pixel Mali production build と OEM opt-in device に関係する platform-level SELinux / IOCTL policy hardening として扱うのが妥当である。

現在の公式 `#faq` は、依頼文の診断系 FAQ とは異なり、OEM opt-in、AOSP release default、SoC / OEM の IOCTL list 更新責任、Pixel 6-9 適用、performance、userspace / kernel driver との同期を説明している。SELinux denial、supported graphics APIs、AGI / Streamline、bug filing path は親セクション / Testing 側の記述として確認した。

### Applicability Classification

- Primary classification: `OS_UPDATE_ALL_APPS`
- Confidence: Medium

理由:

- 公式文書は targetSdkVersion gate ではなく Pixel Mali / production build / platform-level policy / OEM opt-in を述べている。
- Android 16 `system/sepolicy` には `set_xperm_filter(...)` があり、IOCTL command category ごとの allow / neverallow を表現できる。
- compat framework Change ID は確認できず、targetSdkVersion 36 gate も確認できなかった。

### Facts

- Android 16 `system/sepolicy/public/te_macros` には `set_xperm_filter(target_context, allowed_target, unpriv_ioctls, restricted_ioctls, instrumentation_ioctls)` がある。
- Android 15 `android-15.0.0_r36` の `public/te_macros` には同 macro は確認できない。
- `set_xperm_filter` は restricted IOCTL を `appdomain -allowed_target` に対して `neverallowxperm` し、instrumentation IOCTL は `allowed_target`, `runas_app`, `shell` に許可する。
- Pixel Tensor device repos は Mali EGL/Vulkan stack と `/dev/mali0` を示しており、公式の Pixel 6-9 / Mali scope と整合する。
- 公式文書は Vulkan / OpenGL など supported graphics APIs は影響しないと述べる。
- `/dev/mali0` に対する `avc: denied { ioctl } ... tcontext=u:object_r:gpu_device:s0 tclass=chr_file` は影響判定の主要 signal である。

### Observations

- OS update impact と targetSdkVersion impact は混ぜない。Android 16 production build の Pixel Mali device では targetSdkVersion 35 でも 36 でも direct blocked IOCTL は deny され得る。
- SELinux denial は診断 signal であり、実際の business impact は crash、feature failure、diagnostic-only failure、graceful fallback のどれになるかで変わる。
- Android GPU Inspector / Streamline Performance Analyzer が影響しないという公式記述は、shell / debuggable app exception と整合する。
- non-Pixel / non-Mali / OEM opt-in device では、device policy と SoC / OEM の IOCTL list maintenance 次第で挙動が変わる。

### Hypotheses

- Pixel production build では vendor/arm/mali 側の policy が `set_xperm_filter(gpu_device, ...)` を呼び、Arm r54p2 の IOCTL categorization を取り込んでいる可能性が高い。
- supported graphics APIs が影響しないのは、Vulkan / OpenGL / EGL に必要な IOCTL が unprivileged / allowed category に分類されるためと推測される。
- `ioctlcmd` の具体値を Arm r54p2 document または compiled device policy と照合すれば、denial の category を追加確認できる。

### 期待挙動

| Scenario | Expected behavior |
|---|---|
| Android 16 / targetSdkVersion 35 | Pixel Mali production + blocked IOCTL なら deny され得る |
| Android 16 / targetSdkVersion 36 | target 35 と同様。target SDK 固有ではない |
| Android 15 / targetSdkVersion 36 | Android 16 の `set_xperm_filter` mechanism は未確認 |
| Vulkan / OpenGL ES | 公式文書上、影響なし |
| Android GPU Inspector / Streamline | 公式文書上、影響なし |
| non-debuggable app / profiling IOCTL | deny され得る |
| shell / debuggable app / profiling IOCTL | 許可される想定 |
| non-Pixel Mali / OEM opt-in | OEM policy 次第 |

### Developer Action Candidates

- `/dev/mali0` を直接 open / ioctl している native code / SDK / middleware を確認する。
- Pixel 6-9 / Android 16 production build で `avc: denied { ioctl }` を確認する。
- denial の `ioctlcmd`, `scontext`, `tcontext`, `tclass`, package name を記録する。
- denial が crash / feature failure / graceful fallback のどれに繋がるかを切り分ける。
- 可能なら Vulkan / OpenGL / EGL など supported graphics APIs に移行する。
- blocked IOCTL が必要な場合は再現手順と denial log を添えて bug を file し、`android-partner-security@google.com` に assign する。

### Test Focus

- Android 16 / Pixel 6-9 / production build
- targetSdkVersion 35 vs 36
- debuggable app vs non-debuggable app
- shell process vs app process
- direct `/dev/mali0` access
- deprecated / development-only / profiling / ordinary allowed IOCTL
- Vulkan / OpenGL ES rendering
- Android GPU Inspector / Streamline Performance Analyzer
- SELinux denial 有無と app 実影響
- non-Mali GPU / non-Pixel Mali OEM opt-in / non-opt-in device

### Human Decision Placeholder

- Human decision: 未判断
- Priority: 未判断
- Severity: 未判断
- Release readiness: 未判断
- Customer communication priority: 未判断

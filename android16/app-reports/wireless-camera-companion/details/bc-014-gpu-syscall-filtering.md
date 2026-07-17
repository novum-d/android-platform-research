# BC-014: GPU syscall filtering

## 基本情報

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/16/behavior-changes-16
- Section: GPU syscall filtering

既存調査:
- [android16/behavior-changes/target/security/gpu-syscall-filtering.md](../../../behavior-changes/target/security/gpu-syscall-filtering.md)
- [GPU syscall filtering - 基礎概念 FAQ](../../../behavior-changes/target/security/gpu-syscall-filtering-concepts-faq.md)
- [android16/summaries/target/security/gpu-syscall-filtering-summary.md](../../../summaries/target/security/gpu-syscall-filtering-summary.md)
- [BC-014 GPU syscall filtering - PM向け概要](bc-014-gpu-syscall-filtering-pm-overview.md)

## 対象アプリとの関係

関連するアプリ機能:
- live view rendering。
- native graphics SDK。
- custom profiling / diagnostics。
- game / rendering engine 相当の middleware。

アプリが該当する可能性:
- 通常は低い。direct `/dev/mali0` ioctl を使う SDK / native code がある場合は要注意。

## 適用条件分類

主分類:
- `OS_UPDATE_ALL_APPS`

必要条件:
- Android 16。
- Pixel 6-9 など Mali GPU device。
- production build。
- app process から deprecated / profiling / development-only Mali IOCTL。

Confidence:
- Medium。具体的な vendor policy invocation は公開 checkout だけでは限定的。

## AOSP / 公式根拠

既存 Android16 調査で確認済み:
- `system/sepolicy` の `set_xperm_filter(...)` macro。
- appdomain に対する restricted IOCTL deny。
- shell / `runas_app` / allowlist target の instrumentation IOCTL 例外。
- targetSdkVersion gate は確認できない。

## アプリ影響

想定される影響:
- supported Vulkan / OpenGL ES だけなら低リスク。
- native SDK が direct Mali IOCTL / GPU profiling を production で行う場合、SELinux denial。
- live view rendering 自体より、diagnostics / profiling / vendor-specific GPU access が主なリスク。

推奨対応:
- native SDK / graphics middleware で `/dev/mali0` direct access がないか確認する。
- Pixel Mali device / Android 16 production build で logcat / avc denial を確認する。
- supported graphics APIs へ移行する。

PM向けの変更概要、用語、カメラアプリ影響予測、具体的な調査方法は [PM向け概要](bc-014-gpu-syscall-filtering-pm-overview.md) を参照する。

## テスト観点

- Pixel 6-9 / Android 16 production build。
- live view rendering。
- native graphics SDK init。
- logcat `avc: denied { ioctl } ... path="/dev/mali0"`。
- debuggable / non-debuggable。

## Human Decision

- Final priority: TBD by human
- Release readiness impact: TBD by human

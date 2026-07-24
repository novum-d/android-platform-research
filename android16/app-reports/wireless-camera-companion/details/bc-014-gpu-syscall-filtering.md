# BC-014: GPU syscall filtering

## 基本情報

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/16/behavior-changes-16
- セクション: GPU syscall filtering

既存調査:
- [android16/behavior-changes/target/security/gpu-syscall-filtering.md](../../../behavior-changes/target/security/gpu-syscall-filtering.md)
- [GPU syscall filtering - 基礎概念 FAQ](../../../behavior-changes/target/security/gpu-syscall-filtering-concepts-faq.md)
- [android16/summaries/target/security/gpu-syscall-filtering-summary.md](../../../summaries/target/security/gpu-syscall-filtering-summary.md)
- [BC-014 GPU syscall filtering - PM向け概要](bc-014-gpu-syscall-filtering-pm-overview.md)

## 対象アプリとの関係

関連するアプリ機能:
- ライブビューの描画。
- native graphics SDK。
- 独自の profiling / 診断機能。
- ゲーム / rendering engine 相当の middleware。

アプリが該当する可能性:
- 通常は低い。`/dev/mali0` に対して `ioctl` を直接呼び出す SDK / native code がある場合は注意が必要である。

## 適用条件分類

主分類:
- `OS_UPDATE_ALL_APPS`

必要条件:
- Android 16。
- Pixel 6〜9 などの Mali GPU 搭載端末。
- 製品版ビルド。
- アプリプロセスから、非推奨、profiling 用、開発専用の Mali IOCTL を呼び出す。

Confidence:
- Medium。vendor policy から呼び出す具体的な箇所は、公開されている checkout だけでは十分に確認できない。

## AOSP / 公式根拠

既存 Android16 調査で確認済み:
- `system/sepolicy` の `set_xperm_filter(...)` macro。
- appdomain に対する制限対象 IOCTL の拒否。
- shell / `runas_app` / allowlist 対象に対する instrumentation 用 IOCTL の例外。
- targetSdkVersion gate は確認できない。

## アプリ影響

想定される影響:
- 正式に対応している Vulkan / OpenGL ES だけを使う場合は低リスクである。
- native SDK が製品版アプリで Mali IOCTL の直接呼び出しや GPU profiling を行う場合、SELinux に拒否される可能性がある。
- ライブビューの描画自体よりも、診断、profiling、ベンダー固有の GPU アクセスが主なリスクである。

推奨対応:
- native SDK / graphics middleware が `/dev/mali0` へ直接アクセスしていないか確認する。
- Mali GPU を搭載した Pixel 端末 / Android 16 の製品版ビルドで、logcat の `avc: denied` を確認する。
- 正式に対応しているグラフィックス API へ移行する。

PM向けの変更概要、用語、カメラアプリ影響予測、具体的な調査方法は [PM向け概要](bc-014-gpu-syscall-filtering-pm-overview.md) を参照する。

## テスト観点

- Pixel 6〜9 / Android 16 の製品版ビルド。
- ライブビューの描画。
- native graphics SDK の初期化。
- logcat `avc: denied { ioctl } ... path="/dev/mali0"`。
- debuggable / non-debuggable。

## 人間の判断欄

- 最終優先度: 人間が判断する
- リリース判断への影響: 人間が判断する

# GPU syscall filtering - 1ページ要約

## 要約

Android 16 の GPU syscall filtering は、Mali GPU の非推奨、開発専用、profiling 用の IOCTL を製品版ビルドで制限する、プラットフォーム単位のセキュリティ強化である。公式に示されている対象は Mali GPU を使う Pixel 端末で、具体的には Pixel 6〜9 である。

通常の Vulkan / OpenGL 利用には影響しないと説明されている。影響が疑われるのは、アプリや native library が `/dev/mali0` に対して IOCTL を直接発行している場合である。

カメラアプリ向けの変更概要、用語、影響予測、調査方法は [BC-014 GPU syscall filtering - PM向け概要](../../../app-reports/wireless-camera-companion/details/bc-014-gpu-syscall-filtering-pm-overview.md) を参照する。

Mali は Arm が設計し、SoC または端末メーカーがチップへ組み込む GPU IP の名称である。通常のアプリは Mali を直接操作せず、`app -> Vulkan / OpenGL ES / EGL -> userspace driver -> /dev/mali0 kernel driver -> GPU` という正式に対応している経路を使う。今回の filtering は GPU へのアクセスや `ioctl` 全体を止めるものではなく、非推奨、開発専用、profiling 用などの IOCTL command を分類ごとに制限する。

## 適用条件

- 主分類: `OS_UPDATE_ALL_APPS`
- 実際に影響する条件:
  - Android 16 以上
  - Pixel 6〜9 などの Mali GPU 搭載端末
  - 製品版ビルド
  - アプリプロセスから `/dev/mali0` に IOCTL を直接発行する
  - 非推奨、開発専用、profiling 用のいずれかの IOCTL に該当する
- targetSdkVersion の条件なし:
  - 公開されている AOSP 根拠では、targetSdkVersion 36 の gate は確認できなかった。
  - targetSdkVersion 35 / 36 のどちらでも、該当する端末、policy、IOCTL の条件を満たせば影響する可能性がある。

## 主な根拠

- Android 16 `system/sepolicy` に `set_xperm_filter(...)` macro が追加されている。
- macro は appdomain に対し、権限を必要としない IOCTL を許可し、制限対象の IOCTL を拒否する。また、instrumentation 用 IOCTL は shell / `runas_app` / allowlist の対象に限定する。
- Android 15 tag には `set_xperm_filter` は見つからない。
- Pixel `gs101`, `gs201`, `zuma` device repos は `libGLES_mali`, `vulkan.mali`, `/dev/mali0` を示す。
- 具体的な Mali IOCTL の分類一覧と、vendor policy から呼び出す箇所は、公開されている checkout では未確認である。

## 期待される挙動

| 条件 | 期待される挙動 |
|---|---|
| Android 16 / Pixel Mali / targetSdkVersion 35 | 制限対象の IOCTL は拒否される可能性がある |
| Android 16 / Pixel Mali / targetSdkVersion 36 | targetSdkVersion 35 と同様 |
| Android 16 / debuggable app | profiling 用 IOCTL は許可される想定 |
| Android 16 / shell process | profiling 用 IOCTL は許可される想定 |
| Android 16 / non-debuggable app | profiling 用または制限対象の IOCTL は拒否される想定 |
| Vulkan / OpenGL | 公式文書上、影響なし |
| Mali 以外の GPU | 今回の公式な対象外 |

## 顧客影響

通常のゲームやグラフィックスアプリが、正式に対応している Vulkan / OpenGL ES API だけを使っている場合、影響は想定されない。

要注意:

- `/dev/mali0` を直接開き、`ioctl` を呼び出す
- 独自の GPU middleware、profiling、tracing、診断、ベンチマーク用ツールを含む
- 製品版アプリで GPU profiling 用 IOCTL を使う
- 不正対策やベンダー固有の GPU アクセスコードがある

主な診断情報は、次の SELinux 拒否ログである。

`avc: denied { ioctl } ... path="/dev/mali0" ... tcontext=u:object_r:gpu_device:s0 tclass=chr_file`

## 推奨対応

- Mali IOCTL を直接使用していないか、native code、同梱 SDK、middleware を確認する。
- Pixel 6〜9 / Android 16 の製品版ビルドで SELinux 拒否ログを確認する。
- 拒否ログの `ioctlcmd`、`scontext`、`tcontext`、`tclass`、パッケージ名を記録する。
- 正式に対応しているグラフィックス API で代替できる場合は、Vulkan / OpenGL / EGL 経由へ移行する。
- 制限対象の IOCTL が必要な場合は不具合を報告し、`android-partner-security@google.com` を担当に指定する。

簡易確認:

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

debuggable app では profiling / instrumentation 用 IOCTL が許可される可能性があるため、non-debuggable の製品版ビルドを必ず含める。拒否ログが出た場合は、Android 15 / 16、targetSdkVersion 35 / 36、debug / release、通常のグラフィックス API / native 機能による直接アクセスを比較する。そのうえで、クラッシュ、機能停止、安全な代替処理への切り替え、診断ログだけの失敗のどれに該当するかまで確認する。詳細手順は [主レポートの「確認方法」](../../../behavior-changes/target/security/gpu-syscall-filtering.md#確認方法)を参照する。

## 人間の判断欄

- 最終優先度: 人間が判断する
- 最終影響度: 人間が判断する
- リリース判断への影響: 人間が判断する
- 顧客通知の優先度: 人間が判断する
- 管理者の判断 / 次の対応: 人間が判断する

## 再検証記録（2026-08-22）

- Android 16 の公式 Behavior Change 一覧と最新通常AOSPタグを再確認した。
- 対応する[主レポート](../../../behavior-changes/target/security/gpu-syscall-filtering.md)で official section、AOSP project / remote / checkout、解決済み commit、比較 command、dirty risk を再検証した。
- 主レポートの分類、confidence、未確認事項を維持し、実機未実施の項目を Observed 済みへ変更していない。
- 全件の結果は[再検証台帳](../../../analysis/REVALIDATION_2026-08-22.md)を参照する。

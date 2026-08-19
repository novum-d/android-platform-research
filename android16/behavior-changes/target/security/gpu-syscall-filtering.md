# GPU syscall filtering

## 調査メタデータ

- Android バージョン: Android 16
- バージョンディレクトリ: `android16`
- 比較元タグ: `android-15.0.0_r36`
- 比較先タグ: `android-16.0.0_r4`
- 以前の targetSdkVersion: 35
- 対象 targetSdkVersion: 36
- Behavior Change セクション: GPU syscall filtering
- 公式ドキュメント URL: https://developer.android.com/about/versions/16/behavior-changes-16#gpu-syscall-filtering
- カメラアプリの PM 向け概要: [BC-014 GPU syscall filtering - PM向け概要](../../../app-reports/wireless-camera-companion/details/bc-014-gpu-syscall-filtering-pm-overview.md)
- 公式ドキュメントの分類: Security
- 適用条件分類: `OS_UPDATE_ALL_APPS`
- Confidence: Medium


Confidence の注記: 公式文書は、Pixel の Mali GPU、製品版ビルド、プラットフォーム単位の policy を対象としており、targetSdkVersion の gate は示していない。公開されている AOSP の `system/sepolicy` では IOCTL xperm filter mechanism を確認できたが、Pixel Mali 用の具体的な IOCTL 分類、allowlist、denylist は公開 checkout 内で確認できなかった。そのため Confidence は Medium とする。

## 公式ドキュメントの確認

2026-07-03 の確認に加え、2026-07-17 に公式ドキュメントの GPU syscall filtering セクションを再確認した。対象ページは 2026-07-14 UTC 更新として表示されていた。

確認した公式記述:

- Mali GPU の攻撃対象領域を堅牢化するため、非推奨または GPU 開発専用の Mali GPU IOCTL が製品版ビルドで拒否される。
- GPU profiling 用 IOCTL は、shell process または debuggable application に制限される。
- 詳細は SAC update のプラットフォーム単位の policy を参照する。
- 対象は Mali GPU を使う Pixel 端末で、具体的には Pixel 6〜9 である。
- Arm r54p2 release の `Documentation/ioctl-categories.rst` に IOCTL categorization がある。
- 正式に対応している graphics API、Vulkan、OpenGL には影響しない想定である。
- Streamline Performance Analyzer と Android GPU Inspector は影響しない想定。
- `/dev/mali0` に対する SELinux `avc: denied { ioctl }` が出た場合、影響を受けている可能性がある。
- 制限対象の IOCTL が必要な場合は不具合を報告し、`android-partner-security@google.com` を担当に指定する。

依頼文に記載された原文と適用条件の詳細について、公式本文との実質的な差は見つからなかった。

## 補足: Mali GPU と GPU syscall filtering の位置づけ

### Mali GPU とは

GPU は、画面描画、3D rendering、画像処理などを並列実行するプロセッサである。Mali は [Arm の GPU 製品](https://www.arm.com/products)であり、SoC ベンダーや端末メーカーがチップへ組み込む GPU IP の名称である。Android 固有の API 名ではなく、すべての Android 端末が Mali GPU を使うわけではない。

今回公式に示された対象は、Mali GPU を搭載する Pixel 6〜9 である。Pixel 以外の Mali 搭載端末では、OEM / SoC ベンダーが同等の policy に opt-in しているかによって適用が変わる。Mali 以外の GPU は、今回確認した公式な対象外である。

通常、アプリは Mali GPU や device node を直接操作せず、次の正式に対応している graphics API の経路を使う。

```text
app / game / graphics framework
  -> Vulkan / OpenGL ES / EGL
  -> Mali userspace driver
  -> ioctl system call
  -> /dev/mali0 kernel driver
  -> Mali GPU
```

Vulkan / OpenGL ES / EGL を使用していても、driver 内部では IOCTL が使われる場合がある。ただし、今回の変更は GPU device へのアクセス全体や `ioctl` system call 全体を禁止するものではない。通常描画に必要な IOCTL を許可し、非推奨、開発専用、profiling 用などの分類を command 単位で制限する仕組みである。そのため、正式に対応している graphics API だけを使う通常のアプリには影響しない、という公式説明と整合する。

### syscall と IOCTL

system call は、userspace の app / library が Linux kernel に処理を依頼する interface である。`ioctl` はその一種で、file descriptor に対して device 固有の control command を送る。Mali の場合は `/dev/mali0` を open した後、`ioctlcmd` で GPU driver の操作を指定する。

「GPU syscall filtering」という名称だが、実際の policy は GPU 関連 system call を一律拒否するのではなく、SELinux extended permission により `ioctlcmd` ごとに許可・拒否を分ける。

| IOCTL category | Android 16 での想定 |
|---|---|
| 通常 graphics API に必要な unprivileged / allowed IOCTL | 許可 |
| deprecated IOCTL | production build で block |
| GPU development-only / restricted IOCTL | production build で block |
| profiling / instrumentation IOCTL | shell process または debuggable app に限定 |

通常の retail device で配布用 release app を動かす条件では、shell / debuggable app 向け例外を前提にしない。debug build だけで profiling 機能が動いても、non-debuggable release build では拒否される可能性があるため、両方を分けて確認する。

## 理解補助資料

shell command、syscall、IOCTL の関係、`ioctl` を使う app、IOCTL が許可・拒否された後の挙動は、primary report と分けた [GPU syscall filtering - 基礎概念 FAQ](gpu-syscall-filtering-concepts-faq.md) を参照する。

## AOSP Evidence Scope

Primary evidence:

- `platform/system/sepolicy`
  - `android-15.0.0_r36`
  - `android-16.0.0_r4`

Supplemental device evidence:

- `device/google/gs101`
- `device/google/gs201`
- `device/google/zuma`

Pixel device repos は `android-16.0.0_r4` tag が確認できなかったため、Pixel Mali device scope の補助 evidence として current checkout を確認した。tag 比較 evidence としては扱わない。

Public repository limitation:

- `vendor/arm/mali/gs101` / `vendor/arm/mali/valhall` は device makefile から参照されるが、今回確認した公開 AOSP URL では repository を取得できなかった。
- そのため、Mali IOCTL の具体的 category list、deprecated / development-only / profiling IOCTL の個別 command list は public AOSP evidence では未確認。

## Facts

### Android 16 sepolicy mechanism

Android 16 `system/sepolicy/public/te_macros` には `set_xperm_filter(target_context, allowed_target, unpriv_ioctls, restricted_ioctls, instrumentation_ioctls)` が追加されている。

この macro は次を行う。

- `allowxperm appdomain <target_context>:chr_file ioctl { unpriv_ioctls }`
- `neverallowxperm { appdomain -<allowed_target> } <target_context>:chr_file ioctl { restricted_ioctls }`
- `<allowed_target>` には restricted IOCTL を許可する
- instrumentation IOCTL は `<allowed_target>`, `runas_app`, `shell` に許可する
- `appdomain -<allowed_target> -runas_app -shell` には instrumentation IOCTL を `neverallowxperm` で禁止する

Macro comment は `instrumentation_ioctls` を development 用 IOCTL と説明し、shell または debuggable applications から許可されると説明している。

Reviewed source:

- `system/sepolicy/public/te_macros`
  - `set_xperm_filter(...)`

### Android 15 baseline

`android-15.0.0_r36` の `system/sepolicy/public/te_macros` には `set_xperm_filter` は存在しない。

Android 15 / Android 16 の `private/app.te` はどちらも appdomain に `gpu_device:chr_file rw_file_perms` を許可している。

Interpretation:

- GPU device への通常アクセス許可そのものを Android 16 で完全に取り除く変更ではない。
- Android 16 では xperm filter mechanism により、device/vendor policy が特定 IOCTL command を allow / deny できるようになっている。

### Pixel Mali device evidence

Pixel Tensor device repos の current checkout では、Mali stack の採用が確認できる。

`device/google/gs101/device.mk`:

- `TARGET_USES_VULKAN = true`
- `vendor/arm/mali/gs101`
- `libGLES_mali`
- `vulkan.mali`
- `ro.hardware.vulkan=mali`
- `ro.hardware.egl = mali`
- `graphics.gpu.profiler.support=true`

`device/google/gs201/device.mk`:

- `vendor/arm/mali/valhall`
- `libGLES_mali`
- `vulkan.mali`
- `ro.hardware.egl = mali`
- `ro.hardware.vulkan = mali`
- `graphics.gpu.profiler.support=true`

`device/google/zuma/device.mk`:

- `vendor/arm/mali/valhall`
- `libGLES_mali`
- `vulkan.mali`
- `ro.hardware.egl=mali`
- `ro.hardware.vulkan=mali`
- `graphics.gpu.profiler.support=true`

各 device repo の ueventd rc は `/dev/mali0` を定義している。

- `device/google/gs101/conf/ueventd.gs101.rc`: `/dev/mali0 0666 system system`
- `device/google/gs201/conf/ueventd.gs201.rc`: `/dev/mali0 0666 system system`
- `device/google/zuma/conf/ueventd.zuma.rc`: `/dev/mali0 0666 system system`

この evidence は公式文書の Pixel Mali device scope と `/dev/mali0` denial 例に整合する。

### Supported graphics APIs

Pixel device makefiles は `libGLES_mali` と `vulkan.mali` を package に含め、Vulkan / OpenGL ES capability XML を copy している。公式文書は supported graphics APIs は影響しないと述べる。

Public AOSP evidence からは、Vulkan / OpenGL API call path が blocked IOCTL list とどのように切り分けられているかまでは確認できなかった。ただし `set_xperm_filter` の設計上、`unpriv_ioctls` を allow し、restricted / instrumentation IOCTL だけを制限する構造であるため、通常 graphics API に必要な IOCTL は unprivileged / allowed category に含める前提の policy と解釈できる。

### SELinux denial signal

公式文書の denial 例は次の形である。

- `{ ioctl }`
- `path="/dev/mali0"`
- `tcontext=u:object_r:gpu_device:s0`
- `tclass=chr_file`
- `scontext=u:r:untrusted_app_25:...`
- `ioctlcmd=...`

AOSP evidence:

- `gpu_device` は `system/sepolicy/public/device.te` で `dev_type` として定義される。
- appdomain は GPU device に file permission を持つが、Android 16 の xperm filter mechanism で IOCTL command 単位の allow / deny が可能。

### Compat framework / targetSdkVersion

公式 compat framework changes ページでは、GPU syscall filtering に対応する Change ID は確認できなかった。

AOSP public evidence でも、targetSdkVersion 36 を直接確認する app compat gate は見つからなかった。`set_xperm_filter` の comment には allowed_target について「allowlist of services, or gating by a target SDK」と書かれているが、今回確認できた public repos では Pixel Mali policy の具体的 invocation が未確認であり、実際に target SDK gate が使われている証拠はない。

## Observations

### これは targetSdkVersion-gated app behavior ではなく platform policy hardening

公式文書も AOSP evidence も、targetSdkVersion 36 以上に限定する直接 gate を示していない。実質条件は次の組み合わせである。

- Android 16 以上の production build
- Pixel 6-9 など Mali GPU device
- GPU syscall filtering policy が組み込まれている device build
- app process から `/dev/mali0` に direct IOCTL を発行する
- IOCTL が restricted または instrumentation category に該当する

そのため primary classification は `OS_UPDATE_ALL_APPS` とする。ただし、すべての Android 16 devices / all apps に広く影響するという意味ではなく、「targetSdkVersion に依存しない OS / device policy change」としての分類である。

### Shell / debuggable app exception

`set_xperm_filter` は instrumentation IOCTL を `{ allowed_target runas_app shell }` に許可し、その他 appdomain からは `neverallowxperm` で禁止する。`runas_app` は debuggable app と関連する domain であり、公式文書の「shell process or debuggable applications」に整合する。

### Production build condition

公式文書は production builds で block と説明する。AOSP public macro 自体には build variant 条件はない。production / userdebug / eng の差は device/vendor policy の組み込み方、debug policy、または build configuration 側で表現される可能性があるが、今回の public evidence では具体的な Mali policy invocation が未確認である。

### Pixel Mali scope

Pixel device repos は Mali driver / EGL / Vulkan stack と `/dev/mali0` を示すため、公式の Pixel 6-9 scope と整合する。Pixel 9 については public repo 名と product mapping の完全な tag evidence は確認できていないが、公式文書を根拠として Pixel 6-9 を対象 scope とする。

### Non-Mali / non-Pixel

公式文書は Pixel devices using the Mali GPU と明記している。AOSP public evidence では Adreno など non-Mali GPU への適用は確認していない。OEM が同様の policy を opt-in / vendor policy として組み込む可能性はあるが、今回の evidence では device-specific と扱う。

## Hypotheses

- Pixel production build では vendor/arm/mali 側の policy が `set_xperm_filter(gpu_device, ...)` を呼び、Arm r54p2 の IOCTL categorization に従って unprivileged / restricted / instrumentation IOCTL を分類している可能性が高い。
- Vulkan / OpenGL / EGL が影響しないのは、これらの supported API path が unprivileged / allowed IOCTL のみを使うよう分類されているためと推測される。
- Android GPU Inspector / Streamline Performance Analyzer が影響しないのは、shell または debuggable app / profiling path が instrumentation IOCTL を許可される設計のためと推測される。

これらは公式文書と `set_xperm_filter` macro からの推論であり、具体的な Mali vendor policy / Arm r54p2 `ioctl-categories.rst` / 実機 denial で確認すべきである。

## Applicability Classification

Primary classification: `OS_UPDATE_ALL_APPS`

理由:

- 公式文書は targetSdkVersion gate ではなく Pixel Mali / production build / platform-level policy を述べる。
- AOSP public evidence では targetSdkVersion 36 gate は確認できない。
- 影響は app の targetSdkVersion より、device build policy、SELinux domain、debuggable 状態、shell / app process、発行 IOCTL category に依存する。

追加条件:

- Android 16 以上
- GPU syscall filtering policy が有効な production build
- Pixel 6-9 など Mali GPU device
- app process から Mali GPU IOCTL を direct に発行
- deprecated / development-only / profiling IOCTL に該当

Compat framework:

- 該当 Change ID は確認できず。
- default state / force-enable / force-disable は compat framework evidence なし。

## Expected Behavior Matrix

| Scenario | Expected behavior |
|---|---|
| Android 16 / targetSdkVersion 35 | Pixel Mali production + blocked IOCTL なら deny。target SDK 35 でも影響し得る |
| Android 16 / targetSdkVersion 36 | Pixel Mali production + blocked IOCTL なら deny。target SDK 36 固有ではない |
| Android 15 / targetSdkVersion 36 | `set_xperm_filter` は Android 15 tag に存在せず、同じ platform-level filtering は確認できない |

## Detailed Scenario Matrix

| Scenario | Expected behavior |
|---|---|
| Android 16 / Pixel Mali / production build / targetSdkVersion 35 | direct blocked IOCTL は SELinux deny され得る |
| Android 16 / Pixel Mali / production build / targetSdkVersion 36 | target 35 と同様。target SDK 固有ではない |
| Android 16 / Pixel Mali / debuggable app | profiling / instrumentation IOCTL は許可される想定 |
| Android 16 / Pixel Mali / non-debuggable app | profiling / instrumentation IOCTL は deny される想定 |
| Android 16 / Pixel Mali / shell process | profiling / instrumentation IOCTL は許可される想定 |
| deprecated IOCTL | production build で block される想定 |
| development-only IOCTL | production build で block される想定 |
| profiling IOCTL | shell / debuggable app 以外では制限される想定 |
| ordinary allowed IOCTL | unprivileged IOCTL として allow される想定 |
| Vulkan API | 公式文書上、影響なし |
| OpenGL ES API | 公式文書上、影響なし |
| Android GPU Inspector | 公式文書上、影響なし |
| Streamline Performance Analyzer | 公式文書上、影響なし |
| Android 16 / non-Mali GPU | 今回の公式 scope 外 |
| Android 16 / non-Pixel Mali / OEM opt-in | OEM policy 次第で類似影響の可能性 |
| Android 16 / non-Pixel Mali / OEM opt-in なし | 今回の公式 scope では影響なし |
| Android 15 / Pixel Mali | Android 16 の `set_xperm_filter` mechanism は未確認 |
| SELinux denial appears | `/dev/mali0` / `gpu_device` / `ioctl` denial は影響 signal |
| SELinux denial absent because allowed API / shell / debuggable path | 通常 graphics API または profiling exception として問題なし |

## Developer Impact

影響対象:

- NDK で Mali GPU device node に直接アクセスするアプリ
- custom native rendering / GPU middleware を含むアプリ
- GPU profiling / tracing / diagnostics tool
- benchmarking / performance analysis tool
- anti-cheat / device diagnostics / vendor tooling
- non-debuggable production app で profiling IOCTL を使うアプリ
- Pixel 6-9 ユーザーに配布されるアプリ
- non-Pixel / OEM Mali device を対象にするアプリ

非影響と考えられる対象:

- Vulkan / OpenGL ES など supported graphics APIs だけを使う通常の game / graphics app
- Android GPU Inspector を通常の supported flow で使う開発者
- Streamline Performance Analyzer を supported profiling flow で使う開発者
- shell process または debuggable app として profiling IOCTL を使う開発用 flow

## Recommended Action Candidates

- `/dev/mali0` を直接 open / ioctl している native code がないか確認する。
- app / SDK / middleware / anti-cheat / benchmark library が non-public Mali IOCTL に依存していないか確認する。
- Pixel 6-9 / Android 16 production build で logcat / dmesg の SELinux denial を確認する。
- `avc: denied { ioctl }` の `ioctlcmd`, `scontext`, `tcontext`, `tclass`, package name を記録する。
- supported graphics API で代替できる場合は Vulkan / OpenGL / EGL 経由に移行する。
- blocked IOCTL が業務上必要な場合は、再現手順と denial log を添えて bug を file し、`android-partner-security@google.com` に assign する。

## 確認方法

### 1. Source code / bundled native library の静的確認

まず、app 本体だけでなく、bundled SDK、graphics middleware、profiling、benchmark、anti-cheat などの native component を対象にする。

```bash
rg -n -i '/dev/mali0|ioctl\s*\(|mali|gpu_device' <native-source-or-sdk-directory>
rg -a -n -i '/dev/mali0|mali' <directory-containing-so-files>
```

`ioctl(` だけでは GPU 用か判断できないため、該当 call の file descriptor が `/dev/mali0` 由来か、Mali vendor library 経由かを call site まで追う。`.so` に文字列がない場合でも direct IOCTL を否定できないため、依存 SDK の仕様確認と実機検証を併用する。

### 2. Device / build 条件の確認

Pixel 6-9 の Android 16 production build を主対象とし、比較用に Android 15、debuggable app、可能なら non-Mali device を用意する。

```bash
adb shell getprop ro.product.model
adb shell getprop ro.build.version.release
adb shell getprop ro.build.version.sdk
adb shell getprop ro.build.type
adb shell getprop ro.hardware.egl
adb shell getprop ro.hardware.vulkan
```

`ro.build.type=user` は retail production build の確認材料になる。GPU property が空の場合は `adb shell dumpsys SurfaceFlinger` などの renderer 情報も確認し、端末型番と合わせて Mali device か判断する。

### 3. Release app での denial log 確認

debuggable app には profiling / instrumentation IOCTL の例外があるため、配布相当の non-debuggable release build を必ず含める。対象操作の直前に log を clear し、再現後の denial を取得する。

```bash
adb logcat -c
# GPU rendering / profiling / SDK feature などの対象操作を実行
adb logcat -d | rg 'avc: denied.*ioctl|/dev/mali0|gpu_device'
```

主な判定 signal:

- `{ ioctl }`
- `path="/dev/mali0"`
- `tcontext=u:object_r:gpu_device:s0`
- `tclass=chr_file`
- `ioctlcmd=...`
- `scontext=...` と package name

device 権限上取得できる場合は kernel / audit log も補助確認する。denial が見つかったら、時刻、package、操作手順、`ioctlcmd`、app の debuggable 状態、device / build を一組で記録する。

### 4. 実影響と適用条件の切り分け

同じ操作を、少なくとも次の組み合わせで比較する。

| 比較 | 確認目的 |
|---|---|
| Android 15 vs Android 16 | OS update による差か |
| targetSdkVersion 35 vs 36 | target SDK 固有ではないことを確認できるか |
| debug build vs non-debuggable release build | profiling / instrumentation exception の差か |
| 通常 Vulkan / OpenGL rendering vs direct native feature | supported API path は正常で direct IOCTL path だけ失敗するか |
| Mali device vs non-Mali device | Mali policy に依存する差か |

denial の有無だけで customer impact を確定せず、対応する機能が crash、feature failure、graceful fallback、diagnostic-only failure のどれになるかまで確認する。denial がなく対象機能も正常なら、その device / build / app version / 操作範囲では影響を検出しなかった、と記録する。全 IOCTL や全 device で非影響と一般化はしない。

## Test Considerations

- Android 15 端末上の targetSdkVersion 35
- Android 16 端末上の targetSdkVersion 35
- Android 16 端末上の targetSdkVersion 36
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較
- Pixel 6 / 7 / 8 / 9 の Mali GPU 端末
- production build
- userdebug / eng build
- debuggable app
- non-debuggable app
- shell process
- `/dev/mali0` への direct access
- deprecated IOCTL の発行
- development-only IOCTL の発行
- profiling IOCTL の発行
- ordinary allowed IOCTL の発行
- Vulkan rendering
- OpenGL ES rendering
- Android GPU Inspector attach / capture
- Streamline Performance Analyzer profiling
- SELinux denial log の有無
- `avc: denied { ioctl }` の `ioctlcmd` / `scontext` / `tcontext` / `tclass`
- fallback behavior when IOCTL is denied
- app crash / error handling / feature disable path
- non-Mali GPU 端末での比較
- OEM opt-in 端末 / non-opt-in 端末での比較

## 結論

- GPU syscall filtering は targetSdkVersion 36 固有の API 挙動変更ではなく、Mali GPU を搭載した Pixel の製品版ビルドに対する、プラットフォーム単位の SELinux / IOCTL policy 強化として説明するのが適切である。
- Android 16 の `system/sepolicy` には `set_xperm_filter` macro が追加され、制限対象の IOCTL と instrumentation 用 IOCTL を、appdomain に対して command 単位で制限できる仕組みを確認できる。
- Pixel の device repository は Mali EGL/Vulkan stack と `/dev/mali0` を示しており、公式に示された Pixel Mali の対象範囲と整合する。
- 具体的な Mali IOCTL の分類一覧と、Pixel の製品版 policy から呼び出す箇所は、公開されている AOSP checkout では確認できなかった。そのため、非推奨、開発専用、profiling 用 IOCTL の個別判定には、実機の拒否ログ、vendor policy、Arm r54p2 の文書による追加確認が必要である。
- 正式に対応している Vulkan / OpenGL の利用には、公式文書上は影響しない。影響が疑われるのは、Mali IOCTL の直接使用、特に non-debuggable の製品版アプリから制限対象または instrumentation 用 IOCTL を使用する場合である。

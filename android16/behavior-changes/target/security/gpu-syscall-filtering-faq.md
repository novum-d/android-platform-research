# GPU syscall filtering: FAQ

## 調査メタデータ

- Android version: Android 16
- Version directory: `android16`
- From tag: `android-15.0.0_r36`
- To tag: `android-16.0.0_r4`
- Previous targetSdkVersion: 35
- Target targetSdkVersion: 36
- Behavior Change section: FAQ
- Parent section: GPU syscall filtering
- Official documentation URL: https://developer.android.com/about/versions/16/behavior-changes-16#faq
- Official documentation category: Security
- Report output file: `android16/behavior-changes/target/security/gpu-syscall-filtering-faq.md`
- Summary output file: `android16/summaries/target/security/gpu-syscall-filtering-faq-summary.md`
- Applicability classification: `OS_UPDATE_ALL_APPS`
- Confidence: Medium


Confidence note: 公式文書は Pixel Mali / production build / platform-level policy / OEM opt-in を述べており、targetSdkVersion 36 gate は述べていない。AOSP public `system/sepolicy` では IOCTL xperm filter mechanism を確認できたが、Pixel Mali 用の具体的 IOCTL category list / allowlist / denylist は公開 checkout 内では確認できなかった。そのため confidence は Medium とする。

## Official Documentation Review

2026-07-03 に公式ドキュメントの `#gpu-syscall-filtering` から `#faq` までを再確認した。対象ページは 2026-07-01 UTC 更新として表示されていた。

重要な差分:

- 依頼文の Original statements のうち、SELinux denial、supported graphics APIs、Android GPU Inspector / Streamline Performance Analyzer、bug filing path に関する記述は、現在の公式 HTML では `#faq` ではなく親セクションの本文および `#testing` subsection にある。
- 現在の `#faq` subsection は、OEM opt-in、AOSP release default、SoC / OEM の IOCTL list 更新責任、Pixel in-market devices、performance、userspace / kernel driver と IOCTL list の同期、restricted / instrumentation IOCTL の OEM categorization を扱っている。
- したがって本 report では、`#faq` の実本文を一次対象としつつ、依頼文の診断系 Original statements は親セクション / Testing statement として検証した。

確認した公式 FAQ 記述:

- この policy change は全 OEM に強制適用されるのではなく、利用したい OEM が opt-in できる。
- platform-level change は新しい AOSP release に含まれるが、vendor が適用したい場合は codebase 側で opt-in する。
- SoC / OEM は driver release に合わせて IOCTL list を device ごとに更新する必要がある。
- Arm は driver update に合わせて公開 IOCTL list を更新するが、OEM は自社 SEPolicy に取り込み、必要な custom IOCTL を list に追加する必要がある。
- Pixel in-market devices using the Mali GPU、Pixel 6-9 には適用され、user action は不要。
- Mali GPU / GFXBench で test され、GPU performance の measurable change は観測されなかった。
- allowed IOCTL list は userspace と kernel driver が support する IOCTL と同期している必要がある。
- restricted / instrumentation の分類は、Arm list を参考にしつつ OEM / SoC が userspace Mali libraries の構成に基づいて決める。

親セクション / Testing で確認した公式記述:

- deprecated または GPU development-only の Mali GPU IOCTL は production builds で block される。
- GPU profiling 用 IOCTL は shell process または debuggable applications に制限される。
- 対象は Mali GPU を使う Pixel devices、具体的には Pixel 6-9。
- supported graphics APIs、Vulkan、OpenGL には影響しない想定。
- Streamline Performance Analyzer と Android GPU Inspector は影響しない想定。
- `/dev/mali0` に対する SELinux `avc: denied { ioctl }` が出た場合、影響を受けている可能性がある。
- blocked IOCTL が必要な場合は bug を file し、`android-partner-security@google.com` に assign する。

## AOSP Evidence Scope

Primary evidence:

- `platform/system/sepolicy`
  - `android-15.0.0_r36`
  - `android-16.0.0_r4`

Supplemental device evidence:

- `device/google/gs101`
- `device/google/gs201`
- `device/google/zuma`

Frameworks / API evidence:

- `frameworks-base` は clean checkout であり、`android-15.0.0_r36` と `android-16.0.0_r4` tag を確認した。
- `frameworks-base/core/api/current.txt` の Android 16 API surface には GPU syscall filtering / Mali IOCTL / `/dev/mali0` に直接対応する public SDK API は確認できなかった。検出された `GPU` は graphics buffer / OpenGL / performance headroom など既存 API 文脈であり、本件の SEPolicy hardening とは直接対応しない。

Public repository limitation:

- `vendor/arm/mali/gs101` / `vendor/arm/mali/valhall` は device makefile から参照されるが、今回確認した公開 AOSP URL では repository を取得できなかった。
- そのため、Mali IOCTL の具体的 category list、deprecated / development-only / profiling IOCTL の個別 command list、Pixel production policy の具体的 invocation は public AOSP evidence では未確認。

## Facts

### Android 16 sepolicy mechanism

Android 16 `system/sepolicy/public/te_macros` には `set_xperm_filter(target_context, allowed_target, unpriv_ioctls, restricted_ioctls, instrumentation_ioctls)` が存在する。

Reviewed source:

- `system/sepolicy/public/te_macros`
  - Symbol: `set_xperm_filter(...)`
  - Relevance: device/vendor policy が appdomain に対して character device の IOCTL command を category ごとに allow / deny する entry point。

この macro は次を行う。

- `allowxperm appdomain <target_context>:chr_file ioctl { unpriv_ioctls }`
- `neverallowxperm { appdomain -<allowed_target> } <target_context>:chr_file ioctl { restricted_ioctls }`
- `<allowed_target>` には restricted IOCTL を許可する
- instrumentation IOCTL は `<allowed_target>`, `runas_app`, `shell` に許可する
- `appdomain -<allowed_target> -runas_app -shell` には instrumentation IOCTL を `neverallowxperm` で禁止する

AOSP source context:

- File / symbol / entry point: `system/sepolicy/public/te_macros`, `set_xperm_filter(...)`
- Why relevant: 公式文書の deprecated / development-only / profiling Mali IOCTL block を、SELinux extended permission で表現する platform policy mechanism。
- Baseline Android behavior: Android 15 tag には同 macro が確認できない。
- Target Android behavior: Android 16 tag では IOCTL category ごとの allow / neverallow mechanism が存在する。
- Diff kind: added behavior。
- Classification support: targetSdkVersion gate ではなく SEPolicy mechanism として追加されているため、target SDK ではなく OS / device policy 条件に依存する。

### Android 15 baseline

`android-15.0.0_r36` の `system/sepolicy/public/te_macros` には `set_xperm_filter` は存在しない。

Android 15 / Android 16 の `private/app.te` はどちらも appdomain に `gpu_device:chr_file rw_file_perms` を許可している。

Interpretation:

- GPU device への通常アクセス許可そのものを Android 16 で完全に取り除く変更ではない。
- Android 16 では xperm filter mechanism により、device/vendor policy が特定 IOCTL command を allow / deny できるようになっている。

### SELinux denial diagnostic

公式文書の denial 例は次の形である。

```text
avc: denied { ioctl } for path="/dev/mali0" dev="tmpfs" ino=... ioctlcmd=...
scontext=u:r:untrusted_app_25:s0:...
tcontext=u:object_r:gpu_device:s0
tclass=chr_file
permissive=0
app=...
```

AOSP evidence:

- `system/sepolicy/public/device.te` は `gpu_device` を device type として定義する。
- Android 16 `set_xperm_filter` は `chr_file ioctl` に対して command 単位の `allowxperm` / `neverallowxperm` を定義できる。
- したがって `/dev/mali0` が `gpu_device` として label され、appdomain から denied IOCTL が発行されると、公式例のような `tcontext=u:object_r:gpu_device:s0 tclass=chr_file` の denial が出ることは SEPolicy model と整合する。

制限:

- `ioctlcmd` の具体値が deprecated / development-only / profiling のどの category に属するかは、公開 checkout だけでは確認できなかった。Arm r54p2 `Documentation/ioctl-categories.rst`、vendor policy、または実機上の compiled policy で照合が必要。

### Shell / debuggable app exception

`set_xperm_filter` は instrumentation IOCTL を `{ <allowed_target> runas_app shell }` に許可し、その他の appdomain には `neverallowxperm` を置く。

AOSP source context:

- File / symbol / entry point: `system/sepolicy/public/te_macros`, `set_xperm_filter(...)`
- Why relevant: 公式文書の「GPU profiling IOCTL は shell process または debuggable applications に制限される」を裏付ける。
- Baseline Android behavior: Android 15 tag では同 macro が確認できない。
- Target Android behavior: Android 16 tag では instrumentation IOCTL に shell / runas_app exception がある。
- Diff kind: added behavior。
- Classification support: shell / debuggable condition は SEPolicy domain 条件であり、targetSdkVersion 条件ではない。

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

この evidence は公式文書の Pixel Mali device scope と `/dev/mali0` denial 例に整合する。ただし、これら Pixel device repos では `android-16.0.0_r4` tag が確認できなかったため、tag diff evidence ではなく補助 evidence として扱う。

### FAQ-specific OEM / SoC responsibility

公式 FAQ は、この policy が全 OEM に強制されるものではなく、OEM opt-in で利用可能な hardening method であると述べる。また、SoC / OEM は driver release に合わせて IOCTL list を device ごとに更新し、userspace / kernel driver の support と同期させる必要がある。

AOSP evidence:

- `set_xperm_filter` は generic macro であり、具体的な target context、allowed target、unprivileged / restricted / instrumentation IOCTL list は macro caller 側が与える設計である。
- つまり、実際の Mali IOCTL list と category は device / vendor policy 側に置かれる構造であり、公式 FAQ の「OEM / SoC が取り込む・更新する」説明と整合する。

### Supported graphics APIs

公式文書は Vulkan / OpenGL など supported graphics APIs は影響しないと述べる。

AOSP / device evidence:

- Pixel device makefiles は `libGLES_mali` と `vulkan.mali` を package に含め、Vulkan / EGL Mali stack を構成している。
- `set_xperm_filter` は全 IOCTL を一律 deny する仕組みではなく、`unpriv_ioctls` を appdomain に allow し、restricted / instrumentation category を別扱いにする。

Interpretation:

- supported graphics API に必要な IOCTL は unprivileged / allowed category に分類される前提の policy と解釈できる。
- ただし、公開 AOSP evidence から Vulkan / OpenGL の実際の IOCTL command list までは追跡できなかった。

### Compat framework / targetSdkVersion

公式 compat framework changes ページでは、GPU syscall filtering に対応する Change ID は確認できなかった。

AOSP public evidence でも、targetSdkVersion 36 を直接確認する app compat gate は見つからなかった。`set_xperm_filter` の comment には allowed target について target SDK gating の可能性が書かれているが、今回確認できた public repos では Pixel Mali policy の具体的 invocation が未確認であり、実際に target SDK gate が使われている証拠はない。

### API surface

`frameworks-base/core/api/current.txt` の Android 16 public API surface には、GPU syscall filtering / Mali IOCTL / `/dev/mali0` に対応する public SDK API 追加・変更は確認できなかった。

この項目は SDK API change ではなく、SEPolicy / SAC / device policy hardening として扱うのが妥当である。

## Observations

### FAQ は diagnostics だけでなく OEM implementation boundary を説明している

依頼文では FAQ を「影響判定、SELinux denial、supported graphics API 非影響、bug filing path」として扱っているが、現在の公式 `#faq` は OEM / SoC 側の実装責任を詳述している。

そのため、customer-facing explanation では次を分ける必要がある。

- アプリ開発者向け診断: `/dev/mali0` の `avc: denied { ioctl }` が出るか。
- アプリ開発者向け非影響: Vulkan / OpenGL など supported graphics APIs は影響しない想定。
- OEM / device 実装差: Pixel 6-9 は user action 不要で適用、他 OEM / SoC は opt-in と IOCTL list maintenance 次第。

### これは targetSdkVersion-gated app behavior ではなく platform policy hardening

公式文書も AOSP evidence も、targetSdkVersion 36 以上に限定する直接 gate を示していない。実質条件は次の組み合わせである。

- Android 16 以上の production build
- Pixel 6-9 など Mali GPU device
- GPU syscall filtering policy が組み込まれている device build
- app process から `/dev/mali0` に direct IOCTL を発行する
- IOCTL が restricted または instrumentation category に該当する

そのため primary classification は `OS_UPDATE_ALL_APPS` とする。ただし、すべての Android 16 devices / all apps に広く影響するという意味ではなく、「targetSdkVersion に依存しない OS / device policy change」としての分類である。

### SELinux denial は診断 signal であり、business impact そのものではない

`avc: denied { ioctl }` は該当 IOCTL が block されたことを示す強い診断 signal である。一方、アプリの実影響は以下で変わる。

- deny された IOCTL が必須機能か、optional diagnostics / profiling か。
- app が fallback できるか。
- crash するか、feature を disable するか、performance metrics の取得だけ失敗するか。
- denial が production user build で発生するか、debug / test build のみで発生するか。

### Shell / debuggable path と AGI / Streamline

Android 16 `set_xperm_filter` の instrumentation IOCTL exception は shell / runas_app を許可する。これは Android GPU Inspector や Streamline Performance Analyzer が supported profiling flow で影響を受けない、という公式記述に整合する。

ただし、non-debuggable production app 自身が profiling IOCTL を直接使う場合は、同じ profiling category でも deny される可能性がある。

### Production build condition

公式文書は production builds で block と説明する。AOSP public macro 自体には build variant 条件はない。production / userdebug / eng の差は device/vendor policy の組み込み方、debug policy、または build configuration 側で表現される可能性があるが、今回の public evidence では具体的な Mali policy invocation が未確認である。

### OEM opt-in と Pixel scope

公式 FAQ は「OEM は opt-in できる」と述べる一方、Pixel 6-9 については「user action 不要で適用」と述べる。つまり、Pixel Mali devices では Google device build 側で適用済み、他 OEM / SoC は採用・IOCTL list maintenance 次第と説明するのが適切である。

## Hypotheses

- Pixel production build では vendor/arm/mali 側の policy が `set_xperm_filter(gpu_device, ...)` を呼び、Arm r54p2 の IOCTL categorization に従って unprivileged / restricted / instrumentation IOCTL を分類している可能性が高い。
- Vulkan / OpenGL / EGL が影響しないのは、これらの supported API path が unprivileged / allowed IOCTL のみを使うよう分類されているためと推測される。
- Android GPU Inspector / Streamline Performance Analyzer が影響しないのは、shell または debuggable app / profiling path が instrumentation IOCTL を許可される設計のためと推測される。
- `ioctlcmd` の具体値を Arm r54p2 `Documentation/ioctl-categories.rst` または device compiled policy と照合できれば、denial が deprecated / development-only / profiling のどれに該当するかをより高 confidence で説明できる。

これらは公式文書と `set_xperm_filter` macro からの推論であり、具体的な Mali vendor policy / Arm r54p2 `ioctl-categories.rst` / 実機 denial で確認すべきである。

## Applicability Classification

Primary classification: `OS_UPDATE_ALL_APPS`

理由:

- 公式文書は targetSdkVersion gate ではなく Pixel Mali / production build / platform-level policy / OEM opt-in を述べる。
- AOSP public evidence では targetSdkVersion 36 gate は確認できない。
- 影響は app の targetSdkVersion より、device build policy、SELinux domain、debuggable 状態、shell / app process、発行 IOCTL category に依存する。

追加条件:

- Android 16 以上
- GPU syscall filtering policy が有効な production build
- Pixel 6-9 など Mali GPU device、または OEM が同等 policy に opt-in した Mali device
- app process から Mali GPU IOCTL を direct に発行
- deprecated / development-only / profiling IOCTL に該当
- profiling IOCTL の場合、shell process / debuggable app では許可される可能性がある

Compat framework:

- 該当 Change ID は確認できず。
- default state / force-enable / force-disable は compat framework evidence なし。

## Expected Behavior Matrix

| Scenario | Expected behavior |
|---|---|
| Android 16 / targetSdkVersion 35 | Pixel Mali production + blocked IOCTL なら deny。target SDK 35 でも影響し得る |
| Android 16 / targetSdkVersion 36 | Pixel Mali production + blocked IOCTL なら deny。target SDK 36 固有ではない |
| Android 15 / targetSdkVersion 36 | Android 16 の `set_xperm_filter` mechanism は Android 15 tag では確認できず、同じ platform-level filtering は未確認 |

## Detailed Scenario Matrix

| Scenario | Expected behavior |
|---|---|
| Android 16 / Pixel Mali / production build / targetSdkVersion 35 | direct blocked IOCTL は SELinux deny され得る |
| Android 16 / Pixel Mali / production build / targetSdkVersion 36 | target 35 と同様。target SDK 固有ではない |
| Android 16 / Pixel Mali / debuggable app | profiling / instrumentation IOCTL は許可される想定 |
| Android 16 / Pixel Mali / non-debuggable app | profiling / instrumentation IOCTL は deny される想定 |
| Android 16 / Pixel Mali / shell process | profiling / instrumentation IOCTL は許可される想定 |
| Android 16 / Pixel Mali / deprecated IOCTL | production build で block される想定 |
| Android 16 / Pixel Mali / development-only IOCTL | production build で block される想定 |
| Android 16 / Pixel Mali / profiling IOCTL | shell / debuggable app 以外では制限される想定 |
| Android 16 / Pixel Mali / ordinary allowed IOCTL | unprivileged IOCTL として allow される想定 |
| Android 16 / Pixel Mali / Vulkan API | 公式文書上、影響なし |
| Android 16 / Pixel Mali / OpenGL ES API | 公式文書上、影響なし |
| Android 16 / Pixel Mali / Android GPU Inspector | 公式文書上、影響なし |
| Android 16 / Pixel Mali / Streamline Performance Analyzer | 公式文書上、影響なし |
| Android 16 / non-Mali GPU | 今回の公式 Pixel Mali scope 外 |
| Android 16 / non-Pixel Mali device with OEM opt-in | OEM policy と IOCTL list 次第で類似影響の可能性 |
| Android 16 / non-Pixel Mali device without OEM opt-in | 今回の公式 scope では影響なし |
| Android 15 / Pixel Mali / same app behavior | Android 16 の `set_xperm_filter` mechanism は未確認 |
| SELinux denial appears | `/dev/mali0` / `gpu_device` / `ioctl` denial は影響 signal |
| SELinux denial absent because allowed API / shell / debuggable path | 通常 graphics API または profiling exception として問題なし |
| SELinux denial appears but app has graceful fallback | denial は発生しているが business impact は限定的 |
| SELinux denial appears and app crashes / feature fails | blocked IOCTL が実機能に直結している可能性が高い |

## Customer-facing Impact

OS update impact と targetSdkVersion impact は分けて説明する。

- Android 16 へ OS update しただけでも、Pixel 6-9 など Mali GPU production build で該当 IOCTL を direct に使う app / native library は影響を受け得る。
- targetSdkVersion 36 化そのものが GPU syscall filtering を有効化する evidence は確認できない。
- Vulkan / OpenGL ES だけを使う通常の game / graphics app は、公式文書上は影響しない。
- Android GPU Inspector / Streamline Performance Analyzer は supported profiling path では影響しないとされる。
- `/dev/mali0` の `avc: denied { ioctl }` は影響判定の主要 signal だが、app crash / feature failure / graceful fallback のどれになるかは app 実装次第である。
- non-Pixel / non-Mali / OEM opt-in device では、device policy と SoC / OEM の IOCTL list maintenance 次第で挙動が変わる。

## Impacted App Categories

影響対象:

- NDK で Mali GPU device node に直接アクセスするアプリ
- custom native rendering / GPU middleware を含むアプリ
- GPU profiling / tracing / diagnostics tool
- benchmarking / performance analysis tool
- anti-cheat / device diagnostics / vendor tooling
- non-debuggable production app で profiling IOCTL を使うアプリ
- Pixel 6-9 ユーザーに配布されるアプリ
- non-Pixel / OEM Mali device を対象にするアプリ
- SELinux denial を監視する QA / support / observability team

非影響と考えられる対象:

- Vulkan / OpenGL ES など supported graphics APIs だけを使う通常の game / graphics app
- Android GPU Inspector を通常の supported flow で使う開発者
- Streamline Performance Analyzer を supported profiling flow で使う開発者
- shell process または debuggable app として profiling IOCTL を使う開発用 flow

## Recommended Action Candidates

- `/dev/mali0` を直接 open / ioctl している native code がないか確認する。
- app / SDK / middleware / anti-cheat / benchmark library が non-public Mali IOCTL に依存していないか確認する。
- Pixel 6-9 / Android 16 production build で logcat / audit log の SELinux denial を確認する。
- `avc: denied { ioctl }` の `ioctlcmd`, `scontext`, `tcontext`, `tclass`, package name を記録する。
- denial が crash、feature failure、diagnostic-only failure、graceful fallback のどれに該当するかを切り分ける。
- supported graphics API で代替できる場合は Vulkan / OpenGL / EGL 経由に移行する。
- blocked IOCTL が業務上必要な場合は、再現手順と denial log を添えて bug を file し、`android-partner-security@google.com` に assign する。

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
- denial が app crash / feature failure / graceful fallback に繋がるか
- bug filing に必要な最小情報
- fallback behavior when IOCTL is denied
- non-Mali GPU 端末での比較
- OEM opt-in 端末 / non-opt-in 端末での比較

## Conclusions

- 現在の公式 `#faq` は、依頼文の診断系 FAQ ではなく、主に OEM / SoC / Pixel 適用範囲 / IOCTL list maintenance を説明している。診断系記述は親セクションの `#testing` にある。
- GPU syscall filtering FAQ は targetSdkVersion 36 固有の app behavior change ではなく、Pixel Mali production build と OEM opt-in device に関係する platform-level SELinux / IOCTL policy hardening として説明するのが適切である。
- Android 16 `system/sepolicy` には `set_xperm_filter` macro が追加され、restricted IOCTL と instrumentation IOCTL を appdomain に対して command 単位で制限できる仕組みが確認できる。
- Pixel device repos は Mali EGL/Vulkan stack と `/dev/mali0` を示し、公式 Pixel Mali scope と整合する。
- SELinux denial は impacted app の主要診断 signal だが、実際の customer impact は app が該当 IOCTL にどれだけ依存するかで変わる。
- 具体的な Mali IOCTL category list と Pixel production policy invocation は公開 AOSP checkout では確認できなかったため、deprecated / development-only / profiling IOCTL の個別判定は実機 denial、vendor policy、Arm r54p2 documentation で追加確認が必要。

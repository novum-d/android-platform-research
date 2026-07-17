# カメラ連携アプリ Android 16 Behavior Changes 調査レポート

## 基本情報（Metadata）

### 対象アプリ（Target App）

アプリ名:
- 非記載。本文・ファイル名には対象アプリを特定できる名称を含めない。

パッケージ名:
- 非記載。

現在の targetSdkVersion:
- 要確認。比較上は previous targetSdkVersion 35 を前提にする。

想定する更新後 targetSdkVersion:
- 36

主な機能領域:
- [x] Bluetooth / Connectivity
- [x] Wi-Fi / local network
- [x] 画像 / 動画転送
- [x] リモート操作
- [x] Companion device / pairing flow
- [x] WebView / Network / TLS
- [x] Large Screen / Window
- [x] Native library / JNI / third-party SDK
- [x] 定期処理 / polling / retry / sync
- [ ] 通知
- [ ] Foreground Service
- [ ] カメラ / マイク
- [ ] メディア / Audio
- [ ] Contacts / Calendar / Storage
- [ ] 認証 / Credential
- [ ] その他:

### 調査対象 Android バージョン（Android Versions）

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:
- `android16/AGENTS.md` は To tag を `android-16.0.0_r1` としているが、本アプリ別調査では既存 Android16 調査と同じく `android-16.0.0_r4` を参照する。

### 調査日（Investigation Date）

2026-07-07（2026-07-16 更新）

### 調査範囲（Scope）

対象にした Behavior Change 文書:
- https://developer.android.com/about/versions/16/behavior-changes-all
- https://developer.android.com/about/versions/16/behavior-changes-16

対象外にした領域:
- 対象アプリのソースコード、APK、manifest、通信先一覧、実機ログの直接確認。
- アプリ固有の最終 priority / severity / release readiness 判断。
- 対象アプリを特定できる名称、パッケージ名、ストア URL の記載。

アプリコード確認の有無:
- なし。

確認したアプリ実装範囲:
- API usage: 未確認。カメラ連携アプリとして Bluetooth、Wi-Fi / LAN、HTTP(S)、画像 / 動画転送、リモート操作、companion pairing を利用する前提で仮評価。`ScheduledThreadPoolExecutor` / `ScheduledExecutorService` / `Timer` の `scheduleAtFixedRate` による定期 polling、接続監視、同期、retry、cleanup の有無は要確認。
- Manifest: 未確認。`NEARBY_WIFI_DEVICES`、Bluetooth / Nearby devices、local network testing、orientation / resize / aspect ratio、edge-to-edge opt-out、predictive back opt-out は要確認。
- Permissions: 未確認。Bluetooth runtime permissions、Nearby devices、location、future local network permission、storage / MediaStore 利用は要確認。
- Background / service behavior: 未確認。接続復旧、定期 polling / retry / sync / cleanup、通知経由起動、Intent forwarding、PendingIntent / IntentSender 利用は要確認。
- Device / form factor assumptions: スマートフォン中心と推定。ただし tablet / foldable / desktop windowing / virtual display projection は要確認。
- 実機・自動テスト: 未実施。

---

# エグゼクティブサマリー（Executive Summary）

対象アプリ種別では、Android 16 の影響は Bluetooth reconnect / pairing、local network opt-in testing、native library 16 KB page size、large screen / edge-to-edge / predictive back、Intent security、fixed-rate 定期処理に集中する。

OS アップデートだけで影響しうる項目は、Bluetooth bond loss handling、Companion Device Manager discovery timeout、Intent redirection hardening、16 KB page-size compatibility mode、ART internal changes、virtual device owner projection override、GPU syscall filtering である。targetSdkVersion 36 へ上げる場合は、adaptive layouts、edge-to-edge opt-out 無効化、predictive back default enabled、Safer Intents opt-in、MediaStore version lockdown、fixed-rate work scheduling optimization などを別途確認する。

Android 16 の Local Network Permission は Android 17 と異なり、現時点では default-on の targetSdkVersion 36 behavior ではない。Android 16 r4 では `RESTRICT_LOCAL_NETWORK` compat flag による opt-in testing behavior として扱い、カメラ探索、カメラ側 Wi-Fi AP、mDNS / NSD / `.local`、ローカル IP への HTTP / socket、ライブビュー、画像 / 動画転送をテスト対象にする。

対象アプリの manifest / API usage は未確認であるため、最終判断には実装棚卸しと実機テストが必要である。特に Bluetooth Classic / BLE / CDM、native `.so`、Intent router、fixed orientation / non-resizable UI、`scheduleAtFixedRate` による定期処理の有無を優先して確認する。

---

# 影響一覧（Impact Overview）

| ID | Behavior Change | 関連アプリ機能 | 適用分類 | アプリ影響 | 対応候補 | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| BC-001 | Local Network Permission | カメラ探索、Wi-Fi 接続、mDNS / NSD / `.local`、ローカル IP 通信、画像 / 動画転送 | UNKNOWN_NEEDS_MORE_EVIDENCE（Android 16 current opt-in） | 要確認。Android 16 default-on ではなく opt-in testing impact | `RESTRICT_LOCAL_NETWORK` enable、`NEARBY_WIFI_DEVICES` granted / denied、future permission UX を確認 | Medium |
| BC-002 | Improved bond loss handling | Bluetooth pairing、再接続、bond loss recovery | OS_UPDATE_ALL_APPS | 影響ありの可能性 | remote bond loss、auth failure、system dialog、`BOND_NONE` 依存を確認 | High |
| BC-003 | New intents to handle bond loss and encryption changes | Bluetooth bond loss / encryption change signal | OS_UPDATE_ALL_APPS（API 採用条件あり） | 要確認。新 signal 採用機会 | `ACTION_KEY_MISSING` / `ACTION_ENCRYPTION_CHANGE` と fallback を確認 | Medium |
| BC-004 | Companion apps no longer notified of discovery timeouts | CDM pairing / association discovery | OS_UPDATE_ALL_APPS | CDM 利用時は影響あり | `RESULT_DISCOVERY_TIMEOUT` 依存を `RESULT_USER_REJECTED` も含めて見直す | High |
| BC-005 | Improved security against Intent redirection attacks | deep link router、SDK router、notification workflow、nested Intent | OS_UPDATE_ALL_APPS | 要確認。unsafe nested Intent forwarding で影響 | nested Intent validation / IntentSanitizer / opt-out 最小化 | High |
| BC-006 | Safer Intents | 外部アプリ連携、explicit Intent、receiver / service / activity filter | TARGET_SDK_36_CONDITIONAL | opt-in している場合は影響 | `android:intentMatchingFlags` 利用有無と cross-app intent を確認 | Medium |
| BC-007 | 16 KB page size compatibility mode | JNI / native SDK、画像・動画処理、codec、ML、DB / crypto | OS_UPDATE_ALL_APPS | native `.so` があれば要確認 | 16 KB alignment、third-party SDK update、`android:pageSizeCompat` を確認 | High |
| BC-008 | ART internal changes | hidden API、hooking、hotfix、instrumentation、monitoring SDK | MAINLINE_OR_PLAY_SYSTEM_UPDATE | 要確認。依存 SDK 次第 | ART internals / non-SDK / hidden API 使用を棚卸し | High |
| BC-009 | Adaptive layouts | live view、remote control、画像一覧、固定向き UI | TARGET_SDK_36_CONDITIONAL | large screen で要確認 | tablet / foldable / multi-window、orientation / resize 制限を確認 | High |
| BC-010 | Virtual device owner overrides | PC / VR / car / Chromebook への projection | OS_UPDATE_ALL_APPS | projection 利用時に要確認 | external display / virtual device owner で layout を確認 | High |
| BC-011 | Edge-to-edge opt-out going away | 全画面 / live view / image viewer / setup flow UI | TARGET_SDK_36_CONDITIONAL | opt-out 依存なら影響あり | insets / system bar / IME 対応へ移行 | High |
| BC-012 | Predictive back default enabled | setup wizard、camera connection flow、image viewer、custom back | TARGET_SDK_36_CONDITIONAL | legacy back handling 依存なら影響あり | OnBackInvoked / AndroidX back APIs へ移行 | High |
| BC-013 | MediaStore version lockdown | 端末内写真 / 動画 cache、MediaStore sync | TARGET_SDK_36_CONDITIONAL | `MediaStore#getVersion()` 利用時のみ要確認 | opaque token として扱い、format parse をやめる | High |
| BC-014 | GPU syscall filtering | live view / rendering / native graphics / profiling SDK | OS_UPDATE_ALL_APPS | 通常 API 利用は低リスク。direct Mali ioctl は要注意 | Pixel Mali device で SELinux denial を確認 | Medium |
| BC-015 | Fixed rate work scheduling optimization | camera status polling、接続監視、同期、retry、cleanup、metrics upload | TARGET_SDK_36_CONDITIONAL | executor / Timer の `scheduleAtFixedRate` missed backlog に依存する場合は処理回数が減る。API は `@Deprecated` ではないが Lint `DiscouragedApi` と同じ問題領域 | API 利用箇所を棚卸しし、fixed-delay 移行可否と Change ID 288912692 / 351566728 enabled / disabled を確認 | High |

---

# アプリ影響サマリー（App Impact Summary）

## OS アップデートだけで影響しうる項目（OS Update Impact）

| Behavior Change | 影響条件 | 想定されるアプリ影響 | 推奨確認 |
| --- | --- | --- | --- |
| Improved bond loss handling | Android 16、bonded Bluetooth device、remote bond loss / auth failure | 自動 bond removal / automatic re-pairing / immediate `BOND_NONE` 前提が崩れる | カメラ側 bond reset、factory reset、range out 後 reconnect を確認 |
| Companion apps discovery timeout | Android 16、CDM association discovery | timeout が `RESULT_DISCOVERY_TIMEOUT` ではなく timeout dialog dismissal 後の `RESULT_USER_REJECTED` に見える | no-device discovery、manual stop、custom timeout UI、analytics を確認 |
| Intent redirection hardening | Android 16、untrusted nested Intent Activity launch | external Intent extras をそのまま起動する router が block / exception になる可能性 | nested Intent validation と legitimate flow を確認 |
| 16 KB page size compatibility mode | Android 16、16 KB page-size device、4 KB-aligned native libs | startup dialog、compat mode、native crash / performance 差 | APK / AAB の `.so` alignment と 16 KB device startup を確認 |
| ART internal changes | Android 16 または Android 12+ updated ART module、ART internals 依存 | hidden API / runtime internals 依存 SDK が crash する可能性 | SDK 棚卸し、hidden API warning / JNI failure を確認 |
| Virtual device owner overrides | Android 16、trusted virtual device owner projection | fixed orientation / non-resizable / aspect ratio 制限が projection 上で無視される | PC / car / Chromebook / VR projection があるか確認 |
| GPU syscall filtering | Android 16、Mali GPU production build、direct `/dev/mali0` ioctl | unsupported graphics profiling / middleware が SELinux deny | native graphics SDK と Pixel Mali device logs を確認 |

## targetSdkVersion 36 更新で影響しうる項目（Target SDK Impact）

| Behavior Change | targetSdkVersion 条件 | 追加条件 | 想定されるアプリ影響 | 推奨確認 |
| --- | --- | --- | --- | --- |
| Adaptive layouts | targetSdkVersion 36 以上 | Android 16、`sw >= 600dp`、non-game、opt-out なし | live view / remote control / image list が large screen bounds に伸びる | fixed orientation、`resizeableActivity=false`、min/max aspect ratio を確認 |
| Edge-to-edge opt-out going away | targetSdkVersion 36 以上 | Android 16、`windowOptOutEdgeToEdgeEnforcement` 依存 | system bars / navigation bar / IME と UI が重なる | setup / live view / image viewer の insets を確認 |
| Predictive back default enabled | targetSdkVersion 36 以上 | Android 16、legacy `onBackPressed` / `KEYCODE_BACK` 依存 | back handling、connection flow、image viewer の戻る挙動が変わる | AndroidX / OnBackInvoked へ移行し、temporary opt-out を限定 |
| Safer Intents | targetSdkVersion 36 / compile SDK 36 採用時に opt-in しやすい | Android 16、`android:intentMatchingFlags` opt-in、cross-app explicit Intent | external app / SDK からの explicit Intent が filter mismatch で block | manifest opt-in と intent filter を確認 |
| MediaStore version lockdown | targetSdkVersion 36 以上 | Android 16、`MediaStore#getVersion()` 利用 | version string parsing / cross-app comparison が壊れる | opaque token として扱う |
| Fixed rate work scheduling optimization | targetSdkVersion 36 以上 | Android 16、executor / Timer の `scheduleAtFixedRate` 利用、freeze / suspend 等で複数 period を missed | 復帰時の immediate catch-up が最大 1 回となり、polling / retry / sync / cleanup の実行回数が減る可能性 | missed 回数を callback の catch-up に依存させず、最終処理時刻から必要量を計算する |

## Android 16 current opt-in / future readiness として扱う項目

| Behavior Change | 判断 | カメラ連携アプリへの意味 | 推奨確認 |
| --- | --- | --- | --- |
| Local Network Permission | Android 16 current stage は default-on ではなく opt-in testing | Android 17 以降の本対応に向け、Android 16 で LAN access failure を先行再現できる | `RESTRICT_LOCAL_NETWORK` enabled、`NEARBY_WIFI_DEVICES` granted / denied、mDNS / NSD / socket / HTTP を確認 |

## 要確認の項目（Needs More Evidence）

| Behavior Change | 不足している根拠 | 次に確認すること | Blocker |
| --- | --- | --- | --- |
| Local network | manifest、LAN API usage、`NEARBY_WIFI_DEVICES`、mDNS / NSD / `.local` / socket / HTTP | source / APK で local network access 箇所を検索 | 対象アプリ実装未確認 |
| Bluetooth bond loss / new intents | Bluetooth Classic / BLE / CDM 利用有無、receiver 実装 | remote bond loss、encryption change、receiver / permission を確認 | 対象アプリ実装未確認 |
| CDM timeout | `CompanionDeviceManager#associate()` 利用有無 | timeout result handling と custom UI を確認 | 対象アプリ実装未確認 |
| Native / ART | bundled `.so`、third-party SDK、hooking / hotfix / instrumentation | APK `.so` alignment、hidden API / JNI usage を確認 | 対象アプリ・SDK 実装未確認 |
| Intent security | nested Intent forwarding / router / SDK dispatcher | `getParcelableExtra(Intent)` から launch する箇所を確認 | 対象アプリ実装未確認 |
| Large screen / UI | manifest restrictions、fixed aspect live view、edge-to-edge opt-out、legacy back handling | tablet / foldable / Android 16 target 36 で確認 | 対象アプリ実装未確認 |
| Fixed-rate 定期処理 | `ScheduledThreadPoolExecutor` / `ScheduledExecutorService` / `Timer` の `scheduleAtFixedRate` 利用有無、missed backlog 依存 | camera status polling、接続監視、同期、retry、cleanup、metrics upload の実装を検索 | 対象アプリ実装未確認 |

---

# 推奨テストマトリクス（Recommended Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | Compat / flag | 目的（Purpose） | 確認すべき機能 | 期待挙動（Expected behavior） |
| --- | --- | --- | --- | --- | --- |
| Android 15 | 35 | default | baseline | Bluetooth pairing、Wi-Fi 接続、画像 / 動画転送、リモート操作、back / UI | 現行挙動を記録 |
| Android 16 | 35 | default | OS update impact | bond loss、CDM timeout、Intent redirection、16 KB device、ART、projection | targetSdkVersion を変えずに OS 差分を確認 |
| Android 16 | 36 | default | targetSdkVersion migration impact | adaptive layouts、edge-to-edge、predictive back、MediaStore、Safer Intents opt-in、fixed-rate 定期処理 | target 36 固有または opt-in 差分を確認。`scheduleAtFixedRate` は復帰時 immediate catch-up が最大 1 回 |
| Android 16 | 35 / 36 | `RESTRICT_LOCAL_NETWORK` enabled | local network opt-in testing | camera discovery、mDNS / NSD、local IP HTTP / socket、transfer | permission denied / granted の failure surface を先行確認 |
| Android 16 | 36 | force-enabled / disabled where available | isolated change test | edge-to-edge、predictive back、adaptive layout、MediaStore、fixed-rate 定期処理 | compat flag がある項目は個別に再現 |

追加テスト:
- Android 16 / 16 KB page-size device: `.so` alignment、startup dialog、native crash。
- Bluetooth remote bond deleted / factory reset: system dialog、`ACTION_KEY_MISSING`、`BOND_NONE`、GATT / profile callback。
- CDM no-device discovery: timeout dialog、`RESULT_USER_REJECTED`、app retry。
- Intent router: nested Intent to exported / non-exported component、URI grant、ClipData。
- Large screen: tablet / foldable / desktop windowing / virtual projection、camera live view、image viewer、setup flow。
- Edge-to-edge: status bar、navigation bar、IME、display cutout、landscape live view。
- Predictive back: setup wizard、connection flow、image viewer、unsaved transfer / cancel flow。
- MediaStore: `getVersion()` format parsing、cache invalidation。
- ART / native: hidden API warning、JNI failure、third-party SDK init、native `.so` load。
- Fixed-rate work: app process を freeze / suspend 相当の状態に置き、復帰時の camera status polling、接続 retry、同期、cleanup の実行回数とデータ整合性を executor Change ID 288912692 と Timer Change ID 351566728 の enabled / disabled で比較。

---

# 個別調査結果（Per Behavior Change Investigation）

| ID | Behavior Change | 詳細 |
| --- | --- | --- |
| BC-001 | Local Network Permission | [details/bc-001-local-network-permission.md](details/bc-001-local-network-permission.md) |
| BC-002 | Improved bond loss handling | [details/bc-002-improved-bond-loss-handling.md](details/bc-002-improved-bond-loss-handling.md) |
| BC-003 | New intents to handle bond loss and encryption changes | [details/bc-003-new-intents-bond-loss-encryption.md](details/bc-003-new-intents-bond-loss-encryption.md) |
| BC-004 | Companion apps no longer notified of discovery timeouts | [details/bc-004-companion-device-discovery-timeout.md](details/bc-004-companion-device-discovery-timeout.md) |
| BC-005 | Improved security against Intent redirection attacks | [details/bc-005-intent-redirection-hardening.md](details/bc-005-intent-redirection-hardening.md) |
| BC-006 | Safer Intents | [details/bc-006-safer-intents.md](details/bc-006-safer-intents.md) |
| BC-007 | 16 KB page size compatibility mode | [details/bc-007-16kb-page-size-compatibility-mode.md](details/bc-007-16kb-page-size-compatibility-mode.md) |
| BC-008 | ART internal changes | [details/bc-008-art-internal-changes.md](details/bc-008-art-internal-changes.md) |
| BC-009 | Adaptive layouts | [details/bc-009-adaptive-layouts-large-screen.md](details/bc-009-adaptive-layouts-large-screen.md) |
| BC-010 | Virtual device owner overrides | [details/bc-010-virtual-device-owner-overrides.md](details/bc-010-virtual-device-owner-overrides.md) |
| BC-011 | Edge-to-edge opt-out going away | [details/bc-011-edge-to-edge-opt-out.md](details/bc-011-edge-to-edge-opt-out.md) |
| BC-012 | Predictive back default enabled | [details/bc-012-predictive-back.md](details/bc-012-predictive-back.md) |
| BC-013 | MediaStore version lockdown | [details/bc-013-mediastore-version-lockdown.md](details/bc-013-mediastore-version-lockdown.md) |
| BC-014 | GPU syscall filtering | [Details](details/bc-014-gpu-syscall-filtering.md) / [PM向け概要](details/bc-014-gpu-syscall-filtering-pm-overview.md) |
| BC-015 | Fixed rate work scheduling optimization | [details/bc-015-fixed-rate-work-scheduling-optimization.md](details/bc-015-fixed-rate-work-scheduling-optimization.md) |

---

# 顧客向け説明（Customer-facing Explanation）

Android 16 では、カメラ連携アプリに対して「すぐに targetSdkVersion 36 化で壊れる項目」と「Android 16 OS 上で条件が揃うと影響する項目」と「Android 16 では opt-in testing に留まるが将来対応の準備になる項目」を分けて説明する必要がある。

ローカルネットワークについては、Android 16 current stage では Android 17 のような default runtime permission enforcement ではない。Android 16 r4 では `RESTRICT_LOCAL_NETWORK` を明示的に enable した opt-in testing として、カメラ探索、カメラ側 Wi-Fi AP、ローカル IP / `.local` / mDNS / NSD、画像 / 動画転送、ライブビュー、リモート操作の failure handling を先行検証する位置づけである。

Bluetooth については、Android 16 OS update だけで remote bond loss handling と CDM timeout result が変わり得る。カメラの factory reset、bond reset、範囲外からの復帰、初回 discovery timeout など、onboarding と reconnect のユーザー体験を重点的に確認する。

targetSdkVersion 36 へ移行する場合は、large screen / edge-to-edge / predictive back が UI に直接影響する。カメラ live view、remote control、image viewer、setup wizard は fixed orientation、system bar avoidance、legacy back handling への依存が表に出やすいため、Android 16 / targetSdkVersion 36 の実機確認が必要である。

定期処理については、executor または `Timer#scheduleAtFixedRate` で camera status polling、接続監視、同期、retry、cleanup 等を実装している場合、targetSdkVersion 36 では freeze / suspend 復帰時に missed execution が最大 1 回しか即時実行されない。missed period 数だけ処理する設計は callback の catch-up 回数に依存させず、最終処理時刻と現在時刻から必要量を明示的に計算する必要がある。
Android Studio の `DiscouragedApi` 警告はこの Behavior Change と無関係ではない。短周期 polling は、前回の実際の開始時刻基準でよければ `Timer#schedule(..., period)`、前回処理完了から一定間隔を空けたければ `ScheduledExecutorService#scheduleWithFixedDelay` を移行候補とする。WorkManager / JobScheduler は本件の移行先ではなく、process death 後も再実行する別の background work 要件がある場合に限って検討する。

Native / SDK については、16 KB page-size device、ART internal changes、GPU syscall filtering を分けて確認する。画像・動画処理、codec、ML、暗号化、DB、monitoring / profiling / anti-tamper SDK が bundled native library や runtime internals に依存している場合、OS update だけでも互換性リスクになり得る。

---

# One Page Summary 用メモ（One Page Summary Notes）

## 対象アプリで重要な変更

- 最重要: Android 16 OS update の Bluetooth bond loss handling と CDM timeout result。
- 高優先: targetSdkVersion 36 の adaptive layouts、edge-to-edge、predictive back。
- 高優先: 16 KB page-size device 上の native library alignment。
- 中優先: Intent redirection hardening / Safer Intents。
- 中優先: ART internal changes / third-party SDK。
- 要確認: fixed-rate work scheduling optimization。`scheduleAtFixedRate` と missed backlog 依存の有無で対応要否が決まる。
- 先行検証: Local Network Permission は Android 16 current stage では opt-in testing。
- 条件付き: virtual device owner projection、MediaStore version lockdown、GPU syscall filtering。

## 対応要否

- 必須確認候補: Bluetooth reconnect / pairing、CDM timeout、native `.so` alignment、large screen UI、edge-to-edge insets、predictive back。
- 推奨確認: local network opt-in testing、nested Intent validation、MediaStore version usage、ART internal dependency、`scheduleAtFixedRate` 利用箇所と freeze / suspend 復帰時の実行回数。
- 不要候補: CDM 不使用、native code なし、MediaStore#getVersion 不使用、`scheduleAtFixedRate` 不使用、direct Mali ioctl 不使用なら該当項目の優先度は下げられる。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Critical / High / Medium / Low

判断（Decision）:
- Explain / Monitor / Ignore / Further investigation required

顧客説明優先度（Customer communication priority）:
- TBD by human

リリース判定（Release readiness decision）:
- TBD by human

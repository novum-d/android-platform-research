# Companion apps no longer notified of discovery timeouts 調査レポート

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:
- `android16/AGENTS.md` は To tag を `android-16.0.0_r1` としているが、本調査では依頼スコープに従い公開済み Android 16 tag として `android-16.0.0_r4` を使用した。
- AOSP checkout `frameworks-base` は clean で、`android-15.0.0_r36` / `android-16.0.0_r4` tag の存在を確認した。

Previous targetSdkVersion:
- 35

Target targetSdkVersion:
- 36

### Behavior Change 文書（Behavior Change Source）

Document:
- https://developer.android.com/about/versions/16/behavior-changes-all#companion-device-timeout

Page:
- Behavior changes: all apps

Category:
- Security

Section:
- Companion apps no longer notified of discovery timeouts

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `OS_UPDATE_ALL_APPS`

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 16 に OS アップデートしただけで適用されるか | Yes / Conditional | 公式 all apps ページ掲載。AOSP の CDM discovery UI / service path で Android 15 から Android 16 への runtime behavior 差分を確認した。影響は `CompanionDeviceManager#associate()` を使う discovery flow に限られる。 |
| targetSdkVersion 36 以上が必要か | No | `CompanionAssociationActivity` / `CompanionDeviceDiscoveryService` / `CompanionDeviceManager` の確認範囲で targetSdkVersion 36 gate は見つからない。 |
| 追加の実行時条件があるか | Yes | Companion Device Manager の pairing / association discovery flow を使い、timeout result や探索時間に依存している場合。 |
| Compat Change ID が関係するか | No / Not found | 公式 compat framework changes ページで `Companion` / `DISCOVERY` / `TIMEOUT` 関連の該当項目は見つからない。AOSP confirmed path でも compat change gate は見つからない。 |

### 調査日（Investigation Date）

2026-07-06

### 信頼度（Confidence）

- High

理由:
- 公式文書は Android 16 all apps / Security section として、targetSdkVersion に関係なく Android 16 上の companion app に適用される変更を説明している。
- Android 15 baseline では discovery timeout 時に `CompanionAssociationActivity` が `RESULT_DISCOVERY_TIMEOUT` で cancel する実装を確認した。
- Android 16 target では discovery state から `FINISHED_TIMEOUT` がなくなり、20 秒の soft timeout、5 分の hard timeout、timeout message UI、user cancel / dismiss 後の `RESULT_USER_REJECTED` path を確認した。
- targetSdkVersion gate / compat framework gate は確認できない。

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [x] OS update / all apps on Android 16 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 36 on Android 16+
- [ ] targetSdkVersion >= 36, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [ ] Unknown / needs more evidence

必要な実行時条件（Required runtime conditions）:
- Android version: Android 16
- targetSdkVersion: 条件なし。targetSdkVersion 35 / 36 の両方が影響対象になり得る。
- Device/form factor: 条件なし。
- Permission/API/component condition: `CompanionDeviceManager#associate()` / CDM association discovery flow を使うこと。
- App state/process condition: discovery timeout、user stop、または first 20 seconds 内の discovery result に依存する pairing flow。

Compat framework:
- Change ID: 見つからない。
- Change name: N/A
- Default state: N/A
- Toggleable for testing: N/A。`debug.cdm.discovery_timeout` sysprop は discovery timeout を短縮・調整する debug hook として AOSP に存在するが、app compat framework change ではない。

分類信頼度（Classification confidence）:
- High

分類根拠（Classification evidence）:
- Official documentation page: `behavior-changes-all` の Security section。
- Original applicability statement: Android 16 上の companion device pairing flow の新挙動として説明されている。
- AOSP targetSdk gate: 見つからない。
- Compat framework entry: 見つからない。

---

# エグゼクティブサマリー（Executive Summary）

Android 16 では、Companion Device Manager の device discovery が timeout しても、companion app は `RESULT_DISCOVERY_TIMEOUT` を直接受け取らなくなる。代わりに CDM の system UI が timeout message を表示し、ユーザーが flow を閉じると app には `RESULT_USER_REJECTED` が返る。

Android 15 では 20 秒 timeout で discovery を終了し、app に `RESULT_DISCOVERY_TIMEOUT` を返していた。Android 16 では 20 秒は soft timeout になり、未発見なら UI message を出して探索を継続し、5 分 hard timeout またはユーザー操作で終了する。20 秒以内に 1 件以上見つかっている場合は追加探索を止める。

この変更は targetSdkVersion 36 化だけの影響ではない。Android 16 OS 上で CDM pairing / association discovery flow を使い、timeout result、retry、analytics、custom timeout UI に依存するアプリが確認対象になる。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statement）

公式文書は以下を説明している。

- Android 16 は、悪意あるアプリからユーザーの location privacy を守るため、companion device pairing flow に新しい挙動を導入する。
- Android 16 上で動作する companion app は、`RESULT_DISCOVERY_TIMEOUT` による discovery timeout の直接通知を受けなくなる。
- 代わりに、timeout event は user-facing visual dialog でユーザーに通知される。
- ユーザーが dialog を dismiss すると、app は association failure として `RESULT_USER_REJECTED` を受ける。
- search duration は従来の 20 秒から延長され、ユーザーは探索中いつでも device discovery を止められる。
- 検索開始後 20 秒以内に少なくとも 1 device が見つかった場合、CDM は追加 device の探索を停止する。

## 公式文書との差分確認

- requested anchor `#companion-device-timeout` は現在の公式 HTML 上で確認できた。
- 公式文書の該当 section は 2026-06-24 UTC 更新の Android 16 all apps ページに存在する。
- 依頼の Original statements は現在の公式本文と一致する。

## 解釈（Interpretation）

この Behavior Change は、CDM discovery timeout をアプリへ直接通知すると「近くに対象 device が存在しなかった」ことをアプリが推測できるため、その情報を system UI 側に閉じ込める privacy hardening と解釈できる。

ただし `RESULT_DISCOVERY_TIMEOUT` 定数自体は Android 16 API surface に残る。互換性リスクは API 削除ではなく、Android 16 の CDM discovery timeout 実行時 path が app-facing result を `RESULT_USER_REJECTED` に変える点にある。

---

# 変更内容（What Changed）

## 変更点

- Android 15:
  - `CompanionDeviceDiscoveryService` は `TIMEOUT_DEFAULT = 20_000L` を使い、timeout 時に `DiscoveryState.FINISHED_TIMEOUT` を設定する。
  - `CompanionAssociationActivity#onDiscoveryStateChanged()` は `FINISHED_TIMEOUT` かつ scan result が空の場合、`cancel(RESULT_DISCOVERY_TIMEOUT, null)` を呼ぶ。
  - app callback / Activity result には timeout reason として `RESULT_DISCOVERY_TIMEOUT` / `REASON_DISCOVERY_TIMEOUT` が流れ得る。
- Android 16:
  - `TIMEOUT_DEFAULT` / `FINISHED_TIMEOUT` / `timeout()` が削除され、`TIMEOUT_SOFT = 20_000L` と `TIMEOUT_HARD = 300_000L` に分かれた。
  - 20 秒 soft timeout 時点で device が 0 件なら `DiscoveryState.IN_PROGRESS_EXTENDED` になり、CDM UI が soft timeout message を表示して探索を続ける。
  - 20 秒 soft timeout 時点で 1 件以上 device がある場合は `stopDiscoveryAndFinish()` を呼び、追加探索を止める。
  - hard timeout / user stop / cancel は `DiscoveryState.FINISHED_STOPPED` に収束し、scan result が空なら hard timeout message を表示する。
  - user が cancel / dismiss すると `cancel(RESULT_USER_REJECTED, null)` により app callback と Activity result に `RESULT_USER_REJECTED` が返る。

## 適用条件（Applicability）

### OS アップデート時の挙動（OS Update Behavior）

- Android 16 にアップデートしただけで適用されるか: Yes / Conditional。
- targetSdkVersion に依存しない根拠: AOSP confirmed path に targetSdkVersion 36 gate は見つからない。公式文書も all apps ページ。
- Android 15 以前での挙動: Android 15 baseline では 20 秒 discovery timeout が `RESULT_DISCOVERY_TIMEOUT` として app に直接通知され得る。

### targetSdkVersion 36 以上での挙動（targetSdkVersion 36 Behavior）

- targetSdkVersion 36 以上で適用されるか: targetSdkVersion 36 は必要条件ではない。
- Android 16 以外で targetSdkVersion 36 にした場合の挙動: Android 15 OS 上では Android 16 の CDM timeout UI / soft-hard timeout path は確認できない。targetSdkVersion 36 だけで同じ挙動になる根拠はない。
- opt-out / temporary override の有無: app-facing opt-out は確認できない。debug sysprop `debug.cdm.discovery_timeout` は platform debug/testing 用であり、app mitigation ではない。

### その他の条件（Other Conditions）

- device/form factor: 条件なし。
- permission: CDM association request に必要な companion profile permission / nearby discovery permission は別途関係するが、この timeout 挙動自体の gate ではない。
- API usage: `CompanionDeviceManager#associate()` / `AssociationRequest` / CDM discovery flow。
- manifest attribute: 条件なし。
- component boundary: CDM system UI / `CompanionDeviceDiscoveryService` を経由する association flow。

---

# AOSP 調査（AOSP Investigation）

## 関連ファイル（Related Files）

- `frameworks-base/core/java/android/companion/CompanionDeviceManager.java`
- `frameworks-base/core/java/android/companion/AssociationRequest.java`
- `frameworks-base/core/api/current.txt`
- `frameworks-base/packages/CompanionDeviceManager/src/com/android/companiondevicemanager/CompanionAssociationActivity.java`
- `frameworks-base/packages/CompanionDeviceManager/src/com/android/companiondevicemanager/CompanionDeviceDiscoveryService.java`
- `frameworks-base/packages/CompanionDeviceManager/src/com/android/companiondevicemanager/Utils.java`
- `frameworks-base/packages/CompanionDeviceManager/res/layout/activity_confirmation.xml`
- `frameworks-base/packages/CompanionDeviceManager/res/values/strings.xml`
- `frameworks-base/services/companion/java/com/android/server/companion/association/AssociationRequestsProcessor.java`

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル（File / symbol） | Android 15 の基準挙動（baseline） | Android 16 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `CompanionDeviceManager#associate()` | CDM association request を system service へ渡し、callback で result を受ける。 | 同じ public entry point。profile permission 追加などはあるが timeout behavior gate はない。 | app が CDM pairing flow を開始する public API。 |
| `CompanionDeviceManager.RESULT_DISCOVERY_TIMEOUT` / `RESULT_USER_REJECTED` | `RESULT_DISCOVERY_TIMEOUT = 2`、`RESULT_USER_REJECTED = 1`。 | 定数は引き続き存在。 | API 削除ではなく result delivery path の挙動変更である根拠。 |
| `CompanionDeviceDiscoveryService.TIMEOUT_DEFAULT` | `20_000L`。`mTimeoutRunnable = this::timeout`。 | `TIMEOUT_SOFT = 20_000L`、`TIMEOUT_HARD = 300_000L`。soft / hard timeout に分離。 | search duration extension と 20 秒 soft timeout の根拠。 |
| `CompanionDeviceDiscoveryService.DiscoveryState` | `FINISHED_TIMEOUT` が存在。 | `FINISHED_TIMEOUT` が消え、`IN_PROGRESS_EXTENDED` と `FINISHED_STOPPED` になる。 | timeout を app result として直接表現しなくなった根拠。 |
| `CompanionDeviceDiscoveryService#softTimeout()` | 該当なし。20 秒で timeout finish。 | 0 件なら `IN_PROGRESS_EXTENDED`、1 件以上なら `stopDiscoveryAndFinish()`。 | 未発見時は UI message 表示・探索継続、発見済みなら追加探索停止の根拠。 |
| `CompanionDeviceDiscoveryService#scheduleTimeout()` | 20 秒 timeout runnable だけを post。 | soft timeout と 5 分 hard timeout を post。 | 検索時間延長の実装根拠。 |
| `CompanionAssociationActivity#onDiscoveryStateChanged()` | `FINISHED_TIMEOUT` かつ result 空なら `cancel(RESULT_DISCOVERY_TIMEOUT, null)`。 | `IN_PROGRESS_EXTENDED` で soft message 表示、`FINISHED_STOPPED` で hard message 表示。自動 `RESULT_DISCOVERY_TIMEOUT` cancel は削除。 | app-facing result code 変更の中心。 |
| `CompanionAssociationActivity#cancel()` / `onNegativeButtonClick()` | user rejection は `RESULT_USER_REJECTED`。timeout は別 path。 | user cancel / dismiss 後に `RESULT_USER_REJECTED` を callback と Activity result に送る。 | timeout dialog dismissal 後に app が `RESULT_USER_REJECTED` を受ける根拠。 |
| `activity_confirmation.xml` / `strings.xml` | timeout message UI はない。 | `timeout_message` TextView、soft / hard timeout message が追加。 | system visual dialog / CDM UI が timeout をユーザーへ表示する根拠。 |
| `Utils.RESULT_CODE_TO_REASON` | `RESULT_DISCOVERY_TIMEOUT` -> `REASON_DISCOVERY_TIMEOUT`、`RESULT_USER_REJECTED` -> `REASON_USER_REJECTED`。 | mapping 自体は残る。 | result code 定数と reason は残るが、timeout path から直接使われにくくなる根拠。 |

必須記入項目（Required context）:
- Entry point / caller: app `CompanionDeviceManager#associate()` -> system service association request -> CDM package `CompanionAssociationActivity` / `CompanionDeviceDiscoveryService` -> app callback `CompanionDeviceManager.Callback#onFailure(...)` または Activity result。
- Relevant class or service responsibility: `CompanionDeviceDiscoveryService` は Bluetooth / BLE / Wi-Fi filter に基づく device discovery と timeout scheduling を担当し、`CompanionAssociationActivity` は system UI と app-facing result を担当する。
- Runtime path from app API / system event to changed code: app が CDM association を開始し、CDM UI が device discovery を開始する。20 秒 soft timeout / hard timeout / user stop / device found event が LiveData state として activity に流れ、activity が UI message または callback result に変換する。
- Why unrelated code paths were excluded: companion device presence、virtual device、data sync、transport、bond management は CDM 全体の別機能であり、discovery timeout result 変更の根拠ではないため除外した。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
| `RESULT_DISCOVERY_TIMEOUT` import と `cancel(RESULT_DISCOVERY_TIMEOUT, null)` が `CompanionAssociationActivity` から削除 | app へ timeout を直接返す path の removed behavior。 | 公式文書の「no longer directly notified」に対応。 | High |
| `TIMEOUT_DEFAULT = 20_000L` が `TIMEOUT_SOFT = 20_000L` / `TIMEOUT_HARD = 300_000L` に変更 | timeout の意味が「終了」から「soft message + extended search」に変わった changed behavior。 | 公式文書の「search duration has also been extended」に対応。 | High |
| `FINISHED_TIMEOUT` が削除され `IN_PROGRESS_EXTENDED` が追加 | timeout event が app-facing failure ではなく UI state へ寄った changed condition。 | system visual dialog / timeout message 表示の根拠。 | High |
| `softTimeout()` が 0 件なら message 表示、1 件以上なら stop | first 20 seconds の discovery result による分岐追加。 | 公式文書の「If at least one device was discovered within the first 20 seconds...」に対応。 | High |
| `timeout_message` TextView と soft / hard timeout strings 追加 | user-facing visual timeout UI の added behavior。 | 公式文書の「user is notified ... with a visual dialog」に対応。 | High |
| targetSdkVersion / compat gate が見つからない | OS update all-apps behavior として解釈。 | classification を `OS_UPDATE_ALL_APPS` とする根拠。 | High |
| API surface 上 `RESULT_DISCOVERY_TIMEOUT` / `RESULT_USER_REJECTED` は維持 | API deletion ではない。 | app の compile break ではなく runtime result semantics の変更。 | High |

必須分類（Required interpretation）:
- Added behavior: Android 16 で timeout message UI、soft timeout state、hard timeout が追加。
- Removed behavior: Android 15 の timeout direct callback `cancel(RESULT_DISCOVERY_TIMEOUT, null)` path が削除。
- Changed condition / gate: 20 秒時点で device 0 件なら探索継続 + UI message、1 件以上なら追加探索停止。
- Changed default: discovery timeout が app-facing direct failure ではなく user-facing UI + user rejection result に寄る。
- No behavior change found: `RESULT_DISCOVERY_TIMEOUT` 定数自体は current API surface に残る。

## 事実（Facts）

- 公式文書はこの項目を Android 16 all apps / Security として掲載している。
- 公式文書は `RESULT_DISCOVERY_TIMEOUT` の直接通知をやめ、timeout dialog dismissal 後に `RESULT_USER_REJECTED` を返すと説明している。
- Android 15 `CompanionAssociationActivity#onDiscoveryStateChanged()` は `FINISHED_TIMEOUT` かつ scan result empty の場合に `cancel(RESULT_DISCOVERY_TIMEOUT, null)` を呼ぶ。
- Android 15 `CompanionDeviceDiscoveryService` は `TIMEOUT_DEFAULT = 20_000L` を使う。
- Android 16 `CompanionDeviceDiscoveryService` は `TIMEOUT_SOFT = 20_000L` と `TIMEOUT_HARD = 300_000L` を使う。
- Android 16 `CompanionDeviceDiscoveryService#softTimeout()` は、device 未発見なら `IN_PROGRESS_EXTENDED`、device 発見済みなら `stopDiscoveryAndFinish()` を呼ぶ。
- Android 16 `CompanionAssociationActivity#onDiscoveryStateChanged()` は `IN_PROGRESS_EXTENDED` で soft timeout message を表示し、`FINISHED_STOPPED` で scan result が空なら hard timeout message を表示する。
- Android 16 `CompanionAssociationActivity#onNegativeButtonClick()` は `cancel(RESULT_USER_REJECTED, null)` を呼ぶ。
- Android 16 `CompanionAssociationActivity#cancel()` は app callback `onFailure(errorCode, errorMessage)` と Activity result に同じ error code を送る。
- Android 16 API surface に `RESULT_DISCOVERY_TIMEOUT = 2` と `RESULT_USER_REJECTED = 1` は残っている。

## 観察（Observations）

- Android 16 では discovery timeout と user manual stop / dismiss が app result code 上は `RESULT_USER_REJECTED` に収束しやすい。app は `RESULT_USER_REJECTED` を純粋な user cancellation として扱うと、timeout を user rejection と誤分類する可能性がある。
- `RESULT_DISCOVERY_TIMEOUT` / `REASON_DISCOVERY_TIMEOUT` は mapping と API に残るが、Android 16 の通常 timeout path から app に直接返る根拠は確認できない。
- 20 秒以内に device が見つかった場合、multi-device flow でも追加探索が止まるため、従来より「後から見つかる候補 device」を UI に追加し続ける時間が短くなる可能性がある。
- CDM UI 側に timeout message が追加されたため、app 独自の timeout UI / retry prompt と重複する可能性がある。

## 仮説（Hypotheses）

- 直接 `RESULT_DISCOVERY_TIMEOUT` を返さない理由は、対象 device が近くに存在しない、Bluetooth / Wi-Fi が有効でない、または探索条件に一致しないといった近接・場所に関する情報を app に渡しにくくする privacy hardening と考えられる。
- `RESULT_DISCOVERY_TIMEOUT` 定数が残るのは backward compatibility、既存 API surface、または別 path / legacy path との互換性維持のためと考えられる。
- 公式文書の「visual dialog」は AOSP 上では `CompanionAssociationActivity` の system-controlled association UI 内の timeout message / confirmation dialog として実装されている。

## 結論（Conclusions）

- 顧客向け分類は `OS_UPDATE_ALL_APPS`。Android 16 OS 上で CDM pairing / discovery flow を使う app は、targetSdkVersion 35 のままでも影響を受け得る。
- targetSdkVersion 36 化だけの影響ではない。Android 15 OS 上で targetSdkVersion 36 にしても、この Android 16 CDM timeout behavior が発生する根拠はない。
- `RESULT_DISCOVERY_TIMEOUT` による retry / analytics / support log / UI 分岐に依存する app は、Android 16 では `RESULT_USER_REJECTED` と system timeout UI を考慮して pairing failure handling を見直す必要がある。
- app 側の推奨対応は、`RESULT_DISCOVERY_TIMEOUT` だけに依存せず、`RESULT_USER_REJECTED` でも timeout dialog dismissal / manual cancellation / generic rejection を区別できない前提で graceful retry / support messaging を設計することである。

## 適用ゲート根拠（Applicability Gate Evidence）

- targetSdkVersion gate: 見つからない。
- CompatChanges.isChangeEnabled / ChangeId: 見つからない。
- @EnabledAfter / @EnabledSince / default state: 見つからない。
- Build.VERSION / SDK_INT gate: CDM package は Android 16 platform implementation として差し替わる。app code 上の SDK_INT gate ではない。
- DeviceConfig / resources config: 見つからない。
- Permission/AppOps gate: CDM association flow に必要な permission はあるが、この timeout behavior の gate ではない。
- Manifest/property gate: 見つからない。
- No gate found: `CompanionAssociationActivity` / `CompanionDeviceDiscoveryService` の confirmed path に targetSdkVersion / compat gate は見つからない。
- Gate conclusion: Android 16 OS 上で CDM association discovery flow を使う全アプリに条件付きで適用。
- Reasoning from source context: app-facing timeout result を送っていた Android 15 UI path が Android 16 で削除され、targetSdkVersion 判定なしに CDM package の runtime state machine が変わっているため。

---

# 期待挙動マトリクス（Expected Behavior Matrix）

## OS / targetSdkVersion マトリクス

| シナリオ | 期待挙動 | 影響 |
| --- | --- | --- |
| Android 16 / targetSdkVersion 35 | CDM discovery timeout の直接 `RESULT_DISCOVERY_TIMEOUT` 通知は行われず、system UI message 後の user dismiss / cancel で `RESULT_USER_REJECTED` が返る | 影響あり |
| Android 16 / targetSdkVersion 36 | targetSdkVersion 35 と同じ。targetSdkVersion 36 固有ではない | 影響あり |
| Android 15 / targetSdkVersion 36 | Android 15 baseline では 20 秒 timeout で `RESULT_DISCOVERY_TIMEOUT` が返る path がある。targetSdkVersion 36 だけで Android 16 behavior になる根拠はない | 比較対象 |

## 詳細シナリオマトリクス

| シナリオ | 期待挙動 / 調査結論 |
| --- | --- |
| Android 16 / targetSdkVersion 35 / CDM pairing flow | 新挙動の対象。timeout は app へ直接 `RESULT_DISCOVERY_TIMEOUT` として返らない |
| Android 16 / targetSdkVersion 36 / CDM pairing flow | targetSdkVersion 35 と同様 |
| Android 16 / targetSdkVersion 35 / non-CDM pairing flow | 今回の CDM path では影響しない |
| Android 16 / targetSdkVersion 36 / non-CDM pairing flow | 今回の CDM path では影響しない |
| Android 16 / discovery timeout occurs | CDM UI が timeout message を表示し、app は user dismissal / cancel 後に `RESULT_USER_REJECTED` を受ける |
| Android 16 / app expects RESULT_DISCOVERY_TIMEOUT | timeout 分岐が実行されず、retry / analytics / support log がずれる可能性 |
| Android 16 / app receives RESULT_USER_REJECTED after timeout dialog dismissal | 公式文書と AOSP cancel path に整合 |
| Android 16 / user dismisses timeout dialog | app-facing result は `RESULT_USER_REJECTED` |
| Android 16 / user manually stops discovery | app-facing result は `RESULT_USER_REJECTED` |
| Android 16 / no devices discovered in first 20 seconds | `IN_PROGRESS_EXTENDED` になり soft timeout message を表示、探索継続 |
| Android 16 / at least one device discovered within first 20 seconds | soft timeout 時に `stopDiscoveryAndFinish()` し、追加探索を停止 |
| Android 16 / CDM stops searching for additional devices | 20 秒時点で device が 1 件以上ある場合に発生 |
| Android 16 / CDM continues search beyond original 20 seconds | 20 秒時点で device が 0 件の場合に発生。hard timeout は 5 分 |
| Android 16 / app custom timeout UI | CDM system timeout message と重複する可能性 |
| Android 16 / app retry behavior based on RESULT_DISCOVERY_TIMEOUT | Android 16 では見直しが必要 |
| Android 16 / app retry behavior based on RESULT_USER_REJECTED | timeout dismissal と user cancellation が同じ result code に見える前提で設計が必要 |
| Android 16 / metrics logging timeout as user rejection | analytics 上の timeout / user rejection 混同に注意 |
| Android 16 / BLE companion device | CDM BLE scan path は対象 |
| Android 16 / Bluetooth classic companion device | CDM Bluetooth discovery path は対象 |
| Android 16 / Wi-Fi / nearby device association if applicable | `WifiDeviceFilter` path は対象 |
| Android 15 / targetSdkVersion 35 / CDM discovery timeout | baseline は 20 秒 timeout direct result |
| Android 15 / targetSdkVersion 36 / same app behavior if technically comparable | Android 16 OS behavior と混同せず比較 |
| app updates result handling | `RESULT_USER_REJECTED` を generic failure として graceful retry / support messaging へ誘導 |
| app continues relying on RESULT_DISCOVERY_TIMEOUT | Android 16 で timeout-specific flow が動かない可能性 |

---

# 影響対象（Affected App Types）

- `CompanionDeviceManager` を使うアプリ。
- CDM association / pairing flow を使うアプリ。
- `RESULT_DISCOVERY_TIMEOUT` に依存するアプリ。
- `RESULT_USER_REJECTED` を単純な user cancellation として扱っているアプリ。
- pairing timeout / retry / fallback UI を独自実装しているアプリ。
- discovery timeout を analytics / customer support / fraud detection / onboarding funnel に使うアプリ。
- wearable / earbuds / health device / IoT / camera / tracker / automotive accessory をペアリングするアプリ。
- BLE / Bluetooth / Wi-Fi device filter を使うアプリ。
- companion app onboarding の user-visible failure / retry behavior が重要なアプリ。
- location privacy / nearby device discovery privacy に敏感なアプリ。

---

# 非影響または低影響（Expected Non-impact / Lower-impact）

- CDM association / pairing flow を使わないアプリ。
- `RESULT_DISCOVERY_TIMEOUT` に依存しないアプリ。
- `RESULT_USER_REJECTED` を generic association failure として扱い、retry / fallback が破綻しないアプリ。
- 20 秒以内に対象 device が見つかり、ユーザーがその device を選択する flow。
- CDM ではなく app 独自の pairing flow だけを使う場合。ただし nearby discovery privacy / permission は別途確認が必要。
- Android 15 以前の端末。ただし targetSdkVersion 36 との比較は実機で分けて確認する。

---

# 推奨対応候補（Recommended Action Candidates）

- `RESULT_DISCOVERY_TIMEOUT` だけに依存している timeout-specific retry / UI / analytics を棚卸しする。
- Android 16 では `RESULT_USER_REJECTED` が timeout dialog dismissal と user cancellation の両方を表し得る前提で、error message / retry CTA / support log を設計する。
- CDM flow の周辺に app 独自 timeout UI を出している場合、system timeout message と二重表示にならないか確認する。
- onboarding funnel / customer support metrics では、Android 16 以降の `RESULT_USER_REJECTED` 増加を timeout 由来と user cancellation 由来に機械的に分けられない可能性を明記する。
- 20 秒以内に複数 candidate device が出る想定の UI は、Android 16 で追加探索が止まることによる候補数の変化を確認する。

---

# テスト観点（Test Points）

- Android 15 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 36。
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較。
- `CompanionDeviceManager#associate()`。
- `AssociationRequest` filter combinations。
- discovery timeout。
- no device discovered。
- one or more devices discovered within first 20 seconds。
- multiple devices discovered after first 20 seconds。
- user dismisses timeout dialog。
- user manually stops discovery。
- `RESULT_DISCOVERY_TIMEOUT` callback / result。
- `RESULT_USER_REJECTED` callback / result。
- app retry / fallback / onboarding state。
- custom timeout UI and system timeout dialog interaction。
- logcat / `dumpsys companiondevice` / `dumpsys activity` / metrics。
- BLE / Bluetooth classic / Wi-Fi discovery variants if applicable。
- user-visible dialog screenshot / screen recording。
- analytics event mapping before / after。
- customer support logs / error reason text。
- accessibility / localization of timeout dialog if relevant。
- regression testing for pairing success, timeout, cancellation, and retry。

---

# Evidence Gaps / Limits

- CTS / unit test でこの exact behavior を検証する test は今回の grep 範囲では確認できなかった。UI behavior は実機 / emulator での manual / instrumentation verification が望ましい。
- 公式文書の「location privacy」について、AOSP code comment で直接その目的を説明する箇所は確認できなかった。privacy motivation は公式文書を根拠とし、AOSP は implementation evidence として扱う。
- `RESULT_DISCOVERY_TIMEOUT` 定数が残る理由は AOSP comment からは断定できない。互換性維持または他 path への残存利用の可能性として扱う。

---

# Human Decision Placeholder

最終優先度（Final Priority）:
- TBD by human

判断（Decision）:
- TBD by human

顧客説明優先度（Customer communication priority）:
- TBD by human

リリース判定（Release readiness decision）:
- TBD by human

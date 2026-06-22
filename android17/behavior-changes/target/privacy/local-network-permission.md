# Android 17 をターゲットにするアプリで必要になるローカルネットワーク権限

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

### Behavior Change 文書（Behavior Change Source）

文書:
https://developer.android.com/about/versions/17/behavior-changes-17

関連文書:
- https://developer.android.com/reference/android/Manifest.permission#ACCESS_LOCAL_NETWORK
- https://developer.android.com/privacy-and-security/local-network-permission

セクション:
- Local network permission required for apps targeting Android 17

ページ種別:
- Android 17 以上をターゲットにするアプリ

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- TARGET_SDK_37_CONDITIONAL

公式文書からの適用条件判断:
- 公式文書は、Android 17 / targetSdkVersion 37 以上のアプリでは local network access に `ACCESS_LOCAL_NETWORK` runtime permission、または system-mediated picker が必要になると説明している。
- 追加条件は、アプリが LAN / Wi-Fi / Ethernet などの local network 上の device discovery / connection / socket communication を行うこと。
- AOSP `frameworks-base` では permission 定義、API surface、AppOps、permission policy、BPF permission map への接続、MediaRouter の互換処理を確認できた。
- 一方、local network traffic を実際に拒否する packet / socket enforcement と targetSdkVersion ゲートの本体は connectivity module 側にあると考えられ、`frameworks-base` だけでは High confidence まで上げない。

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 通常は targetSdkVersion 37 条件が主条件 | 公式文書は Android 17 target changes として説明。`frameworks-base` では MediaRouter が compat change disabled の uid には local network permission を満たした扱いにする互換処理を持つ。 |
| targetSdkVersion 37 以上が必要か | Yes と判断 | 公式文書の対象が targetSdkVersion 37 以上。`MediaRouter2ServiceImpl` の comment は connectivity module の `RESTRICT_LOCAL_NETWORK` ChangeId を参照し、compat change による target gate が存在することを示す。 |
| 追加の実行時条件があるか | ある | local network access、permission grant state、system picker 利用有無、feature flag `access_local_network_permission_enabled`。 |
| Compat Change ID が関係するか | 関係する可能性が高い | `MediaRouter2ServiceImpl` が ChangeId `365139289L` を `RESTRICT_LOCAL_NETWORK` として扱う。ただし ChangeId 定義本体は connectivity module 側で、`frameworks-base` では comment と利用箇所のみ確認。 |

### 調査日（Investigation Date）

2026-06-18

### 信頼度（Confidence）

- Medium

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] targetSdkVersion に関係なく Android 17 の全アプリへ適用
- [ ] Android 17 以上かつ targetSdkVersion 37 以上で適用
- [x] targetSdkVersion 37 以上かつ追加の実行時条件を満たす場合に適用
- [ ] Mainline / Google Play system update に依存
- [ ] API 追加のみであり、挙動変更ではない
- [ ] 未確認 / 追加 evidence が必要

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 以上。
- targetSdkVersion: 37 以上。
- Device / network condition: broadcast-capable interface を持つ local network。AOSP manifest comment は Wi-Fi / Ethernet を例示し、WWAN / VPN を除外している。
- Permission / API condition: `ACCESS_LOCAL_NETWORK` の manifest declaration と runtime grant、または system-mediated picker path。
- App state / process condition: app が local network device discovery / connection / local endpoint access を行う時点。
- Release flag condition: `android.permission.flags.access_local_network_permission_enabled` が有効であること。

Compat framework:
- Change ID: `365139289L`
- 変更名: `RESTRICT_LOCAL_NETWORK`（`MediaRouter2ServiceImpl` の comment による。定義本体は connectivity module 側）
- 既定状態: `frameworks-base` だけでは未確認
- テスト時に切り替え可能か: compat change として扱われるため可能性は高いが、定義本体未確認のため未確定

分類信頼度（Classification confidence）:
- Medium

分類根拠（Classification evidence）:
- 公式 Behavior Change 文書は targetSdkVersion 37 以上で mandatory enforcement になると説明している。
- AOSP `core/res/AndroidManifest.xml` に `ACCESS_LOCAL_NETWORK` dangerous permission が追加されている。
- AOSP `AppOpsManager` に `OPSTR_ACCESS_LOCAL_NETWORK` と permission linkage が追加されている。
- AOSP permission policy は `ACCESS_LOCAL_NETWORK` を nearby devices permission set に含める。
- AOSP permission service は `ACCESS_LOCAL_NETWORK` を BPF permission map に流せる permission として扱う。
- `MediaRouter2ServiceImpl` は `RESTRICT_LOCAL_NETWORK` compat change が disabled の uid では local network permission を満たした扱いにする互換処理を持つ。
- ただし実際の network enforcement と ChangeId 定義本体は `frameworks-base` 外の connectivity module 側確認が必要である。

---

# エグゼクティブサマリー

Android 17 では、targetSdkVersion 37 以上のアプリが LAN 上の device を discover / connect する場合、新しい `ACCESS_LOCAL_NETWORK` runtime permission、または system-mediated な privacy-preserving picker が必要になる。AOSP `frameworks-base` では、この permission の API / manifest 定義、AppOps、runtime permission policy、permission state を BPF map に配布する仕組み、MediaRouter 経由の互換処理を確認できた。

この変更は local network access を dangerous runtime permission の制御下に置く privacy hardening である。smart home、IoT、casting、mDNS / NSD、`.local` resolution、local endpoint socket などを使うアプリは、targetSdkVersion 37 更新前に access path の棚卸しが必要になる。

信頼度は Medium とする。`frameworks-base` だけで permission infrastructure は十分確認できたが、packet / socket enforcement と targetSdkVersion ゲートの定義本体は connectivity module 側に残るため、High confidence にはしていない。

---

# 公式ドキュメント確認

## 原文（Statement）

ページタイトル:
- Behavior changes: Apps targeting Android 17 or higher

ページ URL:
- https://developer.android.com/about/versions/17/behavior-changes-17

セクションタイトル:
- Local network permission required for apps targeting Android 17

検証対象の原文:
- Android 17 は `ACCESS_LOCAL_NETWORK` runtime permission を導入する。
- Android 17 / API level 37 以上をターゲットにするアプリが local network communication を維持するには、system-mediated picker を使うか、runtime permission を request する必要がある。

## 解釈（Interpretation）

この変更は、targetSdkVersion 37 以上のアプリが direct local network access を行う場合に permission gate を追加する挙動変更である。アプリが system-mediated picker だけで要件を満たせる場合は broad runtime permission を避けられる。一方、持続的または広範な LAN access が必要な場合は `ACCESS_LOCAL_NETWORK` の manifest declaration、runtime request、denial / revocation handling が必要になる。

---

# 変更内容（What Changed）

公式文書上の変更点:
- Android 17 は `ACCESS_LOCAL_NETWORK` runtime permission を導入する。
- targetSdkVersion 37 以上では local network access が default block になり、picker または runtime permission grant が必要になる。
- permission は nearby devices 系の runtime permission として扱われる。
- Android 16 では opt-in test が可能だったが、Android 17 target では mandatory enforcement になる。

AOSP で確認した変更点:
- `Manifest.permission.ACCESS_LOCAL_NETWORK` が API surface に追加された。
- `core/res/AndroidManifest.xml` に dangerous permission として追加された。
- `AppOpsManager` に local network access 用 app op が追加された。
- permission policy / default grant policy / upgrade path が `ACCESS_LOCAL_NETWORK` を nearby devices permission set に含める。
- `PermissionBpfMap` と `PermissionManagerLocal` が permission state を BPF map に配布するための仕組みを追加し、`ACCESS_LOCAL_NETWORK` が許可対象に含まれる。
- `MediaRouter2ServiceImpl` は target package が local network permission を持たない場合の権限補完と、`RESTRICT_LOCAL_NETWORK` compat change disabled 時の後方互換処理を持つ。

未確認として残る点:
- connectivity module 側の `RESTRICT_LOCAL_NETWORK` 定義、default state、targetSdkVersion ゲート。
- packet / socket / DNS / NSD / Cronet / OkHttp などに対する実 enforcement path。
- 旧 targetSdkVersion アプリに対する temporary implicit grant の実装詳細。

---

# AOSP 調査（AOSP Investigation）

## チェックアウト状態

根拠利用前に確認したコマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list android-17.0.0_r1
```

結果:
- `frameworks-base` working tree: clean at the time of investigation.
- From tag: `android-16.0.0_r4` exists.
- To tag: `android-17.0.0_r1` exists.

## 関連ファイル（Related Files）

- `core/api/current.txt`
- `core/res/AndroidManifest.xml`
- `core/java/android/permission/flags.aconfig`
- `core/java/android/app/AppOpsManager.java`
- `services/permission/java/com/android/server/permission/access/permission/AppIdPermissionPolicy.kt`
- `services/permission/java/com/android/server/permission/access/permission/AppIdPermissionUpgrade.kt`
- `services/permission/java/com/android/server/permission/access/permission/PermissionService.kt`
- `services/core/java/com/android/server/permission/PermissionManagerLocal.java`
- `services/core/java/com/android/server/permission/PermissionBpfMap.java`
- `services/core/java/com/android/server/pm/permission/DefaultPermissionGrantPolicy.java`
- `services/core/java/com/android/server/SystemConfig.java`
- `services/core/java/com/android/server/media/MediaRouter2ServiceImpl.java`
- `packages/SystemUI/src/com/android/systemui/media/dialog/MediaSwitchingController.kt`

## 確認したソース文脈（Source Context Reviewed）

| File / symbol | Android 16 baseline | Android 17 behavior | 関連性 |
| --- | --- | --- | --- |
| `core/api/current.txt` / `Manifest.permission.ACCESS_LOCAL_NETWORK` | permission なし | `@FlaggedApi("android.permission.flags.access_local_network_permission_enabled")` として API surface に追加 | 開発者が manifest / permission request で参照する public API。 |
| `core/res/AndroidManifest.xml` / `ACCESS_LOCAL_NETWORK` | permission なし | dangerous permission として定義。local network を Wi-Fi / Ethernet 等の broadcast-capable interface と説明し、WWAN / VPN を除外 | Behavior Change の permission 本体。 |
| `core/java/android/permission/flags.aconfig` / `access_local_network_permission_enabled` | flag なし | exported / fixed read-only flag として追加。説明文は local network protection 用 permission と明記 | release flag による有効化条件。 |
| `core/java/android/app/AppOpsManager.java` / `OPSTR_ACCESS_LOCAL_NETWORK` | local network 用 app op なし | `ACCESS_LOCAL_NETWORK` permission と app op を関連付け、nearby device op collection に含める | runtime permission grant と app op state を結び付ける。 |
| `AppIdPermissionPolicy.kt` / `NEARBY_DEVICES_PERMISSIONS` | local network permission なし | flag 有効時に `ACCESS_LOCAL_NETWORK` を nearby devices permission set に追加 | permission group / user flag handling の文脈。 |
| `AppIdPermissionUpgrade.kt` / `clearNearbyDevicesPermissionsUserFlags` | local network permission なし | `ACCESS_LOCAL_NETWORK` を明示 request した package の nearby devices user flags を migration 対象に含める | target update / package update 時の runtime permission migration。 |
| `PermissionService.kt` / `ALLOWED_BPF_PERMISSIONS` | local network permission なし | `ACCESS_LOCAL_NETWORK` を BPF map へ配布できる permission に追加 | networking enforcement へ permission state を渡す入口。 |
| `PermissionManagerLocal.java` / `registerPermissionStateCallback` | permission BPF map なし | BPF map に runtime permission state を反映する local API を追加 | networking stack が system_server に都度問い合わせず permission state を参照するための基盤。 |
| `PermissionBpfMap.java` | interface なし | UID ごとの granted permission bitmap を管理する interface を追加 | local network access enforcement が参照する permission state の保存先。 |
| `DefaultPermissionGrantPolicy.java` / `NEARBY_DEVICES_PERMISSIONS` | local network permission なし | `ACCESS_LOCAL_NETWORK` を default grant policy の nearby devices set に含める | permission grant policy の追加。 |
| `SystemConfig.java` / `VENDOR_ASSIGNABLE_PERMISSIONS` | vendor assignable ではない | `INTERNET` とともに `ACCESS_LOCAL_NETWORK` を vendor assignable permission に含める | system config からの permission assignment 対象。 |
| `MediaRouter2ServiceImpl.java` / `permissionAllowedForAppCompat` | local network permission check なし | `RESTRICT_LOCAL_NETWORK` compat change が disabled の uid では `ACCESS_LOCAL_NETWORK` を満たした扱いにする | targetSdkVersion ゲート / compat gate が存在することを示す frameworks-base 側 evidence。 |
| `SystemUI MediaSwitchingController` | local network permission request なし | flag 有効時に media output picker で `ACCESS_LOCAL_NETWORK` を request / check | system-mediated media routing UI の permission path。 |

Source context の補足:
- Entry point / caller: app の direct local network access、media routing / picker、permission request、networking enforcement path。
- 関連性: `frameworks-base` は permission API、runtime permission state、AppOps、system UI / MediaRouter の permission check を担当する。実際の packet filtering / socket rejection は connectivity module 側が主担当と考えられる。
- Baseline Android behavior: Android 16 tag では `ACCESS_LOCAL_NETWORK` permission、関連 AppOps、BPF permission distribution、MediaRouter の local network compat branch が存在しない。
- Target Android behavior: Android 17 tag では `ACCESS_LOCAL_NETWORK` が dangerous runtime permission として追加され、permission state が AppOps / permission policy / BPF map / MediaRouter path に接続される。
- Source diff type: added behavior、changed condition、changed default。
- Excluded code paths: Contacts / Telephony / Bluetooth など local network permission と関係しない permission policy は除外した。networking stack 本体は `frameworks-base` 外のため未完了 evidence として扱う。

## 差分解釈（Diff Interpretation）

| 観測した diff | 解釈 | Behavior Change との関連 | 信頼度 |
| --- | --- | --- | --- |
| `ACCESS_LOCAL_NETWORK` permission / API の追加 | added behavior | アプリが新 runtime permission を宣言 / request できるようになる | High |
| AppOps と permission policy への追加 | added behavior | runtime grant と app op を local network access 判定に使えるようにする | High |
| BPF permission map の追加と allowlist 追加 | added behavior | networking path が UID permission state を高速参照できる基盤を追加 | Medium |
| `MediaRouter2ServiceImpl` の `RESTRICT_LOCAL_NETWORK` compat branch | changed condition | compat change disabled の uid は local network permission check を通過させ、target gate があることを示す | Medium |
| packet / socket enforcement 未確認 | evidence gap | 実際に local traffic が拒否される境界は未検証 | Low |

---

# 事実・観察・仮説・結論

## 事実（Facts）

- `frameworks-base` の `android-16.0.0_r4` と `android-17.0.0_r1` tag は存在し、調査時点の working tree は clean。
- Android 17 tag の API surface には `Manifest.permission.ACCESS_LOCAL_NETWORK` が存在する。
- Android 17 tag の manifest は `ACCESS_LOCAL_NETWORK` を dangerous permission として定義する。
- Android 17 tag の AppOps は `OPSTR_ACCESS_LOCAL_NETWORK` を定義し、flag 有効時に `Manifest.permission.ACCESS_LOCAL_NETWORK` と関連付ける。
- Android 17 tag の permission policy は `ACCESS_LOCAL_NETWORK` を nearby devices permission set に含める。
- Android 17 tag の permission service は `ACCESS_LOCAL_NETWORK` を BPF permission map に配布可能な permission として扱う。
- Android 17 tag の `MediaRouter2ServiceImpl` は `365139289L` を connectivity module の `RESTRICT_LOCAL_NETWORK` として参照し、compat change disabled の uid では local network permission を許可扱いにする。

## 観察（Observations）

- `frameworks-base` 側は permission declaration だけでなく、AppOps、permission migration、default grant、BPF map、MediaRouter / SystemUI まで接続している。
- `MediaRouter2ServiceImpl` の互換分岐は、旧 targetSdkVersion など compat change disabled のアプリに対する後方互換を維持するための処理と読める。
- `frameworks-base` grep では `ACCESS_LOCAL_NETWORK` と targetSdkVersion を直接比較する実装は見つからなかった。

## 仮説（Hypotheses）

- `RESTRICT_LOCAL_NETWORK` の ChangeId 定義、default state、`targetSdkVersion >= 37` gate は connectivity module 側にある。
- packet / socket enforcement は BPF permission map の UID permission bitmap を参照して local network traffic を許可 / 拒否する。
- legacy app の temporary implicit grant も connectivity / permission upgrade path の組み合わせで実現されている可能性がある。

## 結論（Conclusions）

- この Behavior Change は `TARGET_SDK_37_CONDITIONAL` と分類する。
- Android 17 / targetSdkVersion 37 以上で direct local network access を行うアプリは、system-mediated picker を使うか、`ACCESS_LOCAL_NETWORK` runtime permission を取得する必要がある。
- `frameworks-base` evidence は permission infrastructure と compat bridge を十分に裏付けるが、実 enforcement の最終確認には connectivity module evidence が必要である。
- 信頼度は Medium。High confidence には `RESTRICT_LOCAL_NETWORK` 定義本体と networking enforcement path の確認が必要。

---

# 開発者影響

影響を受ける可能性が高いアプリ:
- smart home / IoT device setup
- casting / media routing
- NAS / printer / camera / hub など LAN device 連携
- mDNS / NSD / `.local` resolution
- private IP address への socket / HTTP / WebSocket access
- WebView 内から local network endpoint にアクセスする host app

必要な対応候補:
- local network access 箇所を棚卸しする。
- system-mediated picker で要件を満たせる機能は picker path を優先する。
- direct / persistent access が必要な機能は `ACCESS_LOCAL_NETWORK` を manifest に宣言し、runtime permission request と denied / revoked handling を実装する。
- targetSdkVersion 37 で、permission 未許可時、許可後、取り消し後、旧 targetSdkVersion 互換時の挙動をテストする。
- Android 16 opt-in / compat change で事前検証できる場合は regression test を作る。

---

# テスト観点（Test Matrix）

| 端末 OS | targetSdkVersion | Permission state | 期待挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | なし | 従来どおり local network access が許可される想定。Android 16 opt-in は別途 compat 設定確認が必要。 |
| Android 17 | 36 | なし | legacy app として temporary implicit grant / compat exemption が働く想定。ただし connectivity evidence で要確認。 |
| Android 17 | 37 | 未許可 | direct local network access は拒否される想定。picker path は許可される可能性。 |
| Android 17 | 37 | `ACCESS_LOCAL_NETWORK` granted | direct local network access が許可される想定。 |
| Android 17 | 37 | permission revoked | local network access が拒否され、アプリ側は再 request / fallback / error handling が必要。 |

---

# 追加調査 TODO

- connectivity module の `ConnectivityCompatChanges.java` で `RESTRICT_LOCAL_NETWORK` / `365139289L` の `@EnabledSince(targetSdkVersion = 37)` と default state を確認する。
- packet / socket enforcement path が BPF permission map の `ACCESS_LOCAL_NETWORK` bit を参照していることを確認する。
- `INTERNET` permission による legacy implicit grant の実装箇所を確認する。
- NSD / mDNS / local IP socket / WebView / Cronet / OkHttp の境界別に、どこで local network と判定されるかを確認する。

---

# 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断

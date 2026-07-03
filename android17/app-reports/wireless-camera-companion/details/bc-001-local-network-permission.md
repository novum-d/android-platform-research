# BC-001: Local network permission required for apps targeting Android 17

## 基本情報（Basic Information）

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/17/behavior-changes-17
- Section: Local network permission required for apps targeting Android 17

Original statement:
> Android 17 を target にするアプリでは、direct local network access に新しい runtime permission または system-mediated picker が必要になる、という趣旨の公式説明。

調査対象 Android バージョン:
- From: android-16.0.0_r4
- To: android-17.0.0_r1

## 対象アプリとの関係（Relevance to Target App）

関連するアプリ機能:
- カメラ探索。
- カメラとの Wi-Fi 接続。
- ローカル IP / `.local` / mDNS / NSD / socket / HTTP(S) を使う画像・動画転送。
- リモート制御。

関連する API / permission / component:
- `ACCESS_LOCAL_NETWORK`
- direct local network socket / HTTP(S)
- mDNS / NSD / `.local` resolution
- MediaRouter / system picker path の利用可能性

アプリが該当する可能性:
- Conditional。カメラへの direct local network access がある場合は該当可能性が高い。

判断理由:
- カメラ連携アプリでは、スマートフォンとカメラが同一 LAN またはカメラ側 Wi-Fi AP を介して通信する設計が一般的である。Android 17 / targetSdkVersion 37 では、この種の direct local network access が runtime permission の影響を受ける可能性がある。
- system picker など system-mediated picker でユーザー許可を取得する経路を使わない場合、direct local network access には manifest への `ACCESS_LOCAL_NETWORK` 宣言と、コード上の runtime permission request / denied handling が必要になる。
- カメラ連携では、カメラ探索、Wi-Fi 接続後の再探索、ローカル IP への HTTP / WebSocket / socket 接続、ライブビュー、リモート操作、画像 / 動画転送、切断後の再接続など、複数 endpoint または継続的 communication を必要とする可能性が高い。そのため、system-mediated picker だけで要件を満たすより、`ACCESS_LOCAL_NETWORK` runtime permission を明示 request する設計の方が適合しやすい。
- system-mediated picker は、ユーザーが picker で 1 台の device / service を選び、その endpoint だけに接続すれば機能が成立する場合に検討する。独自 discovery、カメラ側 Wi-Fi AP、手動 IP 接続、継続的な制御チャネルがある場合は picker だけでは不足する可能性がある。

確認したアプリ実装:
- File / module: 未確認。
- Symbol / entry point: 未確認。
- Manifest / permission: 未確認。
- Runtime condition: カメラ探索 / 接続 / 転送時。

## 適用条件分類（Applicability Classification）

主分類（Primary classification）:
- TARGET_SDK_37_CONDITIONAL

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | No / Conditional | 既存 targetSdkVersion では legacy app として免除または implicit grant の対象と考えられるが、connectivity module enforcement は追加確認が必要。 |
| targetSdkVersion 37 以上が必要か | Yes | `ACCESS_LOCAL_NETWORK` は Android 17 target app の direct local network access 条件として扱われる。 |
| 追加の実行時条件があるか | Yes | direct local network access、permission grant state、picker 利用有無。 |
| Compat Change ID が関係するか | Yes | `365139289L`。 |

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 以上。
- targetSdkVersion: 37 以上。
- Device/form factor: 条件なし。
- Permission/API/component condition: direct local network access、`ACCESS_LOCAL_NETWORK` runtime grant、system picker 利用有無。
- App state/process condition: カメラ探索・接続・転送時。
- Manifest/property condition: `ACCESS_LOCAL_NETWORK` declaration が必要になる可能性。
- Mainline/module condition: connectivity module enforcement の追加確認が必要。

Compat framework:
- Change ID: `365139289L`
- Change name: `RESTRICT_LOCAL_NETWORK`
- Default state: frameworks-base 側では未確認。MediaRouter2ServiceImpl は connectivity module の Change ID として参照。
- Toggleable for testing: 要確認。

## AOSP 調査（AOSP Investigation）

関連ファイル:
- `core/res/AndroidManifest.xml`
- `core/api/current.txt`
- `core/java/android/app/AppOpsManager.java`
- `services/core/java/com/android/server/media/MediaRouter2ServiceImpl.java`
- `PermissionService.kt`
- `PermissionManagerLocal.java`
- `PermissionBpfMap.java`

確認したソース文脈（Source Context Reviewed）:

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `core/res/AndroidManifest.xml` / `ACCESS_LOCAL_NETWORK` | permission 定義なし | dangerous permission として追加。formal な `permissionGroup` は `android.permission-group.UNDEFINED` | runtime permission としての公開根拠。nearby devices group に直接属する permission ではないことも示す。 |
| `AppOpsManager` / `OPSTR_ACCESS_LOCAL_NETWORK` | 対応 AppOp なし | local network permission に対応する AppOp が追加 | permission state と enforcement の接続点。 |
| `PermissionBpfMap` | local network permission state の BPF 配布なし | permission state を BPF map へ配布する基盤が追加 | network traffic enforcement に使われる可能性があるため。 |
| `MediaRouter2ServiceImpl` / `RESTRICT_LOCAL_NETWORK` | local network restriction 参照なし | Change ID を参照し compat disabled uid を permission satisfied と扱う path | legacy app exemption / compat path の根拠。 |

必須記入項目:
- Entry point / caller: アプリの LAN device discovery / socket / HTTP(S) / MediaRouter usage -> framework permission / AppOps / connectivity enforcement。
- Relevant class or service responsibility: local network access permission、permission state、compat path の管理。
- Runtime path from app API / system event to changed code: direct local network access 時に permission state / AppOps / BPF map / connectivity module enforcement が関係する想定。
- Why unrelated code paths were excluded: Contacts / SMS / audio など local network access と直接関係しない path は除外。

差分解釈（Diff Interpretation）:
- Added behavior: `ACCESS_LOCAL_NETWORK` permission と関連 AppOp / API surface が追加。
- Changed condition / gate: Change ID `365139289L` による compat path。
- No behavior change found: connectivity module の最終 enforcement 本体は未確認。

適用ゲート根拠（Applicability Gate Evidence）:
- targetSdkVersion gate: Android 17 target app 向け変更として公式文書に記載。
- CompatChanges.isChangeEnabled / ChangeId: `365139289L`。
- Permission/AppOps gate: `ACCESS_LOCAL_NETWORK` / `OPSTR_ACCESS_LOCAL_NETWORK`。
- Gate conclusion: Android 17 上で targetSdkVersion 37 以上、かつ direct local network access を行う場合に影響する可能性が高い。
- Reasoning from source context: permission / AppOp / BPF map / MediaRouter compat path が追加されており、local network access の permission controlled 化を支える。

## 事実・観察・仮説・結論（Facts / Observations / Hypotheses / Conclusion）

事実（Facts）:
- Android 17 で `ACCESS_LOCAL_NETWORK` dangerous permission と関連 AppOp が追加されている。
- `ACCESS_LOCAL_NETWORK` の formal な manifest `permissionGroup` は `android.permission-group.UNDEFINED` であり、`NEARBY_DEVICES` group に直接属するわけではない。
- 一方、AOSP permission policy / migration / default grant handling では `ACCESS_LOCAL_NETWORK` が nearby devices 系 permission set に含められる。
- local network permission state を network enforcement に渡す基盤が追加されている。
- Change ID `365139289L` が `RESTRICT_LOCAL_NETWORK` として参照される。

観察（Observations）:
- カメラ連携アプリの中核機能は direct local network access に該当する可能性が高い。

仮説（Hypotheses）:
- 対象アプリがカメラ探索・接続・転送に direct socket / HTTP / mDNS / NSD を使っている場合、Android 17 / targetSdkVersion 37 で runtime permission UX が必要になる。

結論（Conclusion）:
- 最優先確認項目。対象アプリの manifest / local network API usage / permission denied handling を確認する必要がある。

## アプリ影響（App Impact）

想定される影響:
- permission 未許可時にカメラ探索、接続、転送、リモート操作が失敗する可能性。

ユーザー影響:
- 初回接続時の権限要求が増える。
- 権限拒否または取り消し後にカメラが見つからない、接続できない、転送できない状態になる可能性。

開発者影響:
- system picker でユーザー許可を取得できる機能か、direct / persistent local network access が必要な機能かを分ける必要がある。
- direct / persistent local network access では、manifest declaration、runtime request、permission denied / revoked handling の設計が必要。
- カメラ連携アプリでは、初回接続・再接続・ライブビュー・リモート操作・転送が direct / persistent access に寄る可能性が高いため、`ACCESS_LOCAL_NETWORK` runtime permission UX を第一候補として設計する。
- picker path を採用できるのは、ユーザーが選択した単一 camera service / endpoint だけで接続と操作が完結し、アプリ側の broad discovery や継続的な LAN 監視が不要な場合に限られる可能性が高い。

既存実装で確認すべき点:
- local network access の全 entry point。
- permission request timing。
- カメラ Wi-Fi への接続導線。
- OS 設定から権限を取り消した後の recovery。
- system-mediated picker で成立する機能と、`ACCESS_LOCAL_NETWORK` runtime permission が必要な機能の切り分け。

推奨対応候補:
- local network access を棚卸しする。
- カメラ探索、カメラ側 Wi-Fi AP 接続、ライブビュー、リモート操作、画像 / 動画転送、再接続が direct / persistent local network access に該当するか確認する。
- direct / persistent local network access については、manifest に `ACCESS_LOCAL_NETWORK` を追加し、コードで runtime permission request と拒否時の案内を実装する。
- system-mediated picker は、単一 device / service selection だけで完結する限定機能に適用できるかを個別に検討する。
- Android 17 / targetSdkVersion 37 で permission denied / granted / revoked をテストする。
- 権限説明文をカメラ接続の文脈に合わせる。

## Confidence

Confidence:
- Medium

Confidence の根拠:
- frameworks-base で permission / AppOp / compat path は確認済み。

不足している根拠:
- 対象アプリ実装。
- connectivity module の最終 enforcement。

---

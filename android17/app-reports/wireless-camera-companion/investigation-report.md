# カメラ連携アプリ Android 17 Behavior Changes 調査レポート

## 基本情報（Metadata）

### 対象アプリ（Target App）

アプリ名:
- 非記載。本文・ファイル名には対象アプリを特定できる名称を含めない。

パッケージ名:
- 非記載。

現在の targetSdkVersion:
- 要確認。

想定する更新後 targetSdkVersion:
- 37

主な機能領域:
- [x] Bluetooth / Connectivity
- [x] Wi-Fi / local network
- [x] 画像 / 動画転送
- [x] リモート操作
- [x] 位置情報または Nearby devices 周辺の権限利用可能性
- [x] WebView / Network / TLS
- [x] Large Screen / Window
- [ ] 通知
- [ ] バックグラウンド処理
- [ ] Foreground Service
- [ ] カメラ / マイク
- [ ] メディア / Audio
- [ ] Contacts / Calendar / Storage
- [ ] 認証 / Credential
- [ ] その他:

### 調査対象 Android バージョン（Android Versions）

From:
- android-16.0.0_r4

To:
- android-17.0.0_r1

### 調査日（Investigation Date）

2026-06-19

### 調査範囲（Scope）

対象にした Behavior Change 文書:
- https://developer.android.com/about/versions/17/behavior-changes-all
- https://developer.android.com/about/versions/17/behavior-changes-17

対象外にした領域:
- 対象アプリのソースコード、APK、manifest、通信先一覧、実機ログの直接確認。
- アプリ固有の最終優先度、最終 severity、リリース可否判断。
- 対象アプリを特定できる名称、パッケージ名、ストア URL の記載。

アプリコード確認の有無:
- なし。

確認したアプリ実装範囲:
- API usage: 未確認。カメラ連携アプリとして Bluetooth、Wi-Fi / LAN、HTTP(S)、画像 / 動画転送、リモート操作を利用する前提で仮評価。
- Manifest: 未確認。`ACCESS_LOCAL_NETWORK`、Bluetooth / Nearby devices、location、network security config、activity orientation / resize 設定は要確認。
- Permissions: 未確認。local network runtime permission、Bluetooth runtime permissions、location permission の利用有無は要確認。
- Background / service behavior: 未確認。バックグラウンド接続、通知経由起動、PendingIntent / IntentSender 利用は要確認。
- Device / form factor assumptions: スマートフォン中心と推定。ただし tablet / foldable / desktop windowing での利用可能性は要確認。
- 実機・自動テスト: 未実施。

---

# エグゼクティブサマリー（Executive Summary）

対象アプリは、カメラとの Bluetooth / Wi-Fi 接続、ローカルネットワーク上の機器探索・接続、画像 / 動画転送、リモート操作を行う可能性が高い。そのため Android 17 では、特に `ACCESS_LOCAL_NETWORK`、Bluetooth bond loss recovery、RFCOMM `BluetoothSocket.read()`、TLS 周辺の変更を優先確認すべきである。加えて、古いアプリ / SDK の reflection と、画像・動画処理またはネットワーク処理 native library の dynamic loading は、Static final fields / Safer Native DCL-C の 1 項目として確認する。

OS アップデートだけで影響しうる項目は、Bluetooth bond loss 後の autonomous re-pairing と app memory limits である。targetSdkVersion 37 更新時に影響しうる項目は、ローカルネットワーク権限、RFCOMM read EOF、certificate transparency、ECH、Activity Security、大画面制約無視、Static final fields / Safer Native DCL-C である。

現時点では対象アプリの manifest / API usage を直接確認していないため、アプリ固有影響は「要確認」を含む。特にカメラとの直接 Wi-Fi 接続、mDNS / NSD / `.local` 解決、ローカル IP への socket / HTTP 接続がある場合、Android 17 / targetSdkVersion 37 で runtime permission UX と接続失敗時の fallback を設計する必要がある。

---

# 影響一覧（Impact Overview）

| ID | Behavior Change | 関連アプリ機能 | 適用分類 | アプリ影響 | 対応候補 | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| BC-001 | Local network permission required for apps targeting Android 17 | カメラ探索、Wi-Fi 接続、ローカル IP / `.local` / mDNS / NSD、画像転送 | TARGET_SDK_37_CONDITIONAL | 要確認。該当可能性は高い | manifest / permission request / denied handling / picker path の棚卸し | Medium |
| BC-002 | Autonomous re-pairing for Bluetooth bond losses | Bluetooth ペアリング、再接続、接続復旧 | OS_UPDATE_ALL_APPS | 影響ありの可能性 | bond loss、repairing context、`ACTION_KEY_MISSING` のテスト | High |
| BC-003 | Consistent BluetoothSocket read() behavior for RFCOMM | Bluetooth Classic / RFCOMM / SPP 相当の通信 | TARGET_SDK_37_CONDITIONAL | 要確認。RFCOMM 利用時は影響あり | read loop で `-1` を EOF / disconnect として扱う | High |
| BC-004 | Enable CT by default | HTTPS API、クラウド連携、証明書 pinning、staging endpoint | TARGET_SDK_37_CONDITIONAL | 要確認 | 接続先証明書チェーンと Network Security Config を確認 | High |
| BC-005 | ECH enabled | HTTPS / TLS、CDN、企業ネットワーク、通信監視環境 | TARGET_SDK_37_CONDITIONAL | 影響軽微から要確認 | networking library / server ECH support と `<domainEncryption>` 方針を確認 | High |
| BC-006 | Activity Security | 通知、popup、PendingIntent / IntentSender、古いアプリから新しいアプリへの推奨導線、バックグラウンドからの画面起動 | TARGET_SDK_37_CONDITIONAL | ユーザータップ経由なら影響限定的。background 自動起動は要確認 | PendingIntent 実行が user-mediated path か棚卸し | High |
| BC-007 | Large screen orientation / resizability / aspect ratio restrictions ignored | 固定向き UI、リモート操作画面、ライブビュー、画像一覧 | TARGET_SDK_37_CONDITIONAL | 要確認 | tablet / foldable / multi-window で検証 | High |
| BC-008 | App memory limits | 画像 / 動画一覧、サムネイル生成、転送、キャッシュ | OS_UPDATE_ALL_APPS | 影響軽微から要確認 | memory baseline と `ApplicationExitInfo` 収集 | High |
| BC-009 | Background audio hardening | 音声再生 / 音声アラーム | OS_UPDATE_ALL_APPS / TARGET_SDK_37_CONDITIONAL | 影響なしの可能性が高い | 音声バックグラウンド再生がある場合のみ確認 | Medium |
| BC-010 | Static final fields / Safer Native DCL-C | 古いアプリ / SDK の reflection、JNI、画像・動画処理 native library、ネットワーク処理 native library、native dynamic loading | TARGET_SDK_37_CONDITIONAL | 要確認。古い SDK や native plugin 構成では該当可能性あり | reflection / JNI による `static final` 書き換え、`System.load()` 前の read-only 化、native library 展開処理を棚卸し | High |

---

# アプリ影響サマリー（App Impact Summary）

## OS アップデートだけで影響しうる項目（OS Update Impact）

| Behavior Change | 影響条件 | 想定されるアプリ影響 | 推奨確認 |
| --- | --- | --- | --- |
| Autonomous re-pairing for Bluetooth bond losses | Android 17、Bluetooth peripheral bond loss、system autonomous re-pairing attempt、Bluetooth module flag | ペアリング復旧時の broadcast timing や UI flow が変わる可能性。手動再ペアリング案内だけを前提にしている場合、状態表示がずれる可能性。 | bond loss、repairing 成功、repairing 失敗、`ACTION_KEY_MISSING`、ペアリング要求 UI を実機確認する。 |
| App memory limits | Android 17 の対象 device、vendor config / RAM / process state / memory usage 条件 | 画像 / 動画転送、サムネイル生成、大量キャッシュで memory outlier がある場合、process exit として観測される可能性。 | 画像一覧、連続転送、動画転送、長時間接続で memory baseline を測る。`ApplicationExitInfo` の `REASON_OTHER` / `MemoryLimiter:AnonSwap` を確認する。 |

## targetSdkVersion 37 更新で影響しうる項目（Target SDK Impact）

| Behavior Change | targetSdkVersion 条件 | 追加条件 | 想定されるアプリ影響 | 推奨確認 |
| --- | --- | --- | --- | --- |
| Local network permission required for apps targeting Android 17 | targetSdkVersion 37 以上 | direct local network access、LAN device discovery / connection、system picker 利用有無、`ACCESS_LOCAL_NETWORK` grant state | カメラ探索、接続、画像転送、リモート制御が permission denied 時に失敗する可能性。 | local network API / socket / HTTP / mDNS / NSD / `.local` 利用を棚卸しする。system picker でユーザー許可を取得しない direct access では、manifest への `ACCESS_LOCAL_NETWORK` 追記と runtime permission request 実装が必要。 |
| Static final fields / Safer Native DCL-C | targetSdkVersion 37 以上 | reflection / JNI による `static final` field write、または `System.load()` で writable native file を読み込む場合 | 古いアプリ / SDK の runtime patching、画像・動画処理やネットワーク処理の native module 動的差し替えで初期化失敗や crash が起きる可能性。 | 古い reflection 実装、JNI field write、native library の download / generate / extract / update / load 処理を棚卸しする。`System.load()` 前に対象 `.so` を read-only にし、その後に書き換えない。 |
| RFCOMM `BluetoothSocket.read()` EOF | targetSdkVersion 37 以上 | RFCOMM-based `BluetoothSocket`、socket close / disconnect、read loop | `IOException` だけで read loop を終了している場合、切断処理が期待通り動かない可能性。 | `bytesRead == -1` を EOF / disconnect として処理しているか確認する。 |
| Certificate transparency default enabled | targetSdkVersion 37 以上 | platform TLS / HTTPS、証明書チェーン、Network Security Config | CT 要件を満たさない endpoint で HTTPS 接続が失敗する可能性。 | production / staging / test / device-local HTTPS endpoint の証明書チェーンを確認する。 |
| ECH enabled | targetSdkVersion 37 以上 | TLS connection、ECH 対応 library / server、`<domainEncryption>` | SNI 前提の network inspection / filtering 環境で観測・制御の前提が変わる可能性。 | 通信先、library、CDN、enterprise network 条件を確認し、必要なら domain encryption policy を決める。 |
| Activity Security | targetSdkVersion 37 以上 | PendingIntent / IntentSender 経由の background activity start、visible state、ユーザー操作の有無、通知 PendingIntent の種類 | 表示中 popup または通知をユーザーがタップし、Activity PendingIntent を直接実行して新しいアプリを起動する flow では影響は限定的。background service / receiver がユーザー操作なしで接続画面や推奨画面を直接開く設計、または通知タップ後に broadcast / service を挟む trampoline 型は制限される可能性。 | 通知、popup、外部アプリ連携、ペアリング復旧、接続復旧の起動経路を棚卸しする。 |
| Large screen restrictions ignored | targetSdkVersion 37 以上 | `sw >= 600dp`、固定向き / non-resizable / aspect ratio 制約、game 以外 | tablet / foldable / desktop windowing でリモート操作 UI やライブビューが想定外サイズになる可能性。 | `sw >= 600dp`、multi-window、fold / unfold、rotation を検証する。 |

## 影響なし、または影響軽微と判断した項目（No or Low Impact）

| Behavior Change | 判断 | 根拠 | Confidence |
| --- | --- | --- | --- |
| Contacts Provider PII / strict SQL checks | 影響なしの可能性が高い | カメラ連携アプリの主要機能と Contacts Provider data view query の関連が薄い。ただし連絡先共有機能がある場合は要確認。 | Medium |
| SMS OTP protection | 影響なしの可能性が高い | SMS OTP 受信・読み取りが主要機能に見えない。アカウント認証で SMS Retriever / SMS User Consent を使う場合は要確認。 | Medium |
| Background audio hardening | 影響なしから軽微 | カメラ連携・画像転送が主用途で、background audio playback が主機能ではない想定。 | Medium |
| Static final fields / Safer Native DCL-C | 要確認 | カメラ連携アプリでも、古い SDK が reflection / JNI で `static final` を書き換える場合や、画像・動画処理、ネットワーク処理、codec、AI / ML delegate などの native library を実行時に展開・更新して `System.load()` する場合は影響し得る。 | High |

## 要確認の項目（Needs More Evidence）

| Behavior Change | 不足している根拠 | 次に確認すること | Blocker |
| --- | --- | --- | --- |
| Local network permission | manifest、local network API usage、system picker 利用有無、direct socket / HTTP / mDNS / NSD 利用有無 | APK / source で local network access 箇所を検索し、Android 17 / targetSdkVersion 37 で permission denied / granted をテストする。 | 対象アプリ実装未確認 |
| RFCOMM read EOF | Bluetooth Classic / RFCOMM / SPP 利用有無、read loop 実装 | `BluetoothSocket`、`createRfcommSocketToServiceRecord`、`InputStream.read()` 周辺を確認する。 | 対象アプリ実装未確認 |
| CT / ECH | 通信先一覧、Network Security Config、certificate pinning、利用 networking library | production / staging / device-local endpoint の証明書と ECH support を確認する。 | 通信先・設定未確認 |
| Activity Security | PendingIntent / IntentSender 経由の Activity 起動箇所、古いアプリから新しいアプリへの推奨 PendingIntent flow、通知 `contentIntent` / action の種類 | 通知、popup、ペアリング復旧、接続復旧、外部アプリ連携の起動経路を確認する。特にユーザータップ直後に Activity PendingIntent を直接実行するか、broadcast / service / 非同期 callback を挟むか、background 自動実行かを分ける。 | 対象アプリ実装未確認 |
| Large screen | manifest の orientation / resizability / aspect ratio 設定、UI の adaptive 対応 | tablet / foldable / multi-window で主要画面を確認する。 | 対象アプリ実装未確認 |
| Static final fields / Safer Native DCL-C | 古い reflection / JNI 実装、native library の動的展開・更新・読み込み処理、画像・動画処理 / ネットワーク処理 SDK の実装 | `static final` field write、`System.load()`、download / generate / extract した `.so` の file mode を確認する。 | 対象アプリ実装・SDK 実装未確認 |

---

# 推奨テストマトリクス（Recommended Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | Compat flag | 目的（Purpose） | 確認すべき機能 | 期待挙動（Expected behavior） |
| --- | --- | --- | --- | --- | --- |
| Android 16 | 現行 targetSdkVersion | default | baseline | Bluetooth pairing、Wi-Fi 接続、画像 / 動画転送、リモート操作、HTTPS 通信 | 現行の期待挙動。接続成功率、切断復旧、転送速度、UI 状態を記録する。 |
| Android 17 | 現行 targetSdkVersion | default | OS update impact | Bluetooth bond loss、memory pressure、Wi-Fi 接続、画像 / 動画転送 | targetSdkVersion を変えずに、Bluetooth recovery と memory limit の差分を確認する。 |
| Android 17 | 37 | default | targetSdkVersion update impact | local network permission、RFCOMM EOF、CT / ECH、Activity 起動、大画面 UI | permission granted / denied、切断、証明書、起動制限、画面リサイズを確認する。 |
| Android 17 | 現行 targetSdkVersion | force-enabled if available | isolated targeted change | RFCOMM EOF、Activity Security、CT / ECH など compat flag 対象項目 | compat flag を有効化して個別差分を再現できるか確認する。 |
| Android 17 | 37 | force-disabled if available | rollback / opt-out behavior | RFCOMM EOF、Activity Security、CT / ECH、大画面制約 | compat flag 無効化または設定変更で fallback できるか確認する。 |

追加テスト:
- Android 17 / targetSdkVersion 37 / local network permission denied: カメラ探索、手動 IP 接続、画像転送、リモート操作が適切に失敗・案内されること。
- Android 17 / targetSdkVersion 37 / local network permission granted: 初回接続、再接続、OS 設定からの権限取り消し後の復旧。
- Android 17 / targetSdkVersion 37 / Bluetooth off、range out、peripheral 側 bond loss: UI 状態、re-pairing、manual recovery の整合性。
- Android 17 / targetSdkVersion 37 / tablet or foldable: ライブビュー、設定画面、画像一覧、転送進捗が崩れないこと。

---

# 個別調査結果（Per Behavior Change Investigation）

## BC-001: Local network permission required for apps targeting Android 17

### 基本情報（Basic Information）

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/17/behavior-changes-17
- Section: Local network permission required for apps targeting Android 17

Original statement:
> Android 17 を target にするアプリでは、direct local network access に新しい runtime permission または system-mediated picker が必要になる、という趣旨の公式説明。

調査対象 Android バージョン:
- From: android-16.0.0_r4
- To: android-17.0.0_r1

### 対象アプリとの関係（Relevance to Target App）

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

確認したアプリ実装:
- File / module: 未確認。
- Symbol / entry point: 未確認。
- Manifest / permission: 未確認。
- Runtime condition: カメラ探索 / 接続 / 転送時。

### 適用条件分類（Applicability Classification）

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

### AOSP 調査（AOSP Investigation）

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
| `core/res/AndroidManifest.xml` / `ACCESS_LOCAL_NETWORK` | permission 定義なし | dangerous permission として追加 | runtime permission としての公開根拠。 |
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

### 事実・観察・仮説・結論（Facts / Observations / Hypotheses / Conclusion）

事実（Facts）:
- Android 17 で `ACCESS_LOCAL_NETWORK` dangerous permission と関連 AppOp が追加されている。
- local network permission state を network enforcement に渡す基盤が追加されている。
- Change ID `365139289L` が `RESTRICT_LOCAL_NETWORK` として参照される。

観察（Observations）:
- カメラ連携アプリの中核機能は direct local network access に該当する可能性が高い。

仮説（Hypotheses）:
- 対象アプリがカメラ探索・接続・転送に direct socket / HTTP / mDNS / NSD を使っている場合、Android 17 / targetSdkVersion 37 で runtime permission UX が必要になる。

結論（Conclusion）:
- 最優先確認項目。対象アプリの manifest / local network API usage / permission denied handling を確認する必要がある。

### アプリ影響（App Impact）

想定される影響:
- permission 未許可時にカメラ探索、接続、転送、リモート操作が失敗する可能性。

ユーザー影響:
- 初回接続時の権限要求が増える。
- 権限拒否または取り消し後にカメラが見つからない、接続できない、転送できない状態になる可能性。

開発者影響:
- system picker でユーザー許可を取得できる機能か、direct / persistent local network access が必要な機能かを分ける必要がある。
- direct / persistent local network access では、manifest declaration、runtime request、permission denied / revoked handling の設計が必要。

既存実装で確認すべき点:
- local network access の全 entry point。
- permission request timing。
- カメラ Wi-Fi への接続導線。
- OS 設定から権限を取り消した後の recovery。

推奨対応候補:
- local network access を棚卸しする。
- system picker を使わない direct local network access については、manifest に `ACCESS_LOCAL_NETWORK` を追加し、コードで runtime permission request と拒否時の案内を実装する。
- Android 17 / targetSdkVersion 37 で permission denied / granted / revoked をテストする。
- 権限説明文をカメラ接続の文脈に合わせる。

### Confidence

Confidence:
- Medium

Confidence の根拠:
- frameworks-base で permission / AppOp / compat path は確認済み。

不足している根拠:
- 対象アプリ実装。
- connectivity module の最終 enforcement。

---

## BC-002: Autonomous re-pairing for Bluetooth bond losses

### 基本情報（Basic Information）

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/17/behavior-changes-all
- Section: Autonomous re-pairing for Bluetooth bond losses

Original statement:
> Android 17 では Bluetooth bond loss 後に system が autonomous re-pairing を試行できる、という趣旨の公式説明。

調査対象 Android バージョン:
- From: android-16.0.0_r4
- To: android-17.0.0_r1

### 対象アプリとの関係（Relevance to Target App）

関連するアプリ機能:
- Bluetooth pairing。
- 接続復旧。
- カメラとの再接続。
- ユーザーへの再ペアリング案内。

関連する API / permission / component:
- `ACTION_PAIRING_REQUEST`
- `ACTION_KEY_MISSING`
- `EXTRA_PAIRING_CONTEXT`
- `PAIRING_CONTEXT_REPAIRING`

アプリが該当する可能性:
- Conditional。Bluetooth pairing / bond state / key missing を扱う場合は該当可能性が高い。

判断理由:
- カメラ連携アプリでは Bluetooth を初期接続、Wi-Fi 起動、時刻同期、位置情報連携、再接続の補助に使う可能性がある。bond loss recovery flow の変化は UX に影響しうる。

### 適用条件分類（Applicability Classification）

主分類（Primary classification）:
- OS_UPDATE_ALL_APPS

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | Yes / Conditional | 公式文書は all apps。Bluetooth module evidence に targetSdkVersion gate は見つからない。 |
| targetSdkVersion 37 以上が必要か | No | targetSdkVersion gate は確認されない。 |
| 追加の実行時条件があるか | Yes | Bluetooth peripheral bond loss、system autonomous re-pairing attempt、feature flag。 |
| Compat Change ID が関係するか | No | compat Change ID は見つからない。 |

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17。
- targetSdkVersion: 条件なし。
- Device/form factor: Bluetooth peripheral と bonding が必要。
- Permission/API/component condition: Bluetooth pairing / bond state handling。
- App state/process condition: bond loss / reconnect / pairing recovery。
- Manifest/property condition: Bluetooth permission / receiver 設計は要確認。
- Mainline/module condition: Bluetooth module feature flag の release default は要確認。

Compat framework:
- Change ID: 見つからない。
- Change name: N/A
- Default state: Bluetooth module feature flag に依存。
- Toggleable for testing: 要確認。

### AOSP 調査（AOSP Investigation）

関連ファイル:
- `platform/packages/modules/Bluetooth/framework/java/android/bluetooth/BluetoothDevice.java`
- `platform/packages/modules/Bluetooth/android/app/src/com/android/bluetooth/btservice/BondStateMachine.java`
- `platform/packages/modules/Bluetooth/android/app/src/com/android/bluetooth/btservice/RemoteDevices.java`
- `platform/packages/modules/Bluetooth/flags/framework.aconfig`

確認したソース文脈（Source Context Reviewed）:

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `BluetoothDevice` / pairing context extras | pairing context extras なし | `EXTRA_PAIRING_CONTEXT` と `PAIRING_CONTEXT_REPAIRING` などが追加 | アプリが pairing request の文脈を判別できる公開 API。 |
| `BondStateMachine` | autonomous repairing context を intent に含めない | pairing request / bond state change intent に context を含める | アプリが受け取る broadcast 内容が変わる。 |
| `RemoteDevices` | bond loss 復旧 path が限定的 | bond loss 検出時に autonomous repairing を開始し、失敗時に `ACTION_KEY_MISSING` を送る path | 接続復旧 UI / recovery flow に直接関係する。 |

必須記入項目:
- Entry point / caller: Bluetooth stack の bond loss detection -> autonomous repairing -> pairing request / key missing broadcast。
- Relevant class or service responsibility: Bluetooth pairing / bonding state 管理。
- Runtime path from app API / system event to changed code: peripheral bond loss -> system repair attempt -> broadcast / UI flow。
- Why unrelated code paths were excluded: RFCOMM read EOF は別 Behavior Change として分離。

差分解釈（Diff Interpretation）:
- Added behavior: autonomous repairing と pairing context extras。
- Changed condition / gate: Bluetooth module feature flag。

適用ゲート根拠（Applicability Gate Evidence）:
- targetSdkVersion gate: 見つからない。
- CompatChanges.isChangeEnabled / ChangeId: 見つからない。
- No gate found: targetSdkVersion gate は確認されず、OS update / all apps と扱う。
- Gate conclusion: Android 17 の対象 Bluetooth module で bond loss 条件が成立する場合に適用。

### 事実・観察・仮説・結論（Facts / Observations / Hypotheses / Conclusion）

事実（Facts）:
- Android 17 Bluetooth module に pairing context extras と autonomous repairing path が追加されている。
- targetSdkVersion gate は見つからない。

観察（Observations）:
- 対象アプリが bond state や pairing broadcast に依存する場合、Android 17 OS 更新だけで復旧 flow が変わる可能性がある。

仮説（Hypotheses）:
- 手動再ペアリング案内を固定的に出す実装では、system repair attempt 中の UI と競合する可能性がある。

結論（Conclusion）:
- Bluetooth 接続復旧の実機テストが必要。OS update impact として優先度は高い。

### アプリ影響（App Impact）

想定される影響:
- bond loss 後、アプリ側が想定する manual recovery 前に system repair attempt が発生する。
- `ACTION_KEY_MISSING` の timing が変わる。

ユーザー影響:
- 再接続時の案内、ダイアログ、ペアリング要求が従来と異なる可能性。

開発者影響:
- pairing context を見て repairing と通常 pairing を区別する実装が望ましい。

既存実装で確認すべき点:
- pairing / bond state receiver。
- key missing handling。
- 手動 unpair / re-pair guidance。

推奨対応候補:
- `EXTRA_PAIRING_CONTEXT` を利用できる場合は context を区別する。
- bond loss、repairing 成功、repairing 失敗を実機で確認する。

### Confidence

Confidence:
- High

Confidence の根拠:
- Bluetooth module evidence と targetSdkVersion gate 不在を確認済み。

不足している根拠:
- release build での flag default / device config override。
- 対象アプリ実装。

---

## BC-003: Consistent BluetoothSocket read() behavior for RFCOMM

### 基本情報（Basic Information）

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/17/behavior-changes-17
- Section: Consistent BluetoothSocket read() behavior for RFCOMM

Original statement:
> targetSdkVersion 37 のアプリでは、RFCOMM-based `BluetoothSocket` の `InputStream.read()` が socket closed / connection dropped 時に `-1` を返す、という趣旨の公式説明。

調査対象 Android バージョン:
- From: android-16.0.0_r4
- To: android-17.0.0_r1

### 対象アプリとの関係（Relevance to Target App）

関連するアプリ機能:
- Bluetooth Classic / RFCOMM / SPP 相当の通信。
- カメラとの制御チャネル、ステータス取得、接続維持。

関連する API / permission / component:
- `BluetoothSocket`
- `InputStream.read()`
- RFCOMM socket

アプリが該当する可能性:
- Unknown / Conditional。Bluetooth Low Energy のみなら直接影響は限定的。Bluetooth Classic / RFCOMM を使う場合は該当。

判断理由:
- カメラ連携アプリが Classic Bluetooth RFCOMM を利用するか未確認。利用している場合、切断処理の read loop に直接影響する。

### 適用条件分類（Applicability Classification）

主分類（Primary classification）:
- TARGET_SDK_37_CONDITIONAL

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | No | Android 17 / targetSdkVersion 36 では旧挙動。 |
| targetSdkVersion 37 以上が必要か | Yes | Change ID `383671392` が targetSdkVersion 37 で enabled。 |
| 追加の実行時条件があるか | Yes | RFCOMM `BluetoothSocket`、read loop、socket close / disconnect。 |
| Compat Change ID が関係するか | Yes | `MAKE_SOCKET_READ_BEHAVIOR_CONSISTENT`。 |

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17。
- targetSdkVersion: 37 以上。
- Device/form factor: 条件なし。
- Permission/API/component condition: RFCOMM-based `BluetoothSocket`。
- App state/process condition: read 中の local close / remote disconnect / connection drop。

Compat framework:
- Change ID: `383671392`
- Change name: `MAKE_SOCKET_READ_BEHAVIOR_CONSISTENT`
- Default state: `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.CINNAMON_BUN)`
- Toggleable for testing: compat change として確認候補。

### AOSP 調査（AOSP Investigation）

関連ファイル:
- `tmp/aosp-checkouts/Bluetooth/framework/java/android/bluetooth/BluetoothSocket.java`

確認したソース文脈（Source Context Reviewed）:

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `BluetoothSocket.java` / read EOF path | EOF 時に `IOException` path | targetSdkVersion 37 以上では `-1` を返す | アプリの read loop が直接呼ぶ API の挙動差分。 |

必須記入項目:
- Entry point / caller: app read loop -> `BluetoothSocket` input stream -> RFCOMM socket。
- Relevant class or service responsibility: Bluetooth socket read / EOF handling。
- Runtime path from app API / system event to changed code: remote disconnect / local close -> `read()` return path。
- Why unrelated code paths were excluded: BLE GATT は RFCOMM `BluetoothSocket` ではないため除外。

差分解釈（Diff Interpretation）:
- Changed condition / gate: targetSdkVersion 37 以上で EOF が `-1`。
- Removed behavior: targetSdkVersion 37 以上では EOF を `IOException` だけで扱う旧挙動から変わる。

適用ゲート根拠（Applicability Gate Evidence）:
- targetSdkVersion gate: targetSdkVersion 37。
- CompatChanges.isChangeEnabled / ChangeId: `383671392`。
- @EnabledAfter / @EnabledSince / default state: targetSdkVersion 37 以上で enabled。
- Gate conclusion: Android 17 / targetSdkVersion 37 / RFCOMM `BluetoothSocket` read loop に適用。

### 事実・観察・仮説・結論（Facts / Observations / Hypotheses / Conclusion）

事実（Facts）:
- Android 17 / targetSdkVersion 37 では RFCOMM read EOF が `-1` を返す。

観察（Observations）:
- `IOException` catch だけで切断処理をしている実装は影響を受ける。

仮説（Hypotheses）:
- 対象アプリが RFCOMM を使う場合、切断時の loop 終了、UI 更新、再接続 trigger が変わる可能性がある。

結論（Conclusion）:
- RFCOMM 利用有無と read loop 実装を確認する。該当する場合は対応必須候補。

### アプリ影響（App Impact）

想定される影響:
- 切断時に read loop が終了しない、または disconnect UI に遷移しない可能性。

ユーザー影響:
- カメラ切断後も接続中表示が残る、再接続できない、転送中 UI が止まる可能性。

開発者影響:
- `bytesRead == -1` を EOF / disconnect として処理する修正が必要。

既存実装で確認すべき点:
- `BluetoothSocket.getInputStream().read()` の戻り値 check。
- `IOException` catch だけで終了していないか。

推奨対応候補:
- `-1` handling を追加する。
- remote disconnect、local close、Bluetooth off、range out をテストする。

### Confidence

Confidence:
- High

Confidence の根拠:
- Bluetooth module の Change ID、targetSdkVersion gate、EOF handling を確認済み。

不足している根拠:
- 対象アプリが RFCOMM を使うか未確認。

---

## BC-004: Enable CT by default

### 基本情報（Basic Information）

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/17/behavior-changes-17
- Section: Enable CT by default

Original statement:
> targetSdkVersion 37 以上のアプリでは certificate transparency が default enabled になる、という趣旨の公式説明。

調査対象 Android バージョン:
- From: android-16.0.0_r4
- To: android-17.0.0_r1

### 対象アプリとの関係（Relevance to Target App）

関連するアプリ機能:
- HTTPS API。
- アカウント連携。
- ファームウェア情報取得。
- クラウド同期。
- 利用規約 / お知らせ / ヘルプ表示。
- staging / test endpoint。

関連する API / permission / component:
- platform TLS / HTTPS。
- Network Security Config。
- certificate pinning。

アプリが該当する可能性:
- Conditional。HTTPS 通信がある場合は該当。

判断理由:
- カメラ連携アプリでもクラウド API、サポート情報、利用規約、ファームウェア情報など HTTPS 通信を行う可能性が高い。

### 適用条件分類（Applicability Classification）

主分類（Primary classification）:
- TARGET_SDK_37_CONDITIONAL

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | No | Change ID は targetSdkVersion 37 以上で default enabled。 |
| targetSdkVersion 37 以上が必要か | Yes | `DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY`。 |
| 追加の実行時条件があるか | Yes | TLS / HTTPS、CT policy、証明書チェーン、Network Security Config。 |
| Compat Change ID が関係するか | Yes | `407952621`。 |

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17。
- targetSdkVersion: 37 以上。
- Permission/API/component condition: platform TLS / HTTPS certificate validation。
- Manifest/property condition: Network Security Config の CT 設定。

Compat framework:
- Change ID: `407952621`
- Change name: `DEFAULT_ENABLE_CERTIFICATE_TRANSPARENCY`
- Default state: targetSdkVersion 37 以上で default enabled。
- Toggleable for testing: compat change として確認候補。

### AOSP 調査（AOSP Investigation）

関連ファイル:
- `packages/NetworkSecurityConfig/platform/src/android/security/net/config/NetworkSecurityConfig.java`
- `NetworkSecurityTrustManager.java`
- `RootTrustManager.java`
- `XmlConfigSource.java`

確認したソース文脈（Source Context Reviewed）:

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `NetworkSecurityConfig` / CT default policy | CT は app opt-in が必要 | targetSdkVersion 37 以上で default enabled | platform TLS validation の default policy に直接関係する。 |

差分解釈（Diff Interpretation）:
- Changed default: CT default policy が targetSdkVersion 37 以上で有効。
- Changed condition / gate: Change ID `407952621`。

適用ゲート根拠（Applicability Gate Evidence）:
- targetSdkVersion gate: targetSdkVersion 37 以上。
- CompatChanges.isChangeEnabled / ChangeId: `407952621`。
- Gate conclusion: Android 17 / targetSdkVersion 37 / platform TLS / HTTPS 接続に適用。

### 事実・観察・仮説・結論（Facts / Observations / Hypotheses / Conclusion）

事実（Facts）:
- Android 17 / targetSdkVersion 37 では CT default enabled。

観察（Observations）:
- production endpoint は問題ない可能性が高いが、staging、private PKI、device-local HTTPS、pinning では要確認。

仮説（Hypotheses）:
- 対象アプリが private CA、自己署名、local HTTPS endpoint、古い証明書チェーンを利用している場合、targetSdkVersion 37 更新時に接続影響が出る可能性。

結論（Conclusion）:
- 通信先棚卸しと Android 17 / targetSdkVersion 37 接続テストが必要。

### アプリ影響（App Impact）

想定される影響:
- HTTPS 接続失敗。
- ログイン、クラウド同期、サポート表示、ファームウェア情報取得の失敗。

ユーザー影響:
- 一部ネットワーク機能が利用できない可能性。

開発者影響:
- 証明書チェーン、pinning、Network Security Config、staging endpoint の見直し。

推奨対応候補:
- 全 endpoint の証明書チェーンを確認する。
- Android 17 / targetSdkVersion 37 で接続テストする。

### Confidence

Confidence:
- High

Confidence の根拠:
- AOSP Change ID と Network Security Config path を確認済み。

不足している根拠:
- 対象アプリの endpoint / certificate policy。

---

## BC-005: ECH enabled

### 基本情報（Basic Information）

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/17/behavior-changes-17
- Section: ECH enabled

Original statement:
> targetSdkVersion 37 以上のアプリでは TLS connection に ECH が使われる可能性がある、という趣旨の公式説明。

調査対象 Android バージョン:
- From: android-16.0.0_r4
- To: android-17.0.0_r1

### 対象アプリとの関係（Relevance to Target App）

関連するアプリ機能:
- HTTPS / TLS 通信。
- CDN / API / WebView。
- 企業ネットワークや TLS inspection 環境での利用。

関連する API / permission / component:
- Network Security Config `<domainEncryption>`。
- platform networking library。
- ECH 対応 server / CDN。

アプリが該当する可能性:
- Conditional。HTTPS 通信と ECH 対応 library / server 条件がある。

### 適用条件分類（Applicability Classification）

主分類（Primary classification）:
- TARGET_SDK_37_CONDITIONAL

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | No | compat change は targetSdkVersion 37 以上で default enabled。 |
| targetSdkVersion 37 以上が必要か | Yes | `ENABLE_DEFAULT_ENCRYPTED_CLIENT_HELLO`。 |
| 追加の実行時条件があるか | Yes | TLS、ECH 対応 library / server、domain encryption mode。 |
| Compat Change ID が関係するか | Yes | `419020719`。 |

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17。
- targetSdkVersion: 37 以上。
- Permission/API/component condition: TLS connection。
- Manifest/property condition: `<domainEncryption>` が disabled でないこと。
- Mainline/module condition: platform ECH configuration。

Compat framework:
- Change ID: `419020719`
- Change name: `ENABLE_DEFAULT_ENCRYPTED_CLIENT_HELLO`
- Default state: targetSdkVersion 37 以上で default enabled。
- Toggleable for testing: compat change として確認候補。

### AOSP 調査（AOSP Investigation）

関連ファイル:
- `NetworkSecurityConfig.java`
- `XmlConfigSource.java`
- `ApplicationConfig.java`
- `ConfigNetworkSecurityPolicy.java`
- `NetworkSecurityPolicy.java`

確認したソース文脈（Source Context Reviewed）:

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `NetworkSecurityConfig.defaultDomainEncryptionMode()` | default ECH gate なし | 条件を満たす場合に opportunistic mode | TLS 接続の domain encryption policy に直接関係する。 |
| `XmlConfigSource` / `<domainEncryption>` | 設定なし | domain encryption parser 追加 | app 側で ECH 方針を制御できる。 |

差分解釈（Diff Interpretation）:
- Added behavior: `<domainEncryption>` parser / API surface。
- Changed default: targetSdkVersion 37 以上で opportunistic mode。
- Changed condition / gate: Change ID `419020719`。

適用ゲート根拠（Applicability Gate Evidence）:
- targetSdkVersion gate: targetSdkVersion 37 以上。
- CompatChanges.isChangeEnabled / ChangeId: `419020719`。
- Gate conclusion: Android 17 / targetSdkVersion 37 / TLS / ECH 対応条件で適用。

### 事実・観察・仮説・結論（Facts / Observations / Hypotheses / Conclusion）

事実（Facts）:
- Android 17 / targetSdkVersion 37 で default domain encryption mode が opportunistic になり得る。

観察（Observations）:
- ECH は privacy improvement であり、一般ユーザー環境では問題になりにくい可能性がある。

仮説（Hypotheses）:
- 企業ネットワーク、SNI-based filtering、TLS inspection を前提にした環境では接続観測・制御の前提が変わる可能性。

結論（Conclusion）:
- 通信先と利用 library を確認し、必要なら Network Security Config の domain encryption 方針を決める。

### アプリ影響（App Impact）

想定される影響:
- 一部ネットワーク環境で通信観測・制御・トラブルシュートが変わる可能性。

ユーザー影響:
- 通常は軽微。ただし企業ネットワーク等で接続問題が出る可能性。

開発者影響:
- `<domainEncryption>` の global / per-domain 方針を検討する。

推奨対応候補:
- ECH 対応 library / server / CDN を確認する。
- Android 17 / targetSdkVersion 37 で主要 endpoint へ接続する。

### Confidence

Confidence:
- High

Confidence の根拠:
- AOSP Change ID、Network Security Config API、domain encryption path を確認済み。

不足している根拠:
- 対象アプリの networking library / endpoint。

---

## BC-006: Activity Security

### 基本情報（Basic Information）

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/17/behavior-changes-17
- Section: Activity Security

参考 URL:
- https://developer.android.com/guide/components/activities/secure-bal

Original statement:
> PendingIntent / IntentSender 経由の Background Activity Launch がより厳格になる、という趣旨の公式説明。

調査対象 Android バージョン:
- From: android-16.0.0_r4
- To: android-17.0.0_r1

### 対象アプリとの関係（Relevance to Target App）

関連するアプリ機能:
- 通知からの画面起動。
- 表示中 popup / dialog からの推奨アプリ起動。
- カメラ接続復旧後の画面表示。
- ペアリング / Wi-Fi 接続案内。
- 外部アプリ / system UI / PendingIntent 経由の起動。

関連する API / permission / component:
- `PendingIntent`
- `IntentSender`
- `ActivityOptions`
- Background Activity Launch mode

アプリが該当する可能性:
- Unknown / Conditional。background から Activity を直接起動する経路がある場合に該当。表示中 popup または通知をユーザーが明示的にタップし、Activity PendingIntent を直接実行する flow では影響は限定的と考えられる。通知タップ後に broadcast / service / 非同期 callback を挟んで Activity を起動する場合は別途確認が必要。

### 適用条件分類（Applicability Classification）

主分類（Primary classification）:
- TARGET_SDK_37_CONDITIONAL

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | No | `ASM_RESTRICTIONS` は targetSdkVersion 37 以上で enabled。 |
| targetSdkVersion 37 以上が必要か | Yes | `@EnabledAfter(targetSdkVersion = BAKLAVA)`。 |
| 追加の実行時条件があるか | Yes | PendingIntent / IntentSender 経由の BAL、caller visible state。 |
| Compat Change ID が関係するか | Yes | `230590090L`。 |

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17。
- targetSdkVersion: 37 以上。
- App state/process condition: background activity start。caller / real caller が visible か、ユーザー操作直後かを確認する必要がある。
- Permission/API/component condition: PendingIntent / IntentSender。

Compat framework:
- Change ID: `230590090L`
- Change name: `ASM_RESTRICTIONS`
- Default state: targetSdkVersion 37 以上で enabled。
- Toggleable for testing: `@Overridable`。

### AOSP 調査（AOSP Investigation）

関連ファイル:
- `core/java/android/app/ActivityOptions.java`
- `services/core/java/com/android/server/wm/BackgroundActivityStartController.java`

確認したソース文脈（Source Context Reviewed）:

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `ActivityOptions` / BAL modes | legacy `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` | `ALLOW_IF_VISIBLE` / `ALLOW_ALWAYS` への移行 | app が設定する BAL privilege に直接関係する。 |
| `BackgroundActivityStartController` / `ASM_RESTRICTIONS` | legacy mode の許可範囲が広い | targetSdkVersion 37 以上で stricter evaluation | background からの画面起動可否を決める。 |

差分解釈（Diff Interpretation）:
- Changed condition / gate: targetSdkVersion 37 以上で stricter BAL rules。
- Added behavior: `ALLOW_IF_VISIBLE` / `ALLOW_ALWAYS` modes。

適用ゲート根拠（Applicability Gate Evidence）:
- targetSdkVersion gate: targetSdkVersion 37 以上。
- CompatChanges.isChangeEnabled / ChangeId: `230590090L`。
- Gate conclusion: Android 17 / targetSdkVersion 37 / PendingIntent or IntentSender BAL path に適用。

### 事実・観察・仮説・結論（Facts / Observations / Hypotheses / Conclusion）

事実（Facts）:
- `ASM_RESTRICTIONS` は targetSdkVersion 37 以上で enabled。
- 公式 Activity security guide は、system が送信した notification `PendingIntent` から Activity が起動される場合を background activity start が許可される例外として説明している。
- 同 guide は、`PendingIntent` / `IntentSender` では creator または sender が BAL privileges を opt-in し、かつその app が BAL exception を満たす必要があると説明している。
- 同 guide は、sender 側 opt-in では `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` を推奨しており、この mode は `PendingIntent` 送信時に sender app が画面上で visible な場合だけ許可する。

観察（Observations）:
- 接続復旧やペアリング案内を background から直接 Activity 起動する設計は制限される可能性がある。
- 古いカメラ連携アプリと新しいカメラ連携アプリの両方に対応するカメラへ接続した際、古いアプリが表示中 popup で新しいアプリの利用を推奨し、ユーザーのタップ後に PendingIntent で新しいアプリを起動する flow は、user-mediated / visible flow として扱える可能性が高い。
- ユーザーが他アプリを操作中でも、Foreground Service notification または push notification をタップし、通知の `contentIntent` / action が新しいアプリの Activity PendingIntent を直接起動する flow であれば、公式 guide の notification `PendingIntent` 例外に近い user-mediated launch として影響は限定的と考えられる。

仮説（Hypotheses）:
- 対象アプリが background service や receiver から接続画面を直接開く場合、Android 17 / targetSdkVersion 37 で起動が抑制される可能性。
- 同じ推奨導線でも、カメラ接続検知後に background service / receiver がユーザー操作なしで PendingIntent を実行し、新しいアプリの Activity を自動表示する実装であれば、Android 17 / targetSdkVersion 37 で制限対象になる可能性がある。
- 通知タップ後に receiver / service で接続状態確認や互換性判定を行い、その後で Activity を起動する notification trampoline 型または遅延 background 起動の実装では、通知タップがあっても制限対象になる可能性がある。

結論（Conclusion）:
- PendingIntent / IntentSender / background Activity start を棚卸しし、通知や表示中 popup など user-mediated path に寄せる。
- 今回の推奨アプリ起動シナリオは、ユーザーが popup / 通知を明示的にタップし、Activity PendingIntent が直接実行される限り影響は限定的と考えられる。ただし、ユーザー操作なしの background 自動起動、または通知タップ後に receiver / service / 非同期処理を挟む起動であれば要対応候補になる。
- `PendingIntent` / `IntentSender` の sender 側では、Android 17 / targetSdkVersion 37 の検証時に `ActivityOptions#setPendingIntentBackgroundActivityStartMode()` と `ALLOW_IF_VISIBLE` の利用可否を確認する。creator 側が privileges を delegate する必要がある設計かどうかも分けて確認する。

### アプリ影響（App Impact）

想定される影響:
- background からの接続画面・復旧画面起動が失敗する可能性。
- 古いカメラ連携アプリから新しいカメラ連携アプリへの推奨導線で、ユーザー操作なしに Activity を自動表示している場合、起動が拒否される可能性。

ユーザー影響:
- ペアリングや再接続の案内が表示されない、または通知経由操作が必要になる可能性。
- 表示中 popup または通知をタップして新しいアプリへ遷移する設計であれば、ユーザー影響は限定的と見込まれる。
- 他アプリ操作中に通知をタップする flow でも、通知が直接 Activity PendingIntent を起動する設計であれば、ユーザー影響は限定的と見込まれる。

開発者影響:
- `ALLOW_IF_VISIBLE` / `ALLOW_ALWAYS` の使い分けと通知導線の設計。
- 推奨アプリ起動の PendingIntent が、ユーザータップ直後に実行されているか、background service / receiver から自動実行されているかを分けて確認する必要がある。
- 通知経由の起動では、notification の `contentIntent` / action が Activity PendingIntent か、broadcast / service trampoline かを分けて確認する必要がある。

推奨対応候補:
- legacy `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` 利用を検索する。
- `PendingIntent.send()`、`Context.startIntentSender()`、`IntentSender.sendIntent()`、`ActivityResultLauncher<IntentSenderRequest>` の利用箇所を検索する。
- 表示中 popup / dialog / Activity のボタン押下、または通知タップから Activity PendingIntent を直接実行する flow では、`ALLOW_IF_VISIBLE` 相当で足りるかを確認する。
- sender 側で `ActivityOptions#setPendingIntentBackgroundActivityStartMode(ActivityOptions.MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE)` を付与できるか確認する。
- creator 側で `PendingIntent` を作成して他 component / 他 app に渡している場合は、creator privileges の opt-in が必要な flow か確認する。
- 通知 `contentIntent` / action が broadcast / service を指している場合は、Activity PendingIntent へ直接つなげる設計に変更できるか確認する。
- background 状態でユーザー操作なしに起動している場合は、通知または visible UI 経由に変更する。
- Android 17 / targetSdkVersion 37 で、popup 表示中のタップ、通知タップからの直接 Activity 起動、通知タップ後の receiver / service 経由起動、background 自動実行の 4 ケースを分けてテストする。

### Confidence

Confidence:
- High

Confidence の根拠:
- AOSP Change ID と BAL mode path を確認済み。

不足している根拠:
- 対象アプリの起動経路。

---

## BC-007: Large screen orientation / resizability / aspect ratio restrictions ignored

### 基本情報（Basic Information）

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/17/behavior-changes-17
- Section: Platform API changes to ignore orientation, resizability and aspect ratio constraints on large screens

Original statement:
> targetSdkVersion 37 以上では large screen 上で orientation / resizability / aspect ratio restrictions が ignored になる、という趣旨の公式説明。

調査対象 Android バージョン:
- From: android-16.0.0_r4
- To: android-17.0.0_r1

### 対象アプリとの関係（Relevance to Target App）

関連するアプリ機能:
- ライブビュー / リモート操作画面。
- 画像 / 動画一覧。
- 接続設定。
- 固定縦向きまたは固定横向き UI。

関連する API / permission / component:
- `screenOrientation`
- `resizeableActivity`
- `minAspectRatio` / `maxAspectRatio`
- `setRequestedOrientation()`
- Android 16 opt-out property

アプリが該当する可能性:
- Conditional。固定向き・固定比率・non-resizable に依存する UI がある場合に該当。

### 適用条件分類（Applicability Classification）

主分類（Primary classification）:
- TARGET_SDK_37_CONDITIONAL

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | No / Conditional | Android 17 target で opt-out が無効化される。 |
| targetSdkVersion 37 以上が必要か | Yes | `DISABLE_OPT_OUT_UNIVERSAL_RESIZABLE_BY_DEFAULT`。 |
| 追加の実行時条件があるか | Yes | `sw >= 600dp`、game 以外、orientation / resizability / aspect ratio restriction。 |
| Compat Change ID が関係するか | Yes | `357141415L`, `447301631L`。 |

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17。
- targetSdkVersion: 37 以上。
- Device/form factor: `sw >= 600dp`。
- Manifest/property condition: orientation / resizability / aspect ratio restriction、Android 16 opt-out 依存。

Compat framework:
- Change ID: `357141415L`, `447301631L`
- Change name: `UNIVERSAL_RESIZABLE_BY_DEFAULT`, `DISABLE_OPT_OUT_UNIVERSAL_RESIZABLE_BY_DEFAULT`
- Default state: Android 16 target で制約無視 enabled、Android 17 target で opt-out disabled。
- Toggleable for testing: compat change として確認候補。

### AOSP 調査（AOSP Investigation）

関連ファイル:
- `core/java/android/content/pm/ActivityInfo.java`
- `services/core/java/com/android/server/wm/AppCompatResizeOverrides.java`
- `services/core/java/com/android/server/wm/DisplayContent.java`
- `services/core/java/com/android/server/wm/ActivityRecord.java`

確認したソース文脈（Source Context Reviewed）:

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `ActivityInfo` / `UNIVERSAL_RESIZABLE_BY_DEFAULT` | Android 16 target 以上で large screen 制約無視 | Android 17 でも継続 | large screen resize policy の基本 gate。 |
| `AppCompatResizeOverrides` / `DISABLE_OPT_OUT_UNIVERSAL_RESIZABLE_BY_DEFAULT` | Android 16 opt-out property が効く | Android 17 target で opt-out disabled | targetSdkVersion 37 で既存 opt-out に依存できない根拠。 |

差分解釈（Diff Interpretation）:
- Changed condition / gate: Android 17 target で opt-out disabled。
- Changed default: large screen で app resize / orientation constraints の扱いが変わる。

適用ゲート根拠（Applicability Gate Evidence）:
- targetSdkVersion gate: targetSdkVersion 37 以上。
- Device condition: `smallestScreenWidthDp >= 600dp`。
- Gate conclusion: Android 17 / targetSdkVersion 37 / large screen / fixed constraints に適用。

### 事実・観察・仮説・結論（Facts / Observations / Hypotheses / Conclusion）

事実（Facts）:
- Android 17 target では large screen 制約無視への opt-out が無効になる。

観察（Observations）:
- カメラ連携アプリのライブビューやリモート操作 UI は固定比率・固定向きを前提にしている可能性がある。

仮説（Hypotheses）:
- tablet / foldable / desktop windowing で UI 崩れ、操作ボタン位置ずれ、ライブビュー aspect ratio 問題が出る可能性。

結論（Conclusion）:
- targetSdkVersion 37 更新前に large screen 検証が必要。

### アプリ影響（App Impact）

想定される影響:
- レイアウト崩れ、ライブビューの余白 / crop / stretch、操作 UI の重なり。

ユーザー影響:
- tablet / foldable で撮影操作や画像選択がしづらくなる可能性。

開発者影響:
- adaptive layout、configuration change、multi-window 対応確認が必要。

推奨対応候補:
- `sw >= 600dp` 端末、fold / unfold、multi-window resize、rotation で主要画面を確認する。

### Confidence

Confidence:
- High

Confidence の根拠:
- AOSP Change ID、large screen condition、opt-out disabled path を確認済み。

不足している根拠:
- 対象アプリの manifest / UI 実装。

---

## BC-008: App memory limits

### 基本情報（Basic Information）

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/17/behavior-changes-all
- Section: App memory limits

Original statement:
> Android 17 では device total RAM に基づく app memory limits が導入され、一部の Android devices で適用される、という趣旨の公式説明。

調査対象 Android バージョン:
- From: android-16.0.0_r4
- To: android-17.0.0_r1

### 対象アプリとの関係（Relevance to Target App）

関連するアプリ機能:
- 画像 / 動画一覧。
- サムネイル生成。
- RAW / high-resolution image transfer。
- 動画転送。
- キャッシュ。
- WebView。

関連する API / permission / component:
- `ApplicationExitInfo`
- `am memory-limiter`
- trigger-based profiling

アプリが該当する可能性:
- Conditional。対象 device で memory outlier がある場合に該当。

### 適用条件分類（Applicability Classification）

主分類（Primary classification）:
- OS_UPDATE_ALL_APPS

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | Yes / Conditional | AOSP に targetSdkVersion gate は確認されず、device / vendor config 条件で有効。 |
| targetSdkVersion 37 以上が必要か | No | targetSdkVersion gate は確認されない。 |
| 追加の実行時条件があるか | Yes | 対象 device、vendor config、RAM、process state、memory usage。 |
| Compat Change ID が関係するか | No | compat framework ではなく feature flag / vendor config / DeviceConfig 依存。 |

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17。
- targetSdkVersion: 条件なし。
- Device/form factor: memory limiter 対象 device。
- App state/process condition: memory usage が configured limit に到達。
- Mainline/module condition: vendor config / DeviceConfig / feature enabled。

Compat framework:
- Change ID: 確認されず。
- Change name: N/A
- Default state: vendor config / feature flag / DeviceConfig に依存。
- Toggleable for testing: `am memory-limiter` commands。

### AOSP 調査（AOSP Investigation）

関連ファイル:
- `MemoryLimiter.java`
- `com_android_server_am_MemoryLimiter.cpp`
- `ActivityManagerService.java`
- `ActivityManagerShellCommand.java`
- `ProcessRecord.java`
- `memory-limiter-config.xsd`
- `MemoryLimiter.md`

確認したソース文脈（Source Context Reviewed）:

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `MemoryLimiter` | app memory limits なし | process state に応じた memory / swap limits を native cgroup layer に渡す | app process kill / memory anomaly に直接関係する。 |
| `ActivityManagerShellCommand` / `am memory-limiter` | command なし | ignore / manual / status command 追加 | 公式検証手段。 |

差分解釈（Diff Interpretation）:
- Added behavior: MemoryLimiter 本体、JNI、vendor config schema、shell command。
- Changed condition: vendor config と RAM 条件で対象 device が決まる。

適用ゲート根拠（Applicability Gate Evidence）:
- targetSdkVersion gate: 見つからない。
- CompatChanges.isChangeEnabled / ChangeId: 見つからない。
- DeviceConfig / resources config: vendor config / DeviceConfig に依存。
- Gate conclusion: Android 17 上の対象 device で、対象 app process が configured limit に達した場合に適用。

### 事実・観察・仮説・結論（Facts / Observations / Hypotheses / Conclusion）

事実（Facts）:
- Android 17 で app memory limits が追加され、targetSdkVersion gate は確認されない。

観察（Observations）:
- 画像 / 動画処理は memory usage が大きくなりやすい。

仮説（Hypotheses）:
- 大量画像一覧、動画転送、サムネイルキャッシュ、長時間接続で memory outlier がある場合、対象 device で process exit が起きる可能性。

結論（Conclusion）:
- OS update impact として memory baseline と exit reason 収集を推奨。

### アプリ影響（App Impact）

想定される影響:
- memory limit 到達時の process kill。

ユーザー影響:
- 転送中断、アプリ再起動、画像一覧のリロード。

開発者影響:
- memory baseline、cache limit、bitmap lifecycle、transfer pipeline の見直し。

推奨対応候補:
- `ApplicationExitInfo.getDescription()` で `MemoryLimiter:AnonSwap` を確認する。
- `am memory-limiter status` と manual limit で再現性を確認する。
- 画像 / 動画転送の長時間テストを行う。

### Confidence

Confidence:
- High

Confidence の根拠:
- AOSP MemoryLimiter 本体と shell command を確認済み。

不足している根拠:
- 対象 device での vendor config。
- 対象アプリ memory profile。

---

## BC-009: Background audio hardening

### 基本情報（Basic Information）

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/17/behavior-changes-all
- URL: https://developer.android.com/about/versions/17/behavior-changes-17
- Section: Background audio hardening

Original statement:
> Android 17 では background audio interaction が制限され、audio playback、audio focus request、volume change API などが、アプリの lifecycle / foreground service / capability 条件を満たさない場合に失敗または mute される、という趣旨の公式説明。

調査対象 Android バージョン:
- From: android-16.0.0_r4
- To: android-17.0.0_r1

### 対象アプリとの関係（Relevance to Target App）

関連するアプリ機能:
- カメラ接続完了音、転送完了音、エラー音。
- カメラのシャッター音や操作音をアプリ側で再生する機能。
- 転送完了、タイマー、リモート撮影通知に音声 / アラームを使う機能。
- バックグラウンドで音声再生、audio focus request、volume / ringer mode 変更を行う処理。

関連する API / permission / component:
- `AudioManager.requestAudioFocus()`
- `AudioManager.setStreamVolume()` / `adjustStreamVolume()` / `adjustVolume()`
- `AudioAttributes.USAGE_ALARM`
- foreground service
- exact alarm permission
- AppOps `OP_PLAY_AUDIO` / `OP_TAKE_AUDIO_FOCUS` / `OP_CONTROL_AUDIO`

アプリが該当する可能性:
- 低いから Conditional。カメラ連携・画像転送が主用途で、バックグラウンド音声再生が主要機能でなければ影響は限定的。ただし、バックグラウンドで転送完了音、アラーム、音声通知、音量変更を行う場合は該当し得る。

確認したアプリ実装:
- File / module: 未確認。
- Symbol / entry point: 未確認。
- Manifest / permission: foreground service / exact alarm permission の利用有無は未確認。
- Runtime condition: バックグラウンド状態で音声 API を呼ぶ場合。

### 適用条件分類（Applicability Classification）

主分類（Primary classification）:
- OS_UPDATE_ALL_APPS / TARGET_SDK_37_CONDITIONAL

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | Yes / Conditional | all apps 側の共通制限は targetSdkVersion 37 を必須にしない。 |
| targetSdkVersion 37 以上が必要か | 追加制限では Yes | target 側レポートでは CINNAMON_BUN 以上で strict level に進む条件を確認。 |
| 追加の実行時条件があるか | Yes | background audio interaction、AppOps、foreground service / foreground audio control capability、exact alarm / `USAGE_ALARM` 条件。 |
| Compat Change ID が関係するか | No / 未確認 | `frameworks-base` では compat ChangeId ではなく audio flags / AppOps / hardening override が主要条件。 |

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17。
- targetSdkVersion: 共通制限は条件なし。target 37 追加制限は targetSdkVersion 37 以上。
- Permission/API/component condition: audio playback、audio focus request、volume / ringer mode API、foreground service、exact alarm permission、`USAGE_ALARM`。
- App state/process condition: アプリが background にいて、audio AppOps / process capability により操作が許可されない状態。

Compat framework:
- Change ID: 確認されず。
- Change name: N/A
- Default state: audio flags / AppOps / AudioPolicy hardening override に依存。
- Toggleable for testing: privileged `AudioManager.setHardeningOverride()` / shell hardening override path。

### AOSP 調査（AOSP Investigation）

関連ファイル:
- `services/core/java/com/android/server/audio/HardeningEnforcer.java`
- `services/core/java/com/android/server/audio/AudioService.java`
- `services/core/java/com/android/server/am/psc/OomAdjusterImpl.java`
- `services/core/java/com/android/server/am/psc/CapabilityController.java`
- `core/java/android/app/ActivityManager.java`
- `core/java/android/app/AppOpsManager.java`

確認したソース文脈（Source Context Reviewed）:

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `HardeningEnforcer.blockVolumeMethod()` | AppOps による audio hardening の土台あり | AppOps、targetSdk、exact alarm、hardening override により volume API の block level を決める | volume API が silent no-op になる条件の根拠。 |
| `AudioService.requestAudioFocus()` | hardening block 時に focus request failure | Android 17 でも block 時に `AUDIOFOCUS_REQUEST_FAILED` を返す | audio focus request の開発者可視結果。 |
| `AudioService.playbackHardeningEvent()` | playback hardening event を受ける | reason / usage 付きで background playback mute をログ・metrics に記録 | playback mute の framework 側証跡。 |
| `OomAdjusterImpl` / `CapabilityController` | 従来の process capability 管理 | foreground audio control capability を FGS / process state と結びつける | foreground service / WIU 相当条件との接続点。 |

差分解釈（Diff Interpretation）:
- Changed condition / gate: AppOps、process capability、targetSdkVersion 37、exact alarm exception、hardening flags により block level が変わる。
- Changed default / enforcement: background の audio focus は failure、volume API は no-op、playback は mute され得る。
- No behavior change found: カメラ機能そのものの Camera API 変更ではない。

適用ゲート根拠（Applicability Gate Evidence）:
- targetSdkVersion gate: 共通制限では必須ではない。target 37 追加制限では CINNAMON_BUN 以上が strict level の条件。
- CompatChanges.isChangeEnabled / ChangeId: 確認されず。
- Permission/AppOps gate: `OP_PLAY_AUDIO` / `OP_TAKE_AUDIO_FOCUS` / `OP_CONTROL_AUDIO` / `OP_CONTROL_AUDIO_PARTIAL`。
- Gate conclusion: Android 17 上で background audio interaction を行い、visible activity / 適切な foreground service / foreground audio control capability / alarm exception を満たさない場合に影響する。

### 事実・観察・仮説・結論（Facts / Observations / Hypotheses / Conclusion）

事実（Facts）:
- Android 17 の `HardeningEnforcer` / `AudioService` は background audio interaction に対する focus / volume / playback hardening path を持つ。
- targetSdkVersion 37 以上では strict level の追加条件がある。

観察（Observations）:
- カメラ連携アプリでは、音声再生が主機能でない限り該当可能性は低い。
- ただし、転送完了音、アラーム、バックグラウンド通知音、音量変更を独自実装している場合は確認対象になる。

仮説（Hypotheses）:
- 対象アプリがバックグラウンド転送完了時に音声を鳴らす、またはリモート撮影タイマーで `USAGE_ALARM` を使う場合、Android 17 / targetSdkVersion 37 で failure mode が変わる可能性がある。

結論（Conclusion）:
- カメラ連携アプリでは「影響なしから軽微」と仮置きする。ただし background audio API usage がある場合は、Android 17 / targetSdkVersion 37 の個別確認が必要。

### アプリ影響（App Impact）

想定される影響:
- バックグラウンド状態で転送完了音やアラーム音が鳴らない。
- `requestAudioFocus()` が `AUDIOFOCUS_REQUEST_FAILED` を返す。
- volume / ringer mode API が silent no-op になる。

ユーザー影響:
- 転送完了やエラーを音で認識できない。
- タイマー撮影やリモート操作の音声フィードバックが期待通り動かない。

開発者影響:
- background audio interaction の棚卸し。
- user-initiated flow、foreground service、exact alarm + `USAGE_ALARM` の条件確認。
- audio focus failure の戻り値処理。

推奨対応候補:
- 音声再生 / audio focus / volume 変更 API の利用箇所を検索する。
- バックグラウンド転送中・画面消灯中・通知経由復帰時に音声フィードバックをテストする。
- アラーム用途なら exact alarm permission と `AudioAttributes.USAGE_ALARM` を確認する。

### Confidence

Confidence:
- Medium

Confidence の根拠:
- AOSP Java framework 側の focus / volume / capability path は確認済み。
- 実際の playback mute 最終判定は native AudioPolicy / audioserver 側にもまたがる。

不足している根拠:
- 対象アプリの background audio API usage。
- foreground service / exact alarm / audio usage 設定。

---

## BC-010: Static final fields / Safer Native DCL-C

### 基本情報（Basic Information）

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/17/behavior-changes-17
- Section: Static final fields are now unmodifiable
- Section: Safer Native DCL-C

Original statement:
> Android 17 以上で targetSdkVersion 37 以上のアプリは static final field を reflection / JNI で変更できない。また、targetSdkVersion 37 以上では `System.load()` で読み込む native file が read-only である必要があり、条件を満たさない場合は `UnsatisfiedLinkError` になる、という趣旨の公式説明。

調査対象 Android バージョン:
- From: android-16.0.0_r4
- To: android-17.0.0_r1

### 対象アプリとの関係（Relevance to Target App）

関連するアプリ機能:
- 古いアプリ / SDK の runtime patching。
- 画像・動画処理 SDK、codec、AI / ML delegate、ネットワーク処理 SDK。
- 実行時に native library を download / generate / extract / update して `System.load()` する機能。
- JNI で static final field を変更する初期化処理。

関連する API / permission / component:
- Java reflection `Field.set*()`
- JNI `SetStatic*Field()`
- `System.load(path)`
- `Runtime.load0()`
- `VMRuntime.THROW_ERROR_FOR_WRITABLE_DCL`

アプリが該当する可能性:
- Conditional。通常の Camera API / Camera2 API 利用だけでは該当しない。古い SDK、native plugin、画像・動画処理 module、ネットワーク処理 module が reflection / JNI write または writable native file loading を行う場合に該当する。

確認したアプリ実装:
- File / module: 未確認。
- Symbol / entry point: `Field.set*()`、`SetStatic*Field()`、`System.load()` 利用有無は未確認。
- Manifest / permission: 該当なし。
- Runtime condition: targetSdkVersion 37 以上で該当コードパスが実行される場合。

### 適用条件分類（Applicability Classification）

主分類（Primary classification）:
- TARGET_SDK_37_CONDITIONAL

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 原則 No | static final は ART targetSdkVersion gate、Native DCL-C は compat ChangeId `463348571`。 |
| targetSdkVersion 37 以上が必要か | Yes | static final は ART / runtime gate、Native DCL-C は `@EnabledSince(CINNAMON_BUN)`。 |
| 追加の実行時条件があるか | Yes | static final field write、または writable native file の `System.load()`。 |
| Compat Change ID が関係するか | 一部 Yes | Static final は compat ChangeId 未確認。Native DCL-C は `THROW_ERROR_FOR_WRITABLE_DCL = 463348571`。 |

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 以上。
- targetSdkVersion: 37 以上。
- API/component condition: reflection / JNI による `static final` field write、または `System.load(path)` による dynamic native loading。
- File condition: `System.load()` で読み込む native file が read-only でない場合。
- App state/process condition: アプリ起動時、SDK 初期化時、画像・動画処理 module / native plugin 初期化時。

Compat framework:
- Static final fields:
  - Change ID: 確認されず。
  - Default state: ART runtime targetSdkVersion / SDK version gate。
- Safer Native DCL-C:
  - Change ID: `463348571`
  - Change name: `THROW_ERROR_FOR_WRITABLE_DCL`
  - Default state: `@EnabledSince(targetSdkVersion = CINNAMON_BUN)`
  - Toggleable for testing: compat change / runtime flags により切り替え可能。

### AOSP 調査（AOSP Investigation）

関連ファイル:
- `platform/art/runtime/art_field-inl.h`
- `platform/art/runtime/native/java_lang_reflect_Field.cc`
- `platform/art/runtime/jni/jni_internal.cc`
- `platform/art/test/2396-unmodifiable-final-fields`
- `platform/libcore/ojluni/src/main/java/java/lang/Runtime.java`
- `platform/libcore/libart/src/main/java/dalvik/system/VMRuntime.java`

確認したソース文脈（Source Context Reviewed）:

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `ArtField::IsUnmodifiable()` | 汎用 static final target 37 gate なし | targetSdkVersion / SDK version を見て static final field を unmodifiable と判断 | reflection / JNI の static final write rejection の中心。 |
| `java_lang_reflect_Field.cc` | static final の汎用 write rejection なし | `IsUnmodifiable()` の場合に `IllegalAccessException` | 公式文書の reflection failure path。 |
| `jni_internal.cc` / `SetStatic*Field()` | static final の汎用変更検出なし | `EnsureModifiable()` で static final write attempt を検出 | 公式文書の JNI crash / fatal path。 |
| `Runtime.load0()` | writable native file は warning 中心 | writable file を検出し、条件を満たすと `UnsatisfiedLinkError` | `System.load(path)` の app-facing failure path。 |
| `VMRuntime.THROW_ERROR_FOR_WRITABLE_DCL` | ChangeId なし | `463348571` / `@EnabledSince(CINNAMON_BUN)` | Native DCL-C の targetSdkVersion 37 gate。 |

差分解釈（Diff Interpretation）:
- Added behavior: reflection / JNI の static final field write rejection。
- Added enforcement: `System.load(path)` で writable native file を拒否する path。
- Changed condition / gate: Android 17 runtime + targetSdkVersion 37 以上、または `THROW_ERROR_FOR_WRITABLE_DCL` enabled。
- No behavior change found: 通常の Camera API / Camera2 API 呼び出し自体には直接関係しない。

適用ゲート根拠（Applicability Gate Evidence）:
- targetSdkVersion gate: static final は ART runtime targetSdkVersion / SDK version gate。Native DCL-C は `@EnabledSince(CINNAMON_BUN)`。
- CompatChanges.isChangeEnabled / ChangeId: Native DCL-C は `463348571`。Static final は ChangeId 未確認。
- Build.VERSION / SDK_INT gate: Android 17 runtime が前提。
- Gate conclusion: Android 17 / targetSdkVersion 37 以上で、static final field write または writable native file `System.load()` を行う場合に適用。

### 事実・観察・仮説・結論（Facts / Observations / Hypotheses / Conclusion）

事実（Facts）:
- Static final fields は ART / libcore 側で reflection / JNI write が拒否される。
- Safer Native DCL-C は libcore `Runtime.load0()` と `VMRuntime.THROW_ERROR_FOR_WRITABLE_DCL` で確認できる。

観察（Observations）:
- カメラ連携アプリでも、画像・動画処理、codec、AI / ML delegate、ネットワーク処理 SDK は native library を含む可能性がある。
- 古い SDK では reflection / JNI による内部値変更や、実行時展開した `.so` の load path を持つ可能性がある。

仮説（Hypotheses）:
- 対象アプリが native plugin を実行時に展開・更新して `System.load()` している場合、targetSdkVersion 37 更新後に `UnsatisfiedLinkError` が起きる可能性がある。
- 古い SDK が `static final` field を reflection / JNI で変更している場合、起動時または SDK 初期化時に失敗する可能性がある。

結論（Conclusion）:
- カメラ連携アプリでは要確認。通常のカメラ撮影 API だけではなく、同梱 SDK / native module / plugin 更新処理を含めて棚卸しする必要がある。

### アプリ影響（App Impact）

想定される影響:
- アプリ起動時または SDK 初期化時の crash / initialization failure。
- 画像・動画処理、codec、AI / ML delegate、ネットワーク処理 module の読み込み失敗。
- `System.load()` 時の `UnsatisfiedLinkError`。
- reflection では `IllegalAccessException`、JNI では fatal crash path。

ユーザー影響:
- アプリ起動失敗。
- ライブビュー、画像転送、動画処理、サムネイル生成、クラウド連携などの一部機能が使えない。

開発者影響:
- `Field.set*()` / `setAccessible(true)` / JNI `SetStatic*Field()` の棚卸し。
- `System.load()` / native library 展開・更新処理の棚卸し。
- `System.load()` 前に native file を read-only にし、その後に書き換えない実装への変更。

推奨対応候補:
- アプリコードと SDK で `System.load(`、`Field.set`、`SetStatic`、`.so` 展開処理を検索する。
- dynamic native loading を避け、APK / App Bundle 配布時点の native library に寄せる。
- どうしても動的読み込みが必要な場合は、write 完了後に read-only 化してから `System.load()` する。
- `UnsatisfiedLinkError` と reflection failure を起動 / 機能初期化の failure として検出できるようにする。

### Confidence

Confidence:
- High

Confidence の根拠:
- Static final fields は ART / libcore evidence、Safer Native DCL-C は libcore `Runtime.load0()` / `VMRuntime` evidence を確認済み。

不足している根拠:
- 対象アプリおよび同梱 SDK の reflection / JNI / native loading 実装。
- 実際の targetSdkVersion 37 ビルドでの起動・画像 / 動画処理・転送テスト。

---

# 顧客向け説明（Customer-facing Explanation）

対象アプリ種別では、Android 17 の影響は主に「カメラとの接続」と「ネットワーク通信」に集中します。

OS アップデートだけで確認すべき点は、Bluetooth の bond loss 復旧挙動と、一部端末で導入される app memory limits です。targetSdkVersion を変更しなくても、Bluetooth 再ペアリングのタイミングや、大きな画像 / 動画処理時の memory limit 影響が出る可能性があります。

targetSdkVersion 37 に更新する場合は、ローカルネットワーク権限が最重要です。カメラ探索、Wi-Fi 接続、ローカル IP や `.local` への通信、画像 / 動画転送、リモート操作が direct local network access に該当する場合、system picker でユーザー許可を取得する経路を使えるか確認してください。system picker を使わない direct / persistent access では、`ACCESS_LOCAL_NETWORK` の manifest 宣言、runtime permission request、拒否・取り消し時の案内が必要になります。

古いアプリや組み込み SDK では、`static final` field を reflection / JNI で書き換える実装、または画像・動画処理、ネットワーク処理、codec、AI / ML delegate などの native library を実行時に展開・更新して `System.load()` する実装も確認対象です。Native DCL-C では、`System.load()` 前に読み込む native file を read-only にしておく必要があります。

Bluetooth Classic / RFCOMM を使っている場合は、切断時の `InputStream.read()` が `-1` を返す挙動に対応してください。`IOException` だけで read loop を終了している実装は、Android 17 / targetSdkVersion 37 で切断処理が期待通り動かない可能性があります。

HTTPS 通信については、certificate transparency の default enabled と ECH の導入により、証明書チェーン、staging endpoint、private PKI、Network Security Config、企業ネットワークでの接続を確認してください。

---

# One Page Summary 用メモ（One Page Summary Notes）

## 対象アプリで重要な変更

- 最重要: Android 17 / targetSdkVersion 37 の local network permission。
- 高優先: Bluetooth bond loss autonomous re-pairing。
- 高優先: RFCOMM `BluetoothSocket.read()` EOF `-1`。
- 中優先: CT default enabled / ECH。
- 中優先: Activity Security と large screen。
- 要確認: 古い reflection / JNI の `static final` 書き換え、画像・動画処理 / ネットワーク処理 native library の dynamic loading。
- OS update impact: app memory limits。

## 対応要否

- 必須対応候補: local network access 棚卸し、system picker または `ACCESS_LOCAL_NETWORK` runtime permission UX、Bluetooth read loop / pairing recovery 確認。
- 推奨対応: HTTPS endpoint / certificate / ECH 方針、large screen UI、memory baseline。
- 追加確認: `System.load()` 前の native file read-only 化、古い reflection / JNI 実装の有無。
- 不要候補: Contacts / SMS / background audio は該当 API usage がなければ優先度低。

## 顧客に伝えるべき要点

- targetSdkVersion 37 更新時は、カメラとのローカル接続に runtime permission が関係する可能性がある。
- system picker で許可を得ない direct local network access は、manifest とコードの runtime permission 対応が必要。
- Native DCL-C は、`System.load()` 前に対象 native file を read-only にしておく必要がある。
- Android 17 OS 更新だけでも、Bluetooth 再ペアリングと memory limits は確認対象。
- 実装未確認のため、最終判断には manifest / API usage / 実機テストが必要。

## テストで確認すべき要点

- Android 17 / targetSdkVersion 37 / local network permission denied / granted / revoked。
- Bluetooth bond loss、repairing 成功、repairing 失敗、`ACTION_KEY_MISSING`。
- RFCOMM read loop の `-1` handling。
- HTTPS production / staging / local endpoint。
- tablet / foldable / multi-window。
- 大量画像 / 動画転送時の memory。

---

# 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Critical / High / Medium / Low

判断（Decision）:
- Explain / Monitor / Ignore / Further investigation required

判断者メモ:
- 対象アプリの名称・パッケージ名は本レポートに記載しない方針。
- 最終優先度は、対象アプリの manifest / API usage / 実機テスト結果を確認した後に判断する。

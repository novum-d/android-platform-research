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

対象アプリは、カメラとの Bluetooth / Wi-Fi 接続、ローカルネットワーク上の機器探索・接続、画像 / 動画転送、リモート操作を行う可能性が高い。そのため Android 17 では、特に `ACCESS_LOCAL_NETWORK`、Bluetooth bond loss recovery、RFCOMM `BluetoothSocket.read()`、TLS 周辺の変更を優先確認すべきである。加えて、古いアプリ / SDK の reflection と、画像・動画処理またはネットワーク処理 native library の dynamic loading は、それぞれ Static final fields と Safer Native DCL-C として分けて確認する。

OS アップデートだけで影響しうる項目は、Bluetooth bond loss 後の autonomous re-pairing と app memory limits である。targetSdkVersion 37 更新時に影響しうる項目は、ローカルネットワーク権限、RFCOMM read EOF、certificate transparency、ECH、Activity Security、大画面制約無視、Safer Native DCL-C、Static final fields である。

現時点では対象アプリの manifest / API usage を直接確認していないため、アプリ固有影響は「要確認」を含む。特にカメラとの直接 Wi-Fi 接続、mDNS / NSD / `.local` 解決、ローカル IP への socket / HTTP 接続がある場合、Android 17 / targetSdkVersion 37 で runtime permission UX と接続失敗時の fallback を設計する必要がある。

カメラ連携アプリでは、system-mediated picker よりも `ACCESS_LOCAL_NETWORK` runtime permission を明示 request する設計が第一候補になりやすい。理由は、カメラ探索、カメラ側 Wi-Fi AP 接続、IP 変更後の再探索、ライブビュー、リモート撮影、画像 / 動画転送、再接続などが、単発の device / service selection ではなく direct / persistent local network access に該当しやすいためである。system-mediated picker は、ユーザーが選択した単一 device / service への接続だけで UX が完結する限定機能に使えるかを個別検討する。

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
| BC-010 | Safer Native DCL-C | 画像・動画処理 native library、ネットワーク処理 native library、native dynamic loading | TARGET_SDK_37_CONDITIONAL | 要確認。native plugin / 動的 `.so` 展開構成では該当可能性あり | `System.load()` 前の read-only 化、native library 展開処理を棚卸し | High |
| BC-011 | Static final fields are now unmodifiable | 古いアプリ / SDK の reflection、JNI、runtime patching | TARGET_SDK_37_CONDITIONAL | 要確認。古い SDK が `static final` を書き換える場合は該当可能性あり | reflection / JNI による `static final` 書き換えを棚卸し | High |

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
| Local network permission required for apps targeting Android 17 | targetSdkVersion 37 以上 | direct local network access、LAN device discovery / connection、system picker 利用有無、`ACCESS_LOCAL_NETWORK` grant state | カメラ探索、接続、画像転送、リモート制御が permission denied 時に失敗する可能性。 | local network API / socket / HTTP / mDNS / NSD / `.local` 利用を棚卸しする。カメラ連携では direct / persistent access が多いため、`ACCESS_LOCAL_NETWORK` runtime permission を第一候補にし、picker は単一 device / service 選択で完結する機能に限定できるか確認する。 |
| Safer Native DCL-C | targetSdkVersion 37 以上 | `System.load()` で writable native file を読み込む場合 | 画像・動画処理やネットワーク処理の native module 動的差し替えで `UnsatisfiedLinkError` が起きる可能性。 | native library の download / generate / extract / update / load 処理を棚卸しする。`System.load()` 前に対象 `.so` を read-only にし、その後に書き換えない。 |
| Static final fields are now unmodifiable | targetSdkVersion 37 以上 | reflection / JNI による `static final` field write | 古いアプリ / SDK の runtime patching や初期化処理で例外・crash が起きる可能性。 | 古い reflection 実装、JNI field write、`Field.set*()` / `SetStatic*Field()` を棚卸しする。 |
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

## 要確認の項目（Needs More Evidence）

| Behavior Change | 不足している根拠 | 次に確認すること | Blocker |
| --- | --- | --- | --- |
| Local network permission | manifest、local network API usage、system picker 利用有無、direct socket / HTTP / mDNS / NSD 利用有無 | APK / source で local network access 箇所を検索し、Android 17 / targetSdkVersion 37 で permission denied / granted をテストする。 | 対象アプリ実装未確認 |
| RFCOMM read EOF | Bluetooth Classic / RFCOMM / SPP 利用有無、read loop 実装 | `BluetoothSocket`、`createRfcommSocketToServiceRecord`、`InputStream.read()` 周辺を確認する。 | 対象アプリ実装未確認 |
| CT / ECH | 通信先一覧、Network Security Config、certificate pinning、利用 networking library | production / staging / device-local endpoint の証明書と ECH support を確認する。 | 通信先・設定未確認 |
| Activity Security | PendingIntent / IntentSender 経由の Activity 起動箇所、古いアプリから新しいアプリへの推奨 PendingIntent flow、通知 `contentIntent` / action の種類 | 通知、popup、ペアリング復旧、接続復旧、外部アプリ連携の起動経路を確認する。特にユーザータップ直後に Activity PendingIntent を直接実行するか、broadcast / service / 非同期 callback を挟むか、background 自動実行かを分ける。 | 対象アプリ実装未確認 |
| Large screen | manifest の orientation / resizability / aspect ratio 設定、UI の adaptive 対応 | tablet / foldable / multi-window で主要画面を確認する。 | 対象アプリ実装未確認 |
| Safer Native DCL-C | native library の動的展開・更新・読み込み処理、画像・動画処理 / ネットワーク処理 SDK の実装 | `System.load()`、download / generate / extract した `.so` の file mode を確認する。 | 対象アプリ実装・SDK 実装未確認 |
| Static final fields are now unmodifiable | 古い reflection / JNI 実装、runtime patching、SDK 初期化処理 | `static final` field write、`Field.set*()`、JNI `SetStatic*Field()` を確認する。 | 対象アプリ実装・SDK 実装未確認 |

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

詳細な traceability、AOSP evidence、適用条件分類、アプリ影響は Behavior Change ごとの詳細ファイルに分割する。

| ID | Behavior Change | 詳細 |
| --- | --- | --- |
| BC-001 | Local network permission required for apps targeting Android 17 | [details/bc-001-local-network-permission.md](details/bc-001-local-network-permission.md) |
| BC-002 | Autonomous re-pairing for Bluetooth bond losses | [details/bc-002-bluetooth-bond-loss-repairing.md](details/bc-002-bluetooth-bond-loss-repairing.md) |
| BC-003 | Consistent BluetoothSocket read() behavior for RFCOMM | [details/bc-003-bluetoothsocket-rfcomm-read-eof.md](details/bc-003-bluetoothsocket-rfcomm-read-eof.md) |
| BC-004 | Enable CT by default | [details/bc-004-certificate-transparency-default-enabled.md](details/bc-004-certificate-transparency-default-enabled.md) |
| BC-005 | ECH enabled | [details/bc-005-ech-enabled.md](details/bc-005-ech-enabled.md) |
| BC-006 | Activity Security | [details/bc-006-activity-security.md](details/bc-006-activity-security.md) |
| BC-007 | Large screen orientation / resizability / aspect ratio restrictions ignored | [details/bc-007-large-screen-orientation-resizability-aspect-ratio.md](details/bc-007-large-screen-orientation-resizability-aspect-ratio.md) |
| BC-008 | App memory limits | [details/bc-008-app-memory-limits.md](details/bc-008-app-memory-limits.md) |
| BC-009 | Background audio hardening | [details/bc-009-background-audio-hardening.md](details/bc-009-background-audio-hardening.md) |
| BC-010 | Safer Native DCL-C | [details/bc-010-safer-native-dcl-c.md](details/bc-010-safer-native-dcl-c.md) |
| BC-011 | Static final fields are now unmodifiable | [details/bc-011-static-final-fields-unmodifiable.md](details/bc-011-static-final-fields-unmodifiable.md) |

---

# 顧客向け説明（Customer-facing Explanation）

対象アプリ種別では、Android 17 の影響は主に「カメラとの接続」と「ネットワーク通信」に集中します。

OS アップデートだけで確認すべき点は、Bluetooth の bond loss 復旧挙動と、一部端末で導入される app memory limits です。targetSdkVersion を変更しなくても、Bluetooth 再ペアリングのタイミングや、大きな画像 / 動画処理時の memory limit 影響が出る可能性があります。

targetSdkVersion 37 に更新する場合は、ローカルネットワーク権限が最重要です。カメラ探索、Wi-Fi 接続、ローカル IP や `.local` への通信、画像 / 動画転送、リモート操作が direct local network access に該当する場合、system picker でユーザー許可を取得する経路を使えるか確認してください。system picker を使わない direct / persistent access では、`ACCESS_LOCAL_NETWORK` の manifest 宣言、runtime permission request、拒否・取り消し時の案内が必要になります。

カメラ連携アプリでは、system picker だけで完結するより、`ACCESS_LOCAL_NETWORK` を runtime permission として明示 request する設計が適合しやすい可能性があります。カメラ探索、カメラ側 Wi-Fi AP への接続、ライブビュー、リモート撮影、画像 / 動画転送、再接続は、単一 device picker で選んだ endpoint だけに閉じない direct / persistent access になりやすいためです。system picker は、ユーザーが選択した 1 台の camera service だけに接続すれば十分な限定機能として成立するかを個別に確認してください。

古いアプリや組み込み SDK では、2種類の互換性リスクを分けて確認してください。1つ目は、`static final` field を reflection / JNI で書き換える実装です。2つ目は、画像・動画処理、ネットワーク処理、codec、AI / ML delegate などの native library を実行時に展開・更新して `System.load()` する実装です。Native DCL-C では、`System.load()` 前に読み込む native file を read-only にしておく必要があります。

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
- 要確認: Safer Native DCL-C。画像・動画処理 / ネットワーク処理 native library の dynamic loading。
- 要確認: Static final fields。古い reflection / JNI の `static final` 書き換え。
- OS update impact: app memory limits。

## 対応要否

- 必須対応候補: local network access 棚卸し、`ACCESS_LOCAL_NETWORK` runtime permission UX、system picker で完結できる限定機能の切り分け、Bluetooth read loop / pairing recovery 確認。
- 推奨対応: HTTPS endpoint / certificate / ECH 方針、large screen UI、memory baseline。
- 追加確認: `System.load()` 前の native file read-only 化。
- 追加確認: 古い reflection / JNI 実装の有無。
- 不要候補: Contacts / SMS / background audio は該当 API usage がなければ優先度低。

## 顧客に伝えるべき要点

- targetSdkVersion 37 更新時は、カメラとのローカル接続に runtime permission が関係する可能性がある。
- カメラ探索、ライブビュー、リモート操作、画像 / 動画転送、再接続を行う場合、system picker より `ACCESS_LOCAL_NETWORK` runtime permission が第一候補になりやすい。
- system picker は、ユーザーが選択した単一 device / service だけで UX が完結する場合に限定して検討する。
- system picker で許可を得ない direct / persistent local network access は、manifest とコードの runtime permission 対応が必要。
- Native DCL-C は、`System.load()` 前に対象 native file を read-only にしておく必要がある。
- Static final fields は、targetSdkVersion 37 以上で reflection / JNI による書き換えが拒否される可能性がある。
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

# 決済サービスの顧客別アプリ・機能別アプリ分割に関するリスク評価

## 基本情報

調査日:

- 2026-10-02

対象構成:

- 決済を利用する顧客ごとにサービスアプリを分ける。
- サービスアプリから、カメラ機能アプリ、NFC 機能アプリなどの別アプリを呼び出す。
- アプリ間で処理状態や結果を受け渡し、その状態に応じてサービスアプリの画面を切り替える。

Android バージョンスコープ:

- Android 16: `android-15.0.0_r36` から `android-16.0.0_r4`
- Android 17: `android-16.0.0_r4` から `android-17.0.0_r1`
- targetSdkVersion 36 / 37 の変更を、OS アップデートだけで適用される変更と分けて評価する。

調査範囲:

- 本リポジトリの Android 16 / 17 Behavior Change 調査を、提案構成へ横断適用した。
- 2026-10-02 に online 構成検証を実行し、Android 16 / 17 の version scope には stale 判定がないことを確認した。検証全体は、今回の対象外である AGP stable / preview 登録値の stale 判定により failure となった。
- 対象アプリのソースコード、Manifest、画面仕様、決済シーケンス、署名・配布方式、実機ログは未確認である。
- NFC 固有の Android 16 / 17 Behavior Change は、既存の調査済み一覧に含まれていない。NFC の最終判断には追加調査が必要である。

---

# エグゼクティブサマリー

## 結論

現時点では、顧客別サービスアプリからカメラ・NFC などの機能別アプリへ処理を分割する構成は、**採用をいったん止め、単一アプリ内のモジュール分割を第一候補として再検討する**ことを推奨する。

理由は、コードを分離できる利点よりも、次の境界コストが決済フロー全体へ継続的に発生するためである。

- 1 回の決済状態が複数プロセス・複数 UID・複数タスクへ分散し、状態の正本、タイムアウト、再試行、二重実行、プロセス終了後の復旧をプロトコルとして実装する必要がある。
- 各サービスアプリは、機能アプリから返る成功・失敗・取消・権限拒否・タイムアウト・バージョン不一致・応答なしを画面状態へ変換する必要がある。
- 顧客別アプリ数を `N`、機能別アプリ数を `F` とすると、連携契約は最大 `N × F` 本になる。OS、targetSdkVersion、機能アプリ版、権限状態、foreground / background、process death を加えると、試験組合せはさらに乗算で増える。
- Android 16 では、アプリをまたぐ ordered broadcast の priority 順序を保証できず、nested Intent の転送も強化される。Android 17 では、PendingIntent / IntentSender 経由の background Activity 起動条件が厳格化される。分割構成が依存しやすい連携方式そのものが、直近 OS の変更対象になっている。
- UI、権限、監視、障害解析、段階配信、後方互換性、セキュリティ境界をアプリ数分だけ維持する必要がある。

機能別アプリが独立したセキュリティ境界、別主体による配布、端末管理上の隔離、独立インストールという必須要件を持たない限り、アプリ分割の費用対効果は低いと判断する。

## 推奨構成

第一候補:

- 顧客別サービスアプリの中に、カメラ・NFC をライブラリまたは feature module として組み込む。
- 決済状態と画面遷移は 1 つのアプリが所有する。
- 顧客差分は設定、依存性注入、branding、feature flag、product flavor などで吸収する。

分割が避けられない場合:

- 1 つのオーケストレーターアプリだけが決済状態と画面遷移の正本を持つ。
- 機能アプリは UI とドメイン状態を持ち続けず、明示的でバージョン化された request / result 契約に限定する。
- ordered broadcast や暗黙 Intent を連携の正本にしない。

---

# アーキテクチャ評価

## 状態管理の複雑化

アプリ内の関数・画面遷移は同一プロセスの状態として扱えるが、別アプリへの分割後は分散トランザクションになる。少なくとも次の状態を全連携で定義する必要がある。

| 状態 | サービスアプリ側で必要な扱い | 分割時に増える失敗例 |
| --- | --- | --- |
| 未開始 | 機能アプリを起動できるか確認 | 未インストール、無効化、署名・版不一致 |
| 実行中 | 多重起動を防止し、進捗を復元 | 呼び出し元だけ process death、機能側だけ process death |
| ユーザー操作待ち | foreground 状態と戻り先を維持 | Home、通知、別タスク、画面回転、multi-window |
| 成功 | 同一取引へ一度だけ反映 | result の再配送、古い result、二重決済 |
| 業務失敗 | 再試行可否と案内を決定 | カメラ読取失敗、NFC 通信失敗、端末状態変化 |
| 権限拒否・取消 | 各アプリの権限状態に応じて案内 | 呼び出し元では許可済みでも機能アプリでは未許可 |
| タイムアウト・応答なし | 取消、照会、再開を決定 | OS による kill、機能アプリ更新中、Activity 起動拒否 |
| 取消 | 外部処理と UI を整合 | back、gesture、強制終了、別アプリからの割込み |

特に決済では「結果を受け取れなかった」と「処理が実行されなかった」は同義ではない。再試行で二重実行を起こさないため、transaction ID、idempotency key、最終状態照会、期限、重複 result の破棄規則が必要になる。

## 画面遷移と UX の複雑化

サービスアプリは、機能アプリの内部状態ではなく、公開された結果だけで画面を決める必要がある。そのため、各顧客アプリに同じ状態変換ロジックと例外画面が複製されやすい。

また、別 package の Activity へ移る構成では、次を統一しても完全には同一アプリ内遷移と同じにならない。

- task / back stack、Recents、deep link、通知からの復帰先
- predictive back、画面回転、fold / unfold、multi-window
- status bar、navigation bar、edge-to-edge、テーマ、アクセシビリティ
- 呼び出し元が消えた後の戻り先と、古い result の扱い
- 機能アプリが更新・無効化・アンインストールされた場合の fallback

Android 16 の edge-to-edge / predictive back、Android 16・17 の large screen 変更は、分割した各 UI アプリで個別に対応・検証する必要がある。UI 品質の差が、顧客別アプリと機能別アプリの境界でユーザーに見えやすくなる。

## 開発・運用コスト

| 領域 | 単一アプリ内モジュール | 顧客別アプリ + 機能別アプリ |
| --- | --- | --- |
| API 契約 | compile-time に整合を確認しやすい | package 間 contract、schema、version negotiation が必要 |
| リリース | 原則 1 組の整合版 | 独立配信による version skew と rollback 順序が発生 |
| テスト | モジュール・アプリのテスト | `N × F` の結合、OS / target / 権限 / process state を追加 |
| 障害解析 | 同一ログ・trace で追跡しやすい | package をまたぐ correlation ID、時刻、ログ回収が必要 |
| 権限 | 1 アプリの grant 状態 | package ごとの grant / denied / revoked と説明 UX |
| セキュリティ | 主にアプリ内部境界 | exported component、Intent、URI grant、PendingIntent、caller 検証が必要 |
| データ整合性 | 共有 state holder / DB を利用可能 | 所有者、同期、cache、古い状態、原子的更新を設計 |
| QA・サポート | 1 アプリ版を特定 | 呼出元版、機能側版、OS、権限、起動経路を同時特定 |

テスト規模の概算は、単純な画面数ではなく次の変数で見積もる必要がある。

```text
integration edges = 顧客別サービスアプリ数 N × 機能別アプリ数 F

potential compatibility combinations
  = integration edges
  × 対象 OS 数
  × targetSdkVersion 条件
  × 権限状態
  × foreground / background 条件
  × process survival / process death 条件
```

全組合せを実行しない場合でも、どの組合せを契約テストで代替し、どこを E2E で保証するかを維持し続けるコストは残る。

---

# 直近 Android OS アップデートによる増幅リスク

以下の「構成への評価」は、本リポジトリで確認済みの Behavior Change を提案構成へ適用した分析であり、対象アプリで障害を観測した事実ではない。

| 優先度 | OS / 変更 | 適用条件 | 分割構成で増幅する理由 | 推奨対応 |
| --- | --- | --- | --- | --- |
| Critical | Android 16: ordered broadcast priority scope | OS update / all apps | 別 process・別 app 間の priority 順序は保証されない。状態遷移や初期化順を ordered broadcast に依存できない | 明示的 IPC と request / response、永続 state machine に置換 |
| Critical | Android 17: Activity Security | targetSdkVersion 37 + 起動条件 | background の service / receiver や trampoline から機能画面・結果画面を開く flow が制限対象になり得る | ユーザー操作から Activity PendingIntent へ直接接続し、background 自動起動を前提にしない |
| High | Android 16: Intent redirection hardening | OS update / nested Intent forwarding | サービスアプリが外部入力や nested Intent を機能アプリへそのまま転送する router 構成ほど block / exception / security risk が増える | explicit destination、allowlist、caller・action・data・flags・ClipData・grant の検証 |
| High | Android 17: implicit URI grant 移行 | Android 17 は検出、公式文書上 Android 18 から自動 grant 停止予定 | カメラ撮影、画像共有、本人確認画像を package 間で渡す箇所が増える | read / write URI grant を明示し、Android 17 StrictMode で先行検出 |
| High | Android 17: app memory limits | OS update / 対象端末・メモリ条件 | package / process の一方だけが終了する経路が増え、処理中状態の復旧不備が表面化する | transaction checkpoint、idempotency、`ApplicationExitInfo`、process death E2E |
| High | Android 16 / 17: large screen、edge-to-edge、predictive back | targetSdkVersion 36 / 37 + 画面条件 | 各 UI アプリが個別対応となり、戻る操作・Insets・回転・multi-window の不整合が増える | 共有 UI 基盤、全 package 共通の端末マトリクス、状態復元テスト |
| Medium-High | Android 16: fixed-rate scheduling optimization | targetSdkVersion 36 + 対象 API | 各アプリが独自に polling / retry / timeout を持つと、復帰時の実行回数差が取引状態の不一致につながる | wall-clock と永続状態から再計算し、callback 回数を正本にしない |
| Conditional | Android 17: local network permission | targetSdkVersion 37 + direct LAN access | カメラ機能アプリが Wi-Fi カメラ、ローカル HTTP / socket、mDNS / NSD を使う場合、機能アプリ側に独立した権限 UX が必要 | `ACCESS_LOCAL_NETWORK` の grant / denied / revoked と再接続を機能アプリ単位で検証 |
| Conditional | Android 16: 16 KB page size compatibility | OS update + native library | カメラ画像処理や NFC SDK の native `.so` を複数 APK に含めると、棚卸し・更新・検証対象が増える | 全 APK / AAB と third-party SDK の native alignment を確認 |

## 根拠となる既存調査

- [Android 16: ordered broadcast priority scope](../../../android16/behavior-changes/all/core-functionality/ordered-broadcast-priority-scope-no-longer-global.md)
- [Android 16: Intent redirection hardening](../../../android16/behavior-changes/all/security/improved-security-against-intent-redirection-attacks.md)
- [Android 16: fixed-rate scheduling optimization](../../../android16/behavior-changes/target/core-functionality/fixed-rate-work-scheduling-optimization.md)
- [Android 16: 16 KB page size compatibility mode](../../../android16/behavior-changes/all/core-functionality/16-kb-page-size-compatibility-mode.md)
- [Android 16: predictive back](../../../android16/behavior-changes/target/user-experience-and-system-ui/migration-or-opt-out-required-for-predictive-back.md)
- [Android 16: edge-to-edge opt-out](../../../android16/behavior-changes/target/user-experience-and-system-ui/edge-to-edge-opt-out-going-away.md)
- [Android 17: Activity Security](../../behavior-changes/target/security/activity-security.md)
- [Android 17: implicit URI grants](../../behavior-changes/all/security/restrict-implicit-uri-grants.md)
- [Android 17: app memory limits](../../behavior-changes/all/core-functionality/app-memory-limits.md)
- [Android 17: local network permission](../../behavior-changes/target/privacy/local-network-permission.md)
- [Android 17: large screen restrictions](../../behavior-changes/target/device-form-factors/large-screen-orientation-resizability-aspect-ratio.md)

---

# カメラ・NFC 別の評価

## カメラ機能アプリ

高リスクになりやすい境界:

- 撮影結果の content URI と read / write grant。
- 本人確認や決済証跡に関係する画像の所有者、保存期限、削除責任。
- 撮影中に呼び出し元が終了した場合の復旧。
- 画面回転、大画面、edge-to-edge、predictive back による撮影 flow の中断。
- Wi-Fi カメラを使う場合の Android 17 local network permission。
- native 画像処理 SDK を使う場合の 16 KB page size 対応。

カメラ機能を別アプリにすることで、カメラ権限や画像データの責任範囲が自動的に単純化するわけではない。サービスアプリへ結果を返す時点で、URI grant、データ寿命、再送、取消、監査ログの package 間契約が必要になる。

## NFC 機能アプリ

既存調査から確定できるのは、NFC 固有 API の変更ではなく、アプリ間連携に共通する Intent、Activity 起動、process death、back stack のリスクである。

追加で確認すべき点:

- NFC reader / tag discovery の開始・終了がどの Activity lifecycle に結び付くか。
- tag 検出後のデータをどの形式で、どの呼び出し元へ返すか。
- 機能アプリが foreground を失った場合、通信途中の状態をどう取消・照会するか。
- 同一 transaction の tag を複数回検出した場合の重複排除。
- HCE、reader mode、NFC-F、決済端末連携のどれを使うか。
- 機能アプリの未インストール、無効化、旧版、応答なしをどう扱うか。

したがって、既存資料に NFC 固有の変更がないことを「NFC は OS 更新リスクなし」とは解釈しない。採用判断前に、実際に使用する NFC API と Android 16 / 17 の公式文書・AOSP 根拠を対象に追加調査する必要がある。

---

# 代替案の比較

| 案 | 状態・UI の所有 | 独立配信 | 主な利点 | 主な欠点 | 推奨度 |
| --- | --- | --- | --- | --- | --- |
| A. 顧客別アプリ内のモジュール / SDK | 顧客別アプリ | 不可またはアプリ単位 | 最小の runtime 境界、型安全、復旧が単純 | 各顧客アプリの更新が必要 | 第一候補 |
| B. 共通 core + 顧客差分 shell | 各 shell、共通 state contract | 顧客アプリ単位 | 重複実装を抑えやすい | shell 間の更新統制が必要 | 推奨 |
| C. 1 つのオーケストレーター + feature app | オーケストレーターのみ | feature 単位 | 分割要件を満たしつつ state 所有者を限定 | IPC、配信、権限、復旧コストは残る | 必須要件がある場合のみ |
| D. 各顧客アプリ + 各 feature app が状態を分担 | 複数 app | 可能 | 組織単位で分離しやすい | 分散状態、`N × F` 契約、画面・運用不整合 | 非推奨 |

---

# 分割を採用する場合の最低条件

以下を満たせない場合は、実装開始前に構成を差し戻す。

1. 分割しなければ満たせない要件を明文化する。
   - 独立した署名・配布主体、法令・監査上の隔離、端末管理、独立更新のどれかを示す。
2. 状態の正本を 1 アプリに限定する。
   - 機能アプリを決済状態の正本にしない。
3. versioned contract を定義する。
   - request / result schema、capability negotiation、最低対応版、unsupported result を含める。
4. 全要求に transaction ID と idempotency key を付ける。
   - timeout 後は再実行の前に最終状態を照会できるようにする。
5. 明示的な連携だけを使う。
   - explicit component / package、署名検証、必要なら signature permission を使用する。
   - ordered broadcast の priority、暗黙 Intent、未検証の nested Intent を正本にしない。
6. Activity 起動をユーザー操作と結び付ける。
   - background service / receiver からの自動画面表示や notification trampoline に依存しない。
7. URI grant を明示する。
   - カメラ・共有 flow の read / write grant と有効期間を契約化する。
8. process death を正常系として設計する。
   - 呼び出し元のみ終了、機能側のみ終了、両方終了、更新中断を E2E で検証する。
9. package 間の一貫した observability を用意する。
   - transaction ID、package version、OS、targetSdkVersion、権限状態、起動経路をログへ残す。
10. 互換性・配信マトリクスの所有者を決める。
    - 顧客別アプリと feature app の rollout / rollback 順序、サポート期限、緊急停止手段を定義する。

---

# 推奨検証マトリクス

| ケース | 呼び出し元 | 機能アプリ | 期待結果 |
| --- | --- | --- | --- |
| 正常完了 | foreground | foreground | 一度だけ成功を反映し、正しい画面へ戻る |
| ユーザー取消 | foreground | foreground | 取消を成功・失敗と区別し、再実行可能 |
| 権限拒否 | foreground | foreground | 対象 package の権限不足を正しく案内 |
| 呼出元 process death | killed | 実行継続 | 復帰後に transaction を照会し、二重実行しない |
| 機能側 process death | 待機 | killed | timeout と失敗を区別し、安全に再開できる |
| 両 process death | killed | killed | 永続状態から未確定取引を復旧・照会できる |
| version mismatch | 新版 / 旧版 | 旧版 / 新版 | unsupported を明示し、誤った fallback をしない |
| background 起動 | background | 未起動 | Android 17 の制限下で勝手に画面を出さず、通知等へ誘導 |
| URI 受渡し | foreground | foreground | 明示 grant で読書きでき、期限後は不要な権限を残さない |
| back / gesture | foreground | foreground | 戻り先と取引取消の状態が一致する |
| rotation / fold / multi-window | foreground | foreground | state を失わず、重複起動しない |
| feature app 更新・無効化・未導入 | foreground | unavailable | 安全に中止し、インストール / 更新案内へ遷移 |

OS / targetSdkVersion の最低組合せ:

- Android 15 / targetSdkVersion 35: baseline。
- Android 16 / targetSdkVersion 35: OS update impact。
- Android 16 / targetSdkVersion 36: target 36 impact。
- Android 17 / targetSdkVersion 36: OS update impact。
- Android 17 / targetSdkVersion 37: target 37 impact。

---

# 判断材料として不足している情報

- 顧客別アプリ数 `N`、機能別アプリ数 `F`、各組合せの利用有無。
- 分割しなければ満たせない業務・法令・セキュリティ・配布要件。
- 現在の決済 state machine と、未確定取引の照会・取消仕様。
- アプリ間の起動方式: Activity、PendingIntent、service、broadcast、ContentProvider、AIDL。
- カメラ画像の受渡し方式とデータ保持ポリシー。
- NFC の利用方式と SDK / native library。
- 各 package の署名、exported component、custom permission、caller verification。
- リリース頻度、後方互換期間、段階配信・rollback 手順。

---

# 推奨判断

暫定判断:

- **Hold / No-Go**。アプリ分割を前提に実装へ進まず、単一アプリ内モジュール案との比較を先に行う。

再判断条件:

- 分割必須要件が文書化されている。
- `N × F` の契約・試験・運用コストが見積もられている。
- 状態の正本、versioned contract、idempotency、process death、Activity 起動、URI grant の設計がレビュー済みである。
- カメラ・NFC の実 API と Manifest を使った Android 16 / 17 実機検証計画がある。

人間の最終判断:

- Pending

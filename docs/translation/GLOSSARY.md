# 翻訳用語集

このファイルは、Android Behavior Change 調査レポートを日本語化するときの標準訳を定義する。
分類 ID、API 名、コマンド、ファイルパスは原則として翻訳しない。

## 標準訳

| 英語 | 標準訳 | 備考 |
| --- | --- | --- |
| applicability | 適用条件 | 見出しでは「適用条件分類」も使う。 |
| applicability classification | 適用条件分類 | `APPLICABILITY_CLASSIFICATION.md` ではこの訳を使う。 |
| evidence | 根拠 | AOSP evidence は「AOSP 根拠」でもよい。 |
| finding | 調査項目 | 文脈上「finding」を残す必要がある場合を除く。 |
| gate | gate / 適用 gate | 技術的な gate は無理に訳さない。説明文では「適用条件」も可。 |
| confidence | confidence | `High confidence` などの分類語は英語を残す。 |
| missing evidence | 不足している根拠 | |
| original statement | 検証対象の原文 | Summary / report の根拠欄で使用。 |
| original applicability statement | 検証対象の適用条件文 | |
| official documentation | 公式ドキュメント | |
| official documentation page | 公式ドキュメントページ | |
| AOSP files | AOSP ファイル | |
| AOSP source context | AOSP ソース文脈 | |
| diff interpretation | 差分解釈 | |
| gate conclusion | 適用 gate の結論 | |
| required context | 必須記入項目 | report template 由来の項目。 |
| required interpretation | 必須分類 | |
| evidence limitation | 根拠上の制約 | |
| current status | 現在の状況 | |
| from | 比較元 | AOSP tag の比較元。 |
| to | 比較先 | AOSP tag の比較先。 |
| previous targetSdkVersion | 以前の targetSdkVersion | |
| target targetSdkVersion | 対象 targetSdkVersion | |
| document | 文書 | metadata 欄で使用。 |
| related documents | 関連文書 | |
| section | セクション | |
| page type | ページ種別 | |
| final priority | 最終優先度 | |
| final severity | 最終影響度 | |
| release readiness | リリース判断 | |
| customer communication required | 顧客通知要否 | |
| human decision required | 人間による判断が必要 | |
| further investigation required | 追加調査が必要 | |
| unknown | 未確認 | 調査上未確認の場合。 |
| likely | 可能性が高い | 単独では使わず「可能性が高いが未検証」などにする。 |
| unverified | 未検証 | |
| TBD | 未定 | |
| local checkout | ローカル checkout | 手元にある checkout を指す。 |
| local working tree | ローカル working tree | 手元の git working tree を指す。 |
| local `frameworks-base` checkout | ローカルの `frameworks-base` checkout | 手元にある `frameworks-base` ディレクトリ / checkout を指す。 |
| default state | 既定状態 | compat framework 欄。 |
| change name | 変更名 | compat framework 欄。 |
| toggleable for testing | テスト時の切り替え可否 | |
| camera companion app | カメラ連携アプリ | 特定製品名ではなく、カメラと接続・連携するアプリ全般を指す。 |
| standard pairing | 通常のペアリング | 初回ペアリングを強調する場合は「通常の初回ペアリング」も可。 |
| autonomous re-pairing | 自動再ペアリング | Android 17 の Bluetooth bond loss 復旧機能。 |
| system-managed repairing | システムによる自動修復 | Bluetooth bond loss の文脈。 |
| app-managed recovery | アプリによる復旧処理 | システム側の処理と対比する場合に使う。 |
| manual unpair / re-pair guidance | 手動でのペアリング解除 / 再ペアリング手順 | ユーザー向けの復旧案内を指す。 |
| Wi-Fi handoff | Wi-Fi 接続への引き継ぎ | Bluetooth 接続を起点に Wi-Fi へ移行する文脈。 |
| app-local registration | アプリ内だけの登録 | Android の Bluetooth bond と区別する。 |
| security level | セキュリティレベル | Bluetooth の鍵置き換え条件などで使う。 |
| existing security key | 既存のセキュリティ鍵 | 単に「既存の鍵」としてもよい。 |
| one-finger movement | 1 本指での移動 | タッチパッド操作の説明。 |
| two-finger scroll | 2 本指でのスクロール | タッチパッド操作の説明。 |
| finger lift / reposition | 指の持ち上げ / 置き直し | タッチパッド端での操作継続を説明する場合に使う。 |
| movement delta | 移動量 / 相対移動量 | relative mode の説明では「相対移動量」を優先する。 |
| event-level test | イベント単位のテスト | システムから届くイベント内容の確認。 |
| user-flow test | ユーザー操作単位のテスト | アプリ側の座標解釈を含む動作確認。 |
| visible activity | ユーザーに表示されている Activity | background audio hardening の適用条件。 |
| running FGS | 実行中の FGS | `foreground service` 自体は識別しやすいよう英語を残す。 |
| background-started FGS | バックグラウンドから開始した FGS | user-initiated FGS と対比する。 |
| default condition | 既定状態 | hardening override を強制していない状態など。 |
| default enabled | 既定で有効 | 「標準で有効」も顧客向け説明では使用可。 |
| primary report | 主レポート | 根拠・適用条件・confidence の正本を指す。 |
| one-page summary | 1ページ要約 | ファイル名と対応させる場合もこの訳を使う。 |
| companion document | 補足資料 | 主レポートから分離した比較・FAQ・実装例。 |
| missed execution | 未実行処理 / 未実行分 | `scheduleAtFixedRate` の文脈。 |
| missed period | 実行できなかった周期 | 単に「未実行周期」とせず、何が起きたかを明示する。 |
| catch-up | 追いつき実行 / 未実行分をまとめて実行 | 読者向け説明では後者を優先する。 |
| fixed-rate backlog | fixed-rate の未実行分 | backlog を業務データと誤解させない。 |
| process freeze / suspend | プロセスの凍結 / 一時停止 | process death と区別する。 |
| process death | プロセス終了 | in-memory queue が失われる状態。 |
| legacy back handling | 従来方式の Back 処理 | `onBackPressed()` / `KEYCODE_BACK` 依存など。 |
| system back gesture | システムの Back gesture | API 名と区別できる場合は「システムの戻るジェスチャー」も可。 |
| supported back navigation API | 対応する Back navigation API | `OnBackInvokedCallback` / AndroidX API の文脈。 |
| production build | 製品版ビルド | `user` / retail build を含む実運用向けビルド。 |
| non-debuggable release app | non-debuggable の製品版アプリ | debug 例外との比較で使う。 |
| direct access | 直接アクセス | `/dev/mali0` などへの直接アクセス。 |
| SELinux denial | SELinux の拒否ログ | 実機で観測する `avc: denied`。 |
| feature failure | 機能停止 | 単なるログ出力と区別する。 |
| graceful fallback | 安全な代替処理への切り替え | fallback 先が安全と確認できない場合は「代替処理への切り替え」とする。 |

## 残す用語

以下は原則として英語または識別子のまま残す。

- `targetSdkVersion`
- `minSdkVersion`
- `Compat Change ID`
- `Change ID`
- `AOSP`
- `Behavior Change`
- `Mainline`
- `Google Play system update`
- `API surface`
- `current.txt`
- `frameworks-base`
- `foreground service`
- `while-in-use`
- `WIU capability`
- `exact alarm permission`
- `USAGE_ALARM`
- `hardening override`
- `partial` / `full`
- `absolute mode` / `relative mode`
- `pointer capture`
- `local network`
- `local network permission`
- `IntentSender`
- `PendingIntent`
- `Network Security Configuration`
- `FileProvider`
- `WebOTP`
- `SMS Retriever`
- `SMS User Consent API`
- `UNKNOWN_NEEDS_MORE_EVIDENCE`
- `OS_UPDATE_ALL_APPS`
- `TARGET_SDK_37`
- `TARGET_SDK_37_CONDITIONAL`
- `MAINLINE_OR_PLAY_SYSTEM_UPDATE`
- `API_ADDITION_ONLY`

## `local` の扱い

`local` は文脈で訳し分ける。

| 文脈 | 扱い | 例 |
| --- | --- | --- |
| 手元の checkout / working tree / repository を指す場合 | 「ローカルの」「手元の」と訳す | `local frameworks-base checkout` → `ローカルの frameworks-base checkout` |
| Android 機能名やネットワーク概念の一部の場合 | 原則として `local` を残す | `local network permission`, `local network access` |
| AOSP / git の状態説明の場合 | 「ローカル」を使ってよい | `local checkout has no tag` → `ローカル checkout にタグが存在しない` |

## 判定表の標準表現

| 英語表現 | 標準訳 |
| --- | --- |
| Likely Yes / Conditional, but unverified | 可能性は高いが条件付き、かつ未検証 |
| Likely No, but unverified | 不要と考えられるが未検証 |
| Likely No for this guidance, but unverified | この guidance では不要と考えられるが未検証 |
| Likely No immediate enforcement, but unverified | 即時 enforcement はない可能性が高いが未検証 |
| Likely No immediate runtime behavior, but unverified | 即時の runtime behavior はない可能性が高いが未検証 |
| Yes | ある |
| Yes, for relevance | 関連条件としてある |
| Partially | 一部で必要 |
| Unknown | 未確認 |

## 判断欄の標準表現

| 英語表現 | 標準訳 |
| --- | --- |
| Human decision required | 人間による判断が必要 |
| Further investigation of the related AOSP project is required | 関連AOSP projectの追加調査が必要 |
| Final Priority | 最終優先度 |
| Final Severity | 最終影響度 |
| Release Readiness | リリース判断 |
| Customer Communication Required | 顧客通知要否 |

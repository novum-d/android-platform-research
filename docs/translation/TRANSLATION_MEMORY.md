# 翻訳メモリ

このファイルは、過去の Android 16 / Android 17 調査レポート翻訳で採用した表現を記録する。
今後の翻訳では、ここを参照して表現の一貫性を保つ。

## Metadata

```text
From:
```

採用訳:

```text
比較元:
```

```text
To:
```

採用訳:

```text
比較先:
```

```text
Previous targetSdkVersion:
```

採用訳:

```text
以前の targetSdkVersion:
```

```text
Target targetSdkVersion:
```

採用訳:

```text
対象 targetSdkVersion:
```

```text
Document:
Related documents:
Section:
Page type:
```

採用訳:

```text
文書:
関連文書:
セクション:
ページ種別:
```

## 判定表

```text
| Question | Answer | Evidence |
```

採用訳:

```text
| 確認項目 | 回答 | 根拠 |
```

```text
Likely Yes / Conditional, but unverified
```

採用訳:

```text
可能性は高いが条件付き、かつ未検証
```

```text
Likely No, but unverified
```

採用訳:

```text
不要と考えられるが未検証
```

```text
Yes, for relevance
```

採用訳:

```text
関連条件としてある
```

## Compat framework

```text
Change ID: Unknown
Change name: Unknown
Default state: Unknown
Toggleable for testing: Unknown
```

採用訳:

```text
Change ID: 未確認
変更名: 未確認
既定状態: 未確認
テスト時の切り替え可否: 未確認
```

## 根拠欄

```text
Official documentation:
Original statement:
AOSP files:
AOSP source context:
Diff interpretation:
Gate conclusion:
```

採用訳:

```text
公式ドキュメント:
検証対象の原文:
AOSP ファイル:
AOSP ソース文脈:
差分解釈:
適用 gate の結論:
```

```text
Official documentation page:
Original applicability statement:
```

採用訳:

```text
公式ドキュメントページ:
検証対象の適用条件文:
```

## 判断欄

```text
Human Decision Placeholder
```

採用訳:

```text
人間の判断欄
```

```text
Final Priority:
Final Severity:
Release Readiness:
Customer Communication Required:
```

採用訳:

```text
最終優先度:
最終影響度:
リリース判断:
顧客通知要否:
```

```text
Human decision required
Further investigation of the related AOSP project is required
```

採用訳:

```text
人間による判断が必要
関連AOSP projectの追加調査が必要
```

## README / 手順書

```text
Current status:
Generated from:
Using:
Rule:
How To Use:
```

採用訳:

```text
現在の状況:
生成元:
使用するコマンド:
取り扱いルール:
使い方:
```

```text
The target tag is not currently available in the local checkout for <AOSP project>.
```

採用訳:

```text
現時点では、`<AOSP project>`のローカルcheckoutに対象tagは存在しません。
```

補足:
- ここでの `local` は Android の機能名ではなく、手元にある checkout / ディレクトリを指す。
- `local network permission` の `local` は機能名の一部なので、この訳し方を流用しない。

```text
Do not create High confidence AOSP-backed conclusions until the target tag and relevant implementation path are verified.
```

採用訳:

```text
対象tagと関連実装pathを確認するまでは、AOSP根拠に基づくHigh confidenceの結論を作成しないでください。
```

## 調査上の定型表現

```text
The target AOSP tag is not available in the local checkout for <AOSP project>.
```

採用訳:

```text
`<AOSP project>`のローカルcheckoutには対象AOSP tagが存在しない。
```

```text
Do not assign High confidence.
```

採用訳:

```text
High confidence を付けない。
```

```text
Customer-facing wording does not mix OS update impact with targetSdkVersion impact.
```

採用訳:

```text
顧客向け表現で、OS アップデートによる影響と targetSdkVersion 変更による影響を混同していない。
```

## Bluetooth bond loss / カメラ連携

```text
camera companion app
standard pairing
autonomous re-pairing
system-managed repairing
app-managed recovery
```

採用訳:

```text
カメラ連携アプリ
通常のペアリング
自動再ペアリング
システムによる自動修復
アプリによる復旧処理
```

```text
manual unpair / re-pair guidance
Wi-Fi handoff
app-local registration
existing security key
security level
```

採用訳:

```text
手動でのペアリング解除 / 再ペアリング手順
Wi-Fi 接続への引き継ぎ
アプリ内だけの登録
既存のセキュリティ鍵
セキュリティレベル
```

```text
Confirm that system-managed repairing and app-managed recovery do not compete.
```

採用訳:

```text
システムによる自動修復とアプリによる復旧処理が競合しないことを確認する。
```

補足:
- `BOND_NONE`、`BOND_BONDING`、`BOND_BONDED`、`ACTION_KEY_MISSING` などの識別子は翻訳しない。
- `Wi-Fi-only camera` は「Wi-Fi のみで接続するカメラ」、`Bluetooth-enabled camera` は「Bluetooth 対応カメラ」とする。
- `app-local registration` は Android の Bluetooth bond と区別するため、「アプリ内だけの登録」とする。

## タッチパッド / pointer capture

```text
one-finger movement
two-finger scroll
finger lift / reposition
movement delta
```

採用訳:

```text
1 本指での移動
2 本指でのスクロール
指の持ち上げ / 置き直し
移動量 / 相対移動量
```

```text
event-level test
user-flow test
```

採用訳:

```text
イベント単位のテスト
ユーザー操作単位のテスト
```

```text
Relative mode delivers movement delta instead of the finger location.
```

採用訳:

```text
relative mode は、指の位置ではなく、前回からの移動量を通知する。
```

補足:
- `absolute mode`、`relative mode`、`pointer capture`、`MotionEvent` の定数は技術用語として残す。
- `jump` は、カーソルや選択位置の文脈では「飛ぶ」とする。
- 座標ログだけを指す場合は「イベント単位」、実際のカーソルやカメラ操作まで含む場合は「ユーザー操作単位」と書き分ける。

## Background audio hardening

```text
visible activity
running FGS
background-started FGS
default condition
```

採用訳:

```text
ユーザーに表示されている Activity
実行中の FGS
バックグラウンドから開始した FGS
既定状態
```

```text
The all-app restriction is the base, with additional conditions for apps targeting Android 17 or higher.
```

採用訳:

```text
全アプリ共通の制限を土台として、targetSdkVersion 37 以上のアプリに追加条件が重なる。
```

```text
Run the targetSdkVersion 36 / 37 comparison under default conditions without forcing the hardening override.
```

採用訳:

```text
targetSdkVersion 36 / 37 の比較は、hardening override を強制していない既定状態で実施する。
```

補足:
- `WIU capability`、`exact alarm permission`、`USAGE_ALARM`、`hardening override`、`partial` / `full` は識別しやすいよう英語を残す。
- `positive case` / `negative case` は、条件の成立可否を説明する文脈では「成功ケース」/「失敗ケース」とする。

## Android 16 固定間隔スケジューリング

```text
missed execution
missed period
catch-up
fixed-rate backlog
process freeze / suspend
process death
```

採用訳:

```text
未実行処理 / 未実行分
実行できなかった周期
追いつき実行 / 未実行分をまとめて実行
fixed-rate の未実行分
プロセスの凍結 / 一時停止
プロセス終了
```

```text
At most one missed execution is immediately executed when the app returns to a valid lifecycle.
```

採用訳:

```text
アプリが再び実行可能になったとき、未実行分が即時実行される回数は最大1回となる。
```

```text
Do not depend on the number of catch-up callbacks. Calculate the required work from the last successful time and the current time.
```

採用訳:

```text
callback がまとめて呼ばれる回数に依存せず、最終成功時刻と現在時刻から必要な処理量を計算する。
```

補足:
- `missed execution` を単に「失敗した実行」と訳さない。処理が失敗したのではなく、予定時刻に実行できなかったことを表す。
- `process freeze / suspend` と `process death` を混同しない。後者では Timer / executor と in-memory queue 自体が失われる。
- `catch-up` は開発者向けの用語説明では「追いつき実行」、顧客向け説明では「未実行分をまとめて実行」とする。

## Android 16 Predictive Back

```text
default enabled
legacy back handling
system back gesture
supported back navigation API
temporary opt-out
```

採用訳:

```text
既定で有効
従来方式の Back 処理
システムの Back gesture
対応する Back navigation API
一時的な opt-out
```

```text
Predictive back system animations are enabled by default for apps targeting Android 16 or higher.
```

採用訳:

```text
targetSdkVersion 36 以上のアプリでは、Predictive Back のシステムアニメーションが既定で有効になる。
```

補足:
- 製品機能名として説明する場合は `Predictive Back` と表記する。
- `onBackPressed()`、`KEYCODE_BACK`、`OnBackInvokedCallback`、`OnBackPressedDispatcher` は翻訳しない。
- `back handling` は「Back 処理」、`back event` は「Back イベント」とする。
- `default enabled` は調査レポートでは「既定で有効」、顧客向け説明では「標準で有効」も使用できる。

## Android 16 GPU syscall filtering

```text
production build
non-debuggable release app
direct access
SELinux denial
feature failure
graceful fallback
```

採用訳:

```text
製品版ビルド
non-debuggable の製品版アプリ
直接アクセス
SELinux の拒否ログ
機能停止
安全な代替処理への切り替え
```

```text
Supported Vulkan and OpenGL usage is not affected. Direct Mali IOCTL usage may be affected.
```

採用訳:

```text
正式に対応している Vulkan / OpenGL の利用には影響しない。Mali IOCTL を直接使用する場合は影響する可能性がある。
```

補足:
- `denial` は実機ログを指す場合、「拒否」だけではなく「拒否ログ」とする。
- `supported API` は「正式に対応している API」または「対応済み API」とする。
- `block` / `deny` は policy の挙動として「拒否」とする。「遮断」や「ブロック」は原則として使わない。
- `fallback` が安全であることを確認できない場合は、「安全な」を付けず「代替処理への切り替え」とする。

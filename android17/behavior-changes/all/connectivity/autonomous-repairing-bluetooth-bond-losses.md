# Bluetooth ペアリング情報消失時の自律的な再ペアリング

## 基本情報（Metadata）

### 調査対象 Android バージョン

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP タグ

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

### Behavior Change 文書

Document:
- https://developer.android.com/about/versions/17/behavior-changes-all

Related documents:
- https://developer.android.com/reference/android/bluetooth/BluetoothDevice#ACTION_PAIRING_REQUEST
- https://developer.android.com/reference/android/bluetooth/BluetoothDevice#EXTRA_PAIRING_CONTEXT
- https://developer.android.com/reference/android/bluetooth/BluetoothDevice#ACTION_KEY_MISSING
- https://developer.android.com/guide/topics/connectivity/bluetooth
- https://developer.android.com/develop/connectivity/bluetooth

Section:
- Bluetooth ペアリング情報消失時の自律的な再ペアリング

Page type:
- Behavior changes: 全アプリ

### 分類スナップショット

主分類（Primary classification）:
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- 公式文書は Android 17 の `Behavior changes: all apps` ページにこの項目を掲載している。
- 原文は、Android 17 が Bluetooth のペアリング情報の消失を自動的に解決するシステムレベルの機能強化として自律的な再ペアリングを導入すると説明している。
- 原文は、従来はペアリング情報の消失時にユーザーが OS の設定アプリから手動でペアリング解除と再ペアリングを行う必要があったが、Android 17 ではシステムがバックグラウンドでペアリング情報を再確立できると説明している。
- 原文には targetSdkVersion 条件は記載されていない。
- ただし、ローカルの `frameworks-base` に Android 17 AOSP タグがないため、Bluetooth stack、ペアリング intent、ペアリング情報の状態、鍵更新、通知 UI、Compat framework エントリは未確認である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

早見表:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | その可能性が高いが、追加条件の有無は未確認 | 公式文書は全アプリ向けページに掲載し、targetSdkVersion 条件を示していない。AOSP の適用ゲートは未確認。 |
| targetSdkVersion 37 以上が必要か | 公式文書上は不要だが、AOSP では未確認 | 原文に targetSdkVersion 条件はない。AOSP の targetSdkVersion 適用ゲートは未確認。 |
| 追加の実行時条件があるか | あり | Bluetooth 周辺機器のペアリング情報が失われ、システムが自律的な再ペアリングを試行する場合。コンパニオンアプリがペアリング関連または `ACTION_KEY_MISSING` ブロードキャストを扱う場合は特に確認が必要。 |
| Compat Change ID が関係するか | 未確認 | Android 17 タグと Compat framework の根拠が未確認。 |

### 調査日（Investigation Date）

2026-06-15

### 信頼度

- 低

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] Android 17 上の全アプリ（targetSdkVersion に依存しない）
- [ ] Android 17 以上で targetSdkVersion >= 37
- [ ] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [x] 未確認 / 追加根拠が必要

必要な実行時条件:
- Android バージョン: Android 17 以上。AOSP タグ未取得のため、実装上の OS 適用ゲートは未確認。
- targetSdkVersion: 公式文書上は条件なし。AOSP の targetSdkVersion 適用ゲートは未確認。
- 端末/フォームファクター: Bluetooth 周辺機器とペアリングする Android 端末。
- Permission/API/コンポーネント条件: Bluetooth ボンディング / ペアリング、`BluetoothDevice.ACTION_PAIRING_REQUEST`、`BluetoothDevice.EXTRA_PAIRING_CONTEXT`、`BluetoothDevice.ACTION_KEY_MISSING`、システムのペアリング UI、コンパニオンアプリまたは周辺機器メーカーの復旧フロー。
- アプリ状態/プロセス条件: コンパニオンアプリまたは周辺機器アプリがペアリング関連ブロードキャストや `ACTION_KEY_MISSING` を監視する場合、または手動でのペアリング解除と再ペアリングによる復旧フローを案内している場合。

Compat framework:
- Change ID: 未確認
- 変更名: 未確認
- default state: 未確認
- テスト時の切り替え可否: 未確認

分類信頼度:
- 低

分類根拠:
- Official documentation page: `behavior-changes-all`
- 検証対象の適用条件文: Android 17 は自律的な再ペアリングを導入し、ペアリング情報の消失時にシステムがバックグラウンドでペアリング情報を再確立できる。Bluetooth stack の intent、鍵更新、UI タイミングに変更がある。
- AOSP targetSdk 適用ゲート: 未確認。ローカルの `frameworks-base` に `android-17*` タグがない。
- Compat framework エントリ: 未確認。Android 17 Compat framework の根拠が未取得。

---

# エグゼクティブサマリー

Android 17 では、Bluetooth のペアリング情報が失われた場合に、システムが自動的に回復を試みる自律的な再ペアリングが導入される。従来はペアリング情報が失われると、ユーザーが OS の設定アプリで周辺機器のペアリングを解除し、再度ペアリングする必要があった。Android 17 では、システムがバックグラウンドでペアリング情報の再確立を試行できる。

多くのアプリではコード変更は不要とされている。ただし、Bluetooth コンパニオンアプリ、周辺機器メーカーのアプリ、wearable / audio / IoT / health 端末アプリなど、ペアリングや `ACTION_KEY_MISSING` ブロードキャストを扱うアプリは、Bluetooth stack の挙動変更を確認する必要がある。`ACTION_PAIRING_REQUEST` には `EXTRA_PAIRING_CONTEXT` が追加され、通常のペアリング要求と、システム起点の自律的な再ペアリング試行を区別できる。`ACTION_KEY_MISSING` は、自律的な再ペアリングが失敗した場合だけブロードキャストされる。

現時点ではローカルの `frameworks-base` に Android 17 AOSP タグがなく、Bluetooth stack の実装、API surface、targetSdkVersion 適用ゲート、Compat Change ID を確認できない。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE`、信頼度は低とする。

---

# 公式ドキュメント確認

## 原文（Statement）

Page title:
- Behavior changes: 全アプリ

Page URL:
- https://developer.android.com/about/versions/17/behavior-changes-all

Page type:
- 全アプリ

Section title:
- Bluetooth ペアリング情報消失時の自律的な再ペアリング

検証対象の原文:
- Android 17 は Bluetooth のペアリング情報の消失を自動的に解決するシステムレベルの機能強化として自律的な再ペアリングを導入する。
- 従来は、ペアリング情報の消失時にユーザーが OS の設定アプリで周辺機器を手動でペアリング解除し、再度ペアリングする必要があった。
- Android 17 では、システムがバックグラウンドでペアリング情報を再確立できる。
- `ACTION_PAIRING_REQUEST` は `EXTRA_PAIRING_CONTEXT` extra を含むようになり、通常のペアリング要求と、システム起点の自律的な再ペアリング試行を区別できる。
- 再ペアリングが成功し、新しい接続が以前のペアリング情報と同等以上のセキュリティレベルを満たす場合にのみ、既存のセキュリティ鍵が置き換えられる。
- `ACTION_KEY_MISSING` intent は、自律的な再ペアリング試行が失敗した場合だけブロードキャストされる。
- システムは通知 / ダイアログによって再ペアリングを管理し、ユーザーは再接続を認識できるよう確認を求められる。

## 解釈

この変更は、Bluetooth のペアリング情報消失時の復旧を、ユーザーやアプリが案内する手動復旧から、システム管理の自律的な再ペアリングへ寄せる挙動変更である。アプリ側の主要な確認観点は、ペアリング要求の文脈判定、`ACTION_KEY_MISSING` ブロードキャストのタイミング変化、セキュリティ鍵の更新条件、システム管理の通知 / ダイアログとの整合である。

顧客向けには「すべての Bluetooth アプリで必ず変更が必要」ではなく、「多くのアプリではコード変更は不要だが、コンパニオンアプリや周辺機器メーカーのアプリは、ペアリング情報の遷移を検証する必要がある」と説明する。

---

# 変更内容

公式文書上の変更点:
- Android 17 で自律的な再ペアリングが導入される。
- ペアリング情報の消失後、システムがバックグラウンドでペアリング情報を再確立できる。
- `ACTION_PAIRING_REQUEST` に `EXTRA_PAIRING_CONTEXT` が追加され、ペアリング要求の文脈を区別できる。
- セキュリティ鍵は、再ペアリングが成功し、以前のペアリング情報と同等以上のセキュリティレベルを満たす場合にのみ置き換えられる。
- `ACTION_KEY_MISSING` は、自律的な再ペアリング失敗時だけブロードキャストされる。
- システム管理の通知 / ダイアログによって、ユーザーに再ペアリング試行が提示される。
- 周辺機器メーカーとコンパニオンアプリ開発者は、ペアリング情報の遷移を検証する必要がある。

AOSP で未確認の点:
- 自律的な再ペアリングのトリガー条件とリトライ / タイムアウトポリシー。
- `EXTRA_PAIRING_CONTEXT` の値、型、API surface、通常のペアリングと自律的な再ペアリングの区別方法。
- `ACTION_KEY_MISSING` ブロードキャストのタイミングの実装。
- セキュリティ鍵の置き換えにおけるセキュリティレベル判定。
- システム通知 / ダイアログの UI フローとユーザー確認要件。
- targetSdkVersion 適用ゲートの有無。
- Compat framework Change ID と default state。

## 適用条件（Applicability）

この変更がいつ適用されるかを OS 条件と targetSdkVersion 条件に分けて説明する。

### OS アップデート時の挙動

- Android 17 に OS アップデートしただけで適用されるか: 公式文書上は Yes / Conditional。全アプリ向けページに掲載され、targetSdkVersion 条件は示されていない。ただし AOSP 適用ゲートは未確認。
- targetSdkVersion に依存しない根拠: 原文に targetSdkVersion 条件がない。
- Android 16 以前での挙動: ペアリング情報の消失時は、ユーザーが OS の設定アプリで手動でペアリング解除と再ペアリングを行う必要があったと公式文書が説明している。Android 16 の基準挙動における Bluetooth stack の挙動は AOSP 差分では未確認。

### targetSdkVersion 37 以上での挙動

- targetSdkVersion 37 以上で適用されるか: 公式文書上、targetSdkVersion 37 は必要条件ではない。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: 未確認。公式文書は Android 17 platform の挙動として説明している。
- opt-out / temporary override の有無: 未確認。公式文書にはアプリレベルの opt-out は記載されていない。

### その他の条件

- 端末状態: Bluetooth 周辺機器のペアリング情報の消失が発生する。
- アプリ / 周辺機器の役割: コンパニオンアプリ、周辺機器メーカーのアプリ、wearable / audio / IoT / health 端末アプリなど、ペアリングやペアリング情報の遷移を扱うアプリ。
- ブロードキャスト使用: アプリが `ACTION_PAIRING_REQUEST` または `ACTION_KEY_MISSING` を扱う。
- ユーザーフロー: アプリがユーザーに手動でのペアリング解除と再ペアリングを案内している場合、Android 17 ではシステム管理の復旧と UI が先に入る可能性がある。
- セキュリティ条件: 鍵の置き換えは、再ペアリングが成功し、十分なセキュリティレベルを満たす場合に限定される。

---

# AOSP 調査

## checkout 状態

確認コマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list 'android-17*'
```

結果:
- `frameworks-base` の `status --short` は空で、dirty な作業ツリーは確認されなかった。
- `android-16.0.0_r4` タグは存在する。
- `android-17*` タグはローカル checkout に存在しない。

根拠上の制約:
- Android 17 AOSP タグがローカルの `frameworks-base` にないため、`android-16.0.0_r4` と Android 17 タグの明示的なソース差分は実行できない。
- Bluetooth stack は `frameworks-base` 以外の `packages/modules/Bluetooth` などに実装がある可能性が高いため、Android 17 タグ入手後は該当 project も確認する必要がある。
- そのため、ローカル作業ツリーや未確定 branch を platform 根拠として扱わない。
- 本レポートの AOSP に基づく結論は低信頼度に留める。

## 関連ファイル

Android 17 AOSP タグ未取得のため、タグ間差分に基づく関連ファイルは未確定。

Android 17 タグ 公開後に確認すべき候補:
- `core/java/android/bluetooth/BluetoothDevice.java`
- `packages/modules/Bluetooth/` 以下のペアリング情報 / ペアリング / security manager パス
- Bluetooth ペアリング UI / 通知を扱うシステム UI または Bluetooth module パス
- `ACTION_PAIRING_REQUEST` broadcast generation path
- `EXTRA_PAIRING_CONTEXT` API surface / `current.txt`
- `ACTION_KEY_MISSING` broadcast generation path
- security key 更新 / link key replacement path
- Compat framework 定義ファイル内の Bluetooth 自律的な再ペアリング関連 Change ID

## 確認したソース文脈

AOSP タグ間差分は未実行。以下は公式文書から見た確認予定のソース文脈であり、AOSP 根拠ではない。

| ファイル / シンボル | Android 16 の基準挙動 | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| Bluetooth のペアリング情報消失を検出するパス | 未確認 | ペアリング情報の消失後に自律的な再ペアリングを試行すると公式文書が説明 | システム管理の復旧のトリガーポイントになるため |
| `BluetoothDevice.ACTION_PAIRING_REQUEST` | 未確認 | `EXTRA_PAIRING_CONTEXT` を含むと公式文書が説明 | アプリがペアリングの文脈を区別する、開発者に見える API であるため |
| `BluetoothDevice.ACTION_KEY_MISSING` | 未確認 | 自律的な再ペアリング失敗時のみブロードキャストされると公式文書が説明 | コンパニオンアプリのエラーハンドリングのタイミングに影響するため |
| セキュリティ鍵の更新パス | 未確認 | 再ペアリングが成功し、以前のペアリング情報と同等以上のセキュリティレベルを満たす場合のみ鍵を置き換える | 周辺機器のセキュリティ / ボンディング継続性の根拠になるため |
| システムのペアリング UI / 通知パス | 未確認 | システムが通知 / ダイアログでユーザー確認を扱う | ユーザーに見えるフローと、アプリが案内する復旧フローの衝突確認に必要なため |
| Compat framework エントリ | 未確認 | targetSdkVersion 適用ゲートの有無は不明 | 全アプリ型か targetSdkVersion 適用ゲート型かの確定に必要なため |

必須記入項目:
- 入口 / 呼び出し元: 未確認。想定される入口は、Bluetooth stack がペアリング情報の消失または鍵欠落を検出 -> 自律的な再ペアリング試行 -> ペアリング要求ブロードキャスト / システム UI -> 鍵更新、または `ACTION_KEY_MISSING` 失敗ブロードキャスト、という流れである。
- Relevant class or service responsibility: bond state management、pairing request context、security key 更新、failure notification、system pairing UI。
- アプリ API / システムイベントから変更箇所までの実行時パス: 周辺機器のペアリング情報消失 -> システムが自律的な再ペアリングを開始 -> ユーザー確認 UI / ペアリング文脈を含むブロードキャスト -> 成功した場合はセキュリティ鍵を条件付き更新、失敗した場合は `ACTION_KEY_MISSING` をブロードキャスト、というパスが想定される。AOSP 根拠としては未確認。
- 除外した無関係なコードパス: タグ間差分未実行のため、除外判断は未完了。

## 差分解釈

| 確認した差分 | 解釈 | 挙動変更との関係 | 信頼度 |
| --- | --- | --- | --- |
| Android 17 タグ未取得のためソース差分は未確認 | 公式文書上は、追加された挙動 / 変更されたブロードキャストタイミング / API surface addition と読める | 自律的な再ペアリング、`EXTRA_PAIRING_CONTEXT`、`ACTION_KEY_MISSING` のタイミング変更が説明されている | 低 |

必須分類:
- Added behavior: 公式文書上は該当候補。自律的な再ペアリングと `EXTRA_PAIRING_CONTEXT` が追加される。
- Removed behavior: 未確認。手動復旧が不要になるケースはあるが、手動でのペアリング解除と再ペアリング自体が削除されるとは説明されていない。
- Changed condition / gate: 公式文書上は該当候補。セキュリティ鍵の置き換えと `ACTION_KEY_MISSING` ブロードキャストが、再ペアリングの成功 / 失敗条件に依存する。
- Changed default: 未確認。ペアリング情報消失時の復旧が、システム管理に寄る可能性がある。
- No behavior change found: 現時点では公式文書上の説明と矛盾するため候補ではないが、AOSP タグ間差分で確認が必要。

---

# 影響分析

## 影響を受ける可能性があるアプリ

- Bluetooth コンパニオンアプリ。
- 周辺機器メーカーのアプリ。
- wearable、audio 端末、IoT、health 端末向けアプリ。
- `ACTION_PAIRING_REQUEST` を受けて独自のペアリング UX / ガイダンスを行うアプリ。
- `ACTION_KEY_MISSING` を受けて、ユーザーに手動でのペアリング解除と再ペアリングを案内するアプリ。
- ペアリング情報消失時の復旧をアプリ側で検出し、OS の設定アプリでの手動操作を前提にしているアプリ。

## 影響を受けにくいアプリ

- Bluetooth ペアリング / ボンディングを直接扱わないアプリ。
- システムのペアリング UI に完全に委ねているアプリ。
- `ACTION_PAIRING_REQUEST` / `ACTION_KEY_MISSING` を監視していないアプリ。
- ペアリング情報消失時の復旧フローを持たないアプリ。

## 顧客向けリスク

- `ACTION_KEY_MISSING` を即時の失敗シグナルとして扱っていたアプリでは、Android 17 で通知タイミングが遅れる、または自律的な再ペアリングが成功した場合に通知されなくなる可能性がある。
- アプリが案内する手動でのペアリング解除と再ペアリングのフローが、システム管理の自律的な再ペアリング UI と重複する可能性がある。
- ペアリング要求を通常のペアリングと再ペアリング試行で区別しないアプリでは、誤った UX / logging / analytics になる可能性がある。
- 周辺機器側が再ペアリングフローや鍵更新条件に対応できない場合、ペアリング情報の遷移が不安定になる可能性がある。

---

# 対応候補

## 実装対応（Implementation）

- `ACTION_PAIRING_REQUEST` を扱うアプリは、`EXTRA_PAIRING_CONTEXT` を確認し、通常のペアリング要求とシステム起点の自律的な再ペアリング試行を区別する。
- `ACTION_KEY_MISSING` を扱うアプリは、Android 17 では自律的な再ペアリング失敗後のシグナルとして扱い、復旧が成功した場合には届かない可能性を前提にする。
- 手動でのペアリング解除と再ペアリングを案内する UX は、Android 17 ではシステム管理の通知 / ダイアログと重複しないよう見直す。
- セキュリティ上の影響が大きいアプリ / 周辺機器は、鍵の置き換えが再ペアリング成功と十分なセキュリティレベルを満たす場合に限定されることを前提にテスト計画を作る。
- 周辺機器 firmware とコンパニオンアプリの両方で、ペアリング情報の遷移を適切に扱う。

## 検証対応（Testing）

- Android 16 / targetSdkVersion 36 で、ペアリング情報消失時の復旧に関する基準挙動を確認する。
- Android 17 / targetSdkVersion 36 と Android 17 / targetSdkVersion 37 の両方で、ペアリング情報の消失 -> 自律的な再ペアリング -> 成功 / 失敗のフローを確認する。
- `ACTION_PAIRING_REQUEST` に `EXTRA_PAIRING_CONTEXT` が含まれるか、値が通常のペアリングと自律的な再ペアリングでどう変わるか確認する。
- `ACTION_KEY_MISSING` が自律的な再ペアリング失敗時だけブロードキャストされるか確認する。
- システム通知 / ダイアログとアプリ独自の復旧 UI が競合しないか確認する。
- 公式文書に従い、リモート側のペアリング情報の消失を次のいずれかで再現する。

```text
- 周辺機器側で bond information を手動削除する
- Android 端末の OS の設定アプリ > Connected devices で端末を手動でペアリング解除する
```

## 顧客説明候補（Customer Explanation）

Android 17 では、Bluetooth 周辺機器のペアリング情報が失われた場合、システムが自律的な再ペアリングによってバックグラウンドでペアリング情報の再確立を試行できます。多くのアプリではコード変更は不要ですが、Bluetooth コンパニオンアプリや周辺機器メーカーのアプリは、ペアリング要求の文脈、`ACTION_KEY_MISSING` のタイミング、システム管理の通知 / ダイアログとアプリ側の復旧 UI の整合を確認してください。

---

# 検証マトリクス

| 端末 OS | targetSdkVersion | アプリ条件 | 期待される挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | Bluetooth のペアリング情報の消失 | 基準挙動。手動でのペアリング解除と再ペアリングによる復旧フローを確認。 |
| Android 17 | 36 | ペアリング情報の消失 + 自律的な再ペアリング成功 | システムがバックグラウンドでペアリング情報を再確立し、`ACTION_KEY_MISSING` はブロードキャストされない可能性。AOSP 適用ゲートは未確認。 |
| Android 17 | 36 | ペアリング情報の消失 + 自律的な再ペアリング失敗 | `ACTION_KEY_MISSING` がブロードキャストされる可能性。 |
| Android 17 | 37 | ペアリング情報の消失 + コンパニオンアプリがペアリング関連ブロードキャストを監視 | targetSdkVersion 36 と同様の可能性。公式文書に targetSdkVersion 条件なし。 |
| Android 17 | 36 / 37 | `ACTION_PAIRING_REQUEST` を受信 | `EXTRA_PAIRING_CONTEXT` により、通常のペアリング / 自律的な再ペアリングを区別できることを確認。 |

---

# 未解決事項

- Android 17 AOSP タグ上で、自律的な再ペアリングはどの Bluetooth stack パスで実装されているか。
- `EXTRA_PAIRING_CONTEXT` の型、値、API level、public API surface。
- `ACTION_KEY_MISSING` ブロードキャストのタイミング実装と edge case。
- targetSdkVersion 適用ゲートまたは Compat Change ID が存在するか。
- システム管理の通知 / ダイアログの正確なフローとユーザー確認タイミング。
- セキュリティレベル比較と鍵の置き換え条件の実装。
- 周辺機器 firmware 側で必要な Bluetooth 挙動 / compatibility requirement。

---

# 人間の判断欄

最終優先度（Final Priority）:
- Human decision required

最終影響度（Final Severity）:
- Human decision required

顧客通知要否（Customer Communication Required）:
- Human decision required

リリース判断（Release Readiness）:
- Human decision required

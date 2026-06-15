# [Behavior Change Title] 調査レポート

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP tag

### Behavior Change 文書（Behavior Change Source）

Document:
<URL>

Section:
<Section Name>

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- OS_UPDATE_ALL_APPS / TARGET_SDK_37 / TARGET_SDK_37_CONDITIONAL / MAINLINE_OR_PLAY_SYSTEM_UPDATE / API_ADDITION_ONLY / UNKNOWN_NEEDS_MORE_EVIDENCE

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | Yes / No / Conditional / Unknown | |
| targetSdkVersion 37 以上が必要か | Yes / No / Conditional / Unknown | |
| 追加の実行時条件があるか | Yes / No / Unknown | |
| Compat Change ID が関係するか | Yes / No / Unknown | |

記入例:
- 主分類: `TARGET_SDK_37_CONDITIONAL`
- Android 17 に OS アップデートしただけで適用されるか: `No`
- targetSdkVersion 37 以上が必要か: `Yes`
- 追加の実行時条件があるか: `Yes。例: OTP を含む standard SMS、受信後 3 時間以内、対象外アプリではないこと`
- 根拠: `公式文書の "apps targeting Android 17..." と AOSP の targetSdkVersion gate`

### 調査日（Investigation Date）

YYYY-MM-DD

### 信頼度（Confidence）

- High
- Medium
- Low

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] OS update / all apps on Android 17 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 37 on Android 17+
- [ ] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [ ] Unknown / needs more evidence

必要な実行時条件（Required runtime conditions）:
- Android version:
- targetSdkVersion:
- Device/form factor:
- Permission/API/component condition:
- App state/process condition:

記入例:
- Android version: `Android 17 以上`
- targetSdkVersion: `37 以上`
- Device/form factor: `large screen (sw >= 600dp) のみ / 条件なし`
- Permission/API/component condition: `ContactsContract.Data data view を query する場合`
- App state/process condition: `foreground service 起動中のみ / 条件なし`

Compat framework:
- Change ID:
- Change name:
- Default state:
- Toggleable for testing:

分類信頼度（Classification confidence）:
- High
- Medium
- Low

分類根拠（Classification evidence）:
- Official documentation page:
- Original applicability statement:
- AOSP targetSdk gate:
- Compat framework entry:

記入例:
- Original applicability statement: `For apps targeting Android 17 (API level 37) and higher...`
- AOSP targetSdk gate: `if (appInfo.targetSdkVersion >= VANILLA_ICE_CREAM + 1) ...`
- Compat framework entry: `Change ID 123456789, @EnabledAfter(targetSdkVersion = 36)`

---

# エグゼクティブサマリー（Executive Summary）

3〜5行で説明。

顧客が最初に読む部分。

以下を含める。

- 何が変わったか
- 誰に影響するか
- 対応が必要か

---

# 公式ドキュメント確認（Original Documentation）

公式ドキュメントの該当箇所。

## 原文（Statement）

引用

## 解釈（Interpretation）

ドキュメントが言いたいことを平易に説明。

---

# 変更内容（What Changed）

Android 16 と Android 17 の差分。

- 変更点
- 新仕様
- 廃止仕様

## 適用条件（Applicability）

この変更がいつ適用されるかを OS 条件と targetSdkVersion 条件に分けて説明する。

### OS アップデート時の挙動（OS Update Behavior）

- Android 17 にアップデートしただけで適用されるか:
- targetSdkVersion に依存しない根拠:
- Android 16 以前での挙動:

### targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- targetSdkVersion 37 以上で適用されるか:
- Android 17 以外で targetSdkVersion 37 にした場合の挙動:
- opt-out / temporary override の有無:

### その他の条件（Other Conditions）

- device/form factor:
- permission:
- API usage:
- manifest attribute:
- component boundary:

---

# AOSP 調査（AOSP Investigation）

## 関連ファイル（Related Files）

- file1
- file2
- file3

## 確認したソース文脈（Source Context Reviewed）

AOSP のどの部分を見て、なぜ Behavior Change の根拠として採用したかを明記する。

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
|  |  |  |  |

必須記入項目（Required context）:
- Entry point / caller:
- Relevant class or service responsibility:
- Runtime path from app API / system event to changed code:
- Why unrelated code paths were excluded:

記入例:
- Entry point / caller: `ContentResolver.query()` -> `ContactsProvider2.query()`
- Relevant class or service responsibility: `ContactsContract.Data の data view に返す column を決める provider`
- Runtime path from app API / system event to changed code: `アプリの query が provider に入り、projection/filtering の条件分岐に到達する`
- Why unrelated code paths were excluded: `raw_contacts table の内部同期処理はアプリ公開 API の data view ではないため除外`

## 差分解釈（Diff Interpretation）

AOSP 差分をどのような差分として判断したかを明記する。

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
|  |  |  | High / Medium / Low |

必須分類（Required interpretation）:
- Added behavior:
- Removed behavior:
- Changed condition / gate:
- Changed default:
- No behavior change found:

記入例:
- Added behavior: `Android 17 で PII column を projection から除外する処理が追加された`
- Changed condition / gate: `targetSdkVersion >= 37 の場合だけ新処理に入る条件が追加された`
- Changed default: `設定値の default が false から true に変わった`
- No behavior change found: `該当 API surface の差分はあるが、実行時挙動の変更は確認できなかった`

## 事実（Evidence）

差分から分かった事実。

事実のみ。

推測禁止。

## 適用ゲート根拠（Applicability Gate Evidence）

targetSdkVersion、compat framework、OS version、device condition のいずれで制御されているかを確認する。

- targetSdkVersion gate:
- CompatChanges.isChangeEnabled / ChangeId:
- @EnabledAfter / @EnabledSince / default state:
- Build.VERSION / SDK_INT gate:
- DeviceConfig / resources config:
- Permission/AppOps gate:
- Manifest/property gate:
- No gate found:
- Gate conclusion:
- Reasoning from source context:

記入例:
- targetSdkVersion gate: `targetSdkVersion >= 37`
- CompatChanges.isChangeEnabled / ChangeId: `CompatChanges.isChangeEnabled(RESTRICT_PII_DATA_VIEW, uid)`
- @EnabledAfter / @EnabledSince / default state: `@EnabledAfter(targetSdkVersion = 36)。targetSdkVersion 37 以上で default enabled`
- No gate found: `targetSdkVersion gate は見つからない。OS version 上の実装差分として全アプリに適用される可能性が高い`
- Gate conclusion: `Android 17 以上かつ targetSdkVersion 37 以上で適用`

---

# 影響分析（Impact Analysis）

## 影響を受けるアプリ（Affected Apps）

影響を受けるアプリ例。

## 影響を受けないアプリ（Non-Affected Apps）

影響を受けないケース。

---

# 顧客影響（Customer Impact）

顧客説明用。

## 影響度（Impact Level）

- Critical
- High
- Medium
- Low

※ 仮評価。最終判断は人間が行う。

## ビジネス影響（Business Impact）

- ユーザー影響
- 運用影響
- 開発影響

---

# サービス影響例（Service Impact Examples）

このセクションは、公式文書と AOSP evidence から導いた「起こりうる影響例」を記録する。
特定サービスで実際に発生確認した事実ではない。

実サービス名を出す場合は、repository owner または service owner が確認済みのものだけにする。
それ以外は「ログイン OTP」「Bluetooth プリンター連携」「連絡先 CRM 同期」のような一般化した service / feature pattern として書く。

## 例1（Example 1）: <サービス / 機能パターン名>

- 対象サービス例:
- 影響を受ける実装パターン:
- 発生条件:
- ユーザーに見える症状:
- 開発・運用への影響:
- 推奨対応候補:
- 根拠:
- Confidence（信頼度）:
- 注意:

## 例2（Example 2）: <サービス / 機能パターン名>

- 対象サービス例:
- 影響を受ける実装パターン:
- 発生条件:
- ユーザーに見える症状:
- 開発・運用への影響:
- 推奨対応候補:
- 根拠:
- Confidence（信頼度）:
- 注意:

---

# 対応候補（Required Actions）

## 必須対応（Must）

必須対応。

## 推奨対応（Recommended）

推奨対応。

## 任意対応（Optional）

余裕があれば。

---

# 検証方法（Verification Method）

変更を確認する方法。

## 検証マトリクス（Matrix）

最低限、以下の組み合わせで再現条件を分ける。

| 端末 OS（Device OS） | targetSdkVersion | Compat flag | 期待挙動（Expected behavior） |
| --- | --- | --- | --- |
| Android 16 | 36 | default | |
| Android 17 | 36 | default | |
| Android 17 | 37 | default | |
| Android 17 | 36 | force-enabled if available | |
| Android 17 | 37 | force-disabled if available | |

記入例:
- `Android 17 / targetSdkVersion 36 / default`: 旧挙動が維持される
- `Android 17 / targetSdkVersion 37 / default`: 新挙動が適用される
- `Android 17 / targetSdkVersion 37 / force-disabled if available`: compat 無効化で旧挙動に戻るか確認する

## 手順（Steps）

- targetSdk変更:
- compat framework command:
- テスト方法:
- 再現手順:
- 期待結果:

---

# 結論（Conclusion）

1〜3行。

顧客へ説明する際の結論。

---

# 参照（References）

## ドキュメント（Documentation）

- URL

## AOSP

- File
- File
- File

# CompanionDeviceManager による Bluetooth bond 削除 API

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

From:
- `android-15.0.0_r36`

To:
- `android-16.0.0_r4`

Previous targetSdkVersion:
- 35

Target targetSdkVersion:
- 36

### Behavior Change 文書（Behavior Change Source）

Document:
- https://developer.android.com/about/versions/16/behavior-changes-16#bond-removal-api

Section:
- New way to remove bluetooth bond

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `API_ADDITION_ONLY`

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 16 に OS アップデートしただけで既存アプリの挙動が変わるか | No | API を呼ばない既存アプリへ自動適用される処理ではない。 |
| targetSdkVersion 36 以上が実行時ゲートか | No evidence | AOSP の API / service 実装に targetSdkVersion 判定はない。公式文書は Android 16 を対象にするアプリ向けの新 API として案内する。 |
| 追加条件があるか | Yes | 有効な CDM association、device MAC address、`BLUETOOTH_CONNECT`、Bluetooth 利用可能状態が必要。 |
| Compat Change ID があるか | No | この API 専用の compat change は確認できない。 |

### 調査日（Investigation Date）

- 2026-08-22

### 信頼度（Confidence）

- Medium

Android 16 での公開 API と実装経路は公式文書および AOSP で確認できた。一方、比較元タグにも `@FlaggedApi` 付きの source / API surface が存在するため、Android 15 製品 SDK での公開可否はタグ差分だけでは断定せず、Android 15 / 16 SDK の `android.jar` による追加確認を残す。

## エグゼクティブサマリー

Android 16 では、Companion Device Manager（CDM）で管理している Bluetooth 機器について、アプリが `CompanionDeviceManager.removeBond(associationId)` を使って bond 削除を要求できる。これは既存アプリへ自動適用される挙動変更ではなく、CDM association を持つアプリが採用できる API である。

呼び出しは非同期で、戻り値は削除開始要求の成否を示す。完了結果は `BluetoothDevice.ACTION_BOND_STATE_CHANGED` で監視する。association が呼び出し元アプリのものではない、device MAC address がない、`BLUETOOTH_CONNECT` がない、といった場合は正常な削除経路に入らない。

## 公式ドキュメント確認（Original Documentation）

### 原文の要点（Statement）

公式文書は、Android 16 を対象にするアプリが CDM association で管理される Bluetooth device を、新しい `CompanionDeviceManager.removeBond(int)` API で unpair できると説明する。また、bond state の変化は `ACTION_BOND_STATE_CHANGED` で監視するよう案内している。

### 解釈（Interpretation）

- 新 API を呼ばないアプリに強制される変更ではない。
- `associationId` は任意の Bluetooth device を指定する識別子ではなく、呼び出し元が管理できる CDM association を指す。
- `true` は bond 削除完了ではなく、非同期処理を開始できたことを表す。
- 既存の接続切断、association 削除、bond 削除は同一操作ではないため、アプリの状態管理で区別する必要がある。

## 適用条件（Applicability）

- Android version: Android 16 以上で公開 API として採用する。
- targetSdkVersion: 公式ページは Android 16 target 向けとして掲載するが、AOSP runtime path に targetSdkVersion gate は確認できない。
- Permission: `BLUETOOTH_CONNECT`。
- Association: 呼び出し元 package / user が管理できる association であること。
- Device data: association に Bluetooth MAC address があること。
- API usage: アプリが明示的に `removeBond(associationId)` を呼ぶこと。
- Compat framework: 専用 Change ID なし。

## 変更内容（What Changed）

Android 16 の開発者向け API として、CDM association を起点に Bluetooth bond 削除を要求する公開経路が案内された。service は association ownership と device address を確認し、対象 `BluetoothDevice` の `removeBond()` を呼ぶ。

比較元 `android-15.0.0_r36` にも同じ method と service path が `@FlaggedApi` を伴って存在する。そのため、AOSP source の追加差分ではなく、Android 16 SDK で開発者が利用する API の公開・採用機会として扱う。既存挙動の変更とは分類しない。

## AOSP 調査（AOSP Investigation）

### AOSP 証拠ワークスペース（AOSP Evidence Workspaces）

| AOSP project | Official remote URL | Checkout path | Working tree | From tag / resolved commit | To tag / resolved commit | Comparison command | Dirty risk / limitations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `platform/frameworks/base` | `https://android.googlesource.com/platform/frameworks/base` | `frameworks-base/` | Clean | `android-15.0.0_r36` / `396d32905ded85c082232bc510b525c9e372e585` | `android-16.0.0_r4` / `45034f0663f960d9ee5fb0a101a4732b71f6e2f4` | `git -C frameworks-base diff --no-renames android-15.0.0_r36 android-16.0.0_r4 -- core/java/android/companion services/companion core/api/current.txt` | なし。明示タグ比較のため working tree は根拠に含めない。Android 15 製品 SDK の flag 最終状態は別途確認が必要。 |

### 関連ファイル（Related Files）

- `core/java/android/companion/CompanionDeviceManager.java`
- `core/java/android/companion/ICompanionDeviceManager.aidl`
- `services/companion/java/com/android/server/companion/CompanionDeviceManagerService.java`
- `core/java/android/companion/flags.aconfig`
- `core/api/current.txt`

### 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル | Android 15 baseline | Android 16 behavior | 関連性 |
| --- | --- | --- | --- |
| `CompanionDeviceManager.removeBond(int)` | `@FlaggedApi` 付きで source / `current.txt` に存在 | `@FlaggedApi` 付きで存在し、公式 Android 16 文書が public API として案内 | app-facing entry point。 |
| `ICompanionDeviceManager.removeBond(...)` | binder method が存在 | binder method が存在 | framework API から system service への境界。 |
| `CompanionDeviceManagerService.removeBond(...)` | association ownership と MAC address を確認して `BluetoothDevice.removeBond()` を呼ぶ | 同じ主要経路 | permission / association / device 条件の根拠。 |
| `ACTION_BOND_STATE_CHANGED` | bond state の監視 signal | 非同期完了を監視する signal | 公式文書の結果監視方法。 |

- Entry point / caller: アプリの `CompanionDeviceManager.removeBond(associationId)`。
- Runtime path: framework API -> binder -> `CompanionDeviceManagerService` -> association caller check -> MAC address 解決 -> `BluetoothDevice.removeBond()`。
- Excluded paths: CDM `disassociate()` は association record の削除であり Bluetooth bond 削除そのものではない。Android 16 の remote bond loss 自動処理も、アプリが明示的に呼ぶ本 APIとは別項目である。

### 差分解釈（Diff Interpretation）

| 確認結果 | 解釈 | Behavior Change との関係 | 信頼度 |
| --- | --- | --- | --- |
| 両タグに method / binder / service path が存在 | No behavior change found | source 実装の新規追加ではなく Android 16 SDK の API 公開・採用 guidance とみなす | High |
| Android 16 公式文書が target 16 アプリ向けに API を案内 | API availability / adoption change | `API_ADDITION_ONLY` の根拠 | High |
| runtime path に targetSdkVersion 判定なし | No target gate found | targetSdkVersion 36 で既存挙動が自動変更される項目ではない | High |
| association ownership / address / permission check がある | Conditional API operation | 利用可能な対象を CDM 管理機器へ限定 | High |

## 事実・観察・仮説・結論

### 事実（Facts）

- 公式文書は `CompanionDeviceManager.removeBond(int)` を Android 16 向けの新しい bond 削除 API として案内する。
- API は `BLUETOOTH_CONNECT` を要求し、非同期完了は `ACTION_BOND_STATE_CHANGED` で監視する。
- system service は caller が association を管理できることと device MAC address を確認する。
- 比較元・比較先の両 AOSP タグに `@FlaggedApi` 付き method と service implementation が存在する。
- 専用の targetSdkVersion gate / Compat Change ID は確認できない。

### 観察（Observations）

- AOSP tag 間の source 追加では API の公開時期を説明できず、公式 Android 16 SDK guidance と AOSP 実装を組み合わせる必要がある。
- bond 削除と CDM association 削除を同じ状態遷移として扱うと、アプリ側の device 管理が不整合になる可能性がある。

### 仮説（Hypotheses）

- Android 15 tag の `@FlaggedApi` は開発中 API surface を含むため、一般アプリが利用した Android 15 製品 SDK の公開状態とは一致しない可能性がある。これは SDK artifact で追加確認する。

### 結論（Conclusions）

- 主分類は `API_ADDITION_ONLY`。
- 既存アプリの強制移行ではなく、CDM で Bluetooth device を管理するアプリの実装選択肢である。
- 採用時は association、bond、接続状態を分離し、戻り値と `ACTION_BOND_STATE_CHANGED` の両方を扱う。
- Confidence は Medium。Android 16 の利用方法は明確だが、Android 15 製品 SDK との公開差の説明には SDK artifact 確認が残る。

## 対応候補と検証方法

```kotlin
// 移行例。既存の repository / use case / state management に合わせて調整する。
val started = companionDeviceManager.removeBond(associationId)
if (!started) {
    // 即時エラー。完了通知ではない。
}
// 完了は ACTION_BOND_STATE_CHANGED を既存の監視層で受け取る。
```

確認項目:
- associationId が現在の package / user の association か。
- association に Bluetooth MAC address があるか。
- `BLUETOOTH_CONNECT` の grant 状態。
- 戻り値 `false` と、開始後の `BOND_NONE` / failure を区別できるか。
- bond 削除後も CDM association を保持するか、別操作で削除するか。

## Human Decision

- Status: Pending Human Decision
- 最終優先度、採用可否、顧客説明優先度は repository owner が決定する。
- [Android 16 Decision Log](../../../decisions/DECISION_LOG.md)

## 関連成果物

- [1ページ要約](../../../summaries/target/connectivity/new-way-to-remove-bluetooth-bond-summary.md)
- [Connectivity / Security ケース別ガイド](../../case-guides/connectivity-and-security.md#bluetooth-bond-loss--encryption--unpair)

---

## 再検証記録（2026-08-22）

### 調査日（Investigation Date）

- 2026-08-22

### 公式ドキュメント再確認（Original Documentation Recheck）

- Android 16 の all-apps / target Behavior Change ページを再取得し、このレポートが参照する公式 section の掲載と適用範囲を再確認した。
- 公式ページの最終更新表示: all-apps: 2026-08-14 UTC / target: 2026-08-17 UTC。
- Android 16 compat framework 一覧も 2026-08-22 に再取得した。
- 既存の引用は短い要約として扱い、適用条件は公式ページ種別と AOSP gate の両方で再評価した。

### AOSP 証拠ワークスペース（AOSP Evidence Workspaces）

| AOSP project | Official remote URL | Checkout path | Working tree | From tag / resolved commit | To tag / resolved commit | Comparison command | Dirty risk / limitations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `platform/frameworks/base` | `https://android.googlesource.com/platform/frameworks/base` | `frameworks-base/` | Clean | `android-15.0.0_r36` / `396d32905ded85c082232bc510b525c9e372e585` | `android-16.0.0_r4` / `45034f0663f960d9ee5fb0a101a4732b71f6e2f4` | `git -C frameworks-base diff --no-renames --name-only android-15.0.0_r36 android-16.0.0_r4` | なし。明示タグ比較のため working tree の内容は根拠に含めない。 |

### ソース文脈・差分解釈の再確認（Source Context Reviewed / Diff Interpretation）

- 各 official remote で Android 15 / 16 の最新通常リリースタグが `android-15.0.0_r36` / `android-16.0.0_r4` のままであることを確認した。
- 上表の project-level `--name-only` 比較を再実行し、既存本文の path / symbol 別 source context、gate、追加・削除・条件変更・既定値変更・差分なしの解釈を再確認した。
- タグと解決済み commit が既存調査の比較対象から変わっていないため、本文の evidence record を別タグへ機械的に置換していない。
- 実機 Observed は新規実施していない。既存の「未実施」「未確認」および不足根拠はそのまま維持した。

### 事実（Facts）

- `android-15.0.0_r36` と `android-16.0.0_r4` は 2026-08-22 時点の最新通常リリースタグである。
- 上表に再検証時の working tree 状態を記録し、official remote、両タグ、解決済み commit を確認した。展開中または dirty の working tree は根拠に使用していない。
- 公式 section と AOSP evidence の比較 pair は一致している。

### 観察（Observations）

- 最新タグが変わっていないため、今回の再検証で既存の source diff 解釈を変更する新しい AOSP tag evidence は生じなかった。
- report 内に残る Medium / Low confidence、OEM / Mainline / QPR 条件、未確認の module enforcement は解消したものとして扱わない。

### 仮説（Hypotheses）

- 新しい仮説は追加しない。既存本文で仮説または可能性として記載した事項は、実機・製品 build・未確認 module の evidence が得られるまで事実へ昇格しない。

### 結論（Conclusions）

- 既存本文の主分類、confidence、対応候補を維持する。既存の不足根拠がある場合はその制約も維持する。
- 全件再検証の横断記録は [`android16/analysis/REVALIDATION_2026-08-22.md`](../../../analysis/REVALIDATION_2026-08-22.md) を参照する。

### Human Decision

- この再検証では最終 priority、severity、release readiness、顧客説明優先度を変更していない。
- 人間の判断は [Android 16 Decision Log](../../../decisions/DECISION_LOG.md) を正とする。

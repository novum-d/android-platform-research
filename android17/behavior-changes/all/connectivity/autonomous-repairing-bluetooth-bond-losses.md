# Autonomous re-pairing for Bluetooth bond losses

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

比較元:
- android-16.0.0_r4

比較先:
- TBD: Android 17 AOSP tag

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

### Behavior Change 文書（Behavior Change Source）

文書:
- https://developer.android.com/about/versions/17/behavior-changes-all

関連文書:
- https://developer.android.com/reference/android/bluetooth/BluetoothDevice#ACTION_PAIRING_REQUEST
- https://developer.android.com/reference/android/bluetooth/BluetoothDevice#EXTRA_PAIRING_CONTEXT
- https://developer.android.com/reference/android/bluetooth/BluetoothDevice#ACTION_KEY_MISSING
- https://developer.android.com/guide/topics/connectivity/bluetooth
- https://developer.android.com/develop/connectivity/bluetooth

セクション:
- Autonomous re-pairing for Bluetooth bond losses

ページ種別:
- Behavior changes: all apps

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- 公式文書は Android 17 の `Behavior changes: all apps` ページにこの項目を掲載している。
- 原文は、Android 17 が Bluetooth bond loss を自動的に解決する system-level enhancement として autonomous re-pairing を導入すると説明している。
- 原文は、以前は bond loss 時に users が Settings から手動で unpair / re-pair する必要があったが、Android 17 では system が background で bond を再確立できると説明している。
- 原文には targetSdkVersion 条件は記載されていない。
- ただし、local `frameworks-base` に Android 17 AOSP tag がないため、Bluetooth stack / pairing intent / bond state / key update / notification UI / compat framework entry は未確認である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 可能性は高いが条件付き、かつ未検証 | 公式文書は all apps ページに掲載し、targetSdkVersion 条件を示していない。AOSP gate 未確認。 |
| targetSdkVersion 37 以上が必要か | 不要と考えられるが未検証 | 原文に targetSdkVersion 条件はない。AOSP targetSdkVersion gate 未確認。 |
| 追加の実行時条件があるか | ある | Bluetooth peripheral bond loss が発生し、system が autonomous re-pairing を試行する場合。companion app が pairing / key missing broadcast を扱う場合は特に確認が必要。 |
| Compat Change ID が関係するか | 未確認 | Android 17 tag と compat framework evidence が未確認。 |

### 調査日（Investigation Date）

2026-06-15

### 信頼度（Confidence）

- Low

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] targetSdkVersion に関係なく Android 17 の全アプリへ適用
- [ ] Android 17 以上かつ targetSdkVersion 37 以上で適用
- [ ] targetSdkVersion 37 以上かつ追加の実行時条件を満たす場合に適用
- [ ] Mainline / Google Play system update に依存
- [ ] API 追加のみであり、挙動変更ではない
- [x] 未確認 / 追加 evidence が必要

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 以上。AOSP tag 未取得のため実装上の OS gate は未確認。
- targetSdkVersion: 公式文書上は条件なし。AOSP targetSdkVersion gate 未確認。
- Device/form factor: Bluetooth peripheral と bond / pairing する Android device。
- Permission/API/component condition: Bluetooth bonding / pairing、`BluetoothDevice.ACTION_PAIRING_REQUEST`、`BluetoothDevice.EXTRA_PAIRING_CONTEXT`、`BluetoothDevice.ACTION_KEY_MISSING`、system pairing UI、companion device / peripheral manufacturer flow。
- App state/process condition: companion app または peripheral app が pairing / key-missing broadcast を監視する、または manual unpair / re-pair recovery flow を案内している場合。

Compat framework:
- Change ID: 未確認
- 変更名: 未確認
- 既定状態: 未確認
- テスト時に切り替え可能か: 未確認

分類信頼度（Classification confidence）:
- Low

分類根拠（Classification evidence）:
- 公式ドキュメントページ: `behavior-changes-all`
- 検証対象の適用条件文: Android 17 は autonomous re-pairing を導入し、bond loss 時に system が background で bond を再確立できる。Bluetooth stack の intent / key update / UI timing に変更がある。
- AOSP targetSdk gate: 未確認。local `frameworks-base` に `android-17*` tag がない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# エグゼクティブサマリー（Executive Summary）

Android 17 では、Bluetooth bond loss を system が自動的に回復する autonomous re-pairing が導入される。従来は bond が失われると、users が Settings で peripheral を unpair し、再度 pair する必要があったが、Android 17 では system が background で bond の再確立を試行できる。

多くの app では code change は不要とされている。ただし、Bluetooth companion app、peripheral manufacturer app、wearable / audio / IoT / health device app など、pairing や key missing broadcast を扱う app は、Bluetooth stack の挙動変更を確認する必要がある。`ACTION_PAIRING_REQUEST` には `EXTRA_PAIRING_CONTEXT` が追加され、standard pairing request と autonomous system-initiated re-pairing attempt を区別できる。`ACTION_KEY_MISSING` は autonomous re-pairing が失敗した場合だけ broadcast される。

現時点では local `frameworks-base` に Android 17 AOSP tag がなく、Bluetooth stack の実装、API surface、targetSdkVersion gate、compat Change ID を確認できない。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE`、信頼度は Low とする。

---

# 公式ドキュメント確認

## 原文（Statement）

ページタイトル:
- Behavior changes: all apps

ページ URL:
- https://developer.android.com/about/versions/17/behavior-changes-all

ページ種別:
- all apps

セクションタイトル:
- Autonomous re-pairing for Bluetooth bond losses

検証対象の原文:
- Android 17 は Bluetooth bond loss を自動的に解決する system-level enhancement として autonomous re-pairing を導入する。
- 以前は bond loss 時に users が Settings で peripheral を手動 unpair / re-pair する必要があった。
- Android 17 では system が background で bond を再確立できる。
- `ACTION_PAIRING_REQUEST` は `EXTRA_PAIRING_CONTEXT` extra を含むようになり、standard pairing request と autonomous system-initiated re-pairing attempt を区別できる。
- re-pairing が成功し、新しい connection が previous bond と同等以上の security level を満たす場合にのみ existing security keys が置き換えられる。
- `ACTION_KEY_MISSING` intent は autonomous re-pairing attempt が失敗した場合だけ broadcast される。
- system は notifications / dialogs によって re-pairing を管理し、users は reconnection を認識できるよう confirmation を求められる。

## 解釈（Interpretation）

この変更は、Bluetooth bond loss recovery の ownership を user / app-guided manual recovery から system-managed autonomous re-pairing に寄せる挙動変更である。app 側の主要な観点は、pairing request の context 判定、key missing broadcast timing の変化、security key update 条件、system-managed notification / dialog との整合である。

顧客向けには「全 Bluetooth app が必ず変更必要」ではなく、「多くの app では code change は不要だが、companion app や peripheral manufacturer app は bond transition を検証する必要がある」と説明する。

---

# 変更内容（What Changed）

公式文書上の変更点:
- Android 17 で autonomous re-pairing が導入される。
- bond loss 後、system が background で bond を再確立できる。
- `ACTION_PAIRING_REQUEST` に `EXTRA_PAIRING_CONTEXT` が追加され、pairing request の context を区別できる。
- security keys は、re-pairing 成功かつ previous bond と同等以上の security level を満たす場合にのみ置き換えられる。
- `ACTION_KEY_MISSING` は autonomous re-pairing 失敗時だけ broadcast される。
- system-managed notification / dialog によって users に re-pairing attempt が提示される。
- peripheral device manufacturers と companion app developers は bond transition を検証する必要がある。

AOSP で未確認の点:
- autonomous re-pairing の trigger 条件と retry / timeout policy。
- `EXTRA_PAIRING_CONTEXT` の値、型、API surface、standard pairing と autonomous re-pairing の区別方法。
- `ACTION_KEY_MISSING` broadcast timing の実装。
- security key replacement の security level 判定。
- system notification / dialog の UI flow と user confirmation requirement。
- targetSdkVersion gate の有無。
- compat framework Change ID と default state。

## 適用条件（Applicability）

この変更がいつ適用されるかを OS 条件と targetSdkVersion 条件に分けて説明する。

### OS アップデート時の挙動（OS Update Behavior）

- Android 17 に OS アップデートしただけで適用されるか: 公式文書上は Yes / Conditional。all apps ページに掲載され、targetSdkVersion 条件は示されていない。ただし AOSP gate 未確認。
- targetSdkVersion に依存しない根拠: 原文に targetSdkVersion 条件がない。
- Android 16 以前での挙動: bond loss 時は users が Settings で manual unpair / re-pair する必要があったと公式文書が説明している。Android 16 baseline の Bluetooth stack behavior は AOSP diff 未確認。

### targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- targetSdkVersion 37 以上で適用されるか: 公式文書上、targetSdkVersion 37 は必要条件ではない。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: Unknown。公式文書は Android 17 platform behavior として説明している。
- opt-out / temporary override の有無: 未確認。公式文書には app-level opt-out は記載されていない。

### その他の条件（Other Conditions）

- device state: Bluetooth peripheral の bond loss が発生する。
- app / peripheral role: companion app、peripheral manufacturer app、wearable / audio / IoT / health device app など、pairing / bond transition を扱う app。
- broadcast usage: app が `ACTION_PAIRING_REQUEST` または `ACTION_KEY_MISSING` を扱う。
- user flow: app が users に manual unpair / re-pair を案内している場合、Android 17 では system-managed recovery と UI が先に入る可能性がある。
- security condition: key replacement は successful re-pairing と sufficient security level を満たす場合に限定される。

---

# AOSP 調査（AOSP Investigation）

## checkout 状態（Checkout Status）

確認コマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list 'android-17*'
```

結果:
- `frameworks-base` の `status --short` は空で、dirty working tree は確認されなかった。
- `android-16.0.0_r4` tag は存在する。
- `android-17*` tag は local checkout に存在しない。

根拠上の制約:
- Android 17 AOSP tag が local `frameworks-base` にないため、`android-16.0.0_r4` と Android 17 tag の明示的な source diff は実行できない。
- Bluetooth stack は `frameworks-base` 以外の `packages/modules/Bluetooth` などに実装がある可能性が高いため、Android 17 tag 入手後は該当 project も確認する必要がある。
- そのため、local working tree や未確定 branch を platform evidence として扱わない。
- 本レポートの AOSP-backed conclusion は Low confidence に留める。

## 関連ファイル（Related Files）

Android 17 AOSP tag 未取得のため、tag diff に基づく related files は未確定。

Android 17 tag 公開後に確認すべき候補:
- `core/java/android/bluetooth/BluetoothDevice.java`
- `packages/modules/Bluetooth/` 以下の bond / pairing / security manager path
- Bluetooth pairing UI / notification を扱う system UI または Bluetooth module path
- `ACTION_PAIRING_REQUEST` broadcast generation path
- `EXTRA_PAIRING_CONTEXT` API surface / `current.txt`
- `ACTION_KEY_MISSING` broadcast generation path
- security key update / link key replacement path
- compat framework 定義ファイル内の Bluetooth autonomous re-pairing 関連 Change ID

## 確認したソース文脈（Source Context Reviewed）

AOSP tag diff は未実行。以下は公式文書から見た確認予定の source context であり、AOSP evidence ではない。

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| Bluetooth bond loss detection path | 未確認 | bond loss 後に autonomous re-pairing を試行すると公式文書が説明 | system-managed recovery の trigger point になるため |
| `BluetoothDevice.ACTION_PAIRING_REQUEST` | 未確認 | `EXTRA_PAIRING_CONTEXT` を含むと公式文書が説明 | app が pairing context を区別する developer-visible API であるため |
| `BluetoothDevice.ACTION_KEY_MISSING` | 未確認 | autonomous re-pairing 失敗時のみ broadcast と公式文書が説明 | companion app の error handling timing に影響するため |
| security key update path | 未確認 | successful re-pairing かつ previous bond と同等以上の security level の場合のみ keys を置き換える | peripheral security / bonding continuity の根拠になるため |
| system pairing UI / notification path | 未確認 | system が notifications / dialogs で user confirmation を扱う | user-visible flow と app-guided recovery flow の衝突確認に必要なため |
| compat framework entry | 未確認 | targetSdkVersion gate の有無は不明 | all apps 型か targetSdkVersion gate 型かの確定に必要なため |

必須記入項目:
- Entry point / caller: 未確認。想定される entry point は Bluetooth stack が bond / key missing condition を検出 -> autonomous re-pairing attempt -> pairing request broadcast / system UI -> key update or `ACTION_KEY_MISSING` failure broadcast。
- Relevant class or service responsibility: bond state management、pairing request context、security key update、failure notification、system pairing UI。
- Runtime path from app API / system event to changed code: peripheral bond loss -> system が autonomous re-pairing を開始 -> user confirmation UI / pairing context を含む broadcast -> success なら security keys を条件付き更新、failure なら `ACTION_KEY_MISSING` を broadcast、という path が想定される。AOSP evidence としては未確認。
- Why unrelated code paths were excluded: tag diff 未実行のため、除外判断は未完了。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
| Android 17 tag 未取得のため source diff 未確認 | 公式文書上は added behavior / changed broadcast timing / API surface addition と読める | autonomous re-pairing、`EXTRA_PAIRING_CONTEXT`、`ACTION_KEY_MISSING` timing change が説明されている | Low |

必須分類:
- Added behavior: 公式文書上は該当候補。autonomous re-pairing と `EXTRA_PAIRING_CONTEXT` が追加される。
- Removed behavior: 未確認。manual recovery が不要になるケースがあるが、manual unpair / re-pair 自体が削除されるとは説明されていない。
- Changed condition: 公式文書上は該当候補。security key replacement と `ACTION_KEY_MISSING` broadcast が re-pairing success / failure 条件に依存する。
- Changed default: 未確認。bond loss recovery が system-managed に寄る可能性がある。
- No behavior change: 現時点では公式文書上の説明と矛盾するため候補ではないが、AOSP tag diff で確認が必要。

---

# 影響分析（Impact Analysis）

## 影響を受ける可能性があるアプリ（Potentially Affected Apps）

- Bluetooth companion apps。
- peripheral manufacturer apps。
- wearable、audio device、IoT、health device app。
- `ACTION_PAIRING_REQUEST` を受けて独自 pairing UX / guidance を行う app。
- `ACTION_KEY_MISSING` を受けて users に manual unpair / re-pair を案内する app。
- bond loss recovery を app 側で検出し、Settings での手動操作を前提にしている app。

## 影響を受けにくいアプリ（Less Likely Affected）

- Bluetooth pairing / bonding を直接扱わない app。
- system pairing UI に完全に委ねている app。
- `ACTION_PAIRING_REQUEST` / `ACTION_KEY_MISSING` を監視していない app。
- bond loss recovery flow を持たない app。

## 顧客向けリスク（Customer-facing Risk）

- `ACTION_KEY_MISSING` を immediate failure signal として扱っていた app では、Android 17 で通知 timing が遅れる、または successful autonomous re-pairing 時に通知されなくなる可能性がある。
- app-guided manual unpair / re-pair flow が、system-managed autonomous re-pairing UI と重複する可能性がある。
- pairing request を standard pairing と re-pairing attempt で区別しない app では、誤った UX / logging / analytics になる可能性がある。
- peripheral 側が re-pairing flow や key update condition に対応できない場合、bond transition が不安定になる可能性がある。

---

# 対応候補（Recommended Action Candidates）

## 実装対応（Implementation）

- `ACTION_PAIRING_REQUEST` を扱う app は、`EXTRA_PAIRING_CONTEXT` を確認し、standard pairing request と autonomous system-initiated re-pairing attempt を区別する。
- `ACTION_KEY_MISSING` を扱う app は、Android 17 では autonomous re-pairing failure 後の signal として扱い、successful recovery 時には届かない可能性を前提にする。
- manual unpair / re-pair を案内する UX は、Android 17 では system-managed notification / dialog と重複しないよう見直す。
- security-sensitive app / peripheral は、key replacement が successful re-pairing と sufficient security level に限定されることを前提に test plan を作る。
- peripheral firmware / companion app の両方で bond transition を graceful に扱う。

## 検証対応（Testing）

- Android 16 / targetSdkVersion 36 で bond loss recovery baseline を確認する。
- Android 17 / targetSdkVersion 36 と Android 17 / targetSdkVersion 37 の両方で、bond loss -> autonomous re-pairing -> success / failure flow を確認する。
- `ACTION_PAIRING_REQUEST` に `EXTRA_PAIRING_CONTEXT` が含まれるか、値が standard pairing と autonomous re-pairing でどう変わるか確認する。
- `ACTION_KEY_MISSING` が autonomous re-pairing failure 時だけ broadcast されるか確認する。
- system notification / dialog と app 独自 recovery UI が競合しないか確認する。
- 公式文書に従い、remote bond loss を次のいずれかで simulate する。

```text
- peripheral device 側で bond information を手動削除する
- Android device の Settings > Connected devices で device を手動 unpair する
```

## 顧客説明候補（Customer Explanation）

Android 17 では、Bluetooth peripheral の bond が失われた場合、system が autonomous re-pairing によって background で bond の再確立を試行できます。多くの app では code change は不要ですが、Bluetooth companion app や peripheral manufacturer app は、pairing request の context、`ACTION_KEY_MISSING` の timing、system-managed notification / dialog と app 側 recovery UI の整合を確認してください。

---

# 検証マトリクス（Verification Matrix）

| Device OS | targetSdkVersion | App condition | Expected behavior |
| --- | --- | --- | --- |
| Android 16 | 36 | Bluetooth bond loss | baseline。manual unpair / re-pair recovery flow を確認。 |
| Android 17 | 36 | bond loss + autonomous re-pairing success | system が background で bond を再確立し、`ACTION_KEY_MISSING` は broadcast されない可能性。AOSP gate 未確認。 |
| Android 17 | 36 | bond loss + autonomous re-pairing failure | `ACTION_KEY_MISSING` が broadcast される可能性。 |
| Android 17 | 37 | bond loss + companion app listens to pairing broadcasts | targetSdkVersion 36 と同様の可能性。公式文書に targetSdkVersion 条件なし。 |
| Android 17 | 36 / 37 | `ACTION_PAIRING_REQUEST` received | `EXTRA_PAIRING_CONTEXT` により standard pairing / autonomous re-pairing を区別できることを確認。 |

---

# 未解決事項（Open Questions）

- Android 17 AOSP tag 上で、autonomous re-pairing はどの Bluetooth stack path で実装されているか。
- `EXTRA_PAIRING_CONTEXT` の型、値、API level、public API surface。
- `ACTION_KEY_MISSING` broadcast timing の実装と edge case。
- targetSdkVersion gate または compat Change ID が存在するか。
- system-managed notification / dialog の exact flow と user confirmation timing。
- security level comparison と key replacement condition の実装。
- peripheral firmware 側で必要な Bluetooth behavior / compatibility requirement。

---

# 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

最終影響度:
- 人間による判断が必要

顧客通知要否（Customer Communication Required）:
- 人間による判断が必要

リリース判断:
- 人間による判断が必要

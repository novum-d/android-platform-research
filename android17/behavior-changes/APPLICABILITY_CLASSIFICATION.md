# Android 17 適用条件分類（Applicability Classification）

このファイルは、Android 17 Behavior Changes を「OSアップデート時に自動的に適用される差分」と「targetSdkVersion 37 を上げた時に適用される差分」に分類するための基準を定義する。

## バージョンスコープ（Version Scope）

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP tag

## 公式ドキュメント参照元（Official Documentation Sources）

Primary documentation:
- OS update / all apps: https://developer.android.com/about/versions/17/behavior-changes-all
- targetSdkVersion 37+: https://developer.android.com/about/versions/17/behavior-changes-17

Compat framework:
- TBD: Android 17 compatibility framework page, if published

## 分類ラベル（Classification Labels）

Use exactly one primary label per finding.

### OS_UPDATE_ALL_APPS

公式文書が「targetSdkVersion に関係なく Android 17 上の全アプリに適用される」と説明している場合に使う。

必要な根拠:
- Behavior Change source is `behavior-changes-all`, or equivalent official statement exists.
- AOSP evidence does not show a targetSdkVersion 37 gate, once Android 17 AOSP tag evidence is available.
- If implementation is gated, the gate is OS version, device capability, module version, permission state, app state, API usage, or another non-targetSdk condition.

顧客向け表現:
- Android 17 へ OS アップデートすると、targetSdkVersion を変更していないアプリにも影響する可能性がある。

記入例:
- Android 17 端末上で、targetSdkVersion 36 のままでも新しい制限が有効になる。
- AOSP で targetSdkVersion gate が見つからず、OS version または機能利用条件だけで分岐している。

### TARGET_SDK_37

Android 17 / API level 37 以上を target にするアプリへ適用される場合に使う。

必要な根拠:
- Behavior Change source is `behavior-changes-17`, or equivalent official statement exists.
- AOSP evidence shows a targetSdkVersion 37 gate, compat ChangeId default-enabled for API 37+, or an API 37 condition, once Android 17 AOSP tag evidence is available.
- Android 17 / targetSdkVersion 36 and Android 17 / targetSdkVersion 37 have different expected behavior.

顧客向け表現:
- targetSdkVersion を 37 以上に上げると有効になるため、OS アップデートだけでは原則として発生しない。

記入例:
- Android 17 / targetSdkVersion 36: 旧挙動が維持される。
- Android 17 / targetSdkVersion 37: 新挙動が有効になる。

### TARGET_SDK_37_CONDITIONAL

targetSdkVersion 37 以上が必要だが、それだけでは適用されない場合に使う。

追加条件の例:
- large screen or `sw600dp`
- specific permission group
- specific API usage
- cross-app or cross-profile boundary
- manifest property or opt-out state
- process lifecycle state
- foreground service state

必要な根拠:
- Same evidence as `TARGET_SDK_37`.
- Additional runtime condition is documented and verified in AOSP or official docs.

顧客向け表現:
- targetSdkVersion 37 以上に加えて、特定の端末条件、API 利用、権限、manifest 設定などを満たす場合に影響する。

記入例:
- Android 17 / targetSdkVersion 37 でも、対象 API を呼ばないアプリには影響しない。
- Android 17 / targetSdkVersion 37 かつ `sw >= 600dp` の large screen でのみ影響する。

### MAINLINE_OR_PLAY_SYSTEM_UPDATE

Mainline module または Google Play system update で配信され、Android 17 platform image だけでは適用可否が決まらない場合に使う。

必要な根拠:
- Official documentation states module or Google Play system update delivery.
- AOSP evidence identifies the module or package boundary where possible.
- Impact description separates platform version from module version.

顧客向け表現:
- Android 17 端末だけでなく、対象モジュールが更新された過去 OS の端末にも影響する可能性がある。

記入例:
- Android 16 端末でも、対象 Mainline module の更新後に同じ挙動が発生する可能性がある。

### API_ADDITION_ONLY

新 API の追加・公開であり、既存アプリの実行時挙動変更ではない場合に使う。

必要な根拠:
- API surface change is present.
- No Behavior Change statement or no changed behavior for existing apps is identified.
- Developer action is adoption opportunity, not compatibility mitigation.

顧客向け表現:
- 既存アプリの互換性リスクではなく、新 API の利用機会として扱う。

記入例:
- `current.txt` には新 API が追加されているが、既存 API の返り値・例外・権限条件は変わっていない。

### UNKNOWN_NEEDS_MORE_EVIDENCE

分類を根拠付きで説明できない場合に使う。

必要な対応:
- Do not assign High confidence.
- Record missing evidence.
- Continue investigation before customer-facing conclusion.

記入例:
- 公式文書は targetSdkVersion 37 以上と読めるが、Android 17 AOSP tag がなく gate を確認できない。
- AOSP 差分候補はあるが、公式 Behavior Change の該当文言と結びついていない。

## High confidence の条件（High Confidence Requirements）

A classification can be High confidence only when all of the following are true:

- Original official statement is quoted or paraphrased with source URL.
- The page category and the original statement agree.
- AOSP evidence confirms the applicable gate, or confirms that no targetSdkVersion gate exists.
- Compat framework entry is checked when a Change ID exists.
- Android 17 / targetSdkVersion 36 and Android 17 / targetSdkVersion 37 expected behavior are both stated.
- Additional conditions and exceptions are stated.
- Customer-facing wording does not mix OS update impact with targetSdkVersion impact.

Until an Android 17 AOSP tag is available locally, do not mark AOSP-backed conclusions as High confidence.

## 根拠の記録順（Evidence Pattern）

Record facts in this order:

1. Official documentation page and section.
2. Original applicability statement.
3. AOSP source context reviewed:
   - file / symbol / entry point / caller
   - why this code path is relevant to the Behavior Change
   - Android 16 baseline and Android 17 behavior
   - unrelated code paths excluded, when relevant
4. Diff interpretation:
   - observed source diff
   - whether it adds, removes, gates, or changes default behavior
   - how the diff supports the applicability classification
5. Exact gate evidence.
6. Compat framework Change ID and default state, if any.
7. Expected behavior matrix.
8. Developer impact and action candidates.
9. Confidence and missing evidence.

## よくある誤分類（Common Misclassifications）

- Do not classify an item as `TARGET_SDK_37` only because it appears on Android 17 pages. Confirm the specific page and wording.
- Do not classify an item as `OS_UPDATE_ALL_APPS` only because the implementation changed in AOSP. Check whether the implementation is behind a targetSdkVersion or compat gate.
- Do not treat a new API as a Behavior Change unless existing behavior changes.
- Do not ignore opt-out, exception, device form factor, or permission conditions.
- Do not use High confidence when the Android 17 AOSP tag is unavailable.

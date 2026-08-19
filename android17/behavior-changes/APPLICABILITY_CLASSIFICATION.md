# Android 17 適用条件分類

このファイルは、Android 17 Behavior Changes を「OS アップデート時に自動的に適用される差分」と「targetSdkVersion 37 以上に上げたときに適用される差分」に分類するための基準を定義する。

## バージョンスコープ

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

## 公式ドキュメント参照元

主な参照元:
- OS アップデート / 全アプリ: https://developer.android.com/about/versions/17/behavior-changes-all
- targetSdkVersion 37 以上: https://developer.android.com/about/versions/17/behavior-changes-17

Compat framework:
- AOSP の `@ChangeId` / `@EnabledAfter` / `@EnabledSince` / `CompatChanges.isChangeEnabled` を優先して確認する。

## 分類ラベル

各 finding には、primary label を必ず 1 つだけ付ける。

### OS_UPDATE_ALL_APPS

公式文書が「targetSdkVersion に関係なく Android 17 上の全アプリに適用される」と説明している場合に使う。

必要な根拠:
- Behavior Change の参照元が `behavior-changes-all` である、または同等の公式記述が存在する。
- Android 17 AOSP タグの根拠を確認できる状態で、AOSP 根拠に targetSdkVersion 37 ゲートが見つからない。
- 実装に gate がある場合、その gate が OS version、device capability、module version、permission state、app state、API usage、または targetSdkVersion 以外の条件である。

顧客向け表現:
- Android 17 へ OS アップデートすると、targetSdkVersion を変更していないアプリにも影響する可能性がある。

記入例:
- Android 17 端末上で、targetSdkVersion 36 のままでも新しい制限が有効になる。
- AOSP で targetSdkVersion ゲートが見つからず、OS version または機能利用条件だけで分岐している。

### TARGET_SDK_37

Android 17 / API level 37 以上を target にするアプリへ適用される場合に使う。

必要な根拠:
- Behavior Change の参照元が `behavior-changes-17` である、または同等の公式記述が存在する。
- Android 17 AOSP タグの根拠を確認できる状態で、AOSP 根拠に targetSdkVersion 37 ゲート、API 37 以上で default-enabled になる compat ChangeId、または API 37 条件が確認できる。
- Android 17 / targetSdkVersion 36 と Android 17 / targetSdkVersion 37 で、期待される挙動が異なる。

顧客向け表現:
- targetSdkVersion を 37 以上に上げると有効になるため、OS アップデートだけでは原則として発生しない。

記入例:
- Android 17 / targetSdkVersion 36: 旧挙動が維持される。
- Android 17 / targetSdkVersion 37: 新挙動が有効になる。

### TARGET_SDK_37_CONDITIONAL

targetSdkVersion 37 以上が必要だが、それだけでは適用されない場合に使う。

追加条件の例:
- large screen または `sw600dp`
- 特定の permission group
- 特定の API usage
- cross-app または cross-profile boundary
- manifest property または opt-out state
- process lifecycle state
- foreground service state

必要な根拠:
- `TARGET_SDK_37` と同じ根拠。
- 追加の実行時条件が公式ドキュメントに記載され、AOSP または公式ドキュメントで確認できる。

顧客向け表現:
- targetSdkVersion 37 以上に加えて、特定の端末条件、API 利用、権限、manifest 設定などを満たす場合に影響する。

記入例:
- Android 17 / targetSdkVersion 37 でも、対象 API を呼ばないアプリには影響しない。
- Android 17 / targetSdkVersion 37 かつ `sw >= 600dp` の large screen でのみ影響する。

### MAINLINE_OR_PLAY_SYSTEM_UPDATE

Mainline module または Google Play system update で配信され、Android 17 platform image だけでは適用可否が決まらない場合に使う。

必要な根拠:
- 公式ドキュメントが、module または Google Play system update による配信であると説明している。
- 可能な範囲で、AOSP 根拠により module または package boundary を特定している。
- 影響説明で platform version と module version を分けている。

顧客向け表現:
- Android 17 端末だけでなく、対象モジュールが更新された過去 OS の端末にも影響する可能性がある。

記入例:
- Android 16 端末でも、対象 Mainline module の更新後に同じ挙動が発生する可能性がある。

### API_ADDITION_ONLY

新 API の追加・公開であり、既存アプリの実行時挙動変更ではない場合に使う。

必要な根拠:
- API surface change が存在する。
- Behavior Change としての記述がない、または既存アプリの挙動変更が確認されない。
- 開発者対応は互換性回避ではなく、新 API 採用の機会として説明できる。

顧客向け表現:
- 既存アプリの互換性リスクではなく、新 API の利用機会として扱う。

記入例:
- `current.txt` には新 API が追加されているが、既存 API の返り値・例外・権限条件は変わっていない。

### UNKNOWN_NEEDS_MORE_EVIDENCE

分類を根拠付きで説明できない場合に使う。

必要な対応:
- High confidence を付けない。
- 不足している根拠を記録する。
- 顧客向けの結論を出す前に調査を継続する。

記入例:
- 公式文書はtargetSdkVersion 37以上と読めるが、関連AOSP projectまたは実装pathを特定できずgateを確認できない。
- AOSP 差分候補はあるが、公式 Behavior Change の該当文言と結びついていない。

## High confidence の条件

分類を High confidence とできるのは、以下をすべて満たす場合のみ。

- 公式ドキュメントの原文または要約を、出典 URL とともに記録している。
- ページ種別と原文の内容が一致している。
- AOSP 根拠により適用 gate を確認している、または targetSdkVersion ゲートが存在しないことを確認している。
- Change ID が存在する場合は、compat framework entry を確認している。
- Android 17 / targetSdkVersion 36 と Android 17 / targetSdkVersion 37 の期待挙動をどちらも記載している。
- 追加条件と例外を記載している。
- 顧客向け表現で、OS アップデートによる影響と targetSdkVersion 変更による影響を混同していない。

Android 17 AOSP タグは `android-17.0.0_r1` を利用する。High confidence を付ける場合は、このタグと `android-16.0.0_r4` の明示的な比較に基づくこと。

## 根拠の記録順

事実は以下の順序で記録する。

1. 公式ドキュメントのページとセクション。
2. 検証対象の適用条件文。
3. 確認した AOSP source context:
   - file / symbol / entry point / caller
   - その code path が Behavior Change に関係する理由
   - Android 16 baseline と Android 17 behavior
   - 関連しない code path を除外した場合は、その内容
4. Diff interpretation:
   - 確認した source diff
   - 挙動の追加、削除、gate 追加、default behavior 変更のどれに該当するか
   - その diff が適用条件分類をどのように支えるか
5. 正確な gate evidence。
6. Compat framework Change ID と default state。存在する場合のみ。
7. 期待挙動の matrix。
8. 開発者への影響と対応候補。
9. confidence と不足している根拠。

## よくある誤分類

- Android 17 ページに掲載されているという理由だけで `TARGET_SDK_37` に分類しない。掲載ページと文言を確認する。
- AOSP 実装が変わっているという理由だけで `OS_UPDATE_ALL_APPS` に分類しない。実装が targetSdkVersion ゲートまたは compat gate の内側にないか確認する。
- 既存挙動が変わらない限り、新 API 追加だけを Behavior Change として扱わない。
- opt-out、例外、device form factor、permission 条件を無視しない。
- 関連AOSP projectの`android-17.0.0_r1`タグ、実装path、または必要なgate evidenceを確認できない状態でHigh confidenceを使わない。

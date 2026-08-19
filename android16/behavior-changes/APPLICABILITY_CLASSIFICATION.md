# Android 16 適用条件分類

このファイルは、Android 16 Behavior Changes を「OSアップデート時に自動的に適用される差分」と「targetSdkVersion 36 を上げた時に適用される差分」に分類するための基準を定義する。

## バージョンスコープ

比較元:
- android-15.0.0_r36

比較先:
- android-16.0.0_r4

## 公式ドキュメント参照元

主要ドキュメント:
- OS アップデート / 全アプリ: https://developer.android.com/about/versions/16/behavior-changes-all
- targetSdkVersion 36+: https://developer.android.com/about/versions/16/behavior-changes-16
- Compat framework: https://developer.android.com/about/versions/16/reference/compat-framework-changes

## 分類ラベル

各調査項目には、主分類を必ず1つだけ付ける。

### OS_UPDATE_ALL_APPS

公式文書が「targetSdkVersion にかかわらず、Android 16 上で動作するすべてのアプリに適用される」と説明している場合に使う。

必要な根拠:
- Behavior Change の参照元が `behavior-changes-all` である、または同等の公式記述が存在する。
- AOSP 根拠に targetSdkVersion 36 の適用 gate が見つからない。
- 実装に gate がある場合、その条件が OS バージョン、端末の機能、モジュールのバージョン、権限状態、アプリの状態、API の利用、または targetSdkVersion 以外の条件である。

顧客向け表現:
- Android 16 へ OS アップデートすると、targetSdkVersion を変更していないアプリにも影響する可能性がある。

### TARGET_SDK_36

Android 16 / API level 36 以上を対象とするアプリに適用される場合に使う。

必要な根拠:
- Behavior Change の参照元が `behavior-changes-16` である、または同等の公式記述が存在する。
- AOSP 根拠で、targetSdkVersion の gate、API 36 以上で既定で有効になる compat ChangeId、または API 36 の条件を確認できる。
- Android 16 / targetSdkVersion 35 と Android 16 / targetSdkVersion 36 で、期待される挙動が異なる。

顧客向け表現:
- targetSdkVersion を 36 以上に上げると有効になるため、OS アップデートだけでは原則として発生しない。

### TARGET_SDK_36_CONDITIONAL

targetSdkVersion 36 以上が必要だが、それだけでは適用されない場合に使う。

追加条件の例:
- large screen または `sw600dp`
- 特定の権限グループ
- 特定の API 利用
- アプリ間の component boundary
- manifest property または opt-out の状態
- process lifecycle の状態

必要な根拠:
- `TARGET_SDK_36` と同じ根拠。
- 追加の実行時条件が文書化され、AOSP または公式ドキュメントで確認できる。

顧客向け表現:
- targetSdkVersion 36 以上に加えて、特定の端末条件、API 利用、権限、manifest 設定などを満たす場合に影響する。

### OPT_IN_ONLY

Android 16 の公式ドキュメントが現時点の挙動を明示的な opt-in と説明し、AOSP 根拠から、OS アップデートや targetSdkVersion 36 への更新だけでは有効にならないことを確認できる場合に使う。

opt-in gate の例:
- manifest attribute または manifest property
- app compat flag による強制有効化
- 開発者向けテスト flag
- feature flag と、アプリまたは component の明示的な設定の組み合わせ

必要な根拠:
- 公式ドキュメントに、opt-in であること、または現在が opt-in 段階であることが記載されている。
- AOSP 根拠から、正確な opt-in gate を特定できる。
- AOSP 根拠から、opt-in しない既定の経路ではこの挙動が適用されないことを確認できる。
- Android 16 / targetSdkVersion 35 と Android 16 / targetSdkVersion 36 の期待挙動をどちらも記載している。
- 現在の Android 16 における opt-in の挙動と、将来既定で強制する計画をレポート内で分けている。

顧客向け表現:
- Android 16 の現時点では、OS アップデートや targetSdkVersion 36 化だけでは有効にならず、manifest 設定、compat flag、developer testing 手順などで明示的に opt-in した場合に影響する。

### MAINLINE_OR_PLAY_SYSTEM_UPDATE

変更が Mainline module または Google Play system update で配信され、Android 16 の platform image だけでは適用可否が決まらない場合に使う。

必要な根拠:
- 公式ドキュメントに、module または Google Play system update で配信されることが記載されている。
- 可能な範囲で、AOSP 根拠から module または package boundary を特定している。
- 影響説明で platform version と module version を分けている。

顧客向け表現:
- Android 16 端末だけでなく、対象モジュールが更新された過去 OS の端末にも影響する可能性がある。

### API_ADDITION_ONLY

API を追加または公開するだけで、既存アプリの挙動自体は変わらない場合に使う。

必要な根拠:
- API surface に変更がある。
- Behavior Change としての記述がない、または既存アプリの挙動変更を確認できない。
- 開発者の対応が互換性問題の回避ではなく、新 API を採用する機会として説明できる。

顧客向け表現:
- 既存アプリの互換性リスクではなく、新 API の利用機会として扱う。

### UNKNOWN_NEEDS_MORE_EVIDENCE

適用条件分類を根拠付きで説明できない場合に使う。

必要な対応:
- High confidence を付けない。
- 不足している根拠を記録する。
- 顧客向けの結論を出す前に調査を継続する。

## High confidence の条件

以下をすべて満たす場合に限り、適用条件分類を High confidence とできる。

- 公式ドキュメントの原文または要約を、出典 URL とともに記録している。
- ページ種別と検証対象の原文が一致している。
- AOSP 根拠から適用 gate を確認している、または targetSdkVersion の gate が存在しないことを確認している。
- Change ID が存在する場合は、compat framework の項目を確認している。
- Android 16 / targetSdkVersion 35 と Android 16 / targetSdkVersion 36 の期待挙動をどちらも記載している。
- 追加条件と例外を記載している。
- 顧客向け表現で、OS アップデートによる影響と targetSdkVersion 変更による影響を混同していない。

## 根拠の記録順

事実は次の順序で記録する。

1. 公式ドキュメントのページとセクション。
2. 検証対象の適用条件文。
3. 確認した AOSP ソース文脈:
   - file / symbol / entry point / caller
   - その code path が Behavior Change に関係する理由
   - Android 15 の基準挙動と Android 16 の挙動
   - 関係しない code path を除外した場合は、その内容
4. 差分解釈:
   - 確認したソース差分
   - 挙動の追加、削除、gate の追加、既定動作の変更のどれに該当するか
   - その差分が適用条件分類をどのように支えるか
5. 正確な gate の根拠。
6. Compat framework Change ID と既定状態。存在する場合のみ。
7. 期待挙動の一覧表。
8. 開発者への影響と対応候補。
9. confidence と不足している根拠。

## よくある誤分類

- Android 16 のページに掲載されているという理由だけで `TARGET_SDK_36` に分類しない。掲載ページと文言を確認する。
- AOSP の実装が変わっているという理由だけで `OS_UPDATE_ALL_APPS` に分類しない。実装が targetSdkVersion または compat gate の内側にないか確認する。
- AOSP に targetSdkVersion 36 の実行時 gate がない場合、opt-in 限定の挙動を `TARGET_SDK_36_CONDITIONAL` に無理に分類しない。
- 既存の挙動が変わらない限り、新 API を Behavior Change として扱わない。
- opt-out、例外、端末形態、権限の条件を無視しない。
- AOSP checkout を利用できない場合は High confidence を使わない。

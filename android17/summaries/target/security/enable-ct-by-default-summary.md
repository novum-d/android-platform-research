# CT のデフォルト有効化 - 1ページ要約

## 対象（Target）

Android 17 Behavior Change

比較元:
- android-16.0.0_r4

比較先:
- TBD: Android 17 AOSP tag

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

## 適用条件（Applicability）

- 主分類（Primary classification）: UNKNOWN_NEEDS_MORE_EVIDENCE
- OS アップデート / 全アプリ（OS update / all apps）: 未確認。原文は targetSdkVersion 37 以上を明示しているが、AOSP gate 未確認。
- targetSdkVersion 37 以上: 公式文書上は該当。AOSP gate 未確認。
- その他の必須条件（Other required conditions）: TLS / HTTPS 通信、certificate transparency policy、Network Security Config、証明書チェーン。
- Compat Change ID: 未確認
- Compat default state: 未確認

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 未確認。この section は targetSdkVersion 37 以上向けだが、AOSP gate 未確認。 |
| Android 17 / targetSdkVersion 37 | 公式文書上は CT が default enabled。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | CT 要件を満たさない証明書チェーンを使う HTTPS 接続で失敗する可能性。 |

## 要約（Summary）

Android 17 では、targetSdkVersion 37 以上のアプリで certificate transparency (CT) が default enabled になる、と公式文書は説明している。

## 顧客影響（Customer Impact）

- 要確認

## 影響対象（Who Is Affected）

- 対象アプリ: targetSdkVersion 37 へ更新し、platform TLS / HTTPS 通信を行うアプリ。
- 対象機能: API 通信、ログイン、決済、コンテンツ取得、staging / internal endpoint への接続。
- 対象条件: CT 要件を満たさない証明書チェーン、Network Security Config の CT 設定、証明書 pinning / private PKI との組み合わせ。

## 対応要否（Required Action）

- 必須対応: HTTPS 接続先の証明書チェーンが CT 要件を満たすか棚卸しする。
- 推奨対応: Android 16 の opt-in または Android 17 / targetSdkVersion 37 環境で CT 有効時の接続テストを行う。
- 不要: ネットワーク通信を行わないアプリ、または全接続先が CT 要件を満たすことを確認済みのアプリでは直接影響は限定的。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 16 | 36 | 公式文書上、CT は available だが app opt-in が必要。 |
| Android 17 | 36 | 未確認。この section は targetSdkVersion 37 以上向けだが、AOSP gate 未確認。 |
| Android 17 | 37 | CT が default enabled。CT 要件を満たさない証明書チェーンでは接続影響の可能性。 |

## 顧客向け説明（Explanation for Customers）

Android 17 では、targetSdkVersion 37 以上のアプリで certificate transparency が既定で有効になります。Android 16 ではアプリが明示的に opt in した場合だけ CT が使われていましたが、Android 17 / targetSdkVersion 37 では opt in していない接続にも CT policy が適用される可能性があります。

そのため、公開 HTTPS endpoint、staging endpoint、private PKI、証明書 pinning を利用する通信について、証明書チェーンが CT 要件を満たしているか確認してください。現時点では local AOSP checkout に Android 17 tag がないため、targetSdkVersion gate、例外条件、compat flag の有無は未確認です。

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-17
- 検証対象の原文: targetSdkVersion 37 以上のアプリでは certificate transparency が default enabled。Android 16 では CT は available だが opt in が必要。
- AOSP ファイル: 未確認。local `frameworks-base` に `android-17*` tag がない。
- AOSP ソース文脈: 未確認。tag 間 diff が実行できない。
- 差分解釈: 未分類。公式文書上は changed default と読めるが、AOSP diff による確認は Android 17 tag 待ち。
- Gate conclusion: 未確認。公式文書は targetSdkVersion 37 以上を示すが、AOSP gate evidence は未取得。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 追加調査が必要

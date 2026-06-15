# Android 17 Behavior Changes 調査一覧

Behavior Changes の各セクションごとに、顧客説明向け調査レポートを作成する。

## 現在の状態（Current Status）

Android 17 official Behavior Change documentation is available.

Local AOSP status:
- `frameworks-base` currently has no `android-17*` tag.
- AOSP-backed High confidence conclusions must wait until the target Android 17 AOSP tag is available.

## 早見表（Quick View）

最初にここを見る。各 Behavior Change は必ず 1 つの primary classification に入れる。

| 分類（Classification） | 適用条件（When it applies） | 顧客向けの意味 | 一覧 |
| --- | --- | --- | --- |
| [`OS_UPDATE_ALL_APPS`](APPLICABILITY_CLASSIFICATION.md#os_update_all_apps) | Android 17 上の全アプリ。targetSdkVersion に依存しない | OS アップデートだけで影響する可能性がある | [OS update / all apps](#os-update--all-apps) |
| [`TARGET_SDK_37`](APPLICABILITY_CLASSIFICATION.md#target_sdk_37) | Android 17+ で targetSdkVersion >= 37 | targetSdkVersion 37 化で有効になる | [targetSdkVersion 37](#targetsdkversion-37) |
| [`TARGET_SDK_37_CONDITIONAL`](APPLICABILITY_CLASSIFICATION.md#target_sdk_37_conditional) | targetSdkVersion >= 37 に加えて追加条件あり | targetSdkVersion 37 化だけでは不十分。端末条件、API 利用、権限なども必要 | [targetSdkVersion 37 + conditions](#targetsdkversion-37--conditions) |
| [`MAINLINE_OR_PLAY_SYSTEM_UPDATE`](APPLICABILITY_CLASSIFICATION.md#mainline_or_play_system_update) | Mainline / Google Play system update に依存 | Android 17 platform image だけで決まらない | [Mainline / Play system update](#mainline--play-system-update) |
| [`API_ADDITION_ONLY`](APPLICABILITY_CLASSIFICATION.md#api_addition_only) | 既存挙動変更ではなく API 追加 | 互換性リスクではなく採用機会 | [API addition only](#api-addition-only) |
| [`UNKNOWN_NEEDS_MORE_EVIDENCE`](APPLICABILITY_CLASSIFICATION.md#unknown_needs_more_evidence) | 根拠不足 | 顧客向け結論に使わない | [Unknown / needs evidence](#unknown--needs-evidence) |

使い方:
- レポート作成時は、最初に公式文書のページ種別と原文から仮分類を置く。
- AOSP gate / compat framework / targetSdkVersion 別の期待挙動を確認できるまで、High confidence にしない。
- 分類に迷う場合は `UNKNOWN_NEEDS_MORE_EVIDENCE` に入れ、不足根拠を明記する。

## 公式ドキュメント（Official Documentation）

Use:

```text
https://developer.android.com/about/versions/17/behavior-changes-all
https://developer.android.com/about/versions/17/behavior-changes-17
```

## テンプレート（Template）

Use:

```text
android17/templates/customer-report-template.md
```

<a id="os-update--all-apps"></a>

## OS アップデート / 全アプリ（OS Update / All Apps）

Android 17 へ OS アップデートすると、targetSdkVersion を変更していないアプリにも影響する可能性がある項目。

| レポート（Report） | 要約（Summary） | 根拠セクション（Evidence section） | 1ページ要約 | 状態（Status） |
| --- | --- | --- | --- | --- |
| [App memory limits](16-app-memory-limits.md) | Android 17 で device total RAM に基づく app memory limits が導入される。 | [AOSP 調査](16-app-memory-limits.md#aosp-調査aosp-investigation) | [summary](../summaries/16-app-memory-limits-summary.md) | AOSP tag 待ち / Low confidence |
| [SMS OTP protection](17-sms-otp-protection.md) | Android 17 で WebOTP format messages にも SMS OTP protection が適用される。 | [AOSP 調査](17-sms-otp-protection.md#aosp-調査aosp-investigation) | [summary](../summaries/17-sms-otp-protection-summary.md) | AOSP tag 待ち / Low confidence |
| [Block cross profile loopback traffic](21-block-cross-profile-loopback-traffic.md) | Android 17 で cross-profile loopback traffic が default block される。 | [AOSP 調査](21-block-cross-profile-loopback-traffic.md#aosp-調査aosp-investigation) | [summary](../summaries/21-block-cross-profile-loopback-traffic-summary.md) | AOSP tag 待ち / Low confidence |
| [Restoring default IME visibility after rotation](22-restoring-default-ime-visibility-after-rotation.md) | Android 17 で unhandled configuration change 後に previous IME visibility が自動復元されない。 | [AOSP 調査](22-restoring-default-ime-visibility-after-rotation.md#aosp-調査aosp-investigation) | [summary](../summaries/22-restoring-default-ime-visibility-after-rotation-summary.md) | AOSP tag 待ち / Low confidence |

<a id="targetsdkversion-37"></a>

## targetSdkVersion 37

Android 17+ で targetSdkVersion を 37 以上にした場合に有効になる項目。

| レポート（Report） | 要約（Summary） | 根拠セクション（Evidence section） | 1ページ要約 | 状態（Status） |
| --- | --- | --- | --- | --- |
| まだありません |  |  |  |  |

<a id="targetsdkversion-37--conditions"></a>

## targetSdkVersion 37 + 追加条件（targetSdkVersion 37 + Conditions）

targetSdkVersion 37 以上に加えて、端末条件、権限、API 利用、manifest property、process state などの追加条件を満たす場合に影響する項目。

| レポート（Report） | 要約（Summary） | 根拠セクション（Evidence section） | 1ページ要約 | 状態（Status） |
| --- | --- | --- | --- | --- |
| まだありません |  |  |  |  |

<a id="mainline--play-system-update"></a>

## Mainline / Google Play system update

Mainline module または Google Play system update の配信状態に依存する項目。

| レポート（Report） | 要約（Summary） | 根拠セクション（Evidence section） | 1ページ要約 | 状態（Status） |
| --- | --- | --- | --- | --- |
| まだありません |  |  |  |  |

<a id="api-addition-only"></a>

## API 追加のみ（API Addition Only）

既存アプリの挙動変更ではなく、新 API の利用機会として扱う項目。

| レポート（Report） | 要約（Summary） | 根拠セクション（Evidence section） | 1ページ要約 | 状態（Status） |
| --- | --- | --- | --- | --- |
| まだありません |  |  |  |  |

<a id="unknown--needs-evidence"></a>

## 根拠不足（Unknown / Needs Evidence）

分類根拠が不足しており、顧客向け結論に使えない項目。

| レポート（Report） | 不足根拠（Missing evidence） | 次の確認（Next check） | 状態（Status） |
| --- | --- | --- | --- |
| [usesClearTraffic deprecation plan](18-usescleartexttraffic-deprecation-plan.md) | Android 17 で即時 runtime behavior change があるか、future deprecation plan のみかを AOSP で未確認 | `usesCleartextTraffic` parsing / cleartext policy / deprecation annotation / compat framework を Android 17 tag で確認 | AOSP tag 待ち / Low confidence |
| [Restrict implicit URI grants](19-restrict-implicit-uri-grants.md) | Android 17 で即時 enforcement があるか、Android 18 advance warning / detection guidance のみかを AOSP で未確認 | URI grant path / StrictMode detection / log emission / compat framework を Android 17 tag で確認 | AOSP tag 待ち / Low confidence |
| [Per-app keystore limits](20-per-app-keystore-limits.md) | OS update 側の per-app limit introduction と targetSdkVersion 37 側の stricter limit / error code 分岐を AOSP で未確認 | Keystore enforcement path / targetSdkVersion gate / system app 判定 / exception mapping / compat framework を Android 17 tag で確認 | AOSP tag 待ち / Low confidence |

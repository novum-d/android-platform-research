# Local network permission required for apps targeting Android 17 - 1ページ要約（One Page Summary）

## 対象（Target）

Android 17 Behavior Change

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP tag

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

## 適用条件（Applicability）

- 主分類（Primary classification）: UNKNOWN_NEEDS_MORE_EVIDENCE
- OS アップデート / 全アプリ（OS update / all apps）: Unknown。公式ページは targetSdkVersion 37+ 向け。
- targetSdkVersion 37 以上: 公式文書上は該当。AOSP gate 未確認。
- その他の必須条件（Other required conditions）: local network access、LAN device discovery / connection、permission grant state、system picker 利用有無。
- Compat Change ID: Unknown
- Compat default state: Unknown

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | Unknown。公式 docs 上は legacy app に temporary implicit grant があるが、AOSP gate 未確認。 |
| Android 17 / targetSdkVersion 37 | local network access が default block になり、picker または `ACCESS_LOCAL_NETWORK` runtime grant が必要と公式文書は説明。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | LAN device discovery / connection、mDNS / NSD、casting、IoT、local endpoint socket access が影響を受ける可能性。 |

## 要約（Summary）

Android 17 では、targetSdkVersion 37 以上のアプリが local network devices を discover / connect するには、新しい `ACCESS_LOCAL_NETWORK` runtime permission または system-mediated picker が必要になる、と公式文書は説明している。

## 顧客影響（Customer Impact）

- 要確認

## 影響対象（Who Is Affected）

- 対象アプリ: targetSdkVersion 37 へ更新し、LAN device discovery / connection を行うアプリ。
- 対象機能: smart home、IoT、casting、mDNS / NSD、`.local` resolution、local endpoint socket、WebView local network access。
- 対象条件: system picker を使わず direct local network access を行い、`ACCESS_LOCAL_NETWORK` grant がない場合。

## 対応要否（Required Action）

- 必須対応: local network access 箇所を棚卸しし、picker path か runtime permission path かを決める。
- 推奨対応: direct access が必要な場合は manifest declaration、runtime request、denial / revocation handling、Android 17 テストを実装する。
- 不要: local network access を行わないアプリ、または system-mediated picker だけで要件を満たせるアプリでは broad runtime permission は不要。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 16 | 36 | 公式 docs 上は local network access は open。opt-in test は可能。 |
| Android 17 | 36 | Unknown。legacy app は temporary implicit grant と説明されるが、AOSP gate 未確認。 |
| Android 17 | 37 | default block。picker または `ACCESS_LOCAL_NETWORK` runtime grant が必要と公式文書は説明。 |

## 顧客向け説明（Explanation for Customers）

Android 17 では、targetSdkVersion 37 以上のアプリが LAN 上の device を discover / connect する場合、新しい `ACCESS_LOCAL_NETWORK` runtime permission が必要になります。casting、smart home、IoT、mDNS / NSD、`.local` 解決、local endpoint への socket 通信などが対象になり得ます。system-mediated picker で要件を満たせる場合は、広い permission prompt を避けられます。

現時点では local AOSP checkout に Android 17 tag がないため、targetSdkVersion gate、permission / AppOps linkage、networking stack enforcement、compat flag の有無は未確認です。最終的な適用分類は Android 17 AOSP tag 公開後に再確認が必要です。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-17
- Permission reference: https://developer.android.com/reference/android/Manifest.permission#ACCESS_LOCAL_NETWORK
- Local network permission guide: https://developer.android.com/privacy-and-security/local-network-permission
- Original statement: Android 17 は `ACCESS_LOCAL_NETWORK` runtime permission を導入し、targetSdkVersion 37+ のアプリは picker または runtime permission request により LAN communication を維持する必要がある。
- AOSP files: 未確認。local `frameworks-base` に `android-17*` tag がない。
- AOSP source context: 未確認。tag 間 diff が実行できない。
- Diff interpretation: 未分類。added behavior / changed condition / changed default の判定は Android 17 tag 待ち。
- Gate conclusion: Unknown。公式文書は targetSdkVersion 37+ と runtime / permission / picker 条件を示すが、AOSP gate evidence は未取得。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Human decision required

判断（Decision）:
- Further investigation required

# Cross-profile loopback traffic のブロック - 1ページ要約

## 対象

Android 17 Behavior Change

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

## 適用条件

- 主分類（Primary classification）: OS_UPDATE_ALL_APPS
- OS アップデート / 全アプリ（OS update / all apps）: 該当。Android 17 以上で動作する全アプリに target API level に関係なく適用と明記されている。
- targetSdkVersion 37 以上: 不要。target API level に関係なく適用。
- その他の必須条件（Other required conditions）: 複数 profile があり、loopback traffic が profile boundary を跨ぐこと。same-profile loopback は対象外。
- Compat Change ID: 確認できず
- Compat default state: 未確認
- Confidence: Medium

## 早見マトリクス

| シナリオ | 影響 |
| --- | --- |
| Android 17 / targetSdkVersion 36 | cross-profile loopback traffic は default block。same-profile loopback は影響なし。 |
| Android 17 / targetSdkVersion 37 | targetSdkVersion 36 と同様。target API level に関係なく適用。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | work profile / personal profile など profile boundary を跨ぐ localhost / loopback communication が失敗する可能性。 |

## 要約

Android 17 では、cross-profile loopback traffic が default で許可されなくなる。same-profile loopback traffic は影響を受けないため、localhost 全般の禁止ではなく、profile boundary を跨ぐ loopback communication の制限として扱う。

AOSP framework では `USE_LOOPBACK_INTERFACE` / `FORCE_USE_LOOPBACK_INTERFACE` permission と関連 feature flags、BPF permission allowlist への追加を確認した。packet-level enforcement は Connectivity / netd / BPF 側の追加確認が必要。

## 顧客影響

- work profile / personal profile 間で localhost service に接続する設計が失敗する可能性がある。
- enterprise companion、DPC support、profile 間 helper、testing / diagnostic bridge などで影響が出る可能性がある。

## 影響対象（Who Is Affected）

- 対象アプリ: work profile / personal profile など複数 profile 間で localhost / loopback communication を使うアプリ。
- 対象機能: enterprise companion、DPC support、profile 間 helper、testing / diagnostic bridge。
- 対象条件: one profile で server を起動し、別 profile から `localhost` / `127.0.0.1` / `::1` へ接続する場合。

## 対応要否

- 必須対応: localhost / loopback 利用箇所を棚卸しし、same-profile か cross-profile かを確認する。
- 推奨対応: cross-profile communication は managed profile / enterprise 向けの公式 mechanism へ移行する。
- 不要: single profile device、same-profile loopback のみ、loopback を使わないアプリでは直接影響は限定的。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 36 | baseline。same-profile / cross-profile loopback の現行挙動を確認。 |
| Android 17 | 36 | cross-profile loopback は default block、same-profile loopback は unaffected。 |
| Android 17 | 37 | targetSdkVersion 36 と同じ期待。target API level に関係なく適用。 |

## 顧客向け説明

Android 17 では、work profile と personal profile など、profile boundary を跨ぐ loopback traffic が default で許可されなくなります。これは `localhost` / `127.0.0.1` / `::1` を profile 間通信路として使う設計に影響する可能性があります。

同じ profile 内の loopback traffic は公式文書上影響を受けません。したがって、同一 profile 内で local server を使うだけの機能と、別 profile から localhost へ接続する機能を分けて確認してください。

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-all
- 検証対象の原文: Android 17 から cross-profile loopback traffic は default で許可されない。same-profile loopback traffic は影響なし。Android 17 以上の全アプリに target API level に関係なく適用。
- AOSP ファイル: `core/res/AndroidManifest.xml`, `core/api/current.txt`, `core/api/system-current.txt`, `core/java/android/permission/flags.aconfig`, `services/permission/java/com/android/server/permission/access/permission/PermissionService.kt`
- AOSP ソース文脈: loopback interface traffic を permission で guard する `USE_LOOPBACK_INTERFACE` / `FORCE_USE_LOOPBACK_INTERFACE` と BPF permission allowlist。
- 差分解釈: added permission / changed condition / guarded enforcement surface。
- ゲート結論: targetSdkVersion ゲートは確認されない。packet-level enforcement は Connectivity / netd / BPF 側の追加確認が必要。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断

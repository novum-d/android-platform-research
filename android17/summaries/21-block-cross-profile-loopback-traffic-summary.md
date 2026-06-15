# Block cross profile loopback traffic - 1ページ要約（One Page Summary）

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
- OS アップデート / 全アプリ（OS update / all apps）: 公式文書上は該当候補。Android 17 以上で動作する全アプリに target API level に関係なく適用と明記されている。
- targetSdkVersion 37 以上: 公式文書上は不要。target API level に関係なく適用と説明されている。AOSP gate 未確認。
- その他の必須条件（Other required conditions）: 複数 profile があり、loopback traffic が profile boundary を跨ぐこと。same-profile loopback は対象外。
- Compat Change ID: Unknown
- Compat default state: Unknown

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | cross-profile loopback traffic は default block の可能性。same-profile loopback は影響なし。AOSP gate 未確認。 |
| Android 17 / targetSdkVersion 37 | targetSdkVersion 36 と同様。target API level に関係なく適用と公式文書は説明。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | work profile / personal profile など profile boundary を跨ぐ localhost / loopback communication が失敗する可能性。 |

## 要約（Summary）

Android 17 では、cross-profile loopback traffic が default で許可されなくなる。same-profile loopback traffic は影響を受けないため、localhost 全般の禁止ではなく、profile boundary を跨ぐ loopback communication の制限として扱う。

## 顧客影響（Customer Impact）

- 要確認

## 影響対象（Who Is Affected）

- 対象アプリ: work profile / personal profile など複数 profile 間で localhost / loopback communication を使うアプリ。
- 対象機能: enterprise companion、DPC support、profile 間 helper、testing / diagnostic bridge。
- 対象条件: one profile で server を起動し、別 profile から `localhost` / `127.0.0.1` / `::1` へ接続する場合。

## 対応要否（Required Action）

- 必須対応: localhost / loopback 利用箇所を棚卸しし、same-profile か cross-profile かを確認する。
- 推奨対応: cross-profile communication は managed profile / enterprise 向けの公式 mechanism へ移行する。
- 不要: single profile device、same-profile loopback のみ、loopback を使わないアプリでは直接影響は限定的。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 16 | 36 | baseline。same-profile / cross-profile loopback の現行挙動を確認。 |
| Android 17 | 36 | cross-profile loopback は default block、same-profile loopback は unaffected と公式文書は説明。 |
| Android 17 | 37 | targetSdkVersion 36 と同じ期待。target API level に関係なく適用。 |

## 顧客向け説明（Explanation for Customers）

Android 17 では、work profile と personal profile など、profile boundary を跨ぐ loopback traffic が default で許可されなくなります。これは `localhost` / `127.0.0.1` / `::1` を profile 間通信路として使う設計に影響する可能性があります。

同じ profile 内の loopback traffic は公式文書上影響を受けません。したがって、同一 profile 内で local server を使うだけの機能と、別 profile から localhost へ接続する機能を分けて確認してください。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-all
- Original statement: Android 17 から cross-profile loopback traffic は default で許可されない。same-profile loopback traffic は影響なし。Android 17 以上の全アプリに target API level に関係なく適用。
- AOSP files: 未確認。local `frameworks-base` に `android-17*` tag がない。
- AOSP source context: 未確認。tag 間 diff が実行できない。
- Diff interpretation: 未分類。公式文書上は changed default / changed condition と読めるが、AOSP diff による確認は Android 17 tag 待ち。
- Gate conclusion: Unknown。公式文書上は Android 17 all apps + cross-profile loopback condition。targetSdkVersion gate / compat framework evidence は未取得。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Human decision required

判断（Decision）:
- Further investigation required after Android 17 AOSP tag is available

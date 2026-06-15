# usesClearTraffic deprecation plan - 1ページ要約（One Page Summary）

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
- OS アップデート / 全アプリ（OS update / all apps）: All apps ページに掲載。ただし本文は future release の deprecation plan であり、Android 17 で即時 runtime behavior change があるとは明記していない。
- targetSdkVersion 37 以上: 公式文書上、この項目に targetSdkVersion 37 条件はない。AOSP gate 未確認。
- その他の必須条件（Other required conditions）: unencrypted HTTP connection が必要なアプリ、`android:usesCleartextTraffic` 利用、Network Security Configuration 移行状況、`minSdkVersion` が 24 未満か以上か。
- Compat Change ID: Unknown
- Compat default state: Unknown

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 公式文書上、即時 runtime behavior change は未確認。future deprecation に備えた移行対象。 |
| Android 17 / targetSdkVersion 37 | targetSdkVersion 36 と同様。targetSdkVersion 37 gate は公式文書上確認できない。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | HTTP cleartext が必要な場合、Network Security Configuration へ移行すべき。`minSdkVersion < 24` では `usesCleartextTraffic="true"` も併用。 |

## 要約（Summary）

Android 17 の all apps ページは、将来 release で `usesCleartextTraffic` element を deprecate する計画を示している。Android 17 で即時に HTTP cleartext 接続が壊れる変更とは公式文書上確認できず、主な対応は Network Security Configuration への移行である。

## 顧客影響（Customer Impact）

- 要確認

## 影響対象（Who Is Affected）

- 対象アプリ: HTTP cleartext connection が必要なアプリ、`usesCleartextTraffic` に依存しているアプリ。
- 対象機能: legacy HTTP API、閉域網 endpoint、IoT / gateway / partner integration。
- 対象条件: Network Security Configuration 未導入、または domain-scoped cleartext policy が未整理。

## 対応要否（Required Action）

- 必須対応: `usesCleartextTraffic` と HTTP endpoint を棚卸しし、`minSdkVersion` を確認する。
- 推奨対応: Network Security Configuration を導入し、必要 domain のみ `cleartextTrafficPermitted="true"` にする。
- 不要: HTTP cleartext connection を使わないアプリ、HTTPS 化済みのアプリでは直接影響は限定的。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 16 | 36 | baseline。`usesCleartextTraffic` と Network Security Configuration の現行挙動を確認。 |
| Android 17 | 36 | 即時挙動変更がないか確認。公式文書上は future deprecation plan。 |
| Android 17 | 37 | targetSdkVersion 37 による差分がないか確認。公式文書上は targetSdkVersion gate なし。 |

## 顧客向け説明（Explanation for Customers）

Android 17 の文書では、将来 release で `usesCleartextTraffic` element を deprecate する計画が示されています。Android 17 で直ちに HTTP cleartext 接続が失敗する変更とは公式文書上確認できませんが、HTTP が必要なアプリは Network Security Configuration へ移行することが推奨されています。

`minSdkVersion` が 24 未満の場合は、API 24 未満で Network Security Configuration が使えないため、`usesCleartextTraffic="true"` を残しつつ Network Security Configuration も追加します。`minSdkVersion` が 24 以上であれば、Network Security Configuration を使うことで `usesCleartextTraffic` への依存をなくせます。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-all
- Original statement: future release で `usesCleartextTraffic` element を deprecate する計画があり、unencrypted HTTP connection が必要なアプリは Network Security Configuration file へ移行すべき。
- AOSP files: 未確認。local `frameworks-base` に `android-17*` tag がない。
- AOSP source context: 未確認。tag 間 diff が実行できない。
- Diff interpretation: 未分類。公式文書上は immediate behavior change ではなく future deprecation plan / migration guidance と読めるが、AOSP diff による確認は Android 17 tag 待ち。
- Gate conclusion: Unknown。公式文書上は targetSdkVersion 37 gate なし、`minSdkVersion` と Network Security Configuration support が migration condition。runtime gate / compat framework evidence は未取得。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Human decision required

判断（Decision）:
- Further investigation required after Android 17 AOSP tag is available

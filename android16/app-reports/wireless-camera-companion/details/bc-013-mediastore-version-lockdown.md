# BC-013: MediaStore version lockdown

## 基本情報

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/16/behavior-changes-16
- Section: MediaStore version lockdown

既存調査:
- [android16/behavior-changes/target/security/mediastore-version-lockdown.md](../../../behavior-changes/target/security/mediastore-version-lockdown.md)
- [android16/summaries/target/security/mediastore-version-lockdown-summary.md](../../../summaries/target/security/mediastore-version-lockdown-summary.md)

## 対象アプリとの関係

関連するアプリ機能:
- 端末内写真 / 動画一覧。
- MediaStore sync。
- imported image / video cache invalidation。
- gallery view / thumbnail cache。

アプリが該当する可能性:
- Conditional。`MediaStore#getVersion()` を利用している場合のみ該当。

## 適用条件分類

主分類:
- `TARGET_SDK_36_CONDITIONAL`

必要条件:
- Android 16。
- targetSdkVersion 36 以上。
- `MediaStore#getVersion(Context)` または `getVersion(Context, String)` 利用。

Confidence:
- High。

## AOSP / 公式根拠

既存 Android16 調査で確認済み:
- `LOCKDOWN_MEDIASTORE_VERSION` / 343977174。
- `@EnabledSince(targetSdkVersion = BAKLAVA)`。
- lockdown 有効時は `dbUuid + calling uid` の hash を返す。
- legacy format `db.getVersion() + ":" + dbUuid` とは異なる。

## アプリ影響

想定される影響:
- version string format parsing が壊れる。
- cross-app / cross-device comparison ができなくなる。
- same-app cache invalidation token としての equality comparison は継続できる可能性。

推奨対応:
- `MediaStore#getVersion()` の戻り値を opaque string として扱う。
- format parse、UUID 抽出、cross-app comparison をやめる。
- media item 単位の差分検出は generation API 等を検討する。

## テスト観点

- Android 16 / targetSdkVersion 35。
- Android 16 / targetSdkVersion 36。
- `getVersion()` format。
- app reinstall / work profile / database reset。
- cache invalidation。

## Human Decision

- Final priority: TBD by human
- Release readiness impact: TBD by human

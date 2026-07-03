# MediaStore version lockdown - One Page Summary

## Summary

Android 16 / targetSdkVersion 36 以上では、`MediaStore#getVersion()` の戻り値がアプリごとに unique になる。AOSP では `LOCKDOWN_MEDIASTORE_VERSION` (`343977174`) が `@EnabledSince(targetSdkVersion = BAKLAVA)` として定義され、MediaProvider が `versionLockdown()` と compat change を確認したうえで `dbUuid + calling uid` の hash を返す。

この変更は `MediaStore#getVersion()` の戻り値から database version や UUID のような identifying properties を直接読み取れないようにし、fingerprinting / cross-app correlation 的な利用を抑止するためのもの。

## Applicability

- Classification: `TARGET_SDK_36_CONDITIONAL`
- Applies when:
  - Android 16 以上の MediaProvider behavior が使われる
  - app targets Android 16 / API level 36 以上
  - app calls `MediaStore#getVersion(Context)` or `MediaStore#getVersion(Context, String)`
  - MediaProvider `versionLockdown()` flag と compat change が enabled
- Does not primarily affect:
  - Android 16 / targetSdkVersion 35 apps, unless compat / module behavior is explicitly changed
  - apps that treat the value only as an opaque same-app cache invalidation token

## Key Evidence

- `MediaStore#getVersion(Context)` は `getVersion(context, VOLUME_EXTERNAL_PRIMARY)` を呼ぶ。
- `MediaStore#getVersion(Context, String)` は MediaProvider に `GET_VERSION_CALL` を送る。
- MediaProvider lockdown 有効時は `hash(dbUuid + callingUid)` を返す。
- MediaProvider lockdown 無効時は legacy format `db.getVersion() + ":" + dbUuid` を返す。
- AOSP compat Change ID は `343977174` / `LOCKDOWN_MEDIASTORE_VERSION`。
- 公式 compat framework changes ページでは該当 ID は確認できなかったため、force-enable / force-disable の顧客向け説明は断定しない。

## Expected Behavior

| Scenario | Expected behavior |
|---|---|
| Android 16 / targetSdkVersion 35 | legacy version format が維持される見込み |
| Android 16 / targetSdkVersion 36 | app ごとに unique な opaque token を返す |
| Android 15 / targetSdkVersion 36 | 公式 Android 16 behavior の対象外。module / flag 状態に依存する可能性があるため参考扱い |

## Customer Impact

影響が大きいのは、`MediaStore#getVersion()` の戻り値を opaque token ではなく、識別子や parse 可能な format として扱っているアプリ。

要注意:

- `number:uuid` のような format を parse している
- 複数アプリ間で値を比較している
- 複数端末間で値を比較している
- media database / provider / build / storage 状態を推測している
- analytics / SDK が fingerprinting input として使っている

自アプリ内 cache invalidation で「前回保存値と今回値が等しいか」だけを見ている場合は、多くのケースで継続可能。ただし app reinstall、work profile、volume unavailable、media database reset の扱いは実機で確認する。

## Recommended Actions

- `MediaStore#getVersion()` の戻り値を opaque string として扱う。
- format parsing、cross-app comparison、device identifier 的な利用を削除する。
- cache invalidation では same app 内の equality comparison に限定する。
- media item 単位の差分検出には generation API の利用を検討する。
- targetSdkVersion 36 化の検証では、Android 16 端末で異なるアプリから同じ volume の `getVersion()` を呼び、値が一致しないことを確認する。

## Human Decision Placeholder

- Final priority: TBD by human
- Final severity: TBD by human
- Release readiness impact: TBD by human
- Customer communication priority: TBD by human
- Owner decision / next action: TBD by human

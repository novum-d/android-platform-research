# MediaStore version lockdown

## 調査メタデータ

- Android version: Android 16
- Version directory: `android16`
- From tag: `android-15.0.0_r36`
- To tag: `android-16.0.0_r4`
- Previous targetSdkVersion: 35
- Target targetSdkVersion: 36
- Behavior Change section: MediaStore version lockdown
- Official documentation URL: https://developer.android.com/about/versions/16/behavior-changes-16#mediastore-lockdown
- Official documentation category: Security
- Applicability classification: `TARGET_SDK_36_CONDITIONAL`
- Confidence: High

Scope note: `android16/AGENTS.md` は To tag を `android-16.0.0_r1` としているが、本調査では依頼どおり `android-16.0.0_r4` を使用した。

## Official Documentation Review

2026-07-03 に公式ドキュメントの該当セクションを再確認した。対象ページは 2026-07-01 UTC 更新として表示されていた。

確認した公式記述:

- Apps targeting Android 16 or higher では `MediaStore#getVersion()` がアプリごとに unique になる。
- version string から identifying properties を取り除き、fingerprinting 目的の悪用を防ぐ。
- アプリは version の format を仮定すべきではない。
- 本来の用途である「MediaStore の大きな変更を検出して cache を再スキャンする」使い方では、多くの場合 current behavior を変更する必要はない。
- 追加情報を推測する目的で使っている場合は影響を受ける可能性がある。

依頼文の Original statements / Applicability details と公式本文に実質差分は見つからなかった。

## AOSP Checkout Hygiene

`frameworks-base` は clean で、`android-15.0.0_r36` と `android-16.0.0_r4` tag が存在することを確認した。ただし、この behavior change の主要実装は `frameworks-base` ではなく MediaProvider module にある。

MediaProvider evidence:

- Repository: `platform/packages/providers/MediaProvider`
- From tag commit: `android-15.0.0_r36` = `c118118eb3f198764d5ad060a2b958a7b3484347`
- To tag commit: `android-16.0.0_r4` = `30d7b6964c6448b2c281efc989dd41c3068953cb`
- Local checkout: `tmp/aosp-checkouts/MediaProvider`

## Facts

### Public API surface

`MediaStore#getVersion(Context)` と `MediaStore#getVersion(Context, String)` は Android 15 / Android 16 の API surface で signature 変更はない。

- `apex/framework/api/current.txt`
  - `getVersion(@NonNull Context)`
  - `getVersion(@NonNull Context, @NonNull String)`

Android 16 の `MediaStore.java` では、API doc が引き続き version string を opaque と説明している。`getVersion(Context)` は `VOLUME_EXTERNAL_PRIMARY` 向けの wrapper で、`getVersion(Context, String)` は `ContentProviderClient.call(GET_VERSION_CALL, ...)` を MediaProvider に送る。

Reviewed source:

- `apex/framework/java/android/provider/MediaStore.java`
  - `MediaStore#getVersion(Context)`
  - `MediaStore#getVersion(Context, String)`

### Provider implementation

MediaProvider は `GET_VERSION_CALL` を `getResultForGetVersion(Bundle)` に dispatch する。

Android 16 `MediaProvider.java` の実装では、volume 名から database を取得し、database UUID を取得したうえで次のどちらかを返す。

- lockdown 有効時: `dbUuid + calling uid` を `farmHashFingerprint64()` で hash 化した文字列
- lockdown 無効時: `db.getVersion() + ":" + dbUuid`

Reviewed source:

- `src/com/android/providers/media/MediaProvider.java`
  - `GET_VERSION_CALL`
  - `getResultForGetVersion(Bundle)`
  - `shouldLockdownMediaStoreVersion()`
- `src/com/android/providers/media/DatabaseHelper.java`
  - `getOrCreateUuid(SQLiteDatabase)`

この実装により、lockdown 有効時の戻り値は少なくとも calling UID に依存する。異なる UID のアプリでは同じ MediaProvider database / volume でも同一文字列にならないため、cross-app comparison や device-wide stable identifier としての利用は成立しにくくなる。

### Compat / feature flag

AOSP には次の compat change がある。

- Change ID: `343977174`
- Symbol: `LOCKDOWN_MEDIASTORE_VERSION`
- Annotation: `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)`
- Description in source: MediaStore versioning schema / format を更新し identifying properties を減らす。

`shouldLockdownMediaStoreVersion()` は次の 2 条件を両方要求する。

- MediaProvider aconfig flag `version_lockdown` が true
- `CompatChanges.isChangeEnabled(LOCKDOWN_MEDIASTORE_VERSION, callingUid)` が true

`mediaprovider_flags.aconfig` では `version_lockdown` が `is_fixed_read_only: true` で定義され、説明は MediaStore versioning を apps across でより unique にする flag となっている。

公式 compat framework changes ページでは、2026-07-03 の検索時点で `343977174` / `LOCKDOWN_MEDIASTORE_VERSION` の項目は見つからなかった。このため、force-enable / force-disable 可能性は公式一覧からは確認できない。ただし AOSP 上は `@ChangeId` と `CompatChanges.isChangeEnabled(...)` による compat gate が存在する。

## Observations

### Android 15 baseline と Android 16 target の差分

`android-15.0.0_r36` と `android-16.0.0_r4` の MediaProvider source には、`LOCKDOWN_MEDIASTORE_VERSION`、`versionLockdown()`、`shouldLockdownMediaStoreVersion()`、hash 版 / legacy 版の分岐がどちらの tag にも存在する。

差分としては Android 16 側で `getVersion` の metrics logging と一部 documentation 変更が追加されているが、lockdown 分岐の中心ロジック自体は両 tag で大きく変わっていない。

Interpretation:

- この behavior change は public framework API signature の変更ではない。
- MediaProvider module 内の feature flag + compat change により、Android 16 / targetSdkVersion 36 以上のアプリに対して有効化される behavior と解釈する。
- Android 15 tag に同じ guarded code が存在することから、ソース上の存在だけで Android 15 端末に公式 Android 16 behavior が適用されるとは判断しない。公式 behavior change の適用範囲は Android 16 targeting apps として扱う。

### Previous behavior

lockdown 無効時は `db.getVersion() + ":" + dbUuid` が返る。ここには SQLite database schema version と database UUID が含まれるため、format を parse するアプリ、複数アプリ間で比較するアプリ、device/media database の識別材料として扱うアプリは、意図された opaque token の範囲を超えている。

### Target behavior

lockdown 有効時は `dbUuid + callingUid` の hash が返る。database UUID は入力に残るが、生の `db.getVersion()` と `dbUuid` は返らない。calling UID を混ぜることで、同じ database / volume でも app ごとに異なる token になる。

### Cache invalidation semantics

公式 API doc は従来から、MediaStore を自アプリ cache に import している場合に「substantial changes」を検出する opaque version string として使うことを想定している。Android 16 の実装でも同じ app / same UID / same volume で比較する用途は残る。

ただし lockdown 有効時の実装は `db.getVersion()` を直接含めない。database UUID が変わるケースでは token が変わるが、media item の追加・削除・更新に対する細かい差分追跡には `MediaStore#getGeneration(...)` のほうが適している。version string の内部構造や単調性を仮定してはならない。

## Hypotheses

- app update で UID が維持される場合、same app の version token は database UUID が変わらない限り維持される可能性が高い。
- uninstall / reinstall で UID が変わる場合、同じ package name でも token が変わる可能性がある。
- work profile / secondary user では calling UID と database / user context が異なるため、同じ package name でも token が異なる可能性が高い。
- external / internal volume の扱いは `volumeName` ごとに database selection が変わるため、volume ごとに token が異なる可能性が高い。

これらは AOSP implementation からの推論であり、端末上の実測で確認すべきである。

## Applicability Classification

Primary classification: `TARGET_SDK_36_CONDITIONAL`

根拠:

- 公式文書は apps targeting Android 16 or higher としている。
- AOSP には `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)` がある。
- Provider path は `CompatChanges.isChangeEnabled(LOCKDOWN_MEDIASTORE_VERSION, callingUid)` を確認している。
- さらに MediaProvider flag `versionLockdown()` が true であることが必要。
- 実質的な影響は `MediaStore#getVersion(...)` を呼び、戻り値の format / cross-app equality / identifying properties に依存するアプリに限定される。

OS version condition:

- Android 16 以上の MediaProvider behavior として扱う。
- Android 15 tag に guarded code は存在するが、公式 Android 16 behavior としての適用は Android 16 scope で説明する。

targetSdkVersion condition:

- targetSdkVersion 36 以上で `LOCKDOWN_MEDIASTORE_VERSION` が default enabled。
- targetSdkVersion 35 以下では compat change が default disabled と解釈され、legacy format が維持される見込み。

Compat framework:

- AOSP Change ID: `343977174`
- Default state evidence: `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)`
- Official compat list evidence: 公式 compat framework changes ページでは該当 ID を確認できず。
- Force-enable / force-disable: AOSP compat gate はあるが、公式一覧未掲載のため顧客向けには「adb/app-compat で toggle 可能と断定しない」。

## Expected Behavior Matrix

| Scenario | Expected behavior | Impact |
|---|---|---|
| Android 16 / targetSdkVersion 35 | compat change default disabled。legacy `db.getVersion() + ":" + dbUuid` が返る見込み | OS update だけでは target 36 behavior は原則適用されない |
| Android 16 / targetSdkVersion 36 | `versionLockdown()` かつ compat enabled なら `hash(dbUuid + uid)` が返る | app ごとに unique。format parsing / cross-app comparison が壊れる |
| Android 15 / targetSdkVersion 36 | 公式 Android 16 behavior の対象外。tag 上に guarded code はあるが Android 15 端末挙動としては module / flag 依存 | Android 15 上の target 36 検証は参考扱い |

## Detailed Scenario Matrix

| Scenario | Expected behavior / check point |
|---|---|
| Android 16 / targetSdkVersion 36 / `MediaStore#getVersion(Context)` | `VOLUME_EXTERNAL_PRIMARY` の opaque token を返す。lockdown 有効なら calling UID に依存 |
| Android 16 / targetSdkVersion 36 / `MediaStore#getVersion(Context, volumeName)` | 指定 volume の database から token を返す。volume ごとに値が変わる可能性が高い |
| same app / repeated calls | database UUID と UID が同じなら安定する見込み |
| different apps / same device / same volume | UID が異なるため異なる token になる見込み |
| same app / after media DB changes | version API の intended use は substantial changes 検出。細かい item 差分は generation API で検証すべき |
| app update with same package | UID が維持される通常 update では token も維持される可能性が高い |
| app reinstall | UID 変更により token が変わる可能性がある |
| different Android users / profiles | UID / user context が異なり token が変わる可能性が高い |
| external volume | 指定 volume の database UUID に依存 |
| internal volume | volumeName が許容される場合は別 token になる可能性 |
| app parses version format | legacy の `number:uuid` 前提は破綻する |
| app only checks equality for own cache invalidation | 原則継続可能。ただし null / volume unavailable / reinstall などは扱う |
| app compares version across apps or devices | Android 16 target では成立しない前提として修正が必要 |

## Developer Impact

影響を受ける可能性が高いアプリ:

- `MediaStore#getVersion()` を使っているアプリ
- MediaStore version を自アプリ内 cache invalidation に使っているアプリ
- MediaStore version を複数アプリ間・複数端末間で比較しているアプリ
- MediaStore version string を parse / pattern-match しているアプリ
- MediaStore version から media database / provider / build / storage 状態を推測しているアプリ
- 写真・動画・音楽・ファイル管理・ギャラリー・バックアップ・同期アプリ
- media indexer / scanner state に依存するアプリ
- privacy / anti-fingerprinting 要件に関係する SDK / analytics library

自アプリ内の cache invalidation token として equality comparison だけを行う場合は、多くのケースで変更不要と考えられる。一方で、`:` 区切りを parse する、version number を取り出す、UUID を device/media database identifier として扱う、複数アプリ間で値を照合する実装は修正対象である。

## Recommended Action Candidates

- `MediaStore#getVersion(...)` の戻り値を opaque string として扱い、format parsing を削除する。
- cross-app / cross-device correlation の input として使わない。
- 自アプリ cache invalidation では、保存済み token との equality comparison のみに留める。
- media item 単位の差分検出には `MediaStore#getGeneration(...)` / generation-based query を検討する。
- app update / reinstall / work profile / volume unavailable 時の fallback を実装する。
- SDK / analytics library が MediaStore version を fingerprinting input にしていないか確認する。

## Test Considerations

- Android 15 端末上の targetSdkVersion 35
- Android 16 端末上の targetSdkVersion 35
- Android 16 端末上の targetSdkVersion 36
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較
- 同一アプリで `getVersion()` を複数回呼んだ場合の安定性
- 異なるアプリで `getVersion()` を呼んだ場合の値の違い
- `getVersion(Context)` と `getVersion(Context, volumeName)` の違い
- media item 追加 / 削除 / 更新後の version 変化
- app update / reinstall 後の version 変化
- work profile / secondary user での version 変化
- external storage / internal storage / volumeName ごとの違い
- version string format を parse する既存コードの互換性
- cache invalidation が正しく動くか
- fingerprinting / cross-app correlation に使えなくなることの確認

## Conclusions

- Android 16 target では `MediaStore#getVersion(...)` の戻り値が app ごとに unique になる behavior change として扱うべきである。
- AOSP evidence は `LOCKDOWN_MEDIASTORE_VERSION` Change ID、`@EnabledSince(BAKLAVA)`、`CompatChanges.isChangeEnabled(... uid)`、`hash(dbUuid + uid)` による戻り値生成で公式文書を支持している。
- targetSdkVersion 35 以下の Android 16 アプリには default では適用されない見込みであり、「Android 16 へ OS update しただけの影響」と「targetSdkVersion 36 化した時の影響」は分けて説明する必要がある。
- 自アプリ内 cache invalidation のための opaque equality token として使う実装は大きな変更不要の可能性が高い。
- format parsing、cross-app comparison、device / database / storage 状態の推測、fingerprinting input としての利用は Android 16 target で修正が必要である。

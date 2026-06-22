# Android 17 をターゲットにするアプリで必要になるローカルネットワーク権限 - 1ページ要約

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

- 主分類（Primary classification）: TARGET_SDK_37_CONDITIONAL
- OS アップデート / 全アプリ（OS update / all apps）: 主条件ではない。旧 targetSdkVersion は compat / implicit grant の対象と考えられるが、connectivity module evidence が未確認。
- targetSdkVersion 37 以上: 該当。
- その他の必須条件（Other required conditions）: direct local network access、LAN device discovery / connection、`ACCESS_LOCAL_NETWORK` grant state、system picker 利用有無、`access_local_network_permission_enabled` flag。
- Compat Change ID: `365139289L`
- Compat default state: frameworks-base では未確認。`MediaRouter2ServiceImpl` はこの ID を connectivity module の `RESTRICT_LOCAL_NETWORK` として参照する。

## 早見マトリクス

| シナリオ | 影響 |
| --- | --- |
| Android 17 / targetSdkVersion 36 | legacy app として permission check が免除または implicit grant される想定。ただし final enforcement は connectivity module で要確認。 |
| Android 17 / targetSdkVersion 37 | direct local network access には system picker または `ACCESS_LOCAL_NETWORK` runtime grant が必要。 |
| Android 17 / targetSdkVersion 37 + permission denied | LAN device discovery / connection、mDNS / NSD、casting、IoT、local endpoint socket access が失敗する可能性。 |

## 要約

Android 17 では、targetSdkVersion 37 以上のアプリが LAN 上の device を discover / connect する場合、新しい `ACCESS_LOCAL_NETWORK` runtime permission または system-mediated picker が必要になる。AOSP `frameworks-base` では permission 定義、API surface、AppOps、permission policy、BPF permission map、MediaRouter の compat path まで確認できた。

信頼度は Medium。`frameworks-base` は permission infrastructure を裏付けるが、network traffic の実 enforcement と `RESTRICT_LOCAL_NETWORK` の定義本体は connectivity module 側の追加確認が必要。

## 顧客影響

- smart home、IoT、casting、mDNS / NSD、`.local` resolution、local endpoint socket、WebView local network access を使うアプリは targetSdkVersion 37 更新時に影響を受ける可能性が高い。
- system-mediated picker で要件を満たせる場合は、広い runtime permission request を避けられる。
- direct / persistent access が必要な場合は、manifest declaration、runtime request、denial / revocation handling が必要。

## 対応要否

- 必須対応候補: local network access 箇所を棚卸しし、picker path と runtime permission path のどちらを採用するか決める。
- 推奨対応: Android 17 / targetSdkVersion 37 で permission 未許可、許可、取り消し後の動作をテストする。
- 不要な可能性: local network access を行わないアプリ、または system-mediated picker だけで要件を満たすアプリ。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 36 | 従来どおり local network access が許可される想定。 |
| Android 17 | 36 | legacy app として compat exemption / implicit grant が働く想定。 |
| Android 17 | 37 | direct local network access は `ACCESS_LOCAL_NETWORK` grant または picker path が必要。 |

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-17
- Permission reference: https://developer.android.com/reference/android/Manifest.permission#ACCESS_LOCAL_NETWORK
- AOSP: `core/res/AndroidManifest.xml` に `ACCESS_LOCAL_NETWORK` dangerous permission が追加。
- AOSP: `core/api/current.txt` に `Manifest.permission.ACCESS_LOCAL_NETWORK` が追加。
- AOSP: `core/java/android/app/AppOpsManager.java` に `OPSTR_ACCESS_LOCAL_NETWORK` と permission linkage が追加。
- AOSP: `AppIdPermissionPolicy.kt` / `DefaultPermissionGrantPolicy.java` が nearby devices permission set に `ACCESS_LOCAL_NETWORK` を含める。
- AOSP: `PermissionService.kt` / `PermissionManagerLocal.java` / `PermissionBpfMap.java` が permission state を BPF map へ配布する基盤を追加。
- AOSP: `MediaRouter2ServiceImpl.java` が ChangeId `365139289L` を `RESTRICT_LOCAL_NETWORK` として扱い、compat change disabled の uid では permission を満たした扱いにする。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断

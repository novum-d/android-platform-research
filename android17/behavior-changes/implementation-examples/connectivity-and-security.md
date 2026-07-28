# Android 17 Connectivity and Security 対応例

## 位置づけ

このファイルは、Android 17のconnectivity / security変更をアプリ実装、設定、試験へ落とす
companionである。適用条件、AOSP evidence、confidenceは各主レポートを正とする。

- [Android 16→17挙動比較](../version-comparisons/connectivity-and-security.md)
- [対応例テンプレート](../../templates/implementation-examples-template.md)

## 対象と適用条件

| 項目 | Android 17での主な適用条件 | 主レポート |
| --- | --- | --- |
| Bluetooth autonomous re-pairing | OS update、feature flag、bond loss | [Report](../all/connectivity/autonomous-repairing-bluetooth-bond-losses.md) |
| RFCOMM read EOF | Android 17 + targetSdkVersion 37、RFCOMM close / drop | [Report](../target/connectivity/consistent-bluetoothsocket-read-rfcomm.md) |
| Cleartext migration | Android 17では移行guidance。runtime一律blockではない | [Report](../all/security/usescleartexttraffic-deprecation-plan.md) |
| Explicit URI grants | Android 17では将来変更に向けた検出・移行 | [Report](../all/security/restrict-implicit-uri-grants.md) |
| Per-app Keystore limits | OS update。limit値とerror codeはtarget / app typeで異なる | [Report](../all/security/per-app-keystore-limits.md) |
| Cross-profile loopback block | OS update、profile境界を越えるloopback | [Report](../all/security/block-cross-profile-loopback-traffic.md) |
| Activity Security | Android 17 + targetSdkVersion 37、BAL条件 | [Report](../target/security/activity-security.md) |
| Certificate Transparency | Android 17 + targetSdkVersion 37、platform TLS条件 | [Report](../target/security/enable-ct-by-default.md) |
| Native DCL-C | Android 17 + targetSdkVersion 37、writable native file load | [Report](../target/security/safer-native-dcl-c.md) |
| CP2 PII / strict SQL | Android 17 + targetSdkVersion 37、query / permission条件 | [PII](../target/security/restrict-pii-fields-cp2-data-view.md) / [SQL](../target/security/enforce-strict-sql-checks-cp2.md) |

## 既存実装の検出

```bash
rg -n "ACTION_BOND_STATE_CHANGED|ACTION_PAIRING_REQUEST|ACTION_KEY_MISSING|createBond|removeBond" app src
rg -n "BluetoothSocket|InputStream|read\\(" app src
rg -n "ACTION_SEND|ACTION_SEND_MULTIPLE|ACTION_IMAGE_CAPTURE|EXTRA_OUTPUT|ClipData" app src
rg -n "MODE_BACKGROUND_ACTIVITY_START|setPendingIntentBackgroundActivityStartMode" app src
rg -n "AndroidKeyStore|KeyGenerator|KeyPairGenerator|deleteEntry|KeyStoreException" app src
rg -n "127\\.0\\.0\\.1|::1|localhost|System\\.load|System\\.loadLibrary|\\.so" app src
rg -n "ContactsContract\\.Data|ACCOUNT_NAME|ACCOUNT_TYPE|selectionArgs|sortOrder" app src
```

## 例1: Android 17のBluetooth autonomous re-pairingと競合しない

Android 17 / API 37で追加されたpairing contextを読み、systemによる修復中は
アプリ独自の`createBond()`、pairing UI、timeout recoveryを開始しない。

```kotlin
import android.bluetooth.BluetoothDevice
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.os.Build

sealed interface BondRecoveryState {
    data object Idle : BondRecoveryState
    data object RepairingBySystem : BondRecoveryState
    data object Bonded : BondRecoveryState
    data object ManualRecoveryRequired : BondRecoveryState
}

class BondRecoveryReceiver(
    private val updateState: (BondRecoveryState) -> Unit,
) : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val repairingBySystem =
            Build.VERSION.SDK_INT >= 37 &&
                intent.getIntExtra(
                    BluetoothDevice.EXTRA_PAIRING_CONTEXT,
                    -1,
                ) == BluetoothDevice.PAIRING_CONTEXT_REPAIRING

        when (intent.action) {
            BluetoothDevice.ACTION_PAIRING_REQUEST -> {
                if (repairingBySystem) {
                    updateState(BondRecoveryState.RepairingBySystem)
                    // app独自pairing開始や重複dialog表示を行わない。
                }
            }

            BluetoothDevice.ACTION_BOND_STATE_CHANGED -> {
                when (
                    intent.getIntExtra(
                        BluetoothDevice.EXTRA_BOND_STATE,
                        BluetoothDevice.ERROR,
                    )
                ) {
                    BluetoothDevice.BOND_BONDING ->
                        if (repairingBySystem) {
                            updateState(BondRecoveryState.RepairingBySystem)
                        }

                    BluetoothDevice.BOND_BONDED ->
                        updateState(BondRecoveryState.Bonded)

                    BluetoothDevice.BOND_NONE -> {
                        // 直ちに再pairingしない。repair failure signalかuser操作を待つ。
                    }
                }
            }

            BluetoothDevice.ACTION_KEY_MISSING ->
                updateState(BondRecoveryState.ManualRecoveryRequired)
        }
    }
}
```

API 37未満では新extraを参照せず、従来flowを維持する。
receiverの登録方法、exported設定、`BLUETOOTH_CONNECT`の扱いは、
既存アプリのtarget APIと利用するbroadcastの公式API contractに合わせる。

状態遷移:

```text
bond loss
  -> RepairingBySystem
      -> BOND_BONDED: reconnect
      -> ACTION_KEY_MISSING: manual recovery UI
```

自動修復中の`BOND_NONE`だけを根拠にperipheral登録情報を削除しない。
成功時に`ACTION_KEY_MISSING`が届くことも前提にしない。

試験:

- peripheral側だけのbond情報を削除し、自動修復成功を確認する。
- peripheralを応答不能にし、失敗後の`ACTION_KEY_MISSING`とmanual recoveryを確認する。
- user confirmationのaccept / reject、app foreground / background、process recreationを分ける。
- system dialogとapp dialogが重複しないことを確認する。

## 例2: RFCOMM read loopでEOFとexceptionの両方を終了扱いにする

```kotlin
import android.bluetooth.BluetoothSocket
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.isActive
import kotlinx.coroutines.withContext
import java.io.IOException

suspend fun readRfcomm(
    socket: BluetoothSocket,
    onBytes: (ByteArray) -> Unit,
    onDisconnected: (Throwable?) -> Unit,
) = withContext(Dispatchers.IO) {
    val buffer = ByteArray(8 * 1024)
    try {
        while (currentCoroutineContext().isActive) {
            val count = socket.inputStream.read(buffer)
            if (count == -1) {
                onDisconnected(null)
                break
            }
            if (count > 0) {
                onBytes(buffer.copyOf(count))
            }
        }
    } catch (error: IOException) {
        onDisconnected(error)
    } finally {
        runCatching { socket.close() }
    }
}
```

`read() == -1`でloopを継続するとbusy loopまたは切断検知漏れになる。
Android 16でexception、Android 17 / target 37でEOFになる経路を同じdisconnect eventへ集約する。

## 例3: URI grantをIntentへ明示する

単一URIの共有:

```kotlin
val shareIntent = Intent(Intent.ACTION_SEND).apply {
    type = "image/jpeg"
    putExtra(Intent.EXTRA_STREAM, contentUri)
    clipData = ClipData.newUri(contentResolver, "shared image", contentUri)
    addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
}
startActivity(Intent.createChooser(shareIntent, null))
```

camera出力:

```kotlin
val captureIntent = Intent(MediaStore.ACTION_IMAGE_CAPTURE).apply {
    putExtra(MediaStore.EXTRA_OUTPUT, outputUri)
    clipData = ClipData.newUri(contentResolver, "camera output", outputUri)
    addFlags(
        Intent.FLAG_GRANT_READ_URI_PERMISSION or
            Intent.FLAG_GRANT_WRITE_URI_PERMISSION,
    )
}
cameraLauncher.launch(captureIntent)
```

複数URIでは全URIを`ClipData`へ含める。
`file://`へ戻したり、providerを広くexportしたり、永続grantを不要に付けたりしない。
受信側packageが決まっている特殊flowでは、必要最小限のURIと期間を検討する。

## 例4: Cleartext許可をdomain単位へ絞る

Manifest:

```xml
<application
    android:networkSecurityConfig="@xml/network_security_config"
    android:usesCleartextTraffic="false"
    ... />
```

移行中の限定domainだけを一時許可する:

```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="false" />
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="false">legacy-device.example</domain>
    </domain-config>
</network-security-config>
```

API 24未満もsupportする場合は、Manifest fallbackの挙動を別途確認する。
cleartext許可には対象endpoint、owner、TLS移行条件、削除期限を残す。
Android 17で`usesCleartextTraffic`が突然無効になる例ではない。

## 例5: PendingIntent送信時のBAL privilegeをvisible条件へ絞る

```kotlin
import android.app.ActivityOptions
import android.app.PendingIntent
import android.content.Context
import android.os.Build

fun sendFromVisibleUi(
    context: Context,
    pendingIntent: PendingIntent,
) {
    val options = ActivityOptions.makeBasic()
    // ALLOW_IF_VISIBLEはAPI 36で追加済み。Android 17移行前から利用できる。
    if (Build.VERSION.SDK_INT >= 36) {
        options.setPendingIntentBackgroundActivityStartMode(
            ActivityOptions.MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE,
        )
    }

    pendingIntent.send(
        context,
        0,
        null,
        null,
        null,
        null,
        options.toBundle(),
    )
}
```

送信元がbackgroundなら、`ALLOW_IF_VISIBLE`でActivityが開かないことを正常系として扱い、
notificationや既存画面のin-app stateへ誘導する。
`ALLOW_ALWAYS`はconnected deviceなどの正当なBAL exceptionを満たす限定flowでのみ検討し、
用途、threat model、削除条件を記録する。

## 例6: Keystore key数をbounded lifecycleで管理する

key creation失敗を一括catchして握りつぶさず、API 37では専用errorを診断する。

```kotlin
import android.os.Build
import android.security.KeyStoreException

private tailrec fun findAndroidKeyStoreException(
    error: Throwable?,
): KeyStoreException? = when (error) {
    null -> null
    is KeyStoreException -> error
    else -> findAndroidKeyStoreException(error.cause)
}

fun <T> createOrLoadKey(
    alias: String,
    loadExisting: () -> T?,
    create: () -> T,
    onLimitReached: (String) -> Unit,
): T {
    loadExisting()?.let { return it }

    try {
        return create()
    } catch (error: Exception) {
        // 利用するJCA APIによってはProviderException等のcauseに入る場合も扱う。
        val keyStoreError = findAndroidKeyStoreException(error)
        val tooManyKeys =
            Build.VERSION.SDK_INT >= 37 &&
                keyStoreError?.numericErrorCode == KeyStoreException.ERROR_TOO_MANY_KEYS

        if (tooManyKeys) {
            onLimitReached(alias)
        }
        throw error
    }
}
```

対応の中心はexception retryではなく、alias reuse、rotation後の旧key削除、
account削除時のcleanup、transaction失敗時のorphan回収である。
通常の試験でlimit到達まで数万keyを作るのではなく、key lifecycleのcount / cleanupを
fake repositoryで検証し、実機limit試験は隔離したtest packageで計画する。

## 例7: Dynamic native libraryをload前にread-only化する

可能ならdynamic native code loading自体を廃止し、APK / App Bundleへ同梱する。
やむを得ず生成・展開する場合は、完全に書き終え、closeし、read-only化してからloadする。

```kotlin
fun loadVerifiedNativeLibrary(
    destination: File,
    expectedSha256: String,
) {
    check(destination.isFile)
    // sha256()は、アプリ側で実装するstreaming hash検証関数。
    check(sha256(destination).equals(expectedSha256, ignoreCase = true))
    check(destination.setReadOnly()) {
        "Failed to make native library read-only: ${destination.name}"
    }
    check(!destination.canWrite()) {
        "Native library remained writable: ${destination.name}"
    }
    System.load(destination.absolutePath)
}
```

実装では、app-private directory、atomic rename、signature / hash検証、symlink拒否、
同時更新の排他、失敗時cleanupも必要である。load後に同じfileを再びwritableにしない。

## 例8: CP2 Data queryとaccount queryを分離する

Data viewでは`RAW_CONTACT_ID`だけを取得し、account情報が本当に必要な処理だけ
`RawContacts`へ問い合わせる。

```kotlin
val dataProjection = arrayOf(
    ContactsContract.Data._ID,
    ContactsContract.Data.RAW_CONTACT_ID,
    ContactsContract.Data.MIMETYPE,
)

val rawContactIds = buildSet<Long> {
    contentResolver.query(
        ContactsContract.Data.CONTENT_URI,
        dataProjection,
        "${ContactsContract.Data.MIMETYPE} = ?",
        arrayOf(ContactsContract.CommonDataKinds.Email.CONTENT_ITEM_TYPE),
        null,
    )?.use { cursor ->
        val idIndex = cursor.getColumnIndexOrThrow(
            ContactsContract.Data.RAW_CONTACT_ID,
        )
        while (cursor.moveToNext()) add(cursor.getLong(idIndex))
    }
}
```

`RawContacts`側:

```kotlin
val rawProjection = arrayOf(
    ContactsContract.RawContacts._ID,
    ContactsContract.RawContacts.ACCOUNT_NAME,
    ContactsContract.RawContacts.ACCOUNT_TYPE,
)

val selection = rawContactIds.joinToString(
    prefix = "${ContactsContract.RawContacts._ID} IN (",
    postfix = ")",
    separator = ",",
) { "?" }

val args = rawContactIds.map(Long::toString).toTypedArray()
contentResolver.query(
    ContactsContract.RawContacts.CONTENT_URI,
    rawProjection,
    selection,
    args,
    null,
)?.use { cursor ->
    // 必要最小限のaccount metadataを処理する。
}
```

空のID集合ではqueryを実行しない。大量IDはchunk化する。
selectionへ値を文字列連結せず`selectionArgs`を使い、projection、selection、sort orderを
documented column / grammarへ限定する。
`READ_CONTACTS`あり / なし、target 36 / 37、Contact Picker session経路を分けて試験する。

## 設定だけでは解決しない項目

### Cross-profile loopback

`127.0.0.1`、`::1`、`localhost`を別profileとのIPCとして使わない。
同一profile内loopbackは維持しつつ、profile境界はsupported cross-profile API、
Binder、明示的に認証されたnetwork endpointへ設計変更する。
一般アプリからblockを解除する設定例は置かない。

### Certificate Transparency

production、staging、private PKI、pinning対象をinventory化し、
Android 17 / target 37のplatform TLSでcertificate chainとCT log inclusionを確認する。
自前TLS stackやWebViewは別経路として扱う。
security要件を全体解除する汎用例は置かず、endpoint / certificateの是正を優先する。

## 検証マトリクス

| Case | Android 16 / target 36 | Android 17 / target 36 | Android 17 / target 37 |
| --- | --- | --- | --- |
| Bluetooth bond loss | user-driven recovery | autonomous repair | target 36と同じOS条件 |
| RFCOMM peer close | exception中心 | legacy compatibility | EOF `-1` |
| URI grant明示 | recipientが読める | recipientが読める | recipientが読める |
| Keystore lifecycle | cleanup baseline | 200k上限条件 | non-system 50k / dedicated error |
| Cross-profile loopback |到達し得る | block | block |
| PendingIntent from visible UI | legacy mode | compatibility | `ALLOW_IF_VISIBLE` |
| PendingIntent from background |既存条件 | compatibility | blockを正常処理 |
| CT不適合chain | opt-in時failure | opt-in時failure | default条件でfailure |
| Writable native `.so` | loadし得る | compatibility | `UnsatisfiedLinkError` |
| CP2 legacy query |通り得る | compatibility | projection / SQL restriction |

## 完了条件

- Bluetooth自動修復中にapp独自repairを開始しない。
- RFCOMM EOFと`IOException`を同じdisconnect stateへ収束させる。
- URI grantをactionとURIごとに明示した。
- cleartext許可、BAL privilege、CT例外を全体へ広げていない。
- Keystore aliasの作成・再利用・rotation・削除を計測できる。
- Dynamic native fileは検証・close・read-only化後にだけloadする。
- CP2のData projection、account lookup、SQL grammarを分離した。
- Android 17 / target 36とtarget 37を分けて結果を記録した。

## References

- [Connectivity and Security挙動比較](../version-comparisons/connectivity-and-security.md)
- [Android 17 Behavior Changes一覧](../README.md)

## Human Decision

この対応例では最終priority、severity、release readinessを決定しない。

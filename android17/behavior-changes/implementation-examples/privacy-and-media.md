# Android 17 Privacy and Media 対応例

## 位置づけ

このファイルは、Android 17のprivacy / media変更をアプリ実装、設定、試験へ落とす
companionである。適用条件、AOSP evidence、confidenceは各主レポートを正とする。

- [Android 16→17挙動比較](../version-comparisons/privacy-and-media.md)
- [対応例テンプレート](../../templates/implementation-examples-template.md)

## 対象と適用条件

| 項目 | Android 17での主な適用条件 | 主レポート |
| --- | --- | --- |
| SMS OTP protection | OS updateでall appsに関係。標準SMS受信経路が対象 | [Report](../all/privacy/sms-otp-protection.md) |
| OTP protection for standard SMS | targetSdkVersion 37側の追加条件を含む | [Report](../target/privacy/otp-protection-standard-sms.md) |
| Local Network Permission | Android 17 + targetSdkVersion 37を中心に、LAN access時 | [Report](../target/privacy/local-network-permission.md) |
| Encrypted Client Hello | Android 17 + targetSdkVersion 37。platform TLS / Network Security Config | [Report](../target/privacy/ech-encrypted-client-hello.md) |
| Physical password masking | Android 17 + targetSdkVersion 37。physical inputと標準/custom widget条件 | [Report](../target/privacy/hiding-passwords-physical-devices.md) |
| Background audio hardening | OS update項目とtarget 37項目の両方 | [All apps](../all/media/background-audio-hardening.md) / [Target 37](../target/media/background-audio-hardening.md) |

## 既存実装の検出

```bash
rg -n "RECEIVE_SMS|READ_SMS|SMS_RECEIVED|Telephony\\.Sms" app src
rg -n "SmsRetriever|startSmsUserConsent|otp|one.?time|verification.?code" app src
rg -n "DatagramSocket|MulticastSocket|ServerSocket|Socket\\(|NsdManager|WifiManager" app src
rg -n "networkSecurityConfig|domainEncryption|usesCleartextTraffic" app src
rg -n "PasswordTransformationMethod|TYPE_TEXT_VARIATION_PASSWORD|setTransformationMethod" app src
rg -n "requestAudioFocus|startForeground|mediaPlayback|SCHEDULE_EXACT_ALARM" app src
```

## 例1: OTPをSMS inbox直接読取からuser-mediated flowへ移す

標準SMSのOTPをアプリ側で広く受信・検索する設計は、OS protectionと競合しやすい。
認証providerとmessage formatを調整できる場合はSMS Retriever、
特定messageをuserが選択して許可する場合はSMS User Consentを検討する。

SMS Retriever開始の最小例:

```kotlin
import android.content.Context
import com.google.android.gms.auth.api.phone.SmsRetriever

fun startOtpRetrieval(context: Context, onUnavailable: (Exception) -> Unit) {
    SmsRetriever.getClient(context)
        .startSmsRetriever()
        .addOnFailureListener(onUnavailable)
}
```

この後のbroadcast受信、messageからのcode抽出、timeout、lifecycle解除は
利用中のGoogle Play services APIの公式手順に合わせる。
message本文全体をanalyticsやcrash reportへ送らない。

fallback UX:

```kotlin
data class OtpUiState(
    val code: String = "",
    val autoRetrieveAvailable: Boolean = true,
    val errorMessage: String? = null,
)

fun onAutoRetrieveUnavailable(state: OtpUiState): OtpUiState =
    state.copy(
        autoRetrieveAvailable = false,
        errorMessage = "確認コードを手動で入力してください",
    )
```

検証では、正常受信だけでなく、timeout、複数SMS、誤ったcode、user拒否、
Play servicesなし、process recreationを含める。

## 例2: Local Network Permissionを機能開始時に要求する

Manifest（targetSdkVersion 37へ更新するbuildで追加）:

```xml
<uses-permission android:name="android.permission.ACCESS_LOCAL_NETWORK" />
```

API 37 symbolを参照するため、この例はcompileSdk 37を前提とする。
targetSdkVersion 36以下のbuildでは、公式guidanceどおりpermissionを追加・要求せず、
`INTERNET` permissionによる一時的な互換動作を確認する。
app起動直後ではなく、local device discovery、LAN server接続、multicast利用など、
利用者が機能を開始した時点で要求する。

```kotlin
import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import androidx.activity.ComponentActivity
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat

class LocalDeviceActivity : ComponentActivity() {
    private val requestLocalNetwork =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
            if (granted) {
                startLocalDeviceDiscovery()
            } else {
                showLocalNetworkUnavailable()
            }
        }

    fun onDiscoverDevicesClicked() {
        if (
            Build.VERSION.SDK_INT < 37 ||
            applicationInfo.targetSdkVersion < 37
        ) {
            startLocalDeviceDiscovery()
            return
        }

        when {
            ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.ACCESS_LOCAL_NETWORK,
            ) == PackageManager.PERMISSION_GRANTED -> startLocalDeviceDiscovery()

            else -> requestLocalNetwork.launch(Manifest.permission.ACCESS_LOCAL_NETWORK)
        }
    }

    private fun startLocalDeviceDiscovery() {
        // NSD、multicast、LAN socketなど、対象機能をここから開始する。
    }

    private fun showLocalNetworkUnavailable() {
        // cloud経由や手動入力など、権限不要の代替があれば提示する。
    }
}
```

denial後にsocket retry loopを継続しない。設定画面でのrevoke、one-time state、
app process recreation後も、接続開始直前に現在のpermission stateを再確認する。

試験対象はIPv4/IPv6、unicast/multicast、NSD、device discovery、direct IP入力、
VPN、hotspotなど、アプリが実際に使う経路だけに絞る。

## 例3: ECH policyをNetwork Security Configで明示する

Manifest:

```xml
<application
    android:networkSecurityConfig="@xml/network_security_config"
    ... />
```

ECHを利用するdomainの例:

```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config>
        <domain includeSubdomains="true">api.example.com</domain>
        <domainEncryption mode="enabled" />
    </domain-config>
</network-security-config>
```

移行できていない限定domainだけを一時除外する例:

```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config>
        <domainEncryption mode="enabled" />
    </base-config>

    <domain-config>
        <domain includeSubdomains="false">legacy.example.com</domain>
        <domainEncryption mode="disabled" />
    </domain-config>
</network-security-config>
```

`disabled`を全domainへ広げるのではなく、対象hostname、理由、owner、削除期限を残す。
自前のTLS stackやWebViewなど、platform TLS policyがそのまま適用されない経路は別に確認する。
DNS resolver、network、endpointのECH対応差も含めて実機試験する。

## 例4: Physical keyboard向けに独自password revealを行わない

標準widgetで足りる場合は、platform maskingへ委ねる。

```xml
<EditText
    android:id="@+id/password"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:autofillHints="password"
    android:importantForAutofill="yes"
    android:inputType="textPassword" />
```

避ける実装:

```kotlin
// 入力元に関係なく末尾文字を独自に一定時間表示する。
passwordEditText.transformationMethod = CustomRevealLastCharacterTransformation()
```

独自editorが必要な場合は、software IMEとphysical keyboardを混同したheuristicではなく、
標準`InputType`、accessibility semantics、autofillを保つ。
画面録画、shoulder surfing、accessibility serviceの観点を含め、
USB / Bluetooth keyboardとon-screen keyboardを分けて試験する。

## 例5: Background audioをuser action、audio focus、FGSへ揃える

audio focus requestの結果を必ず処理する。

```kotlin
import android.media.AudioAttributes
import android.media.AudioFocusRequest
import android.media.AudioManager

class PlaybackFocusController(
    private val audioManager: AudioManager,
    onFocusChange: (Int) -> Unit,
) {
    private val request = AudioFocusRequest.Builder(AudioManager.AUDIOFOCUS_GAIN)
        .setAudioAttributes(
            AudioAttributes.Builder()
                .setUsage(AudioAttributes.USAGE_MEDIA)
                .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
                .build(),
        )
        .setOnAudioFocusChangeListener { change -> onFocusChange(change) }
        .build()

    fun acquire(): Boolean =
        audioManager.requestAudioFocus(request) ==
            AudioManager.AUDIOFOCUS_REQUEST_GRANTED

    fun release() {
        audioManager.abandonAudioFocusRequest(request)
    }
}
```

media playback foreground service:

```xml
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK" />

<application ...>
    <service
        android:name=".playback.PlaybackService"
        android:exported="false"
        android:foregroundServiceType="mediaPlayback" />
</application>
```

service開始は明示的なuser playback actionと結び付け、開始後すぐにmedia notificationを表示する。
alarm、receiver、background taskから無条件に再生を再開しない。
target 37でbackgroundからaudio APIを使う場合、foreground serviceの宣言・起動だけでは十分とは
限らず、主レポートにあるWIU capabilityまたはexact alarm + `USAGE_ALARM`条件も確認する。
exact alarm exceptionは、background audio全般の回避策として利用しない。

## 検証マトリクス

| Case | Android 16 / target 36 | Android 17 / target 36 | Android 17 / target 37 |
| --- | --- | --- | --- |
| SMS Retriever / manual fallback | success / timeout | OS protection下でも正規flowを確認 | target 37条件も確認 |
| LAN discovery | permissionなしbaseline | compatibility behaviorを記録 | grant / denial / revoke |
| ECH対応endpoint | existing TLS | compatibility behavior | enabled / disabled domain差 |
| Physical keyboard password | baseline masking | compatibility behavior |文字露出なし |
| User-start playback | focus / FGS success | all-app hardeningを確認 | target 37追加条件も確認 |
| Background restart |既存behavior | block / failureを処理 | target 37追加条件も確認 |

## 完了条件

- OTP自動取得失敗時にmanual inputへ戻れる。
- Local Network Permissionのgrant、denial、revoke後に接続状態が一貫する。
- ECHの対象domainと一時除外domainをinventory化した。
- physical keyboard入力でpassword文字を独自表示しない。
- audio focus failureとforeground service開始失敗をUI stateへ反映する。
- Android 17 / target 36とtarget 37を分けて結果を記録した。

## References

- [Privacy and Media挙動比較](../version-comparisons/privacy-and-media.md)
- [Android 17 Behavior Changes一覧](../README.md)

## Human Decision

この対応例では最終priority、severity、release readinessを決定しない。

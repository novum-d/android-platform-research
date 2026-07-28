# Android 17 Core functionality 対応例

## 位置づけ

このファイルは、Android 17のcore functionality変更をアプリ実装と試験へ落とすための
companionである。適用条件、AOSP evidence、confidenceは各主レポートを正とする。

- [Android 16→17挙動比較](../version-comparisons/core-functionality.md)
- [対応例テンプレート](../../templates/implementation-examples-template.md)

## 対象と適用条件

| 項目 | Android 17での主な適用条件 | 主レポート |
| --- | --- | --- |
| App memory limits | OS update。端末構成、RAM、process visibilityにも依存 | [Report](../all/core-functionality/app-memory-limits.md) |
| Lock-free `MessageQueue` | 原則Android 17 + targetSdkVersion 37 | [Report](../target/core-functionality/messagequeue-lock-free.md) |
| `static final`書き換え禁止 | Android 17 + targetSdkVersion 37。mutation方法とfield条件にも依存 | [Report](../target/core-functionality/static-final-fields.md) |

## 既存実装の検出

```bash
rg -n "BitmapFactory|ByteBuffer|LruCache|onTrimMemory|getHistoricalProcessExitReasons" app src
rg -n "MessageQueue|Looper\\.myQueue|setAccessible|declaredField|declaredMethod" app src
rg -n "static final|Field\\.modifiers|SetStatic.*Field|GetStatic.*Field" app src
rg -n "LooperMode|LEGACY|PAUSED" app src
```

検索結果は、アプリ本体、instrumentation test、unit test、同梱SDK、JNIの順に分類する。
単に文字列が一致しただけの箇所は影響ありと断定しない。

## 例1: MemoryLimiterによる終了を既存のprocess deathと統合する

Android 17では、端末側で有効な場合にapp process別memory limitが設定され得る。
アプリはlimiter固有の再起動処理を増やすのではなく、通常のprocess recreationを成立させた上で、
診断情報に終了履歴を加える。

```kotlin
import android.app.ActivityManager
import android.app.ApplicationExitInfo
import android.content.Context

data class ExitDiagnostic(
    val reason: Int,
    val description: String?,
    val timestampMillis: Long,
    val memoryLimiterRelated: Boolean,
)

fun recentExitDiagnostics(context: Context): List<ExitDiagnostic> {
    val activityManager = context.getSystemService(ActivityManager::class.java)
    return activityManager
        .getHistoricalProcessExitReasons(null, 0, 10)
        .map { exit ->
            ExitDiagnostic(
                reason = exit.reason,
                description = exit.description,
                timestampMillis = exit.timestamp,
                // reasonだけで判定しない。現在のAOSPではdescriptionも診断signalになる。
                memoryLimiterRelated =
                    exit.description?.contains("MemoryLimiter", ignoreCase = true) == true,
            )
        }
}
```

`description`は診断用signalであり、アプリのbusiness logicを切り替える安定APIとして扱わない。
取得した履歴には必要最小限のmetadataだけを残し、user dataや機密情報を加えない。

大きなcacheは上限なしのcollectionではなく、明示的なbudgetを持たせる。

```kotlin
import android.util.LruCache

class PreviewCache(maxBytes: Int) {
    private val cache = object : LruCache<String, ByteArray>(maxBytes) {
        override fun sizeOf(key: String, value: ByteArray): Int = value.size
    }

    fun put(id: String, bytes: ByteArray) {
        cache.put(id, bytes)
    }

    fun clear() {
        cache.evictAll()
    }
}
```

`ComponentCallbacks2.onTrimMemory()`では再生成可能なcacheを解放する。
ただしcallbackだけを頼りにせず、image decode size、video buffer、native allocation、
同時処理数にも上限を設ける。

端末条件と手動試験:

```bash
adb shell am memory-limiter status
adb shell pidof com.example.app
adb shell am memory-limiter manual <pid> 25
adb shell dumpsys activity exit-info com.example.app
adb shell am memory-limiter manual <pid> none
```

`manual`の値は端末のtotal RAMに対する1〜99のpercentageであり、上の`25`は検証例である。
利用可否と現在のsyntaxは対象buildのcommand helpでも確認する。
process終了後に、保存済みnavigation state、編集中data、再送可能な処理が復元できることを確認する。

## 例2: `MessageQueue`のprivate構造依存をpublic APIへ移す

避ける実装:

```kotlin
// Private field名と内部layoutに依存するため、Android 17で維持されない。
val field = android.os.MessageQueue::class.java.getDeclaredField("mMessages")
field.isAccessible = true
val head = field.get(android.os.Looper.myQueue())
```

待機中処理をtestから確認するためにprivate queueを読むのではなく、
実行境界をinterface化してtest doubleへ差し替える。

```kotlin
import android.os.Handler
import android.os.Looper

fun interface TaskDispatcher {
    fun dispatch(task: () -> Unit)
}

class MainThreadDispatcher(
    private val handler: Handler = Handler(Looper.getMainLooper()),
) : TaskDispatcher {
    override fun dispatch(task: () -> Unit) {
        check(handler.post(task)) { "Main looper is exiting" }
    }
}

class RecordingDispatcher : TaskDispatcher {
    private val pending = ArrayDeque<() -> Unit>()

    override fun dispatch(task: () -> Unit) {
        pending.addLast(task)
    }

    fun runNext(): Boolean {
        val task = pending.removeFirstOrNull() ?: return false
        task()
        return true
    }
}
```

Robolectricを使うtestは、legacy looper modeを前提にしたAPIを棚卸しし、
public scheduling APIと現在推奨されるpaused looper modeへ移す。
library versionは固定値をこの例からコピーせず、対象projectで採用するversionのrelease notesを確認する。

Compat overrideによる切り分け:

```bash
adb shell am compat enable USE_NEW_MESSAGEQUEUE com.example.app
adb shell am force-stop com.example.app

adb shell am compat disable USE_NEW_MESSAGEQUEUE com.example.app
adb shell am force-stop com.example.app
```

overrideは原因切り分け用であり、release対応として残さない。
同一APKでHandler大量post、delayed task、removeCallbacks、quit、process recreationを比較する。

## 例3: `static final` mutationを設定注入へ移す

避ける実装:

```kotlin
object EndpointConfig {
    const val BASE_URL = "https://production.example"
}

// testやhot patchからstatic finalを書き換える実装はAndroid 17 / target 37で成立しない。
val field = EndpointConfig::class.java.getDeclaredField("BASE_URL")
field.isAccessible = true
field.set(null, "https://staging.example")
```

移行例:

```kotlin
fun interface EndpointProvider {
    fun baseUrl(): String
}

class FixedEndpointProvider(
    private val endpoint: String,
) : EndpointProvider {
    override fun baseUrl(): String = endpoint
}

class ApiClient(
    private val endpoints: EndpointProvider,
) {
    fun requestUrl(path: String): String =
        "${endpoints.baseUrl().trimEnd('/')}/${path.trimStart('/')}"
}
```

productionではbuild-time configurationまたは署名済みremote configurationから
`FixedEndpointProvider`を生成し、testではtest instanceを注入する。
security-sensitiveなendpointを任意入力で切り替えられるdebug UIへ置き換えない。

JNIで`SetStaticObjectField()`などを使って定数を書き換えている場合も、
native codeが必要な値をJava/Kotlin側から引数またはimmutable configuration objectとして渡す。

```kotlin
external fun nativeInitialize(baseUrl: String, timeoutMillis: Long)

fun initializeNative(provider: EndpointProvider) {
    nativeInitialize(
        baseUrl = provider.baseUrl(),
        timeoutMillis = 10_000L,
    )
}
```

失敗系では、reflection pathが`IllegalAccessException`になることだけでなく、
JNI mutationがprocess crashになり得ることを考慮し、isolated test processで確認する。

## 検証マトリクス

| Case | Android 16 / target 36 | Android 17 / target 36 | Android 17 / target 37 |
| --- | --- | --- | --- |
| Memory growth | baseline peakと既存process death | limiter有効端末で終了・復元 | target 36と同じOS条件 |
| Public Handler API | success | success | success |
| `MessageQueue` private reflection |動作し得る | legacy defaultでも非保証 | failureを許容せず依存を除去 |
| Reflection `static final` write | runtime依存 | compatibility behavior | `IllegalAccessException`想定 |
| JNI `static final` write | runtime依存 | compatibility behavior | crashをisolated processで確認 |

## 完了条件

- peak Java heapだけでなく、native allocation、RSS、anon swapを計測した。
- MemoryLimiter終了後を通常のprocess recreationとして復元できる。
- `MessageQueue`のprivate field / method名への依存を除去した。
- Robolectric / instrumentation testのlooper assumptionを更新した。
- reflectionとJNIの`static final` mutationを、設定注入またはsupported APIへ移した。
- Android 17 / target 36とtarget 37を分けて結果を記録した。

## References

- [Core functionality挙動比較](../version-comparisons/core-functionality.md)
- [Android 17 Behavior Changes一覧](../README.md)

## Human Decision

この対応例では最終priority、severity、release readinessを決定しない。

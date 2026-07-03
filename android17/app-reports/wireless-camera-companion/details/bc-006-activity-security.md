# BC-006: Activity Security

## 基本情報（Basic Information）

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/17/behavior-changes-17
- Section: Activity Security

参考 URL:
- https://developer.android.com/guide/components/activities/secure-bal

Original statement:
> PendingIntent / IntentSender 経由の Background Activity Launch がより厳格になる、という趣旨の公式説明。

調査対象 Android バージョン:
- From: android-16.0.0_r4
- To: android-17.0.0_r1

## 対象アプリとの関係（Relevance to Target App）

関連するアプリ機能:
- 通知からの画面起動。
- 表示中 popup / dialog からの推奨アプリ起動。
- カメラ接続復旧後の画面表示。
- ペアリング / Wi-Fi 接続案内。
- 外部アプリ / system UI / PendingIntent 経由の起動。

関連する API / permission / component:
- `PendingIntent`
- `IntentSender`
- `ActivityOptions`
- Background Activity Launch mode

アプリが該当する可能性:
- Unknown / Conditional。background から Activity を直接起動する経路がある場合に該当。表示中 popup または通知をユーザーが明示的にタップし、Activity PendingIntent を直接実行する flow では影響は限定的と考えられる。通知タップ後に broadcast / service / 非同期 callback を挟んで Activity を起動する場合は別途確認が必要。

## 適用条件分類（Applicability Classification）

主分類（Primary classification）:
- TARGET_SDK_37_CONDITIONAL

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | No | `ASM_RESTRICTIONS` は targetSdkVersion 37 以上で enabled。 |
| targetSdkVersion 37 以上が必要か | Yes | `@EnabledAfter(targetSdkVersion = BAKLAVA)`。 |
| 追加の実行時条件があるか | Yes | PendingIntent / IntentSender 経由の BAL、caller visible state。 |
| Compat Change ID が関係するか | Yes | `230590090L`。 |

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17。
- targetSdkVersion: 37 以上。
- App state/process condition: background activity start。caller / real caller が visible か、ユーザー操作直後かを確認する必要がある。
- Permission/API/component condition: PendingIntent / IntentSender。

Compat framework:
- Change ID: `230590090L`
- Change name: `ASM_RESTRICTIONS`
- Default state: targetSdkVersion 37 以上で enabled。
- Toggleable for testing: `@Overridable`。

## AOSP 調査（AOSP Investigation）

関連ファイル:
- `core/java/android/app/ActivityOptions.java`
- `services/core/java/com/android/server/wm/BackgroundActivityStartController.java`

確認したソース文脈（Source Context Reviewed）:

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `ActivityOptions` / BAL modes | legacy `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` | `ALLOW_IF_VISIBLE` / `ALLOW_ALWAYS` への移行 | app が設定する BAL privilege に直接関係する。 |
| `BackgroundActivityStartController` / `ASM_RESTRICTIONS` | legacy mode の許可範囲が広い | targetSdkVersion 37 以上で stricter evaluation | background からの画面起動可否を決める。 |

差分解釈（Diff Interpretation）:
- Changed condition / gate: targetSdkVersion 37 以上で stricter BAL rules。
- Added behavior: `ALLOW_IF_VISIBLE` / `ALLOW_ALWAYS` modes。

適用ゲート根拠（Applicability Gate Evidence）:
- targetSdkVersion gate: targetSdkVersion 37 以上。
- CompatChanges.isChangeEnabled / ChangeId: `230590090L`。
- Gate conclusion: Android 17 / targetSdkVersion 37 / PendingIntent or IntentSender BAL path に適用。

## 事実・観察・仮説・結論（Facts / Observations / Hypotheses / Conclusion）

事実（Facts）:
- `ASM_RESTRICTIONS` は targetSdkVersion 37 以上で enabled。
- 公式 Activity security guide は、system が送信した notification `PendingIntent` から Activity が起動される場合を background activity start が許可される例外として説明している。
- 同 guide は、`PendingIntent` / `IntentSender` では creator または sender が BAL privileges を opt-in し、かつその app が BAL exception を満たす必要があると説明している。
- 同 guide は、sender 側 opt-in では `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` を推奨しており、この mode は `PendingIntent` 送信時に sender app が画面上で visible な場合だけ許可する。

観察（Observations）:
- 接続復旧やペアリング案内を background から直接 Activity 起動する設計は制限される可能性がある。
- 古いカメラ連携アプリと新しいカメラ連携アプリの両方に対応するカメラへ接続した際、古いアプリが表示中 popup で新しいアプリの利用を推奨し、ユーザーのタップ後に PendingIntent で新しいアプリを起動する flow は、user-mediated / visible flow として扱える可能性が高い。
- ユーザーが他アプリを操作中でも、Foreground Service notification または push notification をタップし、通知の `contentIntent` / action が新しいアプリの Activity PendingIntent を直接起動する flow であれば、公式 guide の notification `PendingIntent` 例外に近い user-mediated launch として影響は限定的と考えられる。

仮説（Hypotheses）:
- 対象アプリが background service や receiver から接続画面を直接開く場合、Android 17 / targetSdkVersion 37 で起動が抑制される可能性。
- 同じ推奨導線でも、カメラ接続検知後に background service / receiver がユーザー操作なしで PendingIntent を実行し、新しいアプリの Activity を自動表示する実装であれば、Android 17 / targetSdkVersion 37 で制限対象になる可能性がある。
- 通知タップ後に receiver / service で接続状態確認や互換性判定を行い、その後で Activity を起動する notification trampoline 型または遅延 background 起動の実装では、通知タップがあっても制限対象になる可能性がある。

結論（Conclusion）:
- PendingIntent / IntentSender / background Activity start を棚卸しし、通知や表示中 popup など user-mediated path に寄せる。
- 今回の推奨アプリ起動シナリオは、ユーザーが popup / 通知を明示的にタップし、Activity PendingIntent が直接実行される限り影響は限定的と考えられる。ただし、ユーザー操作なしの background 自動起動、または通知タップ後に receiver / service / 非同期処理を挟む起動であれば要対応候補になる。
- `PendingIntent` / `IntentSender` の sender 側では、Android 17 / targetSdkVersion 37 の検証時に `ActivityOptions#setPendingIntentBackgroundActivityStartMode()` と `ALLOW_IF_VISIBLE` の利用可否を確認する。creator 側が privileges を delegate する必要がある設計かどうかも分けて確認する。

## アプリ影響（App Impact）

想定される影響:
- background からの接続画面・復旧画面起動が失敗する可能性。
- 古いカメラ連携アプリから新しいカメラ連携アプリへの推奨導線で、ユーザー操作なしに Activity を自動表示している場合、起動が拒否される可能性。

ユーザー影響:
- ペアリングや再接続の案内が表示されない、または通知経由操作が必要になる可能性。
- 表示中 popup または通知をタップして新しいアプリへ遷移する設計であれば、ユーザー影響は限定的と見込まれる。
- 他アプリ操作中に通知をタップする flow でも、通知が直接 Activity PendingIntent を起動する設計であれば、ユーザー影響は限定的と見込まれる。

開発者影響:
- `ALLOW_IF_VISIBLE` / `ALLOW_ALWAYS` の使い分けと通知導線の設計。
- 推奨アプリ起動の PendingIntent が、ユーザータップ直後に実行されているか、background service / receiver から自動実行されているかを分けて確認する必要がある。
- 通知経由の起動では、notification の `contentIntent` / action が Activity PendingIntent か、broadcast / service trampoline かを分けて確認する必要がある。

推奨対応候補:
- legacy `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` 利用を検索する。
- `PendingIntent.send()`、`Context.startIntentSender()`、`IntentSender.sendIntent()`、`ActivityResultLauncher<IntentSenderRequest>` の利用箇所を検索する。
- 表示中 popup / dialog / Activity のボタン押下、または通知タップから Activity PendingIntent を直接実行する flow では、`ALLOW_IF_VISIBLE` 相当で足りるかを確認する。
- sender 側で `ActivityOptions#setPendingIntentBackgroundActivityStartMode(ActivityOptions.MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE)` を付与できるか確認する。
- creator 側で `PendingIntent` を作成して他 component / 他 app に渡している場合は、creator privileges の opt-in が必要な flow か確認する。
- 通知 `contentIntent` / action が broadcast / service を指している場合は、Activity PendingIntent へ直接つなげる設計に変更できるか確認する。
- background 状態でユーザー操作なしに起動している場合は、通知または visible UI 経由に変更する。
- Android 17 / targetSdkVersion 37 で、popup 表示中のタップ、通知タップからの直接 Activity 起動、通知タップ後の receiver / service 経由起動、background 自動実行の 4 ケースを分けてテストする。

## Confidence

Confidence:
- High

Confidence の根拠:
- AOSP Change ID と BAL mode path を確認済み。

不足している根拠:
- 対象アプリの起動経路。

---

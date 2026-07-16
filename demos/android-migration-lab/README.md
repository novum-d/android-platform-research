# Android Migration Lab

この workspace は、Android 15 / 16 / 17 の移行影響を説明・再現するためのデモプロジェクトを管理する場所です。

デモは調査レポートの理解を助けるための補助資料です。Behavior Change の最終根拠は、引き続き公式ドキュメント、AOSP evidence、compat framework evidence、実機・emulator 検証結果に置きます。

## 目的

- OS update impact と targetSdkVersion impact を実行可能な形で分けて示す。
- Behavior Change report の読者が、変更前後の挙動を短時間で確認できるようにする。
- 移行対応の before / after を、調査レポートや 1ページ要約から参照できる形にする。
- Android 15 / 16 / 17 の比較を、個別プロジェクトの散在ではなく、共通 matrix で管理する。

## 非目的

- デモ結果だけで Behavior Change の適用条件や重要度を決めない。
- デモアプリを本番アプリの推奨 architecture 例として扱わない。
- すべての Behavior Change を網羅しようとしない。
- Android 15 / 16 / 17 ごとに独立したサンプルアプリを量産しない。

## 基本方針

デモは `Device OS` と `targetSdkVersion` の組み合わせで管理します。

```text
Device OS
  x targetSdkVersion
  x Demo case
  x Expected behavior
  x Observed behavior
```

特に以下を分けて確認します。

- Baseline: 旧 OS / 旧 targetSdkVersion の既存挙動
- OS update impact: 新 OS / 旧 targetSdkVersion の挙動
- targetSdkVersion impact: 新 OS / 新 targetSdkVersion の挙動
- Compat flag isolation: compat flag がある場合の force-enabled / force-disabled 挙動

## 推奨構成

この workspace は、単一 Gradle workspace の中に共通 app と demo case を置きます。

```text
demos/android-migration-lab/
  README.md
  DEMO_MATRIX.md
  settings.gradle.kts
  build.gradle.kts
  gradle/
  gradlew
  gradlew.bat
  app/
  demo-cases/
    predictive-back/
```

`android15/`, `android16/`, `android17/` のような完全分離プロジェクトは原則として作りません。同じ demo case を targetSdkVersion と端末 OS の組み合わせで比較できる構造を優先します。

## 現在の実装

初期 demo case は Predictive back です。

| 項目 | 値 |
| --- | --- |
| Project path | `demos/android-migration-lab/` |
| App module | `app` |
| Demo case | `demo-cases/predictive-back/` |
| UI toolkit | Android platform Views |
| Language | Java |
| AGP | 9.0.1 |
| Gradle wrapper | 9.1.0 |
| compileSdkVersion | 37 |
| minSdkVersion | 23 |
| targetSdkVersion variants | `target35`, `target36`, `target37` |

AGP 9.0.1 は Android CLI `empty-activity` template の生成時点の既定値です。`compileSdkVersion 37` では AGP が「9.0.1 は compile SDK 36.1 まで検証済み」と警告しますが、targetSdkVersion 37 variant を同じ workspace でビルドするために compileSdkVersion 37 を使います。将来この demo を CI や長期運用対象にする場合は、AGP / Gradle wrapper の組み合わせを再評価します。

targetSdkVersion は product flavor で切り替えます。

```bash
./gradlew :app:assembleTarget35Debug
./gradlew :app:assembleTarget36Debug
./gradlew :app:assembleTarget37Debug
```

## 初期対象候補

| Demo case | 主な対象 | 初期優先度 | 備考 |
| --- | --- | --- | --- |
| Predictive back | Android 16 / targetSdkVersion 36 | High | 実装済み。back path の before / after とテスト観点を説明しやすい |
| Edge-to-edge | Android 16 / targetSdkVersion 36 | High | visual regression と migration 対応を説明しやすい |
| Local network permission | Android 17 / targetSdkVersion 37 | Medium | permission / network path の確認が必要 |
| Large screen / input behavior | Android 16 / 17 | Medium | UI と form factor 条件の整理が必要 |

## レポートとの関係

Behavior Change report には、必要に応じて `Demo` セクションを追加します。

```text
## Demo

- Demo case: demos/android-migration-lab/demo-cases/<case>/
- Matrix row: demos/android-migration-lab/DEMO_MATRIX.md#<anchor>
- Status: 未作成 / 実装中 / 実行確認済み
- Notes: デモは説明・再現補助であり、適用条件の根拠ではない。
```

未実装の場合は `Demo: 未作成` と明記し、調査完了条件や Human Decision と混ぜません。

## 実行環境の記録

各 demo case は、少なくとも以下を記録します。

- Android Studio / AGP / Gradle / Kotlin version
- compileSdkVersion
- minSdkVersion
- targetSdkVersion variants
- emulator / device image
- device API level
- image build ID または system image 名
- 実行日
- 手動確認手順
- 自動確認コマンド
- 既知の未確認事項

Android 17 など preview / beta / final で挙動が変わりうる場合は、確認日と image build を必ず残します。

## 実行方法

Android 15 / 16 / 17 の emulator または device を起動し、対象 flavor を install します。

```bash
./gradlew :app:installTarget35Debug
./gradlew :app:installTarget36Debug
./gradlew :app:installTarget37Debug
```

同じ端末に複数 flavor を同時 install できるよう、applicationId は flavor ごとに suffix を付けています。

| Flavor | targetSdkVersion | applicationId |
| --- | --- | --- |
| `target35` | 35 | `com.example.androidmigrationlab.target35` |
| `target36` | 36 | `com.example.androidmigrationlab.target36` |
| `target37` | 37 | `com.example.androidmigrationlab.target37` |

実機確認では、各 Activity を開いて system Back を押し、画面上の callback count が増えるか、Activity が閉じるかを記録します。

## 現在の検証結果

2026-07-16 時点:

```bash
./gradlew :app:assembleTarget35Debug :app:assembleTarget36Debug :app:assembleTarget37Debug
```

結果:
- Build: 成功
- 生成対象: `target35Debug`, `target36Debug`, `target37Debug`
- 警告: AGP 9.0.1 は compileSdkVersion 37.0 に対して未検証警告を出す
- 端末実行: 未実行
- Blocker: AVD 一覧は空。`adb devices` は sandbox 上で adb server の smart socket listener 作成に失敗したため、接続端末確認まで進めなかった

## 検証方針

- Gradle build / unit test は自動化候補にする。
- UI 表示差分、predictive back gesture、edge-to-edge 表示は screenshot / 動画 / 手動手順を許容する。
- emulator matrix を CI で常時実行することは初期要件にしない。
- compat flag がある場合は、`adb shell am compat` などで isolated check を検討する。

## Human Decision

最終的にデモ化する Behavior Change、顧客向け説明で使うか、CI 対象にするかは repository owner が判断します。

```text
Human decision:
- Demo scope:
- Priority:
- Release readiness:
- Customer communication usage:
- Notes:
```

# Create Android Migration Lab Demo Project

Use this prompt to create the first runnable demo project under `demos/android-migration-lab/`.

````text
あなたは `/Users/novumd/repos/android-platform-research` で作業する Codex agent です。

目的:
Android 15 / 16 / 17 の OS update impact と targetSdkVersion impact を分けて説明・再現できる、最小の Android demo project を `demos/android-migration-lab/` に作成してください。

必ず読むもの:
- `AGENTS.md`
- `README.md`
- `demos/android-migration-lab/README.md`
- `demos/android-migration-lab/DEMO_MATRIX.md`
- 関連する場合は `.codex/prompts/investigation.md`
- 関連する Android version の `android<version>/README.md`
- 関連する Android version の `android<version>/behavior-changes/APPLICABILITY_CLASSIFICATION.md`

方針:
- デモは調査根拠そのものではなく、説明・再現補助として扱う。
- OS update impact と targetSdkVersion impact を分ける。
- `android15/`, `android16/`, `android17/` の独立プロジェクトを作らず、単一 Gradle workspace + targetSdkVersion variants で比較できる構成を優先する。
- 初期 demo case は Android 16 predictive back または edge-to-edge のどちらか 1 件に絞る。
- 本番アプリ向け architecture の見本ではなく、Behavior Change が見える最小実装にする。
- Java / Kotlin の選択、Compose / View の選択、AGP / Gradle / Kotlin version は、現在の Android tooling と repo の目的に合う保守的な構成にする。

作成候補:
```text
demos/android-migration-lab/
  settings.gradle.kts
  build.gradle.kts
  gradle/
  gradlew
  gradlew.bat
  app/
  demo-cases/
    <case>/
      README.md
```

実装要件:
- targetSdkVersion 35 / 36 / 37 の比較方法を用意する。flavor、build type、Gradle property のいずれかを選び、理由を README に書く。
- compileSdkVersion と AGP version の選択理由を書く。
- Android 15 / 16 / 17 emulator または device での手動確認手順を書く。
- `DEMO_MATRIX.md` の対象 row と demo case status を更新する。
- demo case README には、Facts / Demo purpose / Implementation / Verification / Limitations / Human decision を含める。
- 可能なら Gradle build が通るところまで確認する。環境不足で実行できない場合は、不足している SDK / tool / command を明記する。

禁止:
- `docs/notes/PERSONAL_NOTES.md` を編集しない。
- デモ結果だけで Behavior Change の applicability classification や final priority を決めない。
- unrelated な既存調査レポートを書き換えない。
- `frameworks-base` の dirty working tree を platform evidence として扱わない。

完了条件:
- `demos/android-migration-lab/` に runnable project skeleton がある。
- 初期 demo case が 1 件ある。
- OS / targetSdkVersion matrix に沿った確認方法が書かれている。
- 実行できた検証コマンドと、実行できなかった場合の blocker が記録されている。
- `git diff` を確認し、変更範囲を説明できる。
````

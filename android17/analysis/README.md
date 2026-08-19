# Android 17 分析補助ファイル

このディレクトリは、AOSP タグ間の差分から生成した調査候補ファイルを置く場所です。

## 現在の状態

Android 16 / 17 の最新通常リリースタグを使って分析補助ファイルを生成済みです。新規・更新調査ではルート `AGENTS.md` の tag freshness rule に従い、より新しいタグが公開されていないか先に確認してください。

## 生成元

生成元:

```text
比較元: android-16.0.0_r4
比較先: android-17.0.0_r1
```

使用するコマンド:

```bash
VERSION_DIR=android17 scripts/generate_target.sh
```

Tag、codename、出力先は [`research-scope.json`](../research-scope.json) から読み込みます。生成時の remote、working tree、resolved commit、比較 command は [`metadata.json`](metadata.json) に保存します。

## 取り扱いルール

このディレクトリのファイルは、生成された分析補助資料です。

最終的な調査結果として扱わないでください。
生成された `.txt` ファイルを、調査結論として手作業で編集しないでください。

AOSP checkout や比較するタグの組み合わせが変わった場合は、手作業で修正するのではなく、ファイルを再生成してください。

## 使い方

これらのファイルは、AOSP source を読む前に調査候補を絞り込むために使います。

ただし、調査は必ず公式 Behavior Change ドキュメントから開始してください。

利用例:
- 公式 Behavior Change の該当セクションを先に読む。
- そのセクションに関係しそうな package / API 名を `analysis/` の候補ファイルで探す。
- 候補ファイルは入口として使うに留め、最終根拠は AOSP source diff と source context に記録する。

# Android 17 分析補助ファイル

このディレクトリは、AOSP タグ間の差分から生成した調査候補ファイルを置く場所です。

## 現在の状態

現時点では、ローカルの `frameworks-base` checkout に Android 17 AOSP タグは存在しません。

対象となる Android 17 タグが利用可能になり、分析補助ファイルを生成するまでは、AOSP 根拠に基づく High confidence の結論は作成しないでください。

## 生成元

生成元:

```text
比較元: android-16.0.0_r4
比較先: 未定: Android 17 AOSP タグ
```

使用するコマンド:

```bash
VERSION_DIR=android17 \
OLD_TAG=android-16.0.0_r4 \
NEW_TAG=<android-17-aosp-tag> \
TARGET_CODENAME=<android-17-codename> \
scripts/generate_target.sh
```

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

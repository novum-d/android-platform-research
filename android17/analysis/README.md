# Android 17 分析補助ファイル（Analysis Files）

このディレクトリは、AOSP tag 間の差分から生成した調査候補ファイルを置く場所です。

## 現在の状態（Current Status）

Android 17 AOSP tag is not currently available in the local `frameworks-base` checkout.

Do not create High confidence AOSP-backed conclusions until the target Android 17 tag is available and analysis files are generated.

## 生成元予定（Planned Source）

Generated from:

```text
From: android-16.0.0_r4
To:   TBD: Android 17 AOSP tag
```

Using:

```bash
VERSION_DIR=android17 \
OLD_TAG=android-16.0.0_r4 \
NEW_TAG=<android-17-aosp-tag> \
TARGET_CODENAME=<android-17-codename> \
scripts/generate_target.sh
```

## 取り扱いルール（Rule）

Files in this directory are generated analysis aids.

Do not treat them as final findings.
Do not hand-edit generated `.txt` files as research conclusions.

If the AOSP checkout or tag pair changes, regenerate these files instead of manually patching them.

## 使い方（How To Use）

Use these files to narrow investigation candidates before reading AOSP source.

The investigation still must start from official Behavior Change documentation.

利用例:
- 公式 Behavior Change の該当セクションを先に読む。
- その section に関係しそうな package / API 名を `analysis/` の候補ファイルで探す。
- 候補ファイルは入口に留め、最終根拠は AOSP source diff と source context に記録する。

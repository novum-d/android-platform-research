# Android 16 Analysis Files

このディレクトリは、AOSP tag 間の差分から生成した調査候補ファイルを置く場所です。

## Source

Generated from:

```text
From: android-15.0.0_r36
To:   android-16.0.0_r1
```

Using:

```bash
VERSION_DIR=android16 \
OLD_TAG=android-15.0.0_r36 \
NEW_TAG=android-16.0.0_r1 \
TARGET_CODENAME=BAKLAVA \
scripts/generate_target.sh
```

## Rule

Files in this directory are generated analysis aids.

Do not treat them as final findings.
Do not hand-edit generated `.txt` files as research conclusions.

If the AOSP checkout or tag pair changes, regenerate these files instead of manually patching them.

## How To Use

Use these files to narrow investigation candidates before reading AOSP source.

The investigation still must start from official Behavior Change documentation.

```text
Behavior Change Documentation
-> AOSP Evidence
-> Customer-facing Investigation Report
-> One Page Summary
-> Human Decision
```

## Important

`frameworks-base/` is a local temporary AOSP checkout and is not tracked by this repository.
Use explicit tag comparisons when collecting evidence.

```bash
git -C frameworks-base diff <from-tag> <to-tag> -- <path>
```

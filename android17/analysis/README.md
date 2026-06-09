# Android 17 Analysis Files

このディレクトリは、AOSP tag 間の差分から生成した調査候補ファイルを置く場所です。

## Current Status

Android 17 AOSP tag is not currently available in the local `frameworks-base` checkout.

Do not create High confidence AOSP-backed conclusions until the target Android 17 tag is available and analysis files are generated.

## Planned Source

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

## Rule

Files in this directory are generated analysis aids.

Do not treat them as final findings.
Do not hand-edit generated `.txt` files as research conclusions.

If the AOSP checkout or tag pair changes, regenerate these files instead of manually patching them.

## How To Use

Use these files to narrow investigation candidates before reading AOSP source.

The investigation still must start from official Behavior Change documentation.

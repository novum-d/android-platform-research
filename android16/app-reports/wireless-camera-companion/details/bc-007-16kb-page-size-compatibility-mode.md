# BC-007: 16 KB page size compatibility mode

## 基本情報

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/16/behavior-changes-all#16-kb-compatibility-mode
- Section: 16 KB page size compatibility mode

既存調査:
- [android16/behavior-changes/all/core-functionality/16-kb-page-size-compatibility-mode.md](../../../behavior-changes/all/core-functionality/16-kb-page-size-compatibility-mode.md)
- [android16/summaries/all/core-functionality/16-kb-page-size-compatibility-mode-summary.md](../../../summaries/all/core-functionality/16-kb-page-size-compatibility-mode-summary.md)

## 対象アプリとの関係

関連するアプリ機能:
- JNI / NDK。
- 画像 / 動画 decode / encode。
- codec、ML / inference、crypto、compression、database。
- third-party native SDK。
- custom native loader。

アプリが該当する可能性:
- Conditional。native `.so` を含む場合は要確認。

## 適用条件分類

主分類:
- `OS_UPDATE_ALL_APPS`

OS update と targetSdkVersion:
- Android 16 以上、16 KB page-size device、4 KB-aligned native libs が主要条件。
- targetSdkVersion 36 は主要 gate ではない。
- compileSdkVersion 36 は `android:pageSizeCompat` manifest property の利用可否に関係する。

Confidence:
- High。

## AOSP / 公式根拠

既存 Android16 調査で確認済み:
- package scan で native library alignment flags を保存。
- process start で zygote runtime flag を設定。
- zygote native が 16 KB appcompat mode を有効化。
- activity launch で warning dialog。
- `R.attr.pageSizeCompat`。

## アプリ影響

想定される影響:
- 16 KB device で warning dialog / compatibility mode。
- native library load failure / startup crash / performance difference。
- third-party SDK が 16 KB alignment 未対応の場合に影響。

推奨対応:
- APK / AAB 内 `.so` の alignment を確認する。
- third-party native SDK を 16 KB 対応版へ更新する。
- `android:pageSizeCompat` は一時 mitigation として扱い、最終的には 16 KB aligned build にする。

## テスト観点

- 4 KB / 16 KB page-size device。
- `.so` alignment。
- app startup。
- native library load。
- `android:pageSizeCompat` declared / absent。
- performance / reliability comparison。

## Human Decision

- Final priority: TBD by human
- Release readiness impact: TBD by human

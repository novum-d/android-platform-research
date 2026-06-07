# [Behavior Change Title]

## Metadata

### Android Versions

From:
- android-15.0.0_r36

To:
- android-16.0.0_r1

### Behavior Change Source

Document:
<URL>

Section:
<Section Name>

### Classification Snapshot

Primary classification:
- OS_UPDATE_ALL_APPS / TARGET_SDK_36 / TARGET_SDK_36_CONDITIONAL / MAINLINE_OR_PLAY_SYSTEM_UPDATE / API_ADDITION_ONLY / UNKNOWN_NEEDS_MORE_EVIDENCE

At-a-glance impact:

| Question | Answer | Evidence |
| --- | --- | --- |
| Android 16 OS update only? | Yes / No / Conditional / Unknown | |
| targetSdkVersion 36 required? | Yes / No / Conditional / Unknown | |
| Additional runtime conditions? | Yes / No / Unknown | |
| Compat Change ID involved? | Yes / No / Unknown | |

### Investigation Date

YYYY-MM-DD

### Confidence

- High
- Medium
- Low

### Applicability Classification

Applies when:
- [ ] OS update / all apps on Android 16 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 36 on Android 16+
- [ ] targetSdkVersion >= 36, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [ ] Unknown / needs more evidence

Required runtime conditions:
- Android version:
- targetSdkVersion:
- Device/form factor:
- Permission/API/component condition:
- App state/process condition:

Compat framework:
- Change ID:
- Change name:
- Default state:
- Toggleable for testing:

Classification confidence:
- High
- Medium
- Low

Classification evidence:
- Official documentation page:
- Original applicability statement:
- AOSP targetSdk gate:
- Compat framework entry:

---

# Executive Summary

3〜5行で説明。

顧客が最初に読む部分。

以下を含める。

- 何が変わったか
- 誰に影響するか
- 対応が必要か

---

# Original Documentation

公式ドキュメントの該当箇所。

## Statement

引用

## Interpretation

ドキュメントが言いたいことを平易に説明。

---

# What Changed

Android 15 と Android 16 の差分。

- 変更点
- 新仕様
- 廃止仕様

## Applicability

この変更がいつ適用されるかを OS 条件と targetSdkVersion 条件に分けて説明する。

### OS Update Behavior

- Android 16 にアップデートしただけで適用されるか:
- targetSdkVersion に依存しない根拠:
- Android 15 以前での挙動:

### targetSdkVersion 36 Behavior

- targetSdkVersion 36 以上で適用されるか:
- Android 16 以外で targetSdkVersion 36 にした場合の挙動:
- opt-out / temporary override の有無:

### Other Conditions

- device/form factor:
- permission:
- API usage:
- manifest attribute:
- component boundary:

---

# AOSP Investigation

## Related Files

- file1
- file2
- file3

## Source Context Reviewed

AOSP のどの部分を見て、なぜ Behavior Change の根拠として採用したかを明記する。

| File / symbol | Android 15 baseline | Android 16 behavior | Why this code path matters |
| --- | --- | --- | --- |
|  |  |  |  |

Required context:
- Entry point / caller:
- Relevant class or service responsibility:
- Runtime path from app API / system event to changed code:
- Why unrelated code paths were excluded:

## Diff Interpretation

AOSP 差分をどのような差分として判断したかを明記する。

| Observed diff | Interpretation | Behavior Change relevance | Confidence |
| --- | --- | --- | --- |
|  |  |  | High / Medium / Low |

Required interpretation:
- Added behavior:
- Removed behavior:
- Changed condition / gate:
- Changed default:
- No behavior change found:

## Evidence

差分から分かった事実。

事実のみ。

推測禁止。

## Applicability Gate Evidence

targetSdkVersion、compat framework、OS version、device condition のいずれで制御されているかを確認する。

- targetSdkVersion gate:
- CompatChanges.isChangeEnabled / ChangeId:
- @EnabledAfter / @EnabledSince / default state:
- Build.VERSION / SDK_INT gate:
- DeviceConfig / resources config:
- Permission/AppOps gate:
- Manifest/property gate:
- No gate found:
- Gate conclusion:
- Reasoning from source context:

---

# Impact Analysis

## Affected Apps

影響を受けるアプリ例。

## Non-Affected Apps

影響を受けないケース。

---

# Customer Impact

顧客説明用。

## Impact Level

- Critical
- High
- Medium
- Low

※ 仮評価。最終判断は人間が行う。

## Business Impact

- ユーザー影響
- 運用影響
- 開発影響

---

# Required Actions

## Must

必須対応。

## Recommended

推奨対応。

## Optional

余裕があれば。

---

# Verification Method

変更を確認する方法。

## Matrix

最低限、以下の組み合わせで再現条件を分ける。

| Device OS | targetSdkVersion | Compat flag | Expected behavior |
| --- | --- | --- | --- |
| Android 15 | 35 | default | |
| Android 16 | 35 | default | |
| Android 16 | 36 | default | |
| Android 16 | 35 | force-enabled if available | |
| Android 16 | 36 | force-disabled if available | |

## Steps

- targetSdk変更:
- compat framework command:
- テスト方法:
- 再現手順:
- 期待結果:

---

# Conclusion

1〜3行。

顧客へ説明する際の結論。

---

# References

## Documentation

- URL

## AOSP

- File
- File
- File

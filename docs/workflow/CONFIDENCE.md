# Confidence

このファイルは、調査結果の確信度を判断する基準と、各レベルに必要な根拠を定義するためのものです。

調査結果の確信度を記録する。

## Levels

### High

実装、API差分、公式ドキュメント、適用条件分類の整合が取れている。

Required:
- 公式 Behavior Change 原文がある
- AOSP evidence がある
- OS update / targetSdkVersion update / conditional / Mainline / API addition の分類がある
- targetSdkVersion gate の有無を確認している
- compat framework に掲載がある場合、Change ID と default state を確認している
- target Android version / previous targetSdkVersion と target Android version / new targetSdkVersion の期待差分が説明されている
- 例外、opt-out、device/form factor、permission、API usage など追加条件を確認している

### Medium

実装とドキュメントは確認したが、分類の一部に不足がある。

Examples:
- AOSP gate は確認したが、実機/CTS/compat toggle では未確認
- compat framework の Change ID は確認したが、関連 Behavior Change との対応が未確定
- 追加条件や例外の確認が一部不足している

### Low

仮説段階。根拠が限定的。

Examples:
- 公式ドキュメントだけで AOSP evidence がない
- AOSP 差分だけで Behavior Change 原文がない
- OS update と targetSdkVersion update の分類が未確定
- targetSdkVersion gate / compat framework default state が未確認

## Template

### Topic

Confidence:
- High / Medium / Low

Reason:

Missing Evidence:

Applicability:
- OS update / all apps:
- targetSdkVersion update:
- Other conditions:

Compat framework:
- Change ID:
- Default state:

# 信頼度（Confidence）

このファイルは、調査結果の確信度を判断する基準と、各レベルに必要な根拠を定義するためのものです。

調査結果の確信度を記録する。

## レベル（Levels）

### High（高）

実装、API差分、公式ドキュメント、適用条件分類の整合が取れている。

必要条件:
- 公式 Behavior Change 原文がある
- AOSP evidence がある
- OS update / targetSdkVersion update / conditional / Mainline / API addition の分類がある
- targetSdkVersion gate の有無を確認している
- compat framework に掲載がある場合、Change ID と default state を確認している
- target Android version / previous targetSdkVersion と target Android version / new targetSdkVersion の期待差分が説明されている
- 例外、opt-out、device/form factor、permission、API usage など追加条件を確認している

記入例:
- 公式原文、AOSP gate、compat default state がすべて一致している。
- Android 17 / targetSdkVersion 36 と Android 17 / targetSdkVersion 37 の期待挙動を分けて説明できる。

### Medium（中）

実装とドキュメントは確認したが、分類の一部に不足がある。

例:
- AOSP gate は確認したが、実機/CTS/compat toggle では未確認
- compat framework の Change ID は確認したが、関連 Behavior Change との対応が未確定
- 追加条件や例外の確認が一部不足している

### Low（低）

仮説段階。根拠が限定的。

例:
- 公式ドキュメントだけで AOSP evidence がない
- AOSP 差分だけで Behavior Change 原文がない
- OS update と targetSdkVersion update の分類が未確定
- targetSdkVersion gate / compat framework default state が未確認

## 記入テンプレート（Template）

### 調査項目（Topic）

Confidence:
- High / Medium / Low

理由（Reason）:

不足根拠（Missing Evidence）:

適用条件（Applicability）:
- OS update / all apps:
- targetSdkVersion update:
- Other conditions:

Compat framework:
- Change ID:
- Default state:

# BC-005: Improved security against Intent redirection attacks

## 基本情報

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/16/behavior-changes-all#intent-redirect-attacks
- Section: Improved security against Intent redirection attacks

既存調査:
- [android16/behavior-changes/all/security/improved-security-against-intent-redirection-attacks.md](../../../behavior-changes/all/security/improved-security-against-intent-redirection-attacks.md)
- [android16/summaries/all/security/improved-security-against-intent-redirection-attacks-summary.md](../../../summaries/all/security/improved-security-against-intent-redirection-attacks-summary.md)

## 対象アプリとの関係

関連するアプリ機能:
- deep link / app link router。
- notification / shortcut / widget からの workflow router。
- SDK / plugin / mini-app dispatcher。
- 古いカメラ連携アプリから新アプリへの推奨導線。
- URI grant を伴う file / image handoff。

アプリが該当する可能性:
- Conditional。external Intent extras から nested Intent を取り出して launch する場合に該当。

## 適用条件分類

主分類:
- `OS_UPDATE_ALL_APPS`

OS update と targetSdkVersion:
- Android 16 OS 上で targetSdkVersion 35 / 36 の両方に影響し得る。
- compileSdkVersion 36 は `Intent#removeLaunchSecurityProtection()` を直接呼ぶ API availability に関係するが、適用条件ではない。

Confidence:
- High。

## AOSP / 公式根拠

既存 Android16 調査で確認済み:
- nested Intent creator token。
- missing / invalid token flag。
- Activity launch permission / URI grant 再検証。
- `Intent#removeLaunchSecurityProtection()` opt-out API。
- Activity launch path が confirmed enforcement。

## アプリ影響

想定される影響:
- external app から受け取った nested Intent をそのまま `startActivity()` する router が block / exception になる可能性。
- private / non-exported component の誤起動や URI grant leak を防ぐ方向の変更。
- legitimate first-party redirect flow がある場合、validation または限定的 opt-out が必要。

推奨対応:
- component / package / action / data / categories / flags / ClipData / URI grant を allowlist validation する。
- `IntentSanitizer` または同等の sanitizer を検討する。
- `removeLaunchSecurityProtection()` は first-party / allowlisted flow に限定し、広く使わない。

## テスト観点

- nested Intent in extras / ClipData。
- exported / non-exported / permission-protected component。
- URI grant flags。
- legitimate router flow。
- malicious input blocked。

## Human Decision

- Final priority: TBD by human
- Release readiness impact: TBD by human

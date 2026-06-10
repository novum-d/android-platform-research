# Review Checklist

このファイルは、調査レポートと 1ページ要約が必要な根拠・分類・顧客説明を満たしているか確認するためのチェックリストです。

## Customer Report

- [ ] Behavior Change の原文がある
- [ ] 対象バージョンが明記されている
- [ ] 適用条件が OS update / targetSdkVersion update / その他 に分類されている
- [ ] 公式ドキュメントのページ種別を確認している
- [ ] 原文に `regardless of targetSdkVersion` または `targeting Android <version> (API level <api>)` 相当の適用条件があるか確認している
- [ ] OS version 条件と targetSdkVersion 条件を分けて説明している
- [ ] device/form factor、permission、API usage、manifest/property など追加条件を確認している
- [ ] AOSP根拠ファイルがある
- [ ] AOSP のどの部分を見たか、file / symbol / entry point / caller が明記されている
- [ ] そのコードパスを Behavior Change の根拠として採用した理由が書かれている
- [ ] baseline Android version と target Android version の差分解釈が書かれている
- [ ] 無関係と判断したコードパス、または調査対象外にした理由が必要に応じて書かれている
- [ ] AOSP で targetSdkVersion gate の有無を確認している
- [ ] AOSP で CompatChanges / ChangeId / @EnabledAfter / @EnabledSince の有無を確認している
- [ ] Compat framework の Change ID、change name、default state を確認している
- [ ] OSアップデートのみ、targetSdk変更のみ、compat flag 強制変更の検証マトリクスがある
- [ ] 事実と推測が分離されている
- [ ] アプリ開発者への影響が書かれている
- [ ] Service Impact Examples（サービス影響例）がある場合、実発生確認済みの事実と起こりうる影響例が分離されている
- [ ] 顧客説明用の結論がある
- [ ] Required Actions がある
- [ ] Confidence がある
- [ ] Confidence の理由と不足証拠が書かれている
- [ ] 1ページ要約がある
- [ ] 人間の最終判断が DECISION_LOG にある

## Classification Review

High confidence にできる条件:

- [ ] 公式 Behavior Change ページの分類と原文が一致している
- [ ] AOSP 実装で適用 gate を確認している、または gate がないことを確認している
- [ ] AOSP source context と diff interpretation から分類結論が追跡できる
- [ ] compat framework に掲載がある場合、default state と Change ID が一致している
- [ ] target Android version / previous targetSdkVersion と target Android version / new targetSdkVersion の期待差分が明記されている
- [ ] 顧客向け結論が「OSアップデートで発生」「targetSdkVersion 更新で発生」「条件付き」「影響なし」のいずれかで明確に書かれている

High confidence にしてはいけない条件:

- [ ] 公式ドキュメントだけで AOSP gate を未確認
- [ ] AOSP 差分だけで Behavior Change 原文を未確認
- [ ] targetSdkVersion 条件と OS version 条件が混在している
- [ ] compat framework の default state が未確認
- [ ] 追加条件、例外、opt-out を未確認

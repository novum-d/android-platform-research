# レビューチェックリスト（Review Checklist）

このファイルは、調査レポートと 1ページ要約が必要な根拠・分類・顧客説明を満たしているか確認するためのチェックリストです。

## 顧客向け調査レポート（Customer Report）

- [ ] Behavior Change の原文がある
- [ ] 対象バージョンが明記されている
- [ ] 適用条件が OS update / targetSdkVersion update / その他 に分類されている
- [ ] 公式ドキュメントのページ種別を確認している
- [ ] 原文に `regardless of targetSdkVersion` または `targeting Android <version> (API level <api>)` 相当の適用条件があるか確認している
- [ ] OS version 条件と targetSdkVersion 条件を分けて説明している
- [ ] device/form factor、permission、API usage、manifest/property など追加条件を確認している
- [ ] AOSP根拠ファイルがある
- [ ] 根拠に使った各 AOSP project の official remote URL と checkout path がある
- [ ] 比較元・比較先 tag の resolved commit hash がある
- [ ] 明示的な tag 比較 command と working tree の clean / dirty 状態がある
- [ ] dirty な場合、local working tree を evidence に使っていないことと confidence への影響がある
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
- [ ] サービス影響例（Service Impact Examples）がある場合、実発生確認済みの事実と起こりうる影響例が分離されている
- [ ] 顧客説明用の結論がある
- [ ] 対応候補（Required Actions）がある
- [ ] 信頼度（Confidence）がある
- [ ] 信頼度の理由と不足証拠が書かれている
- [ ] 1ページ要約がある
- [ ] `Pending Human Decision` placeholderがあり、Research Completeとして必要な成果物が揃っている

## Repository 構成レビュー

- [ ] `python3 -m unittest discover -s tests -p 'test_*.py'` が成功する
- [ ] `python3 scripts/validate_repository_structure.py` が成功する
- [ ] 新規・更新調査の開始前に `python3 scripts/validate_repository_structure.py --online` が成功する
- [ ] behavior report と 1ページ要約、Build System detail / summary / checklist の索引漏れがない
- [ ] `research-scope.json`、人間向け instructions、analysis metadata が一致する
- [ ] 既存 evidence record を再検証せず最新 tag metadata だけに書き換えていない

## 判断完了レビュー（Decision Complete Review）

Research Complete後に、リポジトリ所有者が判断を記録する段階で確認する。

- [ ] 人間の最終判断がDECISION_LOGにある
- [ ] 最終判断から根拠レポートと1ページ要約を追跡できる
- [ ] agentの分析と人間のpriority / severity / release readiness判断が区別されている

## 分類レビュー（Classification Review）

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

記入例:
- High confidence 可: 公式文書、AOSP gate、compat default state、targetSdkVersion 別の期待挙動がすべて一致している。
- High confidence 不可: 公式文書はあるがAOSP gateが未確認、または関連AOSP projectのtarget tag / implementation pathを確認できずdiffを確認できない。

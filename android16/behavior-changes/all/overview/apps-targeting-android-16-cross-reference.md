# Apps targeting Android 16 cross-reference 調査レポート

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:
- AOSP checkout `frameworks-base` は clean で、`android-15.0.0_r36` / `android-16.0.0_r4` tag の存在を確認した。

Previous targetSdkVersion:
- 35

Target targetSdkVersion:
- 36

### Behavior Change 文書（Behavior Change Source）

Document:
- https://developer.android.com/about/versions/16/behavior-changes-all#targeting-16

Page:
- Behavior changes: all apps

Linked target page:
- https://developer.android.com/about/versions/16/behavior-changes-16

Category:
- Overview / Cross-reference

Section:
- Apps targeting Android 16 cross-reference

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `UNKNOWN_NEEDS_MORE_EVIDENCE`

分類注記（Classification note）:
- この項目は documentation cross-reference であり、独立した Android runtime behavior change ではない。
- `android16/behavior-changes/APPLICABILITY_CLASSIFICATION.md` には `DOCUMENTATION_REFERENCE_ONLY` / `OVERVIEW_ONLY` に相当する正式ラベルがないため、許可済みラベルとして `UNKNOWN_NEEDS_MORE_EVIDENCE` を使用する。
- ただし「runtime 挙動が未知」という意味ではなく、「分類ラベル体系に documentation-only を表す正式ラベルがない」という意味である。
- concrete behavior change の分類は、各 child section の report で `OS_UPDATE_ALL_APPS` / `TARGET_SDK_36` / `TARGET_SDK_36_CONDITIONAL` などを個別に判定する。

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| この cross-reference 自体が runtime behavior change か | No | 公式 all-apps 冒頭の target-only ページへの導線であり、具体的な API / service / framework 実装に対応しない。 |
| all-apps ページの挙動は targetSdkVersion に依存しないか | Officially Yes | 公式 all-apps ページは、Android 16 上で実行される全アプリに適用される変更であり targetSdkVersion に関係しないと説明している。 |
| target-only ページの挙動は targetSdkVersion 36 以上に限定されるか | Officially Yes | 公式 target-only ページは、Android 16 以上を target するアプリにのみ適用される変更と説明している。 |
| `#targeting-16` anchor は現行 HTML 上で確認できたか | No / nearest content found | `targeting-16` 文字列は現行 all-apps HTML では見つからない。最寄りの公式内容は冒頭の target-only page link。 |
| AOSP implementation evidence は必要か | Not for this cross-reference | cross-reference 自体には実装がない。API 36 の定義として `Build.VERSION_CODES.BAKLAVA = 36` を確認した。 |
| report placement の意味 | Overview under all/ | 依頼に従い `android16/behavior-changes/all/overview/` に置くが、これは runtime all-apps behavior ではなく overview / navigation guidance。 |

### 調査日（Investigation Date）

2026-07-06

### 信頼度（Confidence）

- High for documentation role
- Low for runtime applicability, because no runtime behavior exists for this item

理由:
- 公式 all-apps page と target-only page の冒頭文言を再確認した。
- 現行 all-apps HTML では requested anchor `#targeting-16` に対応する heading / id は確認できなかった。
- AOSP では Android 16 / API 36 の定義として `Build.VERSION_CODES.BAKLAVA = 36` と `Build.VERSION.SDK_INT` を確認したが、この cross-reference 自体に対応する実装 entry point は存在しない。

---

## 公式ドキュメント確認（Original Documentation）

### all-apps page

公式 all-apps page は、Android 16 platform には app に影響する可能性のある behavior changes があり、それらは Android 16 上で実行される全アプリに targetSdkVersion に関係なく適用される、と説明している。また、Android 16 を target するアプリだけに影響する behavior changes も確認するよう促している。

### target-only page

公式 target-only page は、Android 16 には app に影響する可能性のある behavior changes があり、それらは Android 16 以上を target するアプリにのみ適用される、と説明している。また、targetSdkVersion に関係なく Android 16 上の全アプリに影響する behavior changes も確認するよう促している。

### Anchor validation

- Requested URL: `https://developer.android.com/about/versions/16/behavior-changes-all#targeting-16`
- 現行 HTML で `targeting-16` 文字列は確認できなかった。
- 公式ページ上の最寄り content は、all-apps page 冒頭の “behavior changes that only affect apps targeting Android 16” link であり、リンク先は `behavior-changes-16` page。
- したがって、この report では `#targeting-16` を concrete section anchor ではなく、all-apps page 冒頭の target-only page cross-reference を指す依頼上の識別子として扱う。

### Documentation drift

- 依頼文の all-apps page statements と target-only page statements は、現行公式本文と実質一致する。
- 差分は、requested anchor `#targeting-16` が現行 HTML で検出できなかった点。

---

## Facts

- all-apps page は、Android 16 上で実行される全アプリに targetSdkVersion に関係なく適用される behavior changes を扱う。
- target-only page は、Android 16 / API level 36 以上を target するアプリにのみ適用される behavior changes を扱う。
- all-apps page と target-only page は相互に参照し、開発者に両方を確認するよう促している。
- この cross-reference 自体は documentation navigation / overview guidance であり、AOSP の service / framework code path に対応する runtime behavior change ではない。
- `frameworks-base/core/java/android/os/Build.java` では `Build.VERSION_CODES.BAKLAVA = 36` が定義されている。
- `Build.VERSION.SDK_INT` は実行中 device の major SDK version を表す runtime value として定義されている。
- `frameworks-base` checkout は clean で、依頼 tag の存在を確認済み。

## Observations

- この項目を `OS_UPDATE_ALL_APPS` と分類すると、documentation cross-reference 自体が Android 16 OS 上で runtime behavior を変えるように誤読される可能性がある。
- この項目を `TARGET_SDK_36` と分類すると、all-apps page 全体まで targetSdkVersion-gated と誤読される可能性がある。
- 既存 repo には `android16/behavior-changes/all/` と `android16/behavior-changes/target/` の両方があり、report placement は公式ページ分類と顧客説明の分離に重要である。
- concrete behavior-change section では、公式ページ分類だけでなく AOSP gate evidence / compat Change ID / targetSdkVersion gate の有無を個別に確認する必要がある。
- targetSdkVersion 36 migration と Android 16 OS update は同時に行われることが多いが、影響分析では分離しないと QA 範囲と顧客説明が混ざる。

## Hypotheses

- 今後 repository の classification labels に `DOCUMENTATION_REFERENCE_ONLY` または `OVERVIEW_ONLY` が追加されれば、この項目はそれに再分類するのが最も正確である。
- `#targeting-16` anchor は過去の generated anchor / navigation link / prompt-side identifier だった可能性がある。現行公式 HTML では、リンク先 `behavior-changes-16` page への cross-reference として扱うのが妥当である。
- target-only page 内の concrete behavior changes には、Android 15 device 上でも targetSdkVersion 36 にした場合に影響がある項目と、Android 16 runtime が必要な項目が混在し得る。各 child report で個別に matrix を作る必要がある。

## Conclusions

- この項目は independent runtime behavior change ではなく、Android 16 behavior-change investigation 全体の triage / report classification / QA matrix 設計のための documentation cross-reference である。
- 顧客向け説明では、Android 16 OS update impact、targetSdkVersion 36 migration impact、両方を同時に行った場合の combined impact を必ず分離する。
- all-apps page の statement は、Android 16 上での OS-version-gated impact を示す starting point であり、targetSdkVersion gate が絶対に存在しないことの AOSP 証明ではない。各 concrete section で確認する。
- target-only page の statement は、targetSdkVersion 36 以上の migration impact を示す starting point であり、Android 15 上でも同じかどうかは各 concrete section で確認する。

---

## AOSP 調査（AOSP Investigation）

### 関連ファイル（Related Files）

- `frameworks-base/core/java/android/os/Build.java`
- `frameworks-base/core/api/current.txt`（cross-reference 自体に対応する API diff なし）

### 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル（File / symbol） | Android 15 baseline | Android 16 target | relevance |
| --- | --- | --- | --- |
| `Build.VERSION_CODES.BAKLAVA` | Android 15 では Android 16 API level の runtime target ではない。 | `BAKLAVA = 36` として定義。 | targetSdkVersion 36 / API level 36 を説明する基礎定義。 |
| `Build.VERSION.SDK_INT` | 実行中 platform の major SDK version を示す。 | 同様。 | Android 16 runtime かどうかを app / test が判定する基礎。 |
| documentation cross-reference | N/A | N/A | AOSP implementation path は存在しない。 |

### Diff interpretation

| 確認項目 | 解釈 | 信頼度 |
| --- | --- | --- |
| cross-reference 自体の API / service 実装 | なし。documentation overview / navigation guidance。 | High |
| `BAKLAVA = 36` | Android 16 / API level 36 の定義として存在。 | High |
| targetSdkVersion gate | この item 自体には gate なし。concrete child changes で個別確認。 | High |
| compat framework Change ID | この item 自体にはなし。concrete child changes で個別確認。 | High |
| CTS / unit test | この item 自体にはなし。concrete child behavior change の test を参照する。 | High |

---

## 適用条件（Applicability）

### Android 16 / targetSdkVersion 35

- all-apps behavior changes: 公式分類上は適用対象。
- target-only behavior changes: 原則適用対象外。ただし child section の AOSP evidence で別条件があれば個別に扱う。
- この cross-reference: runtime impact なし。QA / report review guidance として有効。

### Android 16 / targetSdkVersion 36

- all-apps behavior changes: 適用対象。
- target-only behavior changes: 適用対象。
- この cross-reference: runtime impact なし。両ページを review すべきという調査導線。

### Android 15 / targetSdkVersion 36

- Android 16 all-apps behavior changes: 原則 Android 16 runtime ではないため適用対象外。
- Android 16 target-only behavior changes: child section によっては Android 15 上でも targetSdkVersion 36 により影響する可能性があるため個別確認。
- この cross-reference: runtime impact なし。migration planning guidance として有効。

---

## 期待挙動マトリクス（Expected Behavior Matrix）

| シナリオ | 期待挙動 / 調査結論 |
| --- | --- |
| Documentation cross-reference only | independent runtime change なし。 |
| Android 16 / targetSdkVersion 35 / all-apps behavior changes | 公式分類上、Android 16 runtime により適用対象。 |
| Android 16 / targetSdkVersion 36 / all-apps behavior changes | 公式分類上、targetSdkVersion 35 と同様に適用対象。 |
| Android 16 / targetSdkVersion 35 / target-only behavior changes | 原則対象外。 |
| Android 16 / targetSdkVersion 36 / target-only behavior changes | 公式分類上、適用対象。 |
| Android 15 / targetSdkVersion 35 / Android 16 all-apps behavior changes | 原則対象外。Android 16 runtime が必要。 |
| Android 15 / targetSdkVersion 36 / Android 16 target-only behavior changes | child section ごとに確認。targetSdkVersion gate のみなら影響し得る。 |
| Android 16 OS update only / targetSdkVersion unchanged at 35 | all-apps changes を重点確認。target-only changes は原則対象外。 |
| targetSdkVersion 36 migration only / Android 15 runtime | target-only changes のうち Android 15 runtime でも成立するものを確認。 |
| Android 16 OS update plus targetSdkVersion 36 migration | all-apps + target-only の両方を確認。 |
| all-apps page section / OS-version-gated behavior | `all/` 配下に report。AOSP で target gate の有無を確認。 |
| target-only page section / targetSdkVersion-gated behavior | `target/` 配下に report。AOSP で targetSdkVersion gate を確認。 |
| behavior change with compat framework Change ID | Change ID / default state / override 可否を child report で確認。 |
| behavior change without compat framework Change ID | code path / API surface / docs による分類根拠を child report に記録。 |
| official documentation says all apps / AOSP shows no target gate | `OS_UPDATE_ALL_APPS` 候補。 |
| official documentation says target-only / AOSP shows targetSdkVersion gate | `TARGET_SDK_36` または `TARGET_SDK_36_CONDITIONAL` 候補。 |
| official documentation / AOSP evidence mismatch | mismatch を report に明記し confidence を下げる。 |
| report output under `android16/behavior-changes/all/` | all-apps page または依頼上 all-apps scope。OS update impact として扱うが child evidence で確認。 |
| report output under `android16/behavior-changes/target/` | target-only page scope。targetSdkVersion migration impact として扱うが child evidence で確認。 |

---

## 影響対象（Affected App / Team Categories）

- Android 16 OS アップデートのみを受けるアプリ
- targetSdkVersion 35 のまま Android 16 上で動作するアプリ
- targetSdkVersion 36 へ移行するアプリ
- Android 15 上で targetSdkVersion 36 へ移行するアプリ
- Android 16 OS アップデートと targetSdkVersion 36 移行を同時に行うアプリ
- Android 16 all-apps behavior changes だけを確認しているアプリ
- Android 16 target-only behavior changes だけを確認しているアプリ
- OS-update impact と targetSdkVersion migration impact を顧客説明で分ける必要があるアプリ / チーム
- QA matrix / release readiness / customer communication を分類別に整理する必要があるチーム

---

## テスト観点（Test Viewpoints）

- Android 15 端末上の targetSdkVersion 35
- Android 16 端末上の targetSdkVersion 35
- Android 16 端末上の targetSdkVersion 36
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較
- all-apps page の各 concrete behavior change
- target-only page の各 concrete behavior change
- OS update only scenario
- targetSdkVersion update only scenario
- OS update plus targetSdkVersion update scenario
- compat framework flags enabled / disabled where available
- app manifest targetSdkVersion verification
- runtime `Build.VERSION.SDK_INT` verification
- compileSdkVersion と targetSdkVersion の区別
- report / summary が all-apps と target-only を混同していないこと
- customer-facing explanation が OS update impact と targetSdkVersion migration impact を分離していること

---

## Human Decision Placeholder

最終優先度（Final Priority）:
- TBD by human

最終 severity（Final Severity）:
- TBD by human

顧客説明優先度（Customer communication priority）:
- TBD by human

分類ラベル追加要否（Need repository classification label update）:
- TBD by human

リリース判定（Release readiness decision）:
- TBD by human

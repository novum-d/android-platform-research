# Android 17 調査バックログ（Research Backlog）

## 高優先度候補（High）

- MessageQueue lock-free implementation
- Static final fields are now unmodifiable
- Background audio hardening
- Per-app keystore limits
- Block cross profile loopback traffic

## 中優先度候補（Medium）

- App memory limits
- BluetoothSocket read behavior for RFCOMM
- Contacts Provider privacy / strict SQL changes
- Large screen orientation / resizability opt-out removal

## 低優先度候補（Low）

- API additions only
- Internal-only changes
- UI polish

注意:
- ここでの High / Medium / Low は調査着手順の候補であり、顧客向けの最終 priority / severity ではない。
- 最終判断は各レポートの人間の判断欄と `android17/decisions/DECISION_LOG.md` に記録する。

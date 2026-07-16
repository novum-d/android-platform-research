# Predictive Back Demo

## Demo Case ID

DC-001

## Title

Predictive back migration / opt-out demonstration

## Related Behavior Change

- Android 16: Migration or opt-out required for predictive back
- Official documentation: https://developer.android.com/about/versions/16/behavior-changes-16#predictive-back
- Migration guide: https://developer.android.com/guide/navigation/custom-back/predictive-back-gesture

## Related Report

- `android16/behavior-changes/target/user-experience-and-system-ui/migration-or-opt-out-required-for-predictive-back.md`
- `android16/summaries/target/user-experience-and-system-ui/migration-or-opt-out-required-for-predictive-back-summary.md`
- `android16/behavior-changes/target/user-experience-and-system-ui/migration-or-opt-out-required-for-predictive-back-implementation-examples.md`

## Primary Matrix Rows

- M-15-35
- M-16-35
- M-16-36
- M-17-36
- M-17-37

## Facts

- Official documentation states that, for apps targeting Android 16 / API level 36 or higher and running on Android 16 or higher, predictive back system animations are enabled by default.
- The existing repository report classifies this Behavior Change as `TARGET_SDK_36_CONDITIONAL`.
- Android 16 / targetSdkVersion 35 is expected to preserve the legacy back path for this change.
- Android 16 / targetSdkVersion 36 is expected to stop calling legacy `Activity.onBackPressed()` for activities that have not opted out or migrated.
- `android:enableOnBackInvokedCallback="false"` is the temporary opt-out path documented by Android.

## Demo Purpose

This demo shows the difference between:

- Legacy back handling only: `LegacyBackActivity`
- Migrated platform callback handling: `ModernBackActivity`
- Temporary manifest opt-out: `TemporaryOptOutActivity`

This demo does not prove the Behavior Change classification by itself. The primary report and official documentation remain the source of truth.

## Implementation

Module / package:
- `app`
- `com.example.androidmigrationlab`

targetSdkVersion variants:

| Flavor | targetSdkVersion | applicationId |
| --- | --- | --- |
| `target35` | 35 | `com.example.androidmigrationlab.target35` |
| `target36` | 36 | `com.example.androidmigrationlab.target36` |
| `target37` | 37 | `com.example.androidmigrationlab.target37` |

Activities:

| Activity | Implementation | Expected role |
| --- | --- | --- |
| `LegacyBackActivity` | Overrides `Activity.onBackPressed()` only | Shows legacy callback behavior disappearing on Android 16 + target 36/37 |
| `ModernBackActivity` | Registers `OnBackInvokedCallback` on API 33+ and sets `android:enableOnBackInvokedCallback="true"` | Shows migrated platform callback handling |
| `TemporaryOptOutActivity` | Overrides `Activity.onBackPressed()` and sets `android:enableOnBackInvokedCallback="false"` | Shows temporary activity-level opt-out |

## Verification

Build commands:

```bash
./gradlew :app:assembleTarget35Debug
./gradlew :app:assembleTarget36Debug
./gradlew :app:assembleTarget37Debug
```

Install commands:

```bash
./gradlew :app:installTarget35Debug
./gradlew :app:installTarget36Debug
./gradlew :app:installTarget37Debug
```

Manual steps:

1. Start an Android 15, Android 16, or Android 17 emulator/device.
2. Install the target flavor for the matrix row.
3. Launch Android Migration Lab.
4. Open `Legacy back only`, press system Back, and record whether the counter increments or the activity closes.
5. Open `Modern predictive back`, press system Back, and record whether the modern callback counter increments.
6. Open `Temporary opt-out`, press system Back, and record whether the opt-out counter increments.

Expected behavior:

| Matrix row | LegacyBackActivity | ModernBackActivity | TemporaryOptOutActivity |
| --- | --- | --- | --- |
| M-15-35 | `onBackPressed()` counter increments | Modern callback may run on API 33+ because the activity explicitly opts in | `onBackPressed()` counter increments |
| M-16-35 | `onBackPressed()` counter increments | `OnBackInvokedCallback` counter increments | `onBackPressed()` counter increments |
| M-16-36 | Activity closes or legacy counter does not increment | `OnBackInvokedCallback` counter increments | `onBackPressed()` counter increments |
| M-17-36 | Follow Android 17 device behavior and record result; Android 16 report classification is not extended automatically | `OnBackInvokedCallback` counter increments | `onBackPressed()` counter increments if opt-out remains honored |
| M-17-37 | Follow Android 17 device behavior and record result; Android 16 report classification is not extended automatically | `OnBackInvokedCallback` counter increments | `onBackPressed()` counter increments if opt-out remains honored |

Observed behavior:
- Build verification passed on 2026-07-16:

  ```bash
  ./gradlew :app:assembleTarget35Debug :app:assembleTarget36Debug :app:assembleTarget37Debug
  ```

- Device verification is not yet run.
- AVD list was empty in the current environment.
- `adb devices` could not start adb server because smart socket listener creation failed with `Operation not permitted`.

Evidence artifacts:
- Add screenshots or screen recordings under a future `evidence/` directory if needed.

## Limitations

- This demo uses platform Views and platform `OnBackInvokedCallback`, not AndroidX `OnBackPressedDispatcher`. The AndroidX migration examples remain in the Android 16 implementation examples report.
- Build verification does not replace device verification. Predictive back animation and callback dispatch must be checked on the actual Android OS image.
- AGP 9.0.1 builds the project but warns that compileSdkVersion 37.0 is newer than the version it was tested with. This is recorded as a tooling limitation, not a runtime finding.
- Android 17 rows are included for migration lab continuity, but Android 17 behavior must be verified separately before using it in customer-facing conclusions.
- The demo intentionally keeps Activity behavior minimal; it is not an application architecture recommendation.

## Human Decision

- Use in customer-facing explanation:
- Priority:
- Notes:

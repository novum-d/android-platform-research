package com.example.androidmigrationlab;

import android.app.Activity;
import android.os.Bundle;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

public final class LegacyBackActivity extends Activity {
    private int backCount;
    private TextView status;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        ScrollView scrollView = DemoUi.screen(this, "Legacy back only");
        LinearLayout root = (LinearLayout) scrollView.getChildAt(0);

        DemoUi.addSection(
                root,
                DemoUi.text(
                        this,
                        "This activity only overrides Activity.onBackPressed(). It does not register OnBackInvokedCallback.\n\n"
                                + "Expected: Android 16 + targetSdkVersion 36/37 does not call this legacy callback. Android 16 + targetSdkVersion 35 should keep the legacy callback path.",
                        16));
        status = DemoUi.text(this, "", 18);
        DemoUi.addSection(root, status);
        updateStatus("Waiting for system Back.");

        setContentView(scrollView);
    }

    @Override
    public void onBackPressed() {
        backCount++;
        updateStatus("Activity.onBackPressed() was called.");
    }

    private void updateStatus(String event) {
        status.setText(event + "\nHandled legacy back count: " + backCount);
    }
}

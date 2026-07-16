package com.example.androidmigrationlab;

import android.app.Activity;
import android.os.Bundle;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

public final class TemporaryOptOutActivity extends Activity {
    private int backCount;
    private TextView status;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        ScrollView scrollView = DemoUi.screen(this, "Temporary opt-out");
        LinearLayout root = (LinearLayout) scrollView.getChildAt(0);

        DemoUi.addSection(
                root,
                DemoUi.text(
                        this,
                        "This activity sets android:enableOnBackInvokedCallback=\"false\".\n\n"
                                + "Expected: Android 16 + targetSdkVersion 36/37 keeps the temporary legacy path for this activity, so Activity.onBackPressed() is called.",
                        16));
        status = DemoUi.text(this, "", 18);
        DemoUi.addSection(root, status);
        updateStatus("Waiting for system Back.");

        setContentView(scrollView);
    }

    @Override
    public void onBackPressed() {
        backCount++;
        updateStatus("Temporary opt-out Activity.onBackPressed() was called.");
    }

    private void updateStatus(String event) {
        status.setText(event + "\nHandled opt-out back count: " + backCount);
    }
}

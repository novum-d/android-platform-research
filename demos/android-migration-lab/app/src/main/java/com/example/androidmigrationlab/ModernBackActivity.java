package com.example.androidmigrationlab;

import android.app.Activity;
import android.os.Build;
import android.os.Bundle;
import android.window.OnBackInvokedCallback;
import android.window.OnBackInvokedDispatcher;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

public final class ModernBackActivity extends Activity {
    private int backCount;
    private TextView status;
    private OnBackInvokedCallback callback;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        ScrollView scrollView = DemoUi.screen(this, "Modern predictive back");
        LinearLayout root = (LinearLayout) scrollView.getChildAt(0);

        DemoUi.addSection(
                root,
                DemoUi.text(
                        this,
                        "This activity opts in with android:enableOnBackInvokedCallback=\"true\" and registers OnBackInvokedCallback on API 33+.\n\n"
                                + "Expected: Android 16 + targetSdkVersion 36/37 calls the modern callback instead of legacy onBackPressed().",
                        16));
        status = DemoUi.text(this, "", 18);
        DemoUi.addSection(root, status);

        if (Build.VERSION.SDK_INT >= 33) {
            callback =
                    () -> {
                        backCount++;
                        updateStatus("OnBackInvokedCallback was called.");
                    };
            getOnBackInvokedDispatcher()
                    .registerOnBackInvokedCallback(
                            OnBackInvokedDispatcher.PRIORITY_DEFAULT, callback);
            updateStatus("Registered OnBackInvokedCallback.");
        } else {
            updateStatus("API < 33: falling back to Activity.onBackPressed().");
        }

        setContentView(scrollView);
    }

    @Override
    public void onBackPressed() {
        backCount++;
        updateStatus("Fallback Activity.onBackPressed() was called.");
    }

    @Override
    protected void onDestroy() {
        if (Build.VERSION.SDK_INT >= 33 && callback != null) {
            getOnBackInvokedDispatcher().unregisterOnBackInvokedCallback(callback);
        }
        super.onDestroy();
    }

    private void updateStatus(String event) {
        status.setText(event + "\nHandled modern back count: " + backCount);
    }
}

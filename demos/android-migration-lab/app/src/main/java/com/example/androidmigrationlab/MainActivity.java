package com.example.androidmigrationlab;

import android.app.Activity;
import android.os.Bundle;
import android.widget.LinearLayout;
import android.widget.ScrollView;

public final class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        ScrollView scrollView = DemoUi.screen(this, "Android Migration Lab");
        LinearLayout root = (LinearLayout) scrollView.getChildAt(0);

        DemoUi.addSection(
                root,
                DemoUi.text(
                        this,
                        "Predictive back demo for Android 15 / 16 / 17 and targetSdkVersion 35 / 36 / 37.\n\n"
                                + "Install each product flavor on the target OS image, then open the activities below and press system Back.",
                        16));
        DemoUi.addSection(root, DemoUi.button(this, "Legacy back only", LegacyBackActivity.class));
        DemoUi.addSection(root, DemoUi.button(this, "Modern predictive back", ModernBackActivity.class));
        DemoUi.addSection(root, DemoUi.button(this, "Temporary opt-out", TemporaryOptOutActivity.class));

        setContentView(scrollView);
    }
}

package com.example.androidmigrationlab;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

final class DemoUi {
    private DemoUi() {}

    static ScrollView screen(Activity activity, String title) {
        ScrollView scrollView = new ScrollView(activity);
        scrollView.setFillViewport(true);

        LinearLayout root = new LinearLayout(activity);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(activity, 20), dp(activity, 20), dp(activity, 20), dp(activity, 20));
        scrollView.addView(root);

        TextView heading = text(activity, title, 22);
        heading.setGravity(Gravity.START);
        root.addView(heading);

        TextView runtime =
                text(
                        activity,
                        "Runtime API: "
                                + Build.VERSION.SDK_INT
                                + "\nApp targetSdkVersion: "
                                + activity.getApplicationInfo().targetSdkVersion
                                + "\nFlavor target label: "
                                + BuildConfig.DEMO_TARGET_SDK,
                        16);
        runtime.setPadding(0, dp(activity, 12), 0, dp(activity, 12));
        root.addView(runtime);
        return scrollView;
    }

    static TextView text(Activity activity, String value, int sp) {
        TextView textView = new TextView(activity);
        textView.setText(value);
        textView.setTextSize(sp);
        textView.setLineSpacing(0, 1.15f);
        return textView;
    }

    static Button button(Activity activity, String label, Class<? extends Activity> destination) {
        Button button = new Button(activity);
        button.setText(label);
        button.setAllCaps(false);
        button.setOnClickListener(view -> activity.startActivity(new Intent(activity, destination)));
        return button;
    }

    static void addSection(LinearLayout root, View view) {
        LinearLayout.LayoutParams params =
                new LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT);
        params.setMargins(0, dp(root.getContext(), 12), 0, 0);
        root.addView(view, params);
    }

    static int dp(Context context, int value) {
        return Math.round(value * context.getResources().getDisplayMetrics().density);
    }
}

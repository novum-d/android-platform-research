plugins {
    alias(libs.plugins.android.application)
}

android {
    namespace = "com.example.androidmigrationlab"
    compileSdk = 37

    defaultConfig {
        applicationId = "com.example.androidmigrationlab"
        minSdk = 23
        targetSdk = 36
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }

    flavorDimensions += "targetSdk"
    productFlavors {
        create("target35") {
            dimension = "targetSdk"
            targetSdk = 35
            applicationIdSuffix = ".target35"
            versionNameSuffix = "-target35"
            buildConfigField("String", "DEMO_TARGET_SDK", "\"35\"")
        }
        create("target36") {
            dimension = "targetSdk"
            targetSdk = 36
            applicationIdSuffix = ".target36"
            versionNameSuffix = "-target36"
            buildConfigField("String", "DEMO_TARGET_SDK", "\"36\"")
        }
        create("target37") {
            dimension = "targetSdk"
            targetSdk = 37
            applicationIdSuffix = ".target37"
            versionNameSuffix = "-target37"
            buildConfigField("String", "DEMO_TARGET_SDK", "\"37\"")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    buildFeatures {
        aidl = false
        buildConfig = true
        shaders = false
    }
}

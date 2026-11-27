package com.lumina.wallpaper

import android.app.Activity
import android.os.Bundle

/** Launcher screen for verifying that the foundation APK installs and opens. */
class MainActivity : Activity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}

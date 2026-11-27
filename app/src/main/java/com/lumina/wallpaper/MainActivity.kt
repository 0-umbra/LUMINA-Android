package com.lumina.wallpaper

import android.app.Activity
import android.app.WallpaperManager
import android.content.ActivityNotFoundException
import android.content.ComponentName
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.Button
import android.widget.TextView
import com.lumina.wallpaper.service.CosmicWallpaperService

class MainActivity : Activity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        findViewById<Button>(R.id.preview_wallpaper).setOnClickListener {
            openWallpaperPreview()
        }
    }

    private fun openWallpaperPreview() {
        val status = findViewById<TextView>(R.id.wallpaper_status)
        status.visibility = View.GONE
        val component = ComponentName(this, CosmicWallpaperService::class.java)
        // This feature flag is a diagnostic, not a prerequisite for trying the system UI.
        val liveWallpaperReported = packageManager.hasSystemFeature(PackageManager.FEATURE_LIVE_WALLPAPER)
        Log.i(TAG, "Live wallpaper feature reported=$liveWallpaperReported; component=${component.flattenToShortString()}")

        val preview = Intent(WallpaperManager.ACTION_CHANGE_LIVE_WALLPAPER)
            .putExtra(WallpaperManager.EXTRA_LIVE_WALLPAPER_COMPONENT, component)
        val previewFailure = launchWallpaperActivity(preview) ?: return

        val chooser = Intent(WallpaperManager.ACTION_LIVE_WALLPAPER_CHOOSER)
        val chooserFailure = launchWallpaperActivity(chooser) ?: return

        val feature = if (liveWallpaperReported) R.string.wallpaper_feature_reported
        else R.string.wallpaper_feature_not_reported
        status.text = getString(
            R.string.preview_unavailable,
            getString(previewFailure),
            getString(chooserFailure),
            getString(feature),
        )
        status.visibility = View.VISIBLE
    }

    /** Returns a user-readable failure reason, or null if Android accepted the launch. */
    private fun launchWallpaperActivity(intent: Intent): Int? = try {
        // Launch directly: package visibility can hide an otherwise launchable activity.
        startActivity(intent)
        Log.i(TAG, "Android accepted ${intent.action}")
        null
    } catch (error: ActivityNotFoundException) {
        Log.w(TAG, "No activity available for ${intent.action}", error)
        R.string.wallpaper_launch_no_handler
    } catch (error: SecurityException) {
        Log.w(TAG, "Android denied launch for ${intent.action}", error)
        R.string.wallpaper_launch_denied
    }

    private companion object {
        const val TAG = "LuminaWallpaper"
    }
}

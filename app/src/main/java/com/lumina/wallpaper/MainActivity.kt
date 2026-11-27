package com.lumina.wallpaper

import android.app.Activity
import android.app.WallpaperManager
import android.content.ActivityNotFoundException
import android.content.ComponentName
import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.Toast
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
        val component = ComponentName(this, CosmicWallpaperService::class.java)
        val preview = Intent(WallpaperManager.ACTION_CHANGE_LIVE_WALLPAPER)
            .putExtra(WallpaperManager.EXTRA_LIVE_WALLPAPER_COMPONENT, component)
        try {
            // Launch directly: package visibility can hide an otherwise launchable activity.
            startActivity(preview)
        } catch (_: ActivityNotFoundException) {
            showPreviewUnavailable()
        } catch (_: SecurityException) {
            showPreviewUnavailable()
        }
    }

    private fun showPreviewUnavailable() {
        Toast.makeText(this, R.string.preview_unavailable, Toast.LENGTH_LONG).show()
    }
}

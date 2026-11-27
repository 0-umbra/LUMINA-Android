package com.lumina.wallpaper.service

import android.service.wallpaper.WallpaperService
import android.util.Log
import android.view.Surface
import android.view.SurfaceHolder

/** Android owns the engine and surface, including those used by the system preview. */
class CosmicWallpaperService : WallpaperService() {

    override fun onCreateEngine(): Engine = CosmicEngine()

    private inner class CosmicEngine : Engine() {
        private var renderer: CosmicRenderer? = null
        private var visible = false

        override fun onSurfaceCreated(holder: SurfaceHolder) {
            super.onSurfaceCreated(holder)
            renderer = CosmicRenderer()
        }

        override fun onSurfaceChanged(holder: SurfaceHolder, format: Int, width: Int, height: Int) {
            super.onSurfaceChanged(holder, format, width, height)
            if (visible) drawFrame(holder)
        }

        override fun onVisibilityChanged(visible: Boolean) {
            this.visible = visible
            if (visible) drawFrame(surfaceHolder)
        }

        override fun onSurfaceRedrawNeeded(holder: SurfaceHolder) {
            super.onSurfaceRedrawNeeded(holder)
            // Supply a frame for the system's redraw handshake, even before visibility is reported.
            drawFrame(holder)
        }

        override fun onSurfaceDestroyed(holder: SurfaceHolder) {
            renderer = null
            super.onSurfaceDestroyed(holder)
        }

        override fun onDestroy() {
            renderer = null
            visible = false
            super.onDestroy()
        }

        private fun drawFrame(holder: SurfaceHolder) {
            val currentRenderer = renderer ?: return
            if (!holder.surface.isValid) return

            try {
                // Lock the full surface: a new buffer need not contain any previous pixels.
                val canvas = holder.lockCanvas() ?: return
                try {
                    currentRenderer.draw(canvas)
                } finally {
                    holder.unlockCanvasAndPost(canvas)
                }
            } catch (e: Surface.OutOfResourcesException) {
                Log.w(TAG, "Could not acquire a wallpaper buffer", e)
            } catch (e: IllegalArgumentException) {
                // The system can invalidate a surface between the validity check and lock/post.
                Log.w(TAG, "Wallpaper surface is no longer drawable", e)
            }
        }
    }

    private companion object {
        const val TAG = "CosmicWallpaper"
    }
}

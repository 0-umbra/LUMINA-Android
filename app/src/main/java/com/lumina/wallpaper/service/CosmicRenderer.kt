package com.lumina.wallpaper.service

import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.RadialGradient
import android.graphics.Shader
import kotlin.random.Random

/** One static scene in normalized coordinates; no bitmaps or per-frame resource creation. */
internal class CosmicRenderer {
    private val blueGlow = Paint().apply {
        shader = RadialGradient(0.38f, 0.34f, 0.59f, 0xFF142A56.toInt(), 0x00142A56, Shader.TileMode.CLAMP)
    }
    private val violetGlow = Paint().apply {
        shader = RadialGradient(0.73f, 0.66f, 0.42f, 0x96362255.toInt(), 0x00362255, Shader.TileMode.CLAMP)
    }
    private val starPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = 0xFFD4E1FC.toInt() }
    private val stars = Random(13).let { random -> FloatArray(96) { random.nextFloat() } }

    fun draw(canvas: Canvas) {
        val width = canvas.width.toFloat()
        val height = canvas.height.toFloat()
        canvas.drawColor(0xFF050814.toInt())

        val checkpoint = canvas.save()
        canvas.scale(width, height)
        canvas.drawRect(0f, 0f, 1f, 1f, blueGlow)
        canvas.drawRect(0f, 0f, 1f, 1f, violetGlow)
        canvas.restoreToCount(checkpoint)

        val size = minOf(width, height) * 0.002f
        for (i in stars.indices step 3) {
            val light = stars[i + 2]
            starPaint.alpha = (35 + 100 * light).toInt()
            canvas.drawCircle(stars[i] * width, stars[i + 1] * height, size * (0.4f + 0.6f * light), starPaint)
        }
    }
}

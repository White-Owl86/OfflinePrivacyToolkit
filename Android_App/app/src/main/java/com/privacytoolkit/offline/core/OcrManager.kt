package com.privacytoolkit.offline.core

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.ColorMatrix
import android.graphics.ColorMatrixColorFilter
import android.graphics.Paint
import com.googlecode.tesseract.android.TessBaseAPI
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream
import java.io.InputStream

/**
 * Android Offline OCR Manager
 * Powered by Tesseract4Android native NDK runtime.
 * Extracts Persian (Farsi) and English text with zero internet requirement.
 */
class OcrManager(private val context: Context) {

    private val tessDataDir: File by lazy {
        File(context.filesDir, "tessdata").apply {
            if (!exists()) mkdirs()
        }
    }

    /**
     * Ensures traineddata models (fas & eng) are copied from assets to internal storage.
     */
    suspend fun prepareLanguageModels(): Boolean = withContext(Dispatchers.IO) {
        val models = listOf("fas.traineddata", "eng.traineddata")
        try {
            for (model in models) {
                val targetFile = File(tessDataDir, model)
                if (!targetFile.exists() || targetFile.length() == 0L) {
                    val assetStream: InputStream = context.assets.open("tessdata/$model")
                    val outStream = FileOutputStream(targetFile)
                    assetStream.copyTo(outStream)
                    assetStream.close()
                    outStream.close()
                }
            }
            true
        } catch (e: Exception) {
            e.printStackTrace()
            false
        }
    }

    /**
     * Enhance image for Persian OCR accuracy (Grayscale + High Contrast).
     */
    fun preprocessBitmap(source: Bitmap): Bitmap {
        val width = source.width
        val height = source.height
        val bmpGrayscale = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bmpGrayscale)
        val paint = Paint()

        // High contrast grayscale color matrix
        val matrix = ColorMatrix()
        matrix.setSaturation(0f)
        
        // Increase contrast
        val scale = 1.6f
        val translate = (-0.5f * scale + 0.5f) * 255f
        val contrastMatrix = floatArrayOf(
            scale, 0f, 0f, 0f, translate,
            0f, scale, 0f, 0f, translate,
            0f, 0f, scale, 0f, translate,
            0f, 0f, 0f, 1f, 0f
        )
        matrix.postConcat(ColorMatrix(contrastMatrix))

        paint.colorFilter = ColorMatrixColorFilter(matrix)
        canvas.drawBitmap(source, 0f, 0f, paint)
        return bmpGrayscale
    }

    /**
     * Performs text recognition offline.
     * @param bitmap Document image
     * @param language "fas", "eng", or "fas+eng"
     */
    suspend fun recognizeText(bitmap: Bitmap, language: String = "fas+eng"): Result<String> = withContext(Dispatchers.Default) {
        var tessApi: TessBaseAPI? = null
        try {
            // Prepare models if not ready
            prepareLanguageModels()

            val processed = preprocessBitmap(bitmap)
            tessApi = TessBaseAPI()
            
            // Parent folder of tessdata is required by Tesseract API
            val dataPath = context.filesDir.absolutePath
            val initSuccess = tessApi.init(dataPath, language)
            
            if (!initSuccess) {
                return@withContext Result.failure(Exception("Failed to initialize Tesseract with language: $language"))
            }

            tessApi.pageSegMode = TessBaseAPI.PageSegMode.PSM_AUTO
            tessApi.setImage(processed)
            val extractedText = tessApi.utF8Text ?: ""

            Result.success(extractedText.trim())
        } catch (e: Exception) {
            Result.failure(e)
        } finally {
            tessApi?.recycle()
        }
    }
}

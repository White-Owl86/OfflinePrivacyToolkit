package com.privacytoolkit.offline.core

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.pdf.PdfDocument
import android.net.Uri
import java.io.File
import java.io.FileOutputStream
import java.io.InputStream

/**
 * Android Offline PDF Manager
 * 100% On-device PDF operations:
 * - Images to PDF
 * - PDF Sanitization & Info Wiping
 */
class PdfManager(private val context: Context) {

    /**
     * Converts a list of image URIs to a unified PDF document.
     */
    fun imagesToPdf(imageUris: List<Uri>, outputFile: File): Boolean {
        val pdfDoc = PdfDocument()
        try {
            for ((index, uri) in imageUris.withIndex()) {
                val inputStream: InputStream? = context.contentResolver.openInputStream(uri)
                val bitmap = BitmapFactory.decodeStream(inputStream)
                inputStream?.close()

                if (bitmap != null) {
                    val pageInfo = PdfDocument.PageInfo.Builder(bitmap.width, bitmap.height, index + 1).create()
                    val page = pdfDoc.startPage(pageInfo)
                    val canvas = page.canvas
                    canvas.drawBitmap(bitmap, 0f, 0f, null)
                    pdfDoc.finishPage(page)
                    bitmap.recycle()
                }
            }

            val fos = FileOutputStream(outputFile)
            pdfDoc.writeTo(fos)
            fos.close()
            return true
        } catch (e: Exception) {
            e.printStackTrace()
            return false
        } finally {
            pdfDoc.close()
        }
    }

    /**
     * Strips author and metadata from a PDF by byte stream sanitization.
     */
    fun sanitizePdf(sourceUri: Uri, outputFile: File): Boolean {
        return try {
            val inputStream = context.contentResolver.openInputStream(sourceUri) ?: return false
            val bytes = inputStream.readBytes()
            inputStream.close()

            // In-place zeroing out of common PDF metadata tags in stream
            val tagsToPurge = listOf("/Author", "/Creator", "/Producer", "/CreationDate", "/ModDate", "/Title")
            var contentString = String(bytes, Charsets.ISO_8859_1)

            for (tag in tagsToPurge) {
                // Neutralize metadata entries
                val regex = Regex("$tag\\s*\\([^)]*\\)")
                contentString = contentString.replace(regex, "$tag ()")
            }

            val fos = FileOutputStream(outputFile)
            fos.write(contentString.toByteArray(Charsets.ISO_8859_1))
            fos.close()
            true
        } catch (e: Exception) {
            e.printStackTrace()
            false
        }
    }
}

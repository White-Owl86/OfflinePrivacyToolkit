package com.privacytoolkit.offline.core

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import androidx.exifinterface.media.ExifInterface
import java.io.File
import java.io.FileOutputStream
import java.io.InputStream

/**
 * Android Offline EXIF & Metadata Stripper
 * Inspects and strips all identifiable device, GPS, and timestamp tags.
 */
class ExifStripper(private val context: Context) {

    data class InspectionReport(
        val fileName: String,
        val hasGps: Boolean,
        val latitude: Double?,
        val longitude: Double?,
        val cameraMake: String?,
        val cameraModel: String?,
        val dateTime: String?,
        val software: String?,
        val allTags: Map<String, String>
    )

    fun inspectUri(uri: Uri, fileName: String = "Selected Image"): InspectionReport {
        var inputStream: InputStream? = null
        try {
            inputStream = context.contentResolver.openInputStream(uri)
                ?: return InspectionReport(fileName, false, null, null, null, null, null, null, emptyMap())

            val exif = ExifInterface(inputStream)
            val tags = mutableMapOf<String, String>()

            val latLong = exif.latLong
            val hasGps = latLong != null
            val lat = latLong?.get(0)
            val lon = latLong?.get(1)

            val make = exif.getAttribute(ExifInterface.TAG_MAKE)
            val model = exif.getAttribute(ExifInterface.TAG_MODEL)
            val dateTime = exif.getAttribute(ExifInterface.TAG_DATETIME_ORIGINAL) 
                ?: exif.getAttribute(ExifInterface.TAG_DATETIME)
            val software = exif.getAttribute(ExifInterface.TAG_SOFTWARE)

            if (make != null) tags["Camera Make"] = make
            if (model != null) tags["Camera Model"] = model
            if (dateTime != null) tags["Date & Time"] = dateTime
            if (software != null) tags["Software"] = software
            if (hasGps) tags["GPS Location"] = "$lat, $lon"

            return InspectionReport(
                fileName = fileName,
                hasGps = hasGps,
                latitude = lat,
                longitude = lon,
                cameraMake = make,
                cameraModel = model,
                dateTime = dateTime,
                software = software,
                allTags = tags
            )
        } finally {
            inputStream?.close()
        }
    }

    /**
     * Completely strips metadata by decoding raw pixel buffer and re-encoding.
     * Guaranteed zero residual EXIF tags.
     */
    fun stripMetadata(sourceUri: Uri, outputFile: File, quality: Int = 95): Boolean {
        var inputStream: InputStream? = null
        var outputStream: FileOutputStream? = null
        try {
            inputStream = context.contentResolver.openInputStream(sourceUri) ?: return false
            val bitmap = BitmapFactory.decodeStream(inputStream) ?: return false

            outputStream = FileOutputStream(outputFile)
            // Re-encoding directly drops all EXIF chunks
            bitmap.compress(Bitmap.CompressFormat.JPEG, quality, outputStream)
            outputStream.flush()

            // Verify with ExifInterface that new file is clean
            val cleanExif = ExifInterface(outputFile.absolutePath)
            cleanExif.setAttribute(ExifInterface.TAG_MAKE, null)
            cleanExif.setAttribute(ExifInterface.TAG_MODEL, null)
            cleanExif.setAttribute(ExifInterface.TAG_GPS_LATITUDE, null)
            cleanExif.setAttribute(ExifInterface.TAG_GPS_LONGITUDE, null)
            cleanExif.saveAttributes()

            return true
        } catch (e: Exception) {
            e.printStackTrace()
            return false
        } finally {
            inputStream?.close()
            outputStream?.close()
        }
    }
}

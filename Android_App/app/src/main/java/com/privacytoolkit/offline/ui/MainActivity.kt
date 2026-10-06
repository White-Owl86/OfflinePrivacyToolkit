package com.privacytoolkit.offline.ui

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.graphics.BitmapFactory
import android.net.Uri
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.EditText
import android.widget.RadioButton
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.viewpager2.adapter.FragmentStateAdapter
import com.google.android.material.button.MaterialButton
import com.google.android.material.tabs.TabLayoutMediator
import com.privacytoolkit.offline.R
import com.privacytoolkit.offline.core.ExifStripper
import com.privacytoolkit.offline.core.OcrManager
import com.privacytoolkit.offline.core.PdfManager
import com.privacytoolkit.offline.core.SecurityAuditor
import com.privacytoolkit.offline.databinding.ActivityMainBinding
import kotlinx.coroutines.launch
import java.io.File

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val securityAuditor by lazy { SecurityAuditor(this) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Verify Air-Gap at launch
        val status = securityAuditor.auditAppSecurity()
        binding.tvAuditStatus.text = if (status.isNetworkForbiddenByOs) "Air-Gapped: 0 Sockets" else "Network Alert"

        // Setup ViewPager2 and Tabs
        val adapter = ToolkitPagerAdapter(this)
        binding.viewPager.adapter = adapter

        val tabTitles = arrayOf(
            getString(R.string.tab_exif),
            getString(R.string.tab_pdf),
            getString(R.string.tab_ocr)
        )

        TabLayoutMediator(binding.tabLayout, binding.viewPager) { tab, position ->
            tab.text = tabTitles[position]
        }.attach()
    }

    private class ToolkitPagerAdapter(activity: AppCompatActivity) : FragmentStateAdapter(activity) {
        override fun getItemCount(): Int = 3
        override fun createFragment(position: Int): Fragment {
            return when (position) {
                0 -> ExifFragment()
                1 -> PdfFragment()
                else -> OcrFragment()
            }
        }
    }

    // ==========================================
    // FRAGMENT 1: EXIF STRIPPER
    // ==========================================
    class ExifFragment : Fragment() {
        private var selectedUri: Uri? = null
        private val exifStripper by lazy { ExifStripper(requireContext()) }

        private lateinit var tvStatus: TextView
        private lateinit var tvMetadata: TextView

        private val pickImageLauncher = registerForActivityResult(ActivityResultContracts.GetContent()) { uri: Uri? ->
            uri?.let {
                selectedUri = it
                tvStatus.text = it.toString()
                inspectFile(it)
            }
        }

        override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
            val view = inflater.inflate(R.layout.fragment_exif, container, false)
            tvStatus = view.findViewById(R.id.tvExifStatus)
            tvMetadata = view.findViewById(R.id.tvMetadataDetails)

            view.findViewById<MaterialButton>(R.id.btnSelectImage).setOnClickListener {
                pickImageLauncher.launch("image/*")
            }

            view.findViewById<MaterialButton>(R.id.btnStripExif).setOnClickListener {
                selectedUri?.let { uri ->
                    val outDir = requireContext().getExternalFilesDir(null) ?: requireContext().filesDir
                    val outFile = File(outDir, "Clean_${System.currentTimeMillis()}.jpg")
                    val ok = exifStripper.stripMetadata(uri, outFile)
                    if (ok) {
                        Toast.makeText(context, "${getString(R.string.clean_success)}\n${outFile.absolutePath}", Toast.LENGTH_LONG).show()
                        tvMetadata.text = "فایل پاکسازی شده ذخیره شد:\n${outFile.absolutePath}\nاندازه: ${outFile.length()} بایت"
                    } else {
                        Toast.makeText(context, "خطا در پاکسازی متاداده", Toast.LENGTH_SHORT).show()
                    }
                } ?: Toast.makeText(context, getString(R.string.no_image_selected), Toast.LENGTH_SHORT).show()
            }

            return view
        }

        private fun inspectFile(uri: Uri) {
            val report = exifStripper.inspectUri(uri)
            val sb = StringBuilder()
            sb.append("فایل: ").append(report.fileName).append("\n")
            if (report.hasGps) {
                sb.append("⚠️ موقعیت مکانی (GPS) شناسایی شد: ").append(report.latitude).append(", ").append(report.longitude).append("\n")
            }
            if (report.cameraModel != null) {
                sb.append("دوربین: ").append(report.cameraMake).append(" ").append(report.cameraModel).append("\n")
            }
            if (report.dateTime != null) {
                sb.append("تاریخ ثبت: ").append(report.dateTime).append("\n")
            }
            sb.append("\nکلیه تگ‌ها:\n")
            for ((k, v) in report.allTags) {
                sb.append("• ").append(k).append(": ").append(v).append("\n")
            }
            tvMetadata.text = sb.toString()
        }
    }

    // ==========================================
    // FRAGMENT 2: PDF TOOLKIT
    // ==========================================
    class PdfFragment : Fragment() {
        private val pdfManager by lazy { PdfManager(requireContext()) }
        private lateinit var tvResult: TextView

        private val pickPdfLauncher = registerForActivityResult(ActivityResultContracts.GetContent()) { uri: Uri? ->
            uri?.let {
                val outDir = requireContext().getExternalFilesDir(null) ?: requireContext().filesDir
                val outFile = File(outDir, "Sanitized_${System.currentTimeMillis()}.pdf")
                val ok = pdfManager.sanitizePdf(it, outFile)
                if (ok) {
                    tvResult.text = "تطهیر سند با موفقیت انجام شد:\n${outFile.absolutePath}"
                    Toast.makeText(context, "PDF کاملاً تطهیر شد", Toast.LENGTH_SHORT).show()
                } else {
                    tvResult.text = "خطا در تطهیر فایل PDF"
                }
            }
        }

        override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
            val view = inflater.inflate(R.layout.fragment_pdf, container, false)
            tvResult = view.findViewById(R.id.tvResult)

            view.findViewById<MaterialButton>(R.id.btnSanitizePdf).setOnClickListener {
                pickPdfLauncher.launch("application/pdf")
            }

            return view
        }
    }

    // ==========================================
    // FRAGMENT 3: OFFLINE OCR
    // ==========================================
    class OcrFragment : Fragment() {
        private var selectedUri: Uri? = null
        private val ocrManager by lazy { OcrManager(requireContext()) }
        private lateinit var etResult: EditText
        private lateinit var rbFas: RadioButton
        private lateinit var rbEng: RadioButton

        private val pickOcrDocLauncher = registerForActivityResult(ActivityResultContracts.GetContent()) { uri: Uri? ->
            uri?.let {
                selectedUri = it
                Toast.makeText(context, "سند انتخاب شد", Toast.LENGTH_SHORT).show()
            }
        }

        override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
            val view = inflater.inflate(R.layout.fragment_ocr, container, false)
            etResult = view.findViewById(R.id.etOcrResult)
            rbFas = view.findViewById(R.id.rbFas)
            rbEng = view.findViewById(R.id.rbEng)

            view.findViewById<MaterialButton>(R.id.btnSelectOcrDoc).setOnClickListener {
                pickOcrDocLauncher.launch("image/*")
            }

            view.findViewById<MaterialButton>(R.id.btnStartOcr).setOnClickListener {
                selectedUri?.let { uri ->
                    runOcr(uri)
                } ?: Toast.makeText(context, "لطفاً ابتدا یک تصویر را انتخاب کنید", Toast.LENGTH_SHORT).show()
            }

            view.findViewById<MaterialButton>(R.id.btnCopyText).setOnClickListener {
                val text = etResult.text.toString()
                if (text.isNotEmpty()) {
                    val clipboard = requireContext().getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                    val clip = ClipData.newPlainText("OCR Text", text)
                    clipboard.setPrimaryClip(clip)
                    Toast.makeText(context, getString(R.string.copied_to_clipboard), Toast.LENGTH_SHORT).show()
                }
            }

            return view
        }

        private fun runOcr(uri: Uri) {
            etResult.setText("در حال استخراج آفلاین متن با هوش مصنوعی...")
            lifecycleScope.launch {
                try {
                    val inputStream = requireContext().contentResolver.openInputStream(uri)
                    val bitmap = BitmapFactory.decodeStream(inputStream)
                    inputStream?.close()

                    if (bitmap == null) {
                        etResult.setText("خطا در بارگذاری تصویر.")
                        return@launch
                    }

                    val lang = when {
                        rbFas.isChecked -> "fas"
                        rbEng.isChecked -> "eng"
                        else -> "fas+eng"
                    }

                    val result = ocrManager.recognizeText(bitmap, lang)
                    result.onSuccess { text ->
                        etResult.setText(if (text.isBlank()) "(متنی در سند یافت نشد)" else text)
                    }.onFailure { err ->
                        etResult.setText("خطای OCR: ${err.message}")
                    }
                } catch (e: Exception) {
                    etResult.setText("خطا: ${e.message}")
                }
            }
        }
    }
}

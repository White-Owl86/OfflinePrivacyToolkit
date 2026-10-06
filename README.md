# 🛡️ Offline Privacy & Document Toolkit

[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Android-blue.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.9%2B-brightgreen.svg)](https://python.org)
[![Kotlin](https://img.shields.io/badge/Kotlin-Android%20Material%203-purple.svg)](https://kotlinlang.org)
[![Security](https://img.shields.io/badge/Privacy-100%25%20Air--Gapped-red.svg)](#)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#)

[English](#english) | [فارسی](#فارسی)

---

## English

A comprehensive, air-gapped, and **100% offline** document processing and data privacy suite for **Windows Desktop** and **Android Mobile**.

Perform everyday sensitive document tasks—such as stripping camera/GPS metadata, managing PDFs, and performing optical character recognition (OCR) in Persian and English—without transmitting a single byte over the network or relying on untrusted cloud services.

### 🌟 Key Features

1. **Metadata & EXIF Stripper:**
   - Deeply inspects and permanently strips GPS coordinates, camera models, lens data, serial numbers, software tags, and XMP metadata.
   - Supports JPG, PNG, WEBP, TIFF, BMP, and PDF files.
   - Includes bulk folder sanitization with one click.

2. **Offline PDF Toolkit:**
   - **Merge & Split:** Combine documents or extract custom page ranges without quality degradation.
   - **Smart Compression:** Reduce file size up to 50%+ while preserving text clarity.
   - **Sanitize & Anti-Spying:** Strips embedded JavaScript, external links, tracker annotations, and file attachments.
   - **Two-way Image Conversion:** Batch convert images to PDF and render high-resolution 200/300 DPI page images from PDFs.

3. **Local Offline OCR (English & Persian):**
   - High-accuracy optical character recognition powered by offline Tesseract neural models (`eng` + `fas`).
   - Integrated image preprocessing pipeline (contrast enhancement, binarization, median denoising, and Persian dot/diacritic sharpening).
   - Instant copy-to-clipboard and export to text (.txt).

4. **Guaranteed Air-Gapped Security:**
   - **Android:** The `android.permission.INTERNET` manifest permission is deliberately omitted at the OS/kernel level.
   - **Windows:** Pure local execution with an integrated network audit monitor that verifies zero socket creation or external telemetry.

---

### 📂 Repository Structure

```text
├── 🖥️ Windows_App/                     # Windows Desktop Application (Python + CustomTkinter)
│   ├── src/
│   │   ├── main.py                     # Entry point
│   │   ├── core/                       # Core modules (exif_stripper, pdf_toolkit, ocr_engine, security_audit)
│   │   ├── ui/                         # Modern bilingual graphical interface (English / Persian)
│   │   └── utils/                      # Logging and file helpers
│   ├── tessdata/                       # Offline AI models (fas.traineddata, eng.traineddata)
│   ├── requirements.txt                # Python dependencies
│   ├── run_app.bat                     # Quick launch launcher
│   └── build_exe.bat                   # Standalone .exe packager script
│
├── 📱 Android_App/                     # Android Mobile Application (Kotlin + Material 3)
│   ├── app/
│   │   └── src/main/
│   │       ├── AndroidManifest.xml     # Isolated air-gapped manifest (No INTERNET permission)
│   │       ├── assets/tessdata/        # Embedded English & Persian OCR models
│   │       ├── java/.../core/          # Native ExifStripper, PdfManager, OcrManager
│   │       └── res/                    # Material 3 UI layouts & bilingual translations
│   ├── build.gradle.kts
│   └── settings.gradle.kts
│
└── 📚 Docs/                            # Technical specifications & documentation
    ├── ARCHITECTURE_AND_SECURITY_AUDIT.md
    └── USER_MANUAL_FA.md
```

---

### 🚀 Quick Start

#### Windows Desktop
```powershell
cd Windows_App
pip install -r requirements.txt
python src/main.py
```
*Or simply double-click `Windows_App/run_app.bat`.*

To build a standalone `.exe` without requiring Python on destination systems:
```powershell
.\Windows_App\build_exe.bat
```

#### Android Mobile
1. Open `Android_App/` in **Android Studio** (Flamingo or later).
2. Sync Gradle and select **Build > Build Bundle(s) / APK(s) > Build APK(s)**.
3. The resulting `.apk` can be installed on any device running Android 8.0 (API 26) or newer.

---

## فارسی

### ابزار محلی و کاملاً آفلاین پردازش اسناد و امنیت داده‌ها (ویندوز + اندروید)

پروژه پیش‌رو یک راهکار همه‌جانبه، امن و ۱۰۰ درصد آفلاین است که کارهای پرتکرار روزمره روی فایل‌ها و اسناد را بر روی **کامپیوترهای ویندوز** و **گوشی‌های موبایل اندروید** بدون ارسال حتی ۱ بایت به اینترنت انجام می‌دهد.

### 🌟 قابلیت‌های شاخص
1. **حذف متاداده و امنیت تصاویر (EXIF Stripper):**
   - حذف کامل اطلاعات GPS، مدل دوربین، لنز، مشخصات نرم‌افزاری و تاریخچه ویرایش از تصاویر JPG, PNG, WEBP, TIFF, BMP و PDF.
   - امکان بررسی و گزارش‌گیری قبل از پاکسازی + حالت پاکسازی دسته‌ای کل یک پوشه.
2. **جعبه ابزار آفلاین PDF:**
   - ادغام (Merge)، فشرده‌سازی هوشمند (Compress)، تفکیک صفحات (Split)، تطهیر ضدجاسوسی و حذف ردیاب‌ها (Sanitize).
   - تبدیل سریع عکس‌ها به PDF و تبدیل PDF به تصاویر با کیفیت بالا.
3. **تبدیل عکس به متن (OCR آفلاین فارسی و انگلیسی):**
   - استخراج متن از عکس اسناد اداری، فاکتورها، کتاب‌ها و فایل‌های PDF اسکن‌شده.
   - دارای خط لوله پیش‌پردازش تصویر جهت حذف نویز و بهبود اعراب و نقطه‌های فارسی.
4. **تضمین ۱۰۰٪ حریم خصوصی (Air-Gapped):**
   - در اندروید: دسترسی `android.permission.INTERNET` به صورت عمدی حذف شده تا سیستم‌عامل هرگونه اتصال خارجی را مسدود کند.
   - در ویندوز: ماژول‌های پردازش مستقیماً روی سخت‌افزار محلی اجرا شده و هیچ ترافیک شبکه‌ای تولید نمی‌کنند.

### 🚀 نحوه اجرای سریع ویندوز
کافیست فایل زیر را اجرا کنید:
```powershell
Windows_App\run_app.bat
```
جهت ساخت خروجی فایل اجرایی مستقل (.exe):
```powershell
Windows_App\build_exe.bat
```

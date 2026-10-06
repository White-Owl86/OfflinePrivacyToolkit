"""
Offline OCR Engine for Persian (Farsi) and English
Completely local, private, and high-accuracy text extraction.
Supports Image & PDF input with advanced image enhancement.
"""

import os
import sys
import shutil
from typing import Tuple, Optional, List, Dict, Any
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
import pytesseract
import pymupdf as fitz
import arabic_reshaper
from bidi.algorithm import get_display

try:
    from ..utils.logger import logger
except (ImportError, ValueError):
    from utils.logger import logger

class OcrEngine:
    """Local, offline OCR engine with Persian and English support."""

    def __init__(self, custom_tessdata_dir: Optional[str] = None):
        self.tesseract_cmd = self._find_tesseract_binary()
        if self.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

        # Locate tessdata directory
        if custom_tessdata_dir and os.path.exists(custom_tessdata_dir):
            self.tessdata_dir = custom_tessdata_dir
        else:
            # Check local app tessdata
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            candidate = os.path.join(base_dir, "tessdata")
            if os.path.exists(candidate):
                self.tessdata_dir = candidate
            else:
                self.tessdata_dir = None

    def _find_tesseract_binary(self) -> Optional[str]:
        """Locate Tesseract executable on the system."""
        # 1. Check PATH
        path_cmd = shutil.which("tesseract")
        if path_cmd:
            return path_cmd

        # 2. Check standard Windows installation paths
        common_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Users\it-d\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
        ]
        for p in common_paths:
            if os.path.exists(p):
                return p

        # 3. Check relative local bundle
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        local_bin = os.path.join(base_dir, "tesseract_bin", "tesseract.exe")
        if os.path.exists(local_bin):
            return local_bin

        return None

    def is_tesseract_installed(self) -> bool:
        """Check if Tesseract binary is available."""
        if not self.tesseract_cmd or not os.path.exists(self.tesseract_cmd):
            # Check if pytesseract can run
            try:
                pytesseract.get_tesseract_version()
                return True
            except Exception:
                return False
        return True

    def get_available_languages(self) -> List[str]:
        """List languages available in tessdata."""
        langs = []
        if self.tessdata_dir and os.path.exists(self.tessdata_dir):
            for f in os.listdir(self.tessdata_dir):
                if f.endswith(".traineddata"):
                    langs.append(f.replace(".traineddata", ""))
        return langs

    @staticmethod
    def preprocess_image(image: Image.Image, auto_enhance: bool = True) -> Image.Image:
        """
        Enhance scanned document or photo for maximum Persian/English OCR accuracy:
        - Grayscale conversion
        - Contrast amplification
        - Median filtering for speckle/noise reduction
        - Resizing if low resolution
        """
        # Convert to Grayscale
        img = image.convert("L")

        if auto_enhance:
            # Resize small images to minimum 300 DPI equivalent
            w, h = img.size
            if max(w, h) < 1800:
                scale_factor = 2.0
                img = img.resize((int(w * scale_factor), int(h * scale_factor)), Image.Resampling.LANCZOS)

            # Auto contrast normalization
            img = ImageOps.autocontrast(img, cutoff=2)

            # Contrast enhancer
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.8)

            # Sharpness enhancer (helps distinct Persian dots and accents)
            sharpener = ImageEnhance.Sharpness(img)
            img = sharpener.enhance(1.5)

            # Mild noise filter to remove dust/speckles
            img = img.filter(ImageFilter.MedianFilter(size=3))

        return img

    def recognize_image(
        self,
        image_path: str,
        lang: str = "fas+eng",
        enhance: bool = True
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Extract text from an image completely offline.
        lang: 'fas' (Persian), 'eng' (English), 'fas+eng' (Bilingual)
        """
        stats = {"char_count": 0, "word_count": 0, "language": lang}
        try:
            if not self.is_tesseract_installed():
                err_msg = (
                    "موتور Tesseract روی سیستم یافت نشد.\n"
                    "لطفاً نرم‌افزار رایگان Tesseract OCR را نصب فرمایید یا مسیر آن را در تنظیمات وارد نمایید.\n"
                    "Tesseract is not found on your system. Please install Tesseract-OCR."
                )
                return False, err_msg, stats

            pil_img = Image.open(image_path)
            processed_img = self.preprocess_image(pil_img, auto_enhance=enhance)

            # Build config string with custom tessdata if available
            config_parts = []
            if self.tessdata_dir:
                # Need forward slashes or escaped backslashes for tesseract
                clean_dir = self.tessdata_dir.replace("\\", "/")
                config_parts.append(f'--tessdata-dir "{clean_dir}"')

            # OEM 1 (LSTM neural net mode), PSM 3 (Fully automatic page segmentation)
            config_parts.append("--oem 1 --psm 3")
            custom_config = " ".join(config_parts)

            raw_text = pytesseract.image_to_string(processed_img, lang=lang, config=custom_config)
            cleaned_text = raw_text.strip()

            stats["char_count"] = len(cleaned_text)
            stats["word_count"] = len(cleaned_text.split())

            logger.info(f"OCR completed for {image_path}: {stats['word_count']} words recognized.")
            return True, cleaned_text, stats

        except Exception as e:
            logger.error(f"OCR failed for {image_path}: {e}")
            return False, f"OCR Error: {str(e)}", stats

    def recognize_pdf(
        self,
        pdf_path: str,
        lang: str = "fas+eng",
        enhance: bool = True,
        progress_callback = None
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Perform offline OCR on scanned PDF document by rendering pages offline.
        """
        stats = {"char_count": 0, "word_count": 0, "pages_processed": 0, "language": lang}
        try:
            if not self.is_tesseract_installed():
                return False, "Tesseract OCR engine is not installed.", stats

            doc = fitz.open(pdf_path)
            total_pages = doc.page_count
            full_text_pages = []

            for page_idx in range(total_pages):
                page = doc[page_idx]
                # Render to high-res image (200 DPI for high OCR accuracy)
                pix = page.get_pixmap(dpi=200, alpha=False)
                
                import io
                img_bytes = pix.tobytes("png")
                pil_img = Image.open(io.BytesIO(img_bytes))

                processed_img = self.preprocess_image(pil_img, auto_enhance=enhance)

                config_parts = []
                if self.tessdata_dir:
                    clean_dir = self.tessdata_dir.replace("\\", "/")
                    config_parts.append(f'--tessdata-dir "{clean_dir}"')
                config_parts.append("--oem 1 --psm 3")
                custom_config = " ".join(config_parts)

                page_text = pytesseract.image_to_string(processed_img, lang=lang, config=custom_config).strip()
                page_header = f"\n=== صفحه {page_idx + 1} از {total_pages} (Page {page_idx + 1}/{total_pages}) ===\n"
                full_text_pages.append(f"{page_header}\n{page_text}")

                if progress_callback:
                    progress_callback(page_idx + 1, total_pages)

            doc.close()
            combined_text = "\n\n".join(full_text_pages)

            stats["pages_processed"] = total_pages
            stats["char_count"] = len(combined_text)
            stats["word_count"] = len(combined_text.split())

            logger.info(f"PDF OCR completed for {pdf_path}: {total_pages} pages processed.")
            return True, combined_text, stats

        except Exception as e:
            logger.error(f"PDF OCR failed for {pdf_path}: {e}")
            return False, f"PDF OCR Error: {str(e)}", stats

    @staticmethod
    def reshape_persian_for_display(text: str) -> str:
        """Utility for bi-directional display if running in terminal or simple canvas."""
        try:
            reshaped = arabic_reshaper.reshape(text)
            return get_display(reshaped)
        except Exception:
            return text

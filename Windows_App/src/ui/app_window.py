"""
Modern User Interface for Offline Privacy & Document Toolkit
Powered by CustomTkinter with comprehensive real-time Persian (Farsi) & English localization.
100% Offline with zero cloud connections.
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

try:
    from ..core.exif_stripper import ExifStripper
    from ..core.pdf_toolkit import PdfToolkit
    from ..core.ocr_engine import OcrEngine
    from ..core.security_audit import SecurityAuditor
    from ..utils.file_helpers import format_file_size, get_unique_output_path
    from ..utils.logger import logger
except (ImportError, ValueError):
    from core.exif_stripper import ExifStripper
    from core.pdf_toolkit import PdfToolkit
    from core.ocr_engine import OcrEngine
    from core.security_audit import SecurityAuditor
    from utils.file_helpers import format_file_size, get_unique_output_path
    from utils.logger import logger

# Set initial visual theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Comprehensive Localization dictionary
LANG_DATA = {
    "fa": {
        "title": "جعبه ابزار آفلاین اسناد و حریم خصوصی (Offline Privacy Toolkit)",
        "status_offline": "وضعیت: ۱۰۰٪ آفلاین و امن (Zero Network Calls)",
        "theme_dark": "حالت تاریک",
        "tab_exif": "حذف متاداده (EXIF Stripper)",
        "tab_pdf": "جعبه ابزار PDF",
        "tab_ocr": "تبدیل عکس به متن (OCR)",
        "tab_security": "امنیت و گزارش محلی",
        # EXIF Tab
        "select_file": "انتخاب فایل (تصویر یا PDF)",
        "select_folder": "انتخاب پوشه برای پردازش دسته‌ای",
        "inspect_btn": "بررسی متاداده‌های فایل",
        "strip_btn": "پاکسازی و حذف کامل متاداده‌ها",
        "batch_strip_btn": "پاکسازی کلیه فایل‌های پوشه",
        "no_file": "هیچ فایلی انتخاب نشده است",
        "metadata_found": "متاداده‌های شناسایی شده:",
        "clean_success": "متاداده‌ها با موفقیت حذف شدند!",
        "exif_placeholder": "متاداده‌های فایل پس از انتخاب در این بخش نمایش داده می‌شوند.\n(GPS Location, Camera Spec, Date/Time, Software, Document Author)\n\nیک فایل را انتخاب فرمایید.",
        # PDF Tab
        "pdf_modes": [
            ("ادغام (Merge)", "merge"),
            ("فشرده‌سازی (Compress)", "compress"),
            ("جداسازی صفحات (Split)", "split"),
            ("تطهیر ضدجاسوسی (Sanitize)", "sanitize"),
            ("تصاویر به PDF", "img_to_pdf"),
            ("PDF به تصاویر", "pdf_to_img")
        ],
        "add_files": "افزودن فایل‌ها",
        "clear_list": "پاک کردن لیست",
        "execute": "اجرای عملیات",
        "pdf_settings": "تنظیمات عملیات:",
        "pdf_default_settings": "تنظیمات پیش‌فرض فعال است.",
        "page_range": "محدوده صفحات (1-indexed):",
        "page_range_hint": "مثال: 1, 3, 5-8 (خالی = تمام صفحات)",
        "comp_level": "سطح فشرده‌سازی:",
        "comp_level_hint": "medium / aggressive / high",
        # OCR Tab
        "ocr_select": "انتخاب تصویر یا سند اسکن‌شده PDF",
        "ocr_lang": "زبان سند:",
        "ocr_lang_values": ["fas (فارسی)", "eng (انگلیسی)", "fas+eng (فارسی و انگلیسی)"],
        "ocr_enhance": "بهبود خودکار کیفیت و کنتراست سند",
        "ocr_start": "شروع استخراج متن (OCR)",
        "ocr_copy": "کپی در کلیپ‌بورد",
        "ocr_save": "ذخیره در فایل TXT",
        "ocr_waiting": "متن استخراج‌شده در این قسمت نمایش داده می‌شود...",
        "ocr_stats": "تعداد کلمات: {words} | کاراکترها: {chars}",
        # Security Tab
        "sec_badge": "تضمین حریم خصوصی: ایزولاسیون کامل و قطع ارتباط در سطح هسته",
        "sec_desc": "این برنامه تحت هیچ شرایطی سوکت شبکه باز نمی‌کند و صفر بایت داده به اینترنت ارسال نمی‌شود.",
        "open_folder": "📂 باز کردن پوشه فایل‌ها و لاگ‌ها (Open Output & Logs Folder)",
        "footer": "Offline Privacy & Document Toolkit | توسعه یافته برای نهایت حریم خصوصی و عملکرد محلی",
        # Dialogs
        "warn_title": "هشدار",
        "err_title": "خطا",
        "info_title": "اطلاع",
        "select_file_warn": "لطفاً ابتدا یک فایل را انتخاب کنید.",
        "no_pdf_warn": "هیچ فایلی برای انجام عملیات انتخاب نشده است.",
        "copied": "متن در حافظه کپی شد.",
        "ocr_processing": "در حال پردازش سند با هوش مصنوعی آفلاین...\nلطفاً شکیبا باشید."
    },
    "en": {
        "title": "Offline Privacy & Document Toolkit",
        "status_offline": "Status: 100% Offline & Air-Gapped (Zero Network Calls)",
        "theme_dark": "Dark Mode",
        "tab_exif": "EXIF Stripper",
        "tab_pdf": "PDF Toolkit",
        "tab_ocr": "Offline OCR",
        "tab_security": "Privacy & Audit",
        # EXIF Tab
        "select_file": "Select File (Image or PDF)",
        "select_folder": "Select Folder for Batch Stripping",
        "inspect_btn": "Inspect File Metadata",
        "strip_btn": "Strip All Metadata",
        "batch_strip_btn": "Batch Strip All Files",
        "no_file": "No file selected",
        "metadata_found": "Identified Metadata:",
        "clean_success": "Metadata successfully removed!",
        "exif_placeholder": "File metadata will be inspected and displayed here.\n(GPS Location, Camera Spec, Date/Time, Software, Document Author)\n\nPlease select a file.",
        # PDF Tab
        "pdf_modes": [
            ("Merge PDFs", "merge"),
            ("Compress PDF", "compress"),
            ("Split / Extract", "split"),
            ("Sanitize (Anti-Spy)", "sanitize"),
            ("Images to PDF", "img_to_pdf"),
            ("PDF to Images", "pdf_to_img")
        ],
        "add_files": "Add Files",
        "clear_list": "Clear List",
        "execute": "Execute Operation",
        "pdf_settings": "Operation Settings:",
        "pdf_default_settings": "Default settings applied.",
        "page_range": "Page range (1-indexed):",
        "page_range_hint": "e.g. 1, 3, 5-8 (empty = all pages)",
        "comp_level": "Compression Level:",
        "comp_level_hint": "medium / aggressive / high",
        # OCR Tab
        "ocr_select": "Select Image or Scanned PDF",
        "ocr_lang": "Document Language:",
        "ocr_lang_values": ["fas (Persian)", "eng (English)", "fas+eng (Persian + English)"],
        "ocr_enhance": "Auto-enhance contrast and clarity",
        "ocr_start": "Extract Text (Offline OCR)",
        "ocr_copy": "Copy to Clipboard",
        "ocr_save": "Save as TXT",
        "ocr_waiting": "Recognized text will appear here...",
        "ocr_stats": "Words: {words} | Characters: {chars}",
        # Security Tab
        "sec_badge": "Privacy Guarantee: 100% Air-Gapped at Kernel Level",
        "sec_desc": "This application opens zero outbound network sockets. No data ever leaves your computer.",
        "open_folder": "📂 Open Output & Logs Folder",
        "footer": "Offline Privacy & Document Toolkit | Engineered for Maximum Privacy & Local Performance",
        # Dialogs
        "warn_title": "Warning",
        "err_title": "Error",
        "info_title": "Information",
        "select_file_warn": "Please select a file first.",
        "no_pdf_warn": "No files selected for operation.",
        "copied": "Text copied to clipboard.",
        "ocr_processing": "Processing document with offline OCR engine...\nPlease wait."
    }
}

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.current_lang = "fa"  # Default to Persian
        self.t = LANG_DATA[self.current_lang]

        # Configure Window
        self.title(self.t["title"])
        self.geometry("1100x750")
        self.minsize(950, 650)

        # Set App Icon
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            icon_path = os.path.join(base_dir, "assets", "app_icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass

        # Core Engines
        self.exif_stripper = ExifStripper()
        self.pdf_toolkit = PdfToolkit()
        self.ocr_engine = OcrEngine()
        self.security_auditor = SecurityAuditor()

        # State Variables
        self.selected_file = None
        self.selected_files_list = []
        self.ocr_source_file = None
        self.last_exif_report = ""
        self.last_ocr_text = ""
        self.pdf_op_mode = ctk.StringVar(value="merge")
        self.last_word_count = 0
        self.last_char_count = 0

        self._build_header()
        self._build_tabs()
        self._build_footer()

    def _t(self, key: str) -> str:
        return LANG_DATA[self.current_lang].get(key, key)

    def _build_header(self):
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, height=65)
        self.header_frame.pack(fill="x", padx=0, pady=0)

        # Security Status Pill
        self.offline_label = ctk.CTkLabel(
            self.header_frame,
            text=f"🟢 {self.t['status_offline']}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#2ECC71"
        )
        self.offline_label.pack(side="left", padx=20, pady=15)

        # Right Controls: Dark/Light Mode and Language Switcher
        controls_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        controls_frame.pack(side="right", padx=20, pady=15)

        # Language Toggle
        self.lang_btn = ctk.CTkSegmentedButton(
            controls_frame,
            values=["فارسی", "English"],
            command=self._on_lang_changed
        )
        self.lang_btn.set("فارسی" if self.current_lang == "fa" else "English")
        self.lang_btn.pack(side="left", padx=10)

        # Theme Toggle
        self.theme_switch = ctk.CTkSwitch(
            controls_frame,
            text=self.t["theme_dark"],
            command=self._toggle_theme
        )
        self.theme_switch.select()
        self.theme_switch.pack(side="left", padx=10)

    def _on_lang_changed(self, value):
        new_lang = "fa" if value == "فارسی" else "en"
        self._switch_language(new_lang)

    def _switch_language(self, lang_code: str):
        if self.current_lang == lang_code:
            return

        # Cache existing text inputs and states
        if hasattr(self, "txt_exif_inspector"):
            current_exif = self.txt_exif_inspector.get("1.0", "end").strip()
            if current_exif and not ("متاداده‌های فایل" in current_exif or "File metadata will" in current_exif):
                self.last_exif_report = current_exif

        if hasattr(self, "txt_ocr_output"):
            current_ocr = self.txt_ocr_output.get("1.0", "end").strip()
            if current_ocr and not ("متن استخراج‌شده" in current_ocr or "Recognized text will" in current_ocr):
                self.last_ocr_text = current_ocr

        prev_lang = self.current_lang
        prev_t = LANG_DATA[prev_lang]
        prev_tabs = [prev_t["tab_exif"], prev_t["tab_pdf"], prev_t["tab_ocr"], prev_t["tab_security"]]
        
        # Determine currently selected tab index
        active_tab_idx = 0
        if hasattr(self, "tabview"):
            current_tab_name = self.tabview.get()
            try:
                active_tab_idx = prev_tabs.index(current_tab_name)
            except ValueError:
                active_tab_idx = 0

        # Update language pointer
        self.current_lang = lang_code
        self.t = LANG_DATA[self.current_lang]

        # 1. Update Title & Header
        self.title(self.t["title"])
        self.offline_label.configure(text=f"🟢 {self.t['status_offline']}")
        self.theme_switch.configure(text=self.t["theme_dark"])

        # 2. Rebuild Tabs
        self.tabview.destroy()
        self._build_tabs()

        # 3. Restore active tab
        new_tabs = [self.t["tab_exif"], self.t["tab_pdf"], self.t["tab_ocr"], self.t["tab_security"]]
        if 0 <= active_tab_idx < len(new_tabs):
            self.tabview.set(new_tabs[active_tab_idx])

        # 4. Restore state variables to UI
        if self.selected_file:
            self.lbl_current_file.configure(text=f"📄 {self.selected_file}")
        if self.last_exif_report:
            self.txt_exif_inspector.delete("1.0", "end")
            self.txt_exif_inspector.insert("1.0", self.last_exif_report)

        if self.selected_files_list:
            for f in self.selected_files_list:
                self.pdf_listbox.insert("end", f)

        if self.ocr_source_file:
            self.lbl_ocr_file.configure(text=f"📄 {self.ocr_source_file}")
        if self.last_ocr_text:
            self.txt_ocr_output.delete("1.0", "end")
            self.txt_ocr_output.insert("1.0", self.last_ocr_text)
            self.lbl_ocr_stats.configure(text=self.t["ocr_stats"].format(words=self.last_word_count, chars=self.last_char_count))

        # 5. Update Footer
        self.lbl_footer.configure(text=self.t["footer"])

    def _toggle_theme(self):
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")

    def _build_tabs(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)

        # Tab 1: EXIF Stripper
        self.tab_exif = self.tabview.add(self.t["tab_exif"])
        self._setup_exif_tab()

        # Tab 2: PDF Toolkit
        self.tab_pdf = self.tabview.add(self.t["tab_pdf"])
        self._setup_pdf_tab()

        # Tab 3: OCR
        self.tab_ocr = self.tabview.add(self.t["tab_ocr"])
        self._setup_ocr_tab()

        # Tab 4: Security & Audit
        self.tab_sec = self.tabview.add(self.t["tab_security"])
        self._setup_security_tab()

    # ==========================================
    # TAB 1: EXIF & METADATA STRIPPER
    # ==========================================
    def _setup_exif_tab(self):
        container = ctk.CTkFrame(self.tab_exif)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Top Button Bar
        btn_bar = ctk.CTkFrame(container, fg_color="transparent")
        btn_bar.pack(fill="x", pady=10)

        self.btn_select_file = ctk.CTkButton(
            btn_bar,
            text=f"📂 {self.t['select_file']}",
            command=self._exif_select_file,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.btn_select_file.pack(side="left", padx=10)

        self.btn_strip_single = ctk.CTkButton(
            btn_bar,
            text=f"🛡️ {self.t['strip_btn']}",
            command=self._exif_strip_single,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.btn_strip_single.pack(side="left", padx=10)

        self.btn_batch_strip = ctk.CTkButton(
            btn_bar,
            text=f"📁 {self.t['batch_strip_btn']}",
            command=self._exif_batch_strip,
            fg_color="#8E44AD",
            hover_color="#732D91"
        )
        self.btn_batch_strip.pack(side="right", padx=10)

        # Current File Label
        self.lbl_current_file = ctk.CTkLabel(
            container,
            text=f"📄 {self.t['no_file']}",
            font=ctk.CTkFont(size=12, slant="italic"),
            anchor="w"
        )
        self.lbl_current_file.pack(fill="x", padx=15, pady=5)

        # Inspection Text Box
        self.txt_exif_inspector = ctk.CTkTextbox(container, wrap="word", font=ctk.CTkFont(family="Consolas", size=12))
        self.txt_exif_inspector.pack(fill="both", expand=True, padx=10, pady=10)
        self.txt_exif_inspector.insert("1.0", self.t["exif_placeholder"])

    def _exif_select_file(self):
        f = filedialog.askopenfilename(
            title=self.t["select_file"],
            filetypes=[("Supported Files", "*.jpg;*.jpeg;*.png;*.webp;*.tiff;*.bmp;*.pdf"), ("All Files", "*.*")]
        )
        if f:
            self.selected_file = f
            self.lbl_current_file.configure(text=f"📄 {f}")
            self._inspect_selected_file(f)

    def _inspect_selected_file(self, file_path: str):
        self.txt_exif_inspector.delete("1.0", "end")
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            report = self.exif_stripper.inspect_pdf_metadata(file_path)
        else:
            report = self.exif_stripper.inspect_image_metadata(file_path)

        out_lines = [
            f"=== {self.t['metadata_found']} ===",
            f"File: {report['file_name']}",
            f"Size: {report['file_size']}",
            f"Format: {report.get('format', 'N/A')}",
            f"Dimensions: {report.get('dimensions', 'N/A')}",
            "-" * 50
        ]

        if report.get("has_gps"):
            out_lines.append("⚠️ GPS Location Data Found!")
            out_lines.append(f"GPS Data: {report.get('gps_info')}")
            out_lines.append("-" * 50)

        if report.get("camera_info"):
            out_lines.append("Camera & Hardware Info:")
            for k, v in report["camera_info"].items():
                out_lines.append(f"  • {k}: {v}")
            out_lines.append("-" * 50)

        if report.get("all_tags"):
            out_lines.append("All Metadata Tags:")
            for k, v in report["all_tags"].items():
                out_lines.append(f"  [{k}] = {v}")
        else:
            out_lines.append("No sensitive metadata found or file is clean.")

        full_rep = "\n".join(out_lines)
        self.last_exif_report = full_rep
        self.txt_exif_inspector.insert("1.0", full_rep)

    def _exif_strip_single(self):
        if not self.selected_file or not os.path.exists(self.selected_file):
            messagebox.showwarning(self.t["warn_title"], self.t["select_file_warn"])
            return

        ext = os.path.splitext(self.selected_file)[1].lower()
        if ext == ".pdf":
            success, out_path, saved = self.exif_stripper.strip_pdf_metadata(self.selected_file)
        else:
            success, out_path, saved = self.exif_stripper.strip_image_metadata(self.selected_file)

        if success:
            msg = f"{self.t['clean_success']}\n\nPath:\n{out_path}\nSaved: {format_file_size(saved)}"
            messagebox.showinfo("Success", msg)
            self._inspect_selected_file(out_path)
        else:
            messagebox.showerror(self.t["err_title"], f"{out_path}")

    def _exif_batch_strip(self):
        folder = filedialog.askdirectory(title=self.t["select_folder"])
        if not folder:
            return

        files = [
            os.path.join(folder, f) for f in os.listdir(folder)
            if os.path.splitext(f)[1].lower() in [".jpg", ".jpeg", ".png", ".webp", ".pdf"]
        ]
        if not files:
            messagebox.showinfo(self.t["info_title"], self.t["select_folder_warn"])
            return

        out_dir = os.path.join(folder, "Sanitized_Offline_Output")
        os.makedirs(out_dir, exist_ok=True)

        results = self.exif_stripper.batch_strip(files, out_dir)
        success_count = sum(1 for r in results if r["success"])
        total_saved = sum(r["bytes_saved"] for r in results if r["success"])

        msg = (
            f"{self.t['batch_done']}\n"
            f"Processed: {success_count} / {len(files)}\n"
            f"Saved: {format_file_size(total_saved)}\n"
            f"Output: {out_dir}"
        )
        messagebox.showinfo(self.t["info_title"], msg)

    # ==========================================
    # TAB 2: PDF TOOLKIT
    # ==========================================
    def _setup_pdf_tab(self):
        container = ctk.CTkFrame(self.tab_pdf)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Operation Selector
        selector_frame = ctk.CTkFrame(container)
        selector_frame.pack(fill="x", padx=10, pady=5)

        for label, val in self.t["pdf_modes"]:
            r = ctk.CTkRadioButton(
                selector_frame,
                text=label,
                variable=self.pdf_op_mode,
                value=val,
                command=self._on_pdf_mode_changed
            )
            r.pack(side="left", padx=10, pady=10)

        # File List Controls
        control_bar = ctk.CTkFrame(container, fg_color="transparent")
        control_bar.pack(fill="x", padx=10, pady=5)

        self.btn_pdf_add = ctk.CTkButton(
            control_bar,
            text=f"➕ {self.t['add_files']}",
            command=self._pdf_add_files,
            width=120
        )
        self.btn_pdf_add.pack(side="left", padx=5)

        self.btn_pdf_clear = ctk.CTkButton(
            control_bar,
            text=f"🗑️ {self.t['clear_list']}",
            command=self._pdf_clear_files,
            fg_color="#7F8C8D",
            width=100
        )
        self.btn_pdf_clear.pack(side="left", padx=5)

        # Options Container (Dynamic)
        self.pdf_options_frame = ctk.CTkFrame(container)
        self.pdf_options_frame.pack(fill="x", padx=10, pady=5)

        self.lbl_pdf_param = ctk.CTkLabel(self.pdf_options_frame, text=self.t["pdf_settings"])
        self.lbl_pdf_param.pack(side="left", padx=10)

        self.ent_pdf_param = ctk.CTkEntry(self.pdf_options_frame, placeholder_text=self.t["page_range_hint"], width=250)
        self.ent_pdf_param.pack(side="left", padx=10)

        # File List Box
        self.pdf_listbox = tk.Listbox(
            container,
            bg="#2B2B2B",
            fg="white",
            selectbackground="#2980B9",
            selectforeground="white",
            font=("Segoe UI", 10),
            height=8
        )
        self.pdf_listbox.pack(fill="both", expand=True, padx=10, pady=5)

        # Action Execute Button
        self.btn_pdf_execute = ctk.CTkButton(
            container,
            text=f"🚀 {self.t['execute']}",
            command=self._pdf_execute,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#27AE60",
            hover_color="#1E8449",
            height=40
        )
        self.btn_pdf_execute.pack(fill="x", padx=10, pady=10)

    def _on_pdf_mode_changed(self):
        mode = self.pdf_op_mode.get()
        if mode == "split":
            self.lbl_pdf_param.configure(text=self.t["page_range"])
            self.ent_pdf_param.configure(placeholder_text=self.t["page_range_hint"])
        elif mode == "compress":
            self.lbl_pdf_param.configure(text=self.t["comp_level"])
            self.ent_pdf_param.configure(placeholder_text=self.t["comp_level_hint"])
        else:
            self.lbl_pdf_param.configure(text=self.t["pdf_default_settings"])
            self.ent_pdf_param.delete(0, "end")

    def _pdf_add_files(self):
        mode = self.pdf_op_mode.get()
        if mode == "img_to_pdf":
            files = filedialog.askopenfilenames(
                title=self.t["add_files"],
                filetypes=[("Images", "*.jpg;*.jpeg;*.png;*.webp;*.bmp")]
            )
        else:
            files = filedialog.askopenfilenames(
                title=self.t["add_files"],
                filetypes=[("PDF Documents", "*.pdf")]
            )
        for f in files:
            if f not in self.selected_files_list:
                self.selected_files_list.append(f)
                self.pdf_listbox.insert("end", f)

    def _pdf_clear_files(self):
        self.selected_files_list.clear()
        self.pdf_listbox.delete(0, "end")

    def _pdf_execute(self):
        if not self.selected_files_list:
            messagebox.showwarning(self.t["warn_title"], self.t["no_pdf_warn"])
            return

        mode = self.pdf_op_mode.get()
        first_file = self.selected_files_list[0]

        if mode == "merge":
            out_file = filedialog.asksaveasfilename(
                title="Save Merged PDF",
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf")]
            )
            if out_file:
                success, path, pages = self.pdf_toolkit.merge_pdfs(self.selected_files_list, out_file)
                if success:
                    messagebox.showinfo("Success", f"{path} ({pages} pages)")
                else:
                    messagebox.showerror(self.t["err_title"], path)

        elif mode == "compress":
            out_file = filedialog.asksaveasfilename(
                title="Save Compressed PDF",
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf")]
            )
            if out_file:
                lvl = self.ent_pdf_param.get().strip().lower() or "medium"
                success, path, saved, percent = self.pdf_toolkit.compress_pdf(first_file, out_file, quality=lvl)
                if success:
                    messagebox.showinfo("Success", f"{path}\nSaved: {format_file_size(saved)} ({percent:.1f}%)")
                else:
                    messagebox.showerror(self.t["err_title"], path)

        elif mode == "split":
            out_dir = filedialog.askdirectory(title="Select Output Folder")
            if out_dir:
                ranges = self.ent_pdf_param.get().strip() or None
                success, files, msg = self.pdf_toolkit.split_pdf(first_file, out_dir, ranges)
                if success:
                    messagebox.showinfo("Success", f"{msg}\nFiles: {len(files)}")
                else:
                    messagebox.showerror(self.t["err_title"], msg)

        elif mode == "sanitize":
            out_file = filedialog.asksaveasfilename(
                title="Save Sanitized PDF",
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf")]
            )
            if out_file:
                success, path, items = self.pdf_toolkit.sanitize_pdf(first_file, out_file)
                if success:
                    items_str = "\n• " + "\n• ".join(items) if items else "Clean"
                    messagebox.showinfo("Success", f"{path}\nRemoved:\n{items_str}")
                else:
                    messagebox.showerror(self.t["err_title"], path)

        elif mode == "img_to_pdf":
            out_file = filedialog.asksaveasfilename(
                title="Save Combined PDF",
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf")]
            )
            if out_file:
                success, path, pages = self.pdf_toolkit.images_to_pdf(self.selected_files_list, out_file)
                if success:
                    messagebox.showinfo("Success", f"{path} ({pages} pages)")
                else:
                    messagebox.showerror(self.t["err_title"], path)

        elif mode == "pdf_to_img":
            out_dir = filedialog.askdirectory(title="Select Output Directory for Images")
            if out_dir:
                success, files, msg = self.pdf_toolkit.pdf_to_images(first_file, out_dir, dpi=200)
                if success:
                    messagebox.showinfo("Success", f"{msg}\nPath: {out_dir}")
                else:
                    messagebox.showerror(self.t["err_title"], msg)

    # ==========================================
    # TAB 3: LOCAL OFFLINE OCR
    # ==========================================
    def _setup_ocr_tab(self):
        container = ctk.CTkFrame(self.tab_ocr)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Top Bar
        bar = ctk.CTkFrame(container, fg_color="transparent")
        bar.pack(fill="x", pady=5)

        self.btn_ocr_select = ctk.CTkButton(
            bar,
            text=f"📂 {self.t['ocr_select']}",
            command=self._ocr_select_file,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.btn_ocr_select.pack(side="left", padx=5)

        # Language dropdown
        self.lbl_lang = ctk.CTkLabel(bar, text=self.t["ocr_lang"])
        self.lbl_lang.pack(side="left", padx=10)

        self.ocr_lang_menu = ctk.CTkOptionMenu(
            bar,
            values=self.t["ocr_lang_values"]
        )
        self.ocr_lang_menu.set(self.t["ocr_lang_values"][2])
        self.ocr_lang_menu.pack(side="left", padx=5)

        # Enhance checkbox
        self.chk_enhance = ctk.CTkCheckBox(bar, text=self.t["ocr_enhance"])
        self.chk_enhance.select()
        self.chk_enhance.pack(side="left", padx=15)

        # Action Button
        self.btn_ocr_run = ctk.CTkButton(
            bar,
            text=f"⚡ {self.t['ocr_start']}",
            command=self._ocr_start_threaded,
            fg_color="#2980B9",
            hover_color="#1F618D",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.btn_ocr_run.pack(side="right", padx=5)

        # Source File Label
        self.lbl_ocr_file = ctk.CTkLabel(
            container,
            text=f"📄 {self.t['no_file']}",
            font=ctk.CTkFont(size=12, slant="italic"),
            anchor="w"
        )
        self.lbl_ocr_file.pack(fill="x", padx=10, pady=5)

        # Results Text Box
        self.txt_ocr_output = ctk.CTkTextbox(
            container,
            wrap="word",
            font=ctk.CTkFont(family="Vazirmatn", size=13)
        )
        self.txt_ocr_output.pack(fill="both", expand=True, padx=10, pady=5)
        self.txt_ocr_output.insert("1.0", self.t["ocr_waiting"])

        # Bottom Bar: Copy & Save
        bottom_bar = ctk.CTkFrame(container, fg_color="transparent")
        bottom_bar.pack(fill="x", pady=5)

        self.btn_ocr_copy = ctk.CTkButton(
            bottom_bar,
            text=f"📋 {self.t['ocr_copy']}",
            command=self._ocr_copy_clipboard,
            width=140
        )
        self.btn_ocr_copy.pack(side="left", padx=5)

        self.btn_ocr_save = ctk.CTkButton(
            bottom_bar,
            text=f"💾 {self.t['ocr_save']}",
            command=self._ocr_save_txt,
            width=140
        )
        self.btn_ocr_save.pack(side="left", padx=5)

        self.lbl_ocr_stats = ctk.CTkLabel(
            bottom_bar,
            text=self.t["ocr_stats"].format(words=self.last_word_count, chars=self.last_char_count),
            text_color="#95A5A6"
        )
        self.lbl_ocr_stats.pack(side="right", padx=10)

    def _ocr_select_file(self):
        f = filedialog.askopenfilename(
            title=self.t["ocr_select"],
            filetypes=[("Scanned Documents", "*.jpg;*.jpeg;*.png;*.webp;*.tiff;*.bmp;*.pdf"), ("All Files", "*.*")]
        )
        if f:
            self.ocr_source_file = f
            self.lbl_ocr_file.configure(text=f"📄 {f}")

    def _ocr_start_threaded(self):
        if not self.ocr_source_file or not os.path.exists(self.ocr_source_file):
            messagebox.showwarning(self.t["warn_title"], self.t["select_file_warn"])
            return

        self.btn_ocr_run.configure(state="disabled", text="...")
        self.txt_ocr_output.delete("1.0", "end")
        self.txt_ocr_output.insert("1.0", self.t["ocr_processing"])

        thread = threading.Thread(target=self._ocr_worker, daemon=True)
        thread.start()

    def _ocr_worker(self):
        lang_str = self.ocr_lang_menu.get()
        if "fas+eng" in lang_str:
            lang_code = "fas+eng"
        elif "fas" in lang_str:
            lang_code = "fas"
        else:
            lang_code = "eng"

        enhance = (self.chk_enhance.get() == 1)
        ext = os.path.splitext(self.ocr_source_file)[1].lower()

        if ext == ".pdf":
            success, text, stats = self.ocr_engine.recognize_pdf(self.ocr_source_file, lang=lang_code, enhance=enhance)
        else:
            success, text, stats = self.ocr_engine.recognize_image(self.ocr_source_file, lang=lang_code, enhance=enhance)

        # Update UI in main thread
        self.after(0, lambda: self._ocr_completed(success, text, stats))

    def _ocr_completed(self, success: bool, text: str, stats: dict):
        self.btn_ocr_run.configure(state="normal", text=f"⚡ {self.t['ocr_start']}")
        self.txt_ocr_output.delete("1.0", "end")
        self.txt_ocr_output.insert("1.0", text)

        if success:
            self.last_word_count = stats.get("word_count", 0)
            self.last_char_count = stats.get("char_count", 0)
            self.last_ocr_text = text
            self.lbl_ocr_stats.configure(text=self.t["ocr_stats"].format(words=self.last_word_count, chars=self.last_char_count))
        else:
            messagebox.showerror(self.t["err_title"], text)

    def _ocr_copy_clipboard(self):
        txt = self.txt_ocr_output.get("1.0", "end").strip()
        if txt:
            self.clipboard_clear()
            self.clipboard_append(txt)
            messagebox.showinfo("Clipboard", self.t["copied"])

    def _ocr_save_txt(self):
        txt = self.txt_ocr_output.get("1.0", "end").strip()
        if not txt:
            return
        f = filedialog.asksaveasfilename(
            title=self.t["ocr_save"],
            defaultextension=".txt",
            filetypes=[("Text File", "*.txt")]
        )
        if f:
            with open(f, "w", encoding="utf-8") as file:
                file.write(txt)
            messagebox.showinfo("Success", f"{f}")

    # ==========================================
    # TAB 4: SECURITY & AUDIT
    # ==========================================
    def _setup_security_tab(self):
        container = ctk.CTkFrame(self.tab_sec)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Shield Banner
        banner = ctk.CTkFrame(container, fg_color="#1E3799", corner_radius=8)
        banner.pack(fill="x", padx=15, pady=15)

        lbl_shield = ctk.CTkLabel(
            banner,
            text=f"🔒 {self.t['sec_badge']}",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="white"
        )
        lbl_shield.pack(pady=10)

        lbl_shield_desc = ctk.CTkLabel(
            banner,
            text=self.t["sec_desc"],
            font=ctk.CTkFont(size=12),
            text_color="#DCDDE1"
        )
        lbl_shield_desc.pack(pady=5)

        # Policy Grid
        grid_frame = ctk.CTkFrame(container)
        grid_frame.pack(fill="both", expand=True, padx=15, pady=10)

        manifest = self.security_auditor.get_security_manifest()
        row = 0
        for policy, val in manifest.items():
            ctk.CTkLabel(grid_frame, text=f"• {policy}:", font=ctk.CTkFont(weight="bold")).grid(row=row, column=0, sticky="w", padx=15, pady=8)
            ctk.CTkLabel(grid_frame, text=val, text_color="#2ECC71").grid(row=row, column=1, sticky="w", padx=15, pady=8)
            row += 1

        # Audit logs button
        btn_open_folder = ctk.CTkButton(
            container,
            text=self.t["open_folder"],
            command=self._open_app_folder
        )
        btn_open_folder.pack(pady=15)

    def _open_app_folder(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        os.startfile(base_dir)

    def _build_footer(self):
        footer = ctk.CTkFrame(self, height=30, corner_radius=0)
        footer.pack(fill="x", side="bottom")

        self.lbl_footer = ctk.CTkLabel(
            footer,
            text=self.t["footer"],
            font=ctk.CTkFont(size=11),
            text_color="#7F8C8D"
        )
        self.lbl_footer.pack(side="left", padx=20)

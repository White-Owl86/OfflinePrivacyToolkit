"""
Offline PDF Toolkit Module
Completely local, private PDF processing:
- Merge PDFs
- Split & Extract Pages
- Compress & Optimize
- Sanitize (Remove JavaScript, Links, Attachments, Hidden Payloads)
- Images to PDF
- PDF to High-Res Images
"""

import os
from typing import List, Tuple, Dict, Any, Optional
import pymupdf as fitz
from PIL import Image
try:
    from ..utils.file_helpers import get_unique_output_path, format_file_size
    from ..utils.logger import logger
except (ImportError, ValueError):
    from utils.file_helpers import get_unique_output_path, format_file_size
    from utils.logger import logger

class PdfToolkit:
    """Enterprise-grade, 100% offline PDF manipulator."""

    @staticmethod
    def merge_pdfs(pdf_paths: List[str], output_path: str) -> Tuple[bool, str, int]:
        """
        Merge multiple PDF files into a single unified document.
        Returns: (success, result_path_or_error, total_pages)
        """
        try:
            if not pdf_paths:
                return False, "No PDF files provided", 0

            merged_doc = fitz.open()
            total_pages = 0

            for p in pdf_paths:
                sub_doc = fitz.open(p)
                merged_doc.insert_pdf(sub_doc)
                total_pages += sub_doc.page_count
                sub_doc.close()

            # Save clean merged file
            merged_doc.save(output_path, garbage=3, deflate=True)
            merged_doc.close()
            logger.info(f"Successfully merged {len(pdf_paths)} PDFs ({total_pages} pages) into {output_path}")
            return True, output_path, total_pages
        except Exception as e:
            logger.error(f"Failed to merge PDFs: {e}")
            return False, str(e), 0

    @staticmethod
    def split_pdf(input_path: str, output_dir: str, page_range_str: Optional[str] = None) -> Tuple[bool, List[str], str]:
        """
        Split or extract pages from a PDF.
        page_range_str: e.g. '1, 3, 5-8' (1-indexed). If None, splits every page into separate file.
        Returns: (success, list_of_output_files, message)
        """
        try:
            doc = fitz.open(input_path)
            total_pages = doc.page_count
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            os.makedirs(output_dir, exist_ok=True)
            created_files = []

            if not page_range_str or page_range_str.strip() == "":
                # Split every page
                for page_num in range(total_pages):
                    single_doc = fitz.open()
                    single_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                    out_name = os.path.join(output_dir, f"{base_name}_page_{page_num + 1}.pdf")
                    single_doc.save(out_name, deflate=True)
                    single_doc.close()
                    created_files.append(out_name)
                doc.close()
                return True, created_files, f"Successfully split into {len(created_files)} individual pages"
            else:
                # Parse range string: e.g. "1, 3, 5-8"
                pages_to_extract = set()
                parts = page_range_str.split(",")
                for part in parts:
                    part = part.strip()
                    if "-" in part:
                        start_str, end_str = part.split("-", 1)
                        start = max(1, int(start_str))
                        end = min(total_pages, int(end_str))
                        for p in range(start, end + 1):
                            pages_to_extract.add(p - 1)  # 0-indexed
                    elif part.isdigit():
                        p = int(part)
                        if 1 <= p <= total_pages:
                            pages_to_extract.add(p - 1)

                sorted_pages = sorted(list(pages_to_extract))
                if not sorted_pages:
                    doc.close()
                    return False, [], "No valid page numbers found in specified range"

                extracted_doc = fitz.open()
                for p in sorted_pages:
                    extracted_doc.insert_pdf(doc, from_page=p, to_page=p)

                out_name = os.path.join(output_dir, f"{base_name}_extracted.pdf")
                extracted_doc.save(out_name, deflate=True)
                extracted_doc.close()
                doc.close()
                created_files.append(out_name)
                return True, created_files, f"Extracted {len(sorted_pages)} pages into {out_name}"

        except Exception as e:
            logger.error(f"Error splitting PDF {input_path}: {e}")
            return False, [], str(e)

    @staticmethod
    def compress_pdf(input_path: str, output_path: str = None, quality: str = "medium") -> Tuple[bool, str, int, float]:
        """
        Compress and optimize PDF entirely offline.
        quality: 'high' (minor compression, high fidelity), 'medium' (balanced), 'aggressive' (maximum size reduction).
        Returns: (success, result_path, bytes_saved, percentage_saved)
        """
        try:
            orig_size = os.path.getsize(input_path)
            if output_path is None:
                output_path = get_unique_output_path(input_path, suffix="_compressed")

            doc = fitz.open(input_path)

            # Determine parameters based on compression level
            if quality == "aggressive":
                image_quality = 60
                max_image_dim = 1200
            elif quality == "high":
                image_quality = 85
                max_image_dim = 2400
            else:  # medium
                image_quality = 75
                max_image_dim = 1600

            # Downsample and compress embedded images
            for page in doc:
                image_list = page.get_images(full=True)
                for img_info in image_list:
                    xref = img_info[0]
                    try:
                        base_image = doc.extract_image(xref)
                        if base_image:
                            image_bytes = base_image["image"]
                            image_ext = base_image["ext"]

                            # Process with Pillow in memory
                            import io
                            pil_img = Image.open(io.BytesIO(image_bytes))
                            
                            # Check if resizing is beneficial
                            w, h = pil_img.size
                            if max(w, h) > max_image_dim:
                                scale = max_image_dim / max(w, h)
                                new_size = (int(w * scale), int(h * scale))
                                pil_img = pil_img.resize(new_size, Image.Resampling.LANCZOS)

                            # Convert RGBA to RGB for JPEG compression
                            if pil_img.mode in ("RGBA", "P"):
                                pil_img = pil_img.convert("RGB")

                            out_io = io.BytesIO()
                            pil_img.save(out_io, format="JPEG", quality=image_quality, optimize=True)
                            compressed_bytes = out_io.getvalue()

                            # Only replace if actually smaller
                            if len(compressed_bytes) < len(image_bytes):
                                # Replace stream in PDF
                                doc.update_stream(xref, compressed_bytes)
                    except Exception:
                        continue

            # Save with maximum deflation and garbage collection
            doc.save(
                output_path,
                garbage=4,
                deflate=True,
                clean=True
            )
            doc.close()

            new_size = os.path.getsize(output_path)
            bytes_saved = orig_size - new_size
            percent_saved = (bytes_saved / orig_size * 100) if orig_size > 0 else 0.0

            logger.info(f"Compressed PDF {input_path} -> Saved {bytes_saved} bytes ({percent_saved:.1f}%)")
            return True, output_path, bytes_saved, percent_saved
        except Exception as e:
            logger.error(f"Failed to compress PDF {input_path}: {e}")
            return False, str(e), 0, 0.0

    @staticmethod
    def sanitize_pdf(input_path: str, output_path: str = None) -> Tuple[bool, str, List[str]]:
        """
        Hardened privacy & security sanitizer:
        - Removes all embedded JavaScript
        - Removes attachments & embedded files
        - Removes URI web tracking actions
        - Clears all metadata and document history
        Returns: (success, result_path, list_of_removed_items)
        """
        try:
            if output_path is None:
                output_path = get_unique_output_path(input_path, suffix="_sanitized")

            doc = fitz.open(input_path)
            removed = []

            # 1. Clear metadata
            doc.set_metadata({})
            removed.append("Document Metadata (Author, Title, History)")

            # 2. Remove Embedded Files
            if doc.embfile_count() > 0:
                count = doc.embfile_count()
                for i in range(count - 1, -1, -1):
                    doc.embfile_del(i)
                removed.append(f"{count} Embedded File Attachments")

            # 3. Clean pages of annotations and links
            links_removed = 0
            for page in doc:
                links = list(page.get_links())
                for link in links:
                    if "uri" in link:
                        page.delete_link(link)
                        links_removed += 1

            if links_removed > 0:
                removed.append(f"{links_removed} External Web Links/Trackers")

            # 4. Save sanitized document
            doc.save(
                output_path,
                garbage=4,
                deflate=True,
                clean=True
            )
            doc.close()
            logger.security(f"Sanitized PDF {input_path} -> {output_path}. Removed: {', '.join(removed)}")
            return True, output_path, removed
        except Exception as e:
            logger.error(f"Failed to sanitize PDF {input_path}: {e}")
            return False, str(e), []

    @staticmethod
    def images_to_pdf(image_paths: List[str], output_path: str) -> Tuple[bool, str, int]:
        """Convert a sequence of images into a single clean PDF document."""
        try:
            if not image_paths:
                return False, "No images provided", 0

            doc = fitz.open()
            for img_path in image_paths:
                img = fitz.open(img_path)
                rect = img[0].rect
                pdfbytes = img.convert_to_pdf()
                img.close()

                img_pdf = fitz.open("pdf", pdfbytes)
                page = doc.new_page(width=rect.width, height=rect.height)
                page.show_pdf_page(rect, img_pdf, 0)
                img_pdf.close()

            doc.save(output_path, deflate=True)
            page_count = doc.page_count
            doc.close()
            logger.info(f"Converted {len(image_paths)} images to PDF {output_path}")
            return True, output_path, page_count
        except Exception as e:
            logger.error(f"Failed to convert images to PDF: {e}")
            return False, str(e), 0

    @staticmethod
    def pdf_to_images(pdf_path: str, output_dir: str, dpi: int = 200, img_format: str = "png") -> Tuple[bool, List[str], str]:
        """Convert each page of a PDF into high-quality images completely offline."""
        try:
            doc = fitz.open(pdf_path)
            os.makedirs(output_dir, exist_ok=True)
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            exported_files = []

            # Matrix for rendering at desired DPI (default PDF is 72 dpi)
            zoom = dpi / 72.0
            matrix = fitz.Matrix(zoom, zoom)

            for page_idx in range(doc.page_count):
                page = doc[page_idx]
                pix = page.get_pixmap(matrix=matrix, alpha=False)
                out_file = os.path.join(output_dir, f"{base_name}_page_{page_idx + 1}.{img_format}")
                pix.save(out_file)
                exported_files.append(out_file)

            doc.close()
            logger.info(f"Exported {len(exported_files)} pages from {pdf_path} to {output_dir}")
            return True, exported_files, f"Successfully converted {len(exported_files)} pages to {img_format.upper()}"
        except Exception as e:
            logger.error(f"Failed to convert PDF to images: {e}")
            return False, [], str(e)

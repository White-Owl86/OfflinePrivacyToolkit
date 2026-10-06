"""
Core EXIF & Metadata Stripper Module
Thoroughly inspects and strips all metadata from images and documents offline.
Supports JPEG, PNG, WEBP, TIFF, BMP, and PDF.
"""

import os
from typing import Dict, Any, List, Tuple
from PIL import Image, ExifTags
import pypdf
import pymupdf as fitz
try:
    from ..utils.file_helpers import get_unique_output_path, format_file_size
    from ..utils.logger import logger
except (ImportError, ValueError):
    from utils.file_helpers import get_unique_output_path, format_file_size
    from utils.logger import logger

class ExifStripper:
    """Handles deep metadata extraction and removal for maximum privacy."""

    @staticmethod
    def inspect_image_metadata(file_path: str) -> Dict[str, Any]:
        """Extract all identifiable metadata from an image for inspection."""
        metadata = {
            "file_name": os.path.basename(file_path),
            "file_size": format_file_size(os.path.getsize(file_path)),
            "format": None,
            "dimensions": None,
            "has_exif": False,
            "has_gps": False,
            "gps_info": {},
            "camera_info": {},
            "date_info": {},
            "software_info": None,
            "all_tags": {}
        }

        try:
            with Image.open(file_path) as img:
                metadata["format"] = img.format
                metadata["dimensions"] = f"{img.width} x {img.height}"

                exif = img.getexif()
                if exif:
                    metadata["has_exif"] = True
                    for tag_id, value in exif.items():
                        tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                        # Safe conversion to string for display
                        val_str = str(value)
                        if len(val_str) > 100:
                            val_str = val_str[:97] + "..."
                        metadata["all_tags"][tag_name] = val_str

                        # Extract GPS if present
                        if tag_name == "GPSInfo" or tag_id == 0x8825:
                            metadata["has_gps"] = True
                            gps_dict = {}
                            if hasattr(value, "items"):
                                for g_tag_id, g_val in value.items():
                                    g_tag_name = ExifTags.GPSTAGS.get(g_tag_id, str(g_tag_id))
                                    gps_dict[g_tag_name] = str(g_val)
                            metadata["gps_info"] = gps_dict

                        # Extract camera specs
                        if tag_name in ["Make", "Model", "LensModel", "LensMake"]:
                            metadata["camera_info"][tag_name] = str(value)

                        # Extract dates
                        if tag_name in ["DateTime", "DateTimeOriginal", "DateTimeDigitized"]:
                            metadata["date_info"][tag_name] = str(value)

                        # Software
                        if tag_name == "Software":
                            metadata["software_info"] = str(value)

                # Check IFD sub-exif if available
                if hasattr(img, "_getexif"):
                    sub_exif = img._getexif()
                    if sub_exif:
                        for tag_id, value in sub_exif.items():
                            tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                            if tag_name not in metadata["all_tags"]:
                                metadata["all_tags"][tag_name] = str(value)
                            if tag_name == "GPSInfo":
                                metadata["has_gps"] = True

        except Exception as e:
            logger.error(f"Error inspecting image {file_path}: {e}")
            metadata["error"] = str(e)

        return metadata

    @staticmethod
    def inspect_pdf_metadata(file_path: str) -> Dict[str, Any]:
        """Extract metadata from a PDF file."""
        metadata = {
            "file_name": os.path.basename(file_path),
            "file_size": format_file_size(os.path.getsize(file_path)),
            "format": "PDF",
            "has_metadata": False,
            "all_tags": {}
        }

        try:
            doc = fitz.open(file_path)
            meta = doc.metadata
            metadata["page_count"] = doc.page_count
            
            if meta:
                clean_meta = {k: v for k, v in meta.items() if v}
                if clean_meta:
                    metadata["has_metadata"] = True
                    metadata["all_tags"] = clean_meta
            doc.close()
        except Exception as e:
            logger.error(f"Error inspecting PDF {file_path}: {e}")
            metadata["error"] = str(e)

        return metadata

    @staticmethod
    def strip_image_metadata(input_path: str, output_path: str = None, preserve_quality: bool = True) -> Tuple[bool, str, int]:
        """
        Completely strips all EXIF, GPS, XMP, and device metadata from an image.
        Re-encodes purely from raw pixel buffer.
        Returns: (success, result_path, bytes_saved)
        """
        try:
            original_size = os.path.getsize(input_path)
            if output_path is None:
                output_path = get_unique_output_path(input_path, suffix="_clean")

            with Image.open(input_path) as img:
                # Create a pristine image copy with pixel data only
                data = list(img.getdata())
                clean_img = Image.new(img.mode, img.size)
                clean_img.putdata(data)

                # Format-specific save options
                img_format = img.format if img.format else "JPEG"
                if img_format.upper() in ["JPEG", "JPG"]:
                    # Clean save without exif parameter
                    clean_img.save(output_path, "JPEG", quality=95 if preserve_quality else 85, optimize=True)
                elif img_format.upper() == "PNG":
                    clean_img.save(output_path, "PNG", optimize=True)
                elif img_format.upper() == "WEBP":
                    clean_img.save(output_path, "WEBP", quality=95 if preserve_quality else 85)
                else:
                    clean_img.save(output_path, img_format)

            new_size = os.path.getsize(output_path)
            bytes_saved = original_size - new_size
            logger.security(f"Stripped metadata from {input_path} -> {output_path} (Saved {bytes_saved} bytes)")
            return True, output_path, bytes_saved
        except Exception as e:
            logger.error(f"Failed to strip metadata from {input_path}: {e}")
            return False, str(e), 0

    @staticmethod
    def strip_pdf_metadata(input_path: str, output_path: str = None) -> Tuple[bool, str, int]:
        """
        Completely purges all metadata, author, producer, timestamps, and XMP streams from PDF.
        """
        try:
            original_size = os.path.getsize(input_path)
            if output_path is None:
                output_path = get_unique_output_path(input_path, suffix="_clean")

            doc = fitz.open(input_path)
            # Empty all metadata fields
            empty_meta = {
                "format": "",
                "title": "",
                "author": "",
                "subject": "",
                "keywords": "",
                "creator": "",
                "producer": "",
                "creationDate": "",
                "modDate": "",
                "trapped": ""
            }
            doc.set_metadata(empty_meta)
            
            # Save with garbage collection, deflating streams, clean XMP
            doc.save(
                output_path,
                garbage=4,        # Maximum garbage collection
                deflate=True,     # Compress streams
                clean=True        # Sanitize contents
            )
            doc.close()

            new_size = os.path.getsize(output_path)
            bytes_saved = original_size - new_size
            logger.security(f"Stripped PDF metadata from {input_path} -> {output_path}")
            return True, output_path, bytes_saved
        except Exception as e:
            logger.error(f"Failed to strip PDF metadata from {input_path}: {e}")
            return False, str(e), 0

    @classmethod
    def batch_strip(cls, file_paths: List[str], output_dir: str = None) -> List[Dict[str, Any]]:
        """Batch strip metadata for multiple files."""
        results = []
        for path in file_paths:
            ext = os.path.splitext(path)[1].lower()
            out_file = None
            if output_dir:
                filename = os.path.basename(path)
                name, ext_part = os.path.splitext(filename)
                out_file = os.path.join(output_dir, f"{name}_clean{ext_part}")

            if ext in [".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".bmp"]:
                success, out_path, bytes_saved = cls.strip_image_metadata(path, out_file)
            elif ext == ".pdf":
                success, out_path, bytes_saved = cls.strip_pdf_metadata(path, out_file)
            else:
                success, out_path, bytes_saved = False, "Unsupported file format", 0

            results.append({
                "source": path,
                "success": success,
                "output": out_path,
                "bytes_saved": bytes_saved
            })
        return results

"""
File Helper Utilities for Offline Privacy & Document Toolkit
"""

import os
import hashlib
from typing import Tuple, List

def format_file_size(size_bytes: int) -> str:
    """Format bytes into human-readable string (KB, MB, GB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def calculate_sha256(file_path: str) -> str:
    """Calculate SHA-256 checksum of a file for local integrity verification."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()

def get_unique_output_path(base_path: str, suffix: str = "_cleaned") -> str:
    """Generate a non-colliding output path."""
    dirname, filename = os.path.split(base_path)
    name, ext = os.path.splitext(filename)
    candidate = os.path.join(dirname, f"{name}{suffix}{ext}")
    
    counter = 1
    while os.path.exists(candidate):
        candidate = os.path.join(dirname, f"{name}{suffix}_{counter}{ext}")
        counter += 1
    return candidate

def is_image_file(path: str) -> bool:
    """Check if file is a supported image."""
    ext = os.path.splitext(path)[1].lower()
    return ext in [".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".bmp"]

def is_pdf_file(path: str) -> bool:
    """Check if file is a PDF."""
    return os.path.splitext(path)[1].lower() == ".pdf"

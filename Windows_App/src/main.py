"""
Offline Privacy & Document Toolkit - Main Entry Point
Zero Network Dependencies. 100% Local Execution.
"""

import sys
import os

# Ensure current package can be resolved
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from ui.app_window import MainWindow
from utils.logger import logger

def main():
    logger.security("Launching Offline Privacy & Document Toolkit (Air-Gapped Desktop Application)...")
    try:
        app = MainWindow()
        app.mainloop()
    except Exception as e:
        logger.error(f"Fatal crash in MainWindow: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

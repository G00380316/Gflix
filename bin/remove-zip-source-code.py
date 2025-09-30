# -*- coding: utf-8 -*-
"""
Cleanup script to remove existing zip files from Kodi addon source folders.

This prevents the repository generator from accidentally zipping up old 
.zip archives inside the new ones.
"""

import os

# --- CONFIGURATION ---
# Set this to the same path as your generator.py script
ADDONS_MAIN_PATH = 'C:/Users/Enoch/Documents/GitHub/Gflix/Kodi21'

# The name of the directory where the generator stores its final output zips.
# This folder will be ignored by the cleanup script.
OUTPUT_ZIP_FOLDER_NAME = 'zips'


def cleanup_source_zips():
    """
    Walks through the main path and deletes all .zip files found
    inside addon source folders, ignoring the dedicated output folder.
    """
    print(f"--- Starting cleanup in: {ADDONS_MAIN_PATH} ---")
    deleted_count = 0
    
    # os.walk generates the file tree: (current_dir, subdirs_in_current, files_in_current)
    for root, dirs, files in os.walk(ADDONS_MAIN_PATH):
        
        # 1. Skip the main output folder
        # We check if the root path ends with the name of the output folder.
        if os.path.basename(root).lower() == OUTPUT_ZIP_FOLDER_NAME.lower():
            print(f"[INFO] Skipping dedicated output folder: {root}")
            # Modify 'dirs' in place to stop os.walk from entering this directory
            dirs[:] = [] 
            continue
            
        # 2. Iterate through files and delete .zip archives
        for file_name in files:
            if file_name.lower().endswith('.zip'):
                zip_path = os.path.join(root, file_name)
                
                try:
                    os.remove(zip_path)
                    print(f"  Deleted: {zip_path}")
                    deleted_count += 1
                except Exception as e:
                    print(f"  [ERROR] Could not delete {zip_path}: {e}")

    print(f"\n--- Cleanup complete. {deleted_count} old zip files removed. ---")


if __name__ == "__main__":
    cleanup_source_zips()

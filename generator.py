# -*- coding: utf-8 -*-
"""
    Simple Kodi repository generator

    This script simplifies the process of creating a Kodi repository by
    automatically generating the addons.xml and addons.xml.md5 files.
"""

import os
import re
import sys
import hashlib
from zipfile import ZipFile, ZIP_DEFLATED
from mako.template import Template  # How install: python -m pip install mako

# --- GENERATOR CONFIGURATION ---
# > ADDONS_MAIN_PATH:
# This is the full path to the directory containing all your addon folders.
ADDONS_MAIN_PATH = 'C:/Users/Enoch/Documents/GitHub/Gflix/Kodi21'

# > Files and folders to be excluded per add-on
ZIP_EXCLUDED_FILES = {}
ZIP_EXCLUDED_DIRS = {}


def get_addons_folders():
    """Finds all valid addon folders in the main path."""
    addons_list = []
    # Loop through all items in the main directory
    for item in sorted(os.listdir(ADDONS_MAIN_PATH)):
        full_path = os.path.join(ADDONS_MAIN_PATH, item)
        # Check if the item is a directory
        if not os.path.isdir(full_path):
            continue

        # Check for addon.xml file inside the folder - this is the key check
        addon_xml_path = os.path.join(full_path, 'addon.xml')
        if os.path.exists(addon_xml_path):
            addons_list += [full_path]
            
    return addons_list


class Generator:
    """Handles generation of addon index and zip files."""
    def __init__(self):
        self.addons_xml_file = os.path.join(ADDONS_MAIN_PATH, 'addons.xml')
        self.addons_md5_file = os.path.join(ADDONS_MAIN_PATH, 'addons.xml.md5')

    def generate_addons_index(self):
        """Generates the main addons.xml file from each addon's addon.xml."""
        print("--- Generating addon index file ---")
        addons_xml_content = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n'
        addons_found = False

        for addon_path in get_addons_folders():
            addon_xml_path = os.path.join(addon_path, 'addon.xml')
            try:
                # IMPORTANT FIX: Use encoding='utf-8' to prevent 'charmap' errors
                with open(addon_xml_path, 'r', encoding='utf-8') as f:
                    # Read the XML content and add it to the main index file
                    addon_xml = f.read()
                    addons_xml_content += self._format_xml_lines(addon_xml.splitlines())
                    print(f"  Success: {os.path.basename(addon_path)}")
                    addons_found = True
            except Exception as exc:
                # If there's an error (like missing file or corrupted XML), we skip it
                print(f"  Excluding {os.path.basename(addon_path)}: Exception: {exc}")
                continue
        
        addons_xml_content += '</addons>\n'

        if not addons_found:
            print("  No valid addons with addon.xml files were detected.")
            return False

        self._save_file(addons_xml_content.encode('utf-8'), self.addons_xml_file)
        print("--- Finished generating addons.xml ---")
        return True

    def generate_md5_file(self):
        """Creates an md5 hash of the addons.xml file."""
        if not os.path.exists(self.addons_xml_file):
            print("Error: Cannot generate md5. addons.xml does not exist.")
            return

        # IMPORTANT FIX: Use encoding='utf-8' here too
        with open(self.addons_xml_file, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        md5_hash = hashlib.md5(file_content.encode('utf-8')).hexdigest()
        self._save_file(md5_hash.encode('utf-8'), self.addons_md5_file)
        print("--- Finished generating addons.xml.md5 ---")

    def generate_zip_files(self):
        """Creates a zip file for each addon found."""
        print("--- Generating addon zip files ---")
        for addon_path in get_addons_folders():
            addon_name = os.path.basename(addon_path)
            addon_xml_path = os.path.join(addon_path, 'addon.xml')
            
            try:
                # IMPORTANT FIX: Use encoding='utf-8' when reading the XML version
                with open(addon_xml_path, 'r', encoding='utf-8') as f:
                    addon_xml = f.read()
                addon_version = re.findall(r'version=\"(.*?[0-9])\"', addon_xml)[0]
                
                zip_filename = f"{addon_name}-{addon_version}.zip"
                # Save zips to a 'zips' subfolder for better organization
                zip_dir = os.path.join(ADDONS_MAIN_PATH, 'zips')
                os.makedirs(zip_dir, exist_ok=True)
                zip_path = os.path.join(zip_dir, zip_filename)

                with ZipFile(zip_path, 'w', ZIP_DEFLATED) as zip_obj:
                    # Exclude the zip file itself and hidden items
                    for folder_name, subfolders, filenames in os.walk(addon_path):
                        # Skip hidden folders and excluded folders
                        subfolders[:] = [d for d in subfolders if not d.startswith('.') and d not in ZIP_EXCLUDED_DIRS.get(addon_name, [])]
                        
                        for filename in filenames:
                            # Skip hidden files and excluded files
                            if filename.startswith('.') or filename in ZIP_EXCLUDED_FILES.get(addon_name, []):
                                continue
                            
                            absname = os.path.abspath(os.path.join(folder_name, filename))
                            # Create relative path for the zip archive
                            arcname = os.path.relpath(absname, os.path.join(ADDONS_MAIN_PATH, addon_name))
                            
                            zip_obj.write(absname, os.path.join(addon_name, arcname))
                            
                print(f"  Success: {zip_filename}")
            except Exception as exc:
                print(f"  Fail: Could not create zip for {addon_name} - Exception: {exc}")
                continue
        print("--- Finished zipping addons ---")
        

    def _format_xml_lines(self, xml_lines):
        """Format and clean the xml rows."""
        xml_formatted = ''
        for line in xml_lines:
            if line.find('<?xml') >= 0:
                continue
            xml_formatted += '  ' + line.rstrip() + '\n'
        return xml_formatted.rstrip() + '\n\n'

    def _save_file(self, data, file_path):
        """Write data to the specified file."""
        try:
            with open(file_path, "wb") as f:
                f.write(data)
        except Exception as exc:
            print(f"An error occurred saving {file_path}:\n{exc}")


if __name__ == "__main__":
    generator = Generator()
    
    # Run the generation process
    if generator.generate_addons_index():
        generator.generate_md5_file()
        generator.generate_zip_files()

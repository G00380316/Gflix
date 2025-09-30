import os
import re
import shutil

def remove_empty_folders(root_dir):
    """
    Recursively scans and removes empty subdirectories starting from the root_dir.
    It walks bottom-up to ensure parent folders that become empty are also removed.
    """
    print("\n--- Starting Empty Folder Cleanup ---")
    
    # We walk the directory tree from the bottom up (os.walk returns dirpath, dirnames, filenames)
    # The 'topdown=False' argument is crucial for removing empty directories.
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # We only check the current directory (dirpath)
        if not dirnames and not filenames:
            try:
                # Check again if it's truly empty (sometimes hidden files can mess this up)
                if not os.listdir(dirpath):
                    os.rmdir(dirpath)
                    print(f"Removed empty folder: {dirpath}")
            except OSError as e:
                # This catches errors like 'Directory not empty' or permission issues
                print(f"Error removing folder {dirpath}: {e}")
                
    print("--- Empty Folder Cleanup finished. ---")


def match_and_move_zips():
    """
    Scans the current directory for unzipped addon folders and matching zipped files.
    Moves the zipped file into its corresponding unzipped folder for cleanup.
    
    Example: Finds 'plugin.video.zoro-1.0.0.zip' and moves it into the 'plugin.video.zoro' folder.
    """
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Collect all addon folders (those without version numbers)
    addon_folders = {}
    for item in os.listdir(current_dir):
        item_path = os.path.join(current_dir, item)
        # Check if it's a directory and starts with a standard Kodi prefix (plugin, script, repository, etc.)
        if os.path.isdir(item_path) and item.startswith(('plugin.', 'script.', 'resource.', 'repository.', 'metadata.')):
            # The folder name is the core addon ID
            addon_folders[item] = item_path
            
    if not addon_folders:
        print("No unzipped addon folders found in the current directory. Nothing to match.")
        return

    print("--- Starting Zip File Matching and Moving ---")
    
    # 2. Scan for all zip files in the current directory
    for item in os.listdir(current_dir):
        if item.endswith('.zip'):
            # The pattern looks for the addon ID at the start of the zip file name
            # e.g., 'plugin.video.zoro-1.0.0.zip' -> group 1 is 'plugin.video.zoro'
            match = re.match(r'([a-zA-Z0-9\._]+)-\d+\.\d+\.\d+(?:\.\d+)?\.zip', item)

            if match:
                addon_id = match.group(1)
                zip_filename = item
                zip_path = os.path.join(current_dir, zip_filename)

                # 3. Check if we have a matching unzipped folder
                if addon_id in addon_folders:
                    target_folder_path = addon_folders[addon_id]
                    
                    # The goal is to move the zip *out* of the root, so we move it into the source folder.
                    target_zip_path = os.path.join(target_folder_path, zip_filename)

                    try:
                        shutil.move(zip_path, target_zip_path)
                        print(f"Moved: '{zip_filename}' -> '{addon_id}/'")
                    except Exception as e:
                        print(f"Error moving {zip_filename}: {e}")
                else:
                    print(f"No matching folder found for zip: {zip_filename}. Skipping move.")
            else:
                print(f"Skipping non-addon zip file: {item}")

    print("\n--- Matching and Moving finished. ---")
    
    # 4. Cleanup empty folders after moving zips
    remove_empty_folders(current_dir)


if __name__ == '__main__':
    match_and_move_zips()

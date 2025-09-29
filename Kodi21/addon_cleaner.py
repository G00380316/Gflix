import os
import shutil

# --- Configuration ---
# WARNING: LIST THE NAMES OF THE FOLDERS WHOSE *CONTENTS* YOU WANT TO PRESERVE.
# The script will automatically find all other subfolders and empty them.
EXCLUDED_FOLDERS = [
    ".git",             # Standard Git directory
    "__pycache__",      # Python cache directory
    # IMPORTANT: Add your unzipped addon source folders here if you want to keep their contents.
    # Add any other folders you want to skip cleaning (e.g., resources, docs)
]
# --- Configuration End ---

def cleanup_folders():
    """
    Automatically finds all subdirectories in the current path (excluding those listed in 
    EXCLUDED_FOLDERS) and deletes all files and subdirectories inside them, 
    leaving the target folders empty and intact.
    """
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Automatically exclude the script itself by name
    script_name = os.path.basename(__file__)
    exclude_list = set(EXCLUDED_FOLDERS + [script_name])
    
    print("--- Starting Automatic Folder Content Cleanup ---")
    
    # 1. Identify folders to clean
    folders_to_clean = []
    all_items = os.listdir(current_dir)
    
    for item in all_items:
        item_path = os.path.join(current_dir, item)
        # Check if it's a directory and not in the exclusion list
        if os.path.isdir(item_path) and item not in exclude_list:
            folders_to_clean.append(item)
    
    if not folders_to_clean:
        print("No folders found for cleaning (or all folders are in the exclusion list).")
        return

    # 2. Clean the contents of the identified folders
    for folder_name in folders_to_clean:
        folder_path = os.path.join(current_dir, folder_name)
            
        print(f"\nCleaning contents of folder: '{folder_name}'...")
        
        try:
            # Iterate over all files and subdirectories inside the target folder
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                
                if os.path.isfile(item_path):
                    # Delete file
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    # Delete subdirectory and all its contents recursively
                    shutil.rmtree(item_path)
            
            # Final verification
            if not os.listdir(folder_path):
                print(f"Successfully cleaned: '{folder_name}' is now empty.")
            else:
                print(f"Warning: Folder '{folder_name}' still contains items (possibly hidden or protected files).")

        except Exception as e:
            print(f"An error occurred while cleaning '{folder_name}': {e}")
            
    print("\n--- Cleanup process finished. ---")


if __name__ == '__main__':
    # WARNING: This action is destructive and permanent.
    cleanup_folders()

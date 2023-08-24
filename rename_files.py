import os
import sys

def rename_images_in_folder(folder_path):
    if not os.path.exists(folder_path):
        print(f"Folder path '{folder_path}' does not exist.")
        return
    
    file_list = os.listdir(folder_path)
    sorted_files = sorted(file_list)

    for index, filename in enumerate(sorted_files, start=1):
        old_path = os.path.join(folder_path, filename)
        new_filename = f"{index}.jpg"  # You can modify the extension as needed
        new_path = os.path.join(folder_path, new_filename)
        os.rename(old_path, new_path)
        print(f"Renamed {filename} to {new_filename}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python rename_files.py <folder_path>")
    else:
        folder_path = sys.argv[1]
        rename_images_in_folder(folder_path)


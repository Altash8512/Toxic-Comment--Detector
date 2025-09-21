import os
import shutil


def remove_dir_if_exists(path: str):
    """Removes a directory and its contents if it exists."""
    if os.path.isdir(path):
        print(f"  - Removing directory: {path}")
        try:
            shutil.rmtree(path)
        except OSError as e:
            print(f"    ❌ Error removing {path}: {e}")


def remove_file_if_exists(path: str):
    """Removes a file if it exists."""
    if os.path.isfile(path):
        print(f"  - Removing file: {path}")
        try:
            os.remove(path)
        except OSError as e:
            print(f"    ❌ Error removing {path}: {e}")


def main():
    """Main function to clean the project directory."""
    project_root = os.path.dirname(os.path.abspath(__file__))
    print(f"🧹 Starting cleanup in: {project_root}\n")

    # Directories to remove
    dirs_to_remove = ["__pycache__", ".pytest_cache", ".venv"]

    for root, dirs, files in os.walk(project_root, topdown=True):
        # Create a copy of dirs to iterate over, as we will be modifying the original list
        current_dirs = list(dirs)
        for dir_name in current_dirs:
            if dir_name in dirs_to_remove:
                remove_dir_if_exists(os.path.join(root, dir_name))
                # Prevent os.walk from traversing into the removed directory
                dirs.remove(dir_name)

    print("\n✅ Project cleanup complete.")

if __name__ == "__main__":
    main()
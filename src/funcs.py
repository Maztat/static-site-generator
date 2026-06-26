import os, shutil

from helper_funcs import *

def copy_paste_dir(from_path: str, dest_path: str) -> None:
    if os.path.exists(dest_path):
        shutil.rmtree(dest_path)
    os.makedirs(dest_path, exist_ok=True)
    copy_paste_subdir(from_path, dest_path)

def generate_pages_recursive(from_dir_path: str, template_path: str, dest_dir_path: str, basepath: str) -> None:
    if not os.path.exists(from_dir_path):
        raise Exception(f"ERROR: '{from_dir_path}' not found")
    if not os.path.exists(template_path):
        raise Exception(f"ERROR: '{template_path}' not found")
    for path in os.listdir(from_dir_path):
        full_from_path = os.path.join(from_dir_path, path)
        full_dest_path = os.path.join(dest_dir_path, path)
        if os.path.isfile(full_from_path):
            if not path.endswith(".md"):
                continue
            full_dest_path = f"{full_dest_path[:-3]}.html"
            generate_page(full_from_path, template_path, full_dest_path, basepath)
        elif os.path.isdir(full_from_path):
            generate_pages_recursive(full_from_path, template_path, full_dest_path, basepath)

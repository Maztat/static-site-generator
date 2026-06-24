import os, shutil

from helper_funcs import *

def copy_paste_dir(from_path: str, dest_path: str) -> None:
    if os.path.exists(dest_path):
        shutil.rmtree(dest_path)
    os.makedirs(dest_path, exist_ok=True)
    copy_paste_subdir(from_path, dest_path)

def generate_page(from_path: str, template_path: str, dest_path: str):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    if not os.path.exists(from_path):
        raise Exception(f"ERROR: '{from_path}' not found")
    if not os.path.exists(template_path):
        raise Exception(f"ERROR: '{template_path}' not found")
    dest_dir = os.path.dirname(dest_path)
    os.makedirs(dest_dir, exist_ok=True)
    with open(from_path) as f:
        source = f.read()
    with open(template_path) as f:
        template = f.read()
    source_html = markdown_to_html_node(source).to_html()
    title = extract_title(source)
    page = template
    page = page.replace("{{ Title }}", title)
    page = page.replace("{{ Content }}", source_html)
    with open(dest_path, "w") as f:
        f.write(page)

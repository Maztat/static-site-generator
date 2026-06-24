from funcs import copy_paste_dir, generate_page

def main():
    copy_paste_dir("static", "public")
    generate_page("content/index.md", "template.html", "public/index.html")

if __name__ == "__main__":
    main()

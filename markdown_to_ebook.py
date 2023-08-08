import os, subprocess, sys
from shlex import quote

MARKDOWN_DIR = "markdown"
EPUB_DIR = "epub"
MOBI_DIR = "mobi"

has_changed_files = subprocess.check_output(
    ["git", "ls-files", "-m", "-o", "--exclude-from=.gitignore"])
if not has_changed_files and not os.environ["GITHUB_EVENT_NAME"] == "push":
    print("No .md files have changed, nothing to do...")
else:
    if not os.path.exists(EPUB_DIR):
        os.mkdir(EPUB_DIR)
    if not os.path.exists(MOBI_DIR):
        os.mkdir(MOBI_DIR)
    for lang in os.listdir(MARKDOWN_DIR):
        epub_output_dir = os.path.join(EPUB_DIR, lang)
        if not os.path.exists(epub_output_dir):
            os.mkdir(epub_output_dir)
        mobi_output_dir = os.path.join(MOBI_DIR, lang)
        if not os.path.exists(mobi_output_dir):
            os.mkdir(mobi_output_dir)
        for work in os.listdir(os.path.join(MARKDOWN_DIR, lang)):
            print(f"*** Converting {work} with pandoc from .md to .epub & .mobi ***")
            epub_output_file = os.path.join(epub_output_dir, f"{work}.epub")
            mobi_output_file = os.path.join(mobi_output_dir, f"{work}.mobi")
            input_dir = os.path.join(MARKDOWN_DIR, lang, work)
            input_file = os.path.join(input_dir, f"{work}.md")
            cover_file = os.path.join(input_dir, "cover.png")
            if os.system(f"pandoc -o {quote(epub_output_file)} {quote(input_file)}"
                         " --fail-if-warnings --mathml"
                         f" --epub-cover-image={quote(cover_file)}"
                         f" --resource-path={quote(input_dir)}") != 0:
                sys.exit(1)
            if os.system(f"ebook-convert {quote(epub_output_file)} {quote(mobi_output_file)}") != 0:
                sys.exit(1)

import os, subprocess, sys
from shlex import quote

MARKDOWN_DIR = "markdown"
EPUB_DIR = "epub"

has_changed_files = subprocess.check_output(
    ["git", "ls-files", "-m", "-o", "--exclude-from=.gitignore"])
if not has_changed_files:
    print("No .md files have changed, nothing to do...")
else:
    if not os.path.exists(EPUB_DIR):
        os.mkdir(EPUB_DIR)
    for lang in os.listdir(MARKDOWN_DIR):
        output_dir = os.path.join(EPUB_DIR, lang)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        for work in os.listdir(os.path.join(MARKDOWN_DIR, lang)):
            print(f"*** Converting {work} with pandoc from .md to .epub ***")
            output_file = os.path.join(output_dir, f"{work}.epub")
            input_dir = os.path.join(MARKDOWN_DIR, lang, work)
            input_file = os.path.join(input_dir, f"{work}.md")
            if os.system(f"pandoc -o {quote(output_file)} {quote(input_file)}"
                         " --fail-if-warnings"
                         f" --resource-path={quote(input_dir)}") != 0:
                sys.exit(1)

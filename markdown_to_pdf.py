import os
import subprocess
import sys
from shlex import quote

MARKDOWN_DIR = "markdown"
PDF_DIR = "pdf"

has_changed_files = subprocess.check_output(
    ["git", "ls-files", "-m", "-o", "--exclude-from=.gitignore"])
if not has_changed_files:
    print("No .md files have changed, nothing to do...")
else:
    if not os.path.exists(PDF_DIR):
        os.mkdir(PDF_DIR)
    for lang in os.listdir(MARKDOWN_DIR):
        output_dir = os.path.join(PDF_DIR, lang)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        for work in os.listdir(os.path.join(MARKDOWN_DIR, lang)):
            if "Zettel" in work:
                continue
            print(f"*** Converting {work} with pandoc from .md to .pdf ***")
            output_file = os.path.join(output_dir, f"{work}.pdf")
            input_dir = os.path.join(MARKDOWN_DIR, lang, work)
            input_file = os.path.join(input_dir, f"{work}.md")
            if os.system(f"pandoc header-includes.yaml {quote(input_file)}"
                         f" --resource-path={quote(input_dir)}"
                         #" --fail-if-warnings"
                         " -V linkcolor:blue"
                         " -V geometry:a5paper"
                         " -V geometry:margin=2.7cm"
                         " --pdf-engine=xelatex"
                         f" -o {quote(output_file)}") != 0:
                sys.exit(1)

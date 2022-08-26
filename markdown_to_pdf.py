import os, subprocess, sys
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
            print(f"*** Converting {work} with pandoc from .md to .pdf ***")
            output_file = os.path.join(output_dir, f"{work}.pdf")
            input_dir = os.path.join(MARKDOWN_DIR, lang, work)
            input_file = os.path.join(input_dir, f"{work}.md")
            if lang == "english":
                html_lang = "en"
            elif lang == "german":
                html_lang = "de"
            else:
                raise Exception(f"Unknown language: '{lang}'")
            if os.system(f"pandoc {quote(input_file)}"
                         f" --resource-path={quote(input_dir)}"
                         #" --fail-if-warnings"
                         f" -V lang:{html_lang}"
                         " -V backgroundcolor:#fff"
                         " --template=template.html"
                         " --pdf-engine=weasyprint"
                         " --pdf-engine-opt=-s=pdf.css"
                         f" --pdf-engine-opt=--base-url={quote(input_dir)}"
                         f" -o {quote(output_file)}") != 0:
                sys.exit(1)

import os
import subprocess
import urllib.parse

MARKDOWN_DIR = "markdown"
EPUB_DIR = "epub"
MOBI_DIR = "mobi"
PDF_DIR = "pdf"

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Wittgenstein Ebooks</title>
    <link rel="stylesheet" href="index.css">
  </head>
  <body>{}</body>
</html>"""

has_changed_files = subprocess.check_output(
    ["git", "ls-files", "-m", "-o", "--exclude-from=.gitignore"])
if not has_changed_files and not os.environ["GITHUB_EVENT_NAME"] == "push":
    print("No .md files have changed, nothing to do...")
else:
    body = "<main>\n"
    body += "<a href=\"https://www.wittgensteinproject.org/\">"
    body += "<img class=\"logo\" width=\"260\" height=\"80\" src=\"LWP_logo_hi_text.png\" alt=\"Ludwig Wittgenstein Project Logo\">"
    body += "</a>"
    langs = [
        "german",
        "english",
        "italian",
        "spanish",
        "french",
        "danish",
        "greek",
        "portuguese",
        "romanian",
        "turkish",
    ]
    for lang in langs:
        epub_output_dir = os.path.join(EPUB_DIR, lang)
        mobi_output_dir = os.path.join(MOBI_DIR, lang)
        pdf_output_dir = os.path.join(PDF_DIR, lang)
        body += f"<h2>{lang.title()}</h2>\n"
        body += "<div class=\"lang\">\n"
        for work in sorted(os.listdir(os.path.join(MARKDOWN_DIR, lang))):
            body += "<div class=\"book\">"
            cover = os.path.join(MARKDOWN_DIR, lang, work, "cover.png")
            epub_file = os.path.join(EPUB_DIR, lang, f"{work}.epub")
            mobi_file = os.path.join(MOBI_DIR, lang, f"{work}.mobi")
            pdf_file = os.path.join(PDF_DIR, lang, f"{work}.pdf")
            body += f"<img src=\"{urllib.parse.quote(cover)}\" alt=\"{work} cover\">"
            body += "<div class=\"links\">"
            body += f"<a href=\"{urllib.parse.quote(epub_file)}\">.epub</a>"
            body += f"<a href=\"{urllib.parse.quote(mobi_file)}\">.mobi</a>"
            body += f"<a href=\"{urllib.parse.quote(pdf_file)}\">.pdf</a>"
            body += "</div>"
            body += "</div>\n"
        body += "</div>\n"
    body += "</main>\n"
    with open("index.html", "w") as f:
        f.write(HTML_PAGE.format(body))

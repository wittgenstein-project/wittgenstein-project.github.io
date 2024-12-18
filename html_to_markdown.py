from bs4 import BeautifulSoup, NavigableString
from io import BytesIO
from matplotlib import pyplot as plt
import hashlib
import os
import re
import requests
import sys
import time
import urllib.parse

SECONDS_BETWEEN_DOC_REQUESTS = 0.5
SECONDS_BETWEEN_IMG_REQUESTS = 0.1
BLACKLISTED_LANGS = ["Arabic"]
BLACKLISTED_WORKS = ["Wörterbuch", "Baumstruktur",
                     "tree-like", "arborescente", "albero", "árbol", "árvore"]

# Functions to convert html to (pandoc) markdown:


def parse_line(state, parsed, image_urls, elem, html_tag, md_tag, escape_whitespace=False):
    [errors, refs] = state
    line = [""]
    for child in elem.children:
        parse_html(state, line, image_urls, child)
    if len(line) == 1:
        if escape_whitespace:
            line = line[0].replace(" ", "\\ ")
        else:
            line = line[0].strip()
        parsed[-1] += f"{md_tag}{line}{md_tag}"
    else:
        errors.append(
            f"Expected single line inside <{html_tag}></{html_tag}>, found {line}")


def parse_html(state, parsed, image_urls, elem, escape_newlines=False):
    [errors, refs] = state
    newline = "\\" if escape_newlines else ""
    if isinstance(elem, NavigableString):
        escaped = elem.text.replace("\\", "\\\\").replace(
            "\n", " ").replace("~", "\\~").replace("|", "\\|")
        text = re.sub(r"\s+", " ", escaped)
        parsed[-1] += text
    else:
        if elem.get("style"):
            elem["style"] = elem["style"].replace(
                ":", ": ").replace("  ", " ").strip()

        if elem.name == "br":
            parsed.append(newline)
        elif elem.name == "a":
            title = elem.text
            href = elem["href"]
            parsed[-1] += f"[{title}]({href})"
        elif elem.name == "img":        ## TODO
            alt = elem["alt"]
            # if elem.get("class") == ["mwe-math-fallback-image-inline"]:
            #    parsed[-1] += f"${alt}$"
            # else:
            src = elem["src"]
            image_urls.append(src)
            file_name = os.path.basename(src)
            if "/svg/" in src and not src.endswith(".svg"):
                file_name += ".svg"
            elif "/thumb/" in src:
                file_name = file_name
            # add the non-breaking space "\ " to suppress the caption
            parsed[-1] += f"![{alt}](images/{file_name})\\ "
        
        elif elem.name == 'span' and elem.get('class') == ["smj-container"]:
            # deal with the latex when mathoid -> mathjax
            math_content = elem.get_text(strip=True) 
            if math_content.startswith("[math]") and math_content.endswith("[/math]"):
                math_content = math_content[6:-7].strip()
            
            # rename
            hash_object = hashlib.sha256(math_content.encode())
            file_name = f"{hash_object.hexdigest()}.svg"    # hash the content to get a unique file name
            image_urls.append(math_content)

            math_content = math_content.replace(r"\displaystyle", "")
            parsed[-1] += f"![{math_content}](images/{file_name})\\ "  
            

        elif elem.name == "span" and not elem.get("class") and elem.get("style") == "text-decoration-line: underline; text-decoration-style: dashed;":
            # wavy underline, will be treated as normal text here
            parsed[-1] += elem.text
        elif elem.name == "i" \
                or elem.name == "u" \
                or elem.name == "span" and not elem.get("class") and elem.get("style") == "letter-spacing: 0.2em; margin-right: -0.2em;" \
                or elem.name == "span" and not elem.get("class") and elem.get("style") == "font-variant: small-caps;":
            parse_line(state, parsed, image_urls, elem, "i", "*")
        elif elem.name == "b":
            parse_line(state, parsed, image_urls, elem, "b", "**")
        elif elem.name == "s":
            parse_line(state, parsed, image_urls, elem, "s", "~~")
        elif elem.name == "sub" and not elem.get("class"):
            # this is pandoc markdown syntax
            parse_line(state, parsed, image_urls, elem,
                       "sub", "~", escape_whitespace=True)
        elif elem.name == "sup" and not elem.get("class"):
            # this is pandoc markdown syntax
            parse_line(state, parsed, image_urls, elem,
                       "sup", "^", escape_whitespace=True)
        elif elem.name == "sup" and elem.get("class") == ["reference"] and elem.get("id"):
            ref_number = elem.get("id").replace("cite_ref-", "")
            parsed[-1] += f"[^{ref_number}]"
            refs.append(ref_number)
        elif elem.name == "div" and elem.get("class") and "mw-references-wrap" in elem.get("class"):
            for i, ref in enumerate(elem.find_all("span", "reference-text")):
                ref_number = i + 1
                if not str(ref_number) in refs:
                    continue
                parsed_ref = [f"[^{ref_number}]: "]
                for child in ref.children:
                    parse_html(state, parsed_ref, image_urls, child)
                for line in parsed_ref:
                    if line.lstrip().startswith(">"):
                        line = line.lstrip()[1:].lstrip()
                    if line.strip() == "":
                        parsed.append("\\")
                    else:
                        parsed.append(line)
                if parsed[-1] == "\\":
                    parsed[-1] = ""
                else:
                    parsed.append(newline)
        elif elem.name == "blockquote" and not elem.get("class"):
            parsed_children = [""]
            for child in elem.children:
                parse_html(state, parsed_children, image_urls, child)
            parsed.extend([f"> {child}" for child in parsed_children])
            parsed.append(newline)
        elif elem.name == "hr" and not elem.get("class"):
            parsed.extend(["", "---", "", ""])
        elif elem.name == "dl" and not elem.get("class"):
            for child in elem.children:
                parsed.extend(["", ""])
                parse_html(state, parsed, image_urls, child)
            parsed.extend(["", ""])
        elif elem.name == "dd" and not elem.get("class"):
            for child in elem.children:
                parse_html(state, parsed, image_urls, child)
        elif elem.name == "span" and elem.get("class") == ["tl-check"]:
            # does not seem to contain visible markup, so ignore
            pass
        elif elem.name == "span" and elem.get("class") and "mwe-math-mathml-inline" in elem.get("class"):
            # inline math, ignore for now, parent should also contain svg <img>
            pass
        elif elem.name == "span" and not elem.get("class") and elem.get("style") == "border-top: 1px solid; padding: 0 0.1em;":
            # used for extending a square root sign, so just process children normally
            for child in elem.children:
                parse_html(state, parsed, image_urls, child)
        elif elem.name == "span" and not elem.get("class") and not elem.get("style") \
                or elem.name == "span" and elem.get("class") == ["plainlinks"] \
                or elem.name == "span" and elem.get("class") == ["nowrap"] \
                or elem.name == "span" and elem.get("class") == ["mwe-math-element"] \
                or elem.name == "span" and elem.get("class") == ["mw-headline"] \
                or elem.name == "span" and elem.get("style") == "white-space: nowrap;":
            for child in elem.children:
                parse_html(state, parsed, image_urls, child)
        elif elem.name == "span" and elem.get("class") and elem.get("class")[0] == "tlp-aside-par":
            for child in elem.children:
                parse_html(state, parsed, image_urls, child)
        elif elem.name == "span" and elem.get("class") and elem.get("class")[0].endswith("-aside-par"):
            # page breaks within Nachlass source documents as margin notes
            pass
        elif elem.name == "span" and elem.get("style") and elem.get("style").startswith("text-decoration: overline"):
            parsed[-1] += "$\\overline{"
            for child in elem.children:
                parse_html(state, parsed, image_urls, child)
            parsed[-1] += "}$"
        elif elem.name == "ol":
            parsed.append(newline)
            counter = 1
            for child in elem.children:
                if child.name == "li":
                    if elem.get("style") and "roman;" in elem.get("style"):
                        roman_numerals = ["", "I", "II", "III",
                                          "IV", "V", "VI", "VII", "VIII", "IX", "X"]
                        numeral = roman_numerals[counter]
                        parsed.append(f"  {numeral}. ")
                    else:
                        parsed.append(f"  {counter}. ")
                    parsed_children = [""]
                    for child in child.children:
                        parse_html(state, parsed_children, image_urls, child)
                    parsed.extend([
                        f"    {child}" if i > 0 else child
                        for i, child in enumerate(parsed_children)
                    ])
                    counter += 1
        elif elem.name == "ul":
            parsed.append(newline)
            for child in elem.children:
                if child.name == "li":
                    parsed.append(f"  - ")
                    parsed_children = [""]
                    for child in child.children:
                        parse_html(state, parsed_children, image_urls, child)
                    parsed.extend([
                        f"    {child}" if i > 0 else child
                        for i, child in enumerate(parsed_children)
                    ])
        elif elem.name == "table":
            if elem.find("table"):
                errors.append(f"Found table within table: {elem}")
            header_cells = len(elem.find_all("th"))
            cells_in_first_row = len(elem.find("tr").find_all("td"))
            caption = ""
            parsed_table = [""]
            need_to_add_header_on_next_line = False
            for tbody in elem.children:
                if tbody.name == "caption":
                    caption = tbody.text.strip()
                elif tbody.name == "tbody":
                    for tr in tbody.children:
                        if tr.name == "tr":
                            parsed_table.append("|")
                            if need_to_add_header_on_next_line:
                                for _ in range(header_cells):
                                    parsed_table[-1] += "---|"
                                parsed_table.append("|")
                            for cell in tr.children:
                                if isinstance(cell, NavigableString) and not cell.text.strip():
                                    continue
                                if cell.name == "th":
                                    for child in cell.children:
                                        parse_html(
                                            state, parsed_table, image_urls, child)
                                    parsed_table[-1] += "|"
                                    need_to_add_header_on_next_line = True
                                elif cell.name == "td":
                                    for child in cell.children:
                                        parse_html(
                                            state, parsed_table, image_urls, child)
                                    parsed_table[-1] += "|"
                                    need_to_add_header_on_next_line = False
                                else:
                                    errors.append(
                                        f"Expected <td/>, found {cell}")
                        elif not isinstance(tr, NavigableString):
                            errors.append(f"Expected <tr/>, found {tr}")
                elif not isinstance(tbody, NavigableString):
                    errors.append(f"Expected <tbody/>, found {tbody}")

            if header_cells == 0:
                table_header = ["|"]
                for _ in range(cells_in_first_row):
                    table_header[-1] += "   |"
                table_header.append("|")
                for _ in range(cells_in_first_row):
                    table_header[-1] += "---|"
                if parsed_table[0] == "":
                    parsed_table = table_header + parsed_table[1:]
                else:
                    parsed_table = table_header + parsed_table

            if caption:
                parsed_table.extend([f"  : {caption}", ""])
            parsed_table.append(newline)
            parsed.extend(parsed_table)
        elif elem.name == "p" and not elem.get("class") and elem.get("style") == "text-align: center; font-size: 125%;" \
                or elem.name == "h2" and not elem.get("class") \
                or elem.name == "p" and elem.get("style") and "border-bottom: none; text-align: center; margin-top: 0.5em; margin-bottom: 0.5em;" in elem.get("style") and not elem.get("class"):
            parsed.extend([f"## {elem.text}", ""])
        elif elem.name == "h3" and not elem.get("class"):
            parsed.extend([f"### {elem.text}", ""])
        elif elem.name == "p" and not elem.get("class") and not elem.get("style") \
                or (elem.name == "p" or elem.name == "div") and not elem.get("class") and elem.get("style") == "margin-left: 3em;":
            parsed.append(newline)
            for child in elem.children:
                parse_html(state, parsed, image_urls, child)
            parsed.append(newline)
        elif elem.name == "p" and elem.get("class") == ["mw-empty-elt"]:
            # empty element, ignore
            pass
        elif elem.get("class") and "ebook-ignore-style" in elem.get("class"):
            # ignore the style, just parse the children
            for child in elem.children:
                parse_html(state, parsed, image_urls, child)
        elif elem.name == "div" and elem.get("class") and elem.get("class")[0].endswith("-container"):
            # generic container
            parsed.append(newline)
            for child in elem.children:
                parse_html(state, parsed, image_urls, child)
            parsed.append(newline)
        elif elem.name == "div" and elem.get("class") == ["tlp-column"]:
            parsed.append(newline)
            for child in elem.children:
                parse_html(state, parsed, image_urls, child)
            parsed.append(newline)
        elif elem.name == "div" and not elem.get("class") and elem.get("style") == "margin-left: -3em; float: left;":
            # section mark, ignore
            pass
        elif elem.name == "div" and not elem.get("class") and not elem.text.strip() and elem.get("style") == "clear: both;":
            # empty div, ignore
            pass
        elif elem.get("class") and elem.get("class") == ["custom-desktop-only"]\
                or elem.get("class") and elem.get("class") == ["custom-mobile-only"]:
            # ignore, seems to contain only page breaks of the Nachlass documents
            pass
        elif (elem.name == "div" or elem.name == "span") and elem.get("class") and elem.get("class") == ["noebook"]:
            pass
        elif elem.name == "div" and elem.get("class") and elem.get("class") == ["ebookonly"]:
            parsed.append(newline)
            for child in elem.children:
                parse_html(state, parsed, image_urls, child)
            parsed.append(newline)
        elif elem.name == "span" and elem.get("class") and elem.get("class") == ["ebookonly"]:
            for child in elem.children:
                parse_html(state, parsed, image_urls, child)
        elif elem.name == "div" and elem.get("class") and "colophon" in elem["class"]:
            # colophon
            parsed.append(newline)
            parsed_children = [""]
            for child in elem.children:
                parse_html(state, parsed_children, image_urls, child)
            for child in parsed_children:
                if child.strip():
                    parsed.append(f"_{child.strip()}_")
                else:
                    parsed.append(newline)
            parsed.extend(["", "# <<TITLE>>", "", ""])
        elif elem.name == "div" and elem.get("style") == "border: 1px solid silver; padding: 12px 20px; margin: 20px 0;":
            # box
            parsed.extend(["", "---", "", ""])
            for child in elem.children:
                parse_html(state, parsed, image_urls, child)
            parsed.extend(["", "---", "", ""])
        elif elem.name == "div" and elem.get("style") == "width: 60%; margin-right: auto; margin-left: auto;" \
                or elem.name == "p" and not elem.get("class") and elem.get("style") == "text-align: right;" \
                or elem.name == "p" and not elem.get("class") and elem.get("style") == "text-align: right; font-variant: small-caps;":
            # right
            parsed.append(newline)
            parsed_right = [""]
            for child in elem.children:
                parse_html(state, parsed_right, image_urls, child)
            for line in parsed_right:
                if line and not line.startswith("*"):
                    parsed.append(f"*{line}*")
                else:
                    parsed.append(line)
            parsed.append(newline)
        elif elem.name == "div" and (elem.get("class") == ["center"] or elem.get("style") == "text-align: center;") \
                or elem.name == "div" and not elem.get("class") and elem.get("style") == "display: flex; justify-content: center; align-items: center;" \
                or elem.name == "div" and not elem.get("class") and elem.get("style") == "width: 25%; margin: 2em auto 2em auto;" \
                or elem.name == "p" and not elem.get("class") and elem.get("style") == "text-align: center;" \
                or elem.name == "p" and not elem.get("class") and elem.get("style") == "text-align: center; font-variant: small-caps;" \
                or elem.name == "p" and elem.get("class") == ["plainlinks"] and elem.get("style") == "text-align: center;":
            # center
            parsed.append(newline)
            for child in elem.children:
                parse_html(state, parsed, image_urls, child)
            parsed.append(newline)
        elif elem.name == "div" and elem.get("class") == ["floatnone"] \
                or elem.name == "div" and not elem.get("class") and elem.get("style") == "float: left; width: 33.3%":
            # floatnone
            parsed.append(newline)
            for child in elem.children:
                parse_html(state, parsed, image_urls, child)
            parsed.append(newline)
        elif elem.name == "div" and not elem.get("class") and not elem.text.strip() and elem.get("style") == "display: inline-block; width: 3em;":
            # 4 times unicode NO-BREAK-SPACE
            parsed.append("\u00a0\u00a0\u00a0\u00a0")
        elif elem.name == "div" and elem.get("style")=="display: flex; justify-content: center; align-items: center; gap: 1em;":   
            # deal with the latex when mathoid -> mathjax, corner case
            img_tag = elem.find('img')
            alt = img_tag['alt'] 
            src = img_tag['src'] 
            image_urls.append(src)
            file_name = os.path.basename(src)
            
            # add the non-breaking space "\ " to suppress the caption
            parsed[-1] += f"![{alt}](images/{file_name})\\ "

        else:
            errors.append(
                f"Unrecognized element: <{elem.name} class=\"{elem.get('class')}\", style=\"{elem.get('style')}\">")
            parsed.append(newline)
            parsed.append(str(elem))
            parsed.append(newline)
    return parsed


def convert_latex_to_svg(latex, img_path):
    latex_cleaned = latex.replace(r"\displaystyle", "")
    latex_cleaned = re.sub(r"\\lor", "|", latex_cleaned)
    latex_cleaned = re.sub(r"\\land", "&", latex_cleaned)
    latex_cleaned = re.sub(r"\\supset", "->", latex_cleaned)
    latex_cleaned = re.sub(r"\\equiv", "<->", latex_cleaned)

    # plt.rcParams["text.usetex"] = True
    fig, ax = plt.subplots(figsize=(4, 1))
    ax.axis("off")  
    ax.text(0.5, 0.5, f"${latex_cleaned}$", fontsize=20, ha="center", va="center")
    
    buffer = BytesIO()
    plt.savefig(buffer, format="svg", bbox_inches="tight")
    buffer.seek(0)

    with open(img_path, "wb") as f:
        f.write(buffer.read())
    
    plt.close(fig)



def doc_as_md(text):
    title = text.find("p", "tl-title").text
    errors = []
    refs = []
    state = [errors, refs]
    parsed = f"""
---
author: Ludwig Wittgenstein
title: {title}
---

# Editor's Note

_Published by the [Ludwig Wittgenstein Project](https://www.wittgensteinproject.org/)._

"""
    image_urls = []
    for line in parse_html(state, [""], image_urls, text.find("div", "colophon")):
        parsed += line.strip().replace("# <<TITLE>>", f"# {title}") + "\n"
    after_title = text.find_all("p", "tl-title")[-1]
    while after_title.next_sibling:
        after_title = after_title.next_sibling
        for line in parse_html(state, [""], image_urls, after_title):
            line = line.strip()
            if len(line) > 1 and line[0] == "(":
                parsed += "\\(" + line[1:] + "\n"
            elif len(line) > 2 and line[1] == "." and line[2] == " ":
                parsed += line[0] + "\\." + line[2:] + "\n"
            else:
                parsed += line.strip() + "\n"
    return [errors, re.sub(r"\n(\s|\n)+", "\n\n", parsed).strip(), image_urls]

# Find all texts (language, title, link) on the main page:


all_texts_page = requests.get(
    # "https://www.wittgensteinproject.org/w/index.php?title=Project:All_texts&action=render").content
    "https://www.wittgensteinproject.org/w/index.php/Project:All_texts?action=render").content
all_texts = BeautifulSoup(all_texts_page, features="html.parser")

all_languages = {}
current_language = []
for elem in all_texts.find(id="all-texts-list"):
    if elem.name == "h2" and elem.span["class"] == ["mw-headline"]:
        language = elem.span["id"]
        current_language = []
        all_languages[language] = current_language
    elif elem.name == "ul":
        for link in elem.find_all("a"):
            title = link["title"]
            href = link["href"]
            current_language.append([title, href])

# Iterate through all texts and convert to markdown:

all_errors = []

for (language, texts) in all_languages.items():
    if language in BLACKLISTED_LANGS:
        continue
    for [title, link] in texts:
        if any([blacklisted_title.lower() in title.lower() for blacklisted_title in BLACKLISTED_WORKS]):
            print(f"(✓) {title} (BLACKLISTED)")
            continue
        html_page = requests.get(link, params={"action": "render"}).content
        text = BeautifulSoup(html_page, features="html.parser")
        [errors, md, image_urls] = doc_as_md(text)
        if errors:
            print(f"[ ] {title}")
            for e in errors:
                print(f"    - {e}")
        else:
            print(f"[✓] {title}")
        all_errors.extend(errors)
        cwd = os.getcwd()
        path_to_lang = os.path.join(cwd, "markdown", language.lower())
        path_to_doc_dir = os.path.join(path_to_lang, f"{title}")
        path_to_doc_images_dir = os.path.join(path_to_doc_dir, "images")
        path_to_doc = os.path.join(path_to_doc_dir, f"{title}.md")
        if not os.path.exists(path_to_lang):
            os.mkdir(path_to_lang)
        if not os.path.exists(path_to_doc_dir):
            os.mkdir(path_to_doc_dir)
        with open(path_to_doc, "w") as f:
            f.write(md)
        for image_url in image_urls:           
            if "\displaystyle" in image_url:
                # deal with latex when mathoid -> mathjax, convert latex to svg
                if not os.path.exists(path_to_doc_images_dir):
                    os.mkdir(path_to_doc_images_dir)
                hash_object = hashlib.sha256(image_url.encode())
                file_name = f"{hash_object.hexdigest()}.svg"
                path_to_image_file = os.path.join(
                    path_to_doc_images_dir, file_name)
                if not os.path.exists(path_to_image_file):
                    convert_latex_to_svg(image_url, path_to_image_file)
                    print(f"Converted {image_url} to {path_to_image_file}")
                    time.sleep(SECONDS_BETWEEN_IMG_REQUESTS)
            else:
                if image_url.startswith("/w/"):
                    image_url = "https://www.wittgensteinproject.org" + image_url
                if not os.path.exists(path_to_doc_images_dir):
                    os.mkdir(path_to_doc_images_dir)
                file_name = urllib.parse.unquote(os.path.basename(image_url))
                if "/svg/" in image_url and not image_url.endswith(".svg"):
                    file_name += ".svg"
                elif "/thumb/" in image_url:
                    file_name = file_name
                path_to_image_file = os.path.join(
                    path_to_doc_images_dir, file_name)
                if not os.path.exists(path_to_image_file):
                    print(f"- Fetching '{image_url}'...")
                    img = requests.get(image_url).content
                    with open(path_to_image_file, 'wb') as file:
                        file.write(img)
                    time.sleep(SECONDS_BETWEEN_IMG_REQUESTS)
            
            
        time.sleep(SECONDS_BETWEEN_DOC_REQUESTS)

if all_errors:
    print("ERROR: Not all documents could be converted successfully!")
    sys.exit(1)

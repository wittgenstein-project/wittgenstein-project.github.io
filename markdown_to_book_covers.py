import os, subprocess, sys, math, re
from shlex import quote

MARKDOWN_DIR = "markdown"
EPUB_DIR = "epub"
WIDTH = 1600
HEIGHT = 2400
ROW_TITLE = 20
COLUMN_TITLE = 2
LWP_YELLOW = "hsl(52, 92%, 81%)"

def collides_exact(words, column, row):
    if row >= ROW_TITLE and row < ROW_TITLE + (len(words) * 3):
        word = words[(row - ROW_TITLE) // 3]
        if column > COLUMN_TITLE and column <= COLUMN_TITLE + 1 + (len(word) * 2):
            return True
    return False

def collides_fuzzy(words, column, row):
    collision = False
    for c in range(column - 1, column + 2):
        for r in range(row - 1, row + 2):
            if collides_exact(words, c, r):
                collision = True
                break
    return collision

has_changed_files = subprocess.check_output(
    ["git", "ls-files", "-m", "-o", "--exclude-from=.gitignore"])
if not has_changed_files:
    print("No .md files have changed, nothing to do...")
else:
    for lang in os.listdir(MARKDOWN_DIR):
        for work in os.listdir(os.path.join(MARKDOWN_DIR, lang)):
            print(f"*** Generating cover for {work} ***")
            md_file_name = os.path.join(MARKDOWN_DIR, lang, work, f"{work}.md")
            svg_file_name = os.path.join(MARKDOWN_DIR, lang, work, "cover.svg")
            png_file_name = os.path.join(MARKDOWN_DIR, lang, work, "cover.png")
            with open(md_file_name, 'r') as md:
                md = md.read()
                words = re.split(" |(?<=-)", f"Wittgenstein — {work}")
                svg_fg = ""
                svg_bg = ""
                column = 0
                row = 0
                cell_width = 40
                while row < 10:
                    cx = cell_width + column * cell_width
                    cy = cell_width + row * cell_width
                    svg_fg += f"""\n<circle cx="{cx}" cy="{cy}" r="4" stroke="black" fill="none" stroke-width="2" />"""
                    column += 1
                    if column + 1 >= WIDTH / cell_width:
                        column = 0
                        row += 1
                for remark in md.split("\n"):
                    if not remark:
                        continue
                    cx = cell_width + column * cell_width
                    cy = cell_width + row * cell_width
                    #r = math.log(len(remark) + 1) * 2
                    r = math.log(len(remark) + 1)**2 / 3
                    periods = len([c for c in remark if c == "."])
                    question_marks = len([c for c in remark if c == "?"])
                    if periods <= question_marks:
                        svg_bg += f"""\n<circle cx="{cx}" cy="{cy}" r="{r * 2 + 4}" fill="{LWP_YELLOW}" stroke="{LWP_YELLOW}" stroke-width="8" />"""
                    if "**" in remark:
                        fill = "black"
                    else:
                        fill = "none"
                    #svg += f"""\n<rect x="{cx - r}" y="{cy - r}" width="{r * 2}" height="{r * 2}" fill="{fill}" stroke="black" stroke-width="6" />"""
                    svg_fg += f"""\n<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="black" stroke-width="6" />"""
                    #if "$" in remark:
                    #    x1 = (column * cell_width) + (cell_width / 2)
                    #    y1 = (row * cell_width) + (cell_width * 1.5)
                    #    x2 = x1 + cell_width
                    #    y2 = y1 - cell_width
                    #    svg += f"""\n<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="black" stroke-width="6" />"""
                    while True:
                        column += 1
                        if column + 1 >= WIDTH / cell_width:
                            column = 0
                            row += 1
                        collision = False
                        if not collides_fuzzy(words, column, row):
                            break
                while row + 1 < HEIGHT / cell_width:
                    if not collides_fuzzy(words, column, row):
                        cx = cell_width + column * cell_width
                        cy = cell_width + row * cell_width
                        svg_fg += f"""\n<circle cx="{cx}" cy="{cy}" r="4" stroke="black" fill="none" stroke-width="2" />"""
                    column += 1
                    if column + 1 >= WIDTH / cell_width:
                        column = 0
                        row += 1
                x = (cell_width * 2) + (cell_width * COLUMN_TITLE)
                y = (cell_width * ROW_TITLE)
                font_size = cell_width * 3.3
                for word in words:
                    y += cell_width * 3
                    svg_fg += f"""<text x="{x}" y="{y}" fill="black" font-size="{font_size}" font-weight="bold" font-family="Space Mono">{word}</text>"""
                svg = f"""<svg width="{WIDTH}" height="{HEIGHT}">"""
                svg += svg_bg
                svg += svg_fg
                svg += "\n</svg>"
                with open(svg_file_name, 'w') as file:
                    file.write(svg)
                if os.system(f"rsvg-convert {quote(svg_file_name)} -o {quote(png_file_name)}") != 0:
                    sys.exit(1)

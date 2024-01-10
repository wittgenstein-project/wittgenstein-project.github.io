import os, subprocess, sys, math, re, grapheme
from shlex import quote

MARKDOWN_DIR = "markdown"
EPUB_DIR = "epub"
WIDTH = 1600
HEIGHT = 2400
ROW_TITLE = 20
COLUMN_TITLE = 2
LWP_GRAY = "#4c4c4c"
LWP_YELLOW = "#fbf0a4"
LWP_LOGO_SVG = """<g
     inkscape:label="Layer 1"
     inkscape:groupmode="layer"
     id="layer1">
    <g
       inkscape:export-ydpi="6.959094"
       inkscape:export-xdpi="6.959094"
       transform="translate(10.151076,0.99040557)"
       id="g945"
       style="fill:none;stroke:#4c4c4c;stroke-opacity:1;stroke-width:3.96875;stroke-miterlimit:4;stroke-dasharray:none">
      <path
         inkscape:transform-center-y="-1.4357909e-06"
         transform="rotate(-30,214.5413,172.89371)"
         inkscape:transform-center-x="2.2365329e-06"
         d="m 204.4255,66.549513 c -16.79115,29.083126 -9.82535,25.061419 -43.40765,25.061418 -33.5823,0 -26.6165,4.021707 -43.40765,-25.061418 -16.79115,-29.083126 -16.79115,-21.039712 0,-50.122837 16.79115,-29.083126 9.82535,-25.0614189 43.40765,-25.0614187 33.5823,1e-7 26.6165,-4.0217073 43.40765,25.0614187 16.79115,29.083126 16.79115,21.039711 0,50.122837 z"
         inkscape:randomized="0"
         inkscape:rounded="0.67"
         inkscape:flatsided="true"
         sodipodi:arg2="1.0471976"
         sodipodi:arg1="0.52359878"
         sodipodi:r2="43.407646"
         sodipodi:r1="50.122837"
         sodipodi:cy="41.488094"
         sodipodi:cx="161.01785"
         sodipodi:sides="6"
         id="path940"
         style="opacity:1;fill:none;fill-opacity:1;stroke:#4c4c4c;stroke-width:3.96875;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;stroke-dashoffset:0;stroke-opacity:1"
         sodipodi:type="star" />
      <path
         sodipodi:type="star"
         style="opacity:1;fill:none;fill-opacity:1;stroke:#4c4c4c;stroke-width:3.96875;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;stroke-dashoffset:0;stroke-opacity:1"
         id="path943"
         sodipodi:sides="6"
         sodipodi:cx="161.01785"
         sodipodi:cy="41.488094"
         sodipodi:r1="50.122837"
         sodipodi:r2="43.407646"
         sodipodi:arg1="0.52359878"
         sodipodi:arg2="1.0471976"
         inkscape:flatsided="true"
         inkscape:rounded="0.67"
         inkscape:randomized="0"
         d="m 204.4255,66.549513 c -16.79115,29.083126 -9.82535,25.061419 -43.40765,25.061418 -33.5823,0 -26.6165,4.021707 -43.40765,-25.061418 -16.79115,-29.083126 -16.79115,-21.039712 0,-50.122837 16.79115,-29.083126 9.82535,-25.0614189 43.40765,-25.0614187 33.5823,1e-7 26.6165,-4.0217073 43.40765,25.0614187 16.79115,29.083126 16.79115,21.039711 0,50.122837 z"
         inkscape:transform-center-x="2.2365329e-06"
         transform="rotate(-30,214.5413,172.89371)"
         inkscape:transform-center-y="-1.4357909e-06"
         inkscape:export-xdpi="100"
         inkscape:export-ydpi="100" />
    </g>
    <path
       inkscape:export-ydpi="6.959094"
       inkscape:export-xdpi="6.959094"
       sodipodi:nodetypes="csczc"
       inkscape:connector-curvature="0"
       id="path947"
       d="m 97.916286,69.236227 c 0,-8.20574 2.393794,-16.78667 14.720624,-16.78667 12.32682,0 14.72062,8.58093 14.72062,16.78667 0,0 -6.44546,-2.050791 -14.67337,-2.050791 -8.22791,0 -14.767874,2.050791 -14.767874,2.050791 z"
       style="fill:#4c4c4c;fill-opacity:1;stroke:none;stroke-width:0.36155897px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1" />
    <g
       transform="translate(-657.37874,-138.86078)"
       id="g965"
       inkscape:export-xdpi="6.959094"
       inkscape:export-ydpi="6.959094">
      <path
         style="fill:#4c4c4c;fill-opacity:1;stroke:none;stroke-width:0.30062637px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"
         d="m 771.29132,208.45025 c 8.18498,0 11.31264,1.64466 14.01757,2.70512 4.95929,1.94428 7.58322,8.19609 7.58322,16.56826 0,25.99077 -7.46342,32.52284 -19.54378,33.13876 -1.52441,-7.1807 -2.05701,-20.39336 -2.05701,-25.73529 z"
         id="path951"
         inkscape:connector-curvature="0"
         sodipodi:nodetypes="cssccc" />
      <path
         sodipodi:nodetypes="cssccc"
         inkscape:connector-curvature="0"
         id="path961"
         d="m 768.73998,208.45025 c -8.18498,0 -11.31264,1.64466 -14.01757,2.70512 -4.95929,1.94428 -7.58322,8.19609 -7.58322,16.56826 0,25.99077 7.46342,32.52284 19.54378,33.13876 1.52441,-7.1807 2.05701,-20.39336 2.05701,-25.73529 z"
         style="fill:#4c4c4c;fill-opacity:1;stroke:none;stroke-width:0.30062637px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1" />
    </g>
  </g>"""

def collides_exact(lang, words, column, row):
    if row >= ROW_TITLE and row < ROW_TITLE + (len(words) * 3):
        word = words[(row - ROW_TITLE) // 3]
        word_len = grapheme.length(word) * 2
        if lang == "hindi":
            word_len += 2
        if column > COLUMN_TITLE and column <= COLUMN_TITLE + 1 + (word_len):
            return True
    return False

def collides_fuzzy(lang, words, column, row):
    collision = False
    for c in range(column - 1, column + 2):
        for r in range(row - 1, row + 2):
            if collides_exact(lang, words, c, r):
                collision = True
                break
    return collision

has_changed_files = subprocess.check_output(
    ["git", "ls-files", "-m", "-o", "--exclude-from=.gitignore"])
if not has_changed_files and not os.environ["GITHUB_EVENT_NAME"] == "push":
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
                    if row < 2 or row > 6 or column < 2 or column > 27 or (row < 4 and column > 17):
                        svg_fg += f"""\n<circle cx="{cx}" cy="{cy}" r="4" stroke="black" fill="none" stroke-width="2" />"""
                    column += 1
                    if column + 1 >= WIDTH / cell_width:
                        column = 0
                        row += 1
                for remark in md.split("\n")[12:]: # skip 12 paragraphs (titles + colophon)
                    if not remark:
                        continue
                    cx = cell_width + column * cell_width
                    cy = cell_width + row * cell_width
                    r = math.log(len(remark) + 1)**2 / 3
                    periods = len([c for c in remark if c == "."])
                    question_marks = len([c for c in remark if c == "?"])
                    if periods <= question_marks:
                        svg_bg += f"""\n<circle cx="{cx}" cy="{cy}" r="{r * 2 + 4}" fill="{LWP_YELLOW}" stroke="{LWP_YELLOW}" stroke-width="8" />"""
                    if "**" in remark:
                        fill = "black"
                    else:
                        fill = "none"
                    svg_fg += f"""\n<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="black" stroke-width="6" />"""
                    while True:
                        column += 1
                        if column + 1 >= WIDTH / cell_width:
                            column = 0
                            row += 1
                        collision = False
                        if not collides_fuzzy(lang, words, column, row):
                            break
                while row + 1 < HEIGHT / cell_width:
                    if not collides_fuzzy(lang, words, column, row):
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
                    font_family = "font-family=\"Space Mono\""
                    if lang == "hindi":
                       font_family = "font-family=\"'Nimbus Mono PS', 'Courier New', monospace\""
                    svg_fg += f"""<text x="{x}" y="{y}" fill="black" font-size="{font_size}" font-weight="bold" {font_family}>{word}</text>"""
                svg_fg += f"""<g transform="translate({cell_width * 2.1}, {cell_width * 3 - 6})">{LWP_LOGO_SVG}</g>"""
                svg_fg += f"""<text x="{cell_width * 7.2}" y="{cell_width * 4.6}" fill="{LWP_GRAY}" font-size="{cell_width * 1.65}" font-weight="bold" font-family="Space Mono">The Ludwig</text>"""
                svg_fg += f"""<text x="{cell_width * 7.2}" y="{cell_width * 6.4}" fill="{LWP_GRAY}" font-size="{cell_width * 1.65}" font-weight="bold" font-family="Space Mono">Wittgenstein Project</text>"""
                svg = f"""<svg width="{WIDTH}" height="{HEIGHT}"
                xmlns:dc="http://purl.org/dc/elements/1.1/"
                xmlns:cc="http://creativecommons.org/ns#"
                xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                xmlns:svg="http://www.w3.org/2000/svg"
                xmlns="http://www.w3.org/2000/svg"
                xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
                xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape">
                """                
                svg += svg_bg
                svg += svg_fg
                svg += "\n</svg>"
                with open(svg_file_name, 'w') as file:
                    file.write(svg)
                if os.system(f"rsvg-convert {quote(svg_file_name)} -o {quote(png_file_name)} -b='#ffffff'") != 0:
                    sys.exit(1)

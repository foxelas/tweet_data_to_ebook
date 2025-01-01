from pathlib import Path
import pandas as pd
from os.path import join as pathjoin
from configuration import data_path, media_folder, tweets_csv_file, output_ebook_file
import re

# Paths to the input data and output folder
media_path = Path(data_path) / media_folder  # Use pathlib for joining paths
media_folder = media_path  # Ensure media_folder is a Path object
output_ebook_path = output_ebook_file + ".md"  # Markdown format for the ebook

# Load the sorted and filtered tweets
tweets_df = pd.read_csv(tweets_csv_file)

# Function to remove t.co links from the tweet text
def remove_tco_links(text):
    return re.sub(r'https://t\.co/\S+', '', text).strip()


def embed_media(tweet_id_):
    # Use glob to find files that match the pattern
    media_files = list(media_folder.glob(f"{tweet_id_}-*.jpg"))  # Match files like tweet_id-*.jpg

    media_files = [preprocess_for_latex(file.as_posix()) for file in media_files]
    if media_files:
        num_files = len(media_files)
        if num_files == 1:
            # Single image centered
            media_md = (
                f"\\begin{{center}}\n"
                f"\\includegraphics[height=100pt]{{{media_files[0]}}}\n"
                f"\\end{{center}}"
            )
        elif num_files == 2:
            # 1x2 grid for two images
            media_md = (
                "\\begin{figure}[H]\n"
                "\\centering\n"
                f"\\begin{{subfigure}}[b]{{0.48\\textwidth}}\n"
                f"\\includegraphics[width=\\textwidth, height=\\textwidth, trim=50 50 50 50, clip]{{{media_files[0]}}}\n"
                "\\caption{}\n"
                "\\end{subfigure}\n"
                "\\hfill\n"
                f"\\begin{{subfigure}}[b]{{0.48\\textwidth}}\n"
                f"\\includegraphics[width=\\textwidth, height=\\textwidth, trim=50 50 50 50, clip]{{{media_files[1]}}}\n"
                "\\caption{}\n"
                "\\end{subfigure}\n"
                "\\end{figure}"
            )
        elif num_files == 3:
            # 1x3 grid for three images
            media_md = (
                "\\begin{figure}[H]\n"
                "\\centering\n"
                f"\\begin{{subfigure}}[b]{{0.32\\textwidth}}\n"
                f"\\includegraphics[width=\\textwidth, height=\\textwidth, trim=50 50 50 50, clip]{{{media_files[0]}}}\n"
                "\\caption{}\n"
                "\\end{subfigure}\n"
                "\\hfill\n"
                f"\\begin{{subfigure}}[b]{{0.32\\textwidth}}\n"
                f"\\includegraphics[width=\\textwidth, height=\\textwidth, trim=50 50 50 50, clip]{{{media_files[1]}}}\n"
                "\\caption{}\n"
                "\\end{subfigure}\n"
                "\\hfill\n"
                f"\\begin{{subfigure}}[b]{{0.32\\textwidth}}\n"
                f"\\includegraphics[width=\\textwidth, height=\\textwidth, trim=50 50 50 50, clip]{{{media_files[2]}}}\n"
                "\\caption{}\n"
                "\\end{subfigure}\n"
                "\\end{figure}"
            )
        elif num_files == 4:
            # 2x2 grid for four images
            media_md = (
                "\\begin{figure}[H]\n"
                "\\centering\n"
                f"\\begin{{subfigure}}[b]{{0.48\\textwidth}}\n"
                f"\\includegraphics[width=\\textwidth, height=\\textwidth, trim=50 50 50 50, clip]{{{media_files[0]}}}\n"
                "\\caption{}\n"
                "\\end{subfigure}\n"
                "\\hfill\n"
                f"\\begin{{subfigure}}[b]{{0.48\\textwidth}}\n"
                f"\\includegraphics[width=\\textwidth, height=\\textwidth, trim=50 50 50 50, clip]{{{media_files[1]}}}\n"
                "\\caption{}\n"
                "\\end{subfigure}\n"
                "\\vspace{{0.5cm}}\n"
                f"\\begin{{subfigure}}[b]{{0.48\\textwidth}}\n"
                f"\\includegraphics[width=\\textwidth, height=\\textwidth, trim=50 50 50 50, clip]{{{media_files[2]}}}\n"
                "\\caption{}\n"
                "\\end{subfigure}\n"
                "\\hfill\n"
                f"\\begin{{subfigure}}[b]{{0.48\\textwidth}}\n"
                f"\\includegraphics[width=\\textwidth, height=\\textwidth, trim=50 50 50 50, clip]{{{media_files[3]}}}\n"
                "\\caption{}\n"
                "\\end{subfigure}\n"
                "\\end{figure}"
            )
        else:
            # Fallback: Vertical list for more than 4 images
            media_md = "\n".join(
                [
                    f"\\begin{{center}}\n\\includegraphics[height=100pt]{{{file}}}\n\\end{{center}}"
                    for file in media_files
                ]
            )

        return media_md


# LaTeX preamble for tcolorbox
latex_preamble = r"""
\usepackage{xeCJK}
\setmainfont{Noto Sans}
\setCJKmainfont{Noto Sans JP}
\newfontface\emojifont{Noto Emoji}
\newcommand{\emoji}[1]{{\emojifont #1}}

\usepackage{float}
\usepackage{subcaption}
\usepackage{graphicx}

\usepackage{xcolor}
\usepackage{tcolorbox}
\tcbset{
    sharp corners,
    colframe=blue!75!black,
    colback=blue!10!white,
    boxrule=1mm,
    width=\textwidth,
    enlarge left by=5mm
}
"""

# Build the ebook content
ebook_content = "---\nheader-includes: |\n  " + latex_preamble.replace("\n", "\n  ") + "\n---\n"
ebook_content += "# My Tweet Ebook\n\n"


def preprocess_for_latex(content):
    # Escape special LaTeX characters: # $ % & _ { } ~ ^ \
    content = re.sub(r"([#\$%&_{}^\\])", r"\\\1", content)
    # Handle tilde
    content = re.sub(r"~", r"--", content)
    # Escape square brackets
    content = content.replace("[", "{[}").replace("]", "{]}")
    # Replace emojis dynamically
    content = re.sub(r"([\U0001F300-\U0001FAF6\U0001F1E6-\U0001F1FF\u2660-\u2667\u2640-\u2642\uFE0F])", r"\\emoji{\1}",
                     content)
    return content


# Group tweets into chapters (you can customize this logic)
current_year = None
for i, tweet in tweets_df.iterrows():
    # Extract tweet details
    tweet_text = remove_tco_links(tweet["full_text"])
    created_at = pd.to_datetime(tweet["created_at"])
    tweet_id = tweet["id"]

    # Create a new chapter for each year
    if current_year != created_at.year:
        current_year = created_at.year
        ebook_content += f"\n\n# Chapter {current_year}\n\n"

    # Embed tweet text
    #ebook_content += f"## Tweet from {created_at.strftime('%B %d, %Y')}\n\n"
    tweet_text = preprocess_for_latex(tweet_text)
    ebook_content += f"\\begin{{tcolorbox}}\n{tweet_text}\n"


    # Embed media if available
    media = embed_media(tweet_id)
    if media:
        ebook_content += f"{media}\n\n"

    ebook_content += f"\\end{{tcolorbox}}\n\n"

    if i == 800:
        break

# Save the ebook as a Markdown file
with open(output_ebook_path, "w", encoding="utf-8") as ebook_file:
    ebook_file.write(ebook_content)

print(f"Ebook saved to {output_ebook_path}")

if True:
    import pypandoc
    import os
    import re


    # Ensure the input file exists
    if not os.path.exists(output_ebook_path):
        raise FileNotFoundError(f"{output_ebook_path} not found!")

    # Paths to the Markdown file and output PDF
    pdf_file = output_ebook_file + ".pdf"


    # Convert Markdown to PDF using pypandoc
    # https://latex3.github.io/babel/guides/which-method-for-which-language.html
    output = pypandoc.convert_file(
        output_ebook_path,
        to="pdf",
        outputfile=pdf_file,
        extra_args=[
            "--pdf-engine=xelatex",
            "--variable=mainfont:Noto Sans",
            "--variable=CJKmainfont:Noto Sans JP",
            #"--variable=mainfontfallback:Noto Emoji", #works only in lualatex
            "--variable=geometry:margin=1in",
            #"--from=markdown+raw_html+native_divs", # pandoc --list-extensions=markdown
            "--metadata=lang:gr"]
    )


    print(f"PDF saved to {pdf_file}")



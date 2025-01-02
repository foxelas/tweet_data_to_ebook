from pathlib import Path
import pandas as pd
import pypandoc
import os
import re
from configuration import data_path, media_folder, tweets_csv_file, output_ebook_file, item_styles, style_key, \
    color_palette, latex_preamble, latex_preamble_end, text_title, chapter_title
from get_tweets import prepare_files

# Paths to the input data and output folder
media_path = Path(data_path) / media_folder  # Use pathlib for joining paths
media_folder = media_path  # Ensure media_folder is a Path object
output_ebook_path = output_ebook_file + ".md"  # Markdown format for the ebook

# Load the sorted and filtered tweets
if os.path.exists("selected_tweets.csv"):
    print("selected_tweets.csv found, reading from that one.")
    tweets_df = pd.read_csv("selected_tweets.csv")
else:
    print("selected_tweets.csv not found, preparing files.")
    if not os.path.exists(tweets_csv_file):
        prepare_files(min_favorite_count=0)
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
                "\\begin{figure}[H]\n"
                "\\begin{flushright}\n"
                f"\\includegraphics[height=150pt]{{{media_files[0]}}}\n"
                "\\end{flushright}\n"
                "\\end{figure}"
            )
        elif num_files in {2, 3, 4}:
            # Flexible grid for 1x2, 1x3, or 2x2 layout
            widths = {2: "0.48\\textwidth", 3: "0.32\\textwidth", 4: "0.48\\textwidth"}
            subfigures = "\n".join(
                f"\\begin{{subfigure}}[b]{{{widths[num_files]}}}\n"
                f"\\begin{{center}}\n"
                f"\\includegraphics[width=\\textwidth, height=\\textwidth, trim=10 10 10 10, clip]{{{media_files[i]}}}\n"
                f"\\end{{center}}"
                f"\\end{{subfigure}}"
                + ("\n\\hfill" if i < num_files - 1 else "")
                for i in range(num_files)
            )
            media_md = (
                "\\begin{figure}[H]\n"
                "\\begin{flushright}\n"
                f"{subfigures}\n"
                "\\end{flushright}\n"
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
    return ""


# Define the LaTeX preamble
latex_preamble = latex_preamble
latex_preamble += color_palette
latex_preamble += item_styles.get(style_key, "")
latex_preamble += latex_preamble_end
container_tag = style_key

def preprocess_for_latex(content):
    # Escape standard LaTeX special characters
    content = re.sub(r"([#\$%&_{}\\])", r"\\\1", content)

    # Handle tilde (~) and caret (^)
    content = re.sub(r"~", r"\\textasciitilde{}", content)
    content = re.sub(r"\^", r"\\textasciicircum{}", content)

    # Escape square brackets
    content = content.replace("[", "{[}").replace("]", "{]}")

    # Replace emoji and other pictographic symbols
    content = re.sub(
        r"([\U0001F300-\U0001FAF6\U0001F1E6-\U0001F1FF\u2B00-\u2BFF\u2600-\u26FF\u2900-\u297F\u2700-\u27FF])",
        r"\\emoji{\1}",
        content
    )

    # Replace punctuation and other special mathematical characters
    content = re.sub(
        r"([\u2E00-\u2E7F\u2200-\u22FF])",
        r"\\charfont{\1}",
        content
    )

    # Remove variation selector (U+FE0F) which may cause issues
    content = content.replace("\uFE0F", "")

    return content

# Build the ebook content
ebook_content = "---\nheader-includes: |\n  " + latex_preamble.replace("\n", "\n  ") + "\n---\n"
ebook_content += "# " + text_title + "\n"

# Group tweets into chapters (you can customize this logic)
flag = False
current_year = None
for i, tweet in tweets_df.iterrows():
    # Extract tweet details
    tweet_text = remove_tco_links(tweet["full_text"])
    tweet_text = re.sub(r'^"(.*)"$', r'\1', tweet_text)
    created_at = pd.to_datetime(tweet["created_at"])
    tweet_id = tweet["id"]

    # Create a new chapter for each year
    if current_year != created_at.year:
        flag = False
        current_year = created_at.year
        ebook_content += f"\n\n## {chapter_title} {current_year}\n\n"

    # Embed tweet text
    #ebook_content += f"## Tweet from {created_at.strftime('%B %d, %Y')}\n\n"
    tweet_text = preprocess_for_latex(tweet_text)
    media = embed_media(tweet_id)

    flag = not flag
    if style_key == "newchat":
        if not flag:
            ebook_content += f"\\begin{{{style_key}}}{{{prev_media}}}{{{media}}}\n{prev_text}\n{tweet_text}\n\\end{{{style_key}}}\n\n"
        else:
            prev_text = tweet_text
            prev_media = media

    elif style_key == "custombox":
        color = "primary" if flag else "secondary"
        alignment = "left" if flag else "right"
        if alignment == "left":
            media = re.sub(r"{flushright}", r"{flushleft}", media)
        ebook_content += f"\\begin{{{style_key}}}{{{color}}}{{{alignment}}}\n{tweet_text}\n{media}\\end{{{style_key}}}\n\n"

    #if i == 300:
    #    break

# Save the ebook as a Markdown file
with open(output_ebook_path, "w", encoding="utf-8") as ebook_file:
    ebook_file.write(ebook_content)

print(f"Ebook saved to {output_ebook_path}")


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
        #"--variable=mainfont:Noto Sans", #overwritten in the preamble
        #"--variable=CJKmainfont:Noto Sans JP", #overwritten in the preamble
        #"--variable=mainfontfallback:Noto Emoji", #works only in lualatex
        "--variable=geometry:margin=1in",
        #"--from=markdown+raw_html+native_divs", # pandoc --list-extensions=markdown
        "--metadata=lang:gr"]
)


print(f"PDF saved to {pdf_file}")



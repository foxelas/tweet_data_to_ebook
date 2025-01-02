from pathlib import Path
import pandas as pd
import pypandoc
import re
from configuration import (
    data_path, media_folder, tweets_csv_file, output_ebook_file,
    item_styles, style_key, color_palette, latex_preamble,
    latex_preamble_end, text_title, chapter_title
)
from get_tweets import prepare_files

# Define paths
media_path = Path(data_path) / media_folder
output_ebook_path = f"{output_ebook_file}.md"

# Load tweets
if Path("selected_tweets.csv").exists():
    print("Loading selected_tweets.csv.")
    tweets_df = pd.read_csv("selected_tweets.csv")
else:
    print("selected_tweets.csv not found. Preparing tweets.")
    if not Path(tweets_csv_file).exists():
        prepare_files(min_favorite_count=0)
    tweets_df = pd.read_csv(tweets_csv_file)

# Remove `t.co` links
def remove_tco_links(text):
    return re.sub(r'https://t\.co/\S+', '', text).strip()

# Embed media into LaTeX
def embed_media(tweet_id_):
    media_files = list(media_path.glob(f"{tweet_id_}-*.jpg"))
    if not media_files:
        return ""

    media_files = [preprocess_for_latex(file.as_posix()) for file in media_files]
    num_files = len(media_files)

    if num_files == 1:
        return (
            "\\begin{figure}[H]\n"
            "\\begin{flushright}\n"
            f"\\includegraphics[height=150pt]{{{media_files[0]}}}\n"
            "\\end{flushright}\n"
            "\\end{figure}"
        )

    if num_files in {2, 3, 4}:
        widths = {2: "0.48\\textwidth", 3: "0.32\\textwidth", 4: "0.48\\textwidth"}
        subfigures = "\n".join(
            f"\\begin{{subfigure}}[b]{{{widths[num_files]}}}\n"
            f"\\begin{{center}}\n"
            f"\\includegraphics[width=\\textwidth, height=\\textwidth, trim=10 10 10 10, clip]{{{media_files[i]}}}\n"
            f"\\end{{center}}\n"
            f"\\end{{subfigure}}"
            + ("\n\\hfill" if i < num_files - 1 else "")
            for i in range(num_files)
        )
        return (
            "\\begin{figure}[H]\n"
            "\\begin{flushright}\n"
            f"{subfigures}\n"
            "\\end{flushright}\n"
            "\\end{figure}"
        )

    return "\n".join(
        f"\\begin{{center}}\n\\includegraphics[height=100pt]{{{file}}}\n\\end{{center}}"
        for file in media_files
    )

# Preprocess text for LaTeX
def preprocess_for_latex(content):
    content = re.sub(r"([#\$%&_{}\\])", r"\\\1", content)
    content = re.sub(r"~", r"\\textasciitilde{}", content)
    content = re.sub(r"\^", r"\\textasciicircum{}", content)
    content = content.replace("[", "{[}").replace("]", "{]}")
    content = re.sub(
        r"([\U0001F300-\U0001FAF6\U0001F1E6-\U0001F1FF\u2B00-\u2BFF\u2600-\u26FF\u2900-\u297F\u2700-\u27FF])",
        r"\\emoji{\1}",
        content
    )
    content = re.sub(r"([\u2E00-\u2E7F\u2200-\u22FF])", r"\\charfont{\1}", content)
    return content.replace("\uFE0F", "")

# Build LaTeX preamble
latex_preamble = f"{latex_preamble}{color_palette}{item_styles.get(style_key, '')}{latex_preamble_end}"
ebook_content = "---\nheader-includes: |\n  " + latex_preamble.replace("\n", "\n  ") + "\n---\n"
ebook_content += f"# {text_title}\n"

# Process tweets into the ebook
current_year = None
flag = False
for _, tweet in tweets_df.iterrows():
    tweet_text = preprocess_for_latex(remove_tco_links(tweet["full_text"]).strip('"'))
    created_at = pd.to_datetime(tweet["created_at"])
    tweet_id = tweet["id"]

    # Create new chapter for each year
    if current_year != created_at.year:
        current_year = created_at.year
        flag = False
        ebook_content += f"\n\n## {chapter_title} {current_year}\n\n"

    # Embed tweet and media
    media = embed_media(tweet_id)
    flag = not flag
    if style_key == "newchat":
        if not flag:
            ebook_content += f"\\begin{{{style_key}}}{{{prev_media}}}{{{media}}}\n{prev_text}\n{tweet_text}\n\\end{{{style_key}}}\n\n"
        else:
            prev_text, prev_media = tweet_text, media
    elif style_key == "custombox":
        color = "primary" if flag else "secondary"
        alignment = "left" if flag else "right"
        media = re.sub(r"{flushright}", r"{flushleft}", media) if alignment == "left" else media
        ebook_content += f"\\begin{{{style_key}}}{{{color}}}{{{alignment}}}\n{tweet_text}\n{media}\\end{{{style_key}}}\n\n"

# Save ebook content
with open(output_ebook_path, "w", encoding="utf-8") as ebook_file:
    ebook_file.write(ebook_content)

print(f"Ebook saved to {output_ebook_path}")

# Convert Markdown to PDF
pdf_file = f"{output_ebook_file}.pdf"
pypandoc.convert_file(
    output_ebook_path,
    to="pdf",
    outputfile=pdf_file,
    extra_args=["--pdf-engine=xelatex", "--variable=geometry:margin=1in", "--metadata=lang:gr"]
)
print(f"PDF saved to {pdf_file}")

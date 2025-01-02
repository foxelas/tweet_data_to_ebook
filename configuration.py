data_path = 'twitter-2024-12-22-63817e8a76ce4d8e9278696556deeaa87bf3aa5bbad26aab0fa3e0e61c544068/data/'
tweets_file = 'tweets.js'
tweets_csv_file = 'sorted_filtered_tweets.csv'
media_folder = 'tweets_media'
output_ebook_file = 'tweets_ebook'

text_title = "Ημερολόγιο Ιαπωνίας"
chapter_title = "Κεφάλαιο"

# LaTeX preamble
latex_preamble = r"""
```{=latex}
\usepackage{xeCJK}

\usepackage{unicode-math} 
\setmathfont{Noto Sans Math} 
\setmainfont{DejaVu Sans Bold}
\setCJKmainfont{Noto Sans Mono CJK SC}
\newfontface\emojifont{Noto Color Emoji}
\newfontface\mathfont{Noto Sans Math}

\newcommand{\emoji}[1]{{\emojifont #1}}
\newcommand{\charfont}[1]{{\mathfont #1}}


\usepackage{float}
\usepackage{subcaption}
\usepackage{graphicx}

\usepackage{xcolor}

"""

latex_preamble_end = "\n```"

color_palette = r"""
\definecolor{primary}{HTML}{D8BFD8}    % Pastel Purple (Thistle)
\definecolor{secondary}{HTML}{ADD8E6}  % Pastel Blue (Light Blue)
\definecolor{accent}{HTML}{E6E6FA}     % Lavender
\definecolor{tertiary}{HTML}{88EABB}   % Soft Mint Green
\definecolor{highlight}{HTML}{FAF0FF}  % Pale Lavender Tint
"""



item_styles = {
    "custombox": r"""
\usepackage{tcolorbox}
\tcbset{
    rounded corners,
    flush left,
    halign=left,
    colframe=primary!75!black,
    colback=primary,
    width=0.8\textwidth,
    boxrule=1mm,
    enlarge left by=5mm
}

\newtcolorbox{custombox}[3][]{colframe=#2!75!black, colback=#2, flush #3, halign=#3, #1}
""",

    "newchat": r"""\usepackage{tikz}
\usepackage{xparse}

\newcounter{chatlinenum}

%% Adjust text width to suit
\tikzset{chatstyle/.style={text width=0.8\textwidth,rounded corners=2pt}}


\begingroup
    \lccode`~=`\^^M
    \lowercase{%
\endgroup
    \def\newchatline#1~{%
        \stepcounter{chatlinenum}%
        \ifodd\thechatlinenum
            \tikz[]{\node[fill=secondary,chatstyle,align=left]{\strut#1 
            			\IfValueT{\prevmedia}{% Check if media exists for odd lines
            				\prevmedia % Render the block of LaTeX code passed as media
            			}%
            			\strut};}%

        \else
            \hfill
            \tikz[]{\node[fill=primary,chatstyle,align=right]{\strut#1 
            			\IfValueT{\media}{% Check if media exists for odd lines
            				\media % Render the block of LaTeX code passed as media
            			}%
            			\strut};}%
        \fi
        ~
        \smallskip
    }%
}

\NewDocumentEnvironment{newchat}{mm}{% Accept blocks of LaTeX code for prev_media and media
    \def\prevmedia{#1}% Define the content of prev_media
    \def\media{#2}% Define the content of media
    \setcounter{chatlinenum}{0}
    \begin{minipage}{\textwidth}
        \obeylines
        \everypar={\newchatline}
}{%
    \end{minipage}
}
"""
}

style_key = list(item_styles.keys())[0]


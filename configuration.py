data_path = 'twitter-2024-12-22-63817e8a76ce4d8e9278696556deeaa87bf3aa5bbad26aab0fa3e0e61c544068/data/'
tweets_file = 'tweets.js'
tweets_cleaned_file = 'tweets_cleaned.json'
tweets_csv_file = 'sorted_filtered_tweets.csv'
media_folder = 'tweets_media'
output_ebook_file = 'tweets_ebook'


color_palette = r"""
\definecolor{primary}{HTML}{88EABB}
\definecolor{secondary}{HTML}{4A90E2}
"""



item_styles = {
    "tcolorbox": r"""
\usepackage{tcolorbox}
\tcbset{
    sharp corners,
    colframe=primary!75!black,
    colback=primary!10!white,
    boxrule=1mm,
    width=\textwidth,
    enlarge left by=5mm
}
""",

    "newchat": r"""\usepackage{tikz}
\usepackage{xparse}

\newcounter{chatlinenum}

%% Adjust text width to suit
\tikzset{chatstyle/.style={text width=0.8\textwidth,rounded corners=2pt}}

%% Alter colors to suit
\begingroup
    \lccode`~=`\^^M
    \lowercase{%
\endgroup
    \def\newchatline#1~{%
        \stepcounter{chatlinenum}%
        \ifodd\thechatlinenum
            \tikz[]{\node[fill=secondary,chatstyle]{\strut#1\strut};}%
        \else
            \hfill
            \tikz[]{\node[fill=primary,chatstyle,align=right]{\strut#1\strut};}%
        \fi
        ~
        \smallskip
    }%
}

\NewDocumentEnvironment{newchat}{}{%
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


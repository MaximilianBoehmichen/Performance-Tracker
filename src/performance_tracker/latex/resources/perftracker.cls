\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{perftracker}[2025/12/30]

\DeclareOption*{
    \ClassWarning{perftracker}{Cannot process option \CurrentOption}
}
\ProcessOptions\relax
\LoadClass[10pt]{article}
\pagestyle{empty}


\usepackage{eurosym}
\usepackage[utf8]{inputenc}
\DeclareUnicodeCharacter{20AC}{\euro}

\usepackage{textcomp}
\usepackage[T1]{fontenc}
\usepackage[english]{babel}
\usepackage[lighttt]{lmodern}
\usepackage{graphicx}
\usepackage[usenames,dvipsnames,svgnames,table]{xcolor}
\usepackage{datetime}
\usepackage{tikz}
\usetikzlibrary{calc}

\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usepgfplotslibrary{dateplot}

\usepackage[a4paper,hmargin={6.75cm,1cm},vmargin={1cm,2cm}]{geometry}
\reversemarginpar

\usepackage[pdfusetitle,hidelinks]{hyperref}
\usepackage{setspace}
\usepackage[final]{microtype}
\usepackage[autostyle]{csquotes}
\usepackage{marginnote}
\usepackage{xstring}
\usepackage{tabularx}
\usepackage{booktabs}
\usepackage{amssymb}

\usepackage[compact]{titlesec}
\titleformat{\section}
  {\normalfont\LARGE\bfseries\color{mainColour}}
  {\thesection}
  {1em}
  {}

\titlespacing*{\section}{0pt}{*2.25}{*1}

\usepackage{enumitem}
\setlist{noitemsep}

\usepackage[scaled]{helvet}
\renewcommand{\familydefault}{\sfdefault}

\definecolor{mainColour}{RGB}{0, 100, 164}
\newcolumntype{R}{>{\raggedleft\arraybackslash}X}


\usepackage[abspage,user]{zref}


\newcommand{\@sidebarcontent}{}
\newcommand{\setsidebar}[1]{%
  \gdef\@sidebarcontent{\unexpanded{#1}}%
}

\AddToHook{shipout/foreground}{%
  \put (0,0) {%
    \begin{tikzpicture}[remember picture, overlay]

      %\node [anchor=north west, inner sep=1cm] at (current page.north west)
      %  {\includegraphics[width=20mm,height=10mm]{example-image}};

      \draw [color=mainColour, line width=1pt]
        ([xshift=6.375cm, yshift=-1cm]current page.north west) --
        ([xshift=6.375cm, yshift=1cm]current page.south west);

      \node [anchor=north west, inner sep=0cm, rotate=90, font=\small, color=gray, transform shape]
        at ([xshift=0.5cm, yshift=1cm]current page.south west)
        {Financial data sourced via the \href{https://finance.yahoo.com}{Yahoo! finance API}. Copyright \copyright Yahoo Inc. 2021, All Rights Reserved. Refer to TOS.};

      \node [anchor=south east, inner sep=1cm, font=\small\sffamily, color=mainColour]
        at ([xshift=0cm, yshift=0cm]current page.south east)
        {\thepage/\zref[page]{LastPage}};

      \node [anchor=north west,
             text width=5cm,
             align=left,
             inner sep=0pt,
             font=\small\sffamily]
        at ([xshift=1cm, yshift=-1.0cm]current page.north west) {
            \@sidebarcontent
        };

    \end{tikzpicture}%
  }%
}


\endinput

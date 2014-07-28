%% mpreport, an attempt at a modern report layout
%% Michael Piotrowski <mxp@dynalabs.de>

%% NOTE:  This class automatically specifies the a4paper option and
%%        loads the graphicx package.

%% The class begins by announcing itself as |mpreport.cls|.
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{mpreport}[2010/11/04 A variant report class]

%% It passes all options on to the |report| class.
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{report}}
\ProcessOptions

%% It then loads the class |report|.
\LoadClass[a4paper]{report}

%% We also need the |ifthen| package.
\RequirePackage{ifthen}

%% Load |geometry| now; if it's loaded in the document, it'll mess up
%% the layout.
\RequirePackage{geometry}

%% For your convenience we also load |graphicx|--you typically need it 
%% in reports.
\RequirePackage{graphicx}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% The class then redefines |\maketitle|.
   \if@titlepage
   \renewcommand{\maketitle}{%
     \begin{titlepage}%
       % top line
       
       \hspace{-\mp@margwd}\rule{\mp@fullwd}{.25mm}%
       \vspace{-\baselineskip}\vspace{.25mm}%
       \par\hspace{-\mp@margwd}\rule{\mp@margwd}{2mm}%
       \par\hspace{-\mp@margwd}%

       % title

       \begin{flushright}
         \sffamily\bfseries\upshape%
         \large\@author\\[1ex]\huge\@title\\[1ex]\normalsize\@date
         \vfill
       \end{flushright}

       % bottom line
       \par
       \hspace{-\mp@margwd}%
       \rule{\mp@margwd}{2.25mm}%
       \hspace{-\mp@margwd}%
       \rule{\mp@fullwd}{.25mm}%
     \end{titlepage}%
     }
   \else
   \renewcommand{\maketitle}{%
     \begin{flushleft}
       \null\hfill
       \vskip 2cm
       \huge\sffamily\bfseries
       \@title\\
       \large\mdseries\upshape
       \vspace{.5em}%
       \@author\\
       \ifx\date\@empty\else\@date\fi
                                %\rule{\textwidth}{.5mm}\\
     \end{flushleft}
     \@thanks
     \par
     \vskip 1cm
     }
   \fi

%% Redefine |\and| to be useful with the redefined |\maketitle|
   \renewcommand{\and}{\\}

%% Redefine |\chapter|
   \renewcommand{\thechapter}{\arabic{chapter}}
   
   \renewcommand{\chapter}{%
     \if@openright\clearpage{\pagestyle{empty}\cleardoublepage}%
     \else\clearpage%
     \fi
     \secdef\@chapter\@schapter%
     }

   \renewcommand{\@chapter}[2][?]{%
     \clearpage%
     \refstepcounter{chapter}%
     {%
       \parskip1ex%
       \parindent \z@ \raggedright \normalfont%
       \ifnum \c@secnumdepth >\m@ne%
       \par%
       \hspace{-\mp@margwd}\rule{\mp@fullwd}{.25mm}%
       \vspace{-\baselineskip}\\[2mm]%
       \hspace{-\mp@margwd}\rule{\mp@margwd}{2mm}%
       \par\hspace{-\mp@margwd}%
       % typeset the chapter number
       \makebox[\mp@margwd][r]{%
         \fontsize{6\EX}{6\EX}\sffamily\bfseries\thechapter
         }%
       \hfill%
       \fi
       % set variables for the formatting of the chapter title
       \settoheight{\mp@chapnoht}{%
         \fontsize{6\EX}{6\EX}\sffamily\bfseries\thechapter}%
       \settoheight{\mp@chaptlht}{\parbox[b]{.9\textwidth}{%
           \raggedleft\sffamily\bfseries\Huge #2}}
       % set the chapter title                                %
       \raisebox{-\mp@chaptlht}{\raisebox{\mp@chapnoht}{%
           \parbox[b]{.9\textwidth}{\raggedleft\sffamily\bfseries\Huge
             #2}}}%
       \chaptermark{#1}%
       \addcontentsline{toc}{chapter}{\protect\numberline{\thechapter}#1}%
       \par\nobreak%
       \vskip\mp@margwd%
       }}

   \renewcommand{\@schapter}[1]{%        % for chapter*{...}
     {%
       \clearpage%
       \parskip1ex%
       \parindent \z@ \raggedright \normalfont%
       \par%
       \hspace{-\mp@margwd}\rule{\mp@fullwd}{.25mm}%
       \vspace{-\baselineskip}\\[2mm]%
       \hspace{-\mp@margwd}\rule{\mp@margwd}{2mm}%
       \par\hspace{-\mp@margwd}%
       % don't typeset the chapter number
       \hfill%
       % set variables for the formatting of the chapter title
       \settoheight{\mp@chapnoht}{%
         \fontsize{6\EX}{6\EX}\sffamily\bfseries\thechapter}%
       \settoheight{\mp@chaptlht}{\parbox[b]{.9\textwidth}{%
           \raggedleft\sffamily\bfseries\Huge #1}}
       % set the chapter title                                %
       \raisebox{-\mp@chaptlht}{\raisebox{\mp@chapnoht}{%
           \parbox[b]{.9\textwidth}{\raggedleft\sffamily\bfseries\Huge #1}}}%
       \par\nobreak%
       \vskip\mp@margwd%
       }%
     }
     
%% Redefine |\section|
   \renewcommand{\section}{\secdef\@section\@ssection}

   \newlength{\mp@headht}
   \newcommand{\@section}[2][?]%
   {%
     \def\@currentlabelname{#1} % for compatibility with nameref
     \refstepcounter{section}%
     \vspace{\baselineskip}%
     \pagebreak[3]%
     {%
       \parskip1.5ex%
       \hspace{-\mp@margwd}\rule{\mp@fullwd}{.25mm}%
       \par\vspace*{-.5\baselineskip}%
       \hspace{-\mp@margwd}%
       \sffamily\bfseries\large\thesection~#2\par\nobreak
     }%
     \sectionmark{#1}%
     \addcontentsline{toc}{section}{\protect\numberline{\thesection}#1}%
     \nopagebreak[4]
   }

   \newcommand{\@ssection}[1]%        % for section*{...}
   {%
     \def\@currentlabelname{#1} % for compatibility with nameref
     \vspace{\baselineskip}%
     \pagebreak[3]%
     {%
       \parskip1.5ex%
       \hspace{-\mp@margwd}\rule{\mp@fullwd}{.25mm}%
       \par\vspace*{-.5\baselineskip}%
       \hspace{-\mp@margwd}%
       \sffamily\bfseries\large#1\par\nobreak
     }%
     \par
   }

%% Redefine |\subsection|
   \renewcommand{\subsection}{%
     \@startsection
     {subsection}{2}{0pt}{-1.5ex plus -1ex minus -.2ex}%
     {1ex plus .2ex}{\sffamily\bfseries\normalsize}%
     }

%% Redefine |\subsubsection|
   \renewcommand{\subsubsection}{%
     \@startsection
     {subsubsection}{3}{0pt}{-1.5ex plus -1ex minus -.2ex}%
     {1ex plus .2ex}{\sffamily\bfseries\normalsize}%
     }

%% Put caption in the margin, next to the figure/table (place caption first in
%% figure/table environment)
   \newlength{\mp@capht}
   \newcommand{\mp@makefigcap}[2]{%
     % Measure height of caption
     \settoheight{\mp@capht}{%
       \parbox[b]{.9\mp@margwd}{%
         \def\footnotemark{\relax}% Avoid incrementing the footnote counter
         \raggedleft\small\slshape\sffamily#1: #2}}%
     % Actually typeset the caption
     \hspace{-\mp@margwd}%
     \vspace*{-\mp@capht}%
     \parbox[t]{.9\mp@margwd}{\raggedleft\small\slshape\sffamily#1: #2}
     }
   
   \renewcommand{\figure}{%
     \let\@makecaption\mp@makefigcap\@float{figure}%
     }
   \renewcommand{\table}{%
     \let\@makecaption\mp@makefigcap\@float{table}%
     }

%% Page style
%% For |\pagestyle{plain}|
   \renewcommand{\ps@plain}{%
     \renewcommand{\@oddhead}{}%
     \renewcommand{\@evenhead}{}%
     \renewcommand{\@oddfoot}{\hfil\textsf{\thepage}}%
     \renewcommand{\@evenfoot}{\hspace{-\mp@margwd}\textsf{\thepage}\hfil}%
     }
%% For |\pagestyle{headings}|
   \if@twoside
     \renewcommand{\ps@headings}{%
       \renewcommand{\@oddhead}{{\sffamily\rightmark}\hfil}%
       \renewcommand{\@evenhead}{\hfil\sffamily\leftmark}%
       \renewcommand{\@oddfoot}{\hfil\textsf{\thepage}}%
       \renewcommand{\@evenfoot}{\hspace{-\mp@margwd}\textsf{\thepage}\hfil}%
       \let\@mkboth\markboth
       \def\chaptermark##1{%
         \markboth {%
           \ifnum \c@secnumdepth >\m@ne
           \thechapter \quad %
           \fi
           ##1}{}}%
       \def\sectionmark##1{%
         \markright {%
           \ifnum \c@secnumdepth >\z@
           \thesection \quad %
           \fi
           ##1}}%
     }
   \else
     \renewcommand{\ps@headings}{%
       \renewcommand{\@oddhead}{{\hfil{\sffamily\rightmark}}}
       \renewcommand{\@oddfoot}{\hfil\textsf{\thepage}}
       \let\@mkboth\markboth
       \def\chaptermark##1{%
         \markright {%
           \ifnum \c@secnumdepth >\m@ne
           \thechapter \quad %
           \fi
           ##1}}%
     }
   \fi
%% For |\pagestyle{myheadings}|
   \renewcommand{\ps@myheadings}{
     \renewcommand{\@oddhead}{{\sffamily\rightmark}\hfil}
     \renewcommand{\@evenhead}{\hfil\sffamily\leftmark}
     \renewcommand{\@oddfoot}{\hfil\textsf{\thepage}}%
     \renewcommand{\@evenfoot}{\hspace{-\mp@margwd}\textsf{\thepage}\hfil}%

     \let\@mkboth\@gobbletwo
     \let\chaptermark\@gobble
     \let\sectionmark\@gobble
   }

%% Footnote style
%%
%% "Daß man auch den Noten selbst diese kleine hochstehende Ziffer
%% voranstellt, ist eine sinnlose Neuerung der Verfallszeit, die jetzt
%% zum Glück wieder verschwindet. Hier hat nur die Vollziffer mit dem
%% Punkt dahinter zu stehen." (Paul Renner, Die Kunst der Typographie,
%% p. 70)
   \newcommand{\mp@fnsep}{.} % Footnote separator, default is a period
   \newlength{\mp@fnhangindent} % Hanging indent for footnotes
   \newcommand{\mp@setfnhangindent}[1]{%
     \footnotesize%
     \setlength{\mp@fnhangindent}{#1}%
   }
   \renewcommand{\@makefntext}[1]{%
     \setlength{\parindent}{0mm}%
     \hangindent=\mp@fnhangindent%
     \makebox[1.5em][l]{\normalfont\@thefnmark\mp@fnsep}\enspace#1%
   }

%% Let the footnote mark in the text inherit the font and style of
%% the text.
   \renewcommand\@makefnmark{\textsuperscript{\mdseries\@thefnmark}}

%% Marginal notes
%% We redefine the |\marginpar| command so that marginpars always appear
%% in the left margin.  Cf.
%% <http://www.tug.org/tex-archive/support/dbtex/refman.sty>
%% <http://tug.ctan.org/tex-archive/macros/latex/contrib/refman/layout_e.pdf>
   \def\@addmarginpar{\@next\@marbox\@currlist{\@cons\@freelist\@marbox
       \@cons\@freelist\@currbox}\@latexbug\@tempcnta\@ne
       \@tempcnta\m@ne % always in the left margin
       \ifnum\@tempcnta <\z@ \global\setbox\@marbox\box\@currbox \fi
       \@tempdima\@mparbottom \advance\@tempdima -\@pageht
          \advance\@tempdima\ht\@marbox \ifdim\@tempdima >\z@
          \@warning{Marginpar on page \thepage\space moved}\else\@tempdima\z@
          \fi
       \global\@mparbottom\@pageht \global\advance\@mparbottom\@tempdima
          \global\advance\@mparbottom\dp\@marbox
          \global\advance\@mparbottom\marginparpush
       \advance\@tempdima -\ht\@marbox
       \global\ht\@marbox\z@ \global\dp\@marbox\z@
       \vskip -\@pagedp \vskip\@tempdima\nointerlineskip
       \hbox to\columnwidth
         {\ifnum \@tempcnta >\z@
             \hskip\columnwidth \hskip\marginparsep
           \else \hskip -\marginparsep \hskip -\marginparwidth \fi
          \box\@marbox \hss}
       \vskip -\@tempdima
       \nointerlineskip
       \hbox{\vrule \@height\z@ \@width\z@ \@depth\@pagedp}}

%% Set the style of the marginpars to match that of captions
   \let\oldmarginpar\marginpar
   \renewcommand\marginpar[2][none]{%
     \-\oldmarginpar{\raggedleft\sffamily\slshape\small#2}%
   }

%% Dimensions
   \setlength\hoffset{-1in}
   \setlength\voffset{-0.0548822\paperheight} % odd number due to |geometry|
   \setlength\textwidth{0.571429\paperwidth}         % A4: 120 mm
   \ifnum\paperheight>\paperwidth
     \setlength\textheight{.85\paperheight} % portrait
   \else
     \setlength\textheight{.80\paperheight} % landscape
   \fi
   \setlength{\oddsidemargin}{0.357143\paperwidth}   % A4: 75 mm
   \setlength{\evensidemargin}{0.309524\paperwidth}  % A4: 65 mm
   \pagestyle{plain} 

   \parindent0mm
   \parskip1ex

   \newlength{\mp@margwd}
   \setlength{\mp@margwd}{0.238095\paperwidth}       % A4: 50 mm
   \setlength{\marginparwidth}{0.85\mp@margwd}

   \newlength{\mp@fullwd}
   \setlength{\mp@fullwd}{\textwidth}
   \addtolength{\mp@fullwd}{\mp@margwd}

   \newlength{\mp@chapnoht} % height of the chapter number
   \newlength{\mp@chaptlht} % height of the chapter title
   \newlength{\EX}
   \settoheight{\EX}{\normalsize X}
   \setlength{\EX}{2\EX}

\endinput

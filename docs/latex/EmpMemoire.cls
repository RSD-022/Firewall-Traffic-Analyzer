\NeedsTeXFormat{LaTeX2e}[1995/12/01]
\ProvidesClass{EmpMemoire}[1999/06/01\space
           LaTeX2e document class^^J
===========(thesetb\space JM.Rouet, ENST-Bretagne)============^^J
This class has been inspired from thloria, D. Roegel, LORIA]
%% Option draft
\newif\if@draft
\@draftfalse 
\DeclareOption{draft}{%
  \@drafttrue
  }

%% Styles de chapitre
\newif\if@style@chapLargeNum
\@style@chapLargeNumfalse 
\DeclareOption{ChapStyle1}{%
  \@style@chapLargeNumtrue
  \@style@chapOrdinalfalse
  \@style@chapDefaultfalse
  }
\newif\if@style@chapOrdinal
\@style@chapOrdinalfalse
\DeclareOption{ChapStyle2}{%
  \@style@chapOrdinaltrue
  \@style@chapLargeNumfalse
  \@style@chapDefaultfalse
  }
\newif\if@style@chapDefault
\@style@chapDefaulttrue % Style par d�faut
\DeclareOption{ChapStyle0}{%
  \@style@chapOrdinalfalse
  \@style@chapLargeNumfalse
  \@style@chapDefaulttrue
  }

%% Styles de couverture
\newif\if@style@rennes
\@style@rennesfalse
\DeclareOption{rennes1}{%
  \@style@rennestrue
  }
\newif\if@style@brest
\@style@brestfalse
\DeclareOption{brest}{%
  \if@style@rennes
  \ClassWarning*{thesetb}
  {Options \string`brest\string' is ignored\MessageBreak
    when \string`rennes\string' is present.}
  \else
  \@style@bresttrue
  \fi
  }

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{EmpClass}}
\ProcessOptions
\LoadClass[a4paper]{EmpClass}[1995/01/31]

\RequirePackage[utf8]{inputenc}


\if@style@rennes
  \typeout{Mise en page selon le style de these de l'ecole doctorale de  rennes 1}
\else
  \if@style@brest
    \typeout{Mise en page selon le style de these de l'ecole doctorale de    l'UBO}
  \else
    \ClassWarning{thesetb}{style de these non d�fini}
  \fi
\fi

                                % Titre (THESE)
\newcommand{\@ThesisKind}{{\UseEntryFont{ThesisKind}Thesis}}
\newcommand\ThesisKind[1]%
{\renewcommand{\@ThesisKind}{{\UseEntryFont{ThesisKind}#1}}}

                                % Date de la soutenance
\newcommand{\@ThesisDate}{\fbox{{\tt\char`\\ThesisDate}}}
\newcommand\ThesisDate[1]{\renewcommand{\@ThesisDate}{#1}}

                                % pr�sent�e
\newcommand{\@ThesisPresented}{%
  {\UseEntryFont{ThesisKind}Thesis}\\%
  Submitted in partial fulfillment of the requirements for the Master's degree
}
%\newcommand\ThesisPresented[1]%
%{\renewcommand{\@ThesisPresented}{{\UseEntryFont{ThesisPresented}#1}}}
                       
                              % FFiliere
\newcommand{\@ThesisFFiliere}{{\UseEntryFont{ThesisPresented}\bf{Department}~:}}
%\newcommand\ThesisPresented[1]%
%{\renewcommand{\@ThesisPresented}{{\UseEntryFont{ThesisPresented}#1}}}
                               
                                % Filiere
\newcommand{\@ThesisFiliere}{{\UseEntryFont{ThesisPresented}\bf{Department}~:}}
\newcommand\ThesisFiliere[1]{\renewcommand{\@ThesisFiliere}{{#1}}}
                               
                               % OOption
\newcommand{\@ThesisOOption}{{\UseEntryFont{ThesisPresented}\bf{Option}~:}}
%\newcommand\ThesisPresented[1]%
%{\renewcommand{\@ThesisPresented}{{\UseEntryFont{ThesisPresented}#1}}}
                               % Option
\newcommand{\@ThesisOption}{{\UseEntryFont{ThesisPresented}\bf{Option}~:}}
\newcommand\ThesisOption[1]{\renewcommand{\@ThesisOption}{{#1}}}
                               
                               % Insigne
\newcommand{\@ThesisInsigne}{{\UseEntryFont{ThesisPresented}\bf{Ing}~:}}
\newcommand\ThesisInsigne[1]{\renewcommand{\@ThesisInsigne}{#1}}
                               
                               % Inge
\newcommand{\@ThesisInge}{{\UseEntryFont{ThesisPresented}\bf{Ing}~:}}
\newcommand\ThesisInge[1]{\renewcommand{\@ThesisInge}{#1}}
                               
                                % par
\newcommand{\@ThesisPresentedBy}{{\UseEntryFont{ThesisPresentedBy}by}}
\newcommand\ThesisPresentedBy[1]%
{\renewcommand{\@ThesisPresentedBy}{{\UseEntryFont{ThesisPresentedBy}#1}}}

                                % soutenue le ...
\newcommand{\@ThesisPresentedThe}{{Publicly defended on \@ThesisDate{} before the examination committee:}}
\newcommand\ThesisPresentedThe[1]%
{\renewcommand{\@ThesisPresentedThe}{{\UseEntryFont{ThesisPresentedThe}#1}}}
                                
                                % Auteur
\newcommand{\@ThesisMention}{{\UseEntryFont{ThesisMention}By~:
    \fbox{\'ecrire \tt\char`\\ThesisMention\{ la mention \}}}}
\newcommand\ThesisAuteur[1]%
{\renewcommand{\@ThesisMention}{    
    {Par~: {\bf{#1}}}
    }}


                                % Titre de la th�se
\newcommand{\@ThesisTitle}%
{{\UseEntryFont{ThesisTitle}\fbox{\tt\char`\\ThesisTitle}\par}}
\newcommand\ThesisTitle[1]%
{\renewcommand{\@ThesisTitle}{\begin{center}
\begin{tabular}{|p{16.5cm}|}
\hline
\vfill{\begin{center}
{\UseEntryFont{ThesisTitle}#1\par}\end{center}}\\
  \hline
\end{tabular}
 \end{center}}}


 
 
\newcommand\SetEntryFont[2]{\expandafter\def\csname @#1font\endcsname{#2}}
\newcommand\SetTBFont[7]{\expandafter\def\csname @#1font\endcsname
  {\TBusefont{#2}{#3}{#4}{#5}{#6}{#7}}}

\newcommand\UseEntryFont[1]{\csname @#1font\endcsname}
\newcommand{\TBusefont}[6]{\fontsize{#5}{#6}\usefont{#1}{#2}{#3}{#4}}
\newcommand{\TitlePageFontFamily}{cmr}
\newcommand{\TitlePageFontEncoding}{T1}

\SetTBFont{ThesisNumeroOrdre}%
{\TitlePageFontEncoding}{\TitlePageFontFamily}{m}{n}{12}{14}%
\SetTBFont{ThesisTitle}%
{\TitlePageFontEncoding}{\TitlePageFontFamily}{bx}{n}{20}{30}%
\SetTBFont{ThesisKind}%
{\TitlePageFontEncoding}{\TitlePageFontFamily}{bx}{sc}{16}{16}%
\SetTBFont{ThesisPresented}%
{\TitlePageFontEncoding}{\TitlePageFontFamily}{m}{n}{14}{15}%
\SetTBFont{ThesisBefore}%
{\TitlePageFontEncoding}{\TitlePageFontFamily}{bx}{sc}{20.74}{25}%
\SetTBFont{ThesisPresentedThe}%
{\TitlePageFontEncoding}{\TitlePageFontFamily}{m}{n}{14}{15}%
\SetTBFont{ThesisInOrderToGet}%
{\TitlePageFontEncoding}{\TitlePageFontFamily}{m}{n}{14}{15}%
\SetTBFont{ThesisDiploma}%
{\TitlePageFontEncoding}{\TitlePageFontFamily}{bx}{sc}{17.28}{20}
\SetTBFont{ThesisMention}%
{\TitlePageFontEncoding}{\TitlePageFontFamily}{m}{n}{14}{15}%
\SetTBFont{ThesisPresentedBy}%
{\TitlePageFontEncoding}{\TitlePageFontFamily}{m}{n}{14}{15}%
\SetTBFont{ThesisAuthor}%
{\TitlePageFontEncoding}{\TitlePageFontFamily}{bx}{n}{17.28}{20}
\SetTBFont{ThesisJury}%
{\TitlePageFontEncoding}{\TitlePageFontFamily}{m}{n}{14}{15}%
\SetTBFont{ThesisAffil}%
{\TitlePageFontEncoding}{\TitlePageFontFamily}{m}{n}{12}{14}%
\SetTBFont{ThesisAffilSmall}%
{\TitlePageFontEncoding}{\TitlePageFontFamily}{m}{n}{10}{12}%
\SetTBFont{ThesisCompositionJury}%
{\TitlePageFontEncoding}{\TitlePageFontFamily}{m}{n}{14}{15}%

\newif\if@affiliation
\@affiliationfalse
\newtoks\@affil@tokI
\newtoks\@affil@tokII
\newcommand\@tokc@t[3]{%
  \edef\@tokconc@t{\the#1\the#2}%
  #3=\expandafter{\@tokconc@t}%
  }
\newtoks\@thesis@affil
\newcommand{\NewAffilCategory}[3]{%
  \expandafter\newtoks\csname#1\endcsname
  \csname#1\endcsname={}%
  \expandafter\def\csname#1@title\endcsname{{#2}{#3}}%
  \@affil@tokI=\expandafter{\csname#1\endcsname}%
  \@tokc@t\@thesis@affil\@affil@tokI\@thesis@affil
  \@affil@tokI=\expandafter{\csname#1@title\endcsname}%
  \@tokc@t\@thesis@affil\@affil@tokI\@thesis@affil
  }
\newcommand{\ClearAffil}{\@thesis@affil={}}
\ClearAffil
\NewAffilCategory{EquipeAccueil}{Research Team~:}{Research Team~:}
\NewAffilCategory{EquipesAccueil}{Research Teams~:}{Research Teams~:}
\NewAffilCategory{EcoleDoctorale}{Doctoral School~:}{Doctoral School~:}
\NewAffilCategory{EcolesDoctorales}{Doctoral Schools~:}{Doctoral Schools~:}
\def\@selectiaffil#1{\expandafter\@@selectiaffil#1}
\def\@@selectiaffil#1#2{{#1}}
\def\@selectiiaffil#1{\expandafter\@@selectiiaffil#1}
\def\@@selectiiaffil#1#2{{#2}}
\newcommand\@buildaffil[1]{%
  \@affil@tokI={\bgroup\UseEntryFont{ThesisAffil}\begin{tabular}{lll}}%
    \expandafter\@@buildaffil\the#1/%
    \@affil@tokII={\end{tabular}\egroup}%
  \@tokc@t\@affil@tokI\@affil@tokII\@affil@tokI
  \the\@affil@tokI
  }
\def\@@buildaffil#1#2#3/{%
  \def\@tmpa{#3}%
  \ifx\@tmpa\@empty
  \def\@tmpa{#1}%
  \ifx\@tmpa\@empty
  \else\@buildentryaffil#1#2%
  \fi
  \else
  \@buildentryaffil#1#2%
  \@@buildaffil#3/%
  \fi
  }
\newcommand\@buildentryaffil[2]{\expandafter\@buildtableaffil\the#1\\/#2}
\def\@buildtableaffil#1\\#2/#3{%
  \def\@tmpa{#1}%
  \ifx\@tmpa\@empty
  \else
  \@affiliationtrue %cette variable est utilis�e pour supprimer un
                    % \vfill lorsqu'il n'y a pas d'affiliation de 
                    % pr�cis�e
  \def\@tmpa{#2}%
  \ifx\@tmpa\@empty
  \@affil@tokII={\@selectiaffil#3&#1\\}%
  \@tokc@t\@affil@tokI\@affil@tokII\@affil@tokI
  \else
  \@affil@tokII={\@selectiiaffil#3&#1\\}%
  \@tokc@t\@affil@tokI\@affil@tokII\@affil@tokI
  \@@buildtableaffil#2/%
  \fi
  \@affil@tokII={[3mm]}%
  \@tokc@t\@affil@tokI\@affil@tokII\@affil@tokI
  \fi
  }
\def\@@buildtableaffil#1\\#2/{%
  \@affil@tokII={&#1\\}%
  \@tokc@t\@affil@tokI\@affil@tokII\@affil@tokI
  \def\@tmpa{#2}%
  \ifx\@tmpa\@empty
  \else\@@buildtableaffil#2/%
  \fi
  }



\newcommand\@ThesisAffil{
  \if@style@rennes
  \vspace{1cm}\@buildaffil\@thesis@affil
  \else
  \UseEntryFont{ThesisAffil}\fbox{use \tt\char`\\ThesisAffil\{Work carried out at...\}}
  \fi
}
\newcommand\ThesisAffil[1]%
{\@affiliationfalse \ClearAffil \renewcommand{\@ThesisAffil}{{\UseEntryFont{ThesisAffilSmall}#1\par}}}


\newtoks\@jury@tokI
\newtoks\@jury@tokII
\newtoks\@thesis@jury
\newcommand{\NewJuryCategory}[3]{%
  \expandafter\newtoks\csname#1\endcsname
  \csname#1\endcsname={}%
  \expandafter\def\csname#1@title\endcsname{{#2}{#3}}%
  \@jury@tokI=\expandafter{\csname#1\endcsname}%
  \@tokc@t\@thesis@jury\@jury@tokI\@thesis@jury
  \@jury@tokI=\expandafter{\csname#1@title\endcsname}%
  \@tokc@t\@thesis@jury\@jury@tokI\@thesis@jury
  }
\newcommand{\ClearJury}{\@thesis@jury={}}
\ClearJury
\NewJuryCategory{President}{\textbf{Chairperson:}}{\textbf{President:}}
\NewJuryCategory{Examinateurs}{\textbf{Examiner:}}{\textbf{Examiners:}}
\NewJuryCategory{Rapporteurs}{\textbf{Reviewer:}}{\textbf{Reviewers:}}
\NewJuryCategory{Invites}{\textbf{Guest:}}{\textbf{Guests:}}
\def\@selecti#1{\expandafter\@@selecti#1}
\def\@@selecti#1#2{{#1}}
\def\@selectii#1{\expandafter\@@selectii#1}
\def\@@selectii#1#2{{#2}}
\newcommand\@buildjury[1]{%
  \@jury@tokI={\bgroup\begin{tabular}{lll}}%
    \expandafter\@@buildjury\the#1/%
    \@jury@tokII={\end{tabular}\egroup}%
  \@tokc@t\@jury@tokI\@jury@tokII\@jury@tokI
  \the\@jury@tokI
  }
\def\@@buildjury#1#2#3/{%
  \def\@tmpa{#3}%
  \ifx\@tmpa\@empty
  \def\@tmpa{#1}%
  \ifx\@tmpa\@empty
  \else\@buildentry#1#2%
  \fi
  \else
  \@buildentry#1#2%
  \@@buildjury#3/%
  \fi
  }
\newcommand\@buildentry[2]{\expandafter\@buildtable\the#1\\/#2}
\def\@buildtable#1\\#2/#3{%
  \def\@tmpa{#1}%
  \ifx\@tmpa\@empty
  \else
  \def\@tmpa{#2}%
  \ifx\@tmpa\@empty
  \@jury@tokII={\@selecti#3&#1\\}%
  \@tokc@t\@jury@tokI\@jury@tokII\@jury@tokI
  \else
  \@jury@tokII={\@selectii#3&#1\\}%
  \@tokc@t\@jury@tokI\@jury@tokII\@jury@tokI
  \@@buildtable#2/%
  \fi
  \@jury@tokII={[3mm]}%
  \@tokc@t\@jury@tokI\@jury@tokII\@jury@tokI
  \fi
  }
\def\@@buildtable#1\\#2/{%
  \@jury@tokII={&#1\\}%
  \@tokc@t\@jury@tokI\@jury@tokII\@jury@tokI
  \def\@tmpa{#2}%
  \ifx\@tmpa\@empty
  \else\@@buildtable#2/%
  \fi
  }
\newcommand\@ThesisJury{\@buildjury\@thesis@jury}

\newlength\@bindingshift
\setlength\@bindingshift{0pt}
\newcommand\SetBinding[1]{%
  \setlength\@bindingshift{#1}%
  \divide\@bindingshift2\relax
  }
\newlength\@htitlepageshift
\newcommand{\@cover@hook}{}
\newenvironment{changemargin}[2]{\begin{list}{}{%
\setlength{\topsep}{0pt}%
\setlength{\leftmargin}{0pt}%
\setlength{\rightmargin}{0pt}%
\setlength{\listparindent}{\parindent}%
\setlength{\itemindent}{\parindent}%
\setlength{\parsep}{0pt plus 1pt}%
\addtolength{\leftmargin}{#1}%
\addtolength{\rightmargin}{#2}%
}\item }{\end{list}}



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%  Defines Divers                                %%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% les ensembles math�matiques
\RequirePackage{bbm}
\def\N{\ensuremath{\mathbbm{N}}}
\def\R{\ensuremath{\mathbbm{R}}}
\def\Z{\ensuremath{\mathbbm{Z}}}

\def\Q{\ensuremath{\mathbbm{Q}}}
\def\C{\ensuremath{\mathbbm{C}}}
\def\F{\ensuremath{\mathbbm{F}}}
\def\K{\ensuremath{\mathbbm{K}}}

% le \fixme est pratique pour marquer les endroits �
% corriger ult�rieurement dans la th�se (�crit en gras
% on le trouve facilement sur le papier, et par ailleurs
% ou avec la commande unix :
% find . -name \*.tex -exec grep '\\fixme' {} \; -print
\def\fixme{{\bf FIXME: }}

\def\cad{\mbox{i.e.}}
\def\cf{{cf.}}
\def\ie{{\it i.e.}}


%------ quelques commandes de formatage de pages / paragraphes ------
\newcommand{\DS}[1]{\displaystyle{#1}}
\newcommand{\bsloppy}{\begin{sloppypar}}
\newcommand{\esloppy}{\end{sloppypar}}
\newcommand{\msaut}{\vspace*{-0.1cm}}
\newcommand{\gsaut}{\vspace*{1.cm}}
\newcommand{\saut}{\vspace*{.5cm}}
\newcommand{\psaut}{\vspace*{.2cm}}
\newcommand{\ppsaut}{\vspace*{.1cm}}
\newcommand{\malinea}{\hspace*{-2cm}}
\newcommand{\alinea}{\hspace*{2cm}}
\newcommand{\palinea}{\hspace*{1cm}}
\newcommand{\ppalinea}{\hspace*{0.5cm}}
\newcommand{\psalinea}{\hspace*{0.2cm}}
\newcommand{\build}[3]{\mathrel{\mathop{\kern 0pt#1}\limits_{#2}^{#3}}}
\newcommand{\Accolade}[1]{\left\{\begin{array}{l} #1 \end{array}\right. }
\newcommand{\Entrepar}[1]{\left( \begin{array}{c}\hspace*{-0.2cm} #1
\hspace*{-0.2cm}\end{array}\right) }
\newcommand{\Entreacc}[1]{\left\{ \begin{array}{c}\hspace*{-0.2cm} #1
      \hspace*{-0.2cm}\end{array}\right\} }

%-------------- quelques "shortcuts" pratiques ...  ----------------
% \renewcommand{\cf}{{\sl cf.~}}
\newcommand{\cffig}[1]{(\cf~figure~\ref{#1})}
\newcommand{\cfequ}[1]{(\cf~quation~\eqref{#1})}
\newcommand{\cfpar}[1]{(\cf~paragraphe~\ref{#1})}
\newcommand{\etc}{{etc.}}

%--------- pour les citations ( la place de \citation) ------------
\newcommand{\citat}[2]{
\begin{tabular}{p{5.5cm}p{9cm}}
 & ``{\small {\sl #1}}''\\
 &\vspace*{0.5mm} {\scriptsize #2}
\end{tabular} }



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%  PAGE LAYOUT                                   %%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


\topmargin -13mm
\headheight 8mm
\headsep 5mm
\footskip 10mm
\columnsep 6mm
\columnseprule 0pt

\sloppy
%\parindent 3em
%\leftmargini 2em
%\leftmargin\leftmargini
%\leftmarginv .5em
%\leftmarginvi .5em


\if@twoside
\setlength{\oddsidemargin}{0.55cm}
\setlength{\evensidemargin}{0cm} 
\else
\oddsidemargin  0.5cm  
\evensidemargin 0.5cm  
\fi

\evensidemargin 5mm
%\marginparwidth 1.5cm   %   Width of marginal notes.
\textwidth      16cm  
%\voffset        -1.0cm  % Decalage vertical vers le haut
\textheight     24cm


% on d�termine le nombre de flottants autoris�s par page,
\setcounter{totalnumber}{6} 
\renewcommand{\floatpagefraction}{.7}
\renewcommand{\topfraction}{1.0}
\renewcommand{\bottomfraction}{1.0}
\renewcommand{\textfraction}{0.00}


\setlength{\parindent}{0.5cm} % indent au debut d'un paragraph
\setlength{\parskip}{0mm}   % distance entre paragraphes

% \RequirePackage{epsfig}
\if@draft
% \psfull % pour garder les images quand meme
\def\baselinestretch{1.62} %% double interligne en 11pt
\else
\def\baselinestretch{1.4}  %% Interligne
\fi


% The `\flushbottom' declaration makes all text pages the same height,
% adding extra vertical space when necessary to fill out the page.
%    This is the standard if twocolumn mode is selected.
\flushbottom

% on commence en chiffres romains jusqu'a \mainmatter
\pagenumbering{roman} 



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%  Style french                                  %%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\RequirePackage[english]{babel}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%  English Language Settings                     %%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\RequirePackage[english]{babel}

\nonfrenchspacing

\def\acknowledgmentsname{Acknowledgements}
\def\introductionname{Introduction}
\def\conclusionname{Conclusion}
\def\myabstractname{Abstract}
\def\resumename{Summary}

% Automatically generated document headings
\addto\captionsenglish{
  \def\contentsname{Table of Contents}
  \def\refname{References}
  \def\bibname{References}
  \def\listfigurename{List of Figures}
  \def\listtablename{List of Tables}
  \def\indexname{Index}
  \def\seename{\emph{see}}
  \def\seealsoname{\emph{see also}}
  \def\figurename{Figure}
  \def\tablename{Table}
  \def\chaptername{CHAPTER}
  \def\appendixname{Appendix}
  \def\partname{Part}
}

% English cross-reference wording
\def\reftextfaceafter{on the following facing page}
\def\reftextfacebefore{on the preceding facing page}
\def\reftextafter{on the following page}
\def\reftextbefore{on the preceding page}
\def\reftextcurrent{on the current page}
\def\reftextfaraway#1{page~\pageref{#1}}

\ifx\ier\undefined\def\ier{st}\fi

\def\note#1{\footnote{---~#1}}

\def\L#1{\ensuremath{{\cal {L}}^{#1}}}
\def\Linf{\ensuremath{{\cal {L}}^{\infty}\,}}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% fancyhdrs
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

 \RequirePackage{fancyhdr}
 \pagestyle{fancy}
 \renewcommand{\headrulewidth}{0pt}
 \fancyhf{} 
 \fancyhead[L]{\begin{boxedminipage}{16.2cm}
               \small EMP
               \end{boxedminipage}}
 \fancyfoot[c]{\thepage}


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%  Chapitre                                      %%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\renewcommand\cleardoublepage{%
% On desire, dans le cas du recto-verso, si la page de
% gauche n'a pas de texte, d'enlever le style 
% (le haut et le bas de la page) 
\clearpage
\if@twoside
  \ifodd\c@page
  \else
    \hbox{}\thispagestyle{empty}
  \fi
\fi 
}


%\if@style@chapOrdinal
%   \renewcommand{\ps@plain}{%
%     \renewcommand{\@evenhead}{}%
%     \renewcommand{\@oddhead}{}%
%     \renewcommand{\@evenfoot}{\hfill\textrm{\thepage}\hfill}%}
%     \renewcommand{\@oddfoot}{\@evenfoot}}

\def\@Fch{\def\thechapter{}{\ifcase\value{chapter}\or I\or II\or
      III\or IV\or V\or VI\or VII\or VIII\or IX\or X\fi}}


\def\@makechapterhead#1{             % Heading for \chapter command
    \thispagestyle{empty}
        
    
    
    \vspace*{1cm}                     % Space at top of text page.
    { \parindent 0pt \raggedright 
      \ifnum \c@secnumdepth >\m@ne     % IF secnumdepth > -1 THEN
                                %\large\bf \@chapapp{} \thechapter % Print 'Chapter' and number.
         \setlength{\fboxrule}{.7mm}
         \setlength{\fboxsep}{4mm}
         \centering
         \begin{boxedminipage}{7cm}       
           \centering \LARGE \bfseries\chaptername\protect\space\@Fch
         \end{boxedminipage} 
      
      
      \typeout{----------> \@chapapp\space #1.}
      \par 
      \vskip 30pt \fi                  % Space between number and title.
      
      \parindent \z@ \raggedright \normalfont
        
        \interlinepenalty\@M
        \centering\LARGE \bfseries \MakeUppercase{#1}\par\nobreak
        \vskip 30\p@                         
    }
 }
%%%%%%%%%%%%%%%

\setcounter{secnumdepth}{3}   % le num�ro du subsubsection   
\setcounter{tocdepth}{3}      % ajouter le subsubsection au TOC

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% caption %%% ATTENTION CE N'est PAS forcement support� par toutes les
% distrib LateX 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\RequirePackage{caption2}


\captionstyle{centerlast}


\renewcommand\captionfont{\footnotesize}
\renewcommand\captionlabelfont{\bfseries\itshape}
\setcaptionmargin{\leftmargini}
%\setlength\captionindent{\parindent}
\renewcommand\captionlabeldelim{~---}
\onelinecaptionstrue
\setcaptionwidth{12.9999cm}



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% varioref
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\RequirePackage{varioref}

\def\reftextfaceafter {\`a la page \reftextvario{ci-contre}{suivante}}
\def\reftextfacebefore{\`a la page \reftextvario{pr\'ec\'edente}{ci-contre}}
\def\reftextafter     {\`a la page suivante}
\def\reftextbefore    {\`a la page pr\'ec\'edente}
\def\reftextcurrent   {de la pr\'esente page}
\def\reftextfaraway#1{page~\pageref{#1}}

\vrefwarning


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% PARstart (comme dans le style IEEE)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\def\PARstart#1#2{\begingroup\def\par{\endgraf\endgroup\lineskiplimit=0pt}
    \setbox2=\hbox{\uppercase{#2} }\newdimen\tmpht \tmpht \ht2
    \advance\tmpht by \baselineskip\font\hhuge=cmr10 at \tmpht
    \setbox1=\hbox{{\hhuge #1}}
    \count7=\tmpht \count8=\ht1\divide\count8 by 1000 \divide\count7 by\count8
    \tmpht=.001\tmpht\multiply\tmpht by \count7\font\hhuge=cmr10 at \tmpht
    \setbox1=\hbox{{\hhuge #1}} \noindent \hangindent1.05\wd1
    \hangafter=-2 {\hskip-\hangindent \lower1\ht1\hbox{\raise1.0\ht2\copy1}%
    \kern-0\wd1}\copy2\lineskiplimit=-1000pt}

\if@draft\def\PARstart#1#2{#1#2}\fi % if draft, disable it





%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%  Remerciements, R�sum�, Abstract, Intro, Conclu, Biblio %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\newcommand{\Remerciements}[1]{%
  \chapter*{#1}
  \addcontentsline{toc}{chapter}{#1}
}
\newcommand{\Introduction}[1]{%
  %\chapter*{#1}
  \addcontentsline{toc}{chapter}{#1}
}
\newcommand{\Conclusion}[1]{%
  \chapter*{#1}
  \addcontentsline{toc}{chapter}{#1}
}
\newcommand{\Abstract}[1]{%
  \chapter*{#1}
  \addcontentsline{toc}{chapter}{#1}
}
\newcommand{\Resume}[1]{%
  \chapter*{#1}
  \addcontentsline{toc}{chapter}{#1}
}
\newcommand{\Notations}[1]{%
  \chapter*{#1}
  \addcontentsline{toc}{chapter}{#1}
}
\newcommand{\Abreviations}[1]{%
  \chapter*{#1}
  \addcontentsline{toc}{chapter}{#1}
}
\newcommand{\ListeFigures}[1]{%
  \cleardoublepage
  \addcontentsline{toc}{chapter}{#1}
  \listoffigures
}
\newcommand{\ListeTables}[1]{%
  \cleardoublepage
  \addcontentsline{toc}{chapter}{#1}
  \listoftables
}
\newcommand{\Bibliography}[1]{%
  \cleardoublepage
  \addcontentsline{toc}{chapter}{\bibname}
  \bibliography{#1}
}


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%  ChapterAbstract                               %%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\newcommand{\@chapterabstract@hook}{}
\newenvironment{ChapterAbstract}%
{%
  \@chapterabstract@hook
  \vspace*{\stretch{1}} 
  }
{% 
  \vspace*{\stretch{2}}
  \newpage
  }


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%  Page de Signatures                            %%
%%  param�tres : Nom de l'universit�,             %%
%%               Pr�sident de l'universit�        %%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\newcommand{\PageSignatures}[2]{%
  % exemple (RennesI) : 
  % \PageSignatures{l'Universit� de Rennes~I}{Patrick NAVATTE}
  \cleardoublepage
  \thispagestyle{empty}
  {
    \Large
    \vspace*{-2cm}
    \hspace{-2.5cm}
    \begin{minipage}[t]{0.5\textwidth}
      \begin{center}
        APPROVED~:\\[2cm]
        Thesis Supervisor     
      \end{center} 
    \end{minipage}%
    \hspace{2cm}
    \begin{minipage}[t]{0.5\textwidth}
      \begin{center}
        VU~:\\[2cm]
        \mbox{Head of the Doctoral School}
      \end{center}
    \end{minipage}


    \vspace*{\stretch{2}}
    \begin{center}
      \begin{minipage}[t]{0.8\textwidth}    
        APPROVED FOR DEFENSE\\[0.5cm]
        Date:\\[0.5cm]
        President of #1
      \end{minipage}
      
      \vspace*{\stretch{1}}

      #2

      \vspace*{\stretch{3}}

      \begin{minipage}[t]{0.8\textwidth}    
        APPROVED FOR PUBLICATION AFTER DEFENSE~:\\[0.5cm]
        President of the Examination Committee,
      \end{minipage}
    \end{center}  
    \vspace*{\stretch{2}}
    }
  }
  
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%  ThesisDedication                              %%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\newcommand{\@dedication@hook}{}
\newenvironment{ThesisDedication}{%
  \cleardoublepage
  \@dedication@hook
  \@mkboth{}{}
  \thispagestyle{plain}
  \vglue0pt plus.5fil
  \fontfamily{\sfdefault}\fontseries{m}\fontshape{sl}\selectfont
  \begin{flushright}
    }%
  {%
  \end{flushright}
  \vglue0pt plus1fil\cleardoublepage
  }


\endinput

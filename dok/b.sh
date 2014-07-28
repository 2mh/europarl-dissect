#!/bin/sh
fileName=$(echo $(echo CL*tex) | sed -e 's|\.tex||g')
pdflatex ${fileName}.tex
bibtex ${fileName}.aux
makeindex ${fileName}.glo -s ${filenNme}.ist -t ${fileName}.glg -o ${fileName}.gls
pdflatex ${fileName}.tex
pdflatex ${fileName}.tex
evince ${fileName}.pdf &

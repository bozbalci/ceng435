#!/usr/bin/env bash

pushd .
cd part_two/report/
pdflatex report.tex
pdflatex report.tex  # twice for indexing stuff
cp report.pdf ../../TP_Part2_82.pdf
popd

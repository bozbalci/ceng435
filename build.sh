#!/usr/bin/env bash

pushd .
cd part_one/report/
pdflatex report.tex
pdflatex report.tex  # twice for indexing stuff
cp report.pdf ../../TP_Part1_82.pdf
popd

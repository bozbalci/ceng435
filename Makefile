dist:
	./build.sh
	tar --exclude-vcs-ignores -cvzf TP_Part1_82.tar.gz part_one

distclean:
	rm -f *.tar.gz *.pdf

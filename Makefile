dist:
	./build.sh
	tar --exclude-vcs-ignores -cvzf TP_Part2_82.tar.gz part_two

distclean:
	rm -f *.tar.gz *.pdf

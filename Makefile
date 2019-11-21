dist:
	tar --exclude-vcs-ignores -cvzf TP_Part_1_82.tar.gz part_one

distclean:
	rm -f *.tar.gz

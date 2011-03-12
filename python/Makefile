build: extension
	python setup.py build

check:
	sudo python -m unittest discover -v -s evemu

clean:
	sudo rm -rf build
	sudo rm -rf _trial_temp
	sudo find . -name "*.pyc" -exec rm {} \;

clean-parent:
	cd ../; make clean-am && make distclean-am

clean-parent-misc:
	cd ../; sudo rm -rf Makefile Makefile.in aclocal.m4 autom4te.cache/ \
	config-aux/ config.h.in config.log config.status src/.deps/ src/Makefile \
	src/Makefile.in tools/.deps/ tools/Makefile tools/Makefile.in configure

clean-all: clean clean-parent clean-parent-misc

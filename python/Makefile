build: extension
	python setup.py build

check:
	sudo python -m unittest discover -v -s evemu

clean:
	sudo rm -rf build
	sudo rm -rf _trial_temp
	sudo find . -name "*.pyc" -exec rm {} \;
	cd ../; make clean


SRC=./src

lint:
	flake8 ${SRC}


pep8:
	pycodestyle --show-source --show-pep8 ${SRC}

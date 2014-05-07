all: test check_convention

clean:
	rm -fr logs.whiteboxtest

test:
	UPSETO_JOIN_PYTHON_NAMESPACES=yes PYTHONPATH=$(PWD)/py python py/strato/whiteboxtest/tests/test.py

check_convention:
	pep8 py --max-line-length=109

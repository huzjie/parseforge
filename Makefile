PY ?= python

all: compile test doctor

compile:
	$(PY) -m compileall -q parseforge

test:
	$(PY) -m unittest discover -s tests -t .

doctor:
	$(PY) -m parseforge.doctor

bench:
	$(PY) -m parseforge.cli bench --config configs/default.yaml

parse:
	$(PY) -m parseforge.cli parse --config configs/default.yaml

serve:
	$(PY) -m parseforge.cli serve --config configs/default.yaml

.PHONY: all compile test doctor bench parse serve

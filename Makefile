THEME_PATH = annotatedocs/themes/annotatedocs
SASS_PATH = $(THEME_PATH)/static/sass

.PHONY: docs


all: test docs

clean:
	rm -rf tests/sampledocs/_build/

css:
	scss -I$(SASS_PATH) \
		$(THEME_PATH)/static/sass/annotate.scss > $(THEME_PATH)/static/css/annotate.css

theme: css

sampledocs: css
	annotatedocs tests/sampledocs

test:
	py.test

docs:
	cd docs/ && make html

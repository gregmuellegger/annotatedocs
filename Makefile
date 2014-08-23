THEME_PATH = annotatedocs/themes/annotatedocs
SASS_PATH = $(THEME_PATH)/static/sass


all: sampledocs

css:
	scss -I$(SASS_PATH) \
		$(THEME_PATH)/static/sass/annotate.scss > $(THEME_PATH)/static/css/annotate.css

theme: css

sampledocs: css
	annotatedocs tests/sampledocs

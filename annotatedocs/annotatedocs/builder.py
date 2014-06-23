from sphinx.writers.html import HTMLTranslator
from sphinx.builders.html import StandaloneHTMLBuilder


class AnnotatedHTMLTranslator(HTMLTranslator):
    def starttag(self, node, tagname, suffix='\n', empty=False, **attributes):
        # Add new attributes to HTML tags here. Like:
        # attributes['data-annotate'] = tagname
        return HTMLTranslator.starttag(self, node, tagname, suffix=suffix, empty=empty, **attributes)


class AnnotatedHTMLBuilder(StandaloneHTMLBuilder):
    def init_translator_class(self):
        self.translator_class = AnnotatedHTMLTranslator

    def assemble_doctree(self):
        tree = super(AnnotatedHTMLTranslator, self).assemble_doctree()
        return tree

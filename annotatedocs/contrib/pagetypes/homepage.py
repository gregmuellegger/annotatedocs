import re

from ... import metrics
from ... import Check, PageType, Metric, Hint, Warning
from ...utils import normalize_document_path
from ..metrics.textstats import TextStats


def is_toctree(node):
    # Sphinx will add a 'toctree-wrapper' class to the compound node that it
    # creates to display the toctree.
    return 'toctree-wrapper' in node.attributes.get('classes', [])


def is_part_of_toctree(node):
    current = node
    while current:
        if is_toctree(current):
            return True
        current = current.parent
    return False


class TocPosition(Metric):
    def apply_to_document(self, document):
        before_toc = True
        for node in document.nodeset.all():
            if is_part_of_toctree(node):
                before_toc = False
                node['before_toc'] = False
                node['after_toc'] = False
                node['part_of_toc'] = True
            else:
                node['before_toc'] = before_toc
                node['after_toc'] = not before_toc
                node['part_of_toc'] = False


@metrics.require(TocPosition)
class HasTableOfContents(Check):
    annotation = Warning(
        """
        This page does not contain a table of contents. Please make sure that
        your users get an overview of the available sections in your
        documentation.
        """)

    def check(self, nodeset, document):
        toctrees = nodeset.filter(part_of_toc=True)
        if len(toctrees) == 0:
            # Add annotation if there is no toctree directive used.
            document.annotate(self.annotation)


@metrics.require(TextStats, TocPosition)
class HasIntroduction(Check):
    annotation = Warning(
        """
        You should include a reasonable introductionary paragraph on your
        homepage. Your users want to know what your project is about.
        """)

    def check(self, nodeset, document):
        # There is no toc on the document. So leave this check.
        if nodeset.filter(part_of_toc=True).count() == 0:
            return

        paragraphs = nodeset.filter(before_toc=True, sentence_count__exists=True)
        sentences = sum(map(lambda p: p['sentence_count'], paragraphs))

        if sentences < 4:
            document.annotate(self.annotation)


@metrics.require(metrics.NodeType, TocPosition)
class NoContentAfterToc(Check):
    annotation = Hint(
        """
        You should not have too much content after the table of content. Your
        users might miss out on the information listed here. So make sure to
        provide it in a more prominent place.
        """)

    def check(self, nodeset, document):
        after_toc = nodeset.filter(after_toc=True)
        if len(after_toc) > 0:
            after_toc.filter(type="paragraph").annotate(self.annotation)


class Homepage(PageType):
    checks = [
        HasTableOfContents,
        HasIntroduction,
        NoContentAfterToc,
    ]

    name_regex = re.compile("^(index(page|[_.][a-z]{2})?)$")

    def match(self, document):
        name = normalize_document_path(document.name)
        if name == "index":
            return 1
        if self.name_regex.search(name):
            return 0.8
        return 0

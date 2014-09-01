from __future__ import division
import re

from ... import Check, PageType, Hint, metrics
from ...utils import normalize_document_path


__all__ = ('InstallationGuide',)


@metrics.require(metrics.NodeType)
class HasCodeListing(Check):
    """
    Make sure that the page has at least one code listing. Otherwise there is
    probably no command included in the page that explains how to install the
    software via package manager etc.
    """

    annotation = Hint(
        """
        This installation guide does not contain a single code block. Make sure
        that you have copy & pastable examples ready on how to install the
        program.
        """)

    def limit(self, nodeset):
        return nodeset.filter(type='literal_block')

    def check(self, nodeset, document):
        if nodeset.count() == 0:
            document.annotate(self.annotation)


class HasNextLink(Check):
    """
    Make sure that the page has a 'what comes next' section with a link to
    another internal document.
    """


class HasRequirements(Check):
    """
    Make sure the installation guide has a section about the requirements for
    this project.
    """


class LinkToRequirements(Check):
    """
    If the page has a section about requirements, make sure that it contains
    links to external sources (the requirements homepages).
    """


class InstallationGuide(PageType):
    name = 'installation guide'

    checks = [
        HasCodeListing,
        HasRequirements,
        LinkToRequirements,
        HasNextLink,
    ]

    name_regex = re.compile(r'''
        (^|/)
        (
            # Only catch `install`, `installing`, `installation`. All other
            # words starting with `install` shouldn't be catched, like
            # `installer`, `installed` etc.

            .*?
            install(ing|ation)?
            # After the `installation` word, there must not come a letter, or
            # the filename ends.
            ([^a-z]+.*)?
        )
        (/|$)
    ''', re.VERBOSE)

    def match(self, document):
        name = normalize_document_path(document.name)
        if self.name_regex.match(name):
            return 0.8
        return 0

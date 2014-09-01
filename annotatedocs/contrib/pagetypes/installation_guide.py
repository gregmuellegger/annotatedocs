from __future__ import division
import re

from ... import Check, PageType, Hint, metrics
from ...utils import normalize_document_path
from ..metrics.references import References
from ..metrics.sectiontitle import SectionTitleContainsKeywords


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


class DependenciesSection(SectionTitleContainsKeywords):
    flag_name = 'is_dependency_section'
    keywords = (
        'require',
        'requirements',
        'dependencies',
        'dependency',
    )


@metrics.require(DependenciesSection)
class HasDependencies(Check):
    """
    Make sure the installation guide has a section about the requirements for
    this project.
    """

    annotation = Hint(
        """
        Seems like there is no section about which requirments this project
        depends on. Consider adding a specific section on this topic since your
        users usually want to be aware of what depnencies need to be satisfied
        before installting this project.
        """)

    def limit(self, nodeset):
        return nodeset.filter(is_dependency_section=True)

    def check(self, nodeset, document):
        if nodeset.count() == 0:
            document.annotate(self.annotation)


@metrics.require(
    DependenciesSection,
    References)
class LinkToDependencies(Check):
    """
    If the page has a section about requirements, make sure that it contains
    links to external sources (the requirements homepages).
    """

    annotation = Hint(
        """
        This section about the dependencies does not contain a link to
        URL outside of this documentation. If you list dependencies make sure
        that you also supply a link to their project pages.
        """)

    def limit(self, nodeset):
        return nodeset.filter(is_dependency_section=True)

    def check(self, nodeset, document):
        for section in nodeset:
            external_refs = section.nodeset.filter(is_external_ref=True)
            if external_refs.count() == 0:
                section.annotate(self.annotation)


@metrics.require(metrics.NodeType)
class HasNextLink(Check):
    """
    Make sure that the page has a 'what comes next' section with a link to
    another internal document.
    """

    annotation = Hint(
        """
        You don't link to another page in the documentation in this last
        section. Make sure that the users knows where to go next after
        completing this installation guide. Consider including a "What to read
        next" link.
        """)

    def limit(self, nodeset):
        return nodeset.filter(type='section')

    def check(self, nodeset, document):
        last_section = nodeset.last()
        if last_section:
            internal_refs = last_section.nodeset.filter(is_internal_ref=True)
            if internal_refs.count() == 0:
                last_section.annotate(self.annotation)


class InstallationGuide(PageType):
    name = 'installation guide'

    checks = [
        HasCodeListing,
        HasDependencies,
        LinkToDependencies,
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

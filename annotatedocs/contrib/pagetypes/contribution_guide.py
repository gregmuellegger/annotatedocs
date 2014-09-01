import re

from ... import Check, Hint, PageType, metrics
from ...utils import normalize_document_path
from ..metrics.emailaddress import EmailAddress
from ..metrics.references import References
from ..metrics.sectiontitle import SectionTitleContainsKeywords
from ..metrics.stemmer import Stemmer
from ..metrics.twitterusername import TwitterUsername


__all__ = ('ContributionGuide',)


class ReportIssueSection(SectionTitleContainsKeywords):
    """
    Set `is_report_issue_section` flag if the section is about reporting bugs.
    """

    flag_name = 'is_report_issue_section'
    keywords = (
        'report',
        'issues',
        'bugs',
        'issuetracker',
        'bugtracker',
    )


@metrics.require(Stemmer, TwitterUsername, EmailAddress)
class HasContactInformation(Check):
    """
    Check if the page contains information about how to contact the authors.

    It should either include a email address, twitter nickname, IRC channel or
    a link to a Mailinglist.
    """

    annotation = Hint(
        """
        There is no contact information included. Please either mention if you
        are using a mailing list or have a link ready to an IRC channel where
        users can ask question. Links to a twitter account or an email address
        might are not as good but better than no concat information.
        """)

    mailing_list_keywords = (
        'mailinglist',
    )

    def __init__(self, *args, **kwargs):
        super(HasContactInformation, self).__init__(*args, **kwargs)
        self.stemmed_keywords = set(Stemmer.stem(
            ' '.join(self.mailing_list_keywords)))

    def check(self, nodeset, document):
        twitter_usernames = nodeset.filter(twitter_username__exists=True)
        if twitter_usernames.count():
            return
        email_addresses = nodeset.filter(email_address__exists=True)
        if email_addresses.count():
            return
        mentions_mailinglist = nodeset.filter(stemmed_words__exists=True)
        mentions_mailinglist = mentions_mailinglist.filter(
            lambda node: set(node['stemmed_words']) & self.stemmed_keywords)
        if mentions_mailinglist.count():
            return
        document.annotate(self.annotation)


@metrics.require(ReportIssueSection)
class HasReportIssueSection(Check):
    """
    Make sure that the page has section that talks about how to report a bug.
    """

    annotation = Hint(
        """
        It seems like there is no section about how to create a bug report.
        Consider creating a seperate section for this in order to have a go-to
        place for your users when they found a bug.
        """)

    def limit(self, nodeset):
        return nodeset.filter(is_report_issue_section=True)

    def check(self, nodeset, document):
        if nodeset.count() == 0:
            document.annotate(self.annotation)


@metrics.require(References)
class HasLinkToBugTracker(Check):
    """
    Make sure that the page has a link to the projects bug tracker.
    """

    annotation = Hint(
        """
        There is no link to to a bugtracker on the page. Make sure that your
        users know where they can report a bug.
        """)

    keywords = (
        'issue',
        'bug',
        'tracker',
        'report',
    )

    def limit(self, nodeset):
        """
        Return http/https links that are part of the report issue section.
        """
        sections = nodeset.filter(is_report_issue_section=True).subset()
        links = sections.filter(uri_scheme__exists=True)
        links = links.filter(
            lambda node: node['uri_scheme'].lower() in ['http', 'https'])
        return links

    def check(self, nodeset, document):
        for node in nodeset:
            uri = node['refuri'].lower()
            text = node.astext().lower()
            for keyword in self.keywords:
                if keyword in uri:
                    return
                if keyword in text:
                    return
        # There was no reference that contained any of the keywords, either in
        # the URI or in the link text.
        document.annotate(self.annotation)


class ContributionGuide(PageType):
    name = 'contribution guide'

    checks = [
        HasContactInformation,
        HasReportIssueSection,
        HasLinkToBugTracker,
    ]

    name_regex = re.compile(
        r'''
        (^|/)
        (contribut(?![eo]rs?|ed))
        # Only catch the filename if the `contribute` is not part of a
        # directory name. We usually would like to catch all parts of the
        # contribution information if it's part of a directory, however we are
        # not able to fit those pieces together into one big check. So we limit
        # ourselves to single-document contribution guides.
        [^/]*$
        ''', re.VERBOSE)

    def match(self, document):
        name = normalize_document_path(document.name)
        if self.name_regex.search(name):
            return 0.8
        return 0

from ... import Check, PageType, metrics


__all__ = ('ContributionGuide',)


class HasLinkToRepository(Check):
    """
    Make sure that the page has a link to the source code repository.
    """


class HasContactInformation(Check):
    """
    Check if the page contains information about how to contact the authors.

    It should either include a email address, twitter nickname, IRC channel or
    a link to a Mailinglist.
    """


class ContributionGuide(PageType):
    name = 'contribution guide'

    checks = [
        HasLinkToRepository,
        HasContactInformation,
    ]

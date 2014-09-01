from __future__ import absolute_import
import pep8

from ... import Metric, NodeType, metrics


__all__ = ('PEP8Metric',)


class MetricReport(pep8.BaseReport):
    def __init__(self, *args, **kwargs):
        self.errors = []
        super(MetricReport, self).__init__(*args, **kwargs)

    def error(self, line_number, offset, text, check):
        self.errors.append({
            'line_number': line_number,
            'offset': offset,
            'errorno': text[:4],
            'text': text[5:],
        })
        super(MetricReport, self).error(line_number, offset, text, check)


@metrics.require(NodeType)
class PEP8Metric(Metric):
    """
    Will add pep8 error and warnings to the node.

    You can access ``node['pep8_warnings']`` to retrieve all gathered warnings
    and errors. These are stored as dicts with the following keys:

    ``'line_number'``
        The line in which the warning was detected.

    ``'offset'``
        The column in which the warning was detected.

    ``'errorno'``
        The pep8 error/warning number like E122, W292, etc.

    ``'text'``
        The error/warning message as text.
    """

    report_class = MetricReport

    def limit(self, nodeset):
        return nodeset.filter(type='literal_block', language='python')

    def get_report(self):
        options = pep8.StyleGuide(quiet=True).options
        return self.report_class(options)

    def apply(self, node, document):
        code = node.astext()

        # We need to add newlines to the end of each line. That is what the
        # pep8 checker is expecting.
        lines = [line + '\n' for line in code.splitlines()]
        checker = pep8.Checker(
            lines=lines,
            report=self.get_report())
        file_errors = checker.check_all()
        if file_errors:
            errors = sorted(checker.report.errors,
                            key=lambda e: e['line_number'])
            node['pep8_warnings'] = errors

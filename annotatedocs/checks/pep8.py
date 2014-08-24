from . import Check
from ..annotations import Annotation
from ..metrics.pep8 import PEP8Metric


__all__ = ('PEP8Compliance',)


class PEP8Compliance(Check):
    required_metrics = Check.required_metrics + [
        PEP8Metric,
    ]

    # TODO: Implement customizable filtering on Warnings and Errors.

    def limit(self, nodeset):
        return nodeset.filter(pep8_warnings__exists=True)

    def pep8_warning_to_annotation(self, node, warning):
        message = 'Line {line_number}: {errorno} {text}'.format(**warning)
        if warning['errorno'].startswith('E'):
            level = 'warning'
        else:
            level = 'hint'
        return Annotation(
            message,
            level=level,
            title_text=self.get_code_line(node, warning['line_number']))

    def get_code_line(self, node, line_number):
        return node.astext().splitlines()[line_number-1]

    def check(self, nodeset, document):
        for node in nodeset.all():
            for warning in node['pep8_warnings']:
                annotation = self.pep8_warning_to_annotation(node, warning)
                node.annotate(annotation)

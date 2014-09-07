from ... import Check, Annotation, metrics
from ..metrics.pep8 import PEP8Metric


__all__ = ('IsPEP8Compliant',)


@metrics.require(PEP8Metric)
class IsPEP8Compliant(Check):
    # TODO: Implement customizable filtering on Warnings and Errors.

    def limit(self, nodeset):
        return nodeset.filter(pep8_errors__exists=True)

    def pep8_error_to_annotation(self, node, error):
        message = 'Line {line_number}: {errorno} {text}'.format(**error)
        if error['errorno'].startswith('E'):
            level = 'warning'
        else:
            level = 'hint'
        return Annotation(
            message,
            level=level,
            title_text=self.get_code_line(node, error['line_number']))

    def get_code_line(self, node, line_number):
        return node.astext().splitlines()[line_number-1]

    def check(self, nodeset, document):
        for node in nodeset.all():
            for error in node['pep8_errors']:
                annotation = self.pep8_error_to_annotation(node, error)
                node.annotate(annotation)

import docutils
import docutils.parsers.rst


def parse_rst(source, document_name=None):
    """Take ReST source and returns parsed document.

    Specify an optional `document_name` if needed.
    """

    source = source.decode('utf-8')

    settings = docutils.frontend.OptionParser(
        components=(docutils.parsers.rst.Parser,)
    ).get_default_values()
    document = docutils.utils.new_document(document_name, settings)

    parser = docutils.parsers.rst.Parser()
    parser.parse(source, document)
    return document

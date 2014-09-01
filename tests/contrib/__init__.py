from annotatedocs.document import Document

from ..parse import parse_rst


def named_document(name):
    docutils_document = parse_rst("""
Temporary document
==================
    """, document_name=name)

    return Document(
        node=docutils_document,
        bundle=None,
        name=name)

class AnnotationData(object):
    def __init__(self):
        self.data = {}
        self.global_annotations = []

    def init_node(self, node):
        self.data[node] = {}
        for child in node.children:
            self.init_node(child)

        if node.__class__.__name__ == 'document':
            self.add_warning(node, 'You have a document warning.')
        if node.__class__.__name__ == 'paragraph':
            self.add_warning(node, 'This is a paragraph.')

    def add_global_annotation(self, level, message):
        self.global_annotations.append({
            'level': level,
            'message': message,
        })

    def get_global_annotations(self):
        return self.global_annotations

    def add_annotation(self, node, level, message):
        self.data[node].setdefault('annotations', []).append({
            'level': level,
            'message': message,
        })

    def add_hint(self, node, message):
        self.add_annotation(node, 'hint', message)

    def add_warning(self, node, message):
        self.add_annotation(node, 'warning', message)

    def add_document(self, document, name):
        self.init_node(document)
        self[document]['name'] = name

    def __getitem__(self, node):
        return self.data[node]

(function ($) {

    var Annotation = function (opts) {
        this.level = opts.level;
        this.message = opts.message;
        this.title = opts.title;
        this.$element = null;
        this.$annotation = this.render();
    }

    /*
     * Get a list of plain JSON objects (read from the HTML attributes) and
     * return a list of instantiated annotations.
     */
    Annotation.instantiate = function (annotations) {
        return $.map(annotations, function (annotation) {
            return new Annotation(annotation);
        });
    };

    /*
     * Return jQuery object that can be used to represent this annotation in
     * the DOM.
     */
    Annotation.prototype.render = function () {
        var $annotation = $('<div class="annotation" />')
                .addClass('annotation-' + this.level)
                .text(this.message);
        if (this.title) {
            $annotation.attr('title', this.title);
        }
        return $annotation;
    };

    Annotation.prototype.getOrCreateAnnotationsElement = function ($element) {
        var $annotations = $element.find('.annotations:first');
        if ($annotations.length == 0) {
            $annotations = $('<div class="annotations" />');
            $element.append($annotations);
        }
        return $annotations;
    };

    /*
     * Attach the annotation to the given element in the dom. This will
     * create the necessary .annotations div inside the element.
     */
    Annotation.prototype.attach = function ($element) { if (this.$element !==
            null) { throw "Can only attach ones, was already attached to: " +
                this.$element; }

        this.$element = $element;
        var $annotations = this.getOrCreateAnnotationsElement(this.$element);

        if (this.level == 'hint') {
            this.$element.addClass('has-hints');
            $('html').addClass('page-has-hints');
        }
        if (this.level == 'warning') {
            this.$element.addClass('has-warnings');
            $('html').addClass('page-has-warnings');
        }

        $annotations.append(this.$annotation);
    };


    /*
     * A representation of the document's content.
     */
    var Document = function ($element) {
        this.$element = $element;
        this.annotations = [];
        this.documentAnnotations = [];
        return this;
    };

    /*
     * Look for serialized annotations in the DOM and attach them to the
     * elements.
     */
    Document.prototype.init = function () {
        var self = this;
        this.$element.find('[data-annotations]').each(function () {
            var $annotatedElement = $(this);
            var annotations = $annotatedElement.attr('data-annotations');

            annotations = JSON.parse(annotations);
            if (!annotations) {
                return;
            }

            annotations = Annotation.instantiate(annotations);
            $.each(annotations, function (i, annotation) {
                annotation.attach($annotatedElement);
                self.annotations.push(annotation);
            });
        });

        this.$element.find('[data-document-annotations]').each(function () {
            var annotations = $(this).attr('data-document-annotations');
            annotations = JSON.parse(annotations);
            annotations = Annotation.instantiate(annotations);
            $.each(annotations, function (i, annotation) {
                self.addDocumentAnnotation(annotation);
            });
        });
    };

    Document.prototype.getOrCreateDocumentAnnotationsElement = function () {
        var $annotations = this.$element.find('.document-annotations:first');
        if ($annotations.length == 0) {
            $annotations = $('<div class="document-annotations" />');
            this.$element.prepend($annotations);
        }
        return $annotations;
    };

    /*
     * Attach a document annotation.
     */
    Document.prototype.addDocumentAnnotation = function (annotation) {
        var $annotations = this.getOrCreateDocumentAnnotationsElement();
        annotation.attach($annotations);
        this.documentAnnotations.push(annotation);
    };


    $(document).ready(function () {
        // Init toolbox.
        $(document).on('click', "[data-toggle='annotations-head']", function() {
            $("[data-toggle='annotations-toolbox']").toggleClass("shift-up");
        });

        $(document).on('change', ":input[id=show_warnings]", function() {
            $('html').toggleClass('page-hide-warnings', !$(this).is(':checked'));
        });
        $(document).on('change', ":input[id=show_hints]", function() {
            $('html').toggleClass('page-hide-hints', !$(this).is(':checked'));
        });

        var doc = new Document($('[role="main"]'));
        doc.init();
    });

})(jQuery);

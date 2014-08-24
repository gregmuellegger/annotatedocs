$.fn.showAnnotation = function () {
    var getAnnotationTag = function (annotation) {
        var $annotation = $('<div class="annotation" />')
                .addClass('annotation-' + annotation.level)
                .text(annotation.message);
        if (annotation.title) {
            $annotation.attr('title', annotation.title);
        }
        return $annotation
    };

    $(this).each(function () {
        var $self = $(this);

        var annotations = $(this).attr('data-annotations');
        if (!annotations) {
            return;
        }
        annotations = JSON.parse(annotations);

        var $annotations = $self.find('.annotations');
        if ($annotations.length == 0) {
            $annotations = $('<div class="annotations" />').appendTo($self);
        }
        $annotations.empty();

        $.each(annotations, function (i, annotation) {
            if (annotation.level == 'hint') {
                $self.addClass('has-hints');
                $('html').addClass('page-has-hints');
            }
            if (annotation.level == 'warning') {
                $self.addClass('has-warnings');
                $('html').addClass('page-has-warnings');
            }

            var $annotation = getAnnotationTag(annotation);
            $annotations.append($annotation);
        });
    });

    // TODO: Check if there are global annotations somehow differently.
    $('html').addClass('page-has-global-annotations');

    return this;
};

$.fn.addAnnotation  = function (level, message) {
    $(this).each(function () {
        var annotations = $(this).attr('data-annotations');
        if (!annotations) {
            annotations = [];
        } else {
            annotations = JSON.parse(annotations);
        }

        annotations.push({
            level: level,
            message: message
        });

        $(this).attr('data-annotations', JSON.stringify(annotations));
        $(this).showAnnotation();
    });

    return this;
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

    $('[data-annotations]').showAnnotation();
});

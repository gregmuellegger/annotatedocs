$.fn.showAnnotation = function () {
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

            $annotations.append(
                $('<div class="annotation" />')
                    .addClass('annotation-' + annotation.level)
                    .text(annotation.message));
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

$(document).ready(function() {

    // Only show dummy data when we are on the demo page.
    var showDummyData = $('.wy-side-nav-search').text().match(/Sphinx RTD theme demo/);

    if (showDummyData) {
        // Dummy data.
        $('#maaaaath div.math').addAnnotation('warning', 'This equation contains a mathematical contradiction.');
        $('[id="module-test_py_module.test"] dd:first p:first').addAnnotation('hint', 'This sentence does not contain a verb.');
        $('#optional-parameter-args').addAnnotation('hint', 'This paragraph is not very useful.');
        $('#optional-parameter-args').addAnnotation('warning', 'The link inside the paragraph seems dead.');
        $('#sidebar > h2:first').addAnnotation('warning', 'A heading can have warnings as well.');

        var globalMessage = 'Your documentation contains a highly nested structure without having very much content. Think about flattening your structure.';
        $('[role=main]').before(
            $(
                '<div class="global-warnings">' +
                '<div class="annotation annotation-global">' +
                globalMessage +
                '</div>' +
                '</div>'));
    }

});

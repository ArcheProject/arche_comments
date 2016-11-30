

function Comments() {

    this.pure_tpl = $('[data-comments]').clone().html();

    this.load_comments = function() {
        if ($('[data-comments]').length > 0) {
            var request = arche.do_request('./_comments/comments.json');
            request.done(this.render_comments);
        }
    }

    var that = this;
    this.render_comments = function(response) {
        $("[data-comments]").html(that.pure_tpl);
        $("[data-comments]").render(response, that.directive);
        $("[data-comments]").show();
    }

    this.load_comment_form = function(event) {
        event.preventDefault();
        var elem = $(event.currentTarget);
        arche.actionmarker_feedback(elem, true);
        var url = elem.attr('href');
        var request = arche.do_request(url);
        var target = $('[data-comment-form]');
        if (target.length != 1) {
            target = elem;
        }
        request.done(function(response) {
            target.html(response);
            $('[data-add-comment]').hide();
        });
        request.fail(arche.flash_error);
        request.always(function() {
            arche.actionmarker_feedback(elem, false);
            arche.load_flash_messages();
        });
    }

    this.reset_comment_state = function(form_selector) {
        $(form_selector).remove();
        $('[data-add-comment]').show();
    }

    this.directive = {'.comment':
        {'obj<-':
            {
                '.body': 'obj.body',
                '.created': 'obj.created',
                '.author': 'obj.author',
                '.author-img': 'obj.img_tag',
            }
        }
    };


}


$(function () {
    comments = new Comments()
    $('[data-add-comment]').on('click', comments.load_comment_form);
    comments.load_comments();
});

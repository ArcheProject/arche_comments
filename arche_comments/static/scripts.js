

function Comments(url) {
    this.url = url;
    this.pure_tpl = $('[data-comments]').clone().html();

    this.load_comments = function() {
        if ($('[data-comments]').length > 0) {
            var request = arche.do_request(this.url);
            request.done(this.render_comments);
        }
    }

    var that = this;
    this.render_comments = function(response) {
        $("[data-comments]").html(that.pure_tpl);
        $("[data-comments]").render(response, that.directive);
        $("[data-comments]").removeClass('hidden');
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
                '.comment-body': 'obj.body',
                '.created': 'obj.created',
                '.author': 'obj.author',
                '.author-img': 'obj.img_tag',
                '.comment-opts@class+': function(a) {
                    if (a.item.edit === false) return ' hidden';
                },
                'a@href': function(a) {
                    return a.item.path + 'edit';
                },
                '[data-comment]@data-comment': 'obj.uid',
            }
        }
    };
}

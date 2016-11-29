from arche.interfaces import IContent
from arche.utils import generate_slug
from arche.views.base import DefaultAddForm
from arche_comments.interfaces import ICommentsFolder, IComment
from pyramid.httpexceptions import HTTPForbidden, HTTPFound
from pyramid.response import Response
from pyramid.view import view_config

from arche_comments import _


#FIXME: Permission
@view_config(context = IContent, name='_add_comments', renderer='arche:templates/form.pt')
class AddCommentsFolderForm(DefaultAddForm):
    title = _("Enable comments")
    type_name = 'CommentsFolder'

    def save_success(self, appstruct):
        self.flash_messages.add(self.default_success, type="success")
        factory = self.request.content_factories[self.type_name]
        obj = factory(**appstruct)
        name = '_comments'
        if name in self.context:
            raise HTTPForbidden(_("Comments already exit here"))
        self.context[name] = obj
        return HTTPFound(location = self.request.resource_url(self.context))


@view_config(context = ICommentsFolder, name='add', renderer='arche:templates/form.pt')
class AddCommentForm(DefaultAddForm):
    title = _("Add")
    type_name = 'Comment'
    use_ajax = True
    ajax_options = """
        {success:
          function (rText, sText, xhr, form) {
            arche.load_flash_messages();
           }
        }
    """

    def save_success(self, appstruct):
        #self.flash_messages.add(self.default_success, type="success")
        factory = self.request.content_factories[self.type_name]
        obj = factory(**appstruct)
        name = generate_slug(self.context, obj.uid)
        self.context[name] = obj
        return _redirect_or_remove(self)

    def cancel(self, *args):
        return _redirect_or_remove(self)
    cancel_failure = cancel_success = cancel


def _redirect_or_remove(formview):
    if formview.request.is_xhr:
        return Response("""
        <script>
        comments.reset_comment_state({});
        comments.load_comments();
        </script>""".format(formview.formid))
    return HTTPFound(location=formview.request.resource_url(formview.context))

#FIXME: Permission
@view_config(context=ICommentsFolder, name='comments.json', renderer='json')
def comments_json(context, request):
    results = []

    def get_user(obj):
        try:
            return request.root['users'][obj.creator[0]]
        except (KeyError, IndexError):
            pass

    for obj in context.values():
        if IComment.providedBy(obj):
            user = get_user(obj)
            if user:
                author_title = "%s (%s)" % (user.title, user.userid)
                img_tag = request.thumb_tag(user, 'square', direction = 'down')
            else:
                author_title = ''
                img_tag = ''
            item = {
                'body': obj.body,
                'created': request.dt_handler.format_dt(obj.created),
                'author': author_title,
                'img_tag': img_tag,
            }
            results.append(item)
    return results


def includeme(config):
    config.scan(__name__)

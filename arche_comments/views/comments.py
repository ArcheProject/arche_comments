# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from arche.interfaces import IContent
from arche.security import PERM_VIEW
from arche.utils import generate_slug
from arche.views.base import DefaultAddForm
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.view import view_config

from arche_comments import _
from arche_comments.interfaces import IComment
from arche_comments.interfaces import ICommentsFolder
from arche_comments.security import ADD_COMMENT
from arche_comments.security import ENABLE_COMMENTS


@view_config(context = IContent, name='_add_comments',
             permission=ENABLE_COMMENTS,
             renderer='arche:templates/form.pt')
class AddCommentsFolderForm(DefaultAddForm):
    title = _("Create comments section?")
    description = _("You can disable this later on if you wish.")
    type_name = 'CommentsFolder'

    def save_success(self, appstruct):
        self.flash_messages.add(self.default_success, type="success")
        notify_user = appstruct.pop('notify', False)
        factory = self.request.content_factories[self.type_name]
        obj = factory(**appstruct)
        name = '_comments'
        if name in self.context:
            raise HTTPForbidden(_("Comments already exist here"))
        if notify_user:
            obj.notify_userids.add(self.request.authenticated_userid)
        self.context[name] = obj
        return HTTPFound(location = self.request.resource_url(self.context))


@view_config(context = ICommentsFolder, name='add', renderer='arche:templates/form.pt', permission=ADD_COMMENT)
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


@view_config(context=ICommentsFolder,
             name='comments.json',
             renderer='json',
             permission=PERM_VIEW)
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
                try:
                    img_tag = request.thumb_tag(user, 'square', direction = 'down')
                except AttributeError:
                    img_tag = ''
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


@view_config(context=ICommentsFolder, name='_toggle_comments', permission=ENABLE_COMMENTS)
def toggle_comments(context, request):
    enable = request.GET.get('enable') == '1'
    context.enabled = enable
    return HTTPFound(location=request.resource_url(context.__parent__))


def includeme(config):
    config.scan(__name__)

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from arche.interfaces import IContent
from arche.security import PERM_VIEW
from arche.utils import generate_slug
from arche.views.base import BaseView
from arche.views.base import DefaultEditForm
from arche.views.base import DefaultAddForm
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.response import Response
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.traversal import find_interface
from pyramid.view import view_config
from pyramid.view import view_defaults
from repoze.catalog.query import Eq

from arche_comments import _
from arche_comments.interfaces import IComment
from arche_comments.interfaces import ICommentsFolder
from arche_comments.security import ADD_COMMENT
from arche_comments.security import DELETE_COMMENT
from arche_comments.security import EDIT_COMMENT
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
            obj.add_subscribing_userid(self.request.authenticated_userid)
        self.context[name] = obj
        return HTTPFound(location = self.request.resource_url(self.context, anchor='comments'))


@view_config(context = ICommentsFolder, name='add', renderer='arche:templates/form.pt', permission=ADD_COMMENT)
class AddCommentForm(DefaultAddForm):
    title = _("Add")
    type_name = 'Comment'
    use_ajax = True
    formid = "add-comment-form"
    ajax_options = """
        {success:
          function (rText, sText, xhr, form) {
            arche.load_flash_messages();
           }
        }
    """

    @property
    def buttons(self):
        return (self.button_add, self.button_cancel)

    def add_success(self, appstruct):
        factory = self.request.content_factories[self.type_name]
        obj = factory(**appstruct)
        name = generate_slug(self.context, obj.uid)
        self.context[name] = obj
        self.flash_messages.add(_("Added"), type="success")
        return _redirect_or_remove(self)

    def cancel(self, *args):
        return _redirect_or_remove(self)
    cancel_failure = cancel_success = cancel


@view_config(context = IComment, name='edit', renderer='arche:templates/form.pt', permission=NO_PERMISSION_REQUIRED)
class EditCommentForm(DefaultEditForm):
    title = _("Edit")
    type_name = 'Comment'

    def __init__(self, context, request):
        buttons = []
        if request.has_permission(EDIT_COMMENT, context):
            buttons.append(self.button_save)
        if request.has_permission(DELETE_COMMENT, context):
            buttons.append(self.button_delete)
        if not buttons:
            raise HTTPForbidden(_("You're not allowed to edit or delete this comment"))
        buttons.append(self.button_cancel)
        self.buttons = buttons
        super(EditCommentForm, self).__init__(context, request)

    @property
    def formid(self):
        return "edit-comment-%s" % self.context.uid

    def save_success(self, appstruct):
        self.flash_messages.add(_("Updated"), type='success')
        self.context.update(**appstruct)
        return redirect_parent(self.context, self.request)

    def delete_success(self, appstruct):
        self.flash_messages.add(_("Removed"), type='warning')
        redir = redirect_parent(self.context, self.request)
        parent = self.context.__parent__
        del parent[self.context.__name__]
        return redir

    def cancel(self, *args):
        return redirect_parent(self.context, self.request)
    #    return _redirect_or_remove(self)
    cancel_failure = cancel_success = cancel


def _redirect_or_remove(formview):
    if formview.request.is_xhr:
        return Response("""
        <script>
        comments.reset_comment_state('#{}');
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

    query = Eq('type_name', 'Comment') & Eq('path', request.resource_path(context))
    docids = request.root.catalog.query(query, sort_index='created')[1]
    for obj in request.resolve_docids(docids, perm=None):  # Perm already checked
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
                'edit': bool(request.has_permission(DELETE_COMMENT, obj) or request.has_permission(EDIT_COMMENT, obj)),
                'path': request.resource_path(obj),
                'uid': obj.uid,
            }
            results.append(item)
    return results


@view_config(context=ICommentsFolder, name='_toggle_comments', permission=ENABLE_COMMENTS)
def toggle_comments(context, request):
    enable = request.GET.get('enable') == '1'
    context.enabled = enable
    return HTTPFound(location=request.resource_url(context.__parent__))


@view_defaults(context=ICommentsFolder, permission=PERM_VIEW)
class NotificationsView(BaseView):

    @view_config(name='subscribe')
    def subscribe_notifications(self):
        userid = self.request.authenticated_userid
        if not userid:
            raise HTTPUnauthorized(_("You must be logged in"))
        if not self.context.is_subscibing(self.request.authenticated_userid):
            self.context.add_subscribing_userid(userid)
            self.flash_messages.add(_("You will receive email notifications when someone posts something here."))
        else:
            self.flash_messages.add(_("You were already subscribing."))
        return HTTPFound(location=self.request.resource_url(self.context.__parent__))

    @view_config(name='unsubscribe')
    def unsubscribe_notifications(self):
        if not len(self.request.subpath) == 2:
            raise HTTPNotFound()
        userid = self.context.validate(self.request)
        if userid:
            self.context.remove_subscribing_userid(userid)
            self.flash_messages.add(_("Notifications are now turned off."))
        else:
            self.flash_messages.add(_("No subscription found."))
        return HTTPFound(location=self.request.resource_url(self.context.__parent__))


@view_config(context=ICommentsFolder, permission=NO_PERMISSION_REQUIRED)
@view_config(context=IComment, permission=NO_PERMISSION_REQUIRED)
def redirect_parent(context, request):
    """ Redirect to any parent of the CommentsFolder, to the anchor #comments"""
    comments = find_interface(context, ICommentsFolder)
    return HTTPFound(location=request.resource_url(comments.__parent__, anchor='comments'))


def includeme(config):
    config.scan(__name__)

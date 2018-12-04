# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from uuid import uuid4

from BTrees.OOBTree import OOBTree
from arche.api import Base
from arche.api import ContextACLMixin
from arche.api import Folder
from arche.api import LocalRolesMixin
from arche.interfaces import IObjectAddedEvent
from arche.security import ROLE_OWNER
from pyramid.security import Deny
from pyramid.security import Everyone
from zope.interface import implementer

from arche_comments import _
from arche_comments.interfaces import ICommentsFolder
from arche_comments.security import ADD_COMMENT
from arche_comments.security import ENABLE_COMMENTS


@implementer(ICommentsFolder)
class CommentsFolder(Base, Folder, ContextACLMixin, LocalRolesMixin):
    """ Container for comments.
    """
    nav_visible = False
    listing_visible = True
    search_visible = True
    title = _("Comments")
    type_name = "CommentsFolder"
    type_title = _("Comments folder")
    type_description = _("Container for comments.")
    add_permission = ENABLE_COMMENTS
    enabled = False

    def is_subscibing(self, userid):
        return userid in self.subscribers

    def get_subscribers(self):
        return self.subscribers.keys()

    def add_subscribing_userid(self, userid):
        if userid not in self.subscribers:
            self.subscribers[userid] = unicode(uuid4())
        return self.subscribers[userid]

    def remove_subscribing_userid(self, userid):
        self.subscribers.pop(userid, None)

    def subscribe_url(self, request):
        userid = request.authenticated_userid
        if userid not in self.subscribers:
            return request.resource_url(self, 'subscribe')

    def unsubscribe_url(self, request, userid=None):
        userid = userid and userid or request.authenticated_userid
        if userid in self.subscribers:
            return request.resource_url(self, 'unsubscribe', userid, self.subscribers[userid])

    def validate(self, request):
        """ Fetch userid if token is valid. """
        if len(request.subpath) != 2:
            return
        userid = request.subpath[0]
        token = request.subpath[1]
        if self.subscribers.get(userid, object()) == token:
            return userid

    @property
    def subscribers(self):
        if not hasattr(self, '_subscribers'):
            self._subscribers = OOBTree()
        return self._subscribers

    @property
    def __acl__(self):
        """ Return the parents ACL and inject deny in case comments are closed. """
        acl = _find_closest_parent_attr(self, '__acl__', [])
        if not self.enabled:
            acl.insert(0, (Deny, Everyone, ADD_COMMENT))
        return acl


def _find_closest_parent_attr(context, attr, default=None):
    parent = context.__parent__
    while parent:
        if hasattr(parent, attr):
            return getattr(context, attr)
        parent = parent.__parent__
    return default


def add_owner_from_parent(context, event):
    try:
        userids = tuple(context.__parent__.local_roles.get_any_local_with(ROLE_OWNER))
    except AttributeError:
        return
    for userid in userids:
        context.local_roles.add(userid, ROLE_OWNER, event=False)
    if userids:
        context.local_roles.send_event()


def includeme(config):
    config.add_content_factory(CommentsFolder)
    config.add_subscriber(add_owner_from_parent, [ICommentsFolder, IObjectAddedEvent])

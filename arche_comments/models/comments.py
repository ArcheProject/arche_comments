# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from BTrees.OOBTree import OOSet
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

    @property
    def notify_userids(self):
        if not hasattr(self, '_notify_userids'):
            self._notify_userids = OOSet()
        return self._notify_userids

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

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from arche.interfaces import IObjectAddedEvent
from pyramid.renderers import render
from pyramid.threadlocal import get_current_request
from pyramid.traversal import find_interface

from arche_comments import _
from arche_comments.interfaces import IComment
from arche_comments.interfaces import ICommentsFolder


def notify_subscribing_users(context, event):
    """ Send an email to any user subscribing to this folder. """
    request = get_current_request()
    comments = find_interface(context, ICommentsFolder)
    subject = _("Notification")
    comments_context = comments.__parent__
    for userid in comments.get_subscribers():
        if userid == request.authenticated_userid:
            continue
        try:
            user = request.root['users'][userid]
        except KeyError:
            continue
        if not user.email:
            continue
        try:
            comment_user = request.root['users'][context.creator[0]]
        except (KeyError, IndexError):
            comment_user = None
        values = dict(
            user=user,
            body=context.body,
            comment_context=comments_context,
            comment_user=comment_user,
            unsubscribe_url=comments.unsubscribe_url(request, userid),
        )
        body = render('arche_comments:templates/notification_email.pt', values, request=request)
        request.send_email(subject, [user.email], body)


def includeme(config):
    config.add_subscriber(notify_subscribing_users, [IComment, IObjectAddedEvent])

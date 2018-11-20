from __future__ import unicode_literals

from arche.portlets import PortletType
from deform_autoneed import need_lib
from pyramid.renderers import render

from arche_comments import _
from arche_comments.schemas.portlet import CommentsPortletSchema
from arche_comments.security import ADD_COMMENT
from arche_comments.security import ENABLE_COMMENTS


class CommentsPortlet(PortletType):
    name = "comments"
    title = _("Comments")
    tpl = "arche_comments:templates/portlet.pt"
    schema_factory = CommentsPortletSchema

    def render(self, context, request, view, **kwargs):
        comments = context.get('_comments', None)
        allowed_types = self.portlet.settings.get('allowed_types', ())
        if not allowed_types:
            return
        if getattr(context, 'type_name', '') not in allowed_types:
            return
        can_toggle = request.has_permission(ENABLE_COMMENTS, context)
        if comments:
            need_lib('deform')
            can_add = request.has_permission(ADD_COMMENT, comments)
        else:
            can_add = False
        return render(self.tpl,
                      {'portlet': self.portlet,
                       'comments': comments,
                       'view': view,
                       'can_toggle': can_toggle,
                       'can_add': can_add},
                      request=request)


def includeme(config):
    config.add_portlet(CommentsPortlet)

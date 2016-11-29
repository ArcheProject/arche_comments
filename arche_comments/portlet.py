from __future__ import unicode_literals

from arche.portlets import PortletType
from deform_autoneed import need_lib
from pyramid.renderers import render

from arche_comments import _


class CommentsPortlet(PortletType):
    name = "comments"
    title = _("Comments")
    tpl = "arche_comments:templates/portlet.pt"

    def render(self, context, request, view, **kwargs):
        comments = context.get('_comments', None)
        if comments:
            need_lib('deform')
        return render(self.tpl,
                      {'portlet': self.portlet,
                       'comments': comments,
                       'view': view},
                      request=request)


def includeme(config):
    config.add_portlet(CommentsPortlet)

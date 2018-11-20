# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import colander
import deform
from arche.interfaces import IIndexedContent

from arche_comments import _


@colander.deferred
def limit_types_widget(node, kw):
    request = kw['request']
    values = []
    for fact in request.content_factories.values():
        if IIndexedContent.implementedBy(fact):
            values.append((fact.type_name, getattr(fact, 'type_title', fact.__class__.__name__)))
    return deform.widget.CheckboxChoiceWidget(values=values)


class CommentsPortletSchema(colander.Schema):
    allowed_types = colander.SchemaNode(
        colander.Set(),
        title=_("Allow comments on these types?"),
        description=_("It will still require the user to have the correct permission to enable comments."),
        widget=limit_types_widget,
        missing=(),
    )

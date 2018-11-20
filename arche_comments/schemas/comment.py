# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import colander
import deform

from arche_comments import _


class CommentSchema(colander.Schema):
    body = colander.SchemaNode(
        colander.String(),
        title = _("Comment"),
        widget = deform.widget.TextAreaWidget(cols=5),
    )


def includeme(config):
    config.add_content_schema('Comment', CommentSchema, ('add', 'edit'))

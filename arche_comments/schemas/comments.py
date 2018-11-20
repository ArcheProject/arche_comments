# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import colander

from arche_comments import _


class CommentsFolderSchema(colander.Schema):
    notify = colander.SchemaNode(
        colander.Bool(),
        title=_("Send an email notification when a comment is added?"),
    )


def includeme(config):
    config.add_content_schema('CommentsFolder', CommentsFolderSchema, ('add', 'edit'))

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import colander
import deform
from webhelpers.html.converters import nl2br
from webhelpers.html.tools import strip_tags

from arche_comments import _


def convert_text(value):
    """
    Return text with only <br/> intact, all other tags stripped.
    """
    # Essentially, convert newline to br, strip tags turns br into newlines and
    # removes everything else, nl2br turns it into br again :)
    try:
        return nl2br(strip_tags(nl2br(value)))
    except:
        return colander.null


class CommentSchema(colander.Schema):
    body = colander.SchemaNode(
        colander.String(),
        title = _("Comment"),
        description=_("Note that HTML tags will be stripped"),
        widget = deform.widget.TextAreaWidget(cols=10),
        validator=colander.Length(max=5000),
        preparer=convert_text,
    )


def includeme(config):
    config.add_content_schema('Comment', CommentSchema, ('add', 'edit'))

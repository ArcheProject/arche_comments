from arche.api import Base
from arche.api import Folder
from zope.interface import implementer

from arche_comments import _
from arche_comments.interfaces import ICommentsFolder


@implementer(ICommentsFolder)
class CommentsFolder(Base, Folder):
    """ Container for comments.
    """
    nav_visible = False
    listing_visible = True
    search_visible = True
    title = _("Comments")
    type_name = "CommentsFolder"
    type_title = _("Comments folder")
    type_description = _("Container for comments.")


def includeme(config):
    config.add_content_factory(CommentsFolder)

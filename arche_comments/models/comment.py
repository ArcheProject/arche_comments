from arche.api import Base
from zope.interface import implementer

from arche_comments import _
from arche_comments.interfaces import IComment


@implementer(IComment)
class Comment(Base):
    nav_visible = False
    listing_visible = True
    search_visible = True
    type_name = "Comment"
    type_title = _("Comment")
    type_description = _("Comment object.")
    body = ""
    _creator = ()

    @property
    def creator(self):
        return self._creator
    @creator.setter
    def creator(self, value):
        self._creator = tuple(value)


def includeme(config):
    config.add_content_factory(Comment, addable_to = 'CommentsFolder')

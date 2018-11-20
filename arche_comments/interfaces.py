from arche.interfaces import IBase
from arche.interfaces import IFolder
from arche.interfaces import IIndexedContent


class IComment(IBase, IIndexedContent):
    pass


class ICommentsFolder(IBase, IFolder):
    pass

from arche.interfaces import IBase, IIndexedContent

from arche.interfaces import IFolder


class IComment(IBase, IIndexedContent):
    pass


class ICommentsFolder(IBase, IFolder):
    pass




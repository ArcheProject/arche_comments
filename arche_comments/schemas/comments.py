import colander


class CommentsFolderSchema(colander.Schema):
    pass


def includeme(config):
    config.add_content_schema('CommentsFolder', CommentsFolderSchema, ('add', 'edit'))

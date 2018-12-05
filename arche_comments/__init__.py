
from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('arche_comments')


def includeme(config):
    config.include('.fanstatic_lib')
    config.include('.models')
    config.include('.portlet')
    config.include('.schemas')
    config.include('.views')
    # Static dir
    config.add_static_view('static_arche_comments', 'static', cache_max_age=3600)
    # Locales
    config.add_translation_dirs('arche_comments:locale/')

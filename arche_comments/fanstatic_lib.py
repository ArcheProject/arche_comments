from arche.fanstatic_lib import common_js
from arche.fanstatic_lib import pure_js
from arche.interfaces import IBaseView
from arche.interfaces import IViewInitializedEvent
from fanstatic import Library
from fanstatic import Resource
from js.bootstrap import bootstrap_js
from js.bootstrap import bootstrap_css


library = Library('arche_comments', 'static')

arche_comments_css = Resource(library, 'styles.css', depends = (bootstrap_css,))
arche_comments_scripts = Resource(library, 'scripts.js', depends=(bootstrap_js, common_js, pure_js))


def need_subscriber(view, event):
    arche_comments_css.need()
    arche_comments_scripts.need()


def includeme(config):
    config.add_subscriber(need_subscriber, [IBaseView, IViewInitializedEvent])

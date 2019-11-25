"""
Sphinx Bootstrap theme.

Adapted for the pandas documentation.
"""
import os

import sphinx.builders.html
from sphinx.addnodes import pending_xref


from docutils import nodes, utils
from docutils.parsers.rst import Directive, directives

from .bootstrap_html_translator import BootstrapHTML5Translator
import docutils

__version__ = "0.0.1.dev0"

# -----------------------------------------------------------------------------
# Sphinx monkeypatch for adding toctree objects into context


def convert_docutils_node(list_item, only_pages=False):
    if not list_item.children:
        return None
    reference = list_item.children[0].children[0]
    title = reference.astext()
    url = reference.attributes["refuri"]
    active = "current" in list_item.attributes["classes"]

    if only_pages and '#' in url:
        return None

    nav = {}
    nav["title"] = title
    nav["url"] = url
    nav["children"] = []
    nav["active"] = active

    if len(list_item.children) > 1:
        for child_item in list_item.children[1].children:
            child_nav = convert_docutils_node(child_item, only_pages=only_pages)
            if child_nav is not None:
                nav["children"].append(child_nav)

    return nav


def update_page_context(self, pagename, templatename, ctx, event_arg):
    from sphinx.environment.adapters.toctree import TocTree

    def get_nav_object(**kwds):
        """Return a list of nav links that can be accessed from Jinja."""
        toctree = TocTree(self.env).get_toctree_for(
            pagename, self, collapse=True, **kwds
        )

        # Grab all TOC links from any toctrees on the page
        toc_items = [item for child in toctree.children for item in child
                     if isinstance(item, docutils.nodes.list_item)]

        nav = []
        for child in toc_items:
            child_nav = convert_docutils_node(child, only_pages=True)
            nav.append(child_nav)

        return nav

    def get_page_toc_object():
        """Return a list of within-page TOC links that can be accessed from Jinja."""
        self_toc = TocTree(self.env).get_toc_for(pagename, self)

        try:
            nav = convert_docutils_node(self_toc.children[0])
            return nav
        except:
            return {}

    ctx["get_nav_object"] = get_nav_object
    ctx["get_page_toc_object"] = get_page_toc_object
    return None


sphinx.builders.html.StandaloneHTMLBuilder.update_page_context = update_page_context


# -----------------------------------------------------------------------------


def get_html_theme_path():
    """Return list of HTML theme paths."""
    theme_path = os.path.abspath(os.path.dirname(__file__))
    return [theme_path]

# -----------------------------------------------------------------------------

from sphinx.addnodes import pending_xref
from docutils import nodes
from docutils.nodes import pending
from docutils.parsers.rst import roles
from sphinx.roles import XRefRole, AnyXRefRole
#from docutils.parsers.rst.directives.references import TargetNotes

class ButtonRole(XRefRole):
    pass

class ButtonLink(Directive):
    """
    Directive to declare a link as a button
    """

    # required_arguments, optional_arguments = 0,0
    # final_argument_whitespace = True
    has_content = True
    option_spec = {'class'   : directives.unchanged,
                   'target'  : directives.unchanged_required,
                   }
    def run(self):
        #self.assert_has_content()
        node = pending_xref("")
        node["reftarget"] = self.options.get('target', [])
        node["reftype"] = "ref"
        node["refdomain"] = "std"
        node["refexplicit"] = False
        node += nodes.inline("", self.content[0])
        print(self.content)
        #node['target'] = self.options.get('target', None)
        node['classes'] = ["btn", self.options.get('class', "btn-primary")] #
        #self.state.nested_parse(self.content, self.content_offset, node)
        #self.add_name(node)
        return [node]


class button(nodes.Inline, nodes.Element): pass
class Button(Directive):
    """
    Directive to declare a button
    """

    required_arguments, optional_arguments = 0,0
    final_argument_whitespace = True
    has_content = True
    option_spec = {'class'   : directives.class_option,
                   'target'  : directives.unchanged_required }
    def run(self):
        self.assert_has_content()
        node = button()
        node['target'] = pending() #self.options.get('target', None)
        node['classes'] = self.options.get('class', [])
        self.state.nested_parse(self.content, self.content_offset, node)
        self.add_name(node)
        return [node]


def setup(app):
    theme_path = get_html_theme_path()[0]
    app.add_html_theme("pandas_sphinx_theme", theme_path)
    app.set_translator("html", BootstrapHTML5Translator)
    app.add_directive('buttonlink', ButtonLink)
    #app.add_role("buttonrole", ButtonRole)
    roles.register_local_role("buttonrole", ButtonRole(lowercase=True, innernodeclass=nodes.inline, warn_dangling=True))






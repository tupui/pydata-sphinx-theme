"""A custom Sphinx HTML Translator for Bootstrap layout
"""
import sys
import re

from docutils import nodes

from sphinx.locale import admonitionlabels, _
from sphinx.writers.html5 import HTML5Translator


# Mapping of admonition classes to Bootstrap contextual classes
alert_classes = {
    "attention": "primary",
    "caution": "warning",
    "danger": "danger",
    "error": "danger",
    "hint": "info",
    "important": "primary",
    "note": "info",
    "seealso": "info",
    "tip": "primary",
    "warning": "warning",
    "todo": "info",
    "example": "info",
}


class BootstrapHTML5Translator(HTML5Translator):
    """Custom HTML Translator for a Bootstrap-ified Sphinx layout

    This is a specialization of the HTML5 Translator of sphinx.
    Only a couple of functions have been overridden to produce valid HTML to be
    directly styled with Bootstrap.
    """

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.settings.table_style = "table"

    def visit_admonition(self, node, name=""):
        # type: (nodes.Element, str) -> None
        # copy of sphinx source to add alert classes
        classes = ["alert"]
        if name:
            classes.append("alert-{0}".format(alert_classes[name]))
        self.body.append(self.starttag(node, "div", CLASS=" ".join(classes)))
        if name:
            node.insert(0, nodes.title(name, admonitionlabels[name]))

    def visit_table(self, node):
        # type: (nodes.Element) -> None
        # copy of sphinx source to *not* add 'docutils' and 'align-default' classes
        # but add 'table' class
        self.generate_targets_for_table(node)

        self._table_row_index = 0

        classes = [cls.strip(" \t\n") for cls in self.settings.table_style.split(",")]
        # classes.insert(0, "docutils")  # compat
        # if 'align' in node:
        #     classes.append('align-%s' % node['align'])
        tag = self.starttag(node, "table", CLASS=" ".join(classes))
        self.body.append(tag)

    #def visit_buttonlink(self, node):
    #    self.visit_reference(node)
    
    # def depart_buttonlink(self, node):
    #     self.depart_reference(node)

    def visit_button(self, node):
        btn_classes = { 'primary' : 'btn-primary', 'success' : 'btn-success',
                        'info'    : 'btn-info',    'warning' : 'btn-warning',
                        'danger'  : 'btn-danger',  'link'    : 'btn-link',
                        'outline' : 'btn-outline', 'tiny'    : 'btn-xs',
                        'small'   : 'btn-sm',      'large'   : 'btn-lg',
                        'block'   : 'btn-block',   'active'  : 'btn-active',
                        'secondary': 'btn-secondary' }

        classes = 'btn '
        flag = False
        for node_class in node['classes']:
            if node_class in ['primary', 'success', 'warning'
                              'info', 'link', 'danger', 'outline']:
                flag = True
            btn_class = btn_classes.get(node_class, None)
            if btn_class:
                classes += btn_class + ' '
        if flag == False:
            classes += 'btn-default'

        target = node['target']
        properties = ''

        # Disabled
        if 'disabled' in node['classes']:
            if target:
                properties += ' disabled="disabled"'
            else:
                classes += ' disabled'

        # Data toggle
        if 'toggle' in node['classes']:
            classes += ' dropdown-toggle '
            properties += ' data-toggle="dropdown"'
        if target:
            properties += ' role="button"'
            anchor = '<a href="%s" class="%s" %s>' % (target,classes,properties)
            self.body.append(anchor)
        else:
            properties += ' type="button"'
            button = '<button class="%s" %s>' % (classes,properties)
            self.body.append(button)

    def depart_button(self, node):
        if node['target']:
            self.body.append('</a>\n')
        else:
            self.body.append('</button>\n')

    # overwritten
    def visit_reference(self, node):
        # type: (nodes.Element) -> None
        atts = {'class': 'reference'}
        if node.get('internal') or 'refuri' not in node:
            atts['class'] += ' internal'
        else:
            atts['class'] += ' external'
        if 'refuri' in node:
            atts['href'] = node['refuri'] or '#'
            if self.settings.cloak_email_addresses and atts['href'].startswith('mailto:'):
                atts['href'] = self.cloak_mailto(atts['href'])
                self.in_mailto = True
        else:
            assert 'refid' in node, \
                   'References must have "refuri" or "refid" attribute.'
            atts['href'] = '#' + node['refid']
        # if not isinstance(node.parent, nodes.TextElement):
        #     assert len(node) == 1 and isinstance(node[0], nodes.image)
        #     atts['class'] += ' image-reference'
        if 'reftitle' in node:
            atts['title'] = node['reftitle']
        if 'target' in node:
            atts['target'] = node['target']
        self.body.append(self.starttag(node, 'a', '', **atts))

        if node.get('secnumber'):
            self.body.append(('%s' + self.secnumber_suffix) %
                             '.'.join(map(str, node['secnumber'])))

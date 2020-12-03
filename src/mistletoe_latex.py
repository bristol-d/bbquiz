# Let mistletoe parse TeX tokens for us.

import re
import html
from mistletoe.span_token import SpanToken, RawText
from mistletoe.html_renderer import HTMLRenderer
import tex
from mako.template import Template

class InlineMath(SpanToken):
    pattern = re.compile(r"[$](([^$]|\\[$])+)[$](?![$])")
    parse_inner = False
    parse_group = 1 

class HTMLRendererWithTex(HTMLRenderer):

    def __init__(self, renderer, preamble = None):
        super().__init__(InlineMath)
        self.tex = tex.Tex(preamble = preamble, renderer = renderer)
        self.renderer = renderer
        self.template = Template(filename = renderer.template_filename("embed"))

    def render_inline_math(self, token):
        hash = self.tex.render(token.content)
        # alt text. heuristic: if it's only one line, it can go in
        if '\n' in token.content:
            alt = "tex formula"
        else:
            alt = html.escape(token.content, quote = True)
        resdata = self.renderer.render_resource(hash)
        return self.template.render(resdata = resdata, alt = alt)

    def render_block_code(self, token):
        """
        Blackboard strips all newlines, including inside _code blocks_.
        To patch this stupidity, we override the mistletoe method to
        put them back by using break tags.
        While we're at it, we render them in monospace.
        """
        template = '<pre style="font-family: monospace"><code{attr}>{inner}</code></pre>'
        if token.language:
            attr = ' class="{}"'.format('language-{}'.format(self.escape_html(token.language)))
        else:
            attr = ''
        inner = html.escape(token.children[0].content).replace('\n', '<br/>')
        return template.format(attr=attr, inner=inner)

class HTMLRendererWithTexForHTML(HTMLRenderer):
    """
    This one is for creating the HTML output.
    """

    def __init__(self, renderer, preamble = None):
        super().__init__(InlineMath)
        self.tex = tex.Tex(preamble = preamble, renderer = renderer)
        self.renderer = renderer
        self.template = Template(filename = renderer.template_filename("html_embed"))

    def render_inline_math(self, token):
        hash = self.tex.render(token.content)
        if '\n' in token.content:
            alt = "tex formula"
        else:
            alt = html.escape(token.content, quote = True)
        resdata = self.renderer.render_resource(hash)
        localfolder = self.renderer.package.name + "_files"
        return self.template.render(resdata = resdata, alt = alt, localfolder = localfolder)

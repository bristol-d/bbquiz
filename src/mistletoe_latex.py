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
        self.tex = tex.Tex(preamble = preamble)
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

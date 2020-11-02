# Let mistletoe parse TeX tokens for us.

import re
from mistletoe.span_token import SpanToken, RawText
from mistletoe.html_renderer import HTMLRenderer

class InlineMath(SpanToken):
    pattern = re.compile(r"[$](([^$]|\\[$])+)[$](?![$])")
    parse_inner = False
    parse_group = 1 

class HTMLRendererWithTex(HTMLRenderer):
    def __init__(self):
        super().__init__(InlineMath)

    def render_inline_math(self, token):
        return '(TeX)'
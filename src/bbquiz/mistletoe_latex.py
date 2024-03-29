# Let mistletoe parse TeX tokens for us.

import re
import html
import pathlib
from mistletoe.span_token import SpanToken, RawText
from mistletoe.html_renderer import HTMLRenderer
import bbquiz.tex as tex
from mako.template import Template

class InlineMath(SpanToken):
    pattern = re.compile(r"[$](([^$]|\\[$])+)[$](?![$])")
    parse_inner = False
    parse_group = 1

class DisplayMath(SpanToken):
    pattern = re.compile(r"\$\$(([^$]|\\[$])+)\$\$")
    parse_inner = False
    parse_group = 1

class TexBlock(SpanToken):
    pattern = re.compile(r"\$\$\$(([^$]|\\[$]|[$][^$]|[$][$][^$])+)\$\$\$")
    parse_inner = False
    parse_group = 1

def alt_text(t):
    # alt text. heuristic: if it's only one line, it can go in
    if '\n' in t:
        alt = "tex formula"
    else:
        alt = html.escape(t, quote = True)
        alt = alt.replace('{', '&#123;')
        alt = alt.replace('}', '&#125;')
    return alt

class HTMLRendererWithTex(HTMLRenderer):

    def __init__(self, renderer, preamble = None):
        super().__init__(InlineMath, DisplayMath, TexBlock)
        self.tex = tex.Tex(preamble = preamble, renderer = renderer)
        self.renderer = renderer
        self.template = Template(filename = renderer.template_filename("embed"))

    def render_inline_math(self, token):
        hash = self.tex.render(token.content)
        alt = alt_text(token.content)
        resdata = self.renderer.render_resource(hash)
        return self.template.render(resdata = resdata, alt = alt)

    def render_display_math(self, token):
        hash = self.tex.render(token.content, displaymath = True)
        alt = alt_text(token.content)
        resdata = self.renderer.render_resource(hash)
        return self.template.render(resdata = resdata, alt = alt)

    def render_tex_block(self, token):
        hash = self.tex.render(token.content, texblock = True)
        alt = alt_text(token.content)
        resdata = self.renderer.render_resource(hash)
        return self.template.render(resdata = resdata, alt = alt)

    def render_display_math(self, token):
        hash = self.tex.render(token.content, displaymath = True)
        # alt text. heuristic: if it's only one line, it can go in
        if '\n' in token.content:
            alt = "tex formula"
        else:
            alt = html.escape(token.content, quote = True)
        resdata = self.renderer.render_resource(hash)
        return self.template.render(resdata = resdata, alt = alt)

    def render_tex_block(self, token):
        hash = self.tex.render(token.content, texblock = True)
        # alt text. heuristic: if it's only one line, it can go in
        if '\n' in token.content:
            alt = "tex output"
        else:
            alt = html.escape(token.content, quote = True)
        resdata = self.renderer.render_resource(hash)
        return self.template.render(resdata = resdata, alt = alt)

    def render_image(self, token):
        resdata = self.renderer.render_image(token)
        template = '<img src="@X@EmbeddedFile.requestUrlStub@X@bbcswebdav/xid-{}_1" alt="{}" {}>'
        # template = '<img src="{}" alt="{}"{} />'
        if token.title:
            title = ' title="{}"'.format(self.escape_html(token.title))
        else:
            title = ''
        return template.format(resdata.resid, self.render_to_plain(token), title)
    
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
        super().__init__(InlineMath, DisplayMath, TexBlock)
        self.tex = tex.Tex(preamble = preamble, renderer = renderer)
        self.renderer = renderer
        self.template = Template(filename = renderer.template_filename("html_embed"))

    def render_inline_math(self, token):
        hash = self.tex.render(token.content)
        alt = alt_text(token.content)
        resdata = self.renderer.render_resource(hash)
        localfolder = self.renderer.package.name + "_files"
        return self.template.render(resdata = resdata, alt = alt, localfolder = localfolder)

    def render_display_math(self, token):
        hash = self.tex.render(token.content, displaymath = True)
        alt = alt_text(token.content)
        resdata = self.renderer.render_resource(hash)
        localfolder = self.renderer.package.name + "_files"
        return self.template.render(resdata = resdata, alt = alt, localfolder = localfolder)

    def render_tex_block(self, token):
        hash = self.tex.render(token.content, texblock = True)
        alt = alt_text(token.content)
        resdata = self.renderer.render_resource(hash)
        localfolder = self.renderer.package.name + "_files"
        return self.template.render(resdata = resdata, alt = alt, localfolder = localfolder)

    def render_display_math(self, token):
        hash = self.tex.render(token.content, displaymath = True)
        if '\n' in token.content:
            alt = "tex formula"
        else:
            alt = html.escape(token.content, quote = True)
        resdata = self.renderer.render_resource(hash)
        localfolder = self.renderer.package.name + "_files"
        return self.template.render(resdata = resdata, alt = alt, localfolder = localfolder)

    def render_tex_block(self, token):
        hash = self.tex.render(token.content, texblock = True)
        # alt text. heuristic: if it's only one line, it can go in
        if '\n' in token.content:
            alt = "tex output"
        else:
            alt = html.escape(token.content, quote = True)
        resdata = self.renderer.render_resource(hash)
        localfolder = self.renderer.package.name + "_files"
        return self.template.render(resdata = resdata, alt = alt, localfolder = localfolder)

    def render_image(self, token):
        filepath = pathlib.Path(token.src)
        resdata = self.renderer.render_image(token)
        localfolder = self.renderer.package.name + "_files"
        template = Template(filename = self.renderer.template_filename("html_image"))
        return template.render(resdata = resdata, filename = filepath.name, alt = self.render_to_plain(token), localfolder = localfolder)

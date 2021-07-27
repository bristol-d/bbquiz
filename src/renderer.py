from mako.template import Template
from PIL import Image
import zipfile
import pathlib
import mistletoe
import html
import shutil
import random
import time

from mistletoe_latex import HTMLRendererWithTex, HTMLRendererWithTexForHTML

# These helper classes have the correct attributes to be picked up by the XML templates.

class Resource:
    def __init__(self, counter, type, title):
        self.id = 'res' + ('%05i' % counter)
        self.type = type
        self.title = title

class Manifest:
    def __init__(self, resources):
        self.id = "man00001"
        self.resources = resources

class RenderedQuestion:
    def __init__(self, q):
        self.content = q

class PoolResource:
    def __init__(self, name, id, sid, qs, instructions):
        self.name = name
        self.id = id
        self.sid = sid
        self.questions = qs
        self.instructions = instructions

def template_filename(name):
    mydir = pathlib.Path(__file__).parent.absolute()
    return str(mydir.joinpath('templates', name))

class ResourceFileData:
    """
    Data associated with a file resource (e.g. Tex image):
    resid, hash, w, h
    """
    def __init__(self, resid, hash, w, h):
        self.resid = resid
        self.hash = hash
        self.w = w
        self.h = h
    def __str__(self):
        return f"ResourceFileData(resid={self.resid},hash={self.hash},w={self.w},h={self.h})"

class Renderer:
    """
    Our own renderer.
    """

    def __init__(self, package):
        self.package = package
        self.z = None
        self.resmap = {}
        self.imgmap = {}
        self.resources = False
        self._bbid = 3191882 # why ???
        self._resid = 1000001
        self._resid_0 = 1000001
        self.files = pathlib.Path(__file__).parent.parent.joinpath('tmp').absolute()
        self.html = HTMLRendererWithTex(self, preamble = package.preamble)
        # this one is for output in the HTML file
        self.html2 = HTMLRendererWithTexForHTML(self, preamble = package.preamble)
        self.qidtags = {}

    def qidtag(self):
        """
        Return a fresh QID tag.
        """
        while True:
            id = '{id:04X}'.format(id=random.randrange(65536))
            if id not in self.qidtags:
                self.qidtags[id] = True
                return id

    def qn(self, c):
        """
        Return a formatted question number, e.g. with leading zeroes.
        """
        if 'qn_width' in self.package.config:
            w = int(self.package.config['qn_width'])
            s = f"Q%0{w}i"
            return s % c
        else:
            return "Q" + str(c)

    # This is so that the mistletoe renderer can call it
    def template_filename(self, t):
        return template_filename(t)

    def bbid(self):
        self._bbid += 1
        r = "_" + str(self._bbid) + "_1"
        return r

    def resid(self):
        """
        Get the next resource id for including a file.
        """
        self._resid += 1
        return str(self._resid)


    def render(self):
        self.z = zipfile.ZipFile(self.package.name + ".zip", mode = "w",
            compression = zipfile.ZIP_STORED)
        for (counter, pool) in enumerate(self.package.pools):
            self._render_pool(counter, pool)
        self._render_metadata()
        self._render_overview()

    def _render_overview(self):
        """
        Render a HTML overview of the package.
        """
        template = Template(filename = template_filename("html"))
        with open(self.package.name + ".html", "w") as file:
            file.write(template.render(
                package = self.package,
                fmt = self.render_text_html,
                htmlcontent = self.render_text_html(self.package.htmlcontent)
            ))

    def _render_metadata(self):
        """
        Render the manifest, info file and package file.
        """
        template = Template(filename = template_filename('manifest'))
        reslist = [
            Resource(counter + 1, "assessment/x-bb-qti-pool", pool.name)
            for (counter, pool) in enumerate(self.package.pools)
        ]
        reslist.append(Resource(len(reslist)+1, "resource/x-mhhe-course-cx", self.package.name))
        manifest = template.render(manifest=Manifest(reslist))

        self.z.writestr('imsmanifest.xml', manifest)
        self.z.write(template_filename('.bb-package-info'), ".bb-package-info")

        pkg_template = Template(filename = template_filename("package"))
        print("writing " + reslist[-1].id + ".dat")
        self.z.writestr(reslist[-1].id + ".dat", pkg_template.render(name=self.package.name))

    def _render_pool(self, counter, pool):
        questions = [
            RenderedQuestion(q.render(self.qn(c+1), self.bbid, self))
            for (c, q) in enumerate(pool.questions)
        ]
        template = Template(filename = template_filename("pool"))
        data = template.render(p=PoolResource(
            name = pool.name,
            id = self.bbid(),
            sid = self.bbid(),
            qs = questions,
            instructions = self.render_text(pool.instructions)
        ))
        datid = Resource(counter + 1, None, None).id
        print("writing " + datid + ".dat")
        self.z.writestr(datid + ".dat", data)

    def render_resource(self, hash):
        """
        Include a resource file (image of a TeX formula).
        Maintains a cache in resmap so we don't include the same thing multiple times.
        """
        if self.resources == False:
            # write out the package header
            pkgtemplate = Template(filename = template_filename("resource_header"))
            pkgtext = pkgtemplate.render(pkgname = self.package.name)
            self.z.writestr("csfiles/home_dir/LaTeX__xid-1000001_1.xml",
                pkgtext
            )
            self.resources = True
        if hash in self.resmap:
            return self.resmap[hash]
        # we need to write out the file. First, check it exists.
        filename = self.files.joinpath(hash + ".png")
        if filename.exists() and filename.is_file():
           pass
        else:
            raise Exception(f"render_resource: hash {hash} does not refer to a valid file {str(filename)}.")

        rid = self.resid()
        template = Template(filename = template_filename("resource"))
        # the xml file
        self.z.writestr(
            f"csfiles/home_dir/LaTeX__xid-1000001_1/{hash}__xid-{rid}_1.png.xml",
            template.render(hash=hash, resid=rid, pkgname = self.package.name)
        )
        # and the image itself
        self.z.write(
            filename,
            f"csfiles/home_dir/LaTeX__xid-1000001_1/{hash}__xid-{rid}_1.png"
        )
        # Get the image width/height for embedding
        with Image.open(filename) as image:
            width, height = image.size

        self.resmap[hash] = ResourceFileData(rid, hash, width, height)
        print(f"Resource {hash} mapped to id {rid}")
        return self.resmap[hash]

    def render_image(self, token):
        """
        Include a resource file (image).
        Maintains a cache in imgmap (key = filepath) so we don't include the same thing multiple times.
        """
        if self.resources == False:
            # write out the package header
            pkgtemplate = Template(filename = template_filename("resource_header"))
            pkgtext = pkgtemplate.render(pkgname = self.package.name)
            self.z.writestr("csfiles/home_dir/LaTeX__xid-1000001_1.xml",
                pkgtext
            )
            self.resources = True

        # If cache found, return
        filepath = pathlib.Path(token.src)
        if filepath in self.imgmap:
            return self.imgmap[filepath]

        # Check if the image file exists
        if filepath.exists() and filepath.is_file():
           pass
        else:
            raise Exception(f"render_image: Image {str(filepath)} is not found.")

        # Write to localfolder
        localfolder = pathlib.Path(self.package.name + "_files")
        if not localfolder.exists():
            localfolder.mkdir()
        targetfile = localfolder.joinpath(filepath.name)
        if not targetfile.exists():
            shutil.copy(filepath, targetfile)

        # Write to Zip file
        rid = self.resid()
        template = Template(filename = template_filename("resource_image"))
        # the resource id has to go before the extension
        suffix = filepath.suffix

        # Check configuration options to see if user wants to maintain PNG image filenames (default is to obfuscate them)
        if ('keep_imagenames' in self.package.config) and ('true' in self.package.config['keep_imagenames']):
            basename = filepath.name[:-len(suffix)]
        else:
            basename = str(round(time.time() * 1000))

        resname = f"{basename}__xid-{rid}_1{suffix}"

        # the xml file
        self.z.writestr(
            f"csfiles/home_dir/LaTeX__xid-1000001_1/{resname}.xml",
            template.render(filename=f"{resname}", resid=rid, pkgname = self.package.name)
        )
        # and the image itself
        self.z.write(
            filepath,
            f"csfiles/home_dir/LaTeX__xid-1000001_1/{resname}"
        )

        # Get the image width/height for embedding
        with Image.open(filepath) as image:
            width, height = image.size

        self.imgmap[filepath] = ResourceFileData(rid, None, width, height)
        print(f"Resource {filepath} mapped to id {rid}")
        return self.imgmap[filepath]

    def render_text_html(self, text):
        """
        Render text for output in the HTML document.
        """
        ast = mistletoe.Document(text)
        if len(ast.children) == 1 and ast.children[0].__class__.__name__ == "Paragraph":
            ast.children = ast.children[0].children
        ht = self.html2.render(ast)
        # here we don't want to escape, because we are returning raw HTML
        return ht

    def render_text(self, text):
        """
        Render a block of text:
          1. Convert markdown to HTML.
          2. HTML escape the whole thing.
          3. Remove the trailing newline.

        In step 1, if the whole thing is a single paragraph, then we do not want to wrap it
        in p tags.

        If we are doing QID tags, then we add one at the end.
        """
        if text == '': return text
        ast = mistletoe.Document(text)
        # check if we want to 'un-paragraph' it
        if len(ast.children) == 1 and ast.children[0].__class__.__name__ == "Paragraph":
            ast.children = ast.children[0].children
        ht = self.html.render(ast)
        escaped = html.escape(ht, quote = False)
        if escaped[-1] == '\n':
            escaped = escaped[:-1]

        # QID tags
        if 'qidtags' in self.package.config:
            tag = self.qidtag()
            escaped = html.escape(f'<div style="display: none">QID-{tag}</div>\n\n') + escaped

        return escaped

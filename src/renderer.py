from mako.template import Template
import zipfile
import pathlib
import mistletoe
import html

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
    def __init__(self, id, sid, qs):
        self.id = id
        self.sid = sid
        self.questions = qs

def template_filename(name):
    mydir = pathlib.Path(__file__).parent.absolute()
    return str(mydir.joinpath('templates', name))

class Renderer:
    """
    Our own renderer.
    """
    _bbid = 3191882 # why ???

    def __init__(self, package):
        self.package = package
        self.z = None

    def bbid(self):
        self._bbid += 1
        return "_" + str(self._bbid) + "_1"

    def render(self):
        self.z = zipfile.ZipFile(self.package.name + ".zip", mode = "w", 
            compression = zipfile.ZIP_STORED)
        for (counter, pool) in enumerate(self.package.pools):
            self._render_pool(counter, pool)
        self._render_metadata()

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
            RenderedQuestion(q.render(c+1, self.bbid, self)) 
            for (c, q) in enumerate(pool.questions) 
        ]
        template = Template(filename = template_filename("pool"))
        data = template.render(p=PoolResource(self.bbid(), self.bbid(), questions))
        datid = Resource(counter + 1, None, None).id
        print("writing " + datid + ".dat")
        self.z.writestr(datid + ".dat", data)

    def render_text(self, text):
        """
        Render a block of text:
          1. Convert markdown to HTML.
          2. HTML escape the whole thing.
          3. Remove the trailing newline.

        In step 1, if the whole thing is a single paragraph, then we do not want to wrap it
        in p tags.
        """
        ast = mistletoe.Document(text)
        # check if we want to 'un-paragraph' it
        if len(ast.children) == 1 and ast.children[0].__class__.__name__ == "Paragraph":
            ast.children = ast.children[0].children
        ht = mistletoe.HTMLRenderer().render(ast)
        escaped = html.escape(ht)
        if escaped[-1] == '\n':
            return escaped[:-1]
        else:
            return escaped

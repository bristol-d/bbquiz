from mako.template import Template
import zipfile
import pathlib

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
        return self._bbid

    def render(self):
        self.z = zipfile.ZipFile(self.package.name + ".zip", mode = "w", 
            compression = zipfile.ZIP_STORED)
        self._render_metadata()
        for (counter, pool) in enumerate(self.package.pools):
            self._render_pool(counter, pool)

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
        self.z.writestr(reslist[-1].id + ".dat", pkg_template.render(name=self.package.name))

    def _render_pool(self, counter, pool):
        questions = [ 
            RenderedQuestion(q.render(c+1, self.bbid)) 
            for (c, q) in enumerate(pool.questions) 
        ]
        template = Template(filename = template_filename("pool"))
        data = template.render(p=PoolResource(self.bbid(), self.bbid(), questions))
        self.z.writestr(Resource(counter, None, None).id + ".dat", data)

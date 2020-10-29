# An experiment generating a ZIP file without BBQuizMaker

from mako.template import Template
import zipfile
import uuid

class Map(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def newid(): return uuid.uuid4().hex

_bbid = 3191882 # why ???
def bbid():
    global _bbid
    _bbid += 1
    return "_" + str(_bbid) + "_1"

z = zipfile.ZipFile("experiment.zip", mode = "w", compression = zipfile.ZIP_STORED)

manifest_template = Template(filename = "src/templates/manifest")
manifest = manifest_template.render(manifest=Map({
    "id": "man00001",
    "resources": [
        Map({"id": "res00001", "type": "assessment/x-bb-qti-pool", "title": "ExperimentQuestionPool"}),
        Map({"id": "res00002", "type": "resource/x-mhhe-course-cx", "title": "ExperimentPackage"})
    ]
}))
z.writestr('imsmanifest.xml', manifest)
z.write('src/templates/.bb-package-info', ".bb-package-info")

package_template = Template(filename = "src/templates/package")
z.writestr("res00002.dat", package_template.render(name="ExperimentPackage"))

mcq_template = Template(filename = "src/templates/mcq")
pool_template = Template(filename = "src/templates/pool")

correct = newid()
question = Map({
    "title": "Q1",
    "id": bbid(),
    "stem": "What is the answer?",
    "options": [
        Map({"id": newid(), "text": "no"}),
        Map({"id": correct, "text": "yes"})
    ],
    "correctid": correct
})

question_xml = mcq_template.render(d=question)
pool_xml = pool_template.render(p=Map({
    "id": bbid(),
    "sid": bbid(),
    "questions": [
        Map({"content": question_xml})
    ]
}))

z.writestr('res00001.dat', pool_xml)

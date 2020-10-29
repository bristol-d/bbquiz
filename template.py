from mako.template import Template

mcq_template = Template(filename = "src/templates/mcq")
pool_template = Template(filename = "src/templates/pool")

class Map(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

d = Map({
    "title": "TITLE",
    "id": "ID",
    "options": [
        Map({"id": "11111", "text": "one"}),
        Map({"id": "22222", "text": "two"})
    ],
    "correctid": "22222"
})

out = mcq_template.render(d=d)

pool = Map({
    "id": "POOLID",
    "sid": "SID",
    "questions": [
        Map({"content": out})
    ]
})

poolout = pool_template.render(p=pool)

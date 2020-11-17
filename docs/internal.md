# Internal documentation for developers

The blackboard upload format is a ZIP file with the following files in the root folder:
  * `.bb-package-info`: fixed content metadata file (provided).
  * `imsmanifest.xml`: table of contents, listing names and types of resource files (pools and packages).
  * `res#####.dat`: individual XML files.

## Manifest file

The general format can be seen in the `manifest` template. Resource identifiers are `res#####` and types are
  * `assessment/x-bb-qti-pool` for packages
  * `resource/x-mhhe-course-cx` for pools

## How embedded tex is handled

The `.dat` file contains the following code:

    &lt;img src="
    @X@EmbeddedFile.requestUrlStub@X@bbcswebdav/xid-{I}_1"
    style="vertical-align:middle;" width="{W}" height="{H}" alt="{A}"
    &gt;

where W/H are the width/height of the image, A is the alt text (source string) and I is the id.
An example id is `1000002`. The counter starts at 1000002 because `-01` is needed for the folder.

In the zip file, under `csfiles/home_dir`, there are the following:

  * `LaTeX__xid-1000001_1.xml` with the contents

```
<?xml version="1.0" encoding="UTF-8"?>
<lom>
    <relation>
        <resource>
            <identifier>1000001_1#/courses/{PACKAGE}/LaTeX</identifier>
        </resource>
    </relation>
</lom>
```

  * A folder `LaTeX__xid-1000001_1` with, for each file,
    * The file itself as `{NAME}__xid-{ID}_1.png`.
    * A file `{NAME}__xid-{ID}_1.png.xml` with the contents

```
<?xml version="1.0" encoding="UTF-8"?>
<lom>
    <relation>
        <resource>
            <identifier>{ID}#/courses/{PACKAGE}/LaTeX__xid-1000001_1\{NAME}__xid-{ID}_1.png</identifier>
        </resource>
    </relation>
</lom>
```

## Points

The following lines seem to be used to set the number of points for a question:

    <resprocessing scoremodel="SumOfScores">
      <outcomes>
          <decvar varname="SCORE" vartype="Decimal" defaultval="0" minvalue="0" maxvalue="10.00000"/>
      </outcomes>

We use `${question.config['points']}` for the integer part of the maxvalue, which is defined in the question base class.

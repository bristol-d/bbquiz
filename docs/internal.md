# Internal documentation for developers

The blackboard upload format is a ZIP file with the following files in the root folder:
  * `.bb-package-info`: fixed content metadata file (provided).
  * `imsmanifest.xml`: table of contents, listing names and types of resource files (pools and packages).
  * `res#####.dat`: individual XML files.

## Manifest file

The general format can be seen in the `manifest` template. Resource identifiers are `res#####` and types are
  * `assessment/x-bb-qti-pool` for packages
  * `resource/x-mhhe-course-cx` for pools


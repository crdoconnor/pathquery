Is a directory:
  based on: Pathquery
  given:
    files:
      yourdir/file1.js: contents
      yourdir/file2.js: contents
      yourdir/other_folder/file3.js: contents
      yourdir/other_folder/file4: notjs
      yourdir/node_modules/file5.js: contents
      yourdir/node_modules/file6.js: contents
  steps:
  - Run: |
      for path in pathquery("yourdir").is_dir() - pathquery("yourdir/node_modules"):
          output(path)
  - Output contains:
      expected contents:
        - yourdir
        - yourdir/other_folder
      but not:
        - yourdir/node_modules

Is not directory:
  based on: Pathquery
  given:
    files:
      yourdir/file1.js: contents
      yourdir/file2.js: contents
      yourdir/other_folder/file3.js: contents
      yourdir/other_folder/file4: notjs
      yourdir/node_modules/file5.js: contents
      yourdir/node_modules/file6.js: contents
  steps:
  - Run: |
      for path in pathquery("yourdir").is_not_dir():
          output(path)
  - Output contains:
      expected contents:
        - yourdir/file1.js
        - yourdir/file2.js
        - yourdir/other_folder/file3.js
        - yourdir/other_folder/file4
        - yourdir/node_modules/file5.js
        - yourdir/node_modules/file6.js
      but not:
        - yourdir
        - yourdir/other_folder

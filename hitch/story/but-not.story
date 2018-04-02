But not:
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
      for path in pathquery("yourdir").ext("js").but_not(pathquery("yourdir/node_modules")):
          output(path)
  - Output contains:
      expected contents:
        - yourdir/file1.js
        - yourdir/file2.js
        - yourdir/other_folder/file3.js
      but not:
        - yourdir/node_modules/file4
        - yourdir/node_modules/file5

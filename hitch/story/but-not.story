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
  variations:
    whole directory:
      steps:
      - Run: |
          for path in pathquery("yourdir").ext("js") - pathquery("yourdir/node_modules"):
              output(path)
      - Output contains:
          expected contents:
            - yourdir/file1.js
            - yourdir/file2.js
            - yourdir/other_folder/file3.js
          but not:
            - yourdir/node_modules/file5.js
            - yourdir/node_modules/file6.js

    single file:
      steps:
      - Run: |
          for path in pathquery("yourdir").ext("js") - pathquery("yourdir/node_modules").named("file5.js"):
              output(path)
      - Output contains:
          expected contents:
            - yourdir/file1.js
            - yourdir/file2.js
            - yourdir/other_folder/file3.js
            - yourdir/node_modules/file6.js
          but not:
            - yourdir/node_modules/file5.js

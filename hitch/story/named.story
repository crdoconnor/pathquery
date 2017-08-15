File named:
  based on: Pathquery
  preconditions:
    files:
      yourdir/file1.js: contents
      yourdir/file2.js: contents
      yourdir/other_folder/file3.js: contents
      yourdir/other_folder/file1.js: notjs
    code: |
      for path in pathq("yourdir").named("file1.js"):
            output(path)
  scenario:
    - Output contains:
        expected contents:
          - yourdir/file1.js
          - yourdir/other_folder/file1.js

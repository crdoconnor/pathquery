Simple globbing:
  based on: Pathquery
  preconditions:
    files:
      jsfile1.js: contents
      jsfile2.js: contents
      yourdir/other_folder/jsfile3.js: notjs
      file4: contents
      file5.txt: contents
      yourdir/other_folder/file6: contents
    code: |
      for path in pathq(".").glob("*.js"):
            output(path)
  scenario:
    - Output contains:
        expected contents:
          - jsfile1.js
          - jsfile2.js
          - yourdir/other_folder/jsfile3.js
        but not:
          - file4
          - file5.txt
          - yourdir/other_folder/file6

Glob all:
  based on: Pathquery
  preconditions:
    files:
      jsfile1.js: contents
      jsfile2.js: contents
      yourdir/other_folder/jsfile3.js: notjs
    code: |
      for path in pathq(".").glob("*"):
            output(path)
  scenario:
    - Output contains:
        expected contents:
          - .
          - jsfile1.js
          - jsfile2.js
          - yourdir
          - yourdir/other_folder
          - yourdir/other_folder/jsfile3.js

Glob one:
  based on: Pathquery
  preconditions:
    files:
      jsfile1.js: contents
      jsfile2.js: contents
      yourdir/other_folder/jsfile3.js: notjs
    code: |
      for path in pathq(".").glob("jsfile1.js"):
            output(path)
  scenario:
    - Output contains:
        expected contents:
          - jsfile1.js

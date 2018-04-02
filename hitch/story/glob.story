Simple globbing:
  based on: Pathquery
  given:
    files:
      jsfile1.js: contents
      jsfile2.js: contents
      yourdir/other_folder/jsfile3.js: notjs
      file4: contents
      file5.txt: contents
      yourdir/other_folder/file6: contents
  steps:
  - Run: |
      for path in pathquery(".").glob("*.js"):
          output(path)
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
  given:
    files:
      jsfile1.js: contents
      jsfile2.js: contents
      yourdir/other_folder/jsfile3.js: notjs
  steps:
  - Run: |
      for path in pathquery(".").glob("*"):
          output(path)
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
  given:
    files:
      jsfile1.js: contents
      jsfile2.js: contents
      yourdir/other_folder/jsfile3.js: notjs
  steps:
  - Run: |
      for path in pathquery(".").glob("jsfile1.js"):
          output(path)
  - Output contains:
      expected contents:
        - jsfile1.js

Has extension:
  based on: Pathquery
  given:
    files:
      yourdir/file1.js: contents
      yourdir/file2.js: contents
      yourdir/other_folder/file3.js: contents
      yourdir/other_folder/file4: notjs
    symlinks:
      yourdir/other_folder/file5.js: yourdir/other_folder/file4
  steps:
  - Run: |
      for path in pathq("yourdir").ext("js").is_symlink():
          output(path)
  - Output contains:
      expected contents:
        - yourdir/other_folder/file5.js
      but not:
        - yourdir/file1.js
        - yourdir/file2.js
        - yourdir/other_folder/file3.js

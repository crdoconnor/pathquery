Is writable:
  based on: Pathquery
  given:
    files:
      yourdir/writable1.txt: contents
      yourdir/unwritable1.txt: contents
      yourdir/subdir/writable2.txt: contents
      yourdir/subdir/unwritable2.txt: contents
    permissions:
      yourdir/unwritable1.txt: 0444
      yourdir/subdir/unwritable2.txt: 0444
  steps:
  - Run: |
      for path in pathquery("yourdir").is_writable():
          output(path)
  - Output contains:
      expected contents:
        - yourdir
        - yourdir/writable1.txt
        - yourdir/subdir
        - yourdir/subdir/writable2.txt
      but not:
        - yourdir/unwritable1.txt
        - yourdir/subdir/unwritable2.txt


Is not writable:
  based on: Pathquery
  given:
    files:
      yourdir/writable1.txt: contents
      yourdir/unwritable1.txt: contents
      yourdir/subdir/writable2.txt: contents
      yourdir/subdir/unwritable2.txt: contents
    permissions:
      yourdir/unwritable1.txt: 0444
      yourdir/subdir/unwritable2.txt: 0444
  steps:
  - Run: |
      for path in pathquery("yourdir").is_not_writable():
          output(path)
  - Output contains:
      expected contents:
        - yourdir/unwritable1.txt
        - yourdir/subdir/unwritable2.txt
      but not:
        - yourdir
        - yourdir/writable1.txt
        - yourdir/subdir
        - yourdir/subdir/writable2.txt


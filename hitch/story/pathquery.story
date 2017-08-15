Pathquery:
  preconditions:
    python version: (( python version ))
    pathpy version: (( pathpy version ))
    setup: |
      from pathquery import pathq
    code: pass
  params:
    python version: 3.5.0
    pathpy version: 10.3.1
  scenario:
    - Run code

Pathquery:
  given:
    python version: (( python version ))
    pathpy version: (( pathpy version ))
    setup: |
      from pathquery import pathquery
      
      def output(text):
          with open("output.txt", "a") as handle:
              handle.write("{0}\n".format(text))
  with:
    python version: 3.5.0
    pathpy version: 10.3.1

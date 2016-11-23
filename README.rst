PathQuery
=========

PathQuery is a tool to declaratively define file searches.

Example
-------

Search for all files except the node_modules folder:

.. code-block:: python

    from pathquery import pathq

    pathq("yourdir/*.js").but_not(pathq("yourdir/node_modules/*"))

Install
-------

  $ pip install pathquery

Hacking
-------

If you want to hack, you can TDD with::

  sudo pip install hitch
  cd dumbyaml/tests
  hitch init
  hitch test *.test

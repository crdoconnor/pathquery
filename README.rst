PathQuery
=========

PathQuery is a tool to declaratively define file searches that returns a list
of `path.py <https://github.com/jaraco/path.py>`_ Path objects.

Example
-------

Search for all files recursively except in the node_modules folder and change its perms:

.. code-block:: python

    from pathquery import pathq

    for p in pathq("yourdir/*.js").but_not(pathq("yourdir/node_modules/*")):
        p.chmod(0755)

Install
-------

To use::

  $ pip install pathquery

API
---

Path properties can be inspected as part of the query:

.. code-block:: python

    pathq("yourdir/*").is_dir()
    pathq("yourdir/*").is_not_dir()
    pathq("yourdir/*").is_symlink()
    pathq("yourdir/*").is_not_symlink()

Queries are also chainable:

.. code-block:: python

    pathq("yourdir/*.js").is_symlink().but_not(pathq("yourdir/node_modules/*")):
        p.remove()

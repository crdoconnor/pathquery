Hacking
=======

Running on Mac
--------------

To set up a dev environment:

1) Install XCode from the Mac App store, if not already installed.
2) Run "xcode-select --install"
3) Install brew if not already installed -- instructions here : http://brew.sh/
4) Run::

    $ brew install python python3 libtool automake

    $ pip install --upgrade hitchkey virtualenv     # ideally outside virtualenv, n.b. hitchkey has no dependencies

If it fails with a "permission denied", try sudo pip install.    

Git clone the repository somewhere new (e.g. a temporary directory) and switch to the branch you want.

Then (in any directory inside the project)::

    $ hk help

If this fails to run on your mac for any reason, please raise a ticket.


Running on Linux
================

To set up a dev environment::

    $ sudo apt-get install python3 python-pip python-virtualenv libreadline-dev

    $ sudo pip install --upgrade hitchkey         # ideally outside of a virtualenv, hitchkey has no dependencies

Then (in any directory inside the project)::

    $ hk help

If this fails to run on your linux box for any reason, please raise a ticket.

Important commands::

    $ hk bdd not sym    # run individual "is not symlink" story
    
    $ hk lint           # lint using project specific rules
    
    $ hk regression     # lint and run all tests

    $ hk rerun          # rerun the last test but don't capture stdout (useful if you want to embed and use ipython)

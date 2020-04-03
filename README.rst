Twitter scraper
===============

Requirements
------------

Run

.. code::

    pip install -r requirements.txt

This installs the following libraries:

* matplotlib
* twitter-scraper

Usage
-----

.. code::

    python twitter.py USERNAME
    python twitter.py elonmusk
    python twitter.py JeffBezoz
    ...

Optionally you can define the number of pages to download.

.. code::

    python twitter.py elonmusk -p 10
    OR
    python twitter.py elonmusk --pages 25
    ...

To retrieve older/more tweets, increase the number of pages.

TODO
----

* Store tweet history per username *persistently* (JSON/SQL/...?)
    * Convert data to Excel files (requested format: | dd.mm.yyyy | number)

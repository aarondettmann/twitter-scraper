.. image:: https://img.shields.io/badge/python-v3.8-blue.svg?style=flat
   :target: https://www.python.org/
   :alt: Python version


.. image:: https://img.shields.io/badge/license-MIT-green.svg?style=flat
    :target: https://github.com/aarondettmann/twitter-scraper/blob/master/LICENSE.txt
    :alt: License

|

.. image:: https://raw.githubusercontent.com/aarondettmann/twitter-scraper/master/docs/img/logo.png
   :target: https://github.com/aarondettmann/twitter-scraper/
   :alt: Logo


Twitter scraper
===============

Getting started (Windows)
-------------------------

First, make sure you have installed *Python* on your system (version **3.8.0** or higher). It is also recommended that you install *git* as it makes downloading and updating this script easier.

* *Python* (https://www.python.org/)
* *Git* (https://git-scm.com/)

The Twitter download script provided in this package is a *command-line tool*. On Windows it can be run in an interpreter like *cmd*. To start the interpreter, press `<Windows key> <https://en.wikipedia.org/wiki/Windows_key>`_\+R and enter *cmd*.

.. image:: https://raw.githubusercontent.com/aarondettmann/twitter-scraper/master/docs/img/run.png
   :alt: run

After pressing *OK*, the command-line interpreter will open.

.. image:: https://raw.githubusercontent.com/aarondettmann/twitter-scraper/master/docs/img/cmd.png
   :alt: run

Here, you can enter any commands and execute them by pressing *Enter*.

Step 1: Download the script
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Assuming that you have installed *git*, you can now enter the following command (and execute by pressing enter).

.. code::

    git clone https://github.com/aarondettmann/twitter-scraper

The repository including the main script will be downloaded. Next, change into the newly created directory called ``twitter-scraper``.

.. code::

    cd twitter-scraper

You may list the files in the current directory by running ``dir`` in *cmd*. Here, you will see the main script called ``twitter.py``. You may also open the *Explorer* file browser which will show you the same files. To open Explorer in your current directory from the *cmd*, enter ``explorer .`` (notice the dot!).

Step 2: Install additional Python libraries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To run the ``twitter.py``, you first need to install a few additional Python libraries. The simplest way to do this, is to the following command in a terminal:

.. code::

    pip install -r requirements.txt

This automatically installs the following libraries:

* *twitter-scraper* (for access to the Twitter API)
* *openpyxl* (for writing to Excel files)

Step 3: Using the script
~~~~~~~~~~~~~~~~~~~~~~~~

If you have followed the instructions above, you can now use the Twitter download script. Try to enter just:

.. code::

    python twitter.py

A short help page will be shown indicating the available command line arguments that are available.

**Download Twitter data**

Use the ``down`` mode in order to download twitter data. After the ``down`` keyword, you need to specify the ``USERNAME`` (Twitter account name). Use the optional argument ``-p NUMBER`` to specify how many page you want to download. To retrieve older/more tweets, increase the number of pages. Example:

.. code::

    python twitter.py down elonmusk -p 5

Instead of a user name it is also possible to use a *hashtag*. Note that you might have to put the hashtag in quotation marks (e.g. ``python twitter.py down "#aviation" -p 10``).

**Excel files**

When downloading Twitter data, it is by default saved as a JSON file and an Excel file (note that the JSON file may contain more information than the Excel file). In some cases it may be useful to manually convert a JSON file to Excel. In this case this can be achieved as shown in the following example.

.. code::

    python twitter.py xl data/elonmusk_2020-04-01_1030/data.json

This will generate an Excel file ``data/elonmusk_2020-04-01_1030/data.xlsx``.

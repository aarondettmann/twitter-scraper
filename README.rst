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
* openpyxl

Usage
-----

Download Twitter data for user USERNAME. Use ``-p NUMBER`` to specify how many page you want to download. To retrieve older/more tweets, increase the number of pages. The ``-p`` flag is optional.

.. code::

    python twitter.py down USERNAME -p 5

You can visualize date using the **plot** mode. As a second argument, specify the JSON file with the twitter data downloaded in the previous step.

.. code::

    python twitter.py plot data/USERNAME_***/data.json

When downloading Twitter data, it is stored in a JSON format. The data may be converted to an Excel file as shown below:

.. code::

    python twitter.py xl data/USERNAME_***/data.json
    
This will generate an Excel file ```data/USERNAME_***/data.xlsx``.

Twitter scraper
===============

Requirements
------------

To run the script, you need *Python* (version 3.8.0 or higher). A few additional libraries are required. These can be easily installed by running the following command in a terminal:

.. code::

    pip install -r requirements.txt

This installs the following libraries:

* *matplotlib* (for plotting)
* *twitter-scraper* (for access to the Twitter API)
* *openpyxl* (for writing to Excel files)

Usage
-----

**Download Twitter data** Use the ``down`` mode in order to download twitter data. After the ``down`` keyword, you need to specify the ``USERNAME`` (Twitter account name). Use the optional argument ``-p NUMBER`` to specify how many page you want to download. To retrieve older/more tweets, increase the number of pages. Example:

.. code::

    python twitter.py down elonmusk -p 5

**Plotting** You can visualize data using the **plot** mode. As a second argument, specify the JSON file with the twitter data you downloaded in the previous step. Example

.. code::

    python twitter.py plot data/elonmusk_2020-04-01_1030/data.json

**Excel files** When downloading Twitter data, it is stored in a JSON format. The data may be converted to an Excel file as shown in the example below.

.. code::

    python twitter.py xl data/elonmusk_2020-04-01_1030/data.json

This will generate an Excel file ``data/elonmusk_2020-04-01_1030/data.xlsx``.

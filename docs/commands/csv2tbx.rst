
.. _pages/toolkit/csv2tbx#csv2tbx:

csv2tbx
*******

Convert between CSV (Comma Separated Value) files and the :doc:`/formats/tbx` format for terminology exchange.

.. _pages/toolkit/csv2tbx#usage:

Usage
=====

::

  csv2tbx [--charset=CHARSET] [--columnorder=COLUMNORDER] <csv> <tbx>

Where:

| <csv>  | is a CSV file  |
| <tbx>   | is the target TBX file |

Options (csv2tbx):

| --version            | show program's version number and exit   |
| -h, --help           | show this help message and exit   |
| --manpage            | output a manpage based on the help   |
| :doc:`--progress=progress <option_progress>`  | show progress as: dots, none, bar, names, verbose   |
| :doc:`--errorlevel=errorlevel <option_errorlevel>`   | show errorlevel as: none, message, exception, traceback   |
| -iINPUT, --input=INPUT    | read from INPUT in csv format   |
| -xEXCLUDE, --exclude=EXCLUDE    | exclude names matching EXCLUDE from input paths   |
| -oOUTPUT, --output=OUTPUT   | write to OUTPUT in tbx format   |
| :doc:`--psyco=MODE <option_psyco>`         | use psyco to speed up the operation, modes: none, full, profile   |
| --charset=CHARSET    | set charset to decode from csv files   |
| --columnorder=COLUMNORDER   | specify the order and position of columns (comment,source,target)   |

.. _pages/toolkit/csv2tbx#csv_file_layout:

CSV file layout
===============

The CSV file is expected to have three columns (separated by commas, not other characters like semicolons), of which the default layout is

+--------+-------------------+------------------------------------------------------------------+
| Column | Data              | Description                                                      |
+========+===================+==================================================================+
|  A     | comment           | All the PO #: location comments.  These are not used in the TBX  |
|        |                   | files, and can be left empty, but could be generated by          |
|        |                   | :doc:`po2csv <csv2po>`                                           |
+--------+-------------------+------------------------------------------------------------------+
|  B     | Source Language   | The msgid or source string                                       |
+--------+-------------------+------------------------------------------------------------------+
|  C     | Target Language   | The msgstr or target language                                    |
+--------+-------------------+------------------------------------------------------------------+

.. _pages/toolkit/csv2tbx#examples:

Examples
========

These examples demonstrate the use of csv2tbx::

  csv2tbx terms.csv terms.tbx

to simply convert *terms.csv* to *terms.tbx*.

To convert a directory recursively to another directory with the same structure of files::

  csv2tbx csv-dir tbx-target-dir

This will convert CSV files in *csv-dir* to TBX files placed in *tbx-target-dir*.::

  csv2tbx --charset=windows-1250 csv tbx

Users working on Windows will often return files in encoding other the Unicode based encodings.  In this case we convert
CSV files found in *csv* from *windows-1250* to UTF-8 and place the correctly encoded files in *tbx*. Note that
UTF-8 is the only available destination encoding.

.. _pages/toolkit/csv2tbx#two_column_csv:

Two column CSV
==============

::

  csv2tbx --columnorder=source,target foo.csv foo.tbx

.. _pages/toolkit/csv2tbx#notes:

Notes
=====

For conformance to the standards and to see which features are implemented, see :doc:`/formats/csv` and :doc:`/formats/tbx`.

.. _pages/toolkit/csv2tbx#bugs:

Bugs
====

None.
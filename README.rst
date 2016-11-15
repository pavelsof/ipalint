=======
ipalint
=======

Checks linguistic datasets for IPA errors and inconsistencies. Usage::

    ipalint mydataset

This will either (1) print the IPA errors found in the dataset; (2) print
nothing, meaning it found no errors; or (3) print an error message if it fails
to read the file. In no case will the input file be modified.

The linter should be able to read any well-formed csv/tsv/tab dataset, assuming
that there is an IPA data column. It also reads table-less lines and handles
pipes; thus, even if you have a less common format like `this one`_, you can
still lint it by doing something like::

    cat KSL.qlc | grep "^[[:digit:]]" | cut -f 6 | ipalint


optional arguments
==================

``--col COL`` specifies the column containing the IPA data; this can be either
the column name or the column index (starting from 0). If this option is not
set, ipalint will try to guess the column by looking at the column names.

``--no-header`` treats the first row as data. The default is to treat the first
row as header and not lint it.

``--ignore-nfd`` ignores errors about an IPA string that are not in Unicode's
NFD normal form. With very few exceptions, IPA diacritics should be combining
characters. However, in some situations this might be irrelevant for your
purposes and you can ignore these errors.

``--ignore-ws`` ignores errors about leading or trailing whitespace in IPA
strings. If combined with the previous flag, ipalint will only report errors
about symbols that are not part of the IPA chart.

``--linewise`` outputs (line number, error message) tuples, one such tuple per
line of output. The default is to output the set of errors and include the list
of line numbers to the right of each error.

``--no-lines`` only outputs the set of errors found in the data. Useful when
you want a quick glimpse of what might be wrong. This flag is ignored if the
previous one is set.


installation
============

This is a standard Python 3 package without dependencies. Even thought it is
not yet offered in the Cheese Shop, you can install it by cloning this repo
(you can delete it afterwards) and doing this::

    python3 setup.py test
    python3 setup.py install

Of course, you can install it within a virtualenv/venv as well.


similar projects
================

* ipapy_ checks and cleans IPA strings.
* lingpy_ includes some tools for analysing IPA strings.


licence
=======

MIT. Do as you please and praise the snake gods.

.. _`this one`: https://github.com/lingpy/lingpy/blob/facf0230c70a23cde3883a6f904445bb965878f8/lingpy/tests/test_data/KSL.qlc
.. _`ipapy`: https://pypi.python.org/pypi/ipapy
.. _`lingpy`: http://lingpy.org/

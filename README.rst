Crowdin-client
==============

A client for the `Crowdin`_ API which lets you push source translations to
crowdin and pull translated content.

.. _Crowdin: http://crowdin.net/

Installation
------------

::

    (sudo) pip install crowdin-client

If you don't have ``pip``::

    (sudo) easy_install pip
    (sudo) pip install crowdin-client

If you don't even have ``easy_install`` on windows, get the ``.exe`` at
http://pypi.python.org/pypi/setuptools, install it, add ``c:\Python2x\Scripts``
to the Windows path (replace Python2x with the correct directory).

Configuration
-------------

Create a ``.crodwin`` JSON file in your root project directory with the
following structure::

    {
        "project_name": "crowdin project name",
        "api_key": "project API key",
        "localizations": [
            {
                "source_path": "locale/en/LC_MESSAGES/django.po",
                "remote_path": "path/to/django.po",
                "target_langs": {
                    "fr": "locale/en/LC_MESSAGES/django.po",
                    "de": "locale/de/LC_MESSAGES/django.po",
                    "it": "locale/it/LC_MESSAGES/django.po"
                }
            }
        ]
    }

Usage
-----

Push source files::

    crowdin push

Pull translations::

    crowdin pull

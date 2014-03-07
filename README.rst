Crowdin-client
==============

.. image:: https://travis-ci.org/epyx-src/crowdin-client.png?branch=master
	:alt: Build Status
	:target: https://travis-ci.org/epyx-src/crowdin-client

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
            },
            {
            	"source_path": "locale/en/LC_MESSAGES/*.po",
            	"excluded" : "_*, ~*",
            	"remote_path": "path/to/",
            	"target_langs": {
                    "fr": "locale/en/LC_MESSAGES/",
                    "de": "locale/de/LC_MESSAGES/",
                    "it": "locale/it/LC_MESSAGES/"
                }
            }
        ]
    }

The second entry in the json is to use a complete directory as translation source / destination.
Useful for documentation. DO NOT FORGET the trailing slash for directories.

Usage
-----

Push source files::

    crowdin push

Pull translations::

    crowdin pull

If you're importing a project with existing translations to crowdin, run
``crowdin push -a`` to also upload the local target files to crowdin. The
``-a`` flag should only be used once, you must then use the push / review /
pull workflow provided by Crowdin.

Changelog
---------

* 0.3: Added support for wildcard character to manage folders in translations
* 0.2: Added ``-a`` flag to ``crowdin push``.
* 0.1: initial version.

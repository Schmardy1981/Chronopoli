Chronopoli Tutor Plugin
=======================

A Tutor plugin for the Chronopoli global knowledge platform.

Installation
------------

::

    pip install -e ./tutor/plugins/chronopoli/
    tutor plugins enable chronopoli
    tutor config save

Features
--------

- Configures 6 Knowledge Districts as OpenEdX organizations
- Injects Chronopoli Django apps (onboarding, partners)
- Adds custom URL patterns for the platform
- Applies Chronopoli theme settings

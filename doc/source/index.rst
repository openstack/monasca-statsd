Introduction
============

A global :class:`~statsd.MonascaStatsd` instance that is easily shared
across an application's modules. Initialize this once in your application's
set-up code and then other modules can import and use it without further
configuration.

    >>> from monascastatsd import monascastatsd
    >>> monascastatsd.connect(host='localhost', port=8125)

Source
======

The Monasca-Statsd source is freely available on Github. Check it out `here
<https://github.com/openstack/monasca-statsd>`_.

Get in Touch
============

If you'd like to suggest a feature or report a bug,
please add an issue `here <https://bugs.launchpad.net/monasca>`_.

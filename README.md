Team and repository tags
========================

[![Team and repository tags](http://governance.openstack.org/badges/monasca-statsd.svg)](http://governance.openstack.org/reference/tags/index.html)

<!-- Change things from this point on -->

A Monasca-Statsd Python client.
================

Quick Start Guide
-----------------

First install the library with `pip` or `easy_install`

    # Install in system python ...
    sudo pip install monasca-statsd

    # .. or into a virtual env
    pip install monasca-statsd

Then start instrumenting your code:

```
# Import the module.
import monascastatsd as mstatsd

# Create the connection
conn = mstatsd.Connection(host='localhost', port=8125)

# Create the client with optional dimensions
client = mstatsd.Client(connection=conn, dimensions={'env': 'test'})

NOTE: You can also create a client without specifying the connection and it will create the client 
with the default connection information for the monasca-agent statsd processor daemon 
which uses host='localhost' and port=8125.

client = mstatsd.Client(dimensions={'env': 'test'})

# Increment and decrement a counter.
counter = client.get_counter(name='page.views')

counter.increment()
counter += 3

counter.decrement()
counter -= 3

# Record a gauge 50% of the time.
gauge = client.get_gauge('gauge', dimensions={'env': 'test'})

gauge.send('metric', 123.4, sample_rate=0.5)

# Sample a histogram.
histogram = client.get_histogram('histogram', dimensions={'test': 'True'})

histogram.send('metric', 123.4, dimensions={'color': 'red'})

# Time a function call.
timer = client.get_timer()

@timer.timed('page.render')
def render_page():
    # Render things ...
    pass

# Time a block of code.
timer = client.get_timer()

with timer.time('t'):
    # Do stuff
    time.sleep(2)

# Add dimensions to any metric.
histogram = client.get_histogram('my_hist')
histogram.send('query.time', 10, dimensions = {'version': '1.0', 'environment': 'dev'})
```
Repository
-------------

The monasca-statsd code is located here:
[here](https://github.com/stackforge/monasca-statsd).

Feedback
--------

To suggest a feature, report a bug, or general discussion, head over
[here](https://bugs.launchpad.net/monasca).


License
-------

See LICENSE file
Code was originally forked from Datadog's dogstatsd-python, hence the dual license.

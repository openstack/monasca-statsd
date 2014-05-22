monasca-statsd
================

A Monasca-Statsd Python client.

Quick Start Guide
-----------------

First install the library with `pip` or `easy_install`

    # Install in system python ...
    sudo pip install monasca-statsd

    # .. or into a virtual env
    pip install monasca-statsd

Then start instrumenting your code:

``` python
# Import the module.
from monascastatsd import monascastatsd

# Optionally, configure the host and port if you're running Statsd on a
# non-standard port.
monascastatsd.connect('localhost', 8125)

# Increment a counter.
monascastatsd.increment('page.views')

# Record a gauge 50% of the time.
monascastatsd.gauge('users.online', 123, sample_rate=0.5)

# Sample a histogram.
monascastatsd.histogram('file.upload.size', 1234)

# Time a function call.
@monascastatsd.timed('page.render')
def render_page():
    # Render things ...

# Tag a metric.
monascastatsd.histogram('query.time', 10, dimensions = {"version": "1.0", "environment": "dev"})
```
Documentation
-------------

Read the full API docs
[here](https://github.com/stackforge/monasca-statsd).

Feedback
--------

To suggest a feature, report a bug, or general discussion, head over
[here](https://bugs.launchpad.net/monasca).

Change Log
----------
- 1.0.0
    - Initial version of the code


License
-------

Copyright (c) 2014 Hewlett-Packard Development Company, L.P.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
    
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied.
See the License for the specific language governing permissions and
limitations under the License.
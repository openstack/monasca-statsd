# (C) Copyright 2014 Hewlett Packard Enterprise Development Company LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Monasca-Statsd is a Python client for Statsd that adds dimensions.
"""
from monascastatsd.connection import Connection
from monascastatsd.counter import Counter
from monascastatsd.gauge import Gauge
from monascastatsd.histogram import Histogram
from monascastatsd.set import Set
from monascastatsd.timer import Timer


class Client(object):

    def __init__(self, name=None, connection=None, max_buffer_size=50, dimensions=None):
        """Initialize a Client object.

        >>> monascastatsd = MonascaStatsd()

        :name: the name for this client.  Everything sent by this client
            will be prefixed by name
        :param host: the host of the MonascaStatsd server.
        :param port: the port of the MonascaStatsd server.
        :param max_buffer_size: Maximum number of metric to buffer before
         sending to the server if sending metrics in batch
        """
        if connection is None:
            self.connection = Connection(host='localhost',
                                         port=8125,
                                         max_buffer_size=50)
        else:
            self.connection = connection
        self._dimensions = dimensions
        self._name = name

    def get_counter(self, name, connection=None, dimensions=None):
        """Gets a Counter object.

        """
        if connection is None:
            connection = self.connection
        return Counter(name=self._update_name(name),
                       connection=connection,
                       dimensions=self._update_dimensions(dimensions))

    def get_gauge(self, name=None, connection=None, dimensions=None):
        """Gets a Gauge object.

        """
        if connection is None:
            connection = self.connection
        return Gauge(name=self._update_name(name),
                     connection=connection,
                     dimensions=self._update_dimensions(dimensions))

    def get_histogram(self, name=None, connection=None, dimensions=None):
        """Gets a Histogram object.

        """
        if connection is None:
            connection = self.connection
        return Histogram(name=self._update_name(name),
                         connection=connection,
                         dimensions=self._update_dimensions(dimensions))

    def get_set(self, name=None, connection=None, dimensions=None):
        """Gets a Set object.

        """
        if connection is None:
            connection = self.connection
        return Set(name=self._update_name(name),
                   connection=connection,
                   dimensions=self._update_dimensions(dimensions))

    def get_timer(self, name=None, connection=None, dimensions=None):
        """Gets a Timer object.

        """
        if connection is None:
            connection = self.connection
        return Timer(name=self._update_name(name),
                     connection=connection,
                     dimensions=self._update_dimensions(dimensions))

    def _update_name(self, name):
        """Update the metric name with the client

        name that was passed in on instantiation.
        """
        if self._name:
            metric = self._name
            if name:
                metric = metric + "." + name
        else:
            metric = name
        return metric

    def _update_dimensions(self, dimensions):
        """Update the dimensions list with the default

        dimensions that were passed in on instantiation.
        """
        if self._dimensions:
            new_dimensions = self._dimensions.copy()
        else:
            new_dimensions = {}
        if dimensions:
            new_dimensions.update(dimensions)

        return new_dimensions

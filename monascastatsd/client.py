# (C) Copyright 2014-2016 Hewlett Packard Enterprise Development LP
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
#
# Copyright (c) 2012, Datadog <info@datadoghq.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Datadog nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL DATADOG BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Monasca-Statsd is a Python client for Statsd that adds dimensions.
"""
from monascastatsd.connection import Connection
from monascastatsd.counter import Counter
from monascastatsd.gauge import Gauge
from monascastatsd.timer import Timer


class Client(object):

    def __init__(self, name=None, host='localhost', port=8125,
                 connection=None, max_buffer_size=50, dimensions=None):
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
            self.connection = Connection(host=host,
                                         port=port,
                                         max_buffer_size=max_buffer_size)
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
